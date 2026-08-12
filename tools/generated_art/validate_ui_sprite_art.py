#!/usr/bin/env python3
"""Quality gate for Project ØEN production sprites after UI refinement."""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from PIL import Image, ImageStat

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROD = ROOT / "Assets" / "ProjectOEN" / "ProductionArt"
MANIFEST = PROD / "Docs" / "production_art_manifest.json"
REPORT = PROD / "Docs" / "ui_sprite_refinement.json"

FORBIDDEN = ("hunger", "thirst", "malik", "lighthouse", "firearm", "gun")
VFX_CATEGORY = "VFX support graphics"
REQUIRED_P0_IDS = {
    "UI-001","UI-002","UI-003","UI-004","UI-005","UI-006","UI-007","UI-008",
    "UI-012","UI-013","UI-014",
    "PL-001","PL-002","PL-003","PL-004","PL-005","PL-006","PL-008","PL-010","PL-011",
    "WK-001","WK-002","WK-003","WK-005","WK-010","WK-011","WK-013",
}


def inspect_png(path: Path):
    with Image.open(path) as src:
        rgba = src.convert("RGBA")
        alpha = rgba.getchannel("A")
        extrema = alpha.getextrema()
        bbox = alpha.getbbox()
        visible = sum(1 for p in alpha.getdata() if p > 8)
        opaque = sum(1 for p in alpha.getdata() if p > 220)
        rgb = rgba.convert("RGB")
        stat = ImageStat.Stat(rgb)
        variance = sum(stat.var)
        return rgba.size, extrema, bbox, visible, opaque, variance


def main() -> int:
    errors = []
    if not MANIFEST.exists():
        print("ERROR: production-art manifest missing")
        return 1
    if not REPORT.exists():
        print("ERROR: UI refinement report missing")
        return 1

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    sprites = [e for e in manifest if e.get("kind") == "sprite"]
    if len(sprites) != 206:
        errors.append(f"Expected 206 production sprites, found {len(sprites)}")
    if report.get("sprite_count") != len(sprites):
        errors.append("UI refinement report sprite count does not match production manifest")

    by_asset = defaultdict(list)
    by_category = Counter()
    paths = set()
    refined_report_paths = {e.get("path") for e in report.get("entries", [])}

    for e in sprites:
        aid = str(e.get("asset_id", ""))
        category = str(e.get("category", ""))
        variant = str(e.get("variant", "default"))
        rel = str(e.get("path", ""))
        name = str(e.get("name", ""))
        haystack = " ".join((aid, category, variant, rel, name)).lower()
        for token in FORBIDDEN:
            if token in haystack:
                errors.append(f"Forbidden/noncanonical UI token '{token}' in {rel}")

        if rel in paths:
            errors.append(f"Duplicate sprite manifest path: {rel}")
        paths.add(rel)
        if rel not in refined_report_paths:
            errors.append(f"Sprite missing from UI refinement report: {rel}")

        path = ROOT / rel
        if not path.exists():
            errors.append(f"Missing sprite: {rel}")
            continue
        meta = Path(str(path) + ".meta")
        if not meta.exists():
            errors.append(f"Missing .meta: {rel}")
        else:
            mt = meta.read_text(encoding="utf-8")
            for token in ("textureType: 8", "spriteMode: 1", "alphaIsTransparency: 1"):
                if token not in mt:
                    errors.append(f"Sprite importer contract missing '{token}': {rel}")

        try:
            size, extrema, bbox, visible, opaque, variance = inspect_png(path)
        except Exception as ex:
            errors.append(f"Unreadable PNG {rel}: {ex}")
            continue

        if size not in ((1024, 1024), (1024, 512)):
            errors.append(f"Unexpected production sprite dimensions {size}: {rel}")
        if bbox is None or visible < 5000:
            errors.append(f"Too little visible content: {rel}")
        if extrema[0] != 0:
            errors.append(f"Sprite lacks transparent gutter/background: {rel}")
        if extrema[1] < 180:
            errors.append(f"Sprite never reaches useful opacity: {rel}")
        if visible >= size[0] * size[1] * 0.97:
            errors.append(f"Sprite alpha covers essentially entire image: {rel}")
        if variance < 30:
            errors.append(f"Sprite RGB content is suspiciously flat: {rel}")

        by_asset[aid].append((variant, path.read_bytes(), category))
        by_category[category] += 1

    # Non-VFX state variants for one canonical asset must not collapse to
    # identical PNGs. VFX support is explicitly preserved by the UI refinement
    # pass and has its own production-art structural validation elsewhere.
    for aid, variants in by_asset.items():
        categories = {category for _, _, category in variants}
        if categories == {VFX_CATEGORY}:
            continue
        blobs = [blob for _, blob, _ in variants]
        if len(blobs) > 1 and len(set(blobs)) != len(blobs):
            dup_variants = [v for v, _, _ in variants]
            errors.append(f"{aid} contains byte-identical state variants: {dup_variants}")

    present_ids = set(by_asset)
    missing_p0 = REQUIRED_P0_IDS - present_ids
    if missing_p0:
        errors.append(f"Missing required P0 UI/interaction asset IDs: {sorted(missing_p0)}")

    expected_categories = {
        "Branding & identity",
        "Wrist UI & player status",
        "Planning board & phase UI",
        "Resource icons & inventory support",
        "Interaction markers & helper UI",
        "Menus & meta screens",
        VFX_CATEGORY,
    }
    if set(by_category) != expected_categories:
        errors.append(f"Sprite category coverage mismatch: {sorted(by_category)}")

    vfx_count = by_category.get(VFX_CATEGORY, 0)
    if report.get("intentionally_unmodified_vfx_count") != vfx_count:
        errors.append("UI refinement report VFX untouched count mismatch")
    if report.get("refined_count", 0) != len(sprites) - vfx_count:
        errors.append("Every non-VFX production sprite must be changed by the UI refinement pass")

    print("Project ØEN production UI/sprite QA")
    print(f"  sprites          : {len(sprites)}")
    print(f"  canonical IDs    : {len(by_asset)}")
    print(f"  refined non-VFX  : {report.get('refined_count', 0)}")
    print(f"  VFX preserved    : {vfx_count}")
    for category, count in sorted(by_category.items()):
        print(f"  {category:<35}: {count}")

    if errors:
        print(f"\nFAILED with {len(errors)} issue(s):")
        for e in errors:
            print(" - " + e)
        return 1

    print("\nPASS: all production sprites remain separate Unity assets and meet alpha/state/canonical UI gates.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
