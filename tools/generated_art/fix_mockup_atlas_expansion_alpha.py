#!/usr/bin/env python3
"""Keep atlas-expansion shoreline spray visible through mipmapping/headset distance.

The calm variant is intentionally restrained, but the first expansion gate showed its
peak alpha (90) was below the established Unity sprite visibility floor. Lift only
non-zero spray pixels, preserving transparent gutters and the calm/storm distinction.
"""
from __future__ import annotations

import json
from pathlib import Path
from PIL import Image

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
MANIFEST=ROOT/"Assets"/"ProjectOEN"/"ProductionArt"/"Docs"/"mockup_atlas_expansion_manifest.json"


def main()->int:
    data=json.loads(MANIFEST.read_text(encoding="utf-8")); rows=[e for e in data.get("entries",[]) if e.get("asset_id")=="AX-SKY-003"]
    if {e.get("variant") for e in rows}!={"calm","storm"}: raise SystemExit(f"Unexpected AX-SKY-003 states: {rows}")
    results={}
    for e in rows:
        path=ROOT/e["path"]
        with Image.open(path) as src: im=src.convert("RGBA")
        a=im.getchannel("A"); variant=str(e["variant"])
        factor=1.62 if variant=="calm" else 1.15
        a=a.point(lambda p: 0 if p==0 else min(220,int(p*factor+4)))
        im.putalpha(a); im.save(path,compress_level=6)
        lo,hi=a.getextrema(); results[variant]=(lo,hi)
        if lo!=0 or hi<120: raise SystemExit(f"{variant} shoreline spray alpha remains too weak: {(lo,hi)}")
    print(f"Atlas shoreline-spray alpha repaired: {results}")
    return 0


if __name__=="__main__": raise SystemExit(main())
