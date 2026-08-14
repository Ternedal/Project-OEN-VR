#!/usr/bin/env python3
"""Validate the A4 Camp environment production source pack."""

from __future__ import annotations

import re
import struct
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "source_art" / "environment" / "a4" / "production"
TEXTURES = PACK / "textures"

EXPECTED = {
    "ENV_BEACH_CAMP_001": {
        "minimum_vertices": 650,
        "minimum_parts": 20,
        "bounds": ((10.0, 1.8, 8.5), (12.5, 3.0, 10.5)),
        "parts": {"FireCentralSightlineAnchor", "PlanTableLandmarkSocket", "SeaSignalReadableCrossbar", "JungleExitHeader"},
    },
    "ENV_CAMP_GROUND_001": {
        "minimum_vertices": 400,
        "minimum_parts": 14,
        "bounds": ((11.5, 0.08, 10.0), (13.0, 0.30, 11.5)),
        "parts": {"BroadDryCampGround", "FireInteractionCalmZone", "PlanningStableStance", "SeaFacingWetBand", "ReadableCampRoute_1"},
    },
    "ENV_STORM_CAMP_001": {
        "minimum_vertices": 220,
        "minimum_parts": 15,
        "bounds": ((9.5, 0.25, 8.0), (12.0, 0.60, 10.0)),
        "parts": {"LargeWetGroundPatch_1", "BroadStormPuddle_1", "TornShelterCanvasScrap", "PreservedFireReadability", "PreservedSignalFinalApproach"},
    },
}

EXPECTED_TEXTURES = {
    "MAT_A4_CAMP_GROUND_ATLAS_SOURCE_001.png": (1254, 1254),
    "MAT_CAMP_DRY_SAND_001.png": (627, 627),
    "MAT_CAMP_WET_SAND_001.png": (627, 627),
    "MAT_CAMP_STORM_GROUND_001.png": (627, 627),
    "MAT_CAMP_DRIFTWOOD_001.png": (627, 627),
}


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as stream:
        header = stream.read(24)
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG")
    return struct.unpack(">II", header[16:24])


def validate_mesh(name: str, contract: dict[str, object]) -> list[str]:
    errors: list[str] = []
    path = PACK / f"{name}.obj"
    if not path.is_file():
        return [f"{name}: OBJ missing"]
    vertices: list[tuple[float, float, float]] = []
    uv_count = face_count = 0
    parts: set[str] = set()
    materials: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("v "):
            vertices.append(tuple(map(float, line.split()[1:4])))
        elif line.startswith("vt "):
            uv_count += 1
        elif line.startswith("o "):
            parts.add(line[2:])
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
    if len(vertices) < int(contract["minimum_vertices"]):
        errors.append(f"{name}: only {len(vertices)} vertices")
    if len(parts) < int(contract["minimum_parts"]):
        errors.append(f"{name}: only {len(parts)} named parts")
    missing_parts = set(contract["parts"]) - parts
    if missing_parts:
        errors.append(f"{name}: missing semantic parts {sorted(missing_parts)}")
    if not uv_count or not face_count or not materials:
        errors.append(f"{name}: missing UV, face or material data")
    if vertices:
        bounds = tuple(
            max(vertex[axis] for vertex in vertices) - min(vertex[axis] for vertex in vertices)
            for axis in range(3)
        )
        minimum, maximum = contract["bounds"]
        for axis, value in enumerate(bounds):
            if not minimum[axis] <= value <= maximum[axis]:
                errors.append(
                    f"{name}: axis {axis} bound {value:.3f} outside "
                    f"{minimum[axis]}..{maximum[axis]} m"
                )
    mtl = PACK / f"{name}.mtl"
    if not mtl.is_file():
        errors.append(f"{name}: MTL missing")
    else:
        for relative_path in re.findall(
            r"^map_Kd\s+(.+)$", mtl.read_text(encoding="utf-8"), re.MULTILINE
        ):
            texture = PACK / relative_path.strip()
            if not texture.is_file() or texture.suffix.lower() != ".png":
                errors.append(f"{name}: missing texture {relative_path}")
    return errors


def main() -> int:
    errors: list[str] = []
    actual = {path.stem for path in PACK.glob("*.obj")}
    if actual != set(EXPECTED):
        errors.append(
            f"mesh set differs: missing={sorted(set(EXPECTED) - actual)}, "
            f"extra={sorted(actual - set(EXPECTED))}"
        )
    for name, contract in EXPECTED.items():
        errors.extend(validate_mesh(name, contract))
    actual_textures = {path.name for path in TEXTURES.glob("*.png")}
    if actual_textures != set(EXPECTED_TEXTURES):
        errors.append(
            f"texture set differs: missing={sorted(set(EXPECTED_TEXTURES) - actual_textures)}, "
            f"extra={sorted(actual_textures - set(EXPECTED_TEXTURES))}"
        )
    for filename, expected_size in EXPECTED_TEXTURES.items():
        path = TEXTURES / filename
        if not path.is_file():
            continue
        try:
            actual_size = png_size(path)
        except ValueError as error:
            errors.append(f"{filename}: {error}")
            continue
        if actual_size != expected_size:
            errors.append(f"{filename}: size {actual_size}, expected {expected_size}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(
        "A4 Camp environment sources OK: 3 OBJ/MTL assets and 5 PNG sources "
        "have valid bounds, UVs, semantic parts, links and dimensions."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
