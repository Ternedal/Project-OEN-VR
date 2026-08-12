#!/usr/bin/env python3
"""Dedicated deterministic VFX texture pass for Project ØEN.

The 14 VFX-support states are intentionally excluded from UI styling. This pass
replaces their broad icon treatment with effect-oriented RGBA textures suitable
for Unity particle/unlit materials while preserving one file per canonical state.

FX-001 smoke is a 4x4 flipbook atlas by design; the *asset* is still one separate
canonical texture per small/medium state, not a contact sheet of unrelated art.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageChops

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROD = ROOT / "Assets" / "ProjectOEN" / "ProductionArt"
MANIFEST = PROD / "Docs" / "production_art_manifest.json"
REPORT = PROD / "Docs" / "vfx_refinement.json"
SIZE = 1024


def rng_for(seed: str) -> random.Random:
    value = int.from_bytes(hashlib.sha256(seed.encode("utf-8")).digest()[:8], "big")
    return random.Random(value)


def save_rgba(im: Image.Image, path: Path) -> None:
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, compress_level=6)


def radial_alpha(size: int, inner: float, outer: float, power: float = 1.6) -> Image.Image:
    im = Image.new("L", (size, size), 0)
    px = im.load()
    c = (size - 1) * 0.5
    maxr = c
    for y in range(size):
        dy = (y - c) / maxr
        for x in range(size):
            dx = (x - c) / maxr
            r = math.sqrt(dx * dx + dy * dy)
            if r <= inner:
                a = 1.0
            elif r >= outer:
                a = 0.0
            else:
                a = ((outer - r) / max(1e-6, outer - inner)) ** power
            px[x, y] = int(max(0.0, min(1.0, a)) * 255)
    return im


def smoke_flipbook(variant: str, seed: str) -> Image.Image:
    atlas = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    cell = SIZE // 4
    density = 18 if variant == "small" else 26
    radius_scale = 0.72 if variant == "small" else 0.92
    rnd = rng_for(seed)

    for frame in range(16):
        tile = Image.new("L", (cell, cell), 0)
        d = ImageDraw.Draw(tile)
        life = frame / 15.0
        rise = int(life * cell * 0.10)
        spread = 0.62 + life * 0.42
        for _ in range(density):
            cx = cell * 0.5 + rnd.uniform(-0.19, 0.19) * cell * spread
            cy = cell * 0.55 + rnd.uniform(-0.18, 0.18) * cell * spread - rise
            r = rnd.uniform(0.055, 0.15) * cell * radius_scale * (0.85 + life * 0.45)
            alpha = int(rnd.uniform(95, 195) * (1.0 - life * 0.32))
            d.ellipse((cx-r, cy-r, cx+r, cy+r), fill=alpha)
        tile = tile.filter(ImageFilter.GaussianBlur(max(5, int(cell * 0.035))))
        # Keep a transparent cell gutter to avoid atlas bleeding.
        gutter = Image.new("L", (cell, cell), 0)
        gd = ImageDraw.Draw(gutter)
        pad = 8
        gd.rounded_rectangle((pad, pad, cell-pad, cell-pad), 24, fill=255)
        tile = ImageChops.multiply(tile, gutter)

        rgb = Image.new("RGBA", (cell, cell), (205, 215, 216, 255))
        rgb.putalpha(tile)
        x = (frame % 4) * cell
        y = (frame // 4) * cell
        atlas.alpha_composite(rgb, (x, y))
    return atlas


def ember_particle(variant: str, seed: str) -> Image.Image:
    im = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    alpha = Image.new("L", (SIZE, SIZE), 0)
    d = ImageDraw.Draw(alpha)
    rnd = rng_for(seed)
    scale = 0.72 if variant == "small" else 1.0
    cx, cy = SIZE // 2, SIZE // 2
    for i in range(5):
        ox = rnd.uniform(-0.07, 0.07) * SIZE
        oy = rnd.uniform(-0.06, 0.08) * SIZE
        w = rnd.uniform(16, 30) * scale
        h = rnd.uniform(70, 125) * scale
        a = rnd.uniform(-22, 22)
        shard = Image.new("L", (SIZE, SIZE), 0)
        sd = ImageDraw.Draw(shard)
        sd.rounded_rectangle((cx+ox-w, cy+oy-h/2, cx+ox+w, cy+oy+h/2), int(max(4, w)), fill=240)
        shard = shard.rotate(a, resample=Image.Resampling.BICUBIC, center=(cx+ox, cy+oy))
        alpha = ImageChops.lighter(alpha, shard)
    glow = alpha.filter(ImageFilter.GaussianBlur(34 if variant == "medium" else 25)).point(lambda p: int(p * 0.52))
    glow_rgba = Image.new("RGBA", im.size, (255, 95, 18, 255)); glow_rgba.putalpha(glow)
    im = Image.alpha_composite(im, glow_rgba)
    core = Image.new("RGBA", im.size, (255, 205, 76, 255)); core.putalpha(alpha)
    return Image.alpha_composite(im, core)


def ash_particle(seed: str) -> Image.Image:
    im = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    mask = Image.new("L", im.size, 0); d = ImageDraw.Draw(mask)
    rnd = rng_for(seed)
    cx, cy = SIZE//2, SIZE//2
    pts=[]
    for i in range(13):
        a=2*math.pi*i/13 + rnd.uniform(-0.12,0.12)
        r=rnd.uniform(72,150)
        pts.append((cx+math.cos(a)*r,cy+math.sin(a)*r*0.62))
    d.polygon(pts, fill=210)
    for _ in range(9):
        x=cx+rnd.uniform(-70,70); y=cy+rnd.uniform(-45,45); r=rnd.uniform(8,20)
        d.ellipse((x-r,y-r,x+r,y+r),fill=rnd.randint(40,130))
    mask=mask.filter(ImageFilter.GaussianBlur(3))
    layer=Image.new("RGBA",im.size,(194,190,176,255)); layer.putalpha(mask)
    return layer


def rain_splash(variant: str, seed: str) -> Image.Image:
    im=Image.new("RGBA",(SIZE,SIZE),(0,0,0,0))
    mask=Image.new("L",im.size,0); d=ImageDraw.Draw(mask)
    cx,cy=SIZE//2,int(SIZE*.56)
    scale=.72 if variant=="small" else 1.0
    box=(cx-int(190*scale),cy-int(66*scale),cx+int(190*scale),cy+int(66*scale))
    d.ellipse(box,outline=215,width=max(8,int(18*scale)))
    rnd=rng_for(seed)
    for i in range(14):
        a=2*math.pi*i/14+rnd.uniform(-.08,.08)
        x=cx+math.cos(a)*190*scale; y=cy+math.sin(a)*66*scale
        length=rnd.uniform(35,90)*scale
        d.line((x,y,x+math.cos(a)*length,y+math.sin(a)*length*.55),fill=rnd.randint(130,235),width=max(5,int(10*scale)))
    mask=mask.filter(ImageFilter.GaussianBlur(4))
    layer=Image.new("RGBA",im.size,(155,210,230,255)); layer.putalpha(mask)
    return layer


def wet_sheen(seed: str) -> Image.Image:
    im=Image.new("RGBA",(SIZE,SIZE),(0,0,0,0))
    mask=Image.new("L",im.size,0); rnd=rng_for(seed)
    for i in range(7):
        streak=Image.new("L",im.size,0); d=ImageDraw.Draw(streak)
        x=rnd.uniform(.22,.78)*SIZE; y=rnd.uniform(.22,.78)*SIZE
        w=rnd.uniform(70,180); h=rnd.uniform(260,470)
        d.ellipse((x-w/2,y-h/2,x+w/2,y+h/2),fill=rnd.randint(95,190))
        streak=streak.rotate(rnd.uniform(-38,38),resample=Image.Resampling.BICUBIC,center=(x,y))
        mask=ImageChops.lighter(mask,streak)
    mask=mask.filter(ImageFilter.GaussianBlur(32))
    # Keep outer gutter transparent for safe sampling.
    vignette=radial_alpha(SIZE,.52,.86,1.8)
    mask=ImageChops.multiply(mask,vignette)
    layer=Image.new("RGBA",im.size,(225,242,245,255)); layer.putalpha(mask)
    return layer


def lightning(variant: str, seed: str) -> Image.Image:
    im=Image.new("RGBA",(SIZE,SIZE),(0,0,0,0)); rnd=rng_for(seed)
    mask=Image.new("L",im.size,0); d=ImageDraw.Draw(mask)
    near=variant=="near"
    x=SIZE*(.48 if near else .58); y=SIZE*.08
    pts=[(x,y)]
    segments=9 if near else 7
    for i in range(segments):
        x += rnd.uniform(-75,75)*(1.0 if near else .72)
        y += rnd.uniform(70,105)
        pts.append((x,y))
    width=18 if near else 10
    d.line(pts,fill=255,width=width,joint="curve")
    # A few restrained branches.
    for idx in (2,4,6):
        if idx>=len(pts)-1: continue
        sx,sy=pts[idx]
        ex=sx+rnd.uniform(-150,150); ey=sy+rnd.uniform(90,180)
        d.line((sx,sy,ex,ey),fill=205,width=max(4,width//2))
    glow=mask.filter(ImageFilter.GaussianBlur(30 if near else 18)).point(lambda p:int(p*.72))
    g=Image.new("RGBA",im.size,(120,188,255,255)); g.putalpha(glow); im=Image.alpha_composite(im,g)
    core=Image.new("RGBA",im.size,(246,250,255,255)); core.putalpha(mask)
    return Image.alpha_composite(im,core)


def glow_halo(variant: str) -> Image.Image:
    alpha=radial_alpha(SIZE,.05,.68,2.2)
    # Punch down the very center slightly so the halo sits around a source.
    hole=radial_alpha(SIZE,0.0,.16,1.3)
    alpha=ImageChops.subtract(alpha,hole.point(lambda p:int(p*.45)))
    col=(255,112,28,255) if variant=="fire" else (255,190,80,255)
    layer=Image.new("RGBA",(SIZE,SIZE),col); layer.putalpha(alpha.point(lambda p:int(p*.72)))
    return layer


def pulse_ring(variant: str) -> Image.Image:
    im=Image.new("RGBA",(SIZE,SIZE),(0,0,0,0)); mask=Image.new("L",im.size,0); d=ImageDraw.Draw(mask)
    r=210 if variant=="small" else 330
    w=18 if variant=="small" else 24
    cx=cy=SIZE//2
    d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=230,width=w)
    # Three cardinal ticks make scale/state readable in VR.
    for a in (-90,30,150):
        rad=math.radians(a)
        x1=cx+math.cos(rad)*(r-30); y1=cy+math.sin(rad)*(r-30)
        x2=cx+math.cos(rad)*(r+38); y2=cy+math.sin(rad)*(r+38)
        d.line((x1,y1,x2,y2),fill=255,width=w)
    glow=mask.filter(ImageFilter.GaussianBlur(18)).point(lambda p:int(p*.55))
    g=Image.new("RGBA",im.size,(80,183,206,255)); g.putalpha(glow); im=Image.alpha_composite(im,g)
    core=Image.new("RGBA",im.size,(226,218,177,255)); core.putalpha(mask)
    return Image.alpha_composite(im,core)


def render(aid: str, variant: str) -> Image.Image:
    seed=f"ProjectOEN.VFX:{aid}:{variant}"
    if aid=="FX-001": return smoke_flipbook(variant,seed)
    if aid=="FX-002": return ember_particle(variant,seed)
    if aid=="FX-003": return ash_particle(seed)
    if aid=="FX-004": return rain_splash(variant,seed)
    if aid=="FX-005": return wet_sheen(seed)
    if aid=="FX-006": return lightning(variant,seed)
    if aid=="FX-007": return glow_halo(variant)
    if aid=="FX-008": return pulse_ring(variant)
    raise ValueError(f"Unexpected VFX asset ID: {aid}")


def main()->int:
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries=[e for e in manifest if e.get("kind")=="sprite" and e.get("category")=="VFX support graphics"]
    if len(entries)!=14:
        raise SystemExit(f"Expected 14 VFX sprite states, found {len(entries)}")
    report=[]
    for e in entries:
        aid=str(e["asset_id"]); variant=str(e.get("variant","default")); path=ROOT/e["path"]
        im=render(aid,variant)
        if im.size!=(SIZE,SIZE): raise RuntimeError(f"Bad VFX size for {aid}/{variant}: {im.size}")
        save_rgba(im,path)
        report.append({"asset_id":aid,"variant":variant,"path":e["path"],"dimensions":[SIZE,SIZE],"sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
    REPORT.write_text(json.dumps({"vfx_count":len(report),"entries":report},indent=2),encoding="utf-8")
    print("Refined 14 Project ØEN VFX textures: smoke flipbooks, embers, ash, rain splash, wet sheen, lightning, glow and objective pulse")
    return 0

if __name__=="__main__": raise SystemExit(main())
