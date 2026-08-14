#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

from radio_vo_human_review_support import DEFAULT_SESSION, ROOT, ReviewError, load_context, load_json, sha256_file

CONTRACT = ROOT / "content/audio/radio_vo_selected_dry_contract.source.json"


def materialize(normalized_review: Path, session_root: Path, repo_root: Path = ROOT, output_dir: Path | None = None, replace: bool = False) -> dict[str, Any]:
    contract = load_json(repo_root / "content/audio/radio_vo_selected_dry_contract.source.json")
    context = load_context(session_root, repo_root)
    review = load_json(normalized_review)
    required = contract["input"]
    if review.get("status") != required["normalizedStatus"] or review.get("reviewKind") != required["reviewKind"]:
        raise ReviewError("normalized human review status/kind mismatch")
    if review.get(required["readyFlag"]) is not required["readyFlagMustBe"]:
        raise ReviewError("human review is not ready for dry master selection")
    if review.get("bindings") != context["bindings"]:
        raise ReviewError("normalized review bindings are stale")

    records = review.get("records")
    expected = {cue["cueId"]: cue for cue in context["cues"]}
    if not isinstance(records, list) or len(records) != len(expected):
        raise ReviewError("normalized review must contain exactly 9 cue records")
    selected: list[dict[str, Any]] = []
    seen: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            raise ReviewError("normalized review contains invalid cue record")
        cue_id = record.get("cueId")
        if cue_id not in expected or cue_id in seen:
            raise ReviewError(f"invalid/duplicate selected cue: {cue_id!r}")
        seen.add(cue_id)
        if record.get("decision") != "select":
            raise ReviewError(f"{cue_id}: ready review contains non-select decision")
        filename = record.get("selectedFilename")
        selected_sha = record.get("selectedSha256")
        candidates = {item["filename"]: item for item in expected[cue_id]["candidates"]}
        if filename not in candidates:
            raise ReviewError(f"{cue_id}: selected filename is not one of the three accepted takes")
        if selected_sha != candidates[filename]["sha256"]:
            raise ReviewError(f"{cue_id}: selected SHA does not match current technical receipt")
        selected.append({"cueId": cue_id, "sourceFilename": filename, "sourceSha256": selected_sha})
    if seen != set(expected):
        raise ReviewError("normalized review cue set drift")

    session_root = session_root.resolve()
    output = (output_dir or session_root / contract["output"]["directory"]).resolve()
    if output.exists() and any(output.iterdir()) and not replace:
        raise ReviewError(f"output directory is not empty; use --replace explicitly: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".radio-vo-selected-dry-", dir=output.parent))
    try:
        receipt_records = []
        for item in sorted(selected, key=lambda x: x["cueId"]):
            source = session_root / "takes" / item["sourceFilename"]
            dest_name = contract["output"]["filenamePattern"].format(cueId=item["cueId"])
            dest = staging / dest_name
            shutil.copyfile(source, dest)
            output_sha = sha256_file(dest)
            if output_sha != item["sourceSha256"]:
                raise ReviewError(f"{item['cueId']}: copy changed source bytes")
            receipt_records.append({
                "cueId": item["cueId"],
                "sourceFilename": item["sourceFilename"],
                "sourceSha256": item["sourceSha256"],
                "selectedDryFilename": dest_name,
                "selectedDrySha256": output_sha,
                "bytes": dest.stat().st_size,
                "copyOnly": True,
            })
        receipt = {
            "version": 1,
            "status": contract["output"]["receiptStatus"],
            "normalizedHumanReviewSha256": sha256_file(normalized_review),
            "humanReviewBindings": context["bindings"],
            "selectedCount": len(receipt_records),
            "records": receipt_records,
            "sourceApprovalPromoted": False,
            "derivedMasterApprovalPromoted": False,
            "runtimeApprovalPromoted": False,
            "rule": "Selected dry sources are byte-for-byte materialized from human-selected takes. No processing or downstream approval is implied.",
        }
        (staging / contract["output"]["receiptFilename"]).write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        if output.exists():
            if replace:
                shutil.rmtree(output)
            else:
                output.rmdir()
        os.replace(staging, output)
        return receipt
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Materialize nine human-selected PROJECT OEN radio VO dry sources without processing them.")
    parser.add_argument("--review", type=Path, required=True, help="Normalized radio VO human review JSON")
    parser.add_argument("--session", type=Path, default=ROOT / DEFAULT_SESSION)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()
    try:
        receipt = materialize(args.review.resolve(), args.session, output_dir=args.output, replace=args.replace)
    except ReviewError as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"Materialized {receipt['selectedCount']} selected dry VO sources; no processing/approval promotion performed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
