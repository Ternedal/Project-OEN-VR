#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import wave
from pathlib import Path
from typing import Any

from prepare_foley_session import CONTRACT, DEFAULT_OUT, QUEUE, RECONCILIATION, build_session, load_object


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def peak24(raw: bytes) -> tuple[float | None, int]:
    if len(raw) % 3:
        raise ValueError("invalid 24-bit PCM byte count")
    peak = 0
    full = 0
    for i in range(0, len(raw), 3):
        value = raw[i] | (raw[i + 1] << 8) | (raw[i + 2] << 16)
        if value & 0x800000:
            value -= 1 << 24
        amplitude = abs(value)
        peak = max(peak, amplitude)
        if value in (-8388608, 8388607):
            full += 1
    dbfs = None if peak == 0 else 20 * math.log10(peak / 8388607)
    return dbfs, full


def inspect_wav(path: Path) -> dict[str, Any]:
    with wave.open(str(path), "rb") as handle:
        channels = handle.getnchannels()
        sample_width = handle.getsampwidth()
        sample_rate = handle.getframerate()
        frames = handle.getnframes()
        compression = handle.getcomptype()
        raw = handle.readframes(frames)
    peak_dbfs, full_scale = peak24(raw) if sample_width == 3 and channels == 1 else (None, None)
    return {
        "channels": channels,
        "bitDepth": sample_width * 8,
        "sampleRateHz": sample_rate,
        "frames": frames,
        "durationMs": (frames / sample_rate * 1000) if sample_rate else 0,
        "compressionType": compression,
        "peakDbfs": peak_dbfs,
        "fullScaleSampleCount": full_scale,
    }


def provenance_errors(path: Path, contract: dict[str, Any], physical_ids: list[str]) -> list[str]:
    if not path.is_file():
        return [f"missing {contract['provenance']['filename']}"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return [f"invalid provenance JSON: {exc}"]
    if not isinstance(data, dict):
        return ["provenance root must be an object"]
    errors: list[str] = []
    for field in contract["provenance"]["requiredTopLevelFields"]:
        if field not in data:
            errors.append(f"provenance missing {field}")
    for field in ("recordistAlias", "recordedAtUtc", "recordingChain", "rightsStatement"):
        if not isinstance(data.get(field), str) or not data[field].strip():
            errors.append(f"provenance {field} must be non-empty")
    if not isinstance(data.get("commercialReuseAllowed"), bool):
        errors.append("provenance commercialReuseAllowed must be boolean")
    physical = data.get("physicalSessions")
    if not isinstance(physical, dict):
        errors.append("provenance physicalSessions must be an object")
        return errors
    if set(physical) != set(physical_ids):
        errors.append(f"provenance physical session IDs drift: got={sorted(physical)} expected={sorted(physical_ids)}")
    required = contract["provenance"]["requiredPhysicalSessionFields"]
    for session_id in physical_ids:
        entry = physical.get(session_id)
        if not isinstance(entry, dict):
            errors.append(f"provenance {session_id} must be an object")
            continue
        for field in required:
            if field not in entry:
                errors.append(f"provenance {session_id} missing {field}")
        materials = entry.get("sourceMaterials")
        if not isinstance(materials, list) or not materials or not all(isinstance(v, str) and v.strip() for v in materials):
            errors.append(f"provenance {session_id} sourceMaterials must be a non-empty string list")
        if not isinstance(entry.get("locationClass"), str) or not entry["locationClass"].strip():
            errors.append(f"provenance {session_id} locationClass must be non-empty")
        if entry.get("backgroundSpeechNone") is not True:
            errors.append(f"provenance {session_id} backgroundSpeechNone must be true")
        if entry.get("backgroundMusicNone") is not True:
            errors.append(f"provenance {session_id} backgroundMusicNone must be true")
        if not isinstance(entry.get("notes"), str):
            errors.append(f"provenance {session_id} notes must be text")
    return errors


def fresh_expected() -> tuple[dict[str, Any], dict[str, Any]]:
    queue = load_object(QUEUE)
    reconciliation = load_object(RECONCILIATION)
    contract = load_object(CONTRACT)
    return build_session(queue, reconciliation, contract), contract


def validate_session(session_root: Path) -> tuple[dict[str, Any], list[str], list[str]]:
    expected, contract = fresh_expected()
    errors: list[str] = []
    warnings: list[str] = []
    session_file = session_root / "recording_session.json"
    if not session_file.is_file():
        errors.append("missing recording_session.json; run prepare_foley_session.py first")
        prepared: dict[str, Any] = {}
    else:
        try:
            prepared = json.loads(session_file.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"invalid recording_session.json: {exc}")
            prepared = {}
    if isinstance(prepared, dict):
        for key in ("bindings", "expectedQueueSessionCount", "expectedPhysicalSessionCount", "expectedCueCount", "expectedTakeCount", "expectedTakes", "physicalSessionIds"):
            if prepared.get(key) != expected.get(key):
                errors.append(f"recording_session.json is stale or modified: {key} mismatch")
    else:
        errors.append("recording_session.json root must be an object")

    provenance_path = session_root / contract["provenance"]["filename"]
    errors.extend(provenance_errors(provenance_path, contract, expected["physicalSessionIds"]))

    expected_paths = {take["relativePath"] for take in expected["expectedTakes"]}
    takes_root = session_root / "takes"
    actual_paths = {
        path.relative_to(session_root).as_posix()
        for path in takes_root.rglob("*.wav")
        if path.is_file()
    } if takes_root.is_dir() else set()
    unexpected = sorted(actual_paths - expected_paths)
    if unexpected:
        errors.append("unexpected WAV take(s): " + ", ".join(unexpected))

    spec = contract["technicalAcceptance"]
    records: list[dict[str, Any]] = []
    hashes: dict[str, str] = {}
    for take in expected["expectedTakes"]:
        relative = take["relativePath"]
        path = session_root / relative
        if not path.is_file():
            errors.append(f"missing take: {relative}")
            continue
        try:
            tech = inspect_wav(path)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{relative}: unreadable PCM WAV: {exc}")
            continue
        if tech["compressionType"] != "NONE":
            errors.append(f"{relative}: WAV must be uncompressed PCM")
        if tech["sampleRateHz"] != spec["sampleRateHz"]:
            errors.append(f"{relative}: sample rate {tech['sampleRateHz']} != {spec['sampleRateHz']}")
        if tech["bitDepth"] != spec["bitDepth"]:
            errors.append(f"{relative}: bit depth {tech['bitDepth']} != {spec['bitDepth']}")
        if tech["channels"] != spec["channels"]:
            errors.append(f"{relative}: channels {tech['channels']} != {spec['channels']}")
        if tech["fullScaleSampleCount"] is not None and tech["fullScaleSampleCount"] > spec["fullScaleSampleCountMax"]:
            errors.append(f"{relative}: {tech['fullScaleSampleCount']} full-scale sample(s)")
        lo, hi = take["targetLengthMs"]
        within = lo <= tech["durationMs"] <= hi
        if not within:
            warnings.append(f"{relative}: duration {tech['durationMs']:.1f} ms outside {lo}-{hi} ms target")
        digest = sha256_file(path)
        if digest in hashes:
            errors.append(f"duplicate raw take bytes: {relative} == {hashes[digest]}")
        else:
            hashes[digest] = relative
        records.append({
            "queueSessionId": take["queueSessionId"],
            "physicalSessionId": take["physicalSessionId"],
            "cueId": take["cueId"],
            "variant": take["variant"],
            "filename": take["filename"],
            "relativePath": relative,
            "sha256": digest,
            "bytes": path.stat().st_size,
            "sampleRateHz": tech["sampleRateHz"],
            "bitDepth": tech["bitDepth"],
            "channels": tech["channels"],
            "durationMs": round(tech["durationMs"], 3),
            "peakDbfs": None if tech["peakDbfs"] is None else round(tech["peakDbfs"], 3),
            "fullScaleSampleCount": tech["fullScaleSampleCount"],
            "durationTargetMs": take["targetLengthMs"],
            "durationWithinTarget": within,
        })

    complete = len(records) == expected["expectedTakeCount"]
    status = contract["receipt"]["statusOnPass"] if not errors and complete else "technical-intake-incomplete-or-failed"
    receipt = {
        "version": 1,
        "status": status,
        "bindings": expected["bindings"],
        "recordingSessionSha256": sha256_file(session_file) if session_file.is_file() else None,
        "provenanceSha256": sha256_file(provenance_path) if provenance_path.is_file() else None,
        "expectedCueCount": expected["expectedCueCount"],
        "expectedTakeCount": expected["expectedTakeCount"],
        "validatedTakeCount": len(records),
        "records": records,
        "warnings": warnings,
        "rule": "Technical intake is hash/container/clipping/provenance evidence only; human material-fit, variation, listening, source selection, Unity and release approval remain pending.",
    }
    return receipt, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a completed PROJECT OEN physical Foley session without performing human listening approval.")
    parser.add_argument("--session", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    session_root = args.session.resolve()
    receipt, errors, warnings = validate_session(session_root)
    output = args.output.resolve() if args.output else session_root / "foley_intake_receipt.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for warning in warnings:
        print("WARNING:", warning)
    for error in errors:
        print("ERROR:", error)
    if errors:
        print(f"Foley technical intake FAILED: {receipt['validatedTakeCount']}/{receipt['expectedTakeCount']} readable takes")
        return 1
    print(f"Foley technical intake PASS: {receipt['validatedTakeCount']}/{receipt['expectedTakeCount']} exact planned takes")
    print("Human material-fit, variation and under-weather listening remain pending.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
