#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from radio_vo_human_review_support import DEFAULT_SESSION, ROOT, ReviewError, load_context, load_json


def normalize(payload: dict[str, Any], session_root: Path, repo_root: Path = ROOT, require_complete: bool = False) -> dict[str, Any]:
    context = load_context(session_root, repo_root)
    contract = context["contract"]
    export = contract["reviewExport"]
    if payload.get("version") != export.get("version") or payload.get("status") != export.get("status"):
        raise ReviewError("review export version/status mismatch")
    if payload.get("bindings") != context["bindings"]:
        raise ReviewError("review bindings are stale or do not match current session/receipt/source bytes")

    reviewer = payload.get("reviewerAlias")
    rights = payload.get("rightsDecision")
    rights_note = payload.get("rightsNote", "")
    if not isinstance(reviewer, str) or not isinstance(rights, str) or not isinstance(rights_note, str):
        raise ReviewError("reviewerAlias/rights fields must be text")
    if rights and rights not in set(contract["rightsDecisionValues"]):
        raise ReviewError(f"invalid rightsDecision: {rights!r}")

    raw_cues = payload.get("cues")
    if not isinstance(raw_cues, list):
        raise ReviewError("review cues must be a list")
    expected = {cue["cueId"]: cue for cue in context["cues"]}
    if len(raw_cues) != len(expected):
        raise ReviewError(f"review must contain exactly {len(expected)} cues")
    seen: set[str] = set()
    normalized = []
    complete_checks = 0
    total_checks = len(expected) * len(contract["checkIds"])
    decided = 0
    selected = 0
    all_selected_checks_pass = True

    for raw in raw_cues:
        if not isinstance(raw, dict):
            raise ReviewError("review contains invalid cue")
        cue_id = raw.get("cueId")
        if cue_id not in expected:
            raise ReviewError(f"unknown cueId: {cue_id!r}")
        if cue_id in seen:
            raise ReviewError(f"duplicate cueId: {cue_id}")
        seen.add(cue_id)
        cue = expected[cue_id]
        decision = raw.get("decision", "")
        selected_filename = raw.get("selectedFilename", "")
        note = raw.get("note", "")
        if decision and decision not in set(contract["cueDecisionValues"]):
            raise ReviewError(f"{cue_id}: invalid decision {decision!r}")
        if not isinstance(selected_filename, str) or not isinstance(note, str):
            raise ReviewError(f"{cue_id}: selectedFilename/note must be text")
        candidates = {item["filename"]: item for item in cue["candidates"]}
        selected_record = None
        if decision == "select":
            if selected_filename not in candidates:
                raise ReviewError(f"{cue_id}: select requires one of the three technically accepted take filenames")
            selected_record = candidates[selected_filename]
            selected += 1
        elif selected_filename:
            raise ReviewError(f"{cue_id}: selectedFilename must be empty unless decision == select")
        if decision:
            decided += 1

        checks = raw.get("checks")
        if not isinstance(checks, dict) or set(checks) != set(contract["checkIds"]):
            raise ReviewError(f"{cue_id}: human check set mismatch")
        normalized_checks = {}
        cue_checks_pass = True
        for check_id in contract["checkIds"]:
            value = checks[check_id]
            if not isinstance(value, dict):
                raise ReviewError(f"{cue_id}/{check_id}: invalid check")
            result = value.get("result", "")
            check_note = value.get("note", "")
            if result and result not in set(contract["checkResultValues"]):
                raise ReviewError(f"{cue_id}/{check_id}: invalid result {result!r}")
            if not isinstance(check_note, str):
                raise ReviewError(f"{cue_id}/{check_id}: note must be text")
            if result:
                complete_checks += 1
            if result != "pass":
                cue_checks_pass = False
            normalized_checks[check_id] = {"result": result, "note": check_note.strip()}
        if decision == "select" and not cue_checks_pass:
            all_selected_checks_pass = False
        if decision != "select":
            all_selected_checks_pass = False

        normalized.append({
            "cueId": cue_id,
            "spokenText": cue["spokenText"],
            "decision": decision,
            "selectedFilename": selected_filename,
            "selectedSha256": selected_record["sha256"] if selected_record else None,
            "checks": normalized_checks,
            "note": note.strip(),
        })

    complete = bool(reviewer.strip()) and bool(rights) and decided == len(expected) and complete_checks == total_checks
    if require_complete and not complete:
        raise ReviewError(f"human review incomplete: reviewer={bool(reviewer.strip())}, rights={bool(rights)}, decisions={decided}/{len(expected)}, checks={complete_checks}/{total_checks}")
    ready = complete and rights == "accepted" and selected == len(expected) and all_selected_checks_pass
    return {
        "version": 1,
        "status": contract["normalizedStatus"],
        "reviewKind": "radio-vo-human-take-selection",
        "reviewedAt": payload.get("reviewedAt"),
        "reviewerAlias": reviewer.strip(),
        "rightsDecision": rights,
        "rightsNote": rights_note.strip(),
        "bindings": context["bindings"],
        "coverage": {
            "cueDecisionsCompleted": decided,
            "cueDecisionsTotal": len(expected),
            "checksCompleted": complete_checks,
            "checksTotal": total_checks,
            "complete": complete,
        },
        "readyForDryMasterSelection": ready,
        "records": sorted(normalized, key=lambda x: x["cueId"]),
        "rule": "Hash-bound human review evidence only. readyForDryMasterSelection does not imply derived treatment, Unity integration, Quest intelligibility or release approval.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize hash-bound human PROJECT OEN radio VO take review without inventing a positive result.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--session", type=Path, default=ROOT / DEFAULT_SESSION)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    try:
        payload = load_json(args.input)
        result = normalize(payload, args.session, require_complete=args.require_complete)
    except ReviewError as exc:
        print(f"ERROR: {exc}")
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    c = result["coverage"]
    print(f"OK radio VO human evidence: decisions {c['cueDecisionsCompleted']}/{c['cueDecisionsTotal']}, checks {c['checksCompleted']}/{c['checksTotal']}, ready={result['readyForDryMasterSelection']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
