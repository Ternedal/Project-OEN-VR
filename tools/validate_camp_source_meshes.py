#!/usr/bin/env python3
"""Validate the production Camp OBJ/MTL/texture handoff without Unity."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "source_art" / "props" / "a2" / "production"

# Broad source bounds in metres. Runtime scale remains Unity-owned.
EXPECTED = {
    "ENV_WRECKAGE_001": ((3.0, 3.0, 2.7), (3.7, 3.7, 3.5)),
    "PRP_FIREPIT_001": ((0.75, 0.15, 0.75), (0.95, 0.35, 0.95)),
    "PRP_HEAVY_CRATE_001": ((0.9, 0.55, 0.55), (1.15, 0.8, 0.8)),
    "PRP_PLAN_TABLE_001": ((1.0, 0.8, 0.55), (1.3, 1.1, 0.75)),
    "PRP_RADIO_001": ((0.45, 0.7, 0.2), (0.75, 1.1, 0.5)),
    "PRP_SHELTER_BEAM_001": ((1.4, 0.2, 0.2), (1.8, 0.7, 0.6)),
    "PRP_SHELTER_FRAME_001": ((1.8, 1.5, 1.8), (2.7, 2.3, 2.7)),
    "PRP_SHELTER_ROPE_001": ((0.3, 0.1, 0.3), (1.1, 0.3, 0.8)),
    "PRP_SHELTER_TARP_001_TAUT": ((2.0, 0.05, 1.8), (3.1, 0.3, 2.7)),
    "PRP_SHELTER_TARP_001_TORN": ((2.0, 0.2, 1.8), (3.1, 0.7, 2.7)),
    "PRP_SHELTER_TARP_001_WET_SAG": ((2.0, 0.35, 1.8), (3.1, 0.8, 2.7)),
    "PRP_SIGNAL_FRAME_001": ((1.0, 1.5, 0.4), (1.5, 2.5, 0.8)),
    "PRP_SUPPLY_CRATE_001": ((0.65, 0.4, 0.4), (0.8, 0.7, 0.7)),
    "PRP_WIND_SHIELD_001": ((0.35, 0.3, 0.1), (0.6, 0.55, 0.35)),
}


def main() -> int:
    errors: list[str] = []
    actual = {p.stem for p in PACK.glob("*.obj")}
    if actual != set(EXPECTED):
        errors.append(f"mesh set differs: missing={sorted(set(EXPECTED)-actual)}, extra={sorted(actual-set(EXPECTED))}")

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
                    vi, ti = map(int, match.groups())
                    if not 1 <= vi <= len(vertices) or not 1 <= ti <= uv_count:
                        errors.append(f"{name}: out-of-range face token {token}")
        if not vertices or not uv_count or not face_count or not part_count or not materials:
            errors.append(f"{name}: missing required OBJ geometry/UV/part/material data")
            continue
        bounds = tuple(max(v[i] for v in vertices) - min(v[i] for v in vertices) for i in range(3))
        for axis, value in enumerate(bounds):
            if not minimum[axis] <= value <= maximum[axis]:
                errors.append(f"{name}: axis {axis} bound {value:.3f} outside {minimum[axis]}..{maximum[axis]} m")
        mtl = PACK / f"{name}.mtl"
        if not mtl.is_file():
            errors.append(f"{name}: missing MTL")
            continue
        for rel in re.findall(r"^map_Kd\s+(.+)$", mtl.read_text(encoding="utf-8"), re.MULTILINE):
            texture = PACK / rel.strip()
            if not texture.is_file() or texture.suffix.lower() != ".png":
                errors.append(f"{name}: missing texture {rel}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"Camp source meshes OK: {len(EXPECTED)} OBJ/MTL assets, bounds, UVs, parts and texture links valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
