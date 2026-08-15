#!/usr/bin/env python3
"""Render visual review sheets for the actual Project ØEN production sprites/VFX.

The production pack contains many separate canonical PNGs. Technical manifest checks do
not answer the art-direction question, so this script creates deterministic contact
sheets from the files that will actually ship after UI and VFX refinement:

* one representative sprite sheet with up to three states from every non-VFX category;
* one complete 14-state VFX sheet;
* one decal sheet from all production decal PNGs.

Transparent artwork is shown on a neutral checkerless storm/cloth background so alpha
edges and diegetic contrast remain visible. No source image is modified.
"""
from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PROD=ROOT/"Assets"/"ProductionArt"
MANIFEST=PROD/"Docs"/"production_art_manifest.json"
OUT=HERE/"review_renders"
VFX_CATEGORY="VFX support graphics"


def composite_card(path:Path,size=(250,180))->Image.Image:
    w,h=size
    bg=Image.new("RGB",size,(27,34,31)); d=ImageDraw.Draw(bg)
    d.rectangle((0,h//2,w,h),fill=(45,45,38))
    d.line((0,h//2,w,h//2),fill=(68,70,58),width=1)
    with Image.open(path) as src:
        im=src.convert("RGBA")
        # Keep transparent sprite intact, scale down only.
        thumb=ImageOps.contain(im,(w-24,h-24),Image.Resampling.LANCZOS)
    x=(w-thumb.width)//2; y=(h-thumb.height)//2
    bg=bg.convert("RGBA"); bg.alpha_composite(thumb,(x,y)); return bg.convert("RGB")


def representative(entries:list[dict],maxn=3)->list[dict]:
    rows=sorted(entries,key=lambda e:(str(e.get("asset_id","")),str(e.get("variant","")),str(e.get("path",""))))
    if len(rows)<=maxn:return rows
    idx=[0,(len(rows)-1)//2,len(rows)-1]
    return [rows[i] for i in idx]


def render_category_sheet(groups:dict[str,list[dict]],path:Path)->None:
    cats=sorted(groups)
    rows=[]
    for cat in cats:
        for e in representative(groups[cat],3): rows.append((cat,e))
    cols=3; cw,ch=290,235; header=74; nrows=math.ceil(len(rows)/cols)
    sheet=Image.new("RGB",(cols*cw,header+nrows*ch),(13,17,15)); d=ImageDraw.Draw(sheet)
    d.text((18,18),"PROJECT ØEN — ACTUAL PRODUCTION SPRITE REVIEW",fill=(232,226,205))
    d.text((18,43),"Representative canonical states from every non-VFX sprite category after final UI refinement.",fill=(144,160,143))
    for i,(cat,e) in enumerate(rows):
        x=(i%cols)*cw; y=header+(i//cols)*ch
        d.rectangle((x,y,x+cw-1,y+ch-1),fill=(20,25,22),outline=(50,58,50))
        p=ROOT/e["path"]
        if not p.exists(): raise SystemExit(f"Missing sprite review input: {p}")
        card=composite_card(p,(250,180)); sheet.paste(card,(x+20,y+38))
        label=f"{e.get('asset_id','')} / {e.get('variant','default')}"
        d.text((x+12,y+9),cat[:38],fill=(209,204,185))
        d.text((x+12,y+24),label[:40],fill=(135,158,139))
    sheet.save(path,compress_level=6)


def render_vfx(entries:list[dict],path:Path)->None:
    rows=sorted(entries,key=lambda e:(str(e.get("asset_id","")),str(e.get("variant",""))))
    cols=4; cw,ch=250,225; header=68; nrows=math.ceil(len(rows)/cols)
    sheet=Image.new("RGB",(cols*cw,header+nrows*ch),(12,16,15)); d=ImageDraw.Draw(sheet)
    d.text((18,17),"PROJECT ØEN — COMPLETE PRODUCTION VFX REVIEW",fill=(232,226,205))
    d.text((18,41),"All canonical VFX textures after dedicated refinement; alpha shown over neutral storm ground.",fill=(144,160,143))
    for i,e in enumerate(rows):
        x=(i%cols)*cw; y=header+(i//cols)*ch; p=ROOT/e["path"]
        if not p.exists(): raise SystemExit(f"Missing VFX review input: {p}")
        d.rectangle((x,y,x+cw-1,y+ch-1),fill=(20,25,22),outline=(50,58,50))
        sheet.paste(composite_card(p,(220,170)),(x+15,y+36))
        d.text((x+11,y+9),f"{e.get('asset_id')} / {e.get('variant','default')}",fill=(209,204,185))
    sheet.save(path,compress_level=6)


def render_decals(path:Path)->None:
    files=sorted((PROD/"Decals").rglob("*.png"))
    if not files:
        # Decals are optional to this renderer; production validator owns exact count.
        Image.new("RGB",(640,120),(13,17,15)).save(path); return
    cols=3; cw,ch=290,225; header=65; nrows=math.ceil(len(files)/cols)
    sheet=Image.new("RGB",(cols*cw,header+nrows*ch),(13,17,15)); d=ImageDraw.Draw(sheet)
    d.text((18,18),"PROJECT ØEN — PRODUCTION DECAL REVIEW",fill=(232,226,205))
    d.text((18,41),"Every generated environment/set-dressing decal, composited over a neutral surface.",fill=(144,160,143))
    for i,p in enumerate(files):
        x=(i%cols)*cw; y=header+(i//cols)*ch
        d.rectangle((x,y,x+cw-1,y+ch-1),fill=(20,25,22),outline=(50,58,50))
        sheet.paste(composite_card(p,(250,170)),(x+20,y+36))
        d.text((x+10,y+10),p.stem[:42],fill=(205,201,183))
    sheet.save(path,compress_level=6)


def main()->int:
    OUT.mkdir(parents=True,exist_ok=True)
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    sprites=[e for e in manifest if e.get("kind")=="sprite"]
    if not sprites: raise SystemExit("No production sprite entries in manifest")
    groups=defaultdict(list); vfx=[]
    for e in sprites:
        cat=str(e.get("category","Uncategorized"))
        if cat==VFX_CATEGORY: vfx.append(e)
        else: groups[cat].append(e)
    if len(vfx)!=14: raise SystemExit(f"Expected 14 canonical VFX states, found {len(vfx)}")
    render_category_sheet(groups,OUT/"sprite_category_contact_sheet.png")
    render_vfx(vfx,OUT/"vfx_contact_sheet.png")
    render_decals(OUT/"decal_contact_sheet.png")
    print(f"Rendered sprite review for {len(groups)} categories / {len(sprites)-len(vfx)} non-VFX states; complete {len(vfx)}-state VFX review + decals")
    return 0

if __name__=="__main__": raise SystemExit(main())
