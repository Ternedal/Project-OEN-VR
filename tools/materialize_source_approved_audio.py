#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

from audio_source_approval_support import MATERIALIZE_CONTRACT, ROOT, ApprovalError, collect_upstream, expected_bindings, load_json, sha256_file, verify_pack_sources
from normalize_audio_source_approval_review import normalize_check, reviewer_identity_complete, source_eligible


def validate_approval(approval: dict[str, Any], upstream: list[Path], pack_root: Path, repo_root: Path = ROOT) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    context = collect_upstream(upstream, repo_root)
    verify_pack_sources(pack_root, context["selected"])
    contract = context["contract"]
    materialize_contract = load_json(repo_root / MATERIALIZE_CONTRACT)
    gate = materialize_contract["input"]
    if approval.get("status") != gate["status"] or approval.get("reviewKind") != "typed-human-audio-source-approval":
        raise ApprovalError("normalized typed source approval status/kind mismatch")
    if approval.get("bindings") != expected_bindings(context):
        raise ApprovalError("normalized typed source approval bindings are stale")
    reviewer = approval.get("reviewerAlias")
    reviewed_at = approval.get("reviewedAt")
    reviewer_ok = reviewer_identity_complete(reviewer, reviewed_at)
    records = approval.get("records")
    if not isinstance(records, list) or len(records) != len(context["selected"]):
        raise ApprovalError("normalized typed approval source set mismatch")
    seen: set[str] = set()
    promotable: list[dict[str, Any]] = []
    for record in records:
        if not isinstance(record, dict):
            raise ApprovalError("normalized approval contains invalid record")
        key = record.get("sourceKey")
        source = context["selected"].get(key)
        if not source or key in seen:
            raise ApprovalError(f"unknown/duplicate approval sourceKey: {key!r}")
        seen.add(key)
        for field, expected in (
            ("reviewKind", source["reviewKind"]),
            ("target", source["target"]),
            ("reviewPath", source["reviewPath"]),
            ("sourcePath", source["sourcePath"]),
            ("sourceSha256", source["sha256"]),
            ("license", source["license"]),
            ("provider", source["provider"]),
            ("sourcePage", source["sourcePage"]),
            ("sourceKind", source["sourceKind"]),
        ):
            if record.get(field) != expected:
                raise ApprovalError(f"{key}: normalized approval provenance drift in {field}")
        checks = record.get("checks")
        if not isinstance(checks, dict) or set(checks) != set(contract["typedChecks"]):
            raise ApprovalError(f"{key}: normalized typed check set mismatch")
        normalized_checks = {
            check_id: normalize_check(check_id, checks[check_id], contract["typedChecks"][check_id])
            for check_id in contract["typedChecks"]
        }
        decision = record.get("sourceDecision", "")
        recomputed = source_eligible(contract, source, decision, normalized_checks, reviewer_ok)
        if record.get("sourceApprovedEligible") is not recomputed:
            raise ApprovalError(f"{key}: stored sourceApprovedEligible disagrees with current evidence")
        if recomputed:
            promotable.append(source)
    if seen != set(context["selected"]):
        raise ApprovalError("normalized typed approval source set drift")
    if not promotable:
        raise ApprovalError("no source is eligible for source-approved materialization")
    return materialize_contract, promotable


def materialize(approval_path: Path, upstream: list[Path], pack_root: Path, output_dir: Path, repo_root: Path = ROOT, replace: bool = False) -> dict[str, Any]:
    approval = load_json(approval_path)
    contract, promotable = validate_approval(approval, upstream, pack_root, repo_root)
    pack_root = pack_root.resolve()
    output_dir = output_dir.resolve()
    if output_dir.exists() and any(output_dir.iterdir()) and not replace:
        raise ApprovalError(f"output directory is not empty; use --replace explicitly: {output_dir}")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".source-approved-", dir=output_dir.parent))
    try:
        receipt_records = []
        for source in sorted(promotable, key=lambda x: x["sourceKey"]):
            src = pack_root / source["reviewPath"]
            actual = sha256_file(src)
            if actual != source["sha256"]:
                raise ApprovalError(f"{source['sourceKey']}: source bytes changed before materialization")
            dest = staging / source["outputRelative"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dest)
            output_sha = sha256_file(dest)
            if output_sha != actual:
                raise ApprovalError(f"{source['sourceKey']}: source-approved copy changed bytes")
            receipt_records.append({
                "sourceKey": source["sourceKey"],
                "reviewKind": source["reviewKind"],
                "target": source["target"],
                "sourcePath": source["sourcePath"],
                "sourceSha256": source["sha256"],
                "approvedRelativePath": source["outputRelative"],
                "approvedSha256": output_sha,
                "license": source["license"],
                "provider": source["provider"],
                "sourcePage": source["sourcePage"],
                "sourceKind": source["sourceKind"],
                "copyOnly": True,
                "sourceApproved": True,
                "derivedMasterApproved": False,
                "runtimeApproved": False,
                "releaseApproved": False,
            })
        receipt = {
            "version": 1,
            "status": contract["output"]["receiptStatus"],
            "typedApprovalEvidenceSha256": sha256_file(approval_path),
            "upstreamEvidenceSha256": collect_upstream(upstream, repo_root)["upstreamEvidenceSha256"],
            "approvedCount": len(receipt_records),
            "records": receipt_records,
            "rule": "Explicit human source-approved gate materialized original bytes unchanged. Reviewer identity/timestamp are revalidated; derived-master, Unity, Quest and release approval remain separate.",
        }
        (staging / contract["output"]["receiptFilename"]).write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        if output_dir.exists():
            if replace:
                shutil.rmtree(output_dir)
            else:
                output_dir.rmdir()
        os.replace(staging, output_dir)
        return receipt
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Materialize human-approved PROJECT OEN acquired source originals without processing them.")
    parser.add_argument("--approval", type=Path, required=True)
    parser.add_argument("--upstream", type=Path, action="append", required=True)
    parser.add_argument("--pack-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()
    try:
        receipt = materialize(args.approval.resolve(), [x.resolve() for x in args.upstream], args.pack_root, args.output, replace=args.replace)
    except ApprovalError as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"Materialized {receipt['approvedCount']} source-approved original(s); no derived/runtime/release approval promoted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
