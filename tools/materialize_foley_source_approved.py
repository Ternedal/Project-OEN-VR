#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from foley_human_review_support import FoleyReviewError, evaluate_normalized, expected_bindings, load_context, load_json, sha256_file


def validate_normalized(normalized: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    contract = context["reviewContract"]
    if normalized.get("version") != 1 or normalized.get("status") != contract["normalizedStatus"]:
        raise FoleyReviewError("expected normalized human Foley review evidence")
    if normalized.get("reviewKind") != "physical-foley-human-source-approval":
        raise FoleyReviewError("unexpected Foley reviewKind")
    if normalized.get("bindings") != expected_bindings(context):
        raise FoleyReviewError("normalized Foley review bindings are stale")
    cue_reviews = normalized.get("cueReviews")
    if not isinstance(cue_reviews, list) or len(cue_reviews) != contract["expectedCueCount"]:
        raise FoleyReviewError("normalized Foley review must contain exactly 17 cue reviews")
    by_cue = {x.get("cueId"): x for x in cue_reviews if isinstance(x, dict) and isinstance(x.get("cueId"), str)}
    if set(by_cue) != set(context["cueRecords"]):
        raise FoleyReviewError("normalized Foley cue set no longer matches current session")
    for cue_id, source_records in context["cueRecords"].items():
        cue = by_cue[cue_id]
        takes = cue.get("takes")
        if not isinstance(takes, list) or len(takes) != len(source_records):
            raise FoleyReviewError(f"{cue_id}: normalized take count drift")
        for stored, source in zip(takes, source_records, strict=True):
            if not isinstance(stored, dict):
                raise FoleyReviewError(f"{cue_id}: invalid normalized take")
            expected = (source["relativePath"], source["filename"], source["variant"], source["sha256"])
            actual = (stored.get("relativePath"), stored.get("filename"), stored.get("variant"), stored.get("sourceSha256"))
            if actual != expected:
                raise FoleyReviewError(f"{cue_id}: normalized take identity drift: {source['relativePath']}")
    evaluation = evaluate_normalized(normalized, context)
    if normalized.get("reviewComplete") != evaluation["reviewComplete"]:
        raise FoleyReviewError("stored reviewComplete does not match recomputed human evidence")
    if normalized.get("readyForSourceMaterialization") != evaluation["readyForSourceMaterialization"]:
        raise FoleyReviewError("stored readyForSourceMaterialization does not match recomputed human evidence")
    return evaluation


def materialize(session_root: Path, normalized_path: Path, output_root: Path, replace: bool = False) -> dict[str, Any]:
    context = load_context(session_root)
    normalized = load_json(normalized_path)
    evaluation = validate_normalized(normalized, context)
    if not evaluation["readyForSourceMaterialization"]:
        raise FoleyReviewError("Foley human review is valid evidence but is not eligible for source-approved materialization")

    contract = context["materializeContract"]
    if contract.get("input", {}).get("status") != normalized.get("status"):
        raise FoleyReviewError("Foley materialization contract input status drift")
    materialization = contract.get("materialization", {})
    if materialization.get("copyOnly") is not True or materialization.get("sourceAndOutputShaMustMatch") is not True:
        raise FoleyReviewError("Foley materialization contract must remain copy-only with exact SHA preservation")

    output_root = output_root.resolve()
    approved_dir = output_root / contract["output"]["directory"]
    records: list[dict[str, Any]] = []
    for cue_id, source_records in context["cueRecords"].items():
        for source in source_records:
            source_path = context["sessionRoot"] / source["relativePath"]
            target_path = approved_dir / cue_id / source["filename"]
            if target_path.exists() and not replace:
                raise FoleyReviewError(f"refusing to overwrite existing approved source without --replace: {target_path}")
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_path, target_path)
            digest = sha256_file(target_path)
            if digest != source["sha256"] or digest != sha256_file(source_path):
                target_path.unlink(missing_ok=True)
                raise FoleyReviewError(f"copy SHA mismatch for {source['relativePath']}")
            records.append({
                "cueId": cue_id,
                "variant": source["variant"],
                "filename": source["filename"],
                "sourceRelativePath": source["relativePath"],
                "outputRelativePath": target_path.relative_to(output_root).as_posix(),
                "sha256": digest,
                "bytes": target_path.stat().st_size,
                "sourceApproved": True,
                "derivedMasterApproved": False,
                "UnityIntegrated": False,
                "QuestApproved": False,
                "releaseApproved": False,
            })

    if len(records) != materialization.get("expectedTakeCount"):
        raise FoleyReviewError(f"materialized {len(records)} sources, expected {materialization.get('expectedTakeCount')}")
    receipt = {
        "version": 1,
        "status": contract["output"]["receiptStatus"],
        "reviewEvidenceSha256": sha256_file(normalized_path),
        "technicalReceiptSha256": context["technicalReceiptSha256"],
        "provenanceSha256": context["provenanceSha256"],
        "reviewerAlias": normalized["reviewerAlias"],
        "reviewedAt": normalized["reviewedAt"],
        "cueCount": len(context["cueRecords"]),
        "sourceCount": len(records),
        "copyOnly": True,
        "records": records,
        "rule": "These 73 raw Foley originals were explicitly source-approved through hash-bound human evidence. No derived-master, Unity, Quest or release approval is implied.",
    }
    receipt_path = output_root / contract["output"]["receiptFilename"]
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description="Explicitly materialize only fully human-approved PROJECT OEN raw Foley originals by byte-for-byte copy.")
    parser.add_argument("--session", type=Path, required=True)
    parser.add_argument("--review", type=Path, required=True, help="Normalized Foley human review JSON")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()
    try:
        receipt = materialize(args.session, args.review, args.output, replace=args.replace)
    except FoleyReviewError as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"Foley source-approved materialization PASS: {receipt['cueCount']} cues / {receipt['sourceCount']} exact raw sources")
    print("Derived-master, Unity, Quest and release approval remain pending.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
