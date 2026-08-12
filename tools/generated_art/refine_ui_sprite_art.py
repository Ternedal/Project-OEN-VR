#!/usr/bin/env python3
"""Deterministic refinement pass for Project ØEN 2D production sprites.

The broad generator guarantees canonical asset/state coverage. This pass adds a
coherent diegetic visual system without turning the files into contact sheets:
- wrist/status: cool metal/teal bezel language;
- planning board: warm handmade wood/brass language;
- resources: compact rugged inventory-token treatment;
- interaction markers: high-contrast world-space readability;
- menus/branding: restrained framing;
- VFX support textures are intentionally left structurally untouched.

Every source remains one Unity-importable PNG per state/variant.
"""
from __future__ import annotations

import hashlib
import json
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


def add_edge_language(im: Image.Image, category: str, variant: str, panel_like: bool) -> Image.Image:
    rgba = im.convert("RGBA")
    alpha = rgba.getchannel("A")
    w, h = rgba.size
    base, accent0, hardware = category_style(category)
    accent = state_accent(variant, accent0)

    # Soft exterior silhouette improves VR readability without painting into the
    # transparent background beyond a small controlled halo.
    outline = alpha_outline(alpha, max(2, min(w, h) // 220))
    outline = outline.point(lambda p: min(150, int(p * 0.58)))
    outside = Image.new("RGBA", rgba.size, base)
    outside.putalpha(outline)
    out = Image.alpha_composite(outside, rgba)

    # Warm/cool inner rim gives state feedback while preserving the source motif.
    inner = alpha_inner_edge(alpha, max(1, min(w, h) // 320))
    inner = inner.point(lambda p: min(105, int(p * 0.42)))
    rim = Image.new("RGBA", rgba.size, accent)
    rim.putalpha(inner)
    out = Image.alpha_composite(out, rim)

    # Category-specific material grain, clipped strictly to existing alpha.
    grain = Image.effect_noise((128, 128), 24).convert("L").resize(rgba.size, Image.Resampling.BILINEAR)
    strength = 0.055 if panel_like else 0.032
    grain_alpha = grain.point(lambda p: int(p * strength))
    grain_alpha = ImageChops.multiply(grain_alpha, alpha)
    grain_layer = Image.new("RGBA", rgba.size, PALETTE["ivory"])
    grain_layer.putalpha(grain_alpha)
    out = Image.alpha_composite(out, grain_layer)

    # Panels get four restrained brass/rivet cues. These are decorative pixels in
    # the sprite, not extra Unity objects/draw calls.
    if hardware:
        overlay = Image.new("RGBA", rgba.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)
        r = max(3, min(w, h) // 85)
        inset_x = max(18, w // 12)
        inset_y = max(18, h // 10)
        for x, y in ((inset_x, inset_y), (w-inset_x, inset_y),
                     (inset_x, h-inset_y), (w-inset_x, h-inset_y)):
            # Only show hardware where source alpha already exists nearby.
            sample_x = max(0, min(w-1, x)); sample_y = max(0, min(h-1, y))
            if alpha.getpixel((sample_x, sample_y)) > 24:
                d.ellipse((x-r, y-r, x+r, y+r), fill=PALETTE["gold"], outline=PALETTE["ink"], width=max(1, r//3))
                d.ellipse((x-r//3, y-r//3, x+r//3, y+r//3), fill=(235, 220, 177, 220))
        overlay.putalpha(ImageChops.multiply(overlay.getchannel("A"), alpha))
        out = Image.alpha_composite(out, overlay)

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
            refined = add_edge_language(im, category, variant, panel_like)
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
