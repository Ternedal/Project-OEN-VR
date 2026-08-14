#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from foley_human_review_support import FoleyReviewError, evaluate_normalized, expected_bindings, load_context, load_json


def _result_complete(spec: dict[str, Any], value: Any) -> bool:
    if spec.get("type") == "rating":
        return isinstance(value, int) and not isinstance(value, bool) and spec.get("min") <= value <= spec.get("max")
    return isinstance(value, str) and value in spec.get("values", []) and bool(value)


def normalize(payload: dict[str, Any], session_root: Path, require_complete: bool = False) -> dict[str, Any]:
    context = load_context(session_root)
    contract = context["reviewContract"]
    export = contract["reviewExport"]
    if payload.get("version") != export["version"] or payload.get("status") != export["status"]:
        raise FoleyReviewError("expected V1 human-foley-review-unvalidated payload")
    if payload.get("bindings") != expected_bindings(context):
        raise FoleyReviewError("Foley review bindings are stale or do not match current technical evidence")

    reviewer_alias = payload.get("reviewerAlias", "")
    reviewed_at = payload.get("reviewedAt", "")
    if not isinstance(reviewer_alias, str) or not isinstance(reviewed_at, str):
        raise FoleyReviewError("reviewerAlias/reviewedAt must be text")

    take_decisions = payload.get("takeDecisions")
    take_notes = payload.get("takeNotes", {})
    cue_reviews = payload.get("cueReviews")
    expected_paths = list(sorted(context["takeRecords"]))
    expected_cues = list(context["cueRecords"])
    if not isinstance(take_decisions, dict) or set(take_decisions) != set(expected_paths):
        raise FoleyReviewError("takeDecisions must contain exactly the 73 current take paths")
    if not isinstance(take_notes, dict) or set(take_notes) != set(expected_paths):
        raise FoleyReviewError("takeNotes must contain exactly the 73 current take paths")
    if not isinstance(cue_reviews, dict) or set(cue_reviews) != set(expected_cues):
        raise FoleyReviewError("cueReviews must contain exactly the 17 current cue IDs")

    normalized_cues: list[dict[str, Any]] = []
    reviewed_takes = 0
    complete_cues = 0
    take_values = set(contract["takeDecisionValues"])
    cue_values = set(contract["cueDecisionValues"])
    typed = contract["typedChecks"]

    for cue_id, records in context["cueRecords"].items():
        raw_cue = cue_reviews[cue_id]
        if not isinstance(raw_cue, dict):
            raise FoleyReviewError(f"{cue_id}: cue review must be an object")
        cue_decision = raw_cue.get("decision", "")
        if cue_decision not in cue_values | {""}:
            raise FoleyReviewError(f"{cue_id}: invalid cue decision {cue_decision!r}")
        cue_note = raw_cue.get("note", "")
        if not isinstance(cue_note, str):
            raise FoleyReviewError(f"{cue_id}: cue note must be text")
        raw_checks = raw_cue.get("checks")
        if not isinstance(raw_checks, dict) or set(raw_checks) != set(typed):
            raise FoleyReviewError(f"{cue_id}: checks must contain exactly the typed check IDs")

        checks: dict[str, dict[str, Any]] = {}
        checks_complete = True
        for check_id, spec in typed.items():
            raw_entry = raw_checks[check_id]
            if not isinstance(raw_entry, dict):
                raise FoleyReviewError(f"{cue_id}/{check_id}: check must be an object")
            value = raw_entry.get("result")
            note = raw_entry.get("note", "")
            if not isinstance(note, str):
                raise FoleyReviewError(f"{cue_id}/{check_id}: note must be text")
            if value not in ("", None) and not _result_complete(spec, value):
                raise FoleyReviewError(f"{cue_id}/{check_id}: invalid result {value!r}")
            if not _result_complete(spec, value):
                checks_complete = False
            checks[check_id] = {"result": value, "note": note.strip()}

        takes: list[dict[str, Any]] = []
        takes_complete = True
        for record in records:
            rel = record["relativePath"]
            decision = take_decisions[rel]
            note = take_notes[rel]
            if decision not in take_values | {""}:
                raise FoleyReviewError(f"{rel}: invalid take decision {decision!r}")
            if not isinstance(note, str):
                raise FoleyReviewError(f"{rel}: take note must be text")
            if decision:
                reviewed_takes += 1
            else:
                takes_complete = False
            takes.append({
                "relativePath": rel,
                "filename": record["filename"],
                "variant": record["variant"],
                "sourceSha256": record["sha256"],
                "decision": decision,
                "note": note.strip(),
            })

        cue_complete = bool(cue_decision) and checks_complete and takes_complete
        if cue_complete:
            complete_cues += 1
        normalized_cues.append({
            "cueId": cue_id,
            "decision": cue_decision,
            "note": cue_note.strip(),
            "reviewComplete": cue_complete,
            "takes": takes,
            "checks": checks,
        })

    normalized = {
        "version": 1,
        "status": contract["normalizedStatus"],
        "reviewKind": "physical-foley-human-source-approval",
        "reviewerAlias": reviewer_alias.strip(),
        "reviewedAt": reviewed_at.strip(),
        "bindings": expected_bindings(context),
        "coverage": {
            "reviewedTakes": reviewed_takes,
            "expectedTakes": contract["expectedTakeCount"],
            "completeCues": complete_cues,
            "expectedCues": contract["expectedCueCount"],
        },
        "cueReviews": normalized_cues,
        "rule": "Normalized human Foley evidence is evaluated but not materialized. Negative/rerecord decisions remain valid evidence; source promotion is separate.",
    }
    evaluation = evaluate_normalized(normalized, context)
    normalized.update(evaluation)
    normalized["coverage"]["complete"] = evaluation["reviewComplete"]
    if require_complete and not evaluation["reviewComplete"]:
        raise FoleyReviewError(
            f"Foley review incomplete: {reviewed_takes}/{contract['expectedTakeCount']} takes, {complete_cues}/{contract['expectedCueCount']} cues; reviewer/timestamp must also be present"
        )
    return normalized


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize hash-bound human Foley review evidence without automatically promoting source audio.")
    parser.add_argument("--session", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    try:
        payload = load_json(args.input)
        result = normalize(payload, args.session, require_complete=args.require_complete)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    except FoleyReviewError as exc:
        print(f"ERROR: {exc}")
        return 1
    print(
        f"Foley human review normalized: {result['coverage']['reviewedTakes']}/{result['coverage']['expectedTakes']} takes, "
        f"{result['coverage']['completeCues']}/{result['coverage']['expectedCues']} complete cues; "
        f"readyForSourceMaterialization={result['readyForSourceMaterialization']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
