#!/usr/bin/env python3
"""Final world-density pass for Project ØEN Stormnatten.

The approved gameplay mockups are not sparse hero-object turntables: they are dense,
wet coastal spaces with jungle edge, frond litter, vines, rock framing and storm
wreckage around the interaction anchors. Earlier passes fixed the hero silhouettes;
this pass raises the surrounding canonical environment assets to the same art bar.

Only existing canonical OBJ paths are rewritten, so Unity GUIDs and references remain
stable. Geometry is deliberately chunky/VR-readable and reuses the existing shared
Quest-friendly material set.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

from refine_hero_art import Mesh, add_box, add_torus, add_rope_between, write_obj
from refine_environment_art import build as build_environment, add_leaf, add_frond, add_rock
from refine_set_dressing_art import build as build_set_dressing
from refine_mockup_environment import enhance as mockup_enhance, TARGETS as MOCKUP_TARGETS, ENV_TARGETS

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROD = ROOT / "Assets" / "ProjectOEN" / "ProductionArt"
MANIFEST = PROD / "Docs" / "production_art_manifest.json"

TARGETS = {
    "EN-002", "EN-005", "EN-008", "EN-009", "EN-010", "EN-012",
    "EN-013", "EN-014", "EN-015", "EN-019", "EN-023", "EN-024",
}
ENV_BASE = {"EN-002", "EN-005", "EN-008", "EN-009", "EN-010", "EN-012"}


def base_mesh(aid: str, variant: str) -> Mesh:
    mesh = build_environment(aid, variant) if aid in ENV_BASE else build_set_dressing(aid, variant)
    if aid in MOCKUP_TARGETS:
        mockup_enhance(aid, variant, mesh)
    return mesh


def add_ground_leaf(mesh: Mesh, x: float, z: float, yaw: float, scale: float = 1.0) -> None:
    add_leaf(mesh, (x, .025, z), .46 * scale, .17 * scale, yaw, -28, "Leaf", .08)
    add_leaf(mesh, (x + .035, .028, z - .025), .36 * scale, .14 * scale, yaw + 152, -34, "Leaf", .06)


def enhance_planks(mesh: Mesh, variant: str) -> None:
    n = {"small": 3, "medium": 5, "large": 7}.get(variant, 5)
    for i in range(n):
        a = i * 2.19
        r = .28 + .045 * i
        add_ground_leaf(mesh, math.cos(a) * r, math.sin(a) * r, 28 + i * 47, .72 + .08 * (i % 3))
    if variant in ("medium", "large"):
        add_rope_between(mesh, (-.58, .07, -.19), (.68, .045, .24), .010, "Rope", 6)
        add_box(mesh, (.42, .08, -.38), (.52, .035, .10), "Char", (0, 37, -5))


def enhance_stones(mesh: Mesh, variant: str) -> None:
    n = {"small": 3, "medium": 5, "large": 8}.get(variant, 5)
    for i in range(n):
        a = i * 2.399963
        r = .18 + .055 * math.sqrt(i + 1)
        add_ground_leaf(mesh, math.cos(a) * r, math.sin(a) * r, 14 + i * 61, .52 + .06 * (i % 3))
    # Darker embedded pebbles break the isolated grey-boulder read.
    for i in range(max(2, n // 2)):
        a = i * 2.7 + .4
        add_rock(mesh, (math.cos(a) * .23, .005, math.sin(a) * .23), (.075, .038, .070), "Char", 6, i * .51)


def enhance_frond_litter(mesh: Mesh, variant: str) -> None:
    n = 5 if variant == "small" else 9
    for i in range(n):
        a = i * 2.399963
        r = .10 + .065 * math.sqrt(i + 1)
        add_frond(mesh, (math.cos(a) * r, .018 + .008 * (i % 2), math.sin(a) * r),
                  -82 + i * 39, .42 + .05 * (i % 4), "Leaf", .12)
    # A couple of snapped brown midribs keep the litter from reading as a green rosette.
    for i in range(3 if variant == "medium" else 2):
        add_rope_between(mesh, (-.34 + i * .31, .025, -.18 + .07 * i),
                         (.25 + i * .12, .020, .22 - .08 * i), .009, "Wood", 5)


def enhance_bush(mesh: Mesh, variant: str) -> None:
    scale = {"small": .78, "medium": 1.0, "dense": 1.20}.get(variant, 1.0)
    n = 12 if variant == "small" else (19 if variant == "medium" else 30)
    # Broad outer leaves fill the silhouette; the previous bush read too stem-heavy.
    for i in range(n):
        a = i * 2.399963
        ring = .16 + .10 * ((i % 5) / 4)
        y = .16 + .10 * (i % 4)
        root = (math.cos(a) * ring, y, math.sin(a) * ring)
        add_leaf(mesh, root, (.34 + .06 * (i % 3)) * scale, (.19 + .025 * (i % 2)) * scale,
                 math.degrees(a) + (18 if i % 2 else -12), -20 - 5 * (i % 4), "Leaf", .08)
    for i in range(4):
        a = math.radians(30 + i * 92)
        add_ground_leaf(mesh, math.cos(a) * .32, math.sin(a) * .32, 22 + i * 67, .62 * scale)


def enhance_vines(mesh: Mesh, variant: str) -> None:
    n = {"short": 5, "hanging": 8, "dense": 13}.get(variant, 8)
    for i in range(n):
        x = (i - (n - 1) / 2) * .085
        h = .48 if variant == "short" else (.82 + .07 * (i % 4))
        prev = (x, h, .03 * math.sin(i))
        for seg in range(1, 7):
            t = seg / 6
            cur = (x + .07 * math.sin(t * math.pi * 2 + i * .9), h * (1 - t), .07 * math.sin(t * math.pi + i * .55))
            add_rope_between(mesh, prev, cur, .0065 if variant != "dense" else .008, "Rope", 5)
            if seg in (2, 4, 5):
                add_leaf(mesh, cur, .18 + .025 * ((i + seg) % 3), .085, 35 + i * 31 + seg * 19, -32, "Leaf", .05)
            prev = cur
    if variant == "dense":
        for i in range(5): add_ground_leaf(mesh, -.32 + i * .16, .10 * math.sin(i), 40 + i * 49, .58)


def enhance_wall(mesh: Mesh, variant: str) -> None:
    # Large foreground rocks and layered creepers make the modular wall read as a cliff face.
    xs = (-1.42, -.74, -.08, .62, 1.30)
    for i, x in enumerate(xs):
        add_rock(mesh, (x, .00, -.28 + .04 * (i % 2)), (.25 + .03 * (i % 2), .15, .22), "Stone", 8, i * .41)
        if i % 2 == 0:
            add_frond(mesh, (x, .20, -.18), 18 + i * 53, .40, "Leaf", .16)
    for i, x in enumerate((-.98, -.46, .12, .76, 1.08)):
        y = 1.02 + .16 * (i % 3)
        add_rope_between(mesh, (x, y, .02), (x + .08 * math.sin(i), .12, -.06), .0065, "Rope", 5)
        for j in (0, 1):
            add_leaf(mesh, (x + .03 * j, y * (.70 - .18 * j), -.02), .20, .095, 28 + i * 61 + j * 97, -38, "Leaf", .05)


def enhance_grass(mesh: Mesh, variant: str) -> None:
    n = 14 if variant == "short" else 28
    for i in range(n):
        a = i * 2.399963
        r = .06 + .045 * math.sqrt(i + 1)
        x, z = math.cos(a) * r, math.sin(a) * r
        h = (.28 if variant == "short" else .46) * (.75 + .08 * (i % 5))
        add_leaf(mesh, (x, .01, z), h, .035 + .006 * (i % 2), 72 + i * 11, -45, "Leaf", .07)
    for i in range(4): add_ground_leaf(mesh, -.30 + i * .20, -.16 + .06 * (i % 2), 20 + i * 70, .44)


def enhance_cave(mesh: Mesh, variant: str) -> None:
    # Mossy outer ledge and hanging root curtain create the damp cave framing from the mockups.
    for i, x in enumerate((-1.28, -.86, -.40, .08, .56, 1.02, 1.34)):
        add_ground_leaf(mesh, x, -.24 + .05 * (i % 2), 12 + i * 49, .50 + .05 * (i % 3))
    roots = 5 if variant != "arch" else 7
    for i in range(roots):
        x = -.78 + i * (1.56 / max(1, roots - 1))
        top = 1.62 + .10 * math.sin(i * 1.3)
        end = .64 + .10 * (i % 3)
        add_rope_between(mesh, (x, top, .06), (x + .08 * math.sin(i), end, .10), .0065, "Rope", 5)
        add_leaf(mesh, (x, 1.08, .08), .18, .08, 40 + i * 73, -45, "Leaf", .06)


def enhance_cave_debris(mesh: Mesh, variant: str) -> None:
    for i in range(7):
        a = i * 2.399963
        r = .14 + .075 * math.sqrt(i + 1)
        add_ground_leaf(mesh, math.cos(a) * r, math.sin(a) * r, 18 + i * 51, .48 + .05 * (i % 3))
    if variant == "branches":
        add_rope_between(mesh, (-.48, .055, -.22), (.58, .035, .26), .012, "Wood", 6)
        add_rope_between(mesh, (-.36, .045, .31), (.42, .035, -.28), .009, "Wood", 5)


def enhance_signal_hill(mesh: Mesh, variant: str) -> None:
    if variant == "logs":
        for i in range(4): add_ground_leaf(mesh, -.36 + i * .24, -.18 + .08 * (i % 2), 33 + i * 59, .54)
    elif variant == "ropes":
        add_rope_between(mesh, (-.48, .025, -.24), (.55, .022, .30), .010, "Rope", 6)
        add_torus(mesh, (.28, .05, -.18), .13, .009, "Rope", 14, 4, (90, 0, 13))
    else:
        for i in range(5):
            a = i * 1.7
            add_ground_leaf(mesh, math.cos(a) * .28, math.sin(a) * .28, 11 + i * 61, .46)


def enhance_storm_debris(mesh: Mesh, variant: str) -> None:
    # Add visibly torn tarp/cloth, rope tails and splintered wood around the existing debris cluster.
    for i, (x, z, yaw) in enumerate(((-.54, -.24, 24), (-.12, .34, -31), (.38, -.16, 51), (.62, .26, -18))):
        add_box(mesh, (x, .055 + .012 * i, z), (.56 - .05 * (i % 2), .030, .085), "Wood" if i != 2 else "Char", (0, yaw, (i - 1) * 5))
    add_box(mesh, (-.18, .10, -.08), (.46, .018, .26), "Cloth", (0, 18, -7))
    add_box(mesh, (.34, .075, .18), (.34, .016, .20), "Tarp", (0, -27, 5))
    add_rope_between(mesh, (-.56, .04, .18), (.62, .025, -.32), .010, "Rope", 6)
    add_rope_between(mesh, (-.28, .035, -.36), (.48, .028, .42), .007, "Rope", 5)
    for i in range(4): add_ground_leaf(mesh, -.42 + i * .28, .30 * math.sin(i * 1.4), 30 + i * 67, .52)


def enhance_boundary(mesh: Mesh, variant: str) -> None:
    # More convincing beach-camp perimeter: debris at feet plus small cloth warning strips.
    for i, x in enumerate((-.58, -.18, .22, .62)):
        add_ground_leaf(mesh, x, -.12 + .08 * (i % 2), 10 + i * 73, .42)
    if variant == "slack":
        add_box(mesh, (.12, .34, .015), (.23, .018, .12), "Cloth", (0, 4, -11))
    else:
        add_box(mesh, (-.22, .42, .015), (.20, .018, .11), "Cloth", (0, -7, 6))
        add_box(mesh, (.30, .40, .015), (.18, .018, .10), "Cloth", (0, 10, -5))


def enhance(aid: str, mesh: Mesh, variant: str) -> None:
    {
        "EN-002": enhance_planks,
        "EN-005": enhance_stones,
        "EN-008": enhance_frond_litter,
        "EN-009": enhance_bush,
        "EN-010": enhance_vines,
        "EN-012": enhance_wall,
        "EN-013": enhance_grass,
        "EN-014": enhance_cave,
        "EN-015": enhance_cave_debris,
        "EN-019": enhance_signal_hill,
        "EN-023": enhance_storm_debris,
        "EN-024": enhance_boundary,
    }[aid](mesh, variant)


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    count = verts = faces = 0
    seen = set()
    for e in manifest:
        aid = str(e.get("asset_id", "")); variant = str(e.get("variant", "default"))
        if aid not in TARGETS or e.get("kind") != "mesh":
            continue
        mesh = base_mesh(aid, variant)
        enhance(aid, mesh, variant)
        write_obj(mesh, ROOT / e["path"])
        count += 1; verts += len(mesh.verts); faces += len(mesh.faces); seen.add(aid)
    missing = TARGETS - seen
    if missing:
        raise SystemExit("World-density pass missed: " + ", ".join(sorted(missing)))
    print(f"Stormnatten world density: {count} meshes / {len(seen)} families / {verts} vertices / {faces} faces")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
