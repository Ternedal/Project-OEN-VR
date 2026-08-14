#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

from audio_derived_master_support import ROOT, DerivedError, load_json, load_review_context, sha256_file
from normalize_audio_derived_master_review import derived_eligible, expected_bindings, reviewer_identity_complete
from normalize_audio_source_approval_review import normalize_check


def validate_review(review: dict[str, Any], technical_receipt: Path, submission: Path, source_receipt: Path, masters_dir: Path, repo_root: Path = ROOT) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    context = load_review_context(technical_receipt, submission, source_receipt, masters_dir, repo_root)
    contract = context["contract"]
    typed = context["typedChecks"]
    if review.get("status") != contract["humanReview"]["normalizedStatus"] or review.get("reviewKind") != "typed-human-derived-master-approval":
        raise DerivedError("normalized derived human review status/kind mismatch")
    if review.get("bindings") != expected_bindings(context):
        raise DerivedError("normalized derived human review bindings are stale")
    reviewer_ok = reviewer_identity_complete(review.get("reviewerAlias"), review.get("reviewedAt"))
    records = review.get("records")
    expected = {x["masterId"]: x for x in context["technicalReceipt"]["records"]}
    if not isinstance(records, list) or len(records) != len(expected):
        raise DerivedError("normalized derived review master set mismatch")
    promotable = []
    seen: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            raise DerivedError("normalized derived review contains invalid record")
        master_id = record.get("masterId")
        source = expected.get(master_id)
        if not source or master_id in seen:
            raise DerivedError(f"unknown/duplicate derived master: {master_id!r}")
        seen.add(master_id)
        for field in ("sourceKey", "sourceApprovedSha256", "filename", "derivedSha256", "intendedUse", "editRecipe", "technicalProbe"):
            if record.get(field) != source.get(field):
                raise DerivedError(f"{master_id}: normalized derived provenance drift in {field}")
        checks = record.get("checks")
        if not isinstance(checks, dict) or set(checks) != set(typed):
            raise DerivedError(f"{master_id}: repeated listening check set mismatch")
        try:
            normalized_checks = {check_id: normalize_check(check_id, checks[check_id], typed[check_id]) for check_id in typed}
        except Exception as exc:
            raise DerivedError(f"{master_id}: invalid normalized typed evidence: {exc}") from exc
        recomputed = derived_eligible(typed, record.get("decision", ""), normalized_checks, reviewer_ok)
        if record.get("derivedMasterApprovedEligible") is not recomputed:
            raise DerivedError(f"{master_id}: stored eligibility disagrees with current human evidence")
        if recomputed:
            promotable.append(source)
    if seen != set(expected):
        raise DerivedError("normalized derived review master set drift")
    if not promotable:
        raise DerivedError("no derived master is eligible for approval materialization")
    return contract, promotable


def materialize(review_path: Path, technical_receipt: Path, submission: Path, source_receipt: Path, masters_dir: Path, output_dir: Path, repo_root: Path = ROOT, replace: bool = False) -> dict[str, Any]:
    review = load_json(review_path)
    contract, promotable = validate_review(review, technical_receipt, submission, source_receipt, masters_dir, repo_root)
    output_dir = output_dir.resolve(); masters_dir = masters_dir.resolve()
    if output_dir.exists() and any(output_dir.iterdir()) and not replace:
        raise DerivedError(f"output directory is not empty; use --replace explicitly: {output_dir}")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".derived-master-approved-", dir=output_dir.parent))
    try:
        records = []
        for master in sorted(promotable, key=lambda x: x["masterId"]):
            source = masters_dir / master["filename"]
            actual = sha256_file(source)
            if actual != master["derivedSha256"]:
                raise DerivedError(f"{master['masterId']}: derived bytes changed before approval materialization")
            dest = staging / master["filename"]
            shutil.copyfile(source, dest)
            output_sha = sha256_file(dest)
            if output_sha != actual:
                raise DerivedError(f"{master['masterId']}: approval copy changed derived bytes")
            records.append({
                "masterId": master["masterId"], "sourceKey": master["sourceKey"],
                "sourceApprovedSha256": master["sourceApprovedSha256"], "filename": master["filename"],
                "derivedSha256": master["derivedSha256"], "approvedSha256": output_sha,
                "intendedUse": master["intendedUse"], "editRecipe": master["editRecipe"],
                "technicalProbe": master["technicalProbe"], "bytes": dest.stat().st_size,
                "sourceApproved": True, "derivedMasterApproved": True, "runtimeApproved": False, "releaseApproved": False,
            })
        receipt = {
            "version": 1, "status": contract["materialization"]["receiptStatus"],
            "humanDerivedReviewSha256": sha256_file(review_path),
            "technicalReceiptSha256": sha256_file(technical_receipt),
            "approvedCount": len(records), "records": records,
            "rule": "Explicit human derived-master gate materialized verified derived WAV bytes unchanged. Reviewer identity/timestamp are revalidated; runtime/Quest/release approval remain separate."
        }
        (staging / contract["materialization"]["receiptFilename"]).write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        if output_dir.exists():
            if replace: shutil.rmtree(output_dir)
            else: output_dir.rmdir()
        os.replace(staging, output_dir)
        return receipt
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Materialize human-approved PROJECT OEN derived audio masters.")
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--technical-receipt", type=Path, required=True)
    parser.add_argument("--submission", type=Path, required=True)
    parser.add_argument("--source-approved-receipt", type=Path, required=True)
    parser.add_argument("--masters-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()
    try:
        receipt = materialize(args.review.resolve(), args.technical_receipt.resolve(), args.submission.resolve(), args.source_approved_receipt.resolve(), args.masters_dir.resolve(), args.output.resolve(), ROOT, args.replace)
    except DerivedError as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"Materialized {receipt['approvedCount']} derived-master-approved WAV(s); runtime/release approval remains false.")
    return 0


if __name__ == "__main__": raise SystemExit(main())
