#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

from music_family_selection_support import MATERIALIZE_CONTRACT, ROOT, SELECTION_CONTRACT, SelectionError, family_groups, load_json, load_normalized_audition, sha256_file
from normalize_music_family_selection import expected_bindings


def validate_selection(selection: dict[str, Any], audition_path: Path, repo_root: Path) -> tuple[dict, list[dict[str, Any]]]:
    context = load_normalized_audition(audition_path.resolve(), repo_root)
    materialize_contract = load_json(repo_root / MATERIALIZE_CONTRACT)
    selection_contract = load_json(repo_root / SELECTION_CONTRACT)
    gate = materialize_contract["input"]
    if selection.get("status") != gate["normalizedStatus"] or selection.get("reviewKind") != gate["reviewKind"]:
        raise SelectionError("normalized music family selection status/kind mismatch")
    if selection.get(gate["readyFlag"]) is not gate["readyFlagMustBe"]:
        raise SelectionError("music family selection is not ready for source materialization")
    if selection.get("bindings") != expected_bindings(context):
        raise SelectionError("normalized music family selection bindings are stale")
    if selection.get("unmappedFamiliesExcluded") != ["MUS_Warning_LowPulse"]:
        raise SelectionError("unmapped music-family exclusion drift")

    groups = {g["canonicalTarget"]: g for g in family_groups(context)}
    records = selection.get("records")
    if not isinstance(records, list) or len(records) != materialize_contract["materialization"]["expectedCanonicalCueCount"]:
        raise SelectionError("normalized selection must contain exactly five canonical records")
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            raise SelectionError("normalized selection contains invalid record")
        target = record.get("canonicalTarget")
        if target not in groups or target in seen:
            raise SelectionError(f"invalid/duplicate canonical target: {target!r}")
        seen.add(target)
        group = groups[target]
        if record.get("candidateFamily") != group["candidateFamily"] or record.get("decision") != "select":
            raise SelectionError(f"{target}: positive selection must preserve family and select decision")
        selected_file = record.get("selectedFile")
        eligible = {c["file"]: c for c in group["candidates"] if c["eligibleForSelection"]}
        if selected_file not in eligible:
            raise SelectionError(f"{target}: selected file is no longer eligible")
        candidate = eligible[selected_file]
        if record.get("selectedSha256") != candidate["sha256"]:
            raise SelectionError(f"{target}: selected SHA no longer matches audited candidate")
        out.append({
            "canonicalTarget": target,
            "candidateFamily": group["candidateFamily"],
            "sourceFilename": selected_file,
            "sourceSha256": candidate["sha256"],
        })
    if seen != set(groups):
        raise SelectionError("normalized selection canonical target set drift")
    return materialize_contract, out


def materialize(selection_path: Path, audition_path: Path, candidate_dir: Path, output_dir: Path, repo_root: Path = ROOT, replace: bool = False) -> dict[str, Any]:
    selection = load_json(selection_path)
    contract, selected = validate_selection(selection, audition_path, repo_root)
    candidate_dir = candidate_dir.resolve()
    output_dir = output_dir.resolve()
    if output_dir.exists() and any(output_dir.iterdir()) and not replace:
        raise SelectionError(f"output directory is not empty; use --replace explicitly: {output_dir}")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".music-selected-source-", dir=output_dir.parent))
    try:
        receipt_records = []
        for item in sorted(selected, key=lambda x: x["canonicalTarget"]):
            source = candidate_dir / item["sourceFilename"]
            if not source.is_file():
                raise SelectionError(f"selected candidate WAV missing: {item['sourceFilename']}")
            actual = sha256_file(source)
            if actual != item["sourceSha256"]:
                raise SelectionError(f"selected candidate hash mismatch for {item['sourceFilename']}: expected={item['sourceSha256']} actual={actual}")
            dest_name = contract["output"]["filenamePattern"].format(canonicalCueId=item["canonicalTarget"])
            dest = staging / dest_name
            shutil.copyfile(source, dest)
            output_sha = sha256_file(dest)
            if output_sha != actual:
                raise SelectionError(f"copy changed source bytes for {item['canonicalTarget']}")
            receipt_records.append({
                "canonicalTarget": item["canonicalTarget"],
                "candidateFamily": item["candidateFamily"],
                "sourceFilename": item["sourceFilename"],
                "sourceSha256": actual,
                "selectedSourceFilename": dest_name,
                "selectedSourceSha256": output_sha,
                "bytes": dest.stat().st_size,
                "copyOnly": True,
            })
        receipt = {
            "version": 1,
            "status": contract["output"]["receiptStatus"],
            "normalizedSelectionSha256": sha256_file(selection_path),
            "normalizedAuditionSha256": sha256_file(audition_path),
            "selectedCount": len(receipt_records),
            "records": receipt_records,
            "unmappedFamiliesMaterialized": [],
            "sourceApprovalPromoted": False,
            "derivedMasterApprovalPromoted": False,
            "runtimeApprovalPromoted": False,
            "rule": "Human-selected audited candidate bytes copied under canonical cue filenames. No processing or downstream approval is implied.",
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
    parser = argparse.ArgumentParser(description="Materialize five human-selected PROJECT OEN music source candidates without processing them.")
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--audition", type=Path, required=True)
    parser.add_argument("--candidate-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()
    try:
        receipt = materialize(args.selection.resolve(), args.audition.resolve(), args.candidate_dir, args.output, replace=args.replace)
    except SelectionError as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"Materialized {receipt['selectedCount']} selected music sources; no processing/approval promotion performed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
