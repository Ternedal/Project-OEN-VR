#!/usr/bin/env python3
"""Generate Project OEN's original UI/status audio pack.

The pack is deliberately synthesized from primitives rather than third-party samples,
so these clips have no external sample-license dependency. Output is mono 48 kHz,
24-bit PCM WAV with a -3 dBFS peak ceiling.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import shutil
import struct
import wave
import zipfile
from pathlib import Path

SR = 48_000
PEAK = 10 ** (-3 / 20)

COUNTS = {
    "SFX_UI_Hover": 4,
    "SFX_UI_Select": 4,
    "SFX_UI_Back": 4,
    "SFX_UI_Error": 4,
    "SFX_UI_PageTurn": 5,
    "SFX_UI_Map_Open": 4,
    "SFX_UI_Map_Close": 4,
    "SFX_UI_Radio_Click": 5,
    "SFX_UI_Radio_Static": 5,
    "SFX_UI_Inventory_Open": 4,
    "SFX_UI_Inventory_Close": 4,
    "SFX_STS_Injury_Warn": 3,
    "SFX_STS_ColdWet_Warn": 3,
    "SFX_STS_Fatigue_Warn": 3,
    "SFX_STS_Health_Damage": 6,
    "SFX_STS_Health_Critical": 3,
}


def osc(freq: float, t: float, phase: float = 0.0) -> float:
    return math.sin(2 * math.pi * freq * t + phase)


def envelope(i: int, n: int, attack: float = 0.01, release: float = 0.08) -> float:
    t = i / SR
    duration = n / SR
    a = min(1.0, t / max(attack, 1e-6))
    r = min(1.0, max(0.0, duration - t) / max(release, 1e-6))
    return (a * a) * min(1.0, r)


def lowpass_noise(n: int, rng: random.Random, alpha: float = 0.15) -> list[float]:
    y = 0.0
    result: list[float] = []
    for _ in range(n):
        x = rng.uniform(-1.0, 1.0)
        y += alpha * (x - y)
        result.append(y)
    return result


def highpass_noise(n: int, rng: random.Random, alpha: float = 0.03) -> list[float]:
    low = 0.0
    result: list[float] = []
    for _ in range(n):
        x = rng.uniform(-1.0, 1.0)
        low += alpha * (x - low)
        result.append(x - low)
    return result


def normalize(samples: list[float]) -> list[float]:
    maximum = max((abs(value) for value in samples), default=1e-9)
    gain = PEAK / max(maximum, 1e-9)
    return [max(-1.0, min(1.0, value * gain)) for value in samples]


def write_wav24(path: Path, samples: list[float]) -> None:
    frames = bytearray()
    scale = (1 << 23) - 1
    for sample in normalize(samples):
        value = int(sample * scale)
        if value < 0:
            value = (1 << 24) + value
        frames.extend((value & 0xFF, (value >> 8) & 0xFF, (value >> 16) & 0xFF))

    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(3)
        wav.setframerate(SR)
        wav.writeframes(frames)


def synth(kind: str, variant: int) -> list[float]:
    rng = random.Random(1000 + variant * 97 + sum(map(ord, kind)))

    if kind == "SFX_UI_Hover":
        duration = 0.075 + rng.uniform(-0.008, 0.010)
        n = int(duration * SR)
        freq = 900 + rng.uniform(-70, 70)
        return [envelope(i, n, 0.002, 0.045) * (0.8 * osc(freq, i / SR) + 0.18 * osc(freq * 2.01, i / SR)) for i in range(n)]

    if kind == "SFX_UI_Select":
        duration = 0.13 + rng.uniform(-0.01, 0.015)
        n = int(duration * SR)
        f0 = 580 + rng.uniform(-25, 25)
        f1 = 910 + rng.uniform(-30, 30)
        result = []
        for i in range(n):
            p = i / n
            freq = f0 + (f1 - f0) * (p ** 1.4)
            result.append(envelope(i, n, 0.002, 0.07) * (0.74 * osc(freq, i / SR) + 0.22 * osc(freq * 1.5, i / SR)))
        return result

    if kind == "SFX_UI_Back":
        duration = 0.15 + rng.uniform(-0.01, 0.015)
        n = int(duration * SR)
        f0 = 820 + rng.uniform(-30, 30)
        f1 = 470 + rng.uniform(-20, 20)
        return [envelope(i, n, 0.002, 0.075) * (0.82 * osc(f0 + (f1 - f0) * (i / n), i / SR) + 0.15 * osc((f0 + (f1 - f0) * (i / n)) * 0.5, i / SR)) for i in range(n)]

    if kind == "SFX_UI_Error":
        duration = 0.28 + rng.uniform(-0.015, 0.02)
        n = int(duration * SR)
        return [envelope(i, n, 0.004, 0.10) * (0.65 * osc(205, i / SR) + 0.32 * osc(307, i / SR)) * (1.0 if (i // int(SR * 0.055)) % 2 == 0 else 0.6) for i in range(n)]

    if kind == "SFX_UI_PageTurn":
        duration = 0.28 + rng.uniform(-0.03, 0.03)
        n = int(duration * SR)
        noise = highpass_noise(n, rng, 0.04)
        result = []
        for i, value in enumerate(noise):
            p = i / n
            shape = math.sin(math.pi * p) ** 1.2
            result.append(shape * value * (0.35 + 0.65 * p) + 0.08 * shape * osc(1400 + 350 * p, i / SR))
        return result

    if kind in ("SFX_UI_Map_Open", "SFX_UI_Inventory_Open"):
        duration = 0.36 + rng.uniform(-0.02, 0.03)
        n = int(duration * SR)
        noise = lowpass_noise(n, rng, 0.08)
        result = []
        for i, value in enumerate(noise):
            p = i / n
            shape = math.sin(math.pi * p) ** 1.5
            freq = 240 + 850 * (p ** 1.3)
            result.append(shape * (0.38 * value + 0.28 * osc(freq, i / SR)) + 0.18 * envelope(i, n, 0.003, 0.08) * osc(1100, i / SR))
        return result

    if kind in ("SFX_UI_Map_Close", "SFX_UI_Inventory_Close"):
        duration = 0.34 + rng.uniform(-0.02, 0.03)
        n = int(duration * SR)
        noise = lowpass_noise(n, rng, 0.08)
        result = []
        for i, value in enumerate(noise):
            p = i / n
            shape = math.sin(math.pi * p) ** 1.4
            freq = 920 - 680 * (p ** 1.1)
            result.append(shape * (0.38 * value + 0.28 * osc(freq, i / SR)) + 0.12 * envelope(i, n, 0.002, 0.08) * osc(600, i / SR))
        return result

    if kind == "SFX_UI_Radio_Click":
        duration = 0.09 + rng.uniform(-0.008, 0.012)
        n = int(duration * SR)
        noise = highpass_noise(n, rng, 0.05)
        return [envelope(i, n, 0.001, 0.045) * (0.55 * value + 0.45 * osc(170 + rng.uniform(-8, 8), i / SR)) for i, value in enumerate(noise)]

    if kind == "SFX_UI_Radio_Static":
        duration = 0.42 + rng.uniform(-0.06, 0.06)
        n = int(duration * SR)
        noise = highpass_noise(n, rng, 0.018)
        result = []
        for i, value in enumerate(noise):
            p = i / n
            gate = 0.55 + 0.45 * (1.0 if rng.random() > 0.08 else 0.15)
            shape = math.sin(math.pi * p) ** 0.7
            result.append(shape * gate * (0.65 * value + 0.10 * osc(1800 + rng.uniform(-100, 100), i / SR)))
        return result

    if kind == "SFX_STS_Injury_Warn":
        duration = 0.48 + rng.uniform(-0.03, 0.03)
        n = int(duration * SR)
        result = []
        for i in range(n):
            t = i / SR
            p = i / n
            pulse = math.exp(-((t - 0.08) / 0.035) ** 2) + 0.75 * math.exp(-((t - 0.23) / 0.045) ** 2)
            result.append(pulse * (0.68 * osc(145, t) + 0.22 * osc(290, t)) * math.exp(-1.5 * p))
        return result

    if kind == "SFX_STS_ColdWet_Warn":
        duration = 0.62 + rng.uniform(-0.04, 0.04)
        n = int(duration * SR)
        noise = highpass_noise(n, rng, 0.08)
        result = []
        for i, value in enumerate(noise):
            t = i / SR
            p = i / n
            tremolo = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(2 * math.pi * 8.5 * t))
            shape = math.sin(math.pi * p) ** 1.15
            result.append(shape * (0.45 * value * tremolo + 0.18 * osc(1250 + 60 * math.sin(2 * math.pi * 3 * t), t)))
        return result

    if kind == "SFX_STS_Fatigue_Warn":
        duration = 0.70 + rng.uniform(-0.04, 0.05)
        n = int(duration * SR)
        noise = lowpass_noise(n, rng, 0.025)
        return [(math.sin(math.pi * (i / n)) ** 0.85) * (0.55 * value + 0.15 * osc(105, i / SR)) * (1 - 0.35 * (i / n)) for i, value in enumerate(noise)]

    if kind == "SFX_STS_Health_Damage":
        duration = 0.24 + rng.uniform(-0.025, 0.03)
        n = int(duration * SR)
        noise = lowpass_noise(n, rng, 0.12)
        return [envelope(i, n, 0.001, 0.12) * (0.52 * value + 0.55 * osc(82, i / SR) + 0.18 * osc(164, i / SR)) for i, value in enumerate(noise)]

    if kind == "SFX_STS_Health_Critical":
        duration = 0.90 + rng.uniform(-0.03, 0.05)
        n = int(duration * SR)
        result = []
        for i in range(n):
            t = i / SR
            pulse = sum(math.exp(-((t - center) / 0.04) ** 2) for center in (0.08, 0.31, 0.58))
            result.append(pulse * (0.72 * osc(118, t) + 0.20 * osc(236, t)))
        return result

    raise ValueError(f"Unsupported authored event: {kind}")


def generate(output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    files = []
    for event_id, count in COUNTS.items():
        for variant in range(1, count + 1):
            name = f"{event_id}_{variant:02d}.wav"
            path = output / name
            write_wav24(path, synth(event_id, variant))
            data = path.read_bytes()
            files.append({"file": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})

    metadata = {
        "pack": "Project OEN authored UI + status audio v1",
        "sample_rate_hz": SR,
        "bit_depth": 24,
        "channels": 1,
        "peak_dbfs": -3.0,
        "generator": "tools/generate_authored_audio_pack.py",
        "third_party_samples": False,
        "files": files,
    }
    (output / "pack_manifest.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    (output / "LICENSE.txt").write_text(
        "Project OEN authored audio pack v1\n\n"
        "Original procedural works generated for Project OEN. No third-party samples are embedded.\n"
        "They may be used, modified and redistributed as part of Project OEN.\n",
        encoding="utf-8",
    )
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("build/audio-authored-v1"))
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

    print(f"Generated {len(metadata['files'])} authored WAV files in {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
