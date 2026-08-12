#!/usr/bin/env python3
"""Generate Project OEN's original gameplay-feedback + stinger audio pack.

No third-party samples are used. Short feedback cues are mono; stingers are stereo.
All output is 48 kHz / 24-bit PCM WAV with a -3 dBFS peak ceiling.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import shutil
import wave
import zipfile
from pathlib import Path

SR = 48_000
PEAK = 10 ** (-3 / 20)

COUNTS = {
    "SFX_INT_Place_Valid": 6,
    "SFX_INT_Place_Invalid": 4,
    "SFX_INT_Objective_Complete": 4,
    "SFX_INT_Discovery": 6,
    "SFX_INT_Danger_Warning": 4,
    "SFX_INT_Resource_Depleted": 4,
    "SFX_CRF_Start": 6,
    "SFX_CRF_Progress": 8,
    "SFX_CRF_Success": 6,
    "SFX_CRF_Fail": 5,
    "STG_Discovery_Small": 4,
    "STG_Objective_Major": 3,
    "STG_Danger_Reveal": 3,
    "STG_Signal_Success": 3,
}

STEREO_EVENTS = {
    "STG_Discovery_Small",
    "STG_Objective_Major",
    "STG_Danger_Reveal",
    "STG_Signal_Success",
}


def osc(freq: float, t: float, phase: float = 0.0) -> float:
    return math.sin(2.0 * math.pi * freq * t + phase)


def env(i: int, n: int, attack: float = 0.004, release: float = 0.08) -> float:
    t = i / SR
    d = n / SR
    a = min(1.0, t / max(attack, 1e-6))
    r = min(1.0, max(0.0, d - t) / max(release, 1e-6))
    return (a * a) * (r * r)


def lp_noise(n: int, rng: random.Random, alpha: float = 0.08) -> list[float]:
    y = 0.0
    out = []
    for _ in range(n):
        x = rng.uniform(-1.0, 1.0)
        y += alpha * (x - y)
        out.append(y)
    return out


def hp_noise(n: int, rng: random.Random, alpha: float = 0.035) -> list[float]:
    low = 0.0
    out = []
    for _ in range(n):
        x = rng.uniform(-1.0, 1.0)
        low += alpha * (x - low)
        out.append(x - low)
    return out


def normalize_mono(samples: list[float]) -> list[float]:
    maximum = max((abs(x) for x in samples), default=1e-9)
    gain = PEAK / max(maximum, 1e-9)
    return [max(-1.0, min(1.0, x * gain)) for x in samples]


def normalize_stereo(samples: list[tuple[float, float]]) -> list[tuple[float, float]]:
    maximum = max((max(abs(left), abs(right)) for left, right in samples), default=1e-9)
    gain = PEAK / max(maximum, 1e-9)
    return [
        (
            max(-1.0, min(1.0, left * gain)),
            max(-1.0, min(1.0, right * gain)),
        )
        for left, right in samples
    ]


def pcm24(value: float) -> bytes:
    value_int = int(max(-1.0, min(1.0, value)) * ((1 << 23) - 1))
    if value_int < 0:
        value_int = (1 << 24) + value_int
    return bytes((value_int & 0xFF, (value_int >> 8) & 0xFF, (value_int >> 16) & 0xFF))


def write_mono(path: Path, samples: list[float]) -> None:
    frames = bytearray()
    for sample in normalize_mono(samples):
        frames.extend(pcm24(sample))
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(3)
        wav.setframerate(SR)
        wav.writeframes(frames)


def write_stereo(path: Path, samples: list[tuple[float, float]]) -> None:
    frames = bytearray()
    for left, right in normalize_stereo(samples):
        frames.extend(pcm24(left))
        frames.extend(pcm24(right))
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(3)
        wav.setframerate(SR)
        wav.writeframes(frames)


def seed_for(kind: str, variant: int) -> int:
    return 7000 + variant * 131 + sum((i + 1) * ord(char) for i, char in enumerate(kind))


def synth_feedback(kind: str, variant: int) -> list[float]:
    rng = random.Random(seed_for(kind, variant))

    if kind == "SFX_INT_Place_Valid":
        duration = 0.18 + rng.uniform(-0.015, 0.02)
        n = int(duration * SR)
        f0, f1 = 350 + rng.uniform(-15, 15), 590 + rng.uniform(-20, 20)
        return [
            env(i, n, 0.002, 0.08)
            * (0.72 * osc(f0 + (f1 - f0) * (i / n), i / SR) + 0.18 * osc((f0 + f1) * 0.75, i / SR))
            for i in range(n)
        ]

    if kind == "SFX_INT_Place_Invalid":
        duration = 0.23 + rng.uniform(-0.02, 0.02)
        n = int(duration * SR)
        noise = lp_noise(n, rng, 0.12)
        return [
            env(i, n, 0.002, 0.10)
            * (0.68 * osc(165 + rng.uniform(-4, 4), i / SR) + 0.24 * noise[i])
            for i in range(n)
        ]

    if kind == "SFX_INT_Objective_Complete":
        duration = 0.65 + rng.uniform(-0.04, 0.05)
        n = int(duration * SR)
        freqs = [330, 495, 660]
        detune = [1 + rng.uniform(-0.006, 0.006) for _ in freqs]
        return [
            env(i, n, 0.006, 0.18)
            * sum((0.38 / (j + 1)) * osc(freq * detune[j], i / SR, 0.3 * j) for j, freq in enumerate(freqs))
            for i in range(n)
        ]

    if kind == "SFX_INT_Discovery":
        duration = 0.43 + rng.uniform(-0.03, 0.04)
        n = int(duration * SR)
        noise = hp_noise(n, rng, 0.055)
        return [
            env(i, n, 0.01, 0.15)
            * (0.45 * noise[i] + 0.38 * osc(740 + 260 * (i / n), i / SR))
            for i in range(n)
        ]

    if kind == "SFX_INT_Danger_Warning":
        duration = 0.52 + rng.uniform(-0.03, 0.04)
        n = int(duration * SR)
        result = []
        for i in range(n):
            t = i / SR
            pulse = 0.35 + 0.65 * (1 if int(t / 0.09) % 2 == 0 else 0.38)
            result.append(env(i, n, 0.003, 0.14) * pulse * (0.72 * osc(118, t) + 0.24 * osc(177, t)))
        return result

    if kind == "SFX_INT_Resource_Depleted":
        duration = 0.34 + rng.uniform(-0.025, 0.03)
        n = int(duration * SR)
        return [
            env(i, n, 0.002, 0.15)
            * (0.65 * osc(360 - 190 * (i / n), i / SR) + 0.18 * osc(720 - 380 * (i / n), i / SR))
            for i in range(n)
        ]

    if kind == "SFX_CRF_Start":
        duration = 0.22 + rng.uniform(-0.015, 0.02)
        n = int(duration * SR)
        noise = hp_noise(n, rng, 0.08)
        return [
            env(i, n, 0.002, 0.09)
            * (0.42 * noise[i] + 0.52 * osc(245 + 80 * (i / n), i / SR))
            for i in range(n)
        ]

    if kind == "SFX_CRF_Progress":
        duration = 0.12 + rng.uniform(-0.008, 0.012)
        n = int(duration * SR)
        freq = 510 + rng.uniform(-35, 35)
        return [
            env(i, n, 0.001, 0.06)
            * (0.76 * osc(freq, i / SR) + 0.16 * osc(freq * 1.99, i / SR))
            for i in range(n)
        ]

    if kind == "SFX_CRF_Success":
        duration = 0.48 + rng.uniform(-0.025, 0.04)
        n = int(duration * SR)
        f0 = 300 + rng.uniform(-10, 10)
        return [
            env(i, n, 0.003, 0.16)
            * (0.55 * osc(f0, i / SR) + 0.32 * osc(f0 * 1.5, i / SR) + 0.15 * osc(f0 * 2, i / SR))
            for i in range(n)
        ]

    if kind == "SFX_CRF_Fail":
        duration = 0.42 + rng.uniform(-0.03, 0.03)
        n = int(duration * SR)
        noise = lp_noise(n, rng, 0.06)
        return [
            env(i, n, 0.003, 0.15)
            * (0.54 * osc(205 - 55 * (i / n), i / SR) + 0.35 * noise[i])
            for i in range(n)
        ]

    raise ValueError(kind)


def chord(freqs: list[float], t: float, weights: list[float]) -> float:
    return sum(weight * osc(freq, t, 0.15 * i) for i, (freq, weight) in enumerate(zip(freqs, weights)))


def synth_stinger(kind: str, variant: int) -> list[tuple[float, float]]:
    rng = random.Random(seed_for(kind, variant))
    durations = {
        "STG_Discovery_Small": 1.55,
        "STG_Objective_Major": 3.2,
        "STG_Danger_Reveal": 2.35,
        "STG_Signal_Success": 4.1,
    }
    duration = durations[kind] + rng.uniform(-0.08, 0.1)
    n = int(duration * SR)
    left_noise = hp_noise(n, rng, 0.025)
    right_noise = hp_noise(n, random.Random(seed_for(kind, variant) + 991), 0.025)
    out = []
    for i in range(n):
        t = i / SR
        p = i / n
        envelope = env(i, n, 0.02, 0.35)
        if kind == "STG_Discovery_Small":
            base = 392 * (1 + rng.uniform(-0.004, 0.004))
            tonal = chord([base, base * 1.5, base * 2.0], t, [0.55, 0.28, 0.13]) * (0.65 + 0.35 * p)
            shimmer_left = 0.12 * math.sin(math.pi * p) * left_noise[i]
        elif kind == "STG_Objective_Major":
            base = 196 * (1 + rng.uniform(-0.003, 0.003))
            rise = 1 + 0.22 * (p ** 1.5)
            tonal = chord([base * rise, base * 1.5 * rise, base * 2 * rise, base * 2.5 * rise], t, [0.5, 0.28, 0.18, 0.08])
            shimmer_left = 0.09 * math.sin(math.pi * p) * left_noise[i]
        elif kind == "STG_Danger_Reveal":
            base = 110 * (1 + rng.uniform(-0.002, 0.002))
            wobble = 1 + 0.018 * math.sin(2 * math.pi * 2.2 * t)
            tonal = chord([base * wobble, base * 1.414 * wobble, base * 2 * wobble], t, [0.72, 0.31, 0.16])
            shimmer_left = 0.16 * (1 - p) * left_noise[i]
        else:
            base = 261.63 * (1 + rng.uniform(-0.003, 0.003))
            rise = 1 + 0.18 * p
            tonal = chord([base * rise, base * 1.25 * rise, base * 1.5 * rise, base * 2 * rise], t, [0.44, 0.30, 0.24, 0.12])
            shimmer_left = 0.11 * math.sin(math.pi * p) * left_noise[i]
        pan = 0.10 * math.sin(2 * math.pi * (0.22 + 0.03 * variant) * t)
        left = envelope * ((1 - pan) * tonal + shimmer_left)
        right = envelope * ((1 + pan) * tonal + 0.11 * math.sin(math.pi * p) * right_noise[i])
        out.append((left, right))
    return out


def generate(output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    files = []
    for event_id, count in COUNTS.items():
        for variant in range(1, count + 1):
            name = f"{event_id}_{variant:02d}.wav"
            path = output / name
            if event_id in STEREO_EVENTS:
                write_stereo(path, synth_stinger(event_id, variant))
                channels = 2
            else:
                write_mono(path, synth_feedback(event_id, variant))
                channels = 1
            data = path.read_bytes()
            with wave.open(str(path), "rb") as wav:
                duration_seconds = wav.getnframes() / wav.getframerate()
            files.append(
                {
                    "event_id": event_id,
                    "variant": variant,
                    "file": name,
                    "channels": channels,
                    "duration_seconds": round(duration_seconds, 4),
                    "bytes": len(data),
                    "sha256": hashlib.sha256(data).hexdigest(),
                }
            )
    metadata = {
        "pack": "Project OEN authored gameplay + stingers v1",
        "sample_rate_hz": SR,
        "bit_depth": 24,
        "peak_dbfs": -3.0,
        "generator": "tools/generate_authored_gameplay_stingers.py",
        "third_party_samples": False,
        "event_count": len(COUNTS),
        "file_count": len(files),
        "files": files,
    }
    (output / "pack_manifest.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    (output / "LICENSE.txt").write_text(
        "Project OEN authored gameplay + stinger audio v1\n\n"
        "Original procedural works generated for Project OEN. No third-party samples are embedded.\n"
        "They may be used, modified and redistributed as part of Project OEN.\n",
        encoding="utf-8",
    )
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("build/oen-authored-gameplay-stingers-v1"))
    parser.add_argument("--zip", dest="zip_path", type=Path)
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()
    if args.clean and args.output.exists():
        shutil.rmtree(args.output)
    metadata = generate(args.output)
    if args.zip_path:
        args.zip_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(args.zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for path in sorted(args.output.iterdir()):
                archive.write(path, arcname=path.name)
    print(f"Generated {metadata['file_count']} WAV files across {metadata['event_count']} events")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
