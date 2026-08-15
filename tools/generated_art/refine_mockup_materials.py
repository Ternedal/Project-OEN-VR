#!/usr/bin/env python3
"""Final atlas-aligned surface-art pass for Project ØEN shared materials.

The base material pipeline already supplies 1024px albedo, normal maps, packed
metallic/smoothness and deterministic wetness/weathering. This pass intentionally adds
larger, human-readable material storytelling from the approved mockups/asset atlas:
aged tropical timber, fibrous lashings, patched/wet blue tarp, oxidised field metal,
lichen stone, varied tropical leaf, stained cloth, wet mud, ember/fire colour structure,
char/ash cracking and coastal water ripples.

It never changes paths, dimensions, GUIDs or the shared material vocabulary.
"""
from __future__ import annotations

import hashlib
import math
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
TEX=ROOT/"Assets"/"ProductionArt"/"Materials"/"Textures"
NAMES=("wood","rope","tarp","metal","stone","leaf","cloth","mud","fire","char","water")


def seed(name:str)->int:
    return int(hashlib.sha256(("ProjectOEN.MockupMaterial.v1:"+name).encode()).hexdigest()[:16],16)


def rgba_overlay(base:Image.Image, painter)->Image.Image:
    layer=Image.new("RGBA",base.size,(0,0,0,0)); d=ImageDraw.Draw(layer,"RGBA"); painter(d,base.size)
    return Image.alpha_composite(base.convert("RGBA"),layer).convert("RGB")


def wood(base,name):
    rnd=random.Random(seed(name)); w,h=base.size
    def p(d,size):
        # long fibrous grain + darker splits + sparse moss/damp memory
        for y in range(8,h,18):
            phase=rnd.uniform(0,math.pi*2); pts=[]
            for x in range(-20,w+21,24): pts.append((x,y+math.sin(x*.018+phase)*rnd.uniform(1.2,4.2)))
            d.line(pts,fill=(48,28,16,rnd.randint(24,55)),width=rnd.choice((1,1,2)))
        for _ in range(18):
            x=rnd.randrange(w); y=rnd.randrange(h); ln=rnd.randint(85,290)
            pts=[(x,y),(min(w-1,x+ln*.42),y+rnd.randint(-8,8)),(min(w-1,x+ln),y+rnd.randint(-5,5))]
            d.line(pts,fill=(25,19,15,rnd.randint(35,78)),width=rnd.randint(1,3))
        for _ in range(9):
            x=rnd.randrange(w); y=rnd.randrange(h); rx=rnd.randint(18,50); ry=rnd.randint(6,18)
            d.ellipse((x-rx,y-ry,x+rx,y+ry),outline=(36,23,16,rnd.randint(30,65)),width=3)
        for _ in range(14):
            x=rnd.randrange(w); y=rnd.randrange(h); r=rnd.randint(18,65)
            d.ellipse((x-r,y-r*.55,x+r,y+r*.55),fill=(38,63,44,rnd.randint(5,16)))
    out=rgba_overlay(base,p)
    return ImageEnhance.Color(out).enhance(.91)


def rope(base,name):
    rnd=random.Random(seed(name)); w,h=base.size
    def p(d,size):
        for k in range(-h,w+h,26):
            d.line((k,0,k+h,h),fill=(229,196,133,40),width=4)
            d.line((k+10,0,k+h+10,h),fill=(67,48,31,34),width=2)
        for _ in range(70):
            x=rnd.randrange(w); y=rnd.randrange(h); ln=rnd.randint(18,70)
            d.line((x,y,min(w-1,x+ln),min(h-1,y+ln)),fill=(231,212,164,rnd.randint(9,24)),width=1)
        for _ in range(12):
            x=rnd.randrange(w); y=rnd.randrange(h); r=rnd.randint(20,70)
            d.ellipse((x-r,y-r,x+r,y+r),fill=(58,54,41,rnd.randint(5,14)))
    return rgba_overlay(base,p)


def tarp(base,name):
    rnd=random.Random(seed(name)); w,h=base.size
    def p(d,size):
        # Fine woven grid is subtle; broad fold/seam/stain marks do the visual work.
        for x in range(0,w,16): d.line((x,0,x,h),fill=(165,199,204,10),width=1)
        for y in range(0,h,16): d.line((0,y,w,y),fill=(10,28,34,12),width=1)
        for x in (w//3,2*w//3):
            d.line((x,0,x,h),fill=(204,210,196,35),width=4)
            d.line((x+6,0,x+6,h),fill=(20,43,48,28),width=2)
        for _ in range(18):
            x=rnd.randrange(w); y=rnd.randrange(h); rx=rnd.randint(45,150); ry=rnd.randint(10,38)
            d.arc((x-rx,y-ry,x+rx,y+ry),185,355,fill=(11,31,38,rnd.randint(25,55)),width=rnd.randint(2,5))
        for _ in range(20):
            x=rnd.randrange(w); y=rnd.randrange(h); ln=rnd.randint(70,220)
            d.line((x,y,min(w-1,x+ln),min(h-1,y+rnd.randint(25,85))),fill=(181,208,205,rnd.randint(8,22)),width=2)
        # Two old field patches ghosted into the material, not painted logos.
        for _ in range(5):
            x=rnd.randrange(w); y=rnd.randrange(h); rx=rnd.randint(30,75); ry=rnd.randint(20,55)
            d.rectangle((x-rx,y-ry,x+rx,y+ry),outline=(37,51,48,rnd.randint(14,30)),width=3)
    out=rgba_overlay(base,p)
    return ImageEnhance.Color(out).enhance(.88)


def metal(base,name):
    rnd=random.Random(seed(name)); w,h=base.size
    def p(d,size):
        for _ in range(90):
            x=rnd.randrange(w); y=rnd.randrange(h); ln=rnd.randint(25,170)
            bright=rnd.random()<.45
            col=(205,216,210,rnd.randint(12,38)) if bright else (22,29,28,rnd.randint(14,42))
            d.line((x,y,min(w-1,x+ln),y+rnd.randint(-2,2)),fill=col,width=1)
        for _ in range(45):
            x=rnd.randrange(w); y=rnd.randrange(h); rx=rnd.randint(4,28); ry=rnd.randint(3,20)
            d.ellipse((x-rx,y-ry,x+rx,y+ry),fill=(151,71,35,rnd.randint(18,65)))
        for _ in range(14):
            x=rnd.randrange(w); y=rnd.randrange(h); r=rnd.randint(18,55)
            d.arc((x-r,y-r,x+r,y+r),0,320,fill=(32,42,40,rnd.randint(16,40)),width=3)
    out=rgba_overlay(base,p)
    return ImageEnhance.Color(out).enhance(.82)


def stone(base,name):
    rnd=random.Random(seed(name)); w,h=base.size
    def p(d,size):
        for _ in range(110):
            x=rnd.randrange(w); y=rnd.randrange(h); r=rnd.randint(4,32)
            shade=rnd.choice(((31,37,34),(174,178,166),(76,83,77)))
            d.ellipse((x-r,y-r,x+r,y+r),fill=(*shade,rnd.randint(6,22)))
        for _ in range(26):
            x=rnd.randrange(w); y=rnd.randrange(h); r=rnd.randint(10,55)
            d.ellipse((x-r,y-r*.7,x+r,y+r*.7),fill=(87,116,71,rnd.randint(6,20)))
        for _ in range(20):
            x=rnd.randrange(w); y=rnd.randrange(h)
            d.line((x,y,x+rnd.randint(-80,80),y+rnd.randint(25,120)),fill=(29,33,31,rnd.randint(12,32)),width=1)
    return rgba_overlay(base,p)


def leaf(base,name):
    rnd=random.Random(seed(name)); w,h=base.size
    def p(d,size):
        # midrib / branching veins + mottled tropical colour variation
        d.line((0,h//2,w,h//2),fill=(184,199,111,42),width=5)
        for x in range(0,w,54):
            d.line((x,h//2,min(w-1,x+75),0),fill=(185,198,119,30),width=2)
            d.line((x,h//2,min(w-1,x+75),h),fill=(185,198,119,26),width=2)
        for _ in range(95):
            x=rnd.randrange(w); y=rnd.randrange(h); rx=rnd.randint(10,48); ry=rnd.randint(6,30)
            col=rnd.choice(((26,63,31),(92,119,52),(128,111,48)))
            d.ellipse((x-rx,y-ry,x+rx,y+ry),fill=(*col,rnd.randint(5,20)))
        for _ in range(12):
            x=rnd.randrange(w); y=rnd.randrange(h); r=rnd.randint(8,24)
            d.ellipse((x-r,y-r,x+r,y+r),fill=(73,57,31,rnd.randint(10,26)))
    out=rgba_overlay(base,p)
    return ImageEnhance.Color(out).enhance(1.10)


def cloth(base,name):
    rnd=random.Random(seed(name)); w,h=base.size
    def p(d,size):
        for x in range(0,w,11): d.line((x,0,x,h),fill=(210,199,175,10),width=1)
        for y in range(0,h,11): d.line((0,y,w,y),fill=(40,34,29,12),width=1)
        for _ in range(28):
            x=rnd.randrange(w); y=rnd.randrange(h); rx=rnd.randint(18,90); ry=rnd.randint(8,42)
            d.ellipse((x-rx,y-ry,x+rx,y+ry),fill=(51,55,43,rnd.randint(5,18)))
        for _ in range(14):
            x=rnd.randrange(w); y=rnd.randrange(h); ln=rnd.randint(70,250)
            d.line((x,y,min(w-1,x+ln),y+rnd.randint(-8,8)),fill=(219,201,169,rnd.randint(7,18)),width=2)
    return rgba_overlay(base,p)


def mud(base,name):
    rnd=random.Random(seed(name)); w,h=base.size
    def p(d,size):
        for _ in range(55):
            x=rnd.randrange(w); y=rnd.randrange(h); rx=rnd.randint(22,115); ry=rnd.randint(8,48)
            d.ellipse((x-rx,y-ry,x+rx,y+ry),fill=(30,39,36,rnd.randint(8,28)))
            if rnd.random()<.45: d.arc((x-rx,y-ry,x+rx,y+ry),185,345,fill=(151,127,85,rnd.randint(8,18)),width=2)
        for _ in range(22):
            x=rnd.randrange(w); y=rnd.randrange(h)
            d.line((x,y,x+rnd.randint(-55,55),y+rnd.randint(15,80)),fill=(44,36,28,rnd.randint(12,32)),width=1)
    return rgba_overlay(base,p)


def fire(base,name):
    w,h=base.size
    # Purpose-made orange/yellow heat map: yellow core, orange mid, darker edge.
    out=Image.new("RGB",(w,h),(135,43,12)); px=out.load()
    for y in range(h):
        v=1-y/max(1,h-1)
        for x in range(w):
            u=abs((x/(w-1))*2-1)
            core=max(0.0,1-u*1.55)
            heat=max(0.0,min(1.0,.30+.62*v+.55*core))
            r=int(170+85*heat)
            g=int(38+177*(heat**1.7)*core + 75*heat*(1-core))
            b=int(6+42*(heat**2)*core)
            px[x,y]=(min(255,r),min(255,g),min(120,b))
    return Image.blend(base,out,.62)


def char(base,name):
    rnd=random.Random(seed(name)); w,h=base.size
    def p(d,size):
        for _ in range(50):
            x=rnd.randrange(w); y=rnd.randrange(h)
            pts=[(x,y)]
            for _ in range(rnd.randint(2,5)):
                x=max(0,min(w-1,x+rnd.randint(-35,35))); y=max(0,min(h-1,y+rnd.randint(18,75))); pts.append((x,y))
            d.line(pts,fill=(178,166,145,rnd.randint(10,35)),width=1)
        for _ in range(24):
            x=rnd.randrange(w); y=rnd.randrange(h); r=rnd.randint(10,45)
            d.ellipse((x-r,y-r,x+r,y+r),fill=(199,191,171,rnd.randint(4,14)))
    return rgba_overlay(base,p)


def water(base,name):
    rnd=random.Random(seed(name)); w,h=base.size
    def p(d,size):
        for y in range(8,h,26):
            phase=rnd.uniform(0,math.pi*2); pts=[]
            for x in range(-20,w+21,18): pts.append((x,y+math.sin(x*.030+phase)*5))
            d.line(pts,fill=(190,220,223,rnd.randint(12,34)),width=2)
        for _ in range(18):
            x=rnd.randrange(w); y=rnd.randrange(h); rx=rnd.randint(25,95); ry=rnd.randint(5,18)
            d.arc((x-rx,y-ry,x+rx,y+ry),190,350,fill=(18,58,73,rnd.randint(10,28)),width=2)
    return rgba_overlay(base,p)


REFINERS={"wood":wood,"rope":rope,"tarp":tarp,"metal":metal,"stone":stone,"leaf":leaf,"cloth":cloth,"mud":mud,"fire":fire,"char":char,"water":water}


def main()->int:
    changed=0
    for name in NAMES:
        path=TEX/f"{name}_albedo.png"
        if not path.exists(): raise SystemExit(f"Missing albedo: {path}")
        with Image.open(path) as src: base=src.convert("RGB")
        if base.size!=(1024,1024): raise SystemExit(f"Unexpected albedo size for {name}: {base.size}")
        out=REFINERS[name](base,name)
        out.save(path,compress_level=6); changed+=1
    print(f"Atlas-aligned final surface storytelling applied to {changed} shared albedos")
    return 0

if __name__=="__main__": raise SystemExit(main())
