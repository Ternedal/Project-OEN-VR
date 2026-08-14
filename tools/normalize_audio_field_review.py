#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FIELD_RECEIPT = ROOT / "content" / "audio" / "acquisition_field_backlog_receipt.source.json"
FIELD_STATUS = "human-field-review-not-canonical-approval"
OUTPUT_STATUS = "human-review-evidence-unapproved"
DECISIONS = {"", "keep", "maybe", "reject"}
EXPECTED_SOURCE_STATUS = "acquired-original-not-listening-approved"


class ReviewError(RuntimeError):
    pass


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise ReviewError(f"Cannot parse {path}: {exc}") from exc


def field_context(receipt: dict[str, Any]) -> dict[str, dict[str, Any]]:
    records = receipt.get("records")
    if not isinstance(records, list) or not records:
        raise ReviewError("field receipt: records must be a non-empty list")
    out: dict[str, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict):
            raise ReviewError("field receipt: invalid record")
        target = record.get("target")
        filename = record.get("filename")
        sha = record.get("sha256")
        runtime_event = record.get("runtimeEventCandidate")
        if not all(isinstance(v, str) and v for v in (target, filename, sha, runtime_event)):
            raise ReviewError("field receipt: incomplete source identity")
        if len(sha) != 64:
            raise ReviewError(f"field receipt: invalid sha256 for {target}")
        if target in out:
            raise ReviewError(f"field receipt: duplicate target {target}")
        if record.get("status") != EXPECTED_SOURCE_STATUS:
            raise ReviewError(f"field receipt: {target} is not acquired-unapproved")
        out[target] = record
    return out


def validate_bindings(payload: dict[str, Any], context: dict[str, dict[str, Any]]) -> None:
    bindings = payload.get("bindings")
    if not isinstance(bindings, dict):
        raise ReviewError("field review: V2 bindings object is required")
    expected = {target: record["sha256"] for target, record in context.items()}
    if set(bindings) != set(expected):
        missing = sorted(set(expected) - set(bindings))
        extra = sorted(set(bindings) - set(expected))
        raise ReviewError(f"field review: binding keys mismatch; missing={missing}, extra={extra}")
    for target, sha in expected.items():
        if bindings.get(target) != sha:
            raise ReviewError(f"field review: stale or mismatched binding for {target}")


def normalize_field(payload: dict[str, Any], context: dict[str, dict[str, Any]], require_complete: bool = False) -> dict[str, Any]:
    if payload.get("version") != 2 or payload.get("status") != FIELD_STATUS:
        raise ReviewError("field review: expected V2 human-field-review-not-canonical-approval payload")
    validate_bindings(payload, context)
    reviews = payload.get("reviews")
    if not isinstance(reviews, dict):
        raise ReviewError("field review: reviews must be an object")
    unknown = sorted(set(reviews) - set(context))
    if unknown:
        raise ReviewError(f"field review: unknown target(s) {unknown}")

    normalized = []
    for target in sorted(context):
        raw = reviews.get(target, {})
        if not isinstance(raw, dict):
            raise ReviewError(f"field review: invalid review for {target}")
        decision = raw.get("fit", "")
        note = raw.get("notes", "")
        if decision not in DECISIONS:
            raise ReviewError(f"field review: invalid fit for {target}: {decision!r}")
        if not isinstance(note, str):
            raise ReviewError(f"field review: notes must be text for {target}")
        source = context[target]
        normalized.append({
            "target": target,
            "runtimeEventCandidate": source["runtimeEventCandidate"],
            "sourceFilename": source["filename"],
            "sourceSha256": source["sha256"],
            "license": source.get("license"),
            "decision": decision,
            "note": note.strip(),
        })

    reviewed = sum(record["decision"] != "" for record in normalized)
    complete = reviewed == len(normalized)
    if require_complete and not complete:
        raise ReviewError(f"field review: incomplete; reviewed {reviewed}/{len(normalized)}")
    return {
        "version": 1,
        "status": OUTPUT_STATUS,
        "reviewKind": "field-backlog-source-selection",
        "reviewedAt": payload.get("createdAt"),
        "coverage": {"reviewed": reviewed, "total": len(normalized), "complete": complete},
        "records": normalized,
        "rule": "keep/maybe/reject is hash-bound human source-selection evidence only. It never promotes source-approved, derived-master-approved, Unity-integrated or release-approved status.",
    }


def normalize(payload: dict[str, Any], root: Path = ROOT, require_complete: bool = False) -> dict[str, Any]:
    receipt = load_json(root / "content/audio/acquisition_field_backlog_receipt.source.json")
    if not isinstance(receipt, dict):
        raise ReviewError("field receipt must be a JSON object")
    return normalize_field(payload, field_context(receipt), require_complete=require_complete)


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize hash-bound PROJECT OEN field-audio human review evidence without promoting source status.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    try:
        payload = load_json(args.input)
        if not isinstance(payload, dict):
            raise ReviewError("review input must be a JSON object")
        result = normalize(payload, require_complete=args.require_complete)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        coverage = result["coverage"]
        print(f"OK {result['reviewKind']}: {coverage['reviewed']}/{coverage['total']} reviewed; status={result['status']}")
        return 0
    except ReviewError as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
