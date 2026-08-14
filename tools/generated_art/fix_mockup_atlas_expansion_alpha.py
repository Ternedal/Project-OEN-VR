#!/usr/bin/env python3
"""Apply approved-atlas raster V2, then guarantee shoreline-spray visibility.

The workflow already calls this post-generation stage after creating the structural
atlas expansion. Raster V2 is now authoritative for all 40 expansion sprites: it
rebuilds them from the committed approved reference panels. The final small alpha
repair keeps calm shoreline spray visible through mipmapping/headset distance.
"""
from __future__ import annotations

import json
from pathlib import Path
from PIL import Image

from refine_mockup_atlas_expansion_raster_v2 import main as rebuild_raster_v2

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
MANIFEST=ROOT/"Assets"/"ProjectOEN"/"ProductionArt"/"Docs"/"mockup_atlas_expansion_manifest.json"


def main()->int:
    rc=rebuild_raster_v2()
    if rc not in (None,0):
        raise SystemExit(rc)

    data=json.loads(MANIFEST.read_text(encoding="utf-8")); rows=[e for e in data.get("entries",[]) if e.get("asset_id")=="AX-SKY-003"]
    if {e.get("variant") for e in rows}!={"calm","storm"}: raise SystemExit(f"Unexpected AX-SKY-003 states: {rows}")
    results={}
    for e in rows:
        path=ROOT/e["path"]
        with Image.open(path) as src: im=src.convert("RGBA")
        a=im.getchannel("A"); variant=str(e["variant"])
        factor=1.40 if variant=="calm" else 1.12
        a=a.point(lambda p: 0 if p==0 else min(235,int(p*factor+4)))
        im.putalpha(a); im.save(path,compress_level=6)
        lo,hi=a.getextrema(); results[variant]=(lo,hi)
        if lo!=0 or hi<120: raise SystemExit(f"{variant} shoreline spray alpha remains too weak: {(lo,hi)}")
    print(f"Approved-atlas raster V2 applied; shoreline-spray alpha verified: {results}")
    return 0


if __name__=="__main__": raise SystemExit(main())
