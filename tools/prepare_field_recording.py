#!/usr/bin/env python3
"""Prepare licensed field recordings for Project OEN.

Requires ffmpeg on PATH. It never downloads source material; acquisition and license
review remain explicit. Output is 48 kHz / 24-bit PCM WAV with conservative loudness.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--spatial", action="store_true", help="Create mono derivative for 3D playback")
    parser.add_argument("--kind", choices=("bed", "oneshot"), default="bed")
    parser.add_argument("--start", help="Optional trim start, e.g. 00:00:12.5")
    parser.add_argument("--duration", help="Optional duration, e.g. 45.0")
    args = parser.parse_args()

    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise SystemExit("ffmpeg is required on PATH")
    if not args.input.is_file():
        raise SystemExit(f"missing input: {args.input}")

    args.output.parent.mkdir(parents=True, exist_ok=True)

    command = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y"]
    if args.start:
        command += ["-ss", args.start]
    command += ["-i", str(args.input)]
    if args.duration:
        command += ["-t", args.duration]

    filters = ["aresample=48000"]
    if args.spatial:
        filters.append("pan=mono|c0=0.5*c0+0.5*c1")

    # Leave enough headroom for simultaneous VR emitters. One-shots can sit higher
    # than continuous environmental beds, but both retain a -3 dBTP ceiling.
    integrated = -24 if args.kind == "bed" else -18
    filters.append(f"loudnorm=I={integrated}:TP=-3:LRA=12")

    command += [
        "-af", ",".join(filters),
        "-ar", "48000",
        "-c:a", "pcm_s24le",
        str(args.output),
    ]
    subprocess.run(command, check=True)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
