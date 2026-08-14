#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_RECEIPT = ROOT / "content" / "audio" / "acquisition_receipt.source.json"
EXTENSION_RECEIPT = ROOT / "content" / "audio" / "acquisition_extension_receipt.source.json"
EXTENSION_SHORTLIST = ROOT / "content" / "audio" / "acquisition_extension_member_shortlist.source.json"
LISTENING_QA = ROOT / "content" / "audio" / "listening_qa.source.json"

MAIN_STATUS = "human-listening-review-unvalidated"
EXT_STATUS = "human-review-not-canonical-approval"
OUTPUT_STATUS = "human-review-evidence-unapproved"
MAIN_DISPOSITIONS = {"unreviewed", "candidate-pass", "reject", "needs-more-listening"}
CHECK_RESULTS = {"", "pass", "fail", "not-applicable", "needs-more-listening"}
EXT_DECISIONS = {"", "keep", "maybe", "reject"}

MAIN_CHECKS = {
    "AMB_WIND_WORLD": {
        "CONTAMINATION", "MATERIAL_MATCH", "LOOP_OR_SLICE", "NOISE_FLOOR",
        "SPACE_IDENTITY", "VARIATION_VALUE", "SPEECH_SPACE",
    },
    "AMB_RAIN_ALT": {
        "CONTAMINATION", "MATERIAL_MATCH", "LOOP_OR_SLICE", "NOISE_FLOOR",
        "SPACE_IDENTITY", "VARIATION_VALUE", "SPEECH_SPACE",
    },
    "SFX_FIRE_ALT": {
        "CONTAMINATION", "MATERIAL_MATCH", "LOOP_OR_SLICE", "NOISE_FLOOR",
        "TRANSIENT_QUALITY", "SPACE_IDENTITY", "VARIATION_VALUE", "SPEECH_SPACE",
    },
}

class ReviewError(RuntimeError):
    pass


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise ReviewError(f"Cannot parse {path}: {exc}") from exc


def _record_index(data: dict[str, Any], owner: str) -> dict[str, dict[str, Any]]:
    records = data.get("records")
    if not isinstance(records, list):
        raise ReviewError(f"{owner}: records must be a list")
    out: dict[str, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("target"), str):
            raise ReviewError(f"{owner}: invalid record")
        target = record["target"]
        if target in out:
            raise ReviewError(f"{owner}: duplicate target {target}")
        sha = record.get("sha256")
        if not isinstance(sha, str) or len(sha) != 64:
            raise ReviewError(f"{owner}: target {target} has invalid sha256")
        out[target] = record
    return out


def canonical_context(receipt: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return _record_index(receipt, "canonical receipt")


def extension_context(receipt: dict[str, Any], shortlist: dict[str, Any]) -> dict[str, dict[str, Any]]:
    records = _record_index(receipt, "extension receipt")
    out: dict[str, dict[str, Any]] = {}
    ocean = records.get("AMB_OCEAN_ALT")
    if ocean:
        out[f"audio/ocean/{ocean['filename']}"] = {
            "target": "AMB_OCEAN_ALT",
            "sourcePath": ocean["filename"],
            "sha256": ocean["sha256"],
            "sourceKind": "direct-original",
        }

    members = shortlist.get("members")
    if not isinstance(members, list):
        raise ReviewError("extension shortlist: members must be a list")
    for member in members:
        if not isinstance(member, dict):
            raise ReviewError("extension shortlist: invalid member")
        target = member.get("archiveTarget")
        source_path = member.get("path")
        sha = member.get("sha256")
        if not all(isinstance(v, str) and v for v in (target, source_path, sha)) or len(sha) != 64:
            raise ReviewError("extension shortlist: incomplete member identity")
        if target == "SFX_WOOD_PACK_ALT":
            review_path = f"audio/wood/{Path(source_path).name}"
        elif target == "SFX_CLOTH_PACK_ALT":
            review_path = f"audio/cloth/{Path(source_path).name}"
        else:
            raise ReviewError(f"extension shortlist: unsupported archive target {target}")
        if review_path in out:
            raise ReviewError(f"extension shortlist: duplicate review path {review_path}")
        out[review_path] = {
            "target": target,
            "sourcePath": source_path,
            "sha256": sha,
            "sourceKind": "archive-member",
        }
    return out


def _validate_bindings(payload: dict[str, Any], expected: dict[str, str], owner: str) -> None:
    bindings = payload.get("bindings")
    if not isinstance(bindings, dict):
        raise ReviewError(f"{owner}: V2 bindings object is required")
    if set(bindings) != set(expected):
        missing = sorted(set(expected) - set(bindings))
        extra = sorted(set(bindings) - set(expected))
        raise ReviewError(f"{owner}: binding keys mismatch; missing={missing}, extra={extra}")
    for key, sha in expected.items():
        if bindings.get(key) != sha:
            raise ReviewError(f"{owner}: stale or mismatched binding for {key}")


def normalize_main(payload: dict[str, Any], context: dict[str, dict[str, Any]], configured_checks: set[str], require_complete: bool = False) -> dict[str, Any]:
    if payload.get("version") != 2 or payload.get("status") != MAIN_STATUS:
        raise ReviewError("main review: expected V2 human-listening-review-unvalidated payload")
    expected_targets = set(MAIN_CHECKS)
    if set(context) != expected_targets:
        raise ReviewError(f"main review: canonical receipt target set drifted: {sorted(context)}")
    for target, ids in MAIN_CHECKS.items():
        if not ids <= configured_checks:
            raise ReviewError(f"main review: check contract drift for {target}")
    _validate_bindings(payload, {t: context[t]["sha256"] for t in expected_targets}, "main review")

    records = payload.get("records")
    if not isinstance(records, list):
        raise ReviewError("main review: records must be a list")
    seen: set[str] = set()
    normalized = []
    for record in records:
        if not isinstance(record, dict):
            raise ReviewError("main review: invalid record")
        target = record.get("target")
        if target not in expected_targets:
            raise ReviewError(f"main review: unknown target {target!r}")
        if target in seen:
            raise ReviewError(f"main review: duplicate target {target}")
        seen.add(target)
        disposition = record.get("disposition")
        if disposition not in MAIN_DISPOSITIONS:
            raise ReviewError(f"main review: invalid disposition for {target}: {disposition!r}")
        overall = record.get("overall")
        if not isinstance(overall, str):
            raise ReviewError(f"main review: overall must be text for {target}")
        checks = record.get("checks")
        if not isinstance(checks, dict) or set(checks) != MAIN_CHECKS[target]:
            raise ReviewError(f"main review: check set mismatch for {target}")
        normalized_checks = {}
        for check_id in sorted(checks):
            value = checks[check_id]
            if not isinstance(value, dict):
                raise ReviewError(f"main review: invalid {target}/{check_id}")
            result = value.get("result", "")
            note = value.get("note", "")
            if result not in CHECK_RESULTS or not isinstance(note, str):
                raise ReviewError(f"main review: invalid result/note for {target}/{check_id}")
            normalized_checks[check_id] = {"result": result, "note": note.strip()}
        source = context[target]
        normalized.append({
            "target": target,
            "sourceFilename": source.get("filename"),
            "sourceSha256": source["sha256"],
            "disposition": disposition,
            "overall": overall.strip(),
            "checks": normalized_checks,
        })
    if seen != expected_targets:
        raise ReviewError(f"main review: reviewer export must contain all three targets, got {sorted(seen)}")
    reviewed = sum(r["disposition"] != "unreviewed" for r in normalized)
    checks_total = sum(len(r["checks"]) for r in normalized)
    checks_completed = sum(1 for r in normalized for c in r["checks"].values() if c["result"] != "")
    complete = reviewed == len(normalized) and checks_completed == checks_total
    if require_complete and not complete:
        raise ReviewError(
            f"main review: incomplete; dispositions {reviewed}/{len(normalized)}, "
            f"checks {checks_completed}/{checks_total}"
        )
    return {
        "version": 1,
        "status": OUTPUT_STATUS,
        "reviewKind": "main-acquired-originals",
        "reviewedAt": payload.get("reviewedAt"),
        "coverage": {"reviewed": reviewed, "total": len(normalized), "checksCompleted": checks_completed, "checksTotal": checks_total, "complete": complete},
        "records": sorted(normalized, key=lambda r: r["target"]),
        "rule": "Normalized human evidence is hash-bound and never promotes source approval automatically.",
    }


def normalize_extension(payload: dict[str, Any], context: dict[str, dict[str, Any]], require_complete: bool = False) -> dict[str, Any]:
    if payload.get("version") != 2 or payload.get("status") != EXT_STATUS:
        raise ReviewError("extension review: expected V2 human-review-not-canonical-approval payload")
    _validate_bindings(payload, {p: v["sha256"] for p, v in context.items()}, "extension review")
    reviews = payload.get("reviews")
    if not isinstance(reviews, dict):
        raise ReviewError("extension review: reviews must be an object")
    unknown = sorted(set(reviews) - set(context))
    if unknown:
        raise ReviewError(f"extension review: unknown review paths {unknown}")
    normalized = []
    for path in sorted(context):
        raw = reviews.get(path, {})
        if not isinstance(raw, dict):
            raise ReviewError(f"extension review: invalid review for {path}")
        decision = raw.get("fit", "")
        note = raw.get("notes", "")
        if decision not in EXT_DECISIONS:
            raise ReviewError(f"extension review: invalid fit for {path}: {decision!r}")
        if not isinstance(note, str):
            raise ReviewError(f"extension review: notes must be text for {path}")
        src = context[path]
        normalized.append({
            "reviewPath": path,
            "target": src["target"],
            "sourcePath": src["sourcePath"],
            "sourceSha256": src["sha256"],
            "sourceKind": src["sourceKind"],
            "decision": decision,
            "note": note.strip(),
        })
    reviewed = sum(r["decision"] != "" for r in normalized)
    if require_complete and reviewed != len(normalized):
        raise ReviewError(f"extension review: incomplete; reviewed {reviewed}/{len(normalized)}")
    return {
        "version": 1,
        "status": OUTPUT_STATUS,
        "reviewKind": "extension-source-selection",
        "reviewedAt": payload.get("createdAt"),
        "coverage": {"reviewed": reviewed, "total": len(normalized), "complete": reviewed == len(normalized)},
        "records": normalized,
        "rule": "keep/maybe/reject is hash-bound human source-selection evidence only; source-approved remains a separate gate.",
    }


def normalize(payload: dict[str, Any], root: Path = ROOT, require_complete: bool = False) -> dict[str, Any]:
    receipt = load_json(root / "content/audio/acquisition_receipt.source.json")
    ext_receipt = load_json(root / "content/audio/acquisition_extension_receipt.source.json")
    shortlist = load_json(root / "content/audio/acquisition_extension_member_shortlist.source.json")
    listening = load_json(root / "content/audio/listening_qa.source.json")
    configured_checks = {x.get("id") for x in listening.get("requiredListeningChecks", []) if isinstance(x, dict)}
    status = payload.get("status")
    if status == MAIN_STATUS:
        return normalize_main(payload, canonical_context(receipt), configured_checks, require_complete=require_complete)
    if status == EXT_STATUS:
        return normalize_extension(payload, extension_context(ext_receipt, shortlist), require_complete=require_complete)
    raise ReviewError(f"Unsupported review status {status!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize hash-bound PROJECT OEN human audio review evidence without promoting source status.")
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
