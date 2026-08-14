#!/usr/bin/env python3
"""Render scene-level Project ØEN art-direction review compositions.

Asset-by-asset review is necessary but not sufficient: the approved gameplay mockups
are compositions. This renderer combines the *actual canonical generated OBJ files*
into four representative arrangements so silhouette, relative scale and visual language
can be compared at a glance:

1. camp / usable shelter + strong fire + cooking corner;
2. storm aftermath / damaged shelter + low wet fire;
3. beach / open shipwreck + tropical palms;
4. signal hill / active lattice beacon + camp dressing.

It is intentionally dependency-light and deterministic. It does not pretend to be a
Unity beauty render; it is a CI art-direction gate built from the shipping geometry.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from PIL import Image, ImageDraw

from render_mockup_review import PALETTE, THIN_MATERIALS, SOFT_SHADE, normal, tint

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PROD=ROOT/"Assets"/"ProjectOEN"/"ProductionArt"
MANIFEST=PROD/"Docs"/"production_art_manifest.json"
OUT=HERE/"review_renders"

# title, objects. object=(asset_id, variant-or-None, xyz, scale, local_yaw)
SCENES=[
    ("CAMP / USABLE SHELTER + FIRE",[
        ("CS-003",None,(-.55,0,.70),1.00,0),
        ("CS-009",None,(.48,0,-.28),.92,0),
        ("EN-017","pot",(1.28,0,.38),.70,-14),
        ("EN-007","mature",(-1.92,0,1.25),.48,10),
    ]),
    ("STORM AFTERMATH / DAMAGED CAMP",[
        ("CS-004",None,(-.20,0,.55),1.00,-5),
        ("CS-010",None,(.58,0,-.28),.88,0),
        ("PR-001","wet",(1.40,.02,.75),.48,8),
        ("EN-007","broken",(-1.72,0,1.38),.52,-10),
    ]),
    ("BEACH / WRECK + TROPICAL EDGE",[
        ("EN-001","large",(-.05,0,.10),1.00,-3),
        ("EN-007","mature",(-2.10,0,1.25),.55,8),
        ("EN-007","young",(1.90,0,1.48),.52,-9),
        ("EN-006","medium",(1.25,0,-.56),.78,20),
    ]),
    ("SIGNAL HILL / ACTIVE BEACON",[
        ("CS-014",None,(0,0,.38),1.00,0),
        ("EN-019","logs",(-1.05,0,-.42),.72,12),
        ("EN-019","ropes",(.95,0,-.34),.72,-9),
        ("EN-007","young",(-1.75,0,1.70),.42,5),
    ]),
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


def pick(manifest,aid,variant):
    rows=[e for e in manifest if e.get("kind")=="mesh" and str(e.get("asset_id"))==aid]
    if variant is not None:
        exact=[e for e in rows if str(e.get("variant","default")).replace("-","_")==variant.replace("-","_")]
        if exact: rows=exact
    if not rows: raise KeyError(f"No manifest mesh for {aid}/{variant}")
    return ROOT/rows[0]["path"]


def local_transform(p,pos,scale,yaw):
    x,y,z=(v*scale for v in p); a=math.radians(yaw); ca,sa=math.cos(a),math.sin(a)
    x,z=x*ca+z*sa,-x*sa+z*ca
    return (x+pos[0],y+pos[1],z+pos[2])


def camera_transform(p,yaw=-33,pitch=17):
    x,y,z=p; a=math.radians(yaw); ca,sa=math.cos(a),math.sin(a)
    x,z=x*ca+z*sa,-x*sa+z*ca
    b=math.radians(pitch); cb,sb=math.cos(b),math.sin(b)
    y,z=y*cb-z*sb,y*sb+z*cb
    return x,y,z


def load_scene(manifest,objects):
    verts=[]; faces=[]
    for aid,var,pos,scale,yaw in objects:
        ov,of=parse_obj(pick(manifest,aid,var)); offset=len(verts)
        verts.extend(local_transform(p,pos,scale,yaw) for p in ov)
        faces.extend((a+offset,b+offset,c+offset,mat) for a,b,c,mat in of)
    return verts,faces


def render_scene(manifest,title,objects,size=(760,490)):
    ss=2; w,h=size; rw,rh=w*ss,h*ss
    verts,faces=load_scene(manifest,objects); rv=[camera_transform(p) for p in verts]
    xs=[p[0] for p in rv]; ys=[p[1] for p in rv]
    minx,maxx,miny,maxy=min(xs),max(xs),min(ys),max(ys); sx=max(maxx-minx,.01); sy=max(maxy-miny,.01)
    scale=min((rw-100*ss)/sx,(rh-95*ss)/sy); cx=(minx+maxx)/2; floor_y=rh-52*ss
    def sp(p): return (rw/2+(p[0]-cx)*scale,floor_y-(p[1]-miny)*scale)

    im=Image.new("RGB",(rw,rh),(20,27,25)); d=ImageDraw.Draw(im)
    # Deliberately restrained world context: storm-green sky, dark wet ground, no fake scenery.
    horizon=int(rh*.70)
    d.rectangle((0,0,rw,horizon),fill=(24,34,32))
    d.rectangle((0,horizon,rw,rh),fill=(34,39,32))
    d.rectangle((0,int(rh*.53),rw,horizon),fill=(28,37,34))
    d.ellipse((rw*.13,floor_y-9*ss,rw*.87,floor_y+18*ss),fill=(22,27,23))

    light=(.32,.86,-.40); packets=[]
    for ia,ib,ic,mat in faces:
        a,b,c=rv[ia],rv[ib],rv[ic]; n=normal(a,b,c)
        if mat not in THIN_MATERIALS and n[2]>.015: continue
        lam=max(0.0,min(1.0,n[0]*light[0]+n[1]*light[1]+n[2]*light[2]))
        shade=(.80+.10*lam) if mat in SOFT_SHADE else (.57+.40*lam)
        if mat=="Fire": shade=1.00+.08*lam
        depth=(a[2]+b[2]+c[2])/3
        packets.append((depth,(sp(a),sp(b),sp(c)),tint(PALETTE.get(mat,(125,120,110)),shade)))
    for _,poly,col in sorted(packets,key=lambda q:q[0],reverse=True): d.polygon(poly,fill=col)

    d.rectangle((0,0,rw,42*ss),fill=(13,18,16))
    d.text((14*ss,13*ss),title,fill=(229,222,201),stroke_width=0)
    d.text((rw-250*ss,13*ss),"ACTUAL CANONICAL OBJ COMPOSITION",fill=(139,157,136))
    return im.resize(size,Image.Resampling.LANCZOS)


def main()->int:
    OUT.mkdir(parents=True,exist_ok=True)
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8")); cards=[]
    for idx,(title,objects) in enumerate(SCENES,1):
        img=render_scene(manifest,title,objects); cards.append(img)
        img.save(OUT/f"mockup_scene_{idx:02d}.png",compress_level=6)
    cw,ch=cards[0].size; sheet=Image.new("RGB",(cw*2,ch*2+66),(11,15,13)); d=ImageDraw.Draw(sheet)
    d.text((18,16),"PROJECT ØEN — SCENE-LEVEL MOCKUP FIDELITY REVIEW",fill=(232,225,203))
    d.text((18,40),"Shipping geometry composed at gameplay scale; use with original gameplay mockup board for visual sign-off.",fill=(148,163,146))
    for i,img in enumerate(cards): sheet.paste(img,((i%2)*cw,66+(i//2)*ch))
    sheet.save(OUT/"mockup_scene_contact_sheet.png",compress_level=6)
    print(f"Rendered {len(cards)} scene-level fidelity compositions from actual canonical OBJ assets")
    return 0

if __name__=="__main__": raise SystemExit(main())
