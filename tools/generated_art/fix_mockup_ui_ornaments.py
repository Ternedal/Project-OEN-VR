#!/usr/bin/env python3
"""Make BR-007 typography ornaments physically readable at VR scale.

The atlas-aligned UI V2 intentionally reduced these to restrained line work, but the
production sprite gate correctly rejected the result as too sparse. Rebuild the three
canonical variants as broad ivory/brass ornaments with transparent gutters and enough
visual mass to survive mipmapping and headset distance.
"""
from __future__ import annotations

import json
from pathlib import Path
from PIL import Image, ImageDraw

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PROD=ROOT/"Assets"/"ProductionArt"
MANIFEST=PROD/"Docs"/"production_art_manifest.json"
IVORY=(236,224,190,255); BRASS=(181,132,61,255); DARK=(62,49,32,255)


def diamond(d,cx,cy,r,fill=BRASS):
    d.polygon(((cx,cy-r),(cx+r,cy),(cx,cy+r),(cx-r,cy)),fill=fill)
    d.polygon(((cx,cy-r*.45),(cx+r*.45,cy),(cx,cy+r*.45),(cx-r*.45,cy)),fill=DARK)


def leaf(d,root,tip,width,fill=IVORY):
    x0,y0=root; x1,y1=tip; mx=(x0+x1)/2; my=(y0+y1)/2
    dx=x1-x0; dy=y1-y0; ln=(dx*dx+dy*dy)**.5 or 1; px=-dy/ln; py=dx/ln
    d.polygon(((x0,y0),(mx+px*width,my+py*width),(x1,y1),(mx-px*width,my-py*width)),fill=fill)
    d.line((x0,y0,x1,y1),fill=BRASS,width=max(3,int(width*.16)))


def render(variant,size):
    w,h=size; im=Image.new("RGBA",size,(0,0,0,0)); d=ImageDraw.Draw(im); v=variant.lower()
    if "corners" in v:
        pad=int(min(w,h)*.13); arm=int(min(w,h)*.31); thick=max(18,int(min(w,h)*.034))
        for sx,sy in ((1,1),(-1,1),(1,-1),(-1,-1)):
            cx=pad if sx>0 else w-pad; cy=pad if sy>0 else h-pad
            d.line((cx,cy,cx+sx*arm,cy),fill=IVORY,width=thick)
            d.line((cx,cy,cx,cy+sy*arm),fill=IVORY,width=thick)
            diamond(d,cx,cy,thick*1.25)
            leaf(d,(cx+sx*thick,cy+sy*thick),(cx+sx*arm*.62,cy+sy*arm*.34),thick*.75)
            leaf(d,(cx+sx*thick,cy+sy*thick),(cx+sx*arm*.34,cy+sy*arm*.62),thick*.75)
    elif "dividers" in v:
        cy=h//2; x0=int(w*.10); x1=int(w*.90); thick=max(18,int(min(w,h)*.032))
        d.line((x0,cy,x1,cy),fill=IVORY,width=thick)
        d.line((x0,cy-thick*1.4,x0,cy+thick*1.4),fill=BRASS,width=thick//2)
        d.line((x1,cy-thick*1.4,x1,cy+thick*1.4),fill=BRASS,width=thick//2)
        diamond(d,w//2,cy,thick*2.0)
        for off in (-.22,.22):
            cx=w*(.5+off)
            leaf(d,(cx-thick*1.5,cy),(cx-thick*5.0,cy-thick*2.4),thick*.72)
            leaf(d,(cx+thick*1.5,cy),(cx+thick*5.0,cy+thick*2.4),thick*.72)
    else:  # lines
        x0=int(w*.11); x1=int(w*.89); thick=max(15,int(min(w,h)*.025))
        for i,y in enumerate((h*.34,h*.50,h*.66)):
            inset=int(w*(.05*i))
            d.line((x0+inset,y,x1-inset,y),fill=IVORY if i==1 else BRASS,width=thick if i==1 else max(10,thick//2))
            diamond(d,w//2,y,thick*(1.65 if i==1 else 1.15),BRASS if i==1 else IVORY)
        leaf(d,(w*.22,h*.50),(w*.11,h*.39),thick*.85)
        leaf(d,(w*.78,h*.50),(w*.89,h*.61),thick*.85)
    return im


def main():
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8")); count=0
    for e in manifest:
        if e.get("kind")!="sprite" or str(e.get("asset_id",""))!="BR-007": continue
        path=ROOT/e["path"]
        with Image.open(path) as src: size=src.size
        render(str(e.get("variant","default")),size).save(path,compress_level=6); count+=1
    if count!=3: raise SystemExit(f"Expected 3 BR-007 ornament variants, rebuilt {count}")
    print("Rebuilt 3 BR-007 typography ornaments with VR-readable visual mass")
    return 0

if __name__=="__main__": raise SystemExit(main())
