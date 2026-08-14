#!/usr/bin/env python3
"""Validate Project ØEN surface weathering and packed material-response maps."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROD = ROOT / "Assets" / "ProjectOEN" / "ProductionArt"
TEX = PROD / "Materials" / "Textures"
REPORT = PROD / "Docs" / "surface_weathering.json"
NAMES = ("wood","rope","tarp","metal","stone","leaf","cloth","mud","fire","char","water")


def main() -> int:
    errors = []
    stats = {}

    if not REPORT.exists():
        errors.append(f"Missing weathering report: {REPORT.relative_to(ROOT)}")
        report = {}
    else:
        try:
            report = json.loads(REPORT.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"Unreadable weathering report: {exc}")
            report = {}

    if report.get("material_count") != len(NAMES):
        errors.append(f"Weathering report material_count={report.get('material_count')} expected {len(NAMES)}")
    reported = report.get("materials", {})
    if set(reported) != set(NAMES):
        errors.append("Weathering report material set does not match canonical 11 materials")

    for name in NAMES:
        mask_path = TEX / f"{name}_metallic_smoothness.png"
        albedo_path = TEX / f"{name}_albedo.png"
        if not mask_path.exists() or not albedo_path.exists():
            errors.append(f"Missing weathered maps for {name}")
            continue

        with Image.open(mask_path) as im:
            rgba = im.convert("RGBA")
            if rgba.size != (512, 512):
                errors.append(f"{name}: packed mask wrong size {rgba.size}")
                continue
            metallic = rgba.getchannel("R")
            smooth = rgba.getchannel("A")
            mlo, mhi = metallic.getextrema()
            slo, shi = smooth.getextrema()
            stats[name] = {"metallic": [mlo, mhi], "smoothness": [slo, shi]}

            if shi - slo < 18:
                errors.append(f"{name}: smoothness is too flat ({slo}..{shi})")
            if name == "metal":
                if mhi - mlo < 24:
                    errors.append(f"metal: metallic response is too flat ({mlo}..{mhi})")
                if mlo < 100 or mhi > 245:
                    errors.append(f"metal: metallic response outside Quest-friendly authored range ({mlo}..{mhi})")
            elif mhi != 0:
                errors.append(f"{name}: non-metal material unexpectedly has metallic response ({mlo}..{mhi})")

        with Image.open(albedo_path) as im:
            rgb = im.convert("RGB")
            if rgb.size != (1024, 1024):
                errors.append(f"{name}: albedo wrong size {rgb.size}")
            extrema = rgb.getextrema()
            if all(hi - lo < 8 for lo, hi in extrema):
                errors.append(f"{name}: weathered albedo lacks useful variation {extrema}")

        meta = Path(str(mask_path) + ".meta")
        if not meta.exists():
            errors.append(f"{name}: packed mask Unity meta missing")

    print("Project ØEN surface-weathering QA")
    print(f"  materials : {len(NAMES)}")
    for name in NAMES:
        if name in stats:
            print(f"  {name:6} metallic={stats[name]['metallic']} smooth={stats[name]['smoothness']}")
    if errors:
        print(f"\nFAILED with {len(errors)} issue(s):")
        for error in errors:
            print(" - " + error)
        return 1

    print("\nPASS: weathered albedo and packed material response are varied, bounded and Unity-path stable.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
