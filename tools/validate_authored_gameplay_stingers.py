#!/usr/bin/env python3
"""Repo-side QA for Project OEN authored gameplay-feedback + stinger audio."""
from __future__ import annotations

import hashlib
import math
import tempfile
import wave
from pathlib import Path

import generate_authored_gameplay_stingers as authored


def decode_pcm24(frames: bytes) -> list[float]:
    samples = []
    for offset in range(0, len(frames), 3):
        value = frames[offset] | (frames[offset + 1] << 8) | (frames[offset + 2] << 16)
        if value & 0x800000:
            value -= 1 << 24
        samples.append(value / ((1 << 23) - 1))
    return samples


def peak_rms(samples: list[float]) -> tuple[float, float]:
    if not samples:
        return 0.0, 0.0
    peak = max(abs(value) for value in samples)
    rms = math.sqrt(sum(value * value for value in samples) / len(samples))
    return peak, rms


def generate_and_digest(root: Path) -> dict[str, str]:
    authored.generate(root)
    return {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.glob("*.wav"))
    }


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="oen-gameplay-stingers-") as temp:
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
            errors.append("generation is not deterministic")
        if len(set(first_hashes.values())) != len(first_hashes):
            errors.append("duplicate WAV payloads detected")

        for name in sorted(first_hashes):
            path = first / name
            event_id = name.rsplit("_", 1)[0]
            expected_channels = 2 if event_id in authored.STEREO_EVENTS else 1
            with wave.open(str(path), "rb") as wav:
                channels = wav.getnchannels()
                rate = wav.getframerate()
                width = wav.getsampwidth()
                frames = wav.readframes(wav.getnframes())
                duration = wav.getnframes() / max(rate, 1)

            if rate != 48_000:
                errors.append(f"{name}: sample rate != 48000")
            if width != 3:
                errors.append(f"{name}: bit depth != 24-bit PCM")
            if channels != expected_channels:
                errors.append(f"{name}: channels {channels} != expected {expected_channels}")
            if event_id.startswith("STG_") and not (1.0 <= duration <= 8.0):
                errors.append(f"{name}: stinger duration {duration:.2f}s outside 1-8s")
            if not event_id.startswith("STG_") and not (0.05 <= duration <= 2.5):
                errors.append(f"{name}: gameplay cue duration {duration:.2f}s outside 0.05-2.5s")

            peak, rms = peak_rms(decode_pcm24(frames))
            peak_db = 20 * math.log10(max(peak, 1e-12))
            if peak_db > -2.85:
                errors.append(f"{name}: peak {peak_db:.2f} dBFS exceeds -2.85 dBFS")
            if rms < 0.003:
                errors.append(f"{name}: RMS too low ({rms:.5f})")

        if errors:
            print("Gameplay/stinger authored-pack validation FAILED")
            for error in errors:
                print(f"- {error}")
            return 1

        print(
            f"Gameplay/stinger authored-pack validation OK: "
            f"{expected_count} deterministic WAV files across {len(authored.COUNTS)} events"
        )
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
