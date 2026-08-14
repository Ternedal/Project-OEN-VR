#!/usr/bin/env python3
"""Deterministic refinement pass for Project ØEN 2D production sprites.

The broad generator guarantees canonical asset/state coverage. This pass adds a
coherent diegetic visual system without turning the files into contact sheets:
- wrist/status: cool metal/teal bezel language;
- planning board: warm handmade wood/brass language;
- resources: compact rugged inventory-token treatment;
- interaction markers: high-contrast world-space readability;
- menus/branding: restrained framing;
- state variants receive small semantic pips/notches so separate files also read
  as genuinely separate states;
- VFX support textures are intentionally left structurally untouched.

Every source remains one Unity-importable PNG per state/variant.
"""
from __future__ import annotations

import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROD = ROOT / "Assets" / "ProjectOEN" / "ProductionArt"
MANIFEST = PROD / "Docs" / "production_art_manifest.json"
REPORT = PROD / "Docs" / "ui_sprite_refinement.json"

PALETTE = {
    "ink": (22, 28, 28, 255),
    "teal": (60, 113, 124, 255),
    "cold": (112, 170, 190, 255),
    "ivory": (235, 224, 194, 255),
    "gold": (194, 146, 70, 255),
    "rust": (145, 75, 43, 255),
    "wood": (116, 79, 47, 255),
    "danger": (164, 58, 45, 255),
}

SKIP_CATEGORIES = {"VFX support graphics"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def alpha_outline(alpha: Image.Image, radius: int) -> Image.Image:
    size = radius * 2 + 1
    expanded = alpha.filter(ImageFilter.MaxFilter(size))
    return ImageChops.subtract(expanded, alpha)


def alpha_inner_edge(alpha: Image.Image, radius: int) -> Image.Image:
    size = radius * 2 + 1
    eroded = alpha.filter(ImageFilter.MinFilter(size))
    return ImageChops.subtract(alpha, eroded)


def category_style(category: str):
    if category == "Wrist UI & player status":
        return PALETTE["teal"], PALETTE["cold"], True
    if category == "Planning board & phase UI":
        return PALETTE["wood"], PALETTE["gold"], True
    if category == "Resource icons & inventory support":
        return PALETTE["wood"], PALETTE["ivory"], False
    if category == "Interaction markers & helper UI":
        return PALETTE["teal"], PALETTE["ivory"], False
    if category == "Menus & meta screens":
        return PALETTE["ink"], PALETTE["gold"], True
    if category == "Branding & identity":
        return PALETTE["ink"], PALETTE["ivory"], False
    return PALETTE["ink"], PALETTE["gold"], False


def state_accent(variant: str, default):
    v = variant.lower().replace("-", "_")
    if any(k in v for k in ("critical", "danger", "failed", "damaged", "storm", "low")):
        return PALETTE["danger"]
    if any(k in v for k in ("active", "selected", "highlighted", "placed", "ready", "good", "valid", "full")):
        return PALETTE["gold"]
    if any(k in v for k in ("hover", "preview", "wet", "freezing", "rain", "reconnecting")):
        return PALETTE["cold"]
    return default


def deterministic_grain(size, seed: str) -> Image.Image:
    """Small seeded noise tile; avoids nondeterministic CI output churn."""
    rnd = random.Random(hashlib.sha256(seed.encode("utf-8")).digest())
    tile = Image.new("L", (128, 128))
    tile.putdata([max(0, min(255, int(rnd.gauss(128, 24)))) for _ in range(128 * 128)])
    return tile.resize(size, Image.Resampling.BILINEAR)


def semantic_state_overlay(alpha: Image.Image, variant: str, accent, seed: str) -> Image.Image:
    """Add subtle physical-state cues inside the existing visible footprint."""
    w, h = alpha.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    bbox = alpha.getbbox()
    if bbox is None:
        return overlay

    x0, y0, x1, y1 = bbox
    bw = max(1, x1 - x0)
    bh = max(1, y1 - y0)
    v = variant.lower().replace("-", "_")
    r = max(3, min(w, h) // 95)
    spacing = r * 3
    cy = y1 - max(r * 3, bh // 12)
    cx = x1 - max(r * 4, bw // 10)

    # Human-readable semantic cue.
    count = None
    if v in ("single", "light", "primary", "p1", "1_digit"):
        count = 1
    elif v in ("half", "medium", "secondary", "p2", "2_digit"):
        count = 2
    elif v in ("stack", "bundle", "heavy", "high", "full"):
        count = 3

    if count is not None:
        start = cx - (count - 1) * spacing // 2
        for i in range(count):
            x = start + i * spacing
            d.ellipse((x-r, cy-r, x+r, cy+r), fill=accent, outline=PALETTE["ink"], width=max(1, r // 3))
    elif v == "empty":
        d.ellipse((cx-r*2, cy-r*2, cx+r*2, cy+r*2), outline=accent, width=max(2, r // 2))
    elif v == "coil":
        d.ellipse((cx-r*3, cy-r*3, cx+r*3, cy+r*3), outline=accent, width=max(2, r // 2))
        d.ellipse((cx-r, cy-r, cx+r, cy+r), outline=accent, width=max(1, r // 3))
    elif v in ("selected", "highlighted"):
        d.polygon(((cx, cy-r*3), (cx+r*3, cy), (cx, cy+r*3), (cx-r*3, cy)), fill=accent)
    elif v in ("placed", "valid", "ready", "active"):
        d.line((cx-r*3, cy, cx-r, cy+r*2, cx+r*4, cy-r*3), fill=accent, width=max(3, r))
    elif v in ("offline", "off", "inactive", "paused"):
        d.line((cx-r*3, cy, cx+r*3, cy), fill=accent, width=max(3, r))
    elif any(k in v for k in ("critical", "danger", "failed", "damaged", "storm")):
        d.line((cx-r*3, cy-r*3, cx+r*3, cy+r*3), fill=accent, width=max(3, r))
        d.line((cx+r*3, cy-r*3, cx-r*3, cy+r*3), fill=accent, width=max(3, r))

    # Eight tiny state notches encode the variant deterministically. They are a
    # consistent industrial/handmade UI motif and guarantee that distinct states
    # cannot silently collapse to byte-identical images.
    code = hashlib.sha256((seed + ":" + v).encode("utf-8")).digest()[0]
    notch_y = y0 + max(r * 2, bh // 12)
    notch_x = x0 + max(r * 3, bw // 10)
    notch_w = max(2, r // 2)
    notch_gap = max(2, r)
    for bit in range(8):
        if code & (1 << bit):
            x = notch_x + bit * (notch_w + notch_gap)
            d.rounded_rectangle((x, notch_y-r, x+notch_w, notch_y+r), max(1, notch_w//2), fill=accent)

    # Never paint outside the original visible sprite footprint.
    overlay.putalpha(ImageChops.multiply(overlay.getchannel("A"), alpha))
    return overlay


def add_edge_language(im: Image.Image, category: str, variant: str, panel_like: bool, seed: str) -> Image.Image:
    rgba = im.convert("RGBA")
    alpha = rgba.getchannel("A")
    w, h = rgba.size
    base, accent0, hardware = category_style(category)
    accent = state_accent(variant, accent0)

    outline = alpha_outline(alpha, max(2, min(w, h) // 220))
    outline = outline.point(lambda p: min(150, int(p * 0.58)))
    outside = Image.new("RGBA", rgba.size, base)
    outside.putalpha(outline)
    out = Image.alpha_composite(outside, rgba)

    inner = alpha_inner_edge(alpha, max(1, min(w, h) // 320))
    inner = inner.point(lambda p: min(105, int(p * 0.42)))
    rim = Image.new("RGBA", rgba.size, accent)
    rim.putalpha(inner)
    out = Image.alpha_composite(out, rim)

    grain = deterministic_grain(rgba.size, seed)
    strength = 0.055 if panel_like else 0.032
    grain_alpha = grain.point(lambda p: int(p * strength))
    grain_alpha = ImageChops.multiply(grain_alpha, alpha)
    grain_layer = Image.new("RGBA", rgba.size, PALETTE["ivory"])
    grain_layer.putalpha(grain_alpha)
    out = Image.alpha_composite(out, grain_layer)

    if hardware:
        overlay = Image.new("RGBA", rgba.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)
        r = max(3, min(w, h) // 85)
        inset_x = max(18, w // 12)
        inset_y = max(18, h // 10)
        for x, y in ((inset_x, inset_y), (w-inset_x, inset_y),
                     (inset_x, h-inset_y), (w-inset_x, h-inset_y)):
            sample_x = max(0, min(w-1, x)); sample_y = max(0, min(h-1, y))
            if alpha.getpixel((sample_x, sample_y)) > 24:
                d.ellipse((x-r, y-r, x+r, y+r), fill=PALETTE["gold"], outline=PALETTE["ink"], width=max(1, r//3))
                d.ellipse((x-r//3, y-r//3, x+r//3, y+r//3), fill=(235, 220, 177, 220))
        overlay.putalpha(ImageChops.multiply(overlay.getchannel("A"), alpha))
        out = Image.alpha_composite(out, overlay)

    out = Image.alpha_composite(out, semantic_state_overlay(alpha, variant, accent, seed))
    return out


def main() -> int:
    if not MANIFEST.exists():
        raise SystemExit(f"Missing production-art manifest: {MANIFEST}")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries = [e for e in manifest if e.get("kind") == "sprite"]
    processed = []
    by_category = Counter()
    by_asset = defaultdict(int)

    for e in entries:
        path = ROOT / e["path"]
        if not path.exists():
            raise SystemExit(f"Missing production sprite: {path.relative_to(ROOT)}")
        category = str(e.get("category", ""))
        variant = str(e.get("variant", "default"))
        aid = str(e.get("asset_id", ""))
        before = sha256(path)

        if category not in SKIP_CATEGORIES:
            with Image.open(path) as src:
                im = src.convert("RGBA")
            panel_like = im.width > im.height or any(k in str(e.get("name", "")).lower()
                                                    for k in ("panel", "board", "frame", "screen", "track", "card"))
            refined = add_edge_language(im, category, variant, panel_like, aid + ":" + variant)
            refined.save(path, compress_level=6)

        after = sha256(path)
        processed.append({
            "asset_id": aid,
            "category": category,
            "variant": variant,
            "path": e["path"],
            "changed_by_refinement": before != after,
            "sha256": after,
        })
        by_category[category] += 1
        by_asset[aid] += 1

    report = {
        "sprite_count": len(entries),
        "refined_count": sum(1 for e in processed if e["changed_by_refinement"]),
        "intentionally_unmodified_vfx_count": sum(1 for e in entries if e.get("category") in SKIP_CATEGORIES),
        "category_counts": dict(sorted(by_category.items())),
        "asset_id_count": len(by_asset),
        "entries": processed,
    }
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Refined {report['refined_count']} of {len(entries)} production sprites; "
          f"left {report['intentionally_unmodified_vfx_count']} VFX-support sprites structurally untouched")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
