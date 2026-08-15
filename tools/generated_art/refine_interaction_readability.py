#!/usr/bin/env python3
"""Add Quest-readable interaction detail to Project ØEN hero and hand props.

This pass deliberately runs after the broad hero + survival/tool refiners. It rebuilds
only the interaction-critical families from their deterministic source builders and adds
chunky metre-scale detail that survives VR viewing distance: crate latches/handles,
shared-carry grip zones, radio controls/handle wraps, and clearer mallet/knife/anchor
affordances. No material proliferation and no runtime components are introduced.
"""
from __future__ import annotations

import json
from pathlib import Path

from refine_hero_art import (
    Mesh,
    add_box,
    add_cylinder,
    add_torus,
    build as build_hero,
    write_obj,
)
from refine_prop_art import build as build_prop

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROD = ROOT / "Assets" / "ProductionArt"
MANIFEST = PROD / "Docs" / "production_art_manifest.json"

TARGET_IDS = {"PR-004", "PR-005", "PR-017", "PR-018", "PR-019", "PR-020"}
HERO_IDS = {"PR-004", "PR-005", "PR-020"}


def add_crate_interaction_detail(m: Mesh, variant: str, heavy: bool) -> None:
    sx, sy, sz = ((1.35, .82, .96) if heavy else (1.05, .68, .78))
    front_z = -sz / 2 - .105
    back_z = sz / 2 + .095

    # Large central latch assembly: readable at arm's length, not tiny decorative hardware.
    latch_angle = 14 if variant == "broken" else 0
    add_box(m, (0, sy * .52, front_z), (.24, .18, .035), "Metal", (0, 0, latch_angle))
    add_box(m, (0, sy * .58, front_z - .025), (.065, .25, .035), "Metal", (0, 0, latch_angle))
    add_box(m, (0, sy * .43, front_z - .030), (.16, .055, .040), "Rope", (0, 0, latch_angle))

    # Two broad hinge plates on the rear establish a clear lid axis.
    for x in (-sx * .28, sx * .28):
        add_box(m, (x, sy * .72, back_z), (.20, .13, .035), "Metal")

    # U-shaped end handles with rope-wrapped centre grips.
    for side in (-1, 1):
        x = side * (sx / 2 + .055)
        handle_y = sy * .48
        span = .34 if heavy else .28
        for z in (-span / 2, span / 2):
            add_box(m, (x, handle_y, z), (.055, .19, .055), "Metal")
        add_box(m, (x, handle_y + .075, 0), (.060, .055, span + .055), "Metal")
        add_box(m, (x + side * .012, handle_y + .075, 0), (.070, .070, span * .58), "Rope")

    if heavy:
        # Shared-carry box gets a second, lower grip cue on each end so two-hand intent
        # reads independently of controller prompts.
        for side in (-1, 1):
            x = side * (sx / 2 + .060)
            add_box(m, (x, sy * .27, 0), (.070, .070, .42), "Metal")
            add_box(m, (x + side * .012, sy * .27, 0), (.080, .085, .25), "Rope")


def add_radio_interaction_detail(m: Mesh, variant: str) -> None:
    # Reinforced wrapped carry handle across the existing top rail.
    for x in (-.15, 0.0, .15):
        add_torus(m, (x, .96, 0), .040, .010, "Rope", 10, 4, (0, 0, 90))

    # Two deliberately oversized front controls. Their depth keeps the silhouette
    # legible even under flat storm lighting.
    add_cylinder(m, (.31, .56, -.248), .082, .055, "Metal", 10, (90, 0, 0))
    add_cylinder(m, (.10, .56, -.248), .061, .055, "Metal", 10, (90, 0, 0))

    # Frequency window rail + coarse ticks; six chunky marks instead of micro-text.
    add_box(m, (-.15, .57, -.249), (.34, .105, .020), "Cloth")
    for i in range(6):
        x = -.29 + i * .056
        h = .072 if i in (0, 3, 5) else .050
        add_box(m, (x, .57, -.263), (.014, h, .018), "Metal")

    # State cue stays material-bounded: only active/repaired states gain a bright needle.
    if variant in ("active", "repaired"):
        add_box(m, (-.13, .57, -.276), (.018, .090, .016), "Fire", (0, 0, -8))
    if variant == "broken":
        add_box(m, (.31, .56, -.282), (.11, .025, .018), "Char", (0, 0, 28))


def add_mallet_interaction_detail(m: Mesh, variant: str) -> None:
    # Thick grip sleeve and end stops make the grasp region obvious in-hand.
    add_cylinder(m, (0, .27, 0), .061, .34, "Rope", 8)
    add_torus(m, (0, .11, 0), .064, .010, "Rope", 10, 4)
    add_torus(m, (0, .43, 0), .064, .010, "Rope", 10, 4)
    add_box(m, (0, .055, 0), (.15, .055, .15), "Wood")
    if variant == "worn":
        add_box(m, (.245, .78, 0), (.055, .18, .19), "Char")


def add_knife_interaction_detail(m: Mesh, variant: str) -> None:
    # Guard, pommel cap and lanyard eye are silhouette-level interaction cues.
    add_box(m, (0, .245, 0), (.25, .035, .10), "Metal")
    add_box(m, (0, .025, 0), (.14, .04, .09), "Metal")
    add_torus(m, (0, .005, 0), .055, .010, "Rope", 12, 4, (90, 0, 0))
    add_box(m, (0, .125, -.052), (.09, .17, .014), "Rope")
    if variant == "worn":
        add_box(m, (-.040, .36, -.016), (.025, .12, .016), "Char", (0, 0, -7))


def add_anchor_interaction_detail(m: Mesh, variant: str) -> None:
    # Oversized stop collar + rope eye make the intended tie point unmistakable.
    add_torus(m, (0, .48, 0), .125, .020, "Metal", 14, 5)
    add_torus(m, (0, .57, 0), .095, .017, "Rope", 12, 4)
    add_box(m, (0, .19, 0), (.18, .075, .18), "Metal")
    if variant == "active":
        add_box(m, (.20, .16, .08), (.25, .065, .10), "Stone", (0, 28, 12))


def build_refined(asset_id: str, variant: str) -> Mesh:
    mesh = build_hero(asset_id, variant) if asset_id in HERO_IDS else build_prop(asset_id, variant)
    if asset_id == "PR-004":
        add_crate_interaction_detail(mesh, variant, False)
    elif asset_id == "PR-020":
        add_crate_interaction_detail(mesh, variant, True)
    elif asset_id == "PR-005":
        add_radio_interaction_detail(mesh, variant)
    elif asset_id == "PR-017":
        add_mallet_interaction_detail(mesh, variant)
    elif asset_id == "PR-018":
        add_knife_interaction_detail(mesh, variant)
    elif asset_id == "PR-019":
        add_anchor_interaction_detail(mesh, variant)
    else:
        raise KeyError(asset_id)
    return mesh


def main() -> int:
    if not MANIFEST.exists():
        raise SystemExit(f"Missing production manifest: {MANIFEST}")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    refined = vertices = faces = 0
    families = set()
    for entry in manifest:
        aid = str(entry.get("asset_id", ""))
        if aid not in TARGET_IDS or entry.get("kind") != "mesh":
            continue
        variant = str(entry.get("variant", "default"))
        mesh = build_refined(aid, variant)
        write_obj(mesh, ROOT / entry["path"])
        refined += 1
        vertices += len(mesh.verts)
        faces += len(mesh.faces)
        families.add(aid)

    missing = TARGET_IDS - families
    if missing:
        raise SystemExit("Interaction refinement missed families: " + ", ".join(sorted(missing)))
    print(f"Refined {refined} interaction-critical meshes across {len(families)} families: {vertices} vertices / {faces} triangles")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
