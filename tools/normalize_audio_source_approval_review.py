#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from audio_source_approval_support import ROOT, ApprovalError, collect_upstream, expected_bindings, load_json, verify_pack_sources


def normalize_check(check_id: str, raw: Any, spec: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ApprovalError(f"{check_id}: check must be an object")
    value = raw.get("value")
    note = raw.get("note", "")
    if not isinstance(note, str):
        raise ApprovalError(f"{check_id}: note must be text")
    if spec["type"] == "rating":
        if not isinstance(value, int) or isinstance(value, bool) or value < spec["min"] or value > spec["max"]:
            raise ApprovalError(f"{check_id}: rating must be integer {spec['min']}-{spec['max']}")
    elif value not in set(spec["allowed"]):
        raise ApprovalError(f"{check_id}: invalid categorical value {value!r}")
    return {"value": value, "note": note.strip()}


def source_eligible(contract: dict[str, Any], source: dict[str, Any], decision: str, checks: dict[str, dict[str, Any]]) -> bool:
    license_ok = isinstance(source.get("license"), str) and bool(source["license"].strip()) and isinstance(source.get("sourcePage"), str) and bool(source["sourcePage"].strip())
    return (
        decision == "approve-source"
        and license_ok
        and checks["CONTAMINATION"]["value"] == "pass"
        and checks["MATERIAL_MATCH"]["value"] >= contract["typedChecks"]["MATERIAL_MATCH"]["approvalMin"]
        and checks["LOOP_OR_SLICE"]["value"] in {"pass", "not-applicable"}
        and checks["NOISE_FLOOR"]["value"] == "pass"
        and checks["TRANSIENT_QUALITY"]["value"] in {"pass", "not-applicable"}
        and checks["SPACE_IDENTITY"]["value"] == "pass"
        and isinstance(checks["VARIATION_VALUE"]["value"], int)
        and checks["SPEECH_SPACE"]["value"] in {"pass", "not-applicable"}
    )


def normalize(payload: dict[str, Any], upstream: list[Path], pack_root: Path, repo_root: Path = ROOT, require_complete: bool = False) -> dict[str, Any]:
    context = collect_upstream(upstream, repo_root)
    verify_pack_sources(pack_root, context["selected"])
    contract = context["contract"]
    export = contract["reviewExport"]
    if payload.get("version") != export["version"] or payload.get("status") != export["status"]:
        raise ApprovalError("typed source approval export version/status mismatch")
    if payload.get("bindings") != expected_bindings(context):
        raise ApprovalError("typed source approval bindings are stale")
    reviewer = payload.get("reviewerAlias")
    reviewed_at = payload.get("reviewedAt")
    if not isinstance(reviewer, str) or not isinstance(reviewed_at, str):
        raise ApprovalError("reviewerAlias/reviewedAt must be text")
    records = payload.get("records")
    if not isinstance(records, list) or len(records) != len(context["selected"]):
        raise ApprovalError(f"typed review must contain exactly {len(context['selected'])} shortlisted source records")
    allowed_decisions = set(contract["sourceDecisionValues"])
    required_checks = set(contract["typedChecks"])
    seen: set[str] = set()
    normalized = []
    decided = 0
    eligible_count = 0
    for raw in records:
        if not isinstance(raw, dict):
            raise ApprovalError("typed review contains invalid source record")
        key = raw.get("sourceKey")
        source = context["selected"].get(key)
        if not source or key in seen:
            raise ApprovalError(f"unknown/duplicate sourceKey: {key!r}")
        seen.add(key)
        for field, expected in (("reviewKind", source["reviewKind"]), ("target", source["target"]), ("reviewPath", source["reviewPath"]), ("sourcePath", source["sourcePath"]), ("sourceSha256", source["sha256"]), ("license", source["license"])):
            if raw.get(field) != expected:
                raise ApprovalError(f"{key}: source identity/provenance drift in {field}")
        decision = raw.get("sourceDecision", "")
        overall = raw.get("overallNote", "")
        if decision and decision not in allowed_decisions:
            raise ApprovalError(f"{key}: invalid sourceDecision {decision!r}")
        if not isinstance(overall, str):
            raise ApprovalError(f"{key}: overallNote must be text")
        checks = raw.get("checks")
        if not isinstance(checks, dict) or set(checks) != required_checks:
            raise ApprovalError(f"{key}: typed check set mismatch")
        normalized_checks = {check_id: normalize_check(check_id, checks[check_id], contract["typedChecks"][check_id]) for check_id in contract["typedChecks"]}
        if decision:
            decided += 1
        eligible = source_eligible(contract, source, decision, normalized_checks)
        if eligible:
            eligible_count += 1
        normalized.append({
            "sourceKey": key,
            "reviewKind": source["reviewKind"],
            "target": source["target"],
            "reviewPath": source["reviewPath"],
            "sourcePath": source["sourcePath"],
            "sourceSha256": source["sha256"],
            "license": source["license"],
            "provider": source["provider"],
            "sourcePage": source["sourcePage"],
            "sourceKind": source["sourceKind"],
            "sourceDecision": decision,
            "checks": normalized_checks,
            "overallNote": overall.strip(),
            "sourceApprovedEligible": eligible,
        })
    complete = bool(reviewer.strip()) and bool(reviewed_at.strip()) and decided == len(context["selected"])
    if require_complete and not complete:
        raise ApprovalError(f"typed source approval review incomplete: reviewer={bool(reviewer.strip())}, reviewedAt={bool(reviewed_at.strip())}, decisions={decided}/{len(context['selected'])}")
    return {
        "version": 1,
        "status": contract["normalizedStatus"],
        "reviewKind": "typed-human-audio-source-approval",
        "reviewedAt": reviewed_at,
        "reviewerAlias": reviewer.strip(),
        "bindings": expected_bindings(context),
        "coverage": {"decided": decided, "total": len(context["selected"]), "eligibleForSourceApproval": eligible_count, "complete": complete},
        "records": sorted(normalized, key=lambda x: x["sourceKey"]),
        "rule": "Typed human evidence evaluated against sourceApprovedRequires. Eligibility is not materialized source-approved state until the separate promotion tool succeeds."
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize typed PROJECT OEN human audio source approval evidence.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--upstream", type=Path, action="append", required=True)
    parser.add_argument("--pack-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    try:
        payload = load_json(args.input)
        result = normalize(payload, [x.resolve() for x in args.upstream], args.pack_root, require_complete=args.require_complete)
    except ApprovalError as exc:
        print(f"ERROR: {exc}")
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    c = result["coverage"]
    print(f"OK typed source approval evidence: {c['decided']}/{c['total']} decided, {c['eligibleForSourceApproval']} eligible, complete={c['complete']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
