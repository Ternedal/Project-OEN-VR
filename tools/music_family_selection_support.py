from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
AUDIT = Path("content/audio/music_candidate_audit.source.json")
AUDIO_CUES = Path("content/audio/audio_cues.source.json")
SELECTION_CONTRACT = Path("content/audio/music_family_selection_contract.source.json")
MATERIALIZE_CONTRACT = Path("content/audio/music_selected_source_contract.source.json")


class SelectionError(RuntimeError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SelectionError(f"Cannot parse {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SelectionError(f"{path}: root must be an object")
    return value


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def expected_checks(file_record: dict[str, Any]) -> set[str]:
    checks = {"speechSpace", "genreFit", "dramaturgyFit", "technicalStructure"}
    checks.add("loopSeam" if file_record.get("loop") is True else "endingShape")
    return checks


def audit_context(repo_root: Path = ROOT) -> dict[str, Any]:
    audit_path = repo_root / AUDIT
    cues_path = repo_root / AUDIO_CUES
    audit = load_json(audit_path)
    audio_cues = load_json(cues_path)
    files = audit.get("files")
    mappings = audit.get("canonicalMappings")
    unmapped = audit.get("unmappedFamilies")
    if audit.get("status") != "artifact-audited-audition-ready-not-source-approved":
        raise SelectionError("music candidate audit is not audition-ready")
    if not isinstance(files, list) or len(files) != 14:
        raise SelectionError("music candidate audit must contain exactly 14 files")
    if not isinstance(mappings, list) or len(mappings) != 5:
        raise SelectionError("music candidate audit must contain exactly five canonical mappings")
    if not isinstance(unmapped, list) or len(unmapped) != 1 or unmapped[0].get("candidateFamily") != "MUS_Warning_LowPulse":
        raise SelectionError("unmapped warning-family policy drift")

    cue_ids = {x.get("id") for x in audio_cues.get("cues", []) if isinstance(x, dict)}
    mapping_by_target: dict[str, str] = {}
    for mapping in mappings:
        if not isinstance(mapping, dict):
            raise SelectionError("invalid canonical mapping")
        target = mapping.get("canonicalCueId")
        family = mapping.get("candidateFamily")
        if not isinstance(target, str) or not isinstance(family, str) or target in mapping_by_target:
            raise SelectionError("duplicate/invalid canonical music mapping")
        if target not in cue_ids:
            raise SelectionError(f"canonical music target is absent from audio cue catalog: {target}")
        mapping_by_target[target] = family

    file_by_name: dict[str, dict[str, Any]] = {}
    for record in files:
        if not isinstance(record, dict):
            raise SelectionError("invalid music candidate record")
        filename = record.get("file")
        sha = record.get("sha256")
        family = record.get("event_id")
        target = record.get("canonicalTarget")
        status = record.get("mappingStatus")
        if not isinstance(filename, str) or filename in file_by_name:
            raise SelectionError(f"duplicate/invalid candidate filename: {filename!r}")
        if not isinstance(sha, str) or len(sha) != 64:
            raise SelectionError(f"invalid candidate SHA-256: {filename}")
        if family == "MUS_Warning_LowPulse":
            if target is not None or status != "unmapped-extra-candidate":
                raise SelectionError("warning-family candidate acquired a canonical binding")
        else:
            if target not in mapping_by_target or mapping_by_target[target] != family or status != "candidate-for-canonical-audition":
                raise SelectionError(f"candidate mapping drift: {filename}")
        file_by_name[filename] = record
    return {
        "audit": audit,
        "auditPath": audit_path,
        "auditSha256": sha256_file(audit_path),
        "mappingByTarget": mapping_by_target,
        "fileByName": file_by_name,
    }


def load_normalized_audition(path: Path, repo_root: Path = ROOT) -> dict[str, Any]:
    context = audit_context(repo_root)
    review = load_json(path)
    if review.get("version") != 1 or review.get("status") != "human-music-audition-evidence-unapproved":
        raise SelectionError("normalized music audition is not a complete unapproved evidence file")
    if not isinstance(review.get("reviewedAt"), str) or not review["reviewedAt"].strip():
        raise SelectionError("normalized music audition reviewedAt is missing")
    if not isinstance(review.get("reviewerRole"), str) or not review["reviewerRole"].strip():
        raise SelectionError("normalized music audition reviewerRole is missing")
    records = review.get("records")
    if not isinstance(records, list) or len(records) != len(context["fileByName"]):
        raise SelectionError("normalized music audition must contain exactly the current 14 candidates")
    by_name: dict[str, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict):
            raise SelectionError("normalized music audition contains invalid record")
        filename = record.get("file")
        src = context["fileByName"].get(filename)
        if not src or filename in by_name:
            raise SelectionError(f"unknown/duplicate audition candidate: {filename!r}")
        for key, expected in (("sha256", src["sha256"]), ("candidateFamily", src["event_id"]), ("canonicalTarget", src["canonicalTarget"]), ("mappingStatus", src["mappingStatus"])):
            if record.get(key) != expected:
                raise SelectionError(f"{filename}: normalized audition {key} drift")
        checks = record.get("checks")
        required = expected_checks(src)
        if not isinstance(checks, dict) or set(checks) != required:
            raise SelectionError(f"{filename}: audition check set mismatch")
        eligible = record.get("fit") == "keep" and all(isinstance(checks[c], dict) and checks[c].get("result") == "pass" for c in required)
        enriched = dict(record)
        enriched["eligibleForSelection"] = eligible
        by_name[filename] = enriched
    if set(by_name) != set(context["fileByName"]):
        raise SelectionError("normalized music audition candidate set drift")
    context["review"] = review
    context["reviewPath"] = path
    context["reviewSha256"] = sha256_file(path)
    context["reviewByName"] = by_name
    return context


def family_groups(context: dict[str, Any]) -> list[dict[str, Any]]:
    groups = []
    for target, family in context["mappingByTarget"].items():
        candidates = []
        for filename, src in context["fileByName"].items():
            if src.get("canonicalTarget") != target:
                continue
            review = context["reviewByName"][filename]
            candidates.append({
                "file": filename,
                "sha256": src["sha256"],
                "variant": src.get("variant"),
                "loop": src.get("loop"),
                "durationSeconds": src.get("duration_seconds"),
                "fit": review.get("fit"),
                "eligibleForSelection": review["eligibleForSelection"],
            })
        if not candidates:
            raise SelectionError(f"no candidates found for canonical target {target}")
        groups.append({"canonicalTarget": target, "candidateFamily": family, "candidates": sorted(candidates, key=lambda x: x["file"])})
    return sorted(groups, key=lambda x: x["canonicalTarget"])
