#!/usr/bin/env python3
"""Validate the B1 shared world-item OBJ/MTL handoff without Unity."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "source_art" / "items" / "b1" / "production"

# Broad source bounds in metres. Runtime scale and grip setup remain Unity-owned.
EXPECTED = {
    "ITM_FIBER_BUNDLE_001": ((0.45, 0.18, 0.30), (0.70, 0.35, 0.55)),
    "ITM_FOOD_PARCEL_001": ((0.42, 0.42, 0.30), (0.65, 0.60, 0.50)),
    "ITM_GENERAL_SUPPLIES_001": ((0.48, 0.45, 0.28), (0.70, 0.65, 0.50)),
    "ITM_HERB_BUNDLE_001": ((0.50, 0.50, 0.15), (0.80, 0.80, 0.40)),
    "ITM_WOOD_BUNDLE_001": ((0.65, 0.25, 0.25), (0.95, 0.50, 0.50)),
}


def main() -> int:
    errors: list[str] = []
    actual = {path.stem for path in PACK.glob("*.obj")}
    if actual != set(EXPECTED):
        errors.append(
            f"mesh set differs: missing={sorted(set(EXPECTED) - actual)}, "
            f"extra={sorted(actual - set(EXPECTED))}"
        )

    for name, (minimum, maximum) in EXPECTED.items():
        path = PACK / f"{name}.obj"
        if not path.is_file():
            continue
        vertices: list[tuple[float, float, float]] = []
        uv_count = face_count = part_count = 0
        materials: set[str] = set()
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("v "):
                vertices.append(tuple(map(float, line.split()[1:4])))
            elif line.startswith("vt "):
                uv_count += 1
            elif line.startswith("o "):
                part_count += 1
            elif line.startswith("usemtl "):
                materials.add(line[7:])
            elif line.startswith("f "):
                face_count += 1
                for token in line.split()[1:]:
                    match = re.fullmatch(r"(\d+)/(\d+)", token)
                    if not match:
                        errors.append(f"{name}: unsupported face token {token}")
                        continue
                    vertex_index, uv_index = map(int, match.groups())
                    if not 1 <= vertex_index <= len(vertices) or not 1 <= uv_index <= uv_count:
                        errors.append(f"{name}: out-of-range face token {token}")
        if not vertices or not uv_count or not face_count or not part_count or not materials:
            errors.append(f"{name}: missing required OBJ geometry/UV/part/material data")
            continue
        bounds = tuple(max(v[axis] for v in vertices) - min(v[axis] for v in vertices) for axis in range(3))
        for axis, value in enumerate(bounds):
            if not minimum[axis] <= value <= maximum[axis]:
                errors.append(
                    f"{name}: axis {axis} bound {value:.3f} outside "
                    f"{minimum[axis]}..{maximum[axis]} m"
                )
        mtl = PACK / f"{name}.mtl"
        if not mtl.is_file():
            errors.append(f"{name}: missing MTL")
            continue
        for relative_path in re.findall(
            r"^map_Kd\s+(.+)$", mtl.read_text(encoding="utf-8"), re.MULTILINE
        ):
            texture = PACK / relative_path.strip()
            if not texture.is_file() or texture.suffix.lower() != ".png":
                errors.append(f"{name}: missing texture {relative_path}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(
        f"B1 source meshes OK: {len(EXPECTED)} OBJ/MTL assets, bounds, UVs, "
        "parts and texture links valid."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
