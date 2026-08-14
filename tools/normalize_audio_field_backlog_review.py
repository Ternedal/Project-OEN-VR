#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "content/audio/acquisition_field_backlog_receipt.source.json"
STATUS = "human-field-backlog-review-unvalidated"
OUTPUT_STATUS = "human-review-evidence-unapproved"
DISPOSITIONS = {"unreviewed", "candidate-pass", "reject", "needs-more-listening"}
CHECK_RESULTS = {"", "pass", "fail", "not-applicable", "needs-more-listening"}
CHECKS = {
    "CONTAMINATION",
    "MATERIAL_MATCH",
    "LOOP_OR_SLICE",
    "NOISE_FLOOR",
    "SPACE_IDENTITY",
    "VARIATION_VALUE",
    "SPEECH_SPACE",
}


class ReviewError(RuntimeError):
    pass


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise ReviewError(f"Cannot parse {path}: {exc}") from exc


def receipt_context(root: Path = ROOT) -> dict[str, dict[str, Any]]:
    data = load_json(root / "content/audio/acquisition_field_backlog_receipt.source.json")
    records = data.get("records")
    if not isinstance(records, list) or not records:
        raise ReviewError("field receipt records must be a non-empty list")
    out: dict[str, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict):
            raise ReviewError("field receipt contains invalid record")
        target = record.get("target")
        sha = record.get("sha256")
        if not isinstance(target, str) or not target:
            raise ReviewError("field receipt target missing")
        if not isinstance(sha, str) or len(sha) != 64:
            raise ReviewError(f"field receipt invalid sha256 for {target}")
        if target in out:
            raise ReviewError(f"field receipt duplicate target {target}")
        out[target] = record
    return out


def normalize(payload: dict[str, Any], root: Path = ROOT, require_complete: bool = False) -> dict[str, Any]:
    if payload.get("version") != 1 or payload.get("status") != STATUS:
        raise ReviewError("expected V1 human-field-backlog-review-unvalidated payload")
    context = receipt_context(root)
    bindings = payload.get("bindings")
    expected_bindings = {target: record["sha256"] for target, record in context.items()}
    if not isinstance(bindings, dict) or bindings != expected_bindings:
        raise ReviewError("field review bindings must exactly match committed receipt SHA-256 values")

    records = payload.get("records")
    if not isinstance(records, list):
        raise ReviewError("field review records must be a list")
    seen: set[str] = set()
    normalized = []
    for raw in records:
        if not isinstance(raw, dict):
            raise ReviewError("field review contains invalid record")
        target = raw.get("target")
        if target not in context:
            raise ReviewError(f"field review unknown target {target!r}")
        if target in seen:
            raise ReviewError(f"field review duplicate target {target}")
        seen.add(target)
        disposition = raw.get("disposition")
        if disposition not in DISPOSITIONS:
            raise ReviewError(f"invalid disposition for {target}: {disposition!r}")
        overall = raw.get("overall")
        if not isinstance(overall, str):
            raise ReviewError(f"overall must be text for {target}")
        checks = raw.get("checks")
        if not isinstance(checks, dict) or set(checks) != CHECKS:
            raise ReviewError(f"check set mismatch for {target}")
        normalized_checks = {}
        for check_id in sorted(CHECKS):
            value = checks[check_id]
            if not isinstance(value, dict):
                raise ReviewError(f"invalid {target}/{check_id}")
            result = value.get("result", "")
            note = value.get("note", "")
            if result not in CHECK_RESULTS or not isinstance(note, str):
                raise ReviewError(f"invalid result/note for {target}/{check_id}")
            normalized_checks[check_id] = {"result": result, "note": note.strip()}
        source = context[target]
        normalized.append({
            "target": target,
            "runtimeEventCandidate": source.get("runtimeEventCandidate"),
            "sourceFilename": source.get("filename"),
            "sourceSha256": source["sha256"],
            "disposition": disposition,
            "overall": overall.strip(),
            "checks": normalized_checks,
        })

    if seen != set(context):
        raise ReviewError(f"review must contain every field-backlog target; got {sorted(seen)}")
    reviewed = sum(r["disposition"] != "unreviewed" for r in normalized)
    checks_total = sum(len(r["checks"]) for r in normalized)
    checks_completed = sum(1 for r in normalized for c in r["checks"].values() if c["result"] != "")
    complete = reviewed == len(normalized) and checks_completed == checks_total
    if require_complete and not complete:
        raise ReviewError(
            f"field review incomplete; dispositions {reviewed}/{len(normalized)}, "
            f"checks {checks_completed}/{checks_total}"
        )
    return {
        "version": 1,
        "status": OUTPUT_STATUS,
        "reviewKind": "field-backlog-source-selection",
        "reviewedAt": payload.get("createdAt"),
        "coverage": {
            "reviewed": reviewed,
            "total": len(normalized),
            "checksCompleted": checks_completed,
            "checksTotal": checks_total,
            "complete": complete,
        },
        "records": sorted(normalized, key=lambda r: r["target"]),
        "rule": "Hash-bound human evidence only; source-approved remains a separate explicit gate.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize hash-bound PROJECT OEN field-backlog human audio review evidence.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    try:
        payload = load_json(args.input)
        if not isinstance(payload, dict):
            raise ReviewError("review input must be a JSON object")
        result = normalize(payload, require_complete=args.require_complete)
        args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        coverage = result["coverage"]
        print(f"OK {result['reviewKind']}: {coverage['reviewed']}/{coverage['total']} reviewed; status={result['status']}")
        return 0
    except ReviewError as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
