#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from music_family_selection_support import ROOT, SELECTION_CONTRACT, SelectionError, family_groups, load_json, load_normalized_audition


def expected_bindings(context: dict) -> dict:
    return {
        "candidateAuditSha256": context["auditSha256"],
        "normalizedAuditionSha256": context["reviewSha256"],
        "candidateHashes": {name: context["fileByName"][name]["sha256"] for name in sorted(context["fileByName"])},
    }


def normalize(payload: dict[str, Any], audition_path: Path, repo_root: Path = ROOT, require_complete: bool = False) -> dict[str, Any]:
    context = load_normalized_audition(audition_path.resolve(), repo_root)
    contract = load_json(repo_root / SELECTION_CONTRACT)
    export = contract["selectionExport"]
    if payload.get("version") != export["version"] or payload.get("status") != export["status"]:
        raise SelectionError("family selection export version/status mismatch")
    if payload.get("bindings") != expected_bindings(context):
        raise SelectionError("family selection bindings are stale")
    reviewer = payload.get("reviewerAlias")
    reviewed_at = payload.get("reviewedAt")
    if not isinstance(reviewer, str) or not isinstance(reviewed_at, str):
        raise SelectionError("reviewerAlias/reviewedAt must be text")

    groups = {g["canonicalTarget"]: g for g in family_groups(context)}
    families = payload.get("families")
    if not isinstance(families, list) or len(families) != len(groups):
        raise SelectionError(f"family selection must contain exactly {len(groups)} canonical targets")
    allowed = set(contract["decisionValues"])
    seen: set[str] = set()
    normalized = []
    decided = 0
    selected = 0
    for raw in families:
        if not isinstance(raw, dict):
            raise SelectionError("family selection contains invalid record")
        target = raw.get("canonicalTarget")
        if target not in groups or target in seen:
            raise SelectionError(f"unknown/duplicate canonical target: {target!r}")
        seen.add(target)
        group = groups[target]
        if raw.get("candidateFamily") != group["candidateFamily"]:
            raise SelectionError(f"{target}: candidate family drift")
        decision = raw.get("decision", "")
        selected_file = raw.get("selectedFile", "")
        note = raw.get("note", "")
        if decision and decision not in allowed:
            raise SelectionError(f"{target}: invalid decision {decision!r}")
        if not isinstance(selected_file, str) or not isinstance(note, str):
            raise SelectionError(f"{target}: selectedFile/note must be text")
        eligible = {c["file"]: c for c in group["candidates"] if c["eligibleForSelection"]}
        selected_record = None
        if decision == "select":
            if selected_file not in eligible:
                raise SelectionError(f"{target}: selected file is not an eligible keep+all-pass candidate")
            selected_record = eligible[selected_file]
            selected += 1
        elif selected_file:
            raise SelectionError(f"{target}: selectedFile must be empty unless decision == select")
        if decision:
            decided += 1
        normalized.append({
            "canonicalTarget": target,
            "candidateFamily": group["candidateFamily"],
            "decision": decision,
            "selectedFile": selected_file,
            "selectedSha256": selected_record["sha256"] if selected_record else None,
            "note": note.strip(),
        })
    complete = bool(reviewer.strip()) and bool(reviewed_at.strip()) and decided == len(groups)
    if require_complete and not complete:
        raise SelectionError(f"music family selection incomplete: reviewer={bool(reviewer.strip())}, reviewedAt={bool(reviewed_at.strip())}, decisions={decided}/{len(groups)}")
    ready = complete and selected == len(groups)
    return {
        "version": 1,
        "status": contract["normalizedStatus"],
        "reviewKind": "music-canonical-family-selection",
        "reviewedAt": reviewed_at,
        "reviewerAlias": reviewer.strip(),
        "bindings": expected_bindings(context),
        "coverage": {"decided": decided, "total": len(groups), "selected": selected, "complete": complete},
        "readyForSourceMaterialization": ready,
        "records": sorted(normalized, key=lambda x: x["canonicalTarget"]),
        "unmappedFamiliesExcluded": ["MUS_Warning_LowPulse"],
        "rule": "Hash-bound human family-selection evidence only. Negative outcomes remain valid; no source/runtime/release approval is promoted.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize human PROJECT OEN music family selection without forcing a positive result.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--audition", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    try:
        payload = load_json(args.input)
        result = normalize(payload, args.audition, require_complete=args.require_complete)
    except SelectionError as exc:
        print(f"ERROR: {exc}")
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    c = result["coverage"]
    print(f"OK music family selection: {c['decided']}/{c['total']} decided, {c['selected']} selected, ready={result['readyForSourceMaterialization']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
