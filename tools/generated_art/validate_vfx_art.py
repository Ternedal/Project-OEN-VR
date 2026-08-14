#!/usr/bin/env python3
"""Strict QA gate for the 14 Project ØEN production VFX textures."""
from __future__ import annotations

import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path
from PIL import Image, ImageStat

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PROD=ROOT/"Assets"/"ProjectOEN"/"ProductionArt"
MANIFEST=PROD/"Docs"/"production_art_manifest.json"
REPORT=PROD/"Docs"/"vfx_refinement.json"

EXPECTED={
 "FX-001":{"small","medium"},
 "FX-002":{"small","medium"},
 "FX-003":{"single"},
 "FX-004":{"small","medium"},
 "FX-005":{"single"},
 "FX-006":{"near","far"},
 "FX-007":{"fire","lantern"},
 "FX-008":{"small","medium"},
}


def inspect(path:Path):
    with Image.open(path) as src:
        rgba=src.convert("RGBA")
        a=rgba.getchannel("A")
        bbox=a.getbbox(); extrema=a.getextrema()
        visible=sum(1 for p in a.getdata() if p>8)
        strong=sum(1 for p in a.getdata() if p>180)
        # Many VFX textures intentionally use a nearly constant RGB tint and
        # encode their actual visual structure in alpha. Measure the rendered
        # result over black rather than hidden RGB beneath transparent pixels.
        black=Image.new("RGBA",rgba.size,(0,0,0,255))
        composed=Image.alpha_composite(black,rgba).convert("RGB")
        variance=sum(ImageStat.Stat(composed).var)
        return rgba.size,bbox,extrema,visible,strong,variance,hashlib.sha256(path.read_bytes()).hexdigest()


def smoke_cells(path:Path):
    with Image.open(path) as src:
        a=src.convert("RGBA").getchannel("A")
        cell=a.width//4
        occupied=0
        for cy in range(4):
            for cx in range(4):
                crop=a.crop((cx*cell,cy*cell,(cx+1)*cell,(cy+1)*cell))
                if crop.getbbox() is not None:
                    occupied+=1
        return occupied


def main()->int:
    errors=[]
    if not MANIFEST.exists() or not REPORT.exists():
        print("ERROR: production manifest or VFX refinement report missing")
        return 1
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    report=json.loads(REPORT.read_text(encoding="utf-8"))
    entries=[e for e in manifest if e.get("kind")=="sprite" and e.get("category")=="VFX support graphics"]
    if len(entries)!=14: errors.append(f"Expected 14 VFX production states, found {len(entries)}")
    if report.get("vfx_count")!=14: errors.append(f"VFX report count mismatch: {report.get('vfx_count')}")

    by=defaultdict(list); hashes=[]
    report_paths={e.get("path") for e in report.get("entries",[])}
    for e in entries:
        aid=str(e.get("asset_id")); variant=str(e.get("variant","default")); rel=str(e.get("path")); path=ROOT/rel
        by[aid].append(variant)
        if rel not in report_paths: errors.append(f"VFX state missing from refinement report: {rel}")
        if not path.exists(): errors.append(f"Missing VFX PNG: {rel}"); continue
        meta=Path(str(path)+".meta")
        if not meta.exists(): errors.append(f"Missing VFX .meta: {rel}")
        else:
            text=meta.read_text(encoding="utf-8")
            for token in ("alphaIsTransparency: 1","textureType: 8"):
                if token not in text: errors.append(f"VFX importer contract missing {token}: {rel}")
        try:
            size,bbox,extrema,visible,strong,variance,h=inspect(path)
        except Exception as ex:
            errors.append(f"Unreadable VFX PNG {rel}: {ex}"); continue
        hashes.append(h)
        if size!=(1024,1024): errors.append(f"VFX state must be 1024x1024: {rel} -> {size}")
        if bbox is None or visible<7000: errors.append(f"Too little VFX alpha content: {rel}")
        if extrema[0]!=0 or extrema[1]<120: errors.append(f"VFX alpha range lacks transparent gutter/useful peak: {rel} -> {extrema}")
        if visible>=1024*1024*.94: errors.append(f"VFX texture is effectively full-frame opaque: {rel}")
        if variance<20: errors.append(f"VFX rendered content suspiciously flat: {rel}")
        if aid=="FX-001" and smoke_cells(path)!=16: errors.append(f"Smoke flipbook must occupy all 16 cells: {rel}")

    for aid,expected in EXPECTED.items():
        got=set(by.get(aid,[]))
        if got!=expected: errors.append(f"{aid} variants mismatch: expected {sorted(expected)}, got {sorted(got)}")
    if set(by)!=set(EXPECTED): errors.append(f"Unexpected/missing VFX IDs: {sorted(set(by)^set(EXPECTED))}")
    if len(hashes)!=len(set(hashes)): errors.append("Two or more VFX states are byte-identical; states must be visually distinct")

    print("Project ØEN production VFX QA")
    print("  VFX states      : 14")
    print("  smoke flipbooks : 2 x 4x4")
    print("  particle/decal  : embers + ash + rain splash")
    print("  material helpers: wet sheen + glow")
    print("  screen/world FX : lightning + objective pulse")
    if errors:
        print(f"\nFAILED with {len(errors)} issue(s):")
        for e in errors: print(" - "+e)
        return 1
    print("\nPASS: all 14 VFX states are separate, nonblank, state-distinct Unity-importable RGBA textures.")
    return 0

if __name__=="__main__": sys.exit(main())
