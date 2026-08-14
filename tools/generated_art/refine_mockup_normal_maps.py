#!/usr/bin/env python3
"""Replace synthetic 'bubble' normals with atlas-aligned rough surface structure.

The broad material generator used many circular height blobs for stone/mud/char. They
passed technical QA but read as procedural bubbles in the actual material review sheet.
This pass keeps canonical filenames, dimensions and .meta GUIDs, but replaces only the
normal-map pixels for the three visible offenders:

* stone: broad fractured planes + fine mineral grain + sparse cracks;
* mud: low rolling wet relief + shallow ruts + drying fissures;
* char: restrained rough grain + branching heat/ash cracks.

No albedo, masks, importer metadata or shader contracts are changed.
"""
from __future__ import annotations

import hashlib
import math
import random
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageEnhance

from refine_material_textures import normal_from_height

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
TEX=ROOT/"Assets"/"ProjectOEN"/"ProductionArt"/"Materials"/"Textures"
SIZE=512
TARGETS=("stone","mud","char")


def seed(label:str)->int:
    return int(hashlib.sha256(("ProjectOEN.MockupNormals.v1:"+label).encode()).hexdigest()[:16],16)


def periodic_noise(size:int,cells:int,label:str,blur:float=0.0)->Image.Image:
    rnd=random.Random(seed(label))
    vals=[[rnd.randrange(256) for _ in range(cells)] for _ in range(cells)]
    small=Image.new("L",(cells+1,cells+1)); px=small.load()
    for y in range(cells+1):
        for x in range(cells+1): px[x,y]=vals[y%cells][x%cells]
    out=small.resize((size,size),Image.Resampling.BICUBIC)
    if blur>0: out=out.filter(ImageFilter.GaussianBlur(blur))
    return out


def mix_fields(a:Image.Image,b:Image.Image,weight:float,contrast:float=1.0)->Image.Image:
    out=Image.blend(a,b,weight)
    return ImageEnhance.Contrast(out).enhance(contrast)


def add_cracks(base:Image.Image,label:str,count:int,width=(1,3),depth=(18,55),branch_chance=.45)->Image.Image:
    rnd=random.Random(seed(label+":cracks")); out=base.copy(); d=ImageDraw.Draw(out)
    for _ in range(count):
        x=rnd.randrange(SIZE); y=rnd.randrange(SIZE); pts=[(x,y)]
        segments=rnd.randint(2,6)
        for __ in range(segments):
            x=(x+rnd.randint(-55,55))%SIZE; y=(y+rnd.randint(25,85))%SIZE; pts.append((x,y))
        col=max(0,128-rnd.randint(*depth)); w=rnd.randint(*width)
        d.line(pts,fill=col,width=w,joint="curve")
        if rnd.random()<branch_chance and len(pts)>2:
            bx,by=pts[rnd.randint(1,len(pts)-2)]
            d.line((bx,by,(bx+rnd.randint(-60,60))%SIZE,(by+rnd.randint(20,70))%SIZE),fill=min(127,col+10),width=max(1,w-1))
    return out.filter(ImageFilter.GaussianBlur(.35))


def stone_height()->Image.Image:
    broad=periodic_noise(SIZE,9,"stone:broad",5.5)
    medium=periodic_noise(SIZE,27,"stone:medium",1.8)
    fine=periodic_noise(SIZE,78,"stone:fine",.45)
    h=mix_fields(broad,medium,.43,1.18)
    h=mix_fields(h,fine,.20,1.05)
    h=add_cracks(h,"stone",26,(1,2),(24,62),.55)
    # sparse planar seams, deliberately not circular pebbles
    rnd=random.Random(seed("stone:seams")); d=ImageDraw.Draw(h)
    for _ in range(9):
        x=rnd.randrange(SIZE); y=rnd.randrange(SIZE); ln=rnd.randint(80,220)
        ang=rnd.uniform(-.7,.7); x2=(x+math.cos(ang)*ln)%SIZE; y2=(y+math.sin(ang)*ln)%SIZE
        d.line((x,y,x2,y2),fill=rnd.randint(82,111),width=rnd.randint(2,4))
    return h.filter(ImageFilter.GaussianBlur(.7))


def mud_height()->Image.Image:
    broad=periodic_noise(SIZE,7,"mud:broad",8.0)
    medium=periodic_noise(SIZE,19,"mud:medium",3.0)
    h=mix_fields(broad,medium,.34,.88)
    rnd=random.Random(seed("mud:ruts")); d=ImageDraw.Draw(h)
    # shallow dragged/rain ruts, not crater circles
    for _ in range(18):
        y=rnd.randrange(SIZE); phase=rnd.random()*math.tau; pts=[]
        for x in range(-20,SIZE+21,24): pts.append((x,y+math.sin(x*.020+phase)*rnd.uniform(3,11)))
        d.line(pts,fill=rnd.randint(98,119),width=rnd.randint(2,5))
    h=add_cracks(h,"mud",12,(1,2),(10,28),.65)
    return h.filter(ImageFilter.GaussianBlur(1.15))


def char_height()->Image.Image:
    broad=periodic_noise(SIZE,12,"char:broad",4.0)
    fine=periodic_noise(SIZE,64,"char:fine",.5)
    h=mix_fields(broad,fine,.18,.72)
    # char should be mostly restrained roughness; cracks carry the read
    h=Image.blend(Image.new("L",(SIZE,SIZE),128),h,.42)
    h=add_cracks(h,"char",46,(1,2),(34,76),.72)
    rnd=random.Random(seed("char:grain")); d=ImageDraw.Draw(h)
    for _ in range(34):
        x=rnd.randrange(SIZE); y=rnd.randrange(SIZE); ln=rnd.randint(30,130)
        d.line((x,y,min(SIZE-1,x+ln),y+rnd.randint(-5,5)),fill=rnd.randint(105,143),width=1)
    return h.filter(ImageFilter.GaussianBlur(.45))


def main()->int:
    builders={"stone":stone_height,"mud":mud_height,"char":char_height}
    strengths={"stone":1.55,"mud":1.10,"char":1.35}
    for name in TARGETS:
        path=TEX/f"{name}_normal.png"
        meta=Path(str(path)+".meta")
        if not path.exists() or not meta.exists(): raise SystemExit(f"Missing canonical normal/meta for {name}")
        before_meta=meta.read_bytes()
        h=builders[name]()
        n=normal_from_height(h,strengths[name])
        if n.size!=(512,512): raise SystemExit(f"Bad generated normal dimensions for {name}: {n.size}")
        n.save(path,compress_level=6)
        if meta.read_bytes()!=before_meta: raise SystemExit(f"Importer metadata unexpectedly changed for {name}")
    print("Replaced procedural bubble normals for stone/mud/char with fractured, rutted and heat-cracked relief")
    return 0

if __name__=="__main__": raise SystemExit(main())
