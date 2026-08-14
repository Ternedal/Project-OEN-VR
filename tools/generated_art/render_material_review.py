#!/usr/bin/env python3
"""Build a review sheet from the actual Project ØEN production material maps."""
from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
TEX=ROOT/"Assets"/"ProjectOEN"/"ProductionArt"/"Materials"/"Textures"
OUT=HERE/"review_renders"
NAMES=("wood","rope","tarp","metal","stone","leaf","cloth","mud","fire","char","water")


def tile(path:Path,size=(230,230)):
    with Image.open(path) as im:
        return ImageOps.fit(im.convert("RGB"),size,Image.Resampling.LANCZOS)


def main()->int:
    OUT.mkdir(parents=True,exist_ok=True)
    cw,ch=250,278; header=70
    sheet=Image.new("RGB",(cw*3,ch*len(NAMES)+header),(13,17,15)); d=ImageDraw.Draw(sheet)
    d.text((18,18),"PROJECT ØEN — ACTUAL PRODUCTION MATERIAL MAP REVIEW",fill=(232,226,206))
    d.text((18,42),"Albedo / normal / packed metallic-smoothness after weathering + atlas fidelity pass.",fill=(145,160,144))
    for row,name in enumerate(NAMES):
        paths=[TEX/f"{name}_albedo.png",TEX/f"{name}_normal.png",TEX/f"{name}_metallic_smoothness.png"]
        labels=[f"{name.upper()} — ALBEDO","NORMAL","METALLIC / SMOOTHNESS"]
        for col,(path,label) in enumerate(zip(paths,labels)):
            if not path.exists(): raise SystemExit(f"Missing material review input: {path}")
            x=col*cw; y=header+row*ch
            d.rectangle((x,y,x+cw-1,y+ch-1),fill=(20,25,22),outline=(50,58,50))
            im=tile(path); sheet.paste(im,(x+10,y+35)); d.text((x+10,y+11),label,fill=(205,201,183))
    path=OUT/"material_surface_contact_sheet.png"; sheet.save(path,compress_level=6)
    print(f"Rendered {len(NAMES)} production material triplets -> {path.relative_to(ROOT)}")
    return 0

if __name__=="__main__": raise SystemExit(main())
