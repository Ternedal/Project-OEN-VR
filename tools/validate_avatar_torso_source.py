#!/usr/bin/env python3
"""Validate the production avatar grounding and handwear source pack."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "source_art" / "avatar" / "base"
DATA = ROOT / "content" / "avatar" / "chr_torso_base.source.json"

EXPECTED = {
    "CHR_TORSO_BASE_001": {
        "minimum_vertices": 90,
        "minimum_parts": 7,
        "bounds": ((0.35, 0.18, 0.45), (0.55, 0.32, 0.65)),
        "parts": {"TorsoGroundingShell", "OpenNeckCollar", "LeftShoulderStrap", "RightShoulderStrap"},
    },
    "CHR_HAND_P1_001": {
        "minimum_vertices": 170,
        "minimum_parts": 18,
        "bounds": ((0.24, 0.07, 0.38), (0.42, 0.18, 0.55)),
        "parts": {"Left_Palm", "Right_Palm", "Left_RoundPlayerBadge", "Right_RoundPlayerBadge"},
    },
    "CHR_HAND_P2_001": {
        "minimum_vertices": 100,
        "minimum_parts": 18,
        "bounds": ((0.24, 0.07, 0.38), (0.42, 0.18, 0.55)),
        "parts": {"Left_Palm", "Right_Palm", "Left_SquarePlayerBadge", "Right_SquarePlayerBadge"},
    },
}


def validate_mesh(name: str, contract: dict[str, object]) -> list[str]:
    errors: list[str] = []
    obj = PACK / f"{name}.obj"
    if not obj.is_file():
        return [f"{name}: OBJ missing"]
    vertices: list[tuple[float, float, float]] = []
    uv_count = face_count = 0
    parts: set[str] = set()
    materials: set[str] = set()
    for line in obj.read_text(encoding="utf-8").splitlines():
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
    errors = []
    for name, contract in EXPECTED.items():
        errors.extend(validate_mesh(name, contract))

    data = json.loads(DATA.read_text(encoding="utf-8"))
    if data.get("status") != "production-source-ready-unity-pending":
        errors.append("bad torso contract status")
    product_intent = data.get("productIntent", {})
    if product_intent.get("mustNotRequire") != "Meta Avatar dependency":
        errors.append("Meta Avatar independence not explicit")
    if set(product_intent.get("trackedParts", [])) != {"head", "left hand", "right hand"}:
        errors.append("tracked part contract unexpected")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(
        "Avatar production sources OK: torso plus two player glove pairs have "
        "valid silhouettes, UVs, semantic parts, materials and ownership boundaries."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
