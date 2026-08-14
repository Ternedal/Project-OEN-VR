#!/usr/bin/env python3
"""Restore useful alpha coverage for the final Stormnatten ash and wet-sheen VFX.

Visual VFX V2 made the ash deliberately fine and the sheen deliberately restrained,
but the production gate correctly requires enough visible coverage / peak alpha to
survive mipmapping and headset distance. This pass improves those two effects without
changing the validator or the canonical state contract.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageFilter

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PROD=ROOT/"Assets"/"ProjectOEN"/"ProductionArt"
MANIFEST=PROD/"Docs"/"production_art_manifest.json"
SIZE=1024


def rng(seed:str): return random.Random(int(hashlib.sha256(seed.encode()).hexdigest()[:16],16))


def rgba(alpha,color):
    out=Image.new("RGBA",alpha.size,color); out.putalpha(alpha); return out


def build_ash(seed:str)->Image.Image:
    """Fine but sufficiently populated drifting ash/soot flakes."""
    r=rng(seed); alpha=Image.new("L",(SIZE,SIZE),0); d=ImageDraw.Draw(alpha); cx,cy=SIZE*.5,SIZE*.52
    # More flakes, still individually small. The distribution remains clustered so
    # it reads as a particle texture rather than opaque noise.
    for i in range(30):
        x=cx+r.uniform(-.235,.235)*SIZE; y=cy+r.uniform(-.205,.205)*SIZE; rr=r.uniform(7,23)
        pts=[]
        corners=7+r.randrange(3)
        for j in range(corners):
            a=2*math.pi*j/corners+r.uniform(-.16,.16); rad=rr*r.uniform(.62,1.28)
            pts.append((x+math.cos(a)*rad,y+math.sin(a)*rad*.58))
        d.polygon(pts,fill=r.randint(125,225))
        # A faint downward smear gives each flake motion/readability in VR.
        if i%3==0:
            d.line((x,y,x+r.uniform(-5,5),y+r.uniform(16,34)),fill=r.randint(75,125),width=r.randint(2,4))
    alpha=alpha.filter(ImageFilter.GaussianBlur(1.25))
    soft=alpha.filter(ImageFilter.GaussianBlur(5)).point(lambda p:int(p*.20))
    base=rgba(soft,(118,122,116,255)); core=rgba(alpha,(194,191,177,255))
    return Image.alpha_composite(base,core)


def strengthen_wet_sheen(path:Path)->None:
    """Lift only the alpha response; keep V2's streak/puddle silhouette intact."""
    with Image.open(path) as src:
        im=src.convert("RGBA")
    a=im.getchannel("A")
    # Preserve zero-alpha gutter exactly while giving the bright streaks a useful
    # headset/mip peak. Mid values remain translucent; this is not an opacity fill.
    a=a.point(lambda p: 0 if p==0 else min(215,int(p*2.05+8)))
    # Reinforce the brightest original lines very slightly without broadening the mask.
    im.putalpha(a)
    im.save(path,compress_level=6)


def main()->int:
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    ash_rows=[e for e in manifest if e.get("kind")=="sprite" and str(e.get("asset_id"))=="FX-003"]
    sheen_rows=[e for e in manifest if e.get("kind")=="sprite" and str(e.get("asset_id"))=="FX-005"]
    if len(ash_rows)!=1 or len(sheen_rows)!=1:
        raise SystemExit(f"Expected one FX-003 and one FX-005 state, got ash={len(ash_rows)} sheen={len(sheen_rows)}")
    ash_path=ROOT/ash_rows[0]["path"]
    build_ash("Stormnatten.VFX.v2:FX-003:single:coverage").save(ash_path,compress_level=6)
    sheen_path=ROOT/sheen_rows[0]["path"]
    strengthen_wet_sheen(sheen_path)

    # Self-check the exact production minima so a future edit fails here, before the
    # broader validator. These are effect quality requirements, not relaxed gates.
    with Image.open(ash_path) as src:
        aa=src.convert("RGBA").getchannel("A"); visible=sum(1 for p in aa.getdata() if p>8); amin,amax=aa.getextrema()
    with Image.open(sheen_path) as src:
        sa=src.convert("RGBA").getchannel("A"); smin,smax=sa.getextrema()
    if visible<7000 or amin!=0 or amax<120:
        raise SystemExit(f"Ash alpha self-check failed: visible={visible}, range={(amin,amax)}")
    if smin!=0 or smax<120:
        raise SystemExit(f"Wet sheen alpha self-check failed: range={(smin,smax)}")
    print(f"VFX alpha repair: ash visible={visible}, ash range={(amin,amax)}, wet sheen range={(smin,smax)}")
    return 0


if __name__=="__main__": raise SystemExit(main())
