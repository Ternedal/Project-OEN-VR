#!/usr/bin/env python3
"""Render deterministic texture-aware art-direction thumbnails from Project ØEN OBJ assets.

This is still a lightweight CI review renderer, not a fake Unity screenshot. Unlike the
older flat-palette preview it now reads each OBJ's real UV coordinates and samples the
actual shipping production albedo maps. That makes foliage, wet tarp, wood, rope, stone,
metal and char materially representative enough to compare against the approved atlas.

Normals/smoothness remain Unity-side concerns; the preview deliberately keeps simple
lighting and supersampling so it cannot hide silhouette or construction problems.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageStat

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PROD=ROOT/"Assets"/"ProjectOEN"/"ProductionArt"
MANIFEST=PROD/"Docs"/"production_art_manifest.json"
TEX=PROD/"Materials"/"Textures"
OUT=HERE/"review_renders"

PALETTE={
 "Wood":(122,90,58), "Rope":(151,132,94), "Tarp":(49,76,82),
 "Metal":(96,102,101), "Stone":(78,78,76), "Leaf":(48,82,43),
 "Cloth":(112,94,73), "Mud":(87,78,60), "Fire":(255,158,58),
 "Char":(43,43,40), "Water":(46,77,92),
}
THIN_MATERIALS={"Tarp","Cloth","Leaf","Fire","Water"}
SOFT_SHADE={"Tarp","Cloth","Leaf","Fire","Water"}
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

_TEXTURES={}
_TEXTURE_MEANS={}


def _texture_for(mat:str):
    if mat in _TEXTURES: return _TEXTURES[mat]
    path=TEX/f"{mat.lower()}_albedo.png"
    if path.exists():
        im=Image.open(path).convert("RGB")
        _TEXTURES[mat]=im
        _TEXTURE_MEANS[mat]=tuple(int(v) for v in ImageStat.Stat(im).mean[:3])
    else:
        _TEXTURES[mat]=None; _TEXTURE_MEANS[mat]=PALETTE.get(mat,(125,120,110))
    return _TEXTURES[mat]


def material_mean(mat:str):
    _texture_for(mat)
    return _TEXTURE_MEANS.get(mat,PALETTE.get(mat,(125,120,110)))


def parse_obj_textured(path:Path):
    verts=[]; uvs=[]; faces=[]; mat="Wood"
    for raw in path.read_text(encoding="utf-8").splitlines():
        s=raw.strip()
        if s.startswith("v "):
            p=s.split(); verts.append((float(p[1]),float(p[2]),float(p[3])))
        elif s.startswith("vt "):
            p=s.split(); uvs.append((float(p[1]),float(p[2])))
        elif s.startswith("usemtl "):
            mat=s.split(None,1)[1]
        elif s.startswith("f "):
            tokens=s.split()[1:]; vids=[]; tids=[]
            for tok in tokens:
                parts=tok.split('/')
                vids.append(int(parts[0])-1)
                tids.append(int(parts[1])-1 if len(parts)>1 and parts[1] else None)
            if len(vids)>=3:
                for i in range(1,len(vids)-1):
                    faces.append(((vids[0],vids[i],vids[i+1]),(tids[0],tids[i],tids[i+1]),mat))
    return verts,uvs,faces


def parse_obj(path:Path):
    """Backward-compatible geometry-only parser used by older helper imports."""
    verts,_,tf=parse_obj_textured(path)
    return verts,[(v[0],v[1],v[2],mat) for v,_,mat in tf]


def rotate(p,yaw=-35,pitch=16):
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


def blend(a,b,t):
    return tuple(int(a[i]*(1-t)+b[i]*t) for i in range(3))


def face_material_color(mat:str, uv_triplet, pos_triplet=None):
    """Sample the shipping albedo at a triangle centroid, softened by its material mean.

    Most generated OBJ quads carry canonical 0..1 UVs. When a legacy triangle has no
    useful UV, use a stable world-position projection solely for the review preview;
    the actual OBJ/material files are never changed by this renderer.
    """
    tex=_texture_for(mat)
    mean=material_mean(mat)
    if tex is None: return mean
    valid=[uv for uv in uv_triplet if uv is not None]
    if valid:
        u=sum(v[0] for v in valid)/len(valid); v=sum(v[1] for v in valid)/len(valid)
        spread=max((abs(valid[i][0]-valid[0][0])+abs(valid[i][1]-valid[0][1]) for i in range(1,len(valid))),default=0)
        if spread<1e-5 and pos_triplet:
            cx=sum(p[0] for p in pos_triplet)/3; cy=sum(p[1] for p in pos_triplet)/3; cz=sum(p[2] for p in pos_triplet)/3
            u=(u+cx*.37+cz*.19)%1.0; v=(v+cy*.31+cz*.23)%1.0
    elif pos_triplet:
        cx=sum(p[0] for p in pos_triplet)/3; cy=sum(p[1] for p in pos_triplet)/3; cz=sum(p[2] for p in pos_triplet)/3
        u=(cx*.37+cz*.19)%1.0; v=(cy*.31+cz*.23)%1.0
    else:
        return mean
    u%=1.0; v%=1.0; w,h=tex.size
    px=max(0,min(w-1,int(u*(w-1)))); py=max(0,min(h-1,int((1-v)*(h-1))))
    sample=tex.getpixel((px,py))
    # One-pixel UV-centroid sampling can exaggerate a texture speckle. Blending with
    # the full-map mean keeps this a material preview rather than a noisy checkerboard.
    strength=.58 if mat in SOFT_SHADE else .68
    return blend(mean,sample,strength)


def render_obj(path:Path,size=(620,430)):
    ss=3; w,h=size; rw,rh=w*ss,h*ss
    verts,uvs,faces=parse_obj_textured(path); rv=[rotate(v) for v in verts]
    xs=[p[0] for p in rv]; ys=[p[1] for p in rv]
    if not xs: return Image.new("RGB",size,(24,28,26))
    minx,maxx,miny,maxy=min(xs),max(xs),min(ys),max(ys)
    spanx=max(maxx-minx,.01); spany=max(maxy-miny,.01)
    scale=min((rw-100*ss)/spanx,(rh-90*ss)/spany); cx=(minx+maxx)/2
    floor_y=rh-48*ss
    def sp(p): return (rw/2+(p[0]-cx)*scale,floor_y-(p[1]-miny)*scale)

    im=Image.new("RGB",(rw,rh),(18,25,22)); d=ImageDraw.Draw(im)
    # Cool storm backdrop with a muted wet-earth floor; no beauty-shot scenery is invented.
    ground_y=floor_y+5*ss
    d.rectangle((0,0,rw,ground_y),fill=(20,31,29))
    d.rectangle((0,int(ground_y*.60),rw,ground_y),fill=(23,34,31))
    d.rectangle((0,ground_y,rw,rh),fill=(42,43,34))
    d.line((0,ground_y,rw,ground_y),fill=(67,70,57),width=ss)
    shadow_w=min(rw*.70,spanx*scale*.72); shadow_x=rw/2
    d.ellipse((shadow_x-shadow_w/2,ground_y-7*ss,shadow_x+shadow_w/2,ground_y+10*ss),fill=(14,19,16))

    light=(.34,.86,-.38); packets=[]
    for vids,tids,mat in faces:
        a,b,c=(rv[i] for i in vids); n=normal(a,b,c)
        if mat not in THIN_MATERIALS and n[2]>.015: continue
        lam=max(0.0,min(1.0,n[0]*light[0]+n[1]*light[1]+n[2]*light[2]))
        shade=(.84+.11*lam) if mat in SOFT_SHADE else (.60+.38*lam)
        if mat=="Fire": shade=1.00+.08*lam
        uvtri=tuple(uvs[i] if i is not None and 0<=i<len(uvs) else None for i in tids)
        base=face_material_color(mat,uvtri,tuple(verts[i] for i in vids))
        depth=(a[2]+b[2]+c[2])/3
        packets.append((depth,(sp(a),sp(b),sp(c)),tint(base,shade)))
    for _,poly,col in sorted(packets,key=lambda q:q[0],reverse=True): d.polygon(poly,fill=col)
    return im.resize(size,Image.Resampling.LANCZOS)


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
        d=ImageDraw.Draw(img); d.rectangle((0,0,img.width,38),fill=(13,18,16)); d.text((14,11),label,fill=(226,220,199))
        d.text((img.width-92,11),aid,fill=(151,165,137)); cards.append(img)
        img.save(OUT/f"{aid.lower()}_{(var or 'state').replace(' ','_')}.png",compress_level=6)
    cols=2; rows=math.ceil(len(cards)/cols); cw,ch=cards[0].size
    sheet=Image.new("RGB",(cw*cols,ch*rows+68),(12,15,14)); sd=ImageDraw.Draw(sheet)
    sd.text((18,18),"PROJECT ØEN — TEXTURE-AWARE MOCKUP FIDELITY REVIEW",fill=(231,225,204))
    sd.text((18,42),"Actual canonical OBJ silhouette + actual production albedo sampled through OBJ UVs.",fill=(153,164,148))
    for i,img in enumerate(cards): sheet.paste(img,((i%cols)*cw,68+(i//cols)*ch))
    sheet.save(OUT/"mockup_fidelity_contact_sheet.png",compress_level=6)
    print(f"Rendered {len(cards)} texture-aware production OBJ review cards -> {OUT.relative_to(ROOT)}")
    return 0

if __name__=="__main__": raise SystemExit(main())
