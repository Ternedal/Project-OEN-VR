from __future__ import annotations

import hashlib
import json
import math
import wave
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = Path("content/audio/derived_master_contract.source.json")
SOURCE_APPROVAL_CONTRACT = Path("content/audio/source_approval_contract.source.json")


class DerivedError(RuntimeError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise DerivedError(f"Cannot parse {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise DerivedError(f"{path}: root must be an object")
    return value


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def approved_source_index(receipt: dict[str, Any], contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    required = contract["sourceApprovedReceipt"]
    if receipt.get("status") != required["requiredStatus"]:
        raise DerivedError(f"source-approved receipt status mismatch: {receipt.get('status')!r}")
    records = receipt.get("records")
    if not isinstance(records, list) or not records:
        raise DerivedError("source-approved receipt has no records")
    out: dict[str, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict):
            raise DerivedError("source-approved receipt contains invalid record")
        key = record.get("sourceKey")
        sha = record.get("approvedSha256")
        if not isinstance(key, str) or not isinstance(sha, str) or len(sha) != 64 or key in out:
            raise DerivedError("source-approved receipt contains invalid/duplicate source identity")
        if record.get(required["requiredRecordFlag"]) is not required["requiredRecordFlagValue"]:
            raise DerivedError(f"source-approved receipt record is not approved: {key}")
        out[key] = record
    return out


def submission_records(submission: dict[str, Any], sources: dict[str, dict[str, Any]], contract: dict[str, Any]) -> list[dict[str, Any]]:
    if submission.get("version") != 1 or submission.get("status") != contract["submission"]["status"]:
        raise DerivedError("derived master submission version/status mismatch")
    records = submission.get("masters")
    if not isinstance(records, list) or not records:
        raise DerivedError("derived master submission must contain at least one master")
    required_fields = set(contract["submission"]["requiredPerMaster"])
    seen_ids: set[str] = set()
    seen_files: set[str] = set()
    normalized = []
    for raw in records:
        if not isinstance(raw, dict) or not required_fields <= set(raw):
            raise DerivedError("derived master submission record is incomplete")
        master_id = raw.get("masterId")
        source_key = raw.get("sourceKey")
        filename = raw.get("filename")
        source_sha = raw.get("sourceApprovedSha256")
        intended = raw.get("intendedUse")
        recipe = raw.get("editRecipe")
        if not isinstance(master_id, str) or not master_id.strip() or master_id in seen_ids:
            raise DerivedError(f"invalid/duplicate masterId: {master_id!r}")
        if not isinstance(filename, str) or not filename.lower().endswith(".wav") or filename in seen_files or Path(filename).name != filename:
            raise DerivedError(f"invalid/duplicate derived filename: {filename!r}")
        source = sources.get(source_key)
        if not source or source_sha != source.get("approvedSha256"):
            raise DerivedError(f"{master_id}: source-approved binding mismatch")
        if not isinstance(intended, str) or not intended.strip():
            raise DerivedError(f"{master_id}: intendedUse is required")
        if not isinstance(recipe, list) or not recipe:
            raise DerivedError(f"{master_id}: editRecipe must contain at least one explicit operation")
        clean_recipe = []
        for operation in recipe:
            if not isinstance(operation, dict) or not isinstance(operation.get("operation"), str) or not operation["operation"].strip():
                raise DerivedError(f"{master_id}: invalid edit recipe operation")
            details = operation.get("details", "")
            if not isinstance(details, str) or not details.strip():
                raise DerivedError(f"{master_id}: edit recipe operation needs details")
            clean_recipe.append({"operation": operation["operation"].strip(), "details": details.strip()})
        seen_ids.add(master_id); seen_files.add(filename)
        normalized.append({
            "masterId": master_id.strip(), "sourceKey": source_key, "sourceApprovedSha256": source_sha,
            "filename": filename, "intendedUse": intended.strip(), "editRecipe": clean_recipe,
        })
    return normalized


def probe_pcm24_wav(path: Path) -> dict[str, Any]:
    try:
        with wave.open(str(path), "rb") as wav:
            channels = wav.getnchannels(); rate = wav.getframerate(); width = wav.getsampwidth(); frames = wav.getnframes(); comptype = wav.getcomptype()
            raw = wav.readframes(frames)
    except Exception as exc:
        raise DerivedError(f"cannot read WAV {path.name}: {exc}") from exc
    if width != 3:
        raise DerivedError(f"{path.name}: expected 24-bit PCM (3-byte samples), got sample width {width}")
    if comptype != "NONE":
        raise DerivedError(f"{path.name}: compressed WAV is not allowed")
    if len(raw) % 3:
        raise DerivedError(f"{path.name}: malformed 24-bit PCM byte length")
    peak = 0; full_scale = 0
    for i in range(0, len(raw), 3):
        value = raw[i] | (raw[i+1] << 8) | (raw[i+2] << 16)
        if value & 0x800000:
            value -= 1 << 24
        absolute = abs(value)
        if absolute > peak:
            peak = absolute
        if value in (-8388608, 8388607):
            full_scale += 1
    peak_dbfs = -math.inf if peak == 0 else 20.0 * math.log10(peak / 8388608.0)
    return {
        "codec": "pcm_s24le", "sampleRateHz": rate, "bitDepth": 24, "channels": channels,
        "frames": frames, "durationSec": frames / rate if rate else 0.0,
        "peakDbfs": round(peak_dbfs, 6) if math.isfinite(peak_dbfs) else None,
        "fullScaleSampleCount": full_scale,
    }


def validate_technical_submission(submission_path: Path, source_receipt_path: Path, masters_dir: Path, repo_root: Path = ROOT) -> dict[str, Any]:
    contract = load_json(repo_root / CONTRACT)
    source_receipt = load_json(source_receipt_path)
    sources = approved_source_index(source_receipt, contract)
    submission = load_json(submission_path)
    masters = submission_records(submission, sources, contract)
    technical = contract["technicalIntake"]
    receipt_records = []
    for master in masters:
        path = masters_dir / master["filename"]
        if not path.is_file():
            raise DerivedError(f"derived master file missing: {master['filename']}")
        derived_sha = sha256_file(path)
        if technical["derivedShaMustDifferFromSourceSha"] and derived_sha == master["sourceApprovedSha256"]:
            raise DerivedError(f"{master['masterId']}: derived bytes equal source-approved original; use original directly")
        probe = probe_pcm24_wav(path)
        if probe["sampleRateHz"] != technical["sampleRateHz"] or probe["bitDepth"] != technical["bitDepth"] or probe["channels"] not in technical["channelsAllowed"]:
            raise DerivedError(f"{master['masterId']}: derived WAV format does not match 48k/24-bit mono-stereo contract")
        if probe["fullScaleSampleCount"] > technical["fullScaleSampleCountMax"]:
            raise DerivedError(f"{master['masterId']}: full-scale/clipping samples detected: {probe['fullScaleSampleCount']}")
        receipt_records.append({**master, "derivedSha256": derived_sha, "bytes": path.stat().st_size, "technicalProbe": probe})
    return {
        "version": 1,
        "status": technical["passStatus"],
        "sourceApprovedReceiptSha256": sha256_file(source_receipt_path),
        "submissionSha256": sha256_file(submission_path),
        "validatedMasterCount": len(receipt_records),
        "records": receipt_records,
        "rule": "Technical intake only. Human listening must be repeated on every derived WAV before derived-master approval."
    }


def load_review_context(technical_receipt_path: Path, submission_path: Path, source_receipt_path: Path, masters_dir: Path, repo_root: Path = ROOT) -> dict[str, Any]:
    contract = load_json(repo_root / CONTRACT)
    expected = validate_technical_submission(submission_path, source_receipt_path, masters_dir, repo_root)
    receipt = load_json(technical_receipt_path)
    if receipt != expected:
        raise DerivedError("derived technical receipt is stale or differs from current source/submission/master bytes")
    typed = load_json(repo_root / SOURCE_APPROVAL_CONTRACT)["typedChecks"]
    return {"contract": contract, "typedChecks": typed, "technicalReceipt": receipt, "technicalReceiptSha256": sha256_file(technical_receipt_path)}
