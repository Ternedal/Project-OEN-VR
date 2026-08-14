#!/usr/bin/env python3
"""Crop the retained A4 camp-ground ImageGen atlas into material sources."""

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
TEXTURES = ROOT / "source_art" / "environment" / "a4" / "production" / "textures"
SOURCE = TEXTURES / "MAT_A4_CAMP_GROUND_ATLAS_SOURCE_001.png"

CROPS = {
    "MAT_CAMP_DRY_SAND_001.png": (0, 0),
    "MAT_CAMP_WET_SAND_001.png": (1, 0),
    "MAT_CAMP_STORM_GROUND_001.png": (0, 1),
    "MAT_CAMP_DRIFTWOOD_001.png": (1, 1),
}


def main() -> None:
    with Image.open(SOURCE) as atlas:
        if atlas.width != atlas.height or atlas.width % 2:
            raise SystemExit(f"expected an even square atlas, got {atlas.size}")
        half = atlas.width // 2
        for filename, (column, row) in CROPS.items():
            output = TEXTURES / filename
            atlas.crop(
                (column * half, row * half, (column + 1) * half, (row + 1) * half)
            ).save(output, format="PNG", optimize=True)
            print(output.relative_to(ROOT))


if __name__ == "__main__":
    main()
