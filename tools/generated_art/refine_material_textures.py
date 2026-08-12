#!/usr/bin/env python3
"""Upgrade Project ØEN shared world materials with readable Quest-scale surface detail.

Overwrites the broad-pass 512px albedos with deterministic 1024px hero-ready
albedos, and adds 512px normal + metallic/smoothness support maps. Geometry stays
on the same material names, so existing OBJ/MTL references remain stable.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROD = ROOT / "Assets" / "ProjectOEN" / "ProductionArt"
TEX = PROD / "Materials" / "Textures"
DOCS = PROD / "Docs"
MANIFEST = DOCS / "production_art_manifest.json"

MATERIALS = {
    "wood": ((116,79,46), 0, 72),
    "rope": ((171,139,91), 0, 58),
    "tarp": ((47,86,103), 0, 92),
    "metal": ((91,103,103), 220, 128),
    "stone": ((101,107,104), 0, 44),
    "leaf": ((72,104,61), 0, 52),
    "cloth": ((96,83,67), 0, 55),
    "mud": ((76,66,47), 0, 40),
    "fire": ((226,102,30), 0, 210),
    "char": ((42,37,32), 0, 30),
    "water": ((62,112,134), 0, 225),
}


def guid_for(path: Path) -> str:
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    return hashlib.md5(("ProjectOEN.Surface.v1:" + rel).encode()).hexdigest()


def meta(path: Path, max_size: int, normal=False) -> str:
    return f'''fileFormatVersion: 2\nguid: {guid_for(path)}\nTextureImporter:\n  internalIDToNameTable: []\n  externalObjects: {{}}\n  serializedVersion: 13\n  mipmaps:\n    mipMapMode: 0\n    enableMipMap: 1\n  isReadable: 0\n  streamingMipmaps: 0\n  textureSettings:\n    serializedVersion: 2\n    filterMode: 1\n    aniso: 1\n    mipBias: 0\n    wrapU: 0\n    wrapV: 0\n    wrapW: 0\n  nPOTScale: 0\n  alphaIsTransparency: 0\n  textureType: {1 if normal else 0}\n  alphaSource: 1\n  platformSettings:\n  - serializedVersion: 3\n    buildTarget: DefaultTexturePlatform\n    maxTextureSize: {max_size}\n    resizeAlgorithm: 0\n    textureFormat: -1\n    textureCompression: 1\n    compressionQuality: 72\n    crunchedCompression: 0\n    allowsAlphaSplitting: 0\n    overridden: 0\n  userData: Project OEN refined surface map\n  assetBundleName: \n  assetBundleVariant: \n'''


def height_field(name: str, size: int, seed: int) -> Image.Image:
    rnd = random.Random(seed)
    im = Image.new("L", (size,size), 128)
    d = ImageDraw.Draw(im)
    if name == "wood":
        for y in range(0,size,9):
            wobble = rnd.randint(-5,5)
            d.line([(0,y+wobble),(size*.25,y+rnd.randint(-4,4)),(size*.55,y+rnd.randint(-6,6)),(size,y+rnd.randint(-5,5))], fill=rnd.randint(92,170), width=rnd.randint(2,5))
        for _ in range(12):
            x=rnd.randrange(size); y=rnd.randrange(size); rx=rnd.randint(12,35); ry=rnd.randint(5,14)
            d.ellipse((x-rx,y-ry,x+rx,y+ry),outline=rnd.randint(55,100),width=3)
    elif name == "rope":
        for k in range(-size,size,18):
            d.line((k,0,k+size,size),fill=178,width=5)
            d.line((k+8,0,k+size+8,size),fill=88,width=2)
    elif name in ("tarp","cloth"):
        step=14 if name=="tarp" else 10
        for x in range(0,size,step): d.line((x,0,x,size),fill=158,width=2)
        for y in range(0,size,step): d.line((0,y,size,y),fill=98,width=2)
    elif name == "metal":
        for _ in range(90):
            y=rnd.randrange(size); x=rnd.randrange(size); ln=rnd.randint(18,110)
            d.line((x,y,min(size-1,x+ln),y+rnd.randint(-2,2)),fill=rnd.randint(80,175),width=1)
        for _ in range(18):
            x=rnd.randrange(size); y=rnd.randrange(size); r=rnd.randint(4,18)
            d.ellipse((x-r,y-r,x+r,y+r),fill=rnd.randint(65,110))
    elif name in ("stone","mud","char"):
        for _ in range(180):
            x=rnd.randrange(size); y=rnd.randrange(size); r=rnd.randint(4,28)
            d.ellipse((x-r,y-r,x+r,y+r),fill=rnd.randint(70,185))
        if name=="char":
            for _ in range(35):
                x=rnd.randrange(size); y=rnd.randrange(size)
                d.line((x,y,x+rnd.randint(-45,45),y+rnd.randint(25,80)),fill=205,width=2)
    elif name == "leaf":
        d.line((0,size//2,size,size//2),fill=205,width=7)
        for x in range(0,size,42):
            d.line((x,size//2,x+55,0),fill=178,width=3); d.line((x,size//2,x+55,size),fill=178,width=3)
    elif name == "water":
        for y in range(0,size,22):
            pts=[]
            for x in range(0,size+20,20): pts.append((x,y+math.sin((x+y)*.035)*5))
            d.line(pts,fill=174,width=3)
    elif name == "fire":
        for y in range(size):
            val=int(70+170*(1-y/size)); d.line((0,y,size,y),fill=val)
    return im.filter(ImageFilter.GaussianBlur(1.1))


def normal_from_height(h: Image.Image, strength=2.2) -> Image.Image:
    w,hgt=h.size; px=h.load(); out=Image.new("RGB",h.size); op=out.load()
    for y in range(hgt):
        ym=max(0,y-1); yp=min(hgt-1,y+1)
        for x in range(w):
            xm=max(0,x-1); xp=min(w-1,x+1)
            dx=(px[xp,y]-px[xm,y])/255.0*strength
            dy=(px[x,yp]-px[x,ym])/255.0*strength
            nx,ny,nz=-dx,-dy,1.0
            inv=1.0/math.sqrt(nx*nx+ny*ny+nz*nz)
            op[x,y]=(int((nx*inv*.5+.5)*255),int((ny*inv*.5+.5)*255),int((nz*inv*.5+.5)*255))
    return out


def albedo(name: str, base_rgb, height: Image.Image, size=1024) -> Image.Image:
    h=height.resize((size,size),Image.Resampling.BICUBIC)
    im=Image.new("RGB",(size,size),base_rgb)
    shade=h.point(lambda v:max(0,min(255,128+int((v-128)*.42))))
    shade_rgb=Image.merge("RGB",(shade,shade,shade))
    im=ImageChops.multiply(im,shade_rgb).point(lambda p:min(255,int(p*1.95)))
    d=ImageDraw.Draw(im,"RGBA"); rnd=random.Random("albedo:"+name)
    if name=="metal":
        for _ in range(30):
            x=rnd.randrange(size); y=rnd.randrange(size); r=rnd.randint(4,20)
            d.ellipse((x-r,y-r,x+r,y+r),fill=(137,67,36,rnd.randint(30,100)))
    elif name=="tarp":
        for _ in range(14):
            x=rnd.randrange(size); y=rnd.randrange(size); r=rnd.randint(30,90)
            d.ellipse((x-r,y-r,x+r,y+r),fill=(16,35,42,rnd.randint(12,35)))
    elif name=="wood":
        for _ in range(18):
            x=rnd.randrange(size); y=rnd.randrange(size)
            d.line((x,y,min(size,x+rnd.randint(50,180)),y+rnd.randint(-4,4)),fill=(62,36,20,rnd.randint(30,75)),width=2)
    return im


def write_maps(name: str, base_rgb, metallic: int, smooth: int) -> None:
    h=height_field(name,512,int(hashlib.md5(name.encode()).hexdigest()[:8],16))
    a=albedo(name,base_rgb,h,1024)
    ap=TEX/f"{name}_albedo.png"; a.save(ap,compress_level=6); Path(str(ap)+".meta").write_text(meta(ap,1024),encoding="utf-8")
    n=normal_from_height(h)
    np=TEX/f"{name}_normal.png"; n.save(np,compress_level=6); Path(str(np)+".meta").write_text(meta(np,512,True),encoding="utf-8")
    mask=Image.new("RGBA",(512,512),(metallic,metallic,metallic,smooth))
    mp=TEX/f"{name}_metallic_smoothness.png"; mask.save(mp,compress_level=6); Path(str(mp)+".meta").write_text(meta(mp,512),encoding="utf-8")


def write_final_docs() -> None:
    sprite_count = mesh_count = 0
    if MANIFEST.exists():
        manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
        sprite_count=sum(1 for e in manifest if e.get("kind")=="sprite")
        mesh_count=sum(1 for e in manifest if e.get("kind")=="mesh")
    material_names=", ".join(MATERIALS.keys())
    (DOCS/"README.md").write_text(
        "# Project ØEN Production Art\n\n"
        "Generated from the canonical 148-row asset master and then refined by the hero/surface pipeline. "
        "Every listed state/variant is exported as an individual Unity-importable file.\n\n"
        f"- Separate sprites: **{sprite_count}**\n"
        f"- Separate world meshes: **{mesh_count}**\n"
        f"- Shared surface materials: **{len(MATERIALS)}**\n"
        f"- Surface texture maps: **{len(MATERIALS)*3}** (1024px albedo + 512px normal + 512px metallic/smoothness)\n"
        "- Source: `tools/generated_art/asset_master.csv`\n\n"
        "The production pass uses coherent handmade wood/rope/tarp/metal/stone materials, diegetic-first UI, "
        "warm camp accents and cool storm accents. Hero world assets receive a subsequent high-detail geometry "
        "and rope-joinery pass. No Hunger/Thirst HUD assets are generated.\n\n"
        f"Surface set: {material_names}.\n",
        encoding="utf-8")


def main() -> int:
    TEX.mkdir(parents=True,exist_ok=True)
    DOCS.mkdir(parents=True,exist_ok=True)
    for name,(rgb,metallic,smooth) in MATERIALS.items():
        write_maps(name,rgb,metallic,smooth)
    write_final_docs()
    print(f"Refined {len(MATERIALS)} shared materials: 1024 albedo + 512 normal/mask maps")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
