#!/usr/bin/env python3
"""Validate the refined Project ØEN Quest-friendly surface map set."""
from __future__ import annotations

import sys
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TEX = ROOT / "Assets" / "ProjectOEN" / "ProductionArt" / "Materials" / "Textures"
NAMES = ("wood","rope","tarp","metal","stone","leaf","cloth","mud","fire","char","water")


def main() -> int:
    errors=[]; checked=0
    for name in NAMES:
        specs=((f"{name}_albedo.png",(1024,1024)),(f"{name}_normal.png",(512,512)),(f"{name}_metallic_smoothness.png",(512,512)))
        for filename,size in specs:
            path=TEX/filename
            if not path.exists():
                errors.append(f"Missing surface map: {path.relative_to(ROOT)}"); continue
            try:
                with Image.open(path) as im:
                    im.load()
                    if im.size != size:
                        errors.append(f"Wrong map size: {filename}: {im.size} != {size}")
                    extrema=im.convert("RGB").getextrema()
                    if any(lo==hi for lo,hi in extrema) and "metallic_smoothness" not in filename:
                        errors.append(f"Surface map lacks useful variation: {filename}: {extrema}")
            except Exception as exc:
                errors.append(f"Unreadable surface map {filename}: {exc}")
            if not Path(str(path)+".meta").exists():
                errors.append(f"Missing Unity meta: {filename}.meta")
            checked += 1

    # Normal maps must actually be imported as normal maps in Unity.
    for name in NAMES:
        meta=Path(str(TEX/f"{name}_normal.png")+".meta")
        if meta.exists() and "textureType: 1" not in meta.read_text(encoding="utf-8",errors="replace"):
            errors.append(f"Normal map importer is not textureType 1: {meta.name}")

    print("Project ØEN material-texture QA")
    print(f"  materials : {len(NAMES)}")
    print(f"  maps      : {checked}")
    if errors:
        print(f"\nFAILED with {len(errors)} issue(s):")
        for e in errors: print(" - "+e)
        return 1
    print("\nPASS: refined surface maps are complete and Unity-importable.")
    return 0


if __name__=="__main__":
    sys.exit(main())
