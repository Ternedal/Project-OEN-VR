#!/usr/bin/env python3
"""Generate production source geometry for the A4 Camp ground and states."""

from __future__ import annotations

import math
from pathlib import Path

from generate_b1_environment_meshes import lowpoly_mass, path_slab
from generate_camp_source_meshes import Obj


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "source_art" / "environment" / "a4" / "production"

MTL = """# A4 Camp environment materials; final Unity shaders remain runtime-owned.
newmtl MAT_DRY_SAND
Kd 0.64 0.53 0.36
map_Kd textures/MAT_CAMP_DRY_SAND_001.png
newmtl MAT_WET_SAND
Kd 0.31 0.30 0.26
map_Kd textures/MAT_CAMP_WET_SAND_001.png
newmtl MAT_STORM_GROUND
Kd 0.24 0.26 0.25
map_Kd textures/MAT_CAMP_STORM_GROUND_001.png
newmtl MAT_DRIFTWOOD
Kd 0.37 0.29 0.21
map_Kd textures/MAT_CAMP_DRIFTWOOD_001.png
newmtl MAT_ROCK
Kd 0.28 0.32 0.34
map_Kd ../../b1/production/textures/MAT_RAVINE_ROCK_001.png
newmtl MAT_MARKER
Kd 0.66 0.57 0.39
map_Kd ../../b1/production/textures/MAT_ROUTE_MARKER_001.png
newmtl MAT_CANVAS
Kd 0.66 0.59 0.43
map_Kd ../../../props/a2/production/textures/MAT_AGED_CANVAS_001.png
"""


def asset(name: str) -> Obj:
    return Obj(name, OUT, MTL)


def terrain(
    o: Obj,
    name: str,
    width: float,
    depth: float,
    x_steps: int,
    z_steps: int,
) -> None:
    points = []
    for z_index in range(z_steps + 1):
        z = -depth / 2 + depth * z_index / z_steps
        for x_index in range(x_steps + 1):
            x = -width / 2 + width * x_index / x_steps
            edge = (abs(x) / (width / 2)) ** 3 + (abs(z) / (depth / 2)) ** 3
            y = 0.025 * math.sin(x * 1.3) * math.cos(z * 1.1) - 0.035 * max(0, edge - 1)
            points.append((x, y, z))
    faces = []
    row = x_steps + 1
    for z_index in range(z_steps):
        for x_index in range(x_steps):
            start = z_index * row + x_index
            faces.append((start, start + 1, start + row + 1, start + row))
    o._part(name, points, faces)


def camp_ground() -> Path:
    o = asset("ENV_CAMP_GROUND_001")
    o.material("MAT_DRY_SAND")
    terrain(o, "BroadDryCampGround", 12.0, 10.5, 12, 10)
    for name, x, z, radius in (
        ("FireInteractionCalmZone", 0.0, 0.0, 1.35),
        ("ShelterWorkClearance", -3.1, 2.2, 1.25),
        ("PlanningStableStance", 3.1, 0.8, 1.20),
        ("SuppliesReadableZone", 3.25, 2.75, 0.95),
        ("WreckIntroZone", -2.7, -3.25, 1.35),
        ("SignalReachZone", 1.65, -3.85, 1.10),
    ):
        o.cylinder(name, (x, 0.025, z), radius, 0.05, 18)
    o.material("MAT_WET_SAND")
    path_slab(o, "SeaFacingWetBand", (-5.8, -4.95), (5.8, -4.95), 0.72, 0.035)
    o.material("MAT_DRY_SAND")
    for index, (start, end, width) in enumerate((
        ((0,0),(-3.1,2.2),.78),((0,0),(3.1,.8),.78),((0,0),(-2.7,-3.25),.82),
        ((0,0),(1.65,-3.85),.82),((0,0),(0,4.65),.92),((-3.1,2.2),(3.25,2.75),.62)
    ), 1):
        path_slab(o, f"ReadableCampRoute_{index}", start, end, width, 0.055)
    return o.write()


def beach_camp() -> Path:
    o = asset("ENV_BEACH_CAMP_001")
    o.material("MAT_MARKER")
    stations = (
        ("FireCentralSightlineAnchor",0,0,.72),
        ("ShelterLandmarkSocket",-3.1,2.2,.90),
        ("PlanTableLandmarkSocket",3.1,.8,.82),
        ("SuppliesLandmarkSocket",3.25,2.75,.68),
        ("HeavyCrateLandmarkSocket",-1.3,-2.3,.75),
        ("WreckLandmarkSocket",-3.0,-3.55,.90),
        ("SignalSeaLandmarkSocket",1.65,-3.85,.72),
    )
    for name, x, z, radius in stations:
        o.torus(name, (x,.075,z), radius, .045, 16, 5)
    o.beam("JungleExitLeft", (-.75,0,4.65), (-.75,1.8,4.65), .11)
    o.beam("JungleExitRight", (.75,0,4.65), (.75,1.8,4.65), .11)
    o.beam("JungleExitHeader", (-.8,1.8,4.65), (.8,1.8,4.65), .13)
    o.beam("SeaSignalDirectionLeft", (1.18,0,-4.05), (1.65,2.1,-4.05), .10)
    o.beam("SeaSignalDirectionRight", (2.12,0,-4.05), (1.65,2.1,-4.05), .10)
    o.beam("SeaSignalReadableCrossbar", (1.38,1.25,-4.05), (1.92,1.25,-4.05), .09)
    o.material("MAT_DRIFTWOOD")
    clutter = [((-5.0,.14,-3.8),(-4.0,.18,-3.2)),((-4.7,.13,3.4),(-3.7,.15,3.8)),((4.0,.15,3.8),(5.0,.14,3.1)),((4.2,.12,-3.7),(5.2,.13,-3.2))]
    for index, (start, end) in enumerate(clutter, 1):
        o.beam(f"EdgeOnlyDriftwood_{index}", start, end, .18)
    o.material("MAT_ROCK")
    for index, (x, z, scale) in enumerate(((-5.2,-1.8,.7),(-4.8,1.4,.8),(4.9,-1.6,.75),(5.1,1.7,.65),(-2.1,4.5,.6),(2.2,4.4,.7)), 1):
        lowpoly_mass(o, f"EdgeOnlyRock_{index}", (x,.20,z), (.42*scale,.24*scale,.38*scale), 6)
    return o.write()


def storm_camp() -> Path:
    o = asset("ENV_STORM_CAMP_001")
    o.material("MAT_STORM_GROUND")
    wet_paths = [((-5.0,-3.8),(-1.1,-2.8),1.3),((-3.8,2.9),(-.7,1.6),1.15),((1.0,3.7),(4.5,2.1),1.2),((2.0,-3.8),(5.1,-2.5),1.3)]
    for index, (start, end, width) in enumerate(wet_paths, 1):
        path_slab(o, f"LargeWetGroundPatch_{index}", start, end, width, .045)
    for index, (x, z, radius) in enumerate(((-2.1,-1.0,.55),(.9,2.0,.72),(3.2,-1.3,.62),(-3.6,1.0,.48)), 1):
        o.cylinder(f"BroadStormPuddle_{index}", (x,.055,z), radius, .025, 18)
    o.material("MAT_DRIFTWOOD")
    debris = [((-4.0,.16,-.5),(-3.1,.27,-.15)),((-1.0,.15,3.8),(-.1,.30,3.2)),((3.1,.14,3.4),(4.1,.28,2.8)),((3.5,.13,-3.4),(4.4,.25,-2.8))]
    for index, (start, end) in enumerate(debris, 1):
        o.beam(f"LooseReadableDebris_{index}", start, end, .14)
    o.material("MAT_CANVAS")
    o.box("TornShelterCanvasScrap", (-3.7,.10,1.45), (1.05,.035,.55))
    o.box("LooseSignalCanvasScrap", (2.45,.08,-3.95), (.72,.03,.42))
    o.material("MAT_MARKER")
    path_slab(o, "PreservedFireReadability", (-.95,0),(.95,0), .62, .075)
    path_slab(o, "PreservedSignalFinalApproach", (0,-.45),(1.65,-3.65), .65, .075)
    return o.write()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    files = [camp_ground(), beach_camp(), storm_camp()]
    print("\n".join(str(path.relative_to(ROOT)) for path in files))


if __name__ == "__main__":
    main()
