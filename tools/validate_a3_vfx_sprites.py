#!/usr/bin/env python3
"""Validate the deterministic A3 production sprite sources without Pillow."""

from __future__ import annotations

import hashlib
import json
import struct
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "source_art" / "vfx" / "a3" / "production"
METADATA = PACK / "VFX_SPRITE_LAYOUT.source.json"

EXPECTED = {
    "VFX_FIRE_EMBERS_001.png": "93ccb0b0a725b0a09537707ed5a4b9890abc1229285c41c9158451b083eda4b9",
    "VFX_FIRE_SMOKE_001.png": "543301afb99c5497bb64773327df41999c1691f2322fb0e59f87b1b908b5973b",
    "VFX_IMPACT_001.png": "09781cebd57ebc199ae639fa918ab99364f6268dec9c6e9ee9d6a5d781ffd79b",
    "VFX_RAIN_001.png": "e4bfe7a11cc64a2f2219a03dca5f87cfd7c0711cbf4e69f24344104700d0e034",
    "VFX_ROPE_STRAIN_001.png": "0b2551e649feab2ddeaf378a2f976a501a8458270efa13c96e0205b816130049",
    "VFX_WETNESS_REFERENCE_001.png": "8197c1a4c2230c291943075fa8174dd11d54e5b97d9248afe6bc5fdd6459d839",
    "VFX_WIND_DEBRIS_001.png": "5bb1d602db4bc734b229efb85fc23293e64e5b6ab1c287a0a2c0034efbf7fd86",
}


def png_info(path: Path) -> tuple[int, int, int, int]:
    with path.open("rb") as stream:
        header = stream.read(26)
    if len(header) != 26 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError("invalid PNG/IHDR")
    width, height = struct.unpack(">II", header[16:24])
    return width, height, header[24], header[25]


def main() -> int:
    errors: list[str] = []
    actual = {path.name for path in PACK.glob("*.png")}
    if actual != set(EXPECTED):
        errors.append(
            f"sprite set differs: missing={sorted(set(EXPECTED) - actual)}, "
            f"extra={sorted(actual - set(EXPECTED))}"
        )
    for filename, expected_hash in EXPECTED.items():
        path = PACK / filename
        if not path.is_file():
            continue
        try:
            width, height, bit_depth, color_type = png_info(path)
        except ValueError as error:
            errors.append(f"{filename}: {error}")
            continue
        if (width, height) != (512, 512):
            errors.append(f"{filename}: dimensions {(width, height)}, expected (512, 512)")
        if (bit_depth, color_type) != (8, 6):
            errors.append(f"{filename}: expected 8-bit RGBA PNG, got bit-depth/type {(bit_depth, color_type)}")
        actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            errors.append(f"{filename}: byte hash differs from deterministic generator output")

    if not METADATA.is_file():
        errors.append("sprite layout metadata missing")
    else:
        data = json.loads(METADATA.read_text(encoding="utf-8"))
        atlases = data.get("atlases", {})
        if set(atlases) != set(EXPECTED):
            errors.append("sprite layout metadata does not match PNG set")
        for filename, contract in atlases.items():
            if contract.get("cellPixels") not in ([256, 256], [512, 512]):
                errors.append(f"{filename}: unexpected cell size contract")
        if atlases.get("VFX_ROPE_STRAIN_001.png", {}).get("rule") != "secondary cue only":
            errors.append("rope strain secondary-cue boundary missing")
        if "Unity particle systems" not in data.get("runtimeBoundary", ""):
            errors.append("runtime ownership boundary missing")
    for filename in EXPECTED:
        svg = PACK.parent / filename.replace(".png", ".svg")
        if not svg.is_file():
            errors.append(f"{filename}: SVG source master missing")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("A3 VFX production sources OK: 7 deterministic 512px RGBA atlases, layout and ownership boundaries valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
