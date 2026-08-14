#!/usr/bin/env python3
"""Validate Project OEN authored adaptive music candidate renders."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import wave
from pathlib import Path

import numpy as np

EXPECTED = {
    "MUS_Camp_WarmTexture": (3, 90.0, True),
    "MUS_Warning_LowPulse": (3, 60.0, True),
    "MUS_Storm_Phase1": (2, 90.0, True),
    "MUS_Storm_Phase2": (2, 90.0, True),
    "MUS_Storm_Phase3": (2, 90.0, True),
    "MUS_Finale_Success": (2, 24.0, False),
}
SR = 48_000


def decode24(frames: bytes, channels: int) -> np.ndarray:
    raw = np.frombuffer(frames, dtype=np.uint8).reshape(-1, channels, 3)
    unsigned = (
        raw[:, :, 0].astype(np.uint32)
        | (raw[:, :, 1].astype(np.uint32) << 8)
        | (raw[:, :, 2].astype(np.uint32) << 16)
    )
    signed = unsigned.astype(np.int32)
    signed = np.where((unsigned & 0x800000) != 0, signed - (1 << 24), signed)
    return signed.astype(np.float32) / np.float32((1 << 23) - 1)


def event_from_name(name: str) -> str | None:
    stem = Path(name).stem
    for event_id in EXPECTED:
        if stem.startswith(event_id + "_"):
            return event_id
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()

    root = args.input
    errors: list[str] = []
    wavs = sorted(root.glob("*.wav"))
    if len(wavs) != 14:
        errors.append(f"expected 14 WAV files, got {len(wavs)}")

    counts = {event_id: 0 for event_id in EXPECTED}
    hashes: set[str] = set()

    for path in wavs:
        event_id = event_from_name(path.name)
        if event_id is None:
            errors.append(f"unexpected filename: {path.name}")
            continue
        counts[event_id] += 1
        _, expected_duration, loop = EXPECTED[event_id]

        with wave.open(str(path), "rb") as wav:
            channels = wav.getnchannels()
            width = wav.getsampwidth()
            rate = wav.getframerate()
            frames_count = wav.getnframes()
            frames = wav.readframes(frames_count)

        if channels != 2:
            errors.append(f"{path.name}: expected stereo, got {channels} channels")
        if width != 3:
            errors.append(f"{path.name}: expected 24-bit PCM")
        if rate != SR:
            errors.append(f"{path.name}: expected 48000 Hz, got {rate}")

        duration = frames_count / rate
        if abs(duration - expected_duration) > 1 / SR:
            errors.append(f"{path.name}: duration {duration:.6f}s != {expected_duration:.6f}s")

        audio = decode24(frames, channels)
        peak = float(np.max(np.abs(audio)))
        rms = float(np.sqrt(np.mean(np.square(audio, dtype=np.float64))))
        peak_db = 20 * math.log10(max(peak, 1e-12))
        rms_db = 20 * math.log10(max(rms, 1e-12))
        if not (-6.05 <= peak_db <= -5.85):
            errors.append(f"{path.name}: peak {peak_db:.2f} dBFS outside -6 dBFS target")
        if rms_db < -38.0:
            errors.append(f"{path.name}: RMS too low ({rms_db:.2f} dBFS)")
        if rms_db > -14.0:
            errors.append(f"{path.name}: RMS too hot ({rms_db:.2f} dBFS)")

        stereo_delta = float(np.sqrt(np.mean(np.square(audio[:, 0] - audio[:, 1], dtype=np.float64))))
        if stereo_delta < 0.002:
            errors.append(f"{path.name}: stereo channels are effectively identical")

        if loop:
            wrap = np.abs(audio[0] - audio[-1])
            edge = np.concatenate(
                (
                    np.abs(np.diff(audio[:8192], axis=0)).ravel(),
                    np.abs(np.diff(audio[-8192:], axis=0)).ravel(),
                )
            )
            reference = float(np.percentile(edge, 99.9)) + 1e-9
            seam_ratio = float(np.max(wrap) / reference)
            if seam_ratio > 2.5:
                errors.append(f"{path.name}: loop seam ratio {seam_ratio:.2f} > 2.5")

        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest in hashes:
            errors.append(f"{path.name}: duplicate WAV payload")
        hashes.add(digest)

    for event_id, (expected_count, _, _) in EXPECTED.items():
        if counts[event_id] != expected_count:
            errors.append(f"{event_id}: count {counts[event_id]} != {expected_count}")

    manifest = root / "pack_manifest.json"
    if not manifest.exists():
        errors.append("missing pack_manifest.json")
    else:
        metadata = json.loads(manifest.read_text(encoding="utf-8"))
        if metadata.get("file_count") != 14:
            errors.append("pack_manifest file_count must be 14")
        if metadata.get("event_count") != 6:
            errors.append("pack_manifest event_count must be 6")
        if metadata.get("third_party_samples") is not False:
            errors.append("pack_manifest third_party_samples must be false")
        if metadata.get("qa_status") != "candidate-headset-listen":
            errors.append("pack_manifest qa_status must remain candidate-headset-listen")

    if errors:
        print("Adaptive music validation FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Adaptive music validation OK: 14 WAV / 6 events / 48kHz / 24-bit stereo")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
