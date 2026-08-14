#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from audio_derived_master_support import ROOT, DerivedError, load_json, load_review_context
from normalize_audio_source_approval_review import normalize_check


def derived_eligible(typed: dict[str, Any], decision: str, checks: dict[str, dict[str, Any]]) -> bool:
    return (
        decision == "approve-derived-master"
        and checks["CONTAMINATION"]["value"] == "pass"
        and checks["MATERIAL_MATCH"]["value"] >= typed["MATERIAL_MATCH"]["approvalMin"]
        and checks["LOOP_OR_SLICE"]["value"] in {"pass", "not-applicable"}
        and checks["NOISE_FLOOR"]["value"] == "pass"
        and checks["TRANSIENT_QUALITY"]["value"] in {"pass", "not-applicable"}
        and checks["SPACE_IDENTITY"]["value"] == "pass"
        and isinstance(checks["VARIATION_VALUE"]["value"], int)
        and checks["SPEECH_SPACE"]["value"] in {"pass", "not-applicable"}
    )


def expected_bindings(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "technicalReceiptSha256": context["technicalReceiptSha256"],
        "derivedHashes": {x["masterId"]: x["derivedSha256"] for x in context["technicalReceipt"]["records"]},
    }


def normalize(payload: dict[str, Any], technical_receipt: Path, submission: Path, source_receipt: Path, masters_dir: Path, repo_root: Path = ROOT, require_complete: bool = False) -> dict[str, Any]:
    context = load_review_context(technical_receipt, submission, source_receipt, masters_dir, repo_root)
    contract = context["contract"]
    typed = context["typedChecks"]
    if payload.get("version") != 1 or payload.get("status") != contract["humanReview"]["exportStatus"]:
        raise DerivedError("derived human review version/status mismatch")
    if payload.get("bindings") != expected_bindings(context):
        raise DerivedError("derived human review bindings are stale")
    reviewer = payload.get("reviewerAlias")
    reviewed_at = payload.get("reviewedAt")
    if not isinstance(reviewer, str) or not isinstance(reviewed_at, str):
        raise DerivedError("reviewerAlias/reviewedAt must be text")
    records = payload.get("records")
    expected = {x["masterId"]: x for x in context["technicalReceipt"]["records"]}
    if not isinstance(records, list) or len(records) != len(expected):
        raise DerivedError(f"derived review must contain exactly {len(expected)} technical masters")
    allowed_decisions = set(contract["humanReview"]["decisionValues"])
    required_checks = set(typed)
    normalized = []
    seen: set[str] = set()
    decided = 0
    eligible_count = 0
    for raw in records:
        if not isinstance(raw, dict):
            raise DerivedError("derived review contains invalid record")
        master_id = raw.get("masterId")
        source = expected.get(master_id)
        if not source or master_id in seen:
            raise DerivedError(f"unknown/duplicate masterId: {master_id!r}")
        seen.add(master_id)
        for field in ("sourceKey", "sourceApprovedSha256", "filename", "derivedSha256", "intendedUse", "editRecipe"):
            if raw.get(field) != source.get(field):
                raise DerivedError(f"{master_id}: derived review identity drift in {field}")
        decision = raw.get("decision", "")
        overall = raw.get("overallNote", "")
        if decision and decision not in allowed_decisions:
            raise DerivedError(f"{master_id}: invalid decision {decision!r}")
        if not isinstance(overall, str):
            raise DerivedError(f"{master_id}: overallNote must be text")
        checks = raw.get("checks")
        if not isinstance(checks, dict) or set(checks) != required_checks:
            raise DerivedError(f"{master_id}: repeated listening check set mismatch")
        try:
            normalized_checks = {check_id: normalize_check(check_id, checks[check_id], typed[check_id]) for check_id in typed}
        except Exception as exc:
            raise DerivedError(f"{master_id}: invalid typed listening evidence: {exc}") from exc
        if decision:
            decided += 1
        eligible = derived_eligible(typed, decision, normalized_checks)
        if eligible:
            eligible_count += 1
        normalized.append({
            "masterId": master_id,
            "sourceKey": source["sourceKey"],
            "sourceApprovedSha256": source["sourceApprovedSha256"],
            "filename": source["filename"],
            "derivedSha256": source["derivedSha256"],
            "intendedUse": source["intendedUse"],
            "editRecipe": source["editRecipe"],
            "technicalProbe": source["technicalProbe"],
            "decision": decision,
            "checks": normalized_checks,
            "overallNote": overall.strip(),
            "derivedMasterApprovedEligible": eligible,
        })
    complete = bool(reviewer.strip()) and bool(reviewed_at.strip()) and decided == len(expected)
    if require_complete and not complete:
        raise DerivedError(f"derived human review incomplete: reviewer={bool(reviewer.strip())}, reviewedAt={bool(reviewed_at.strip())}, decisions={decided}/{len(expected)}")
    return {
        "version": 1,
        "status": contract["humanReview"]["normalizedStatus"],
        "reviewKind": "typed-human-derived-master-approval",
        "reviewedAt": reviewed_at,
        "reviewerAlias": reviewer.strip(),
        "bindings": expected_bindings(context),
        "coverage": {"decided": decided, "total": len(expected), "eligibleForDerivedMasterApproval": eligible_count, "complete": complete},
        "records": sorted(normalized, key=lambda x: x["masterId"]),
        "rule": "Human re-listening evidence evaluated on derived bytes. Eligibility is not materialized derived-master-approved state until the separate promotion tool succeeds."
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize PROJECT OEN human re-listening evidence for derived audio masters.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--technical-receipt", type=Path, required=True)
    parser.add_argument("--submission", type=Path, required=True)
    parser.add_argument("--source-approved-receipt", type=Path, required=True)
    parser.add_argument("--masters-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    try:
        result = normalize(load_json(args.input), args.technical_receipt.resolve(), args.submission.resolve(), args.source_approved_receipt.resolve(), args.masters_dir.resolve(), require_complete=args.require_complete)
    except DerivedError as exc:
        print(f"ERROR: {exc}")
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    c = result["coverage"]
    print(f"OK derived human evidence: {c['decided']}/{c['total']} decided, {c['eligibleForDerivedMasterApproval']} eligible, complete={c['complete']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
