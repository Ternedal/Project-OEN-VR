#!/usr/bin/env python3
"""Render texture-aware scene-level Project ØEN art-direction review compositions.

The scene gate combines actual canonical generated OBJ files into representative
Stormnatten arrangements. It now preserves OBJ UVs and samples the actual shipping
production albedo maps, so the review reflects the material package rather than a
flat debug palette while still remaining a deterministic CI preview (not a fake
Unity beauty shot).
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from PIL import Image, ImageDraw

from render_mockup_review import (
    THIN_MATERIALS, SOFT_SHADE, normal, tint,
    parse_obj_textured, face_material_color,
)

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PROD=ROOT/"Assets"/"ProductionArt"
MANIFEST=PROD/"Docs"/"production_art_manifest.json"
OUT=HERE/"review_renders"

# title, objects. object=(asset_id, variant-or-None, xyz, scale, local_yaw)
# Repeated canonical vegetation/set-dressing instances are deliberate: the original
# gameplay mockups read as an island world, not isolated catalogue assets.
SCENES=[
    ("CAMP / SHELTER + FIRE / DENSE JUNGLE EDGE",[
        ("CS-003",None,(-.55,0,.72),1.00,0),
        ("CS-009",None,(.48,0,-.34),.80,0),
        ("EN-017","pot",(1.28,0,.28),.68,-14),
        ("EN-018","sack",(1.58,0,.70),.58,18),
        ("EN-007","mature",(-2.05,0,1.30),.50,10),
        ("EN-009","dense",(-1.55,0,.96),.82,15),
        ("EN-009","medium",(1.92,0,1.22),.72,-18),
        ("EN-009","medium",(-1.72,0,-.48),.62,24),
        ("EN-008","medium",(.90,0,-.82),.72,31),
        ("EN-008","small",(-.96,0,-.70),.68,-18),
        ("EN-005","medium",(-.08,0,-.90),.72,8),
        ("EN-006","small",(1.58,0,-.72),.62,-24),
    ]),
    ("STORM AFTERMATH / DAMAGED CAMP + DEBRIS",[
        ("CS-004",None,(-.20,0,.56),1.00,-5),
        ("CS-010",None,(.58,0,-.30),.78,0),
        ("PR-001","wet",(1.44,.02,.78),.46,8),
        ("EN-007","broken",(-1.78,0,1.35),.54,-10),
        ("EN-009","dense",(-1.52,0,.72),.78,21),
        ("EN-009","medium",(1.90,0,1.12),.70,-14),
        ("EN-010","dense",(-1.10,.08,1.54),.72,0),
        ("EN-008","medium",(.94,0,-.76),.72,17),
        ("EN-002","medium",(1.58,0,-.52),.70,-27),
        ("EN-005","large",(-.92,0,-.66),.72,12),
        ("EN-006","medium",(-1.62,0,-.46),.62,32),
    ]),
    ("BEACH / OPEN WRECK + TROPICAL WALL",[
        ("EN-001","large",(-.05,0,.12),1.00,-3),
        ("EN-007","mature",(-2.16,0,1.28),.55,8),
        ("EN-007","young",(2.00,0,1.48),.52,-9),
        ("EN-009","dense",(-1.62,0,1.10),.84,8),
        ("EN-009","dense",(1.52,0,1.18),.82,-12),
        ("EN-009","medium",(.46,0,1.62),.72,26),
        ("EN-008","medium",(-1.10,0,-.70),.72,-25),
        ("EN-008","medium",(1.15,0,-.62),.70,24),
        ("EN-006","medium",(1.52,0,-.66),.76,20),
        ("EN-002","medium",(-1.52,0,-.56),.68,-24),
        ("EN-005","large",(.10,0,-.92),.74,7),
    ]),
    ("SIGNAL HILL / BEACON + CLIFF VEGETATION",[
        ("CS-014",None,(0,0,.38),1.00,0),
        ("EN-019","logs",(-1.08,0,-.46),.70,12),
        ("EN-019","ropes",(.98,0,-.36),.70,-9),
        ("EN-019","stones",(.25,0,-.72),.68,14),
        ("EN-007","young",(-1.86,0,1.72),.43,5),
        ("EN-012","ledge",(1.68,0,1.48),.52,-9),
        ("EN-013","dense",(-1.28,0,-.62),.82,12),
        ("EN-013","dense",(1.32,0,-.68),.76,-18),
        ("EN-009","medium",(-1.54,0,.92),.64,18),
        ("EN-009","medium",(1.48,0,.98),.62,-15),
        ("EN-005","medium",(-.76,0,-.78),.64,5),
    ]),
]


def pick(manifest,aid,variant):
    rows=[e for e in manifest if e.get("kind")=="mesh" and str(e.get("asset_id"))==aid]
    if variant is not None:
        wanted=variant.replace("-","_").replace(" ","_")
        exact=[e for e in rows if str(e.get("variant","default")).replace("-","_").replace(" ","_")==wanted]
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
    verts=[]; uvs=[]; faces=[]
    for aid,var,pos,scale,yaw in objects:
        ov,ou,of=parse_obj_textured(pick(manifest,aid,var))
        vo=len(verts); uo=len(uvs)
        verts.extend(local_transform(p,pos,scale,yaw) for p in ov)
        uvs.extend(ou)
        for vids,tids,mat in of:
            faces.append((tuple(i+vo for i in vids),tuple(None if i is None else i+uo for i in tids),mat))
    return verts,uvs,faces


def render_scene(manifest,title,objects,size=(760,490)):
    ss=3; w,h=size; rw,rh=w*ss,h*ss
    verts,uvs,faces=load_scene(manifest,objects); rv=[camera_transform(p) for p in verts]
    xs=[p[0] for p in rv]; ys=[p[1] for p in rv]
    minx,maxx,miny,maxy=min(xs),max(xs),min(ys),max(ys); sx=max(maxx-minx,.01); sy=max(maxy-miny,.01)
    scale=min((rw-82*ss)/sx,(rh-92*ss)/sy); cx=(minx+maxx)/2; floor_y=rh-48*ss
    def sp(p): return (rw/2+(p[0]-cx)*scale,floor_y-(p[1]-miny)*scale)

    im=Image.new("RGB",(rw,rh),(17,25,23)); d=ImageDraw.Draw(im)
    # Cool wet Stormnatten context. No decorative fake asset silhouettes are added:
    # all foreground forms below remain actual canonical OBJ geometry.
    horizon=int(rh*.69)
    d.rectangle((0,0,rw,int(rh*.38)),fill=(18,29,30))
    d.rectangle((0,int(rh*.38),rw,horizon),fill=(22,35,32))
    d.rectangle((0,horizon,rw,rh),fill=(45,45,34))
    d.line((0,horizon,rw,horizon),fill=(49,60,50),width=ss)
    d.ellipse((rw*.06,floor_y-10*ss,rw*.94,floor_y+19*ss),fill=(13,19,16))

    light=(.32,.86,-.40); packets=[]
    for vids,tids,mat in faces:
        a,b,c=(rv[i] for i in vids); n=normal(a,b,c)
        if mat not in THIN_MATERIALS and n[2]>.015: continue
        lam=max(0.0,min(1.0,n[0]*light[0]+n[1]*light[1]+n[2]*light[2]))
        shade=(.84+.11*lam) if mat in SOFT_SHADE else (.59+.39*lam)
        if mat=="Fire": shade=1.00+.08*lam
        uvtri=tuple(uvs[i] if i is not None and 0<=i<len(uvs) else None for i in tids)
        base=face_material_color(mat,uvtri,tuple(verts[i] for i in vids))
        depth=(a[2]+b[2]+c[2])/3
        packets.append((depth,(sp(a),sp(b),sp(c)),tint(base,shade)))
    for _,poly,col in sorted(packets,key=lambda q:q[0],reverse=True): d.polygon(poly,fill=col)

    d.rectangle((0,0,rw,42*ss),fill=(11,16,14))
    d.text((14*ss,13*ss),title,fill=(229,222,201))
    d.text((rw-285*ss,13*ss),"CANONICAL OBJ + SHIPPING ALBEDO / UV REVIEW",fill=(139,157,136))
    return im.resize(size,Image.Resampling.LANCZOS)


def main()->int:
    OUT.mkdir(parents=True,exist_ok=True)
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8")); cards=[]
    for idx,(title,objects) in enumerate(SCENES,1):
        img=render_scene(manifest,title,objects); cards.append(img)
        img.save(OUT/f"mockup_scene_{idx:02d}.png",compress_level=6)
    cw,ch=cards[0].size; sheet=Image.new("RGB",(cw*2,ch*2+66),(11,15,13)); d=ImageDraw.Draw(sheet)
    d.text((18,16),"PROJECT ØEN — TEXTURE-AWARE DENSE SCENE FIDELITY REVIEW",fill=(232,225,203))
    d.text((18,40),"Actual shipping geometry + production albedo UV sampling at gameplay scale.",fill=(148,163,146))
    for i,img in enumerate(cards): sheet.paste(img,((i%2)*cw,66+(i//2)*ch))
    sheet.save(OUT/"mockup_scene_contact_sheet.png",compress_level=6)
    print(f"Rendered {len(cards)} texture-aware dense scene compositions from canonical OBJ/material assets")
    return 0

if __name__=="__main__": raise SystemExit(main())
