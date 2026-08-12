#!/usr/bin/env python3
"""Generate Project OEN's original adaptive music candidate pack.

The pack uses deterministic procedural synthesis with NumPy. No third-party samples
are embedded. Looping tracks are built from periodic oscillators whose cycles close
exactly over the file duration, avoiding forced fade-to-silence at loop boundaries.

Output: stereo 48 kHz / 24-bit PCM WAV, normalized to -6 dBFS peak for mix headroom.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import wave
import zipfile
from pathlib import Path

import numpy as np

SR = 48_000
PEAK_DBFS = -6.0
PEAK = 10 ** (PEAK_DBFS / 20.0)
GENERATOR_VERSION = "1.0.0"
NUMPY_VERSION = np.__version__

TRACKS = {
    "MUS_Camp_WarmTexture": {"count": 3, "duration": 90.0, "loop": True, "state": "camp-calm"},
    "MUS_Warning_LowPulse": {"count": 3, "duration": 60.0, "loop": True, "state": "warning"},
    "MUS_Storm_Phase1": {"count": 2, "duration": 90.0, "loop": True, "state": "storm-wind"},
    "MUS_Storm_Phase2": {"count": 2, "duration": 90.0, "loop": True, "state": "storm-rain-fire"},
    "MUS_Storm_Phase3": {"count": 2, "duration": 90.0, "loop": True, "state": "storm-signal"},
    "MUS_Finale_Success": {"count": 2, "duration": 24.0, "loop": False, "state": "finale-success"},
}


def seed_for(kind: str, variant: int) -> int:
    return 17000 + variant * 997 + sum((i + 1) * ord(ch) for i, ch in enumerate(kind))


def closed_freq(target_hz: float, duration: float) -> float:
    cycles = max(1, int(round(target_hz * duration)))
    return cycles / duration


def osc(t: np.ndarray, target_hz: float, duration: float, phase: float = 0.0) -> np.ndarray:
    f = closed_freq(target_hz, duration)
    return np.sin((2.0 * np.pi * f) * t + phase, dtype=np.float32)


def slow(t: np.ndarray, duration: float, cycles: int, phase: float = 0.0) -> np.ndarray:
    return np.sin((2.0 * np.pi * cycles / duration) * t + phase, dtype=np.float32)


def add_tone(left: np.ndarray, right: np.ndarray, t: np.ndarray, duration: float,
             freq: float, amp: float, phase: float, width: float, breathe_cycles: int) -> None:
    breathe_l = 0.76 + 0.24 * slow(t, duration, breathe_cycles, phase * 0.31)
    breathe_r = 0.76 + 0.24 * slow(t, duration, breathe_cycles, phase * 0.31 + 0.23)
    fundamental_l = osc(t, freq, duration, phase)
    fundamental_r = osc(t, freq, duration, phase + width)
    second_l = osc(t, freq * 2.0, duration, phase * 0.7 + 0.13)
    second_r = osc(t, freq * 2.0, duration, phase * 0.7 + 0.13 + width * 1.4)
    third_l = osc(t, freq * 3.0, duration, phase * 0.43 + 0.37)
    third_r = osc(t, freq * 3.0, duration, phase * 0.43 + 0.37 + width * 1.8)
    left += amp * breathe_l * (0.78 * fundamental_l + 0.16 * second_l + 0.06 * third_l)
    right += amp * breathe_r * (0.78 * fundamental_r + 0.16 * second_r + 0.06 * third_r)


def add_shimmer(left: np.ndarray, right: np.ndarray, t: np.ndarray, duration: float,
                rng: np.random.Generator, amount: float, count: int = 6) -> None:
    for idx in range(count):
        freq = float(rng.uniform(620.0, 2600.0))
        phase = float(rng.uniform(0.0, 2.0 * np.pi))
        cycles = 2 + (idx % 5)
        mod_l = 0.5 + 0.5 * slow(t, duration, cycles, phase * 0.17)
        mod_r = 0.5 + 0.5 * slow(t, duration, cycles, phase * 0.17 + 0.7)
        left += amount * (0.75 / (idx + 1)) * mod_l * osc(t, freq, duration, phase)
        right += amount * (0.75 / (idx + 1)) * mod_r * osc(
            t, freq * (1.0 + 0.0015 * ((idx % 3) - 1)), duration, phase + 0.19
        )


def add_low_pulse(left: np.ndarray, right: np.ndarray, t: np.ndarray, duration: float,
                  root: float, amp: float, pulse_count: int, phase: float) -> None:
    carrier_l = osc(t, root, duration, phase) + 0.28 * osc(t, root * 2.0, duration, phase + 0.2)
    carrier_r = osc(t, root, duration, phase + 0.04) + 0.28 * osc(t, root * 2.0, duration, phase + 0.27)
    gate = 0.5 + 0.5 * slow(t, duration, pulse_count, -np.pi / 2.0)
    gate = gate * gate
    gate = gate * gate
    left += amp * gate * carrier_l
    right += amp * gate * carrier_r


def synth_loop(kind: str, variant: int, duration: float) -> np.ndarray:
    n = int(round(duration * SR))
    t = np.arange(n, dtype=np.float32) / np.float32(SR)
    left = np.zeros(n, dtype=np.float32)
    right = np.zeros(n, dtype=np.float32)
    rng = np.random.default_rng(seed_for(kind, variant))

    if kind == "MUS_Camp_WarmTexture":
        notes = [(73.42, 0.18), (110.00, 0.13), (130.81, 0.08), (164.81, 0.055), (220.00, 0.035)]
        for idx, (freq, amp) in enumerate(notes):
            add_tone(left, right, t, duration, freq, amp, float(rng.uniform(0, 6.28)), 0.025 + 0.012 * idx, 2 + idx % 3)
        add_shimmer(left, right, t, duration, rng, 0.016, 5)
    elif kind == "MUS_Warning_LowPulse":
        add_tone(left, right, t, duration, 55.0, 0.13, float(rng.uniform(0, 6.28)), 0.018, 2)
        add_tone(left, right, t, duration, 82.41, 0.065, float(rng.uniform(0, 6.28)), 0.025, 3)
        add_low_pulse(left, right, t, duration, 55.0, 0.23, 42 + variant * 3, float(rng.uniform(0, 6.28)))
        add_tone(left, right, t, duration, 77.78, 0.03, float(rng.uniform(0, 6.28)), 0.05, 5)
    elif kind == "MUS_Storm_Phase1":
        notes = [(73.42, 0.16), (110.0, 0.09), (130.81, 0.055), (155.56, 0.04)]
        for idx, (freq, amp) in enumerate(notes):
            add_tone(left, right, t, duration, freq, amp, float(rng.uniform(0, 6.28)), 0.03 + idx * 0.012, 3 + idx)
        add_low_pulse(left, right, t, duration, 36.71, 0.11, 28 + variant * 2, float(rng.uniform(0, 6.28)))
        add_shimmer(left, right, t, duration, rng, 0.020, 5)
    elif kind == "MUS_Storm_Phase2":
        notes = [(73.42, 0.17), (77.78, 0.075), (103.83, 0.065), (138.59, 0.055), (207.65, 0.028)]
        for idx, (freq, amp) in enumerate(notes):
            add_tone(left, right, t, duration, freq, amp, float(rng.uniform(0, 6.28)), 0.035 + idx * 0.013, 3 + idx % 4)
        add_low_pulse(left, right, t, duration, 36.71, 0.16, 40 + variant * 3, float(rng.uniform(0, 6.28)))
        add_shimmer(left, right, t, duration, rng, 0.027, 7)
    elif kind == "MUS_Storm_Phase3":
        notes = [(73.42, 0.18), (77.78, 0.09), (92.50, 0.06), (103.83, 0.055), (116.54, 0.045), (155.56, 0.03)]
        for idx, (freq, amp) in enumerate(notes):
            add_tone(left, right, t, duration, freq, amp, float(rng.uniform(0, 6.28)), 0.04 + idx * 0.012, 2 + idx % 5)
        add_low_pulse(left, right, t, duration, 36.71, 0.19, 54 + variant * 4, float(rng.uniform(0, 6.28)))
        add_shimmer(left, right, t, duration, rng, 0.032, 8)
    else:
        raise ValueError(kind)

    return normalize(np.stack((left, right), axis=1))


def synth_finale(variant: int, duration: float) -> np.ndarray:
    n = int(round(duration * SR))
    t = np.arange(n, dtype=np.float32) / np.float32(SR)
    left = np.zeros(n, dtype=np.float32)
    right = np.zeros(n, dtype=np.float32)
    rng = np.random.default_rng(seed_for("MUS_Finale_Success", variant))
    notes = [(73.42, 0.13), (110.0, 0.09), (146.83, 0.08), (185.0, 0.055), (220.0, 0.04), (293.66, 0.025)]
    for idx, (freq, amp) in enumerate(notes):
        phase = float(rng.uniform(0.0, 2.0 * np.pi))
        width = 0.025 + 0.012 * idx
        left += amp * (0.82 * np.sin(2 * np.pi * freq * t + phase) + 0.14 * np.sin(2 * np.pi * freq * 2 * t + phase * 0.7))
        right += amp * (0.82 * np.sin(2 * np.pi * freq * t + phase + width) + 0.14 * np.sin(2 * np.pi * freq * 2 * t + phase * 0.7 + width))
    p = t / np.float32(duration)
    attack = np.minimum(1.0, p / 0.12)
    release = np.minimum(1.0, (1.0 - p) / 0.22)
    shape = np.power(np.maximum(0.0, attack * release), 1.25).astype(np.float32)
    lift = (0.72 + 0.28 * np.minimum(1.0, p / 0.45)).astype(np.float32)
    left *= shape * lift
    right *= shape * lift
    return normalize(np.stack((left, right), axis=1))


def normalize(stereo: np.ndarray) -> np.ndarray:
    maximum = float(np.max(np.abs(stereo))) if stereo.size else 1.0
    if maximum < 1e-9:
        return stereo
    return (stereo * np.float32(PEAK / maximum)).astype(np.float32, copy=False)


def write_wav24(path: Path, stereo: np.ndarray, chunk_frames: int = 262_144) -> None:
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(3)
        wav.setframerate(SR)
        scale = np.float32((1 << 23) - 1)
        for start in range(0, stereo.shape[0], chunk_frames):
            chunk = stereo[start : start + chunk_frames]
            ints = np.rint(np.clip(chunk, -1.0, 1.0) * scale).astype(np.int32)
            unsigned = ints.astype(np.uint32) & np.uint32(0xFFFFFF)
            packed = np.empty((unsigned.shape[0], 2, 3), dtype=np.uint8)
            packed[:, :, 0] = unsigned & 0xFF
            packed[:, :, 1] = (unsigned >> 8) & 0xFF
            packed[:, :, 2] = (unsigned >> 16) & 0xFF
            wav.writeframesraw(packed.tobytes(order="C"))
        wav.writeframes(b"")


def generate_track(kind: str, variant: int, duration: float, loop: bool) -> np.ndarray:
    return synth_loop(kind, variant, duration) if loop else synth_finale(variant, duration)


def generate(output: Path, only: str | None = None) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    files = []
    for event_id, spec in TRACKS.items():
        for variant in range(1, int(spec["count"]) + 1):
            name = f"{event_id}_{variant:02d}.wav"
            if only and name != only:
                continue
            duration = float(spec["duration"])
            audio = generate_track(event_id, variant, duration, bool(spec["loop"]))
            path = output / name
            write_wav24(path, audio)
            payload = path.read_bytes()
            files.append({
                "event_id": event_id,
                "variant": variant,
                "file": name,
                "state": spec["state"],
                "loop": bool(spec["loop"]),
                "duration_seconds": duration,
                "channels": 2,
                "sample_rate_hz": SR,
                "bit_depth": 24,
                "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            })
            del audio

    metadata = {
        "pack": "Project OEN authored adaptive music candidate v1",
        "qa_status": "candidate-headset-listen",
        "event_count": len({row["event_id"] for row in files}),
        "file_count": len(files),
        "sample_rate_hz": SR,
        "bit_depth": 24,
        "channels": 2,
        "peak_dbfs": PEAK_DBFS,
        "generator": "tools/generate_authored_adaptive_music.py",
        "generator_version": GENERATOR_VERSION,
        "numpy_version": NUMPY_VERSION,
        "third_party_samples": False,
        "files": files,
    }
    (output / "pack_manifest.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    (output / "LICENSE.txt").write_text(
        "Project OEN authored adaptive music candidate v1\n\n"
        "Original procedural works generated for Project OEN. No third-party samples are embedded.\n"
        "Candidate material: headset/listening approval is required before production promotion.\n",
        encoding="utf-8",
    )
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("build/oen-authored-adaptive-music-v1"))
    parser.add_argument("--zip", dest="zip_path", type=Path)
    parser.add_argument("--clean", action="store_true")
    parser.add_argument("--only", help="Generate one exact WAV filename, e.g. MUS_Warning_LowPulse_01.wav")
    args = parser.parse_args()
    if args.clean and args.output.exists():
        shutil.rmtree(args.output)
    metadata = generate(args.output, args.only)
    if args.zip_path:
        args.zip_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(args.zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            for path in sorted(args.output.iterdir()):
                archive.write(path, arcname=path.name)
    print(f"Generated {metadata['file_count']} authored adaptive-music WAV files ({metadata['event_count']} events) in {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
