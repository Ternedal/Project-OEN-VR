#!/usr/bin/env python3
"""Final Stormnatten VFX texture fidelity pass for Project ØEN.

The dedicated VFX generator already guarantees the 14 canonical effect states, but
visual review still read several of them as icons. This pass pushes them toward the
approved atmospheric mockups while keeping the same files, dimensions and Unity
contracts: turbulent smoke, fine ember showers, particulate ash, crown-like rain
splashes, streaky wet sheen, branched lightning and restrained emissive halos/rings.
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
PROD=ROOT/"Assets"/"ProductionArt"
MANIFEST=PROD/"Docs"/"production_art_manifest.json"
REPORT=PROD/"Docs"/"mockup_vfx_v2.json"
SIZE=1024


def rnd(seed:str): return random.Random(int(hashlib.sha256(seed.encode()).hexdigest()[:16],16))

def save(im,path): path.parent.mkdir(parents=True,exist_ok=True); im.convert("RGBA").save(path,compress_level=6)

def rgba_from_alpha(alpha,color):
    im=Image.new("RGBA",alpha.size,color); im.putalpha(alpha); return im

def glow(mask,color,blur=20,strength=.55):
    a=mask.filter(ImageFilter.GaussianBlur(blur)).point(lambda p:int(p*strength)); return rgba_from_alpha(a,color)


def smoke_tile(cell,life,r):
    alpha=Image.new("L",(cell,cell),0); d=ImageDraw.Draw(alpha); cx=cell*.5; base=cell*.64-life*cell*.13
    blobs=22+int(life*8)
    for i in range(blobs):
        layer=(i%4)/3; spread=(.11+.19*life+.06*layer)*cell
        x=cx+r.uniform(-spread,spread); y=base+r.uniform(-.12,.09)*cell-life*cell*.04*layer
        rad=r.uniform(.035,.095)*cell*(.82+.55*life)*(1+.14*layer)
        a=int(r.uniform(85,175)*(1-.28*life)*(1-.08*layer))
        d.ellipse((x-rad*1.15,y-rad,x+rad*1.15,y+rad),fill=a)
    # darker central wisps and a soft torn edge
    alpha=alpha.filter(ImageFilter.GaussianBlur(max(4,int(cell*.025))))
    gutter=Image.new("L",(cell,cell),0); gd=ImageDraw.Draw(gutter); pad=7; gd.rounded_rectangle((pad,pad,cell-pad,cell-pad),24,fill=255)
    return ImageChops.multiply(alpha,gutter)


def smoke(variant,seed):
    atlas=Image.new("RGBA",(SIZE,SIZE),(0,0,0,0)); cell=SIZE//4; r=rnd(seed)
    for frame in range(16):
        life=frame/15; mask=smoke_tile(cell,life,r)
        base=(179-int(life*25),190-int(life*24),190-int(life*19),255)
        cloud=rgba_from_alpha(mask,base); soft=glow(mask,(118,137,141,255),11,.20); tile=Image.alpha_composite(soft,cloud)
        atlas.alpha_composite(tile,((frame%4)*cell,(frame//4)*cell))
    return atlas


def embers(variant,seed):
    im=Image.new("RGBA",(SIZE,SIZE),(0,0,0,0)); r=rnd(seed); mask=Image.new("L",im.size,0); d=ImageDraw.Draw(mask)
    count=22 if variant=="medium" else 13
    cx,cy=SIZE*.50,SIZE*.57
    for i in range(count):
        x=cx+r.uniform(-.16,.16)*SIZE; y=cy+r.uniform(-.18,.13)*SIZE
        ln=r.uniform(22,78)*(1.0 if variant=="medium" else .72); ang=math.radians(r.uniform(-105,-72)); ex=x+math.cos(ang)*ln; ey=y+math.sin(ang)*ln
        width=r.randint(3,8); d.line((x,y,ex,ey),fill=r.randint(150,255),width=width)
        rr=r.uniform(3,8); d.ellipse((ex-rr,ey-rr,ex+rr,ey+rr),fill=255)
    im=Image.alpha_composite(im,glow(mask,(255,73,11,255),20,.72)); core=rgba_from_alpha(mask,(255,190,48,255)); return Image.alpha_composite(im,core)


def ash(seed):
    im=Image.new("RGBA",(SIZE,SIZE),(0,0,0,0)); r=rnd(seed); mask=Image.new("L",im.size,0); d=ImageDraw.Draw(mask); cx,cy=SIZE*.5,SIZE*.52
    for i in range(16):
        x=cx+r.uniform(-.20,.20)*SIZE; y=cy+r.uniform(-.17,.18)*SIZE; rr=r.uniform(5,18)
        pts=[]
        for j in range(7):
            a=2*math.pi*j/7+r.uniform(-.18,.18); rad=rr*r.uniform(.65,1.25); pts.append((x+math.cos(a)*rad,y+math.sin(a)*rad*.62))
        d.polygon(pts,fill=r.randint(105,210))
    mask=mask.filter(ImageFilter.GaussianBlur(1.6)); return rgba_from_alpha(mask,(190,190,178,255))


def splash(variant,seed):
    im=Image.new("RGBA",(SIZE,SIZE),(0,0,0,0)); r=rnd(seed); mask=Image.new("L",im.size,0); d=ImageDraw.Draw(mask); sc=1.0 if variant=="medium" else .72; cx,cy=SIZE*.5,SIZE*.62
    # elliptical crown + rising fingers
    rx,ry=220*sc,70*sc; d.ellipse((cx-rx,cy-ry,cx+rx,cy+ry),outline=170,width=max(7,int(15*sc)))
    for i in range(18):
        a=math.pi*2*i/18+r.uniform(-.10,.10); x=cx+math.cos(a)*rx; y=cy+math.sin(a)*ry
        # upward-biased splash spikes around far half
        rise=r.uniform(28,105)*sc*(1.2 if math.sin(a)<0 else .65); side=r.uniform(-24,24)*sc
        d.line((x,y,x+side,y-rise),fill=r.randint(120,235),width=max(4,int(r.uniform(6,12)*sc)))
        rr=r.uniform(4,10)*sc; d.ellipse((x+side-rr,y-rise-rr,x+side+rr,y-rise+rr),fill=r.randint(145,245))
    # tiny secondary droplets
    for _ in range(16 if variant=="medium" else 9):
        x=cx+r.uniform(-.23,.23)*SIZE*sc; y=cy-r.uniform(.08,.24)*SIZE*sc; rr=r.uniform(2.5,6)*sc; d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=r.randint(115,220))
    soft=glow(mask,(94,175,205,255),10,.28); core=rgba_from_alpha(mask,(166,220,236,255)); return Image.alpha_composite(soft,core)


def wet_sheen(seed):
    im=Image.new("RGBA",(SIZE,SIZE),(0,0,0,0)); r=rnd(seed); mask=Image.new("L",im.size,0); d=ImageDraw.Draw(mask)
    # several long skewed specular ribbons, not a single white blob
    for i in range(12):
        x=r.uniform(.24,.76)*SIZE; y=r.uniform(.25,.75)*SIZE; ln=r.uniform(160,430); ang=math.radians(r.uniform(-55,55)); w=r.uniform(8,24)
        ex=x+math.cos(ang)*ln; ey=y+math.sin(ang)*ln
        d.line((x,y,ex,ey),fill=r.randint(45,125),width=int(w))
        if i%3==0: d.line((x+8,y+3,ex+8,ey+3),fill=r.randint(70,145),width=max(2,int(w*.26)))
    # low, irregular puddle reflections
    for _ in range(5):
        x=r.uniform(.30,.70)*SIZE; y=r.uniform(.38,.70)*SIZE; rx=r.uniform(55,130); ry=r.uniform(16,38); d.ellipse((x-rx,y-ry,x+rx,y+ry),fill=r.randint(24,70))
    mask=mask.filter(ImageFilter.GaussianBlur(8)); vig=Image.new("L",im.size,0); vd=ImageDraw.Draw(vig); vd.ellipse((SIZE*.12,SIZE*.12,SIZE*.88,SIZE*.88),fill=255); vig=vig.filter(ImageFilter.GaussianBlur(45)); mask=ImageChops.multiply(mask,vig)
    return rgba_from_alpha(mask,(210,238,244,255))


def lightning(variant,seed):
    im=Image.new("RGBA",(SIZE,SIZE),(0,0,0,0)); r=rnd(seed); near=variant=="near"; mask=Image.new("L",im.size,0); d=ImageDraw.Draw(mask)
    x=SIZE*(.50 if near else .57); y=SIZE*.08; pts=[(x,y)]; segs=10 if near else 8
    for _ in range(segs):
        x+=r.uniform(-64,64)*(1 if near else .78); y+=r.uniform(58,90); pts.append((x,y))
    width=13 if near else 8; d.line(pts,fill=255,width=width,joint="curve")
    for idx in range(2,len(pts)-2,2):
        sx,sy=pts[idx]; branches=2 if near and idx%4==0 else 1
        for b in range(branches):
            direction=(-1 if (idx+b)%2 else 1); p=[(sx,sy)]; bx,by=sx,sy
            for _ in range(r.randint(2,4)):
                bx+=direction*r.uniform(38,90); by+=r.uniform(38,75); p.append((bx,by))
            d.line(p,fill=r.randint(145,225),width=max(3,width//2),joint="curve")
    im=Image.alpha_composite(im,glow(mask,(63,129,255,255),34 if near else 24,.76)); halo=glow(mask,(155,202,255,255),13,.68); im=Image.alpha_composite(im,halo); core=rgba_from_alpha(mask,(244,250,255,255)); return Image.alpha_composite(im,core)


def radial(size,inner,outer,power=1.8):
    im=Image.new("L",(size,size),0); px=im.load(); c=(size-1)/2
    for y in range(size):
        dy=(y-c)/c
        for x in range(size):
            dx=(x-c)/c; rr=(dx*dx+dy*dy)**.5
            if rr<=inner:a=1
            elif rr>=outer:a=0
            else:a=((outer-rr)/(outer-inner))**power
            px[x,y]=int(a*255)
    return im


def halo(variant):
    color=(255,111,20,255) if variant=="fire" else (255,184,66,255); outer=radial(SIZE,.015,.68,2.25); hole=radial(SIZE,0,.11,1.2); a=ImageChops.subtract(outer,hole.point(lambda p:int(p*.72))).point(lambda p:int(p*.74)); im=rgba_from_alpha(a,color)
    core=radial(SIZE,0,.19,2.5).point(lambda p:int(p*.20)); return Image.alpha_composite(im,rgba_from_alpha(core,(255,232,154,255)))


def pulse(variant):
    im=Image.new("RGBA",(SIZE,SIZE),(0,0,0,0)); mask=Image.new("L",im.size,0); d=ImageDraw.Draw(mask); cx=cy=SIZE//2; large=variant=="medium"; r=320 if large else 215; width=15 if large else 11
    d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=220,width=width); d.ellipse((cx-r*.82,cy-r*.82,cx+r*.82,cy+r*.82),outline=90,width=max(3,width//3))
    for a in (-90,30,150):
        q=math.radians(a); d.line((cx+math.cos(q)*(r-25),cy+math.sin(q)*(r-25),cx+math.cos(q)*(r+42),cy+math.sin(q)*(r+42)),fill=255,width=width)
    im=Image.alpha_composite(im,glow(mask,(20,184,230,255),24,.62)); return Image.alpha_composite(im,rgba_from_alpha(mask,(211,231,219,255)))


def render(aid,variant,seed):
    if aid=="FX-001": return smoke(variant,seed)
    if aid=="FX-002": return embers(variant,seed)
    if aid=="FX-003": return ash(seed)
    if aid=="FX-004": return splash(variant,seed)
    if aid=="FX-005": return wet_sheen(seed)
    if aid=="FX-006": return lightning(variant,seed)
    if aid=="FX-007": return halo(variant)
    if aid=="FX-008": return pulse(variant)
    raise KeyError(aid)


def main():
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8")); entries=[e for e in manifest if e.get("kind")=="sprite" and e.get("category")=="VFX support graphics"]
    if len(entries)!=14: raise SystemExit(f"Expected 14 VFX states, found {len(entries)}")
    report=[]
    for e in entries:
        aid=str(e["asset_id"]); variant=str(e.get("variant","default")); path=ROOT/e["path"]
        im=render(aid,variant,f"Stormnatten.VFX.v2:{aid}:{variant}"); save(im,path)
        report.append({"asset_id":aid,"variant":variant,"path":e["path"],"sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
    REPORT.write_text(json.dumps({"version":2,"count":len(report),"entries":report},indent=2)+"\n",encoding="utf-8")
    print("Stormnatten VFX V2: rebuilt all 14 canonical textures with atmospheric effect silhouettes")
    return 0

if __name__=="__main__": raise SystemExit(main())
