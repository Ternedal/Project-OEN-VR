#!/usr/bin/env python3
"""Generate deterministic transparent production sprite atlases for A3 VFX."""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "source_art" / "vfx" / "a3" / "production"
SIZE = 512
SEED = 20260814


def canvas() -> Image.Image:
    return Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))


def save(image: Image.Image, name: str) -> None:
    path = OUT / f"{name}.png"
    image.save(path, "PNG", optimize=True)
    print(path.relative_to(ROOT))


def rain() -> None:
    image = canvas()
    draw = ImageDraw.Draw(image)
    rng = random.Random(SEED + 1)
    for cell_y in range(2):
        for cell_x in range(2):
            x0, y0 = cell_x * 256, cell_y * 256
            count = 4 + cell_y * 2 + cell_x
            for index in range(count):
                x = x0 + 40 + index * (175 / max(1, count - 1)) + rng.uniform(-10, 10)
                y = y0 + rng.uniform(28, 105)
                length = rng.uniform(70, 132)
                width = rng.choice((3, 4, 5, 6))
                draw.line((x, y, x - length * .40, y + length), fill=(222, 236, 238, rng.randint(100, 190)), width=width)
    save(image, "VFX_RAIN_001")


def wind_debris() -> None:
    image = canvas()
    draw = ImageDraw.Draw(image)
    # leaf, fiber strip, twig and fleck group; one independently addressable cell each.
    draw.polygon([(45,135),(115,63),(210,112),(150,190),(72,178)], fill=(90,112,82,235))
    draw.line((55,168,190,92), fill=(183,194,159,230), width=8)
    draw.rounded_rectangle((300,80,460,160), radius=24, fill=(175,157,111,235))
    draw.line((310,145,450,93), fill=(226,216,181,210), width=7)
    draw.line((55,402,215,304), fill=(115,83,56,245), width=22)
    draw.line((70,410,226,316), fill=(178,144,93,210), width=5)
    rng = random.Random(SEED + 2)
    for _ in range(18):
        x, y = rng.randint(300,470), rng.randint(300,470)
        radius = rng.randint(3,10)
        draw.ellipse((x-radius,y-radius,x+radius,y+radius), fill=(193,178,130,rng.randint(120,220)))
    save(image, "VFX_WIND_DEBRIS_001")


def ember_sprite(image: Image.Image, center: tuple[int, int], radius: int, color: tuple[int, int, int]) -> None:
    glow = canvas()
    glow_draw = ImageDraw.Draw(glow)
    x, y = center
    glow_draw.ellipse((x-radius*3,y-radius*3,x+radius*3,y+radius*3), fill=(*color, 90))
    glow = glow.filter(ImageFilter.GaussianBlur(radius * 1.4))
    image.alpha_composite(glow)
    draw = ImageDraw.Draw(image)
    points = []
    for index in range(8):
        angle = 2 * math.pi * index / 8
        local = radius * (1.0 if index % 2 == 0 else .70)
        points.append((x + math.cos(angle) * local, y + math.sin(angle) * local * 1.35))
    draw.polygon(points, fill=(*color, 245))
    draw.ellipse((x-radius*.28,y-radius*.35,x+radius*.28,y+radius*.35), fill=(255,238,190,245))


def embers() -> None:
    image = canvas()
    ember_sprite(image, (128,128), 25, (218,145,72))
    ember_sprite(image, (384,128), 34, (181,87,61))
    ember_sprite(image, (128,384), 20, (236,190,112))
    ember_sprite(image, (384,384), 29, (211,117,62))
    save(image, "VFX_FIRE_EMBERS_001")


def smoke() -> None:
    image = canvas()
    rng = random.Random(SEED + 3)
    for cell_y in range(2):
        for cell_x in range(2):
            layer = canvas()
            draw = ImageDraw.Draw(layer)
            base_x, base_y = cell_x * 256 + 128, cell_y * 256 + 150
            density = 7 + cell_y * 3
            alpha = 70 + cell_y * 24
            for index in range(density):
                x = base_x + rng.randint(-72,72)
                y = base_y - index * 10 + rng.randint(-20,20)
                rx, ry = rng.randint(35,72), rng.randint(25,58)
                draw.ellipse((x-rx,y-ry,x+rx,y+ry), fill=(88,103,109,alpha))
            layer = layer.filter(ImageFilter.GaussianBlur(13 + cell_y * 3))
            image.alpha_composite(layer)
    save(image, "VFX_FIRE_SMOKE_001")


def impact() -> None:
    image = canvas()
    rng = random.Random(SEED + 4)
    for cell_y in range(2):
        for cell_x in range(2):
            cx, cy = cell_x * 256 + 128, cell_y * 256 + 128
            layer = canvas()
            draw = ImageDraw.Draw(layer)
            draw.ellipse((cx-70,cy-45,cx+70,cy+45), fill=(188,170,128,70 + 25 * cell_y))
            for ray in range(7 + cell_x * 2):
                angle = 2 * math.pi * ray / (7 + cell_x * 2) + rng.uniform(-.18,.18)
                inner, outer = 35, rng.randint(75,110)
                start = (cx + math.cos(angle)*inner, cy + math.sin(angle)*inner)
                end = (cx + math.cos(angle)*outer, cy + math.sin(angle)*outer)
                draw.line((*start,*end), fill=(132,96,63,210), width=rng.randint(5,11))
            for _ in range(8):
                x, y = cx+rng.randint(-95,95), cy+rng.randint(-75,75)
                r = rng.randint(3,8)
                draw.ellipse((x-r,y-r,x+r,y+r), fill=(222,213,180,180))
            layer = layer.filter(ImageFilter.GaussianBlur(2))
            image.alpha_composite(layer)
    save(image, "VFX_IMPACT_001")


def rope_strain() -> None:
    image = canvas()
    rng = random.Random(SEED + 5)
    for cell_y in range(2):
        for cell_x in range(2):
            cx, cy = cell_x * 256 + 128, cell_y * 256 + 128
            draw = ImageDraw.Draw(image)
            intensity = 5 + (cell_y * 2 + cell_x) * 3
            draw.arc((cx-72,cy-72,cx+72,cy+72), 205, 335, fill=(216,185,128,185), width=6)
            for _ in range(intensity):
                angle = rng.uniform(math.radians(205), math.radians(335))
                radius = rng.uniform(55,110)
                x, y = cx+math.cos(angle)*radius, cy+math.sin(angle)*radius
                length = rng.uniform(12,30)
                draw.line((x,y,x+math.cos(angle)*length,y+math.sin(angle)*length), fill=(224,210,172,rng.randint(130,230)), width=rng.randint(2,5))
    save(image, "VFX_ROPE_STRAIN_001")


def wetness() -> None:
    image = Image.new("RGBA", (SIZE, SIZE), (42, 45, 43, 255))
    rng = random.Random(SEED + 6)
    layer = Image.new("L", (SIZE, SIZE), 0)
    draw = ImageDraw.Draw(layer)
    for _ in range(38):
        x, y = rng.randint(-70, SIZE+70), rng.randint(-70, SIZE+70)
        rx, ry = rng.randint(35,110), rng.randint(24,85)
        draw.ellipse((x-rx,y-ry,x+rx,y+ry), fill=rng.randint(80,190))
    layer = layer.filter(ImageFilter.GaussianBlur(22))
    dry = Image.new("RGBA", (SIZE, SIZE), (154, 145, 119, 255))
    wet = Image.new("RGBA", (SIZE, SIZE), (66, 79, 82, 255))
    image = Image.composite(wet, dry, layer)
    image.putalpha(255)
    save(image, "VFX_WETNESS_REFERENCE_001")


def metadata() -> None:
    data = {
        "version": 1,
        "generator": "tools/generate_a3_vfx_sprites.py",
        "atlases": {
            "VFX_RAIN_001.png": {"grid": [2, 2], "cellPixels": [256, 256], "alpha": True},
            "VFX_WIND_DEBRIS_001.png": {"grid": [2, 2], "cellPixels": [256, 256], "alpha": True, "cells": ["leaf", "fiber", "twig", "flecks"]},
            "VFX_FIRE_EMBERS_001.png": {"grid": [2, 2], "cellPixels": [256, 256], "alpha": True},
            "VFX_FIRE_SMOKE_001.png": {"grid": [2, 2], "cellPixels": [256, 256], "alpha": True, "rows": ["lighter", "wet-dense"]},
            "VFX_IMPACT_001.png": {"grid": [2, 2], "cellPixels": [256, 256], "alpha": True},
            "VFX_ROPE_STRAIN_001.png": {"grid": [2, 2], "cellPixels": [256, 256], "alpha": True, "rule": "secondary cue only"},
            "VFX_WETNESS_REFERENCE_001.png": {"grid": [1, 1], "cellPixels": [512, 512], "alpha": False, "rule": "look/mask reference, not shader mandate"},
        },
        "runtimeBoundary": "Unity particle systems, blending, shader binding, timing, density, pooling, overdraw and device QA remain Claude-owned.",
    }
    path = OUT / "VFX_SPRITE_LAYOUT.source.json"
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(path.relative_to(ROOT))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rain()
    wind_debris()
    embers()
    smoke()
    impact()
    rope_strain()
    wetness()
    metadata()


if __name__ == "__main__":
    main()
