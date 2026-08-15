#!/usr/bin/env python3
"""Add deterministic Quest-friendly weathering to Project ØEN shared surface maps.

This pass runs after refine_material_textures.py and deliberately keeps the same
Unity paths, filenames and .meta GUIDs. It improves material read in VR by adding
low-frequency damp/wear variation to albedo and spatially varying smoothness
(and metallic variation for exposed/rusted metal) instead of flat masks.
"""
from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROD = ROOT / "Assets" / "ProductionArt"
TEX = PROD / "Materials" / "Textures"
DOCS = PROD / "Docs"
REPORT = DOCS / "surface_weathering.json"

# metallic_min/max are only non-zero for metal. smooth_min/max map to the
# packed alpha channel used by Unity's metallic/smoothness workflow.
PROFILES = {
    "wood":  {"metallic": (0, 0),   "smooth": (34, 82),  "damp": 0.16},
    "rope":  {"metallic": (0, 0),   "smooth": (24, 62),  "damp": 0.13},
    "tarp":  {"metallic": (0, 0),   "smooth": (62, 132), "damp": 0.22},
    "metal": {"metallic": (142, 230),"smooth": (72, 154), "damp": 0.11},
    "stone": {"metallic": (0, 0),   "smooth": (24, 66),  "damp": 0.17},
    "leaf":  {"metallic": (0, 0),   "smooth": (30, 82),  "damp": 0.18},
    "cloth": {"metallic": (0, 0),   "smooth": (22, 58),  "damp": 0.12},
    "mud":   {"metallic": (0, 0),   "smooth": (30, 112), "damp": 0.28},
    "fire":  {"metallic": (0, 0),   "smooth": (176, 228),"damp": 0.00},
    "char":  {"metallic": (0, 0),   "smooth": (12, 44),  "damp": 0.08},
    "water": {"metallic": (0, 0),   "smooth": (202, 246),"damp": 0.05},
}


def seed_for(label: str) -> int:
    return int(hashlib.sha256(("ProjectOEN.SurfaceWeather.v1:" + label).encode()).hexdigest()[:16], 16)


def tileable_noise(size: int, cells: int, seed: int) -> Image.Image:
    """Create deterministic low-frequency noise whose opposite edges match."""
    rnd = random.Random(seed)
    lattice = [[rnd.randrange(256) for _ in range(cells)] for _ in range(cells)]
    small = Image.new("L", (cells + 1, cells + 1))
    px = small.load()
    for y in range(cells + 1):
        sy = y % cells
        for x in range(cells + 1):
            px[x, y] = lattice[sy][x % cells]
    # One extra periodic lattice sample lets bicubic interpolation meet cleanly.
    return small.resize((size, size), Image.Resampling.BICUBIC)


def weather_field(name: str, size: int) -> Image.Image:
    broad = tileable_noise(size, 12, seed_for(name + ":broad")).filter(ImageFilter.GaussianBlur(size / 96))
    fine = tileable_noise(size, 32, seed_for(name + ":fine")).filter(ImageFilter.GaussianBlur(size / 256))
    mixed = Image.blend(broad, fine, 0.34)
    return ImageEnhance.Contrast(mixed).enhance(1.22)


def remap_luma(source: Image.Image, lo: int, hi: int) -> Image.Image:
    span = hi - lo
    return source.point(lambda v: lo + (v * span // 255))


def write_mask(name: str, field: Image.Image) -> dict[str, int]:
    profile = PROFILES[name]
    mask_path = TEX / f"{name}_metallic_smoothness.png"
    if not mask_path.exists():
        raise FileNotFoundError(mask_path)

    field_512 = field.resize((512, 512), Image.Resampling.BICUBIC)
    smooth = remap_luma(field_512, *profile["smooth"])

    if name == "metal":
        # Rust/wear patches are less metallic than intact exposed metal.
        inv = ImageChops.invert(field_512)
        metallic = remap_luma(inv, *profile["metallic"])
    else:
        metallic = Image.new("L", (512, 512), 0)

    packed = Image.merge("RGBA", (metallic, metallic, metallic, smooth))
    packed.save(mask_path, compress_level=6)

    mlo, mhi = metallic.getextrema()
    slo, shi = smooth.getextrema()
    return {
        "metallic_min": int(mlo), "metallic_max": int(mhi),
        "smoothness_min": int(slo), "smoothness_max": int(shi),
    }


def tint_by_mask(image: Image.Image, field: Image.Image, tint: tuple[int, int, int], strength: float) -> Image.Image:
    if strength <= 0:
        return image
    # Broad high-field regions become damp/worn without crushing the base art.
    mask = field.point(lambda v: max(0, min(255, int((v - 92) * strength * 2.25))))
    layer = Image.new("RGB", image.size, tint)
    return Image.composite(layer, image, mask)


def add_material_marks(name: str, image: Image.Image) -> Image.Image:
    out = image.copy()
    draw = ImageDraw.Draw(out, "RGBA")
    rnd = random.Random(seed_for(name + ":marks"))
    w, h = out.size

    if name == "metal":
        for _ in range(52):
            x, y = rnd.randrange(w), rnd.randrange(h)
            rx, ry = rnd.randint(5, 24), rnd.randint(3, 15)
            draw.ellipse((x-rx, y-ry, x+rx, y+ry), fill=(139, 69, 37, rnd.randint(22, 72)))
        for _ in range(28):
            x, y = rnd.randrange(w), rnd.randrange(h)
            draw.line((x, y, (x+rnd.randint(35, 150)) % w, y+rnd.randint(-3, 3)),
                      fill=(210, 218, 213, rnd.randint(20, 52)), width=1)
    elif name == "wood":
        for _ in range(28):
            x, y = rnd.randrange(w), rnd.randrange(h)
            ln = rnd.randint(45, 190)
            draw.line((x, y, min(w-1, x+ln), y+rnd.randint(-5, 5)),
                      fill=(45, 27, 17, rnd.randint(24, 65)), width=rnd.randint(1, 3))
    elif name == "tarp":
        for _ in range(18):
            x, y = rnd.randrange(w), rnd.randrange(h)
            draw.arc((x-70, y-28, x+70, y+28), 185, 350,
                     fill=(18, 32, 38, rnd.randint(18, 46)), width=2)
    elif name == "mud":
        for _ in range(26):
            x, y = rnd.randrange(w), rnd.randrange(h)
            rx, ry = rnd.randint(18, 75), rnd.randint(8, 35)
            draw.ellipse((x-rx, y-ry, x+rx, y+ry), fill=(35, 42, 37, rnd.randint(12, 42)))
    elif name in ("stone", "char"):
        for _ in range(24):
            x, y = rnd.randrange(w), rnd.randrange(h)
            draw.line((x, y, x+rnd.randint(-45, 45), y+rnd.randint(18, 90)),
                      fill=(30, 31, 29, rnd.randint(12, 36)), width=1)
    return out


def weather_albedo(name: str, field: Image.Image) -> None:
    path = TEX / f"{name}_albedo.png"
    if not path.exists():
        raise FileNotFoundError(path)
    with Image.open(path) as source:
        base = source.convert("RGB")

    profile = PROFILES[name]
    tint = {
        "wood": (65, 51, 39), "rope": (108, 94, 72), "tarp": (25, 50, 61),
        "metal": (66, 72, 70), "stone": (67, 75, 70), "leaf": (45, 69, 45),
        "cloth": (69, 61, 53), "mud": (45, 45, 36), "char": (25, 27, 26),
        "water": (48, 85, 103), "fire": (226, 102, 30),
    }[name]
    out = tint_by_mask(base, field, tint, profile["damp"])
    out = add_material_marks(name, out)
    out.save(path, compress_level=6)


def main() -> int:
    DOCS.mkdir(parents=True, exist_ok=True)
    results = {}
    for name in PROFILES:
        field = weather_field(name, 1024)
        weather_albedo(name, field)
        results[name] = write_mask(name, field)

    report = {
        "version": 1,
        "material_count": len(PROFILES),
        "materials": results,
        "notes": "Deterministic damp/wear albedo variation and non-flat packed smoothness; metal also varies metallic response.",
    }
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Weathered {len(PROFILES)} Project OEN shared materials without changing Unity paths/GUIDs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
