#!/usr/bin/env python3
"""Render visual QA contact sheets for the Project ØEN mockup-atlas expansion.

The expansion only counts as useful if the new families visibly match the approved
atlas direction. This renderer shows the actual generated backgrounds, maps,
documents, wildlife, food and weather sprites plus texture-aware turntables of all
new tool/crafting/communication OBJ families.
"""
from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from render_mockup_review import render_obj

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PROD=ROOT/"Assets"/"ProjectOEN"/"ProductionArt"
MANIFEST=PROD/"Docs"/"mockup_atlas_expansion_manifest.json"
OUT=HERE/"review_renders"


def font(size:int,bold=False):
    for p in (("/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf"),
              ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")):
        try:return ImageFont.truetype(p,size)
        except OSError:pass
    return ImageFont.load_default()


def checker(size,cell=18):
    w,h=size; im=Image.new("RGB",size,(31,36,34)); d=ImageDraw.Draw(im)
    for y in range(0,h,cell):
        for x in range(0,w,cell):
            if (x//cell+y//cell)%2: d.rectangle((x,y,x+cell,y+cell),fill=(38,44,41))
    return im


def sprite_card(entry,size=(360,300)):
    w,h=size; card=Image.new("RGB",size,(14,19,17)); d=ImageDraw.Draw(card)
    d.rectangle((0,0,w,48),fill=(10,14,13)); d.text((12,8),str(entry["asset_id"]),font=font(16,True),fill=(229,220,194)); d.text((82,8),str(entry["variant"]).replace("_"," ").upper(),font=font(13,False),fill=(121,178,184))
    src_path=ROOT/entry["path"]
    with Image.open(src_path) as src:
        rgba=src.convert("RGBA")
    area=(18,60,w-18,h-18); aw=area[2]-area[0]; ah=area[3]-area[1]
    scale=min(aw/rgba.width,ah/rgba.height); nw=max(1,int(rgba.width*scale)); nh=max(1,int(rgba.height*scale))
    resized=rgba.resize((nw,nh),Image.Resampling.LANCZOS)
    bg=checker((aw,ah)); x=(aw-nw)//2; y=(ah-nh)//2; bg.paste(resized,(x,y),resized)
    card.paste(bg,(area[0],area[1])); return card


def mesh_card(entry,size=(420,330)):
    w,h=size; card=Image.new("RGB",size,(14,19,17)); d=ImageDraw.Draw(card)
    d.rectangle((0,0,w,48),fill=(10,14,13)); d.text((12,8),str(entry["asset_id"]),font=font(16,True),fill=(229,220,194)); d.text((86,8),str(entry["variant"]).replace("_"," ").upper(),font=font(13),fill=(213,155,69))
    rendered=render_obj(ROOT/entry["path"],(w,h-48)); card.paste(rendered,(0,48)); return card


def make_sheet(entries,title,subtitle,kind,cols=4,card_size=None):
    if card_size is None: card_size=(360,300) if kind=="sprite" else (420,330)
    cards=[sprite_card(e,card_size) if kind=="sprite" else mesh_card(e,card_size) for e in entries]
    rows=math.ceil(len(cards)/cols); cw,ch=card_size; head=76
    sheet=Image.new("RGB",(cw*cols,ch*rows+head),(11,15,13)); d=ImageDraw.Draw(sheet)
    d.text((18,13),title,font=font(24,True),fill=(235,227,203)); d.text((18,45),subtitle,font=font(14),fill=(145,164,146))
    for i,card in enumerate(cards): sheet.paste(card,((i%cols)*cw,head+(i//cols)*ch))
    return sheet


def main()->int:
    if not MANIFEST.exists(): raise SystemExit(f"Missing atlas expansion manifest: {MANIFEST}")
    data=json.loads(MANIFEST.read_text(encoding="utf-8")); entries=data.get("entries",[]); OUT.mkdir(parents=True,exist_ok=True)
    bycat=defaultdict(list)
    for e in entries: bycat[e["category"]].append(e)

    # Cinematic/world-reference sheets.
    backgrounds=bycat["Key art & backgrounds"]
    make_sheet(backgrounds,"PROJECT ØEN — ATLAS EXPANSION / KEY ART","Actual generated island/camp/shoreline backgrounds", "sprite",3,(520,300)).save(OUT/"atlas_expansion_keyart.png",compress_level=6)

    docs=bycat["Maps & documents"]
    make_sheet(docs,"PROJECT ØEN — ATLAS EXPANSION / MAPS + DOCUMENTS","Physical planning/reference art missing from the original 148-ID master", "sprite",4,(340,360)).save(OUT/"atlas_expansion_maps_documents.png",compress_level=6)

    living=bycat["Animals & wildlife"]+bycat["Food & cooking"]+bycat["Weather & atmosphere"]
    make_sheet(living,"PROJECT ØEN — ATLAS EXPANSION / WORLD BILLBOARDS","Wildlife, food/cooking and atmosphere families from the approved atlas", "sprite",5,(300,270)).save(OUT/"atlas_expansion_world_billboards.png",compress_level=6)

    meshes=bycat["Tools & crafting"]+bycat["Radio & communication"]
    make_sheet(meshes,"PROJECT ØEN — ATLAS EXPANSION / TOOLS + COMMUNICATION","Texture-aware previews of actual new Unity-importable OBJ states", "mesh",4,(390,310)).save(OUT/"atlas_expansion_meshes.png",compress_level=6)

    # Compact overview with first variant of every family.
    first={}
    for e in entries: first.setdefault(e["asset_id"],e)
    chosen=list(first.values()); sprite_first=[e for e in chosen if e["kind"]=="sprite"]; mesh_first=[e for e in chosen if e["kind"]=="mesh"]
    s1=make_sheet(sprite_first,"ATLAS EXPANSION — 22 NEW 2D FAMILIES","One actual generated representative per added sprite family", "sprite",5,(270,245))
    s2=make_sheet(mesh_first,"ATLAS EXPANSION — 12 NEW 3D FAMILIES","One actual generated representative per added mesh family", "mesh",4,(330,270))
    gap=16; overview=Image.new("RGB",(max(s1.width,s2.width),s1.height+s2.height+gap),(9,13,11)); overview.paste(s1,(0,0)); overview.paste(s2,(0,s1.height+gap)); overview.save(OUT/"atlas_expansion_overview.png",compress_level=6)

    print(f"Rendered atlas-expansion visual QA: {len(entries)} outputs / {len(first)} families / 5 review sheets")
    return 0


if __name__=="__main__": raise SystemExit(main())
