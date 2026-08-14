#!/usr/bin/env python3
"""Generate the neutral torso and player-readable glove source meshes."""

from __future__ import annotations

import math
from pathlib import Path

from generate_camp_source_meshes import Obj


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "source_art" / "avatar" / "base"
TEXTURE_ROOT = "../../props/a2/production/textures"


def material_library(accent: tuple[float, float, float]) -> str:
    accent_rgb = " ".join(f"{channel:.3f}" for channel in accent)
    return f"""# Identity-neutral Quest-friendly avatar source materials.
newmtl MAT_TORSO
Kd 0.31 0.34 0.33
map_Kd {TEXTURE_ROOT}/MAT_AGED_CANVAS_001.png
newmtl MAT_STRAP
Kd 0.18 0.21 0.20
map_Kd {TEXTURE_ROOT}/MAT_WORN_IRON_001.png
newmtl MAT_GLOVE
Kd 0.39 0.42 0.39
map_Kd {TEXTURE_ROOT}/MAT_AGED_CANVAS_001.png
newmtl MAT_ACCENT
Kd {accent_rgb}
map_Kd {TEXTURE_ROOT}/MAT_AGED_CANVAS_001.png
"""


def loft(o: Obj, name: str, rings: list[list[tuple[float, float, float]]]) -> None:
    """Add a closed four-sided loft with stable low-poly UVs."""
    points = [point for ring in rings for point in ring]
    faces: list[tuple[int, ...]] = [(3, 2, 1, 0)]
    for ring_index in range(len(rings) - 1):
        start = ring_index * 4
        next_start = start + 4
        for side in range(4):
            following = (side + 1) % 4
            faces.append((start + side, start + following, next_start + following, next_start + side))
    top = (len(rings) - 1) * 4
    faces.append((top, top + 1, top + 2, top + 3))
    o._part(name, points, faces)


def ring(x_half: float, y_half: float, z: float) -> list[tuple[float, float, float]]:
    return [
        (-x_half, -y_half, z),
        (x_half, -y_half, z),
        (x_half, y_half, z),
        (-x_half, y_half, z),
    ]


def torus_z(
    o: Obj,
    name: str,
    center: tuple[float, float, float],
    major: float,
    minor: float,
    major_steps: int = 12,
    minor_steps: int = 5,
) -> None:
    cx, cy, cz = center
    points = []
    for major_index in range(major_steps):
        angle = 2 * math.pi * major_index / major_steps
        for minor_index in range(minor_steps):
            cross_angle = 2 * math.pi * minor_index / minor_steps
            radius = major + minor * math.cos(cross_angle)
            points.append(
                (
                    cx + radius * math.cos(angle),
                    cy + radius * math.sin(angle),
                    cz + minor * math.sin(cross_angle),
                )
            )
    faces = []
    for major_index in range(major_steps):
        for minor_index in range(minor_steps):
            faces.append(
                (
                    major_index * minor_steps + minor_index,
                    ((major_index + 1) % major_steps) * minor_steps + minor_index,
                    ((major_index + 1) % major_steps) * minor_steps + (minor_index + 1) % minor_steps,
                    major_index * minor_steps + (minor_index + 1) % minor_steps,
                )
            )
    o._part(name, points, faces)


def torso() -> Path:
    o = Obj("CHR_TORSO_BASE_001", OUT, material_library((0.55, 0.45, 0.28)))
    o.material("MAT_TORSO")
    loft(
        o,
        "TorsoGroundingShell",
        [ring(0.18, 0.09, 0.00), ring(0.21, 0.10, 0.28), ring(0.19, 0.085, 0.50)],
    )
    o.box("LeftVestPanel", (-0.095, -0.103, 0.27), (0.17, 0.026, 0.38))
    o.box("RightVestPanel", (0.095, -0.103, 0.27), (0.17, 0.026, 0.38))
    o.material("MAT_STRAP")
    o.beam("LeftShoulderStrap", (-0.14, -0.116, 0.13), (-0.14, -0.103, 0.47), 0.048)
    o.beam("RightShoulderStrap", (0.14, -0.116, 0.13), (0.14, -0.103, 0.47), 0.048)
    o.box("ReadableHemBand", (0, -0.102, 0.065), (0.38, 0.03, 0.075))
    o.box("NeutralBackPlate", (0, 0.102, 0.29), (0.20, 0.025, 0.12))
    torus_z(o, "OpenNeckCollar", (0, 0, 0.505), 0.095, 0.018)
    return o.write()


def palm(o: Obj, prefix: str) -> None:
    loft(
        o,
        f"{prefix}_Palm",
        [ring(0.070, 0.036, 0.035), ring(0.092, 0.041, 0.215)],
    )


def glove_pair(name: str, accent: tuple[float, float, float], round_badge: bool) -> Path:
    o = Obj(name, OUT, material_library(accent))
    for side, thumb_sign in (("Left", -1), ("Right", 1)):
        o.material("MAT_GLOVE")
        palm(o, side)
        o.box(f"{side}_Cuff", (0, 0, -0.015), (0.15, 0.085, 0.105))
        finger_data = [(-0.067, 0.120), (-0.023, 0.157), (0.023, 0.168), (0.067, 0.139)]
        for index, (x, length) in enumerate(finger_data, 1):
            o.beam(
                f"{side}_Finger_{index}",
                (x, 0, 0.205),
                (x, 0, 0.205 + length),
                0.035,
            )
        o.beam(
            f"{side}_Thumb",
            (thumb_sign * 0.072, 0, 0.095),
            (thumb_sign * 0.145, 0, 0.185),
            0.045,
        )
        o.box(f"{side}_KnucklePad", (0, -0.045, 0.205), (0.17, 0.022, 0.065))
        o.material("MAT_ACCENT")
        if round_badge:
            o.cylinder(f"{side}_RoundPlayerBadge", (0, -0.051, -0.015), 0.032, 0.018, 12)
        else:
            o.box(f"{side}_SquarePlayerBadge", (0, -0.051, -0.015), (0.062, 0.018, 0.062))
    return o.write()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    files = [
        torso(),
        glove_pair("CHR_HAND_P1_001", (0.835, 0.604, 0.322), True),
        glove_pair("CHR_HAND_P2_001", (0.400, 0.455, 0.361), False),
    ]
    print("\n".join(str(path.relative_to(ROOT)) for path in files))


if __name__ == "__main__":
    main()
