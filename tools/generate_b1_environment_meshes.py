#!/usr/bin/env python3
"""Generate production source meshes for the B1 jungle, ravine and ridge set."""

from __future__ import annotations

import math
from pathlib import Path

from generate_camp_source_meshes import Obj


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "source_art" / "environment" / "b1" / "production"

MTL = """# B1 environment source materials; final Unity shaders remain runtime-owned.
newmtl MAT_FOLIAGE
Kd 0.20 0.31 0.18
map_Kd textures/MAT_JUNGLE_FOLIAGE_001.png
newmtl MAT_ROCK
Kd 0.28 0.32 0.34
map_Kd textures/MAT_RAVINE_ROCK_001.png
newmtl MAT_RIDGE
Kd 0.34 0.34 0.22
map_Kd textures/MAT_RIDGE_GROUND_001.png
newmtl MAT_MARKER
Kd 0.64 0.57 0.40
map_Kd textures/MAT_ROUTE_MARKER_001.png
newmtl MAT_WOOD
Kd 0.42 0.29 0.18
map_Kd ../../../props/a2/production/textures/MAT_WEATHERED_WOOD_001.png
newmtl MAT_ROPE
Kd 0.68 0.60 0.42
map_Kd ../../../props/a2/production/textures/MAT_AGED_CANVAS_001.png
"""


def asset(name: str) -> Obj:
    return Obj(name, OUT, MTL)


def path_slab(
    o: Obj,
    name: str,
    start: tuple[float, float],
    end: tuple[float, float],
    width: float,
    height: float = 0.08,
) -> None:
    ax, az = start
    bx, bz = end
    dx, dz = bx - ax, bz - az
    length = math.hypot(dx, dz)
    nx, nz = -dz / length * width / 2, dx / length * width / 2
    points = [
        (ax + nx, 0, az + nz), (ax - nx, 0, az - nz),
        (bx - nx, 0, bz - nz), (bx + nx, 0, bz + nz),
        (ax + nx, height, az + nz), (ax - nx, height, az - nz),
        (bx - nx, height, bz - nz), (bx + nx, height, bz + nz),
    ]
    faces = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    o._part(name, points, faces)


def tapered_cylinder(
    o: Obj,
    name: str,
    center: tuple[float, float, float],
    bottom_radius: float,
    top_radius: float,
    height: float,
    sides: int = 7,
) -> None:
    cx, cy, cz = center
    points = []
    for y, radius in ((cy - height / 2, bottom_radius), (cy + height / 2, top_radius)):
        for index in range(sides):
            angle = 2 * math.pi * index / sides
            points.append((cx + radius * math.cos(angle), y, cz + radius * math.sin(angle)))
    faces = []
    for index in range(sides):
        faces.append((index, (index + 1) % sides, (index + 1) % sides + sides, index + sides))
    faces.extend([tuple(range(sides - 1, -1, -1)), tuple(range(sides, 2 * sides))])
    o._part(name, points, faces)


def lowpoly_mass(
    o: Obj,
    name: str,
    center: tuple[float, float, float],
    radii: tuple[float, float, float],
    sides: int = 7,
) -> None:
    cx, cy, cz = center
    rx, ry, rz = radii
    points = [(cx, cy + ry, cz), (cx, cy - ry, cz)]
    for index in range(sides):
        angle = 2 * math.pi * index / sides
        points.append((cx + rx * math.cos(angle), cy, cz + rz * math.sin(angle)))
    faces = []
    for index in range(sides):
        current = 2 + index
        following = 2 + (index + 1) % sides
        faces.append((0, current, following))
        faces.append((1, following, current))
    o._part(name, points, faces)


def tree(o: Obj, index: int, x: float, z: float, scale: float = 1.0) -> None:
    o.material("MAT_WOOD")
    tapered_cylinder(o, f"Tree_{index}_Trunk", (x, 1.2 * scale, z), 0.16 * scale, 0.10 * scale, 2.4 * scale)
    o.material("MAT_FOLIAGE")
    lowpoly_mass(o, f"Tree_{index}_CrownLow", (x, 2.25 * scale, z), (0.72 * scale, 0.55 * scale, 0.64 * scale))
    lowpoly_mass(o, f"Tree_{index}_CrownHigh", (x + 0.18 * scale, 2.75 * scale, z - 0.12 * scale), (0.58 * scale, 0.48 * scale, 0.54 * scale))


def jungle() -> Path:
    o = asset("ENV_JUNGLE_PATH_001")
    o.material("MAT_RIDGE")
    route = [((0, 0), (0, 3)), ((0, 3), (1.0, 5.7)), ((1.0, 5.7), (0.25, 8.4)), ((0.25, 8.4), (0.25, 10.5))]
    for index, (start, end) in enumerate(route, 1):
        path_slab(o, f"PrimaryRoute_{index}", start, end, 1.45)
    detour = [((0.95, 5.5), (2.7, 6.1)), ((2.7, 6.1), (2.4, 7.2)), ((2.4, 7.2), (0.55, 7.8))]
    for index, (start, end) in enumerate(detour, 1):
        path_slab(o, f"VisibleReconnectDetour_{index}", start, end, 0.82, 0.06)
    tree_positions = [(-1.5,0.5),(1.6,0.8),(-1.7,2.5),(1.8,3.2),(-1.2,4.6),(2.1,4.4),(-1.0,6.2),(3.4,6.5),(-1.4,8.0),(1.8,8.7),(-1.4,10.1),(1.8,10.4)]
    for index, (x, z) in enumerate(tree_positions, 1):
        tree(o, index, x, z, 0.82 + 0.08 * (index % 3))
    o.material("MAT_MARKER")
    for label, z in (("CampReturnAnchor", 0.25), ("RidgeExitMarker", 10.25)):
        o.beam(f"{label}_Left", (-0.62, 0, z), (-0.62, 1.65, z), 0.10)
        o.beam(f"{label}_Right", (0.62, 0, z), (0.62, 1.65, z), 0.10)
        o.beam(f"{label}_Header", (-0.67, 1.65, z), (0.67, 1.65, z), 0.12)
    o.material("MAT_WOOD")
    o.beam("ResourcePocketBoundaryA", (1.65, 0.16, 5.75), (3.0, 0.18, 5.75), 0.17)
    o.beam("ResourcePocketBoundaryB", (3.0, 0.18, 5.75), (3.15, 0.16, 7.15), 0.17)
    o.material("MAT_FOLIAGE")
    for index, (x, z) in enumerate(((2.2, 6.25), (2.8, 6.55), (2.35, 6.9)), 1):
        lowpoly_mass(o, f"ReadableResourceMass_{index}", (x, 0.35, z), (0.32, 0.45, 0.32))
    return o.write()


def ravine() -> Path:
    o = asset("ENV_RAVINE_001")
    o.material("MAT_ROCK")
    o.box("BelayerCliff", (-2.4, 0.38, 0), (2.8, 0.76, 4.4))
    o.box("RecoveryCliff", (2.4, 0.72, 0), (2.8, 1.44, 4.4))
    for index, (x, y, z, rx, ry, rz) in enumerate([
        (-1.3,.65,-1.7,.65,.42,.55),(-1.4,.70,1.6,.72,.48,.62),(1.3,1.2,-1.6,.68,.55,.62),(1.4,1.35,1.55,.78,.60,.68),
        (-2.8,.85,-1.8,.75,.55,.62),(-2.9,.82,1.75,.70,.50,.58),(2.8,1.55,-1.75,.78,.62,.65),(2.9,1.58,1.7,.82,.66,.70)
    ], 1):
        lowpoly_mass(o, f"CliffSilhouetteRock_{index}", (x, y, z), (rx, ry, rz))
    o.material("MAT_RIDGE")
    o.box("BelayerSafeStance", (-2.0, 0.80, 0), (1.5, 0.10, 1.65))
    o.box("RecoveryObjectiveLedge", (2.0, 1.49, 0), (1.55, 0.10, 1.55))
    o.material("MAT_ROCK")
    for index, (x, y, z) in enumerate(((-0.95,.46,-.15),(-.30,.67,.12),(.38,.88,-.08),(1.02,1.10,.10)), 1):
        lowpoly_mass(o, f"BoundedProgressionPoint_{index}", (x, y, z), (.34,.20,.38), 6)
    o.material("MAT_MARKER")
    for index, (x, y, z) in enumerate(((-.95,.70,-.34),(-.30,.91,.31),(.38,1.12,-.28),(1.02,1.34,.29)), 1):
        o.box(f"RouteOrderMarker_{index}", (x, y, z), (.18,.05,.18))
    o.material("MAT_RIDGE")
    fail_route = [((-1.05, 1.35), (-0.3, 1.55)), ((-0.3, 1.55), (0.5, 1.55)), ((0.5, 1.55), (1.35, 1.35))]
    for index, (start, end) in enumerate(fail_route, 1):
        path_slab(o, f"FailForwardReturn_{index}", start, end, 0.55, 0.12)
    return o.write()


def ridge() -> Path:
    o = asset("ENV_RIDGE_001")
    o.material("MAT_ROCK")
    o.box("RidgeGroundingMass", (0, 0.30, 1.7), (7.2, 0.60, 5.4))
    for index, (x, z, scale) in enumerate(((-3,-.4,.8),(-2.2,4.1,.9),(-.8,4.5,.7),(1.0,4.4,.75),(2.4,4.0,.85),(3.1,.2,.75)), 1):
        lowpoly_mass(o, f"RidgeEdgeRock_{index}", (x,.72,z), (.7*scale,.55*scale,.75*scale))
    o.material("MAT_RIDGE")
    o.box("SafeOverlookPlatform", (0, 0.67, 3.0), (3.1, 0.14, 2.05))
    path_slab(o, "ObviousReturnRoute", (0, -1.0), (0, 2.0), 1.35, 0.12)
    o.material("MAT_MARKER")
    o.beam("ArrivalMarkerLeft", (-.65,.70,-.75), (-.65,2.05,-.75), .10)
    o.beam("ArrivalMarkerRight", (.65,.70,-.75), (.65,2.05,-.75), .10)
    o.beam("ArrivalMarkerHeader", (-.70,2.05,-.75), (.70,2.05,-.75), .12)
    o.beam("WindCueMast", (-1.05,.72,3.25), (-1.05,2.65,3.25), .08)
    o.box("DirectionalWindPanel", (-.72,2.38,3.25), (.62,.035,.32))
    o.material("MAT_WOOD")
    o.beam("SignalDirectionLeft", (.75,.70,3.20), (1.20,2.35,3.20), .09)
    o.beam("SignalDirectionRight", (1.65,.70,3.20), (1.20,2.35,3.20), .09)
    o.beam("SignalDirectionCrossbar", (.92,1.55,3.20), (1.48,1.55,3.20), .08)
    o.material("MAT_ROCK")
    for index, x in enumerate((-1.45,-.95,-.45,.45,.95,1.45), 1):
        lowpoly_mass(o, f"ComfortEdgeBarrier_{index}", (x,.92,4.02), (.32,.35,.30), 6)
    return o.write()


def anchor() -> Path:
    o = asset("PRP_RAVINE_ANCHOR_001")
    o.material("MAT_ROCK")
    lowpoly_mass(o, "MountingRock", (0, .35, 0), (.48,.38,.22), 7)
    o.material("MAT_MARKER")
    o.torus("HighContrastAnchorRing", (0,.46,-.22), .20, .045, 18, 6)
    o.material("MAT_ROPE")
    o.beam("ReadableRopeExitLeft", (-.12,.33,-.25), (-.42,.05,-.26), .06)
    o.beam("ReadableRopeExitRight", (.12,.33,-.25), (.42,.05,-.26), .06)
    return o.write()


def guide_markers() -> Path:
    o = asset("PRP_RAVINE_GUIDE_MARKERS_001")
    o.material("MAT_MARKER")
    o.cylinder("Marker_1_Circle", (-.34,.04,0), .15, .07, 16)
    o.box("Marker_2_Square", (0,.04,0), (.28,.07,.28))
    points = [(-.34,0,0),(0,0,.20),(.34,0,0),(0,0,-.20),(-.34,.08,0),(0,.08,.20),(.34,.08,0),(0,.08,-.20)]
    faces = [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    o._part("Marker_3_Diamond", [(x+.34,y,z) for x,y,z in points], faces)
    o.material("MAT_ROCK")
    for index, x in enumerate((-.34,0,.68), 1):
        o.cylinder(f"Marker_{index}_CenterDot", (x,-.005,0), .045, .015, 10)
    return o.write()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    files = [jungle(), ravine(), ridge(), anchor(), guide_markers()]
    print("\n".join(str(path.relative_to(ROOT)) for path in files))


if __name__ == "__main__":
    main()
