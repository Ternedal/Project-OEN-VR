#!/usr/bin/env python3
"""Generate PROJECT ØEN AU-1 synthetic source cues.

These cues are deliberately limited to tactile/UI/system feedback that can be
credibly designed procedurally. Naturalistic ambience, rope, shelter and fire
recordings are NOT generated here and remain separate source-production work.

Output: mono PCM WAV, 48 kHz, 16-bit. Deterministic for a given script version.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import struct
import wave
from pathlib import Path

SR = 48_000
RNG = random.Random(42)


def adsr(n: int, attack: float = 0.004, decay: float = 0.04,
         sustain: float = 0.55, release: float = 0.08) -> list[float]:
    a = max(1, int(attack * SR))
    d = max(1, int(decay * SR))
    r = max(1, int(release * SR))
    env = [1.0] * n
    for i in range(min(a, n)):
        env[i] = i / a
    for i in range(a, min(a + d, n)):
        p = (i - a) / d
        env[i] = 1.0 + (sustain - 1.0) * p
    start_r = max(a + d, n - r)
    if start_r < n:
        start_value = env[start_r - 1] if start_r > 0 else sustain
        length = n - start_r
        for i in range(start_r, n):
            p = (i - start_r) / max(1, length - 1)
            env[i] = start_value * (1.0 - p)
    return env


def tone(freq: float, dur: float, amp: float = 0.2, decay: float | None = None) -> list[float]:
    n = int(dur * SR)
    env = adsr(n, release=min(0.08, dur / 3))
    out = []
    for i in range(n):
        t = i / SR
        value = amp * math.sin(2 * math.pi * freq * t)
        if decay is not None:
            value *= math.exp(-t / decay)
        else:
            value *= env[i]
        out.append(value)
    return out


def chirp(f0: float, f1: float, dur: float, amp: float = 0.2) -> list[float]:
    n = int(dur * SR)
    env = adsr(n, release=min(0.08, dur / 3))
    k = (f1 - f0) / dur
    out = []
    for i in range(n):
        t = i / SR
        phase = 2 * math.pi * (f0 * t + 0.5 * k * t * t)
        out.append(amp * math.sin(phase) * env[i])
    return out


def noise_click(dur: float = 0.04, amp: float = 0.15, decay: float = 0.012) -> list[float]:
    n = int(dur * SR)
    raw = [RNG.uniform(-1.0, 1.0) for _ in range(n)]
    out = []
    for i in range(n):
        lo = max(0, i - 2)
        hi = min(n, i + 3)
        smoothed = sum(raw[lo:hi]) / (hi - lo)
        t = i / SR
        out.append(smoothed * amp * math.exp(-t / decay))
    return out


def mix(parts: list[tuple[float, list[float]]], total: float, gain: float = 0.9) -> list[float]:
    n = int(total * SR)
    out = [0.0] * n
    for offset, samples in parts:
        start = int(offset * SR)
        for j, sample in enumerate(samples):
            i = start + j
            if i >= n:
                break
            out[i] += sample
    # Gentle saturation avoids brittle digital clipping.
    out = [math.tanh(v * 1.15) for v in out]
    peak = max(abs(v) for v in out) if out else 1.0
    scale = (0.92 / peak) if peak > 0.92 else 1.0
    return [v * scale * gain for v in out]


def cue_set() -> dict[str, list[float]]:
    return {
        "SFX_MARKER_PICKUP_001.wav": mix([
            (0.000, noise_click(0.035, 0.15, 0.008)),
            (0.005, tone(620, 0.10, 0.22, 0.05)),
            (0.045, tone(930, 0.11, 0.18, 0.055)),
        ], 0.20),
        "SFX_MARKER_PLACE_001.wav": mix([
            (0.000, noise_click(0.055, 0.20, 0.012)),
            (0.006, tone(310, 0.14, 0.30, 0.065)),
            (0.025, tone(520, 0.10, 0.12, 0.04)),
        ], 0.22),
        "SFX_MARKER_MOVE_001.wav": mix([
            (0.000, noise_click(0.025, 0.10, 0.007)),
            (0.005, chirp(520, 720, 0.13, 0.20)),
        ], 0.18),
        "SFX_PLAN_READY_001.wav": mix([
            (0.000, tone(494, 0.16, 0.18)),
            (0.110, tone(659, 0.22, 0.19)),
        ], 0.38),
        "SFX_PLAN_LOCK_001.wav": mix([
            (0.000, noise_click(0.06, 0.22, 0.014)),
            (0.000, tone(220, 0.18, 0.25, 0.07)),
            (0.100, tone(660, 0.22, 0.17)),
            (0.180, tone(880, 0.18, 0.13)),
        ], 0.42),
        "SFX_PLAN_CONFLICT_001.wav": mix([
            (0.000, tone(440, 0.15, 0.17)),
            (0.100, tone(370, 0.17, 0.15)),
            (0.200, tone(320, 0.20, 0.13)),
        ], 0.46),
        "UIA_JOIN_SUCCESS_001.wav": mix([
            (0.000, tone(392, 0.13, 0.15)),
            (0.090, tone(523.25, 0.15, 0.17)),
            (0.180, tone(659.25, 0.22, 0.18)),
        ], 0.45),
        "UIA_RECONNECT_START_001.wav": mix([
            (0.000, tone(260, 0.12, 0.13)),
            (0.180, tone(260, 0.12, 0.13)),
        ], 0.45),
        "UIA_RECONNECT_SUCCESS_001.wav": mix([
            (0.000, chirp(360, 520, 0.16, 0.15)),
            (0.120, tone(659, 0.23, 0.17)),
        ], 0.42),
        "SFX_CONFIRM_001.wav": mix([
            (0.000, noise_click(0.025, 0.07, 0.006)),
            (0.005, tone(720, 0.18, 0.17, 0.08)),
        ], 0.26),
        "SFX_WARNING_001.wav": mix([
            (0.000, tone(250, 0.13, 0.16)),
            (0.170, tone(250, 0.13, 0.16)),
        ], 0.42),
        "SFX_ERROR_SOFT_001.wav": mix([
            (0.000, chirp(430, 330, 0.24, 0.15)),
            (0.080, tone(220, 0.18, 0.08, 0.08)),
        ], 0.38),
    }


def write_wav(path: Path, samples: list[float]) -> dict[str, object]:
    path.parent.mkdir(parents=True, exist_ok=True)
    peak = max(abs(v) for v in samples) if samples else 0.0
    pcm = bytearray()
    for value in samples:
        value = max(-0.98, min(0.98, value))
        pcm.extend(struct.pack("<h", round(value * 32767)))
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SR)
        wav.writeframes(bytes(pcm))
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return {
        "file": path.name,
        "sampleRate": SR,
        "bitDepth": 16,
        "channels": 1,
        "durationSeconds": round(len(samples) / SR, 3),
        "peakLinearBeforeQuantize": round(peak, 6),
        "sha256": digest,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("generated_au1"))
    args = parser.parse_args()

    # Reset RNG so repeated invocations are deterministic in one interpreter.
    RNG.seed(42)
    manifest = []
    for name, samples in cue_set().items():
        manifest.append(write_wav(args.output / name, samples))

    (args.output / "manifest.json").write_text(
        json.dumps({"source": "generate_au1.py", "cues": manifest}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Generated {len(manifest)} AU-1 cues in {args.output}")
    for row in manifest:
        print(f"  {row['file']}: {row['durationSeconds']} s, peak {row['peakLinearBeforeQuantize']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
