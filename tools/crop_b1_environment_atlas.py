#!/usr/bin/env python3
"""Crop the retained B1 ImageGen atlas into deterministic material sources."""

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
TEXTURES = ROOT / "source_art" / "environment" / "b1" / "production" / "textures"
SOURCE = TEXTURES / "MAT_B1_ENVIRONMENT_ATLAS_SOURCE_001.png"

CROPS = {
    "MAT_JUNGLE_FOLIAGE_001.png": (0, 0),
    "MAT_RAVINE_ROCK_001.png": (1, 0),
    "MAT_RIDGE_GROUND_001.png": (0, 1),
    "MAT_ROUTE_MARKER_001.png": (1, 1),
}


def main() -> None:
    with Image.open(SOURCE) as atlas:
        if atlas.width != atlas.height or atlas.width % 2:
            raise SystemExit(f"expected an even square atlas, got {atlas.size}")
        half = atlas.width // 2
        for filename, (column, row) in CROPS.items():
            crop = atlas.crop((column * half, row * half, (column + 1) * half, (row + 1) * half))
            output = TEXTURES / filename
            crop.save(output, format="PNG", optimize=True)
            print(output.relative_to(ROOT))


if __name__ == "__main__":
    main()
