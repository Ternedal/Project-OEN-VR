#!/usr/bin/env python3
"""Validate committed AU-1 WAV masters and optional fresh generator output."""

from __future__ import annotations

import argparse
import hashlib
import json
import wave
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PRODUCTION = Path(__file__).resolve().parent / "production"
REGISTRY = ROOT / "content" / "audio" / "audio_cues.source.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", type=Path)
    args = parser.parse_args()
    errors: list[str] = []
    manifest_path = PRODUCTION / "manifest.json"
    if not manifest_path.is_file():
        errors.append("committed production manifest missing")
        manifest = {"cues": []}
    else:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    cues = manifest.get("cues", [])
    if len(cues) != 12:
        errors.append(f"expected 12 committed cues, got {len(cues)}")
    expected_files = {cue.get("file") for cue in cues}
    actual_files = {path.name for path in PRODUCTION.glob("*.wav")}
    if actual_files != expected_files:
        errors.append(f"WAV set differs: expected={sorted(expected_files)}, actual={sorted(actual_files)}")
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    by_id = {cue.get("id"): cue for cue in registry.get("cues", [])}
    for cue in cues:
        filename = cue["file"]
        cue_id = filename.removesuffix(".wav")
        path = PRODUCTION / filename
        if not path.is_file():
            continue
        with wave.open(str(path), "rb") as wav:
            properties = (wav.getframerate(), wav.getnchannels(), wav.getsampwidth())
            duration = wav.getnframes() / wav.getframerate()
        if properties != (48_000, 1, 2):
            errors.append(f"{filename}: expected 48kHz mono 16-bit PCM, got {properties}")
        if not 0.15 <= duration <= 0.60:
            errors.append(f"{filename}: duration {duration:.3f}s outside 0.15..0.60s")
        actual_hash = digest(path)
        if actual_hash != cue.get("sha256"):
            errors.append(f"{filename}: manifest hash mismatch")
        entry = by_id.get(cue_id, {})
        expected_source = f"source_audio/au1/production/{filename}"
        if entry.get("productionStatus") != "production_master_ready":
            errors.append(f"{cue_id}: registry status is not production_master_ready")
        if entry.get("source") != expected_source:
            errors.append(f"{cue_id}: registry source is not committed WAV master")
    if args.generated:
        generated_manifest = args.generated / "manifest.json"
        if not generated_manifest.is_file():
            errors.append("fresh generated manifest missing")
        else:
            generated = json.loads(generated_manifest.read_text(encoding="utf-8"))
            generated_by_file = {cue["file"]: cue for cue in generated.get("cues", [])}
            if set(generated_by_file) != expected_files:
                errors.append("fresh generated cue set differs from committed cue set")
            for filename in expected_files:
                fresh_path = args.generated / filename
                committed_path = PRODUCTION / filename
                if fresh_path.is_file() and committed_path.is_file() and digest(fresh_path) != digest(committed_path):
                    errors.append(f"{filename}: committed bytes differ from fresh deterministic generation")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    suffix = " and fresh generator output" if args.generated else ""
    print(f"AU-1 production audio OK: 12 committed 48kHz mono WAV masters{suffix} match manifest and registry.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
