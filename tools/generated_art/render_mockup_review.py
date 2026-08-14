#!/usr/bin/env python3
"""Render deterministic review thumbnails from canonical Project ØEN OBJ assets.

This is an art-direction gate, not a geometry validator. It produces one contact
sheet from the actual generated OBJ files so reviewers can compare the production
assets with the approved gameplay/asset mockups instead of relying on vertex counts.
No Blender/OpenGL dependency is required; Pillow is already present in the art CI.
"""
from __future__ import annotations

import json, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PROD=ROOT/"Assets"/"ProjectOEN"/"ProductionArt"
MANIFEST=PROD/"Docs"/"production_art_manifest.json"
OUT=HERE/"review_renders"

PALETTE={
 "Wood":(116,83,53), "Rope":(151,132,94), "Tarp":(40,72,83),
 "Metal":(91,98,96), "Stone":(76,79,75), "Leaf":(43,72,43),
 "Cloth":(101,87,68), "Mud":(62,61,48), "Fire":(239,126,40),
 "Char":(39,40,36), "Water":(49,79,91),
}
TARGETS=[
 ("PR-001","wet","WET TARP / PRESENNING"),
 ("PR-005","active","ACTIVE PORTABLE RADIO"),
 ("CS-004",None,"STORM-DAMAGED SHELTER"),
 ("CS-009",None,"STRONG CAMPFIRE"),
 ("CS-014",None,"ACTIVE SIGNAL BEACON"),
 ("EN-001","large","SHIPWRECK ANCHOR"),
 ("EN-007","mature","MATURE PALM"),
 ("EN-017","pot","COOKING CORNER"),
]


def parse_obj(path:Path):
    verts=[]; faces=[]; mat="Wood"
    for raw in path.read_text(encoding="utf-8").splitlines():
        s=raw.strip()
        if s.startswith("v "):
            p=s.split(); verts.append((float(p[1]),float(p[2]),float(p[3])))
        elif s.startswith("usemtl "):
            mat=s.split(None,1)[1]
        elif s.startswith("f "):
            ids=[int(tok.split('/')[0])-1 for tok in s.split()[1:]]
            if len(ids)>=3:
                for i in range(1,len(ids)-1): faces.append((ids[0],ids[i],ids[i+1],mat))
    return verts,faces


def rotate(p,yaw=-35,pitch=18):
    x,y,z=p; a=math.radians(yaw); ca,sa=math.cos(a),math.sin(a)
    x,z=x*ca+z*sa,-x*sa+z*ca
    b=math.radians(pitch); cb,sb=math.cos(b),math.sin(b)
    y,z=y*cb-z*sb,y*sb+z*cb
    return x,y,z


def normal(a,b,c):
    ux,uy,uz=b[0]-a[0],b[1]-a[1],b[2]-a[2]; vx,vy,vz=c[0]-a[0],c[1]-a[1],c[2]-a[2]
    n=(uy*vz-uz*vy,uz*vx-ux*vz,ux*vy-uy*vx); ln=math.sqrt(sum(v*v for v in n)) or 1
    return tuple(v/ln for v in n)


def tint(rgb,k): return tuple(max(0,min(255,int(c*k))) for c in rgb)


def render_obj(path:Path,size=(620,430)):
    w,h=size; verts,faces=parse_obj(path); rv=[rotate(v) for v in verts]
    xs=[p[0] for p in rv]; ys=[p[1] for p in rv]
    if not xs: return Image.new("RGB",size,(24,28,26))
    minx,maxx,miny,maxy=min(xs),max(xs),min(ys),max(ys); spanx=max(maxx-minx,.01); spany=max(maxy-miny,.01)
    scale=min((w-90)/spanx,(h-80)/spany); cx=(minx+maxx)/2; cy=(miny+maxy)/2
    def sp(p): return (w/2+(p[0]-cx)*scale,h/2-(p[1]-cy)*scale+8)
    im=Image.new("RGB",size,(22,27,25)); d=ImageDraw.Draw(im)
    # soft ground plane / horizon anchors scale without pretending to be a game screenshot
    d.rectangle((0,int(h*.76),w,h),fill=(31,35,31)); d.line((0,int(h*.76),w,int(h*.76)),fill=(66,67,58),width=1)
    light=(.28,.82,-.49)
    packets=[]
    for ia,ib,ic,mat in faces:
        a,b,c=rv[ia],rv[ib],rv[ic]; n=normal(a,b,c); lam=max(-.25,min(1,n[0]*light[0]+n[1]*light[1]+n[2]*light[2])); shade=.68+.30*abs(lam)
        depth=(a[2]+b[2]+c[2])/3; packets.append((depth,(sp(a),sp(b),sp(c)),tint(PALETTE.get(mat,(125,120,110)),shade)))
    for _,poly,col in sorted(packets,key=lambda q:q[0],reverse=True):
        d.polygon(poly,fill=col,outline=tint(col,.62))
    return im


def pick(manifest,aid,variant):
    rows=[e for e in manifest if e.get("kind")=="mesh" and str(e.get("asset_id"))==aid]
    if variant is not None:
        exact=[e for e in rows if str(e.get("variant","default"))==variant]
        if exact: rows=exact
    if not rows: raise KeyError(f"No manifest mesh for {aid}/{variant}")
    return ROOT/rows[0]["path"]


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8")); cards=[]
    for aid,var,label in TARGETS:
        path=pick(manifest,aid,var); img=render_obj(path)
        d=ImageDraw.Draw(img); d.rectangle((0,0,img.width,38),fill=(15,18,17)); d.text((14,11),label,fill=(226,220,199))
        d.text((img.width-92,11),aid,fill=(151,165,137)); cards.append(img)
        img.save(OUT/f"{aid.lower()}_{(var or 'state').replace(' ','_')}.png",compress_level=6)
    cols=2; rows=math.ceil(len(cards)/cols); cw,ch=cards[0].size
    sheet=Image.new("RGB",(cw*cols,ch*rows+68),(12,15,14)); sd=ImageDraw.Draw(sheet)
    sd.text((18,18),"PROJECT ØEN — MOCKUP FIDELITY REVIEW / ACTUAL GENERATED OBJ",fill=(231,225,204))
    sd.text((18,42),"Compare silhouette, material breakup, weathering story and hand-built character against approved mockups.",fill=(153,164,148))
    for i,img in enumerate(cards): sheet.paste(img,((i%cols)*cw,68+(i//cols)*ch))
    sheet.save(OUT/"mockup_fidelity_contact_sheet.png",compress_level=6)
    print(f"Rendered {len(cards)} actual production OBJ review cards -> {OUT.relative_to(ROOT)}")
    return 0

if __name__=="__main__": raise SystemExit(main())
