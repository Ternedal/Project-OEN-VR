from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MAIN_RECEIPT = Path("content/audio/acquisition_receipt.source.json")
EXT_RECEIPT = Path("content/audio/acquisition_extension_receipt.source.json")
EXT_SHORTLIST = Path("content/audio/acquisition_extension_member_shortlist.source.json")
FIELD_RECEIPT = Path("content/audio/acquisition_field_backlog_receipt.source.json")
FIELD_FINAL_RECEIPT = Path("content/audio/acquisition_field_backlog_final_receipt.source.json")
APPROVAL_CONTRACT = Path("content/audio/source_approval_contract.source.json")
MATERIALIZE_CONTRACT = Path("content/audio/source_approved_materialization_contract.source.json")
LISTENING_QA = Path("content/audio/listening_qa.source.json")


class ApprovalError(RuntimeError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ApprovalError(f"Cannot parse {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ApprovalError(f"{path}: root must be an object")
    return value


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def records_index(data: dict[str, Any], owner: str) -> dict[str, dict[str, Any]]:
    records = data.get("records")
    if not isinstance(records, list):
        raise ApprovalError(f"{owner}: records must be a list")
    out: dict[str, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("target"), str):
            raise ApprovalError(f"{owner}: invalid record")
        target = record["target"]
        if target in out:
            raise ApprovalError(f"{owner}: duplicate target {target}")
        out[target] = record
    return out


def current_field_records(repo_root: Path = ROOT) -> dict[str, dict[str, Any]]:
    merged = records_index(load_json(repo_root / FIELD_RECEIPT), "field receipt")
    final_path = repo_root / FIELD_FINAL_RECEIPT
    if final_path.is_file():
        final = records_index(load_json(final_path), "final field receipt")
        duplicates = sorted(set(merged) & set(final))
        if duplicates:
            raise ApprovalError(f"duplicate field target across receipts: {duplicates}")
        merged.update(final)
    return merged


def current_source_context(repo_root: Path = ROOT) -> dict[str, dict[str, Any]]:
    main = records_index(load_json(repo_root / MAIN_RECEIPT), "main receipt")
    ext = records_index(load_json(repo_root / EXT_RECEIPT), "extension receipt")
    field = current_field_records(repo_root)
    shortlist = load_json(repo_root / EXT_SHORTLIST).get("members")
    if not isinstance(shortlist, list):
        raise ApprovalError("extension shortlist members missing")
    context: dict[str, dict[str, Any]] = {}
    for target, record in main.items():
        filename = record.get("filename")
        sha = record.get("sha256")
        if not isinstance(filename, str) or not isinstance(sha, str) or len(sha) != 64:
            raise ApprovalError(f"main receipt identity invalid: {target}")
        context[f"main::{target}"] = {
            "sourceKey": f"main::{target}", "reviewKind": "main-acquired-originals", "target": target,
            "sourcePath": filename, "reviewPath": f"audio/main/{filename}", "sha256": sha,
            "license": record.get("license"), "provider": record.get("provider"), "sourcePage": record.get("sourcePage"),
            "sourceKind": "direct-original", "outputRelative": f"main/{target}/{Path(filename).name}",
        }
    ocean = ext.get("AMB_OCEAN_ALT")
    if ocean:
        filename, sha = ocean.get("filename"), ocean.get("sha256")
        if not isinstance(filename, str) or not isinstance(sha, str) or len(sha) != 64:
            raise ApprovalError("extension ocean identity invalid")
        review_path = f"audio/ocean/{filename}"
        context[f"extension::{review_path}"] = {
            "sourceKey": f"extension::{review_path}", "reviewKind": "extension-source-selection", "target": "AMB_OCEAN_ALT",
            "sourcePath": filename, "reviewPath": review_path, "sha256": sha,
            "license": ocean.get("license"), "provider": ocean.get("provider"), "sourcePage": ocean.get("sourcePage"),
            "sourceKind": "direct-original", "outputRelative": f"extension/AMB_OCEAN_ALT/{Path(filename).name}",
        }
    for member in shortlist:
        if not isinstance(member, dict):
            raise ApprovalError("extension shortlist contains invalid member")
        target, source_path, sha = member.get("archiveTarget"), member.get("path"), member.get("sha256")
        if target not in {"SFX_WOOD_PACK_ALT", "SFX_CLOTH_PACK_ALT"} or not isinstance(source_path, str) or not isinstance(sha, str) or len(sha) != 64:
            raise ApprovalError("extension shortlist member identity invalid")
        parent = ext.get(target)
        if not parent:
            raise ApprovalError(f"extension receipt missing parent target {target}")
        folder = "wood" if target == "SFX_WOOD_PACK_ALT" else "cloth"
        review_path = f"audio/{folder}/{Path(source_path).name}"
        context[f"extension::{review_path}"] = {
            "sourceKey": f"extension::{review_path}", "reviewKind": "extension-source-selection", "target": target,
            "sourcePath": source_path, "reviewPath": review_path, "sha256": sha,
            "license": parent.get("license"), "provider": parent.get("provider"), "sourcePage": parent.get("sourcePage"),
            "sourceKind": "archive-member", "outputRelative": f"extension/{target}/{Path(source_path).name}",
        }
    for target, record in field.items():
        filename, sha = record.get("filename"), record.get("sha256")
        if not isinstance(filename, str) or not isinstance(sha, str) or len(sha) != 64:
            raise ApprovalError(f"field receipt identity invalid: {target}")
        context[f"field::{target}"] = {
            "sourceKey": f"field::{target}", "reviewKind": "field-backlog-source-selection", "target": target,
            "sourcePath": filename, "reviewPath": f"audio/field/{filename}", "sha256": sha,
            "license": record.get("license"), "provider": record.get("provider"), "sourcePage": record.get("sourcePage"),
            "sourceKind": "direct-original", "outputRelative": f"field/{target}/{Path(filename).name}",
        }
    return context


def collect_upstream(review_paths: list[Path], repo_root: Path = ROOT) -> dict[str, Any]:
    contract = load_json(repo_root / APPROVAL_CONTRACT)
    current = current_source_context(repo_root)
    accepted_kinds = set(contract["upstreamEvidence"]["acceptedKinds"])
    expected_decisions = contract["upstreamEvidence"]["eligibleUpstreamDecisions"]
    evidence_sha: dict[str, str] = {}
    selected: dict[str, dict[str, Any]] = {}
    for path in review_paths:
        path = path.resolve()
        review = load_json(path)
        kind = review.get("reviewKind")
        if review.get("status") != contract["upstreamEvidence"]["normalizedStatus"] or kind not in accepted_kinds:
            raise ApprovalError(f"unsupported upstream review evidence: {path}")
        if kind in evidence_sha:
            raise ApprovalError(f"only one upstream evidence file per reviewKind is allowed: {kind}")
        evidence_sha[kind] = sha256_file(path)
        records = review.get("records")
        if not isinstance(records, list):
            raise ApprovalError(f"{kind}: normalized records missing")
        for record in records:
            if not isinstance(record, dict):
                raise ApprovalError(f"{kind}: invalid normalized record")
            source_key = None
            decision = None
            source_sha = record.get("sourceSha256")
            if kind == "main-acquired-originals":
                source_key = f"main::{record.get('target')}"
                decision = record.get("disposition")
            elif kind == "extension-source-selection":
                source_key = f"extension::{record.get('reviewPath')}"
                decision = record.get("decision")
            elif kind == "field-backlog-source-selection":
                source_key = f"field::{record.get('target')}"
                decision = record.get("decision")
            source = current.get(source_key)
            if not source:
                raise ApprovalError(f"{kind}: source no longer exists in current provenance: {source_key}")
            if source_sha != source["sha256"]:
                raise ApprovalError(f"{source_key}: upstream evidence SHA no longer matches current provenance")
            if decision == expected_decisions[kind]:
                if source_key in selected:
                    raise ApprovalError(f"duplicate shortlisted source: {source_key}")
                selected[source_key] = source
    if not selected:
        raise ApprovalError("no upstream candidate-pass/keep source is eligible for typed approval review")
    return {"contract": contract, "current": current, "selected": selected, "upstreamEvidenceSha256": evidence_sha}


def verify_pack_sources(pack_root: Path, sources: dict[str, dict[str, Any]]) -> None:
    pack_root = pack_root.resolve()
    for key, source in sources.items():
        path = pack_root / source["reviewPath"]
        if not path.is_file():
            raise ApprovalError(f"shortlisted source bytes missing from audition pack: {source['reviewPath']}")
        actual = sha256_file(path)
        if actual != source["sha256"]:
            raise ApprovalError(f"{key}: audition-pack source SHA mismatch expected={source['sha256']} actual={actual}")


def expected_bindings(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "upstreamEvidenceSha256": context["upstreamEvidenceSha256"],
        "sources": {key: context["selected"][key]["sha256"] for key in sorted(context["selected"])},
    }
