#!/usr/bin/env python3
"""Repo-side QA for deterministic authored Project OEN audio."""
from __future__ import annotations

import hashlib
import math
import shutil
import tempfile
import wave
from pathlib import Path

import generate_authored_audio_pack as authored


def pcm24_peak_rms(frames: bytes) -> tuple[float, float]:
    samples = []
    for offset in range(0, len(frames), 3):
        value = frames[offset] | (frames[offset + 1] << 8) | (frames[offset + 2] << 16)
        if value & 0x800000:
            value -= 1 << 24
        samples.append(value / ((1 << 23) - 1))
    if not samples:
        return 0.0, 0.0
    peak = max(abs(value) for value in samples)
    rms = math.sqrt(sum(value * value for value in samples) / len(samples))
    return peak, rms


def generate_and_digest(root: Path) -> dict[str, str]:
    authored.generate(root)
    result = {}
    for path in sorted(root.glob("*.wav")):
        result[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="oen-audio-") as temp:
        root = Path(temp)
        first = root / "first"
        second = root / "second"
        first_hashes = generate_and_digest(first)
        second_hashes = generate_and_digest(second)

        expected_count = sum(authored.COUNTS.values())
        errors = []
        if len(first_hashes) != expected_count:
            errors.append(f"expected {expected_count} WAV files, got {len(first_hashes)}")
        if first_hashes != second_hashes:
            errors.append("authored audio generation is not deterministic")

        for name in sorted(first_hashes):
            path = first / name
            with wave.open(str(path), "rb") as wav:
                if wav.getframerate() != 48_000:
                    errors.append(f"{name}: sample rate != 48000")
                if wav.getnchannels() != 1:
                    errors.append(f"{name}: channels != mono")
                if wav.getsampwidth() != 3:
                    errors.append(f"{name}: bit depth != 24-bit PCM")
                frames = wav.readframes(wav.getnframes())
            peak, rms = pcm24_peak_rms(frames)
            peak_db = 20 * math.log10(max(peak, 1e-12))
            if peak_db > -2.85:
                errors.append(f"{name}: peak {peak_db:.2f} dBFS exceeds -2.85 dBFS")
            if rms < 0.005:
                errors.append(f"{name}: RMS too low ({rms:.5f}); likely silent/broken")

        if errors:
            print("Audio authored-pack validation FAILED")
            for error in errors:
                print(f"- {error}")
            return 1

        print(f"Audio authored-pack validation OK: {expected_count} deterministic 48kHz/24-bit mono WAV files")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
