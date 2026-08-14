#!/usr/bin/env python3
"""Add VR-readable failure/tension detail to the canonical signal-finale meshes.

This deterministic post-pass runs after the broad hero/prop/set-dressing passes and
after the camp storm-story refinement. It rebuilds only the canonical finale assets
from their source generators and adds a bounded amount of shared-material geometry:

- CS-015 storm-damaged beacon: failed braces, split timber, torn lashings and loaded tails;
- PR-014 storm-damaged signal cloth: torn fringe, failed corner ties and groundward tails;
- EN-019 logs: slipped/split fuel timber plus surviving bundle lashings;
- EN-019 ropes: one failed anchor/stake, spill tail and partial coil;
- EN-019 stones: displaced anchor stones with a rope loop tying the cluster to the beacon story.

No new material families, textures, runtime scripts or file paths are introduced.
"""
from __future__ import annotations

import json
from pathlib import Path

from refine_hero_art import (
    Mesh,
    add_box,
    add_cylinder,
    add_rope_between,
    add_torus,
    build as build_hero,
    write_obj,
)
from refine_prop_art import build as build_prop
from refine_set_dressing_art import ROOT, MANIFEST, build as build_set_dressing
from refine_environment_art import add_rock
from refine_storm_story_geometry import add_splinter_wedge

TARGET_IDS = {"CS-015", "PR-014", "EN-019"}
SHARED_MATERIALS = {
    "Wood", "Rope", "Tarp", "Metal", "Stone", "Leaf",
    "Cloth", "Mud", "Fire", "Char", "Water",
}


def normalize_variant(value: str) -> str:
    return (value or "default").strip().lower().replace("-", "_").replace(" ", "_")


def baseline(asset_id: str, variant: str) -> Mesh:
    if asset_id == "CS-015":
        return build_hero(asset_id, variant)
    if asset_id == "PR-014":
        return build_prop(asset_id, variant)
    if asset_id == "EN-019":
        return build_set_dressing(asset_id, variant)
    raise ValueError(f"Unsupported signal-finale target: {asset_id}/{variant}")


def enhance_damaged_beacon(mesh: Mesh) -> None:
    # Two low, visibly failed braces change the lower silhouette from a clean tower
    # into a structure that is still standing but has lost lateral support.
    add_cylinder(mesh, (-0.27, 0.28, -0.24), 0.035, 0.92, "Wood", 7, (8, 12, 69))
    add_cylinder(mesh, ( 0.31, 0.24,  0.22), 0.032, 0.78, "Wood", 7, (-7, -18, 73))

    # Surviving lash points and long failed tails make the load path readable in VR.
    for center, euler in (
        ((-0.49, 0.48, -0.34), (90, 10, 0)),
        (( 0.49, 0.50,  0.34), (90, -12, 0)),
        (( 0.18, 1.10,  0.34), (90, 18, 8)),
    ):
        add_torus(mesh, center, 0.080, 0.011, "Rope", 12, 4, euler)

    add_rope_between(mesh, (-0.53, 0.49, -0.34), (-0.82, 0.065, -0.50), 0.010, "Rope", 6)
    add_rope_between(mesh, ( 0.52, 0.50,  0.34), ( 0.80, 0.060,  0.54), 0.010, "Rope", 6)
    add_rope_between(mesh, ( 0.20, 1.10,  0.34), ( 0.52, 0.70,  0.53), 0.009, "Rope", 6)

    # Split fibres around the failed top/crossbrace keep the damage readable from
    # several metres without spending topology on the whole tower.
    splinters = (
        ((-0.34, 1.48, -0.12), (0.050, 0.24, 0.045), (14, 22, -25)),
        ((-0.16, 1.53,  0.11), (0.046, 0.20, 0.040), (-12, -31, 20)),
        (( 0.08, 1.46, -0.17), (0.052, 0.23, 0.043), (16, 35, 18)),
        (( 0.28, 1.38,  0.14), (0.045, 0.19, 0.040), (-15, -18, -24)),
        (( 0.43, 0.96,  0.06), (0.044, 0.18, 0.038), (8, 28, 31)),
        ((-0.42, 0.88, -0.05), (0.042, 0.17, 0.038), (-9, -24, -28)),
    )
    for center, size, euler in splinters:
        add_splinter_wedge(mesh, center, size, euler, "Wood")


def enhance_signal_cloth(mesh: Mesh) -> None:
    # Ragged cloth fingers make the storm-damaged state read beyond its original
    # triangular tear while keeping the pole and cloth as one cheap mesh.
    fringe = (
        ((0.12, 0.60, 0.012), (0.10, 0.22, 0.030), (11, 8, -12)),
        ((0.24, 0.55, 0.018), (0.08, 0.18, 0.028), (-8, -10, 14)),
        ((0.35, 0.51, 0.014), (0.07, 0.16, 0.026), (13, 6, -16)),
        ((0.06, 0.70, 0.010), (0.09, 0.19, 0.028), (-10, 9, 10)),
    )
    for center, size, euler in fringe:
        add_box(mesh, center, size, "Cloth", euler)

    add_torus(mesh, (-0.33, 0.85, 0.0), 0.052, 0.008, "Rope", 12, 4, (90, 0, 0))
    add_torus(mesh, (-0.33, 0.48, 0.0), 0.048, 0.008, "Rope", 12, 4, (90, 0, 0))
    add_rope_between(mesh, (0.13, 0.62, 0.02), (0.55, 0.16, 0.18), 0.008, "Rope", 5)
    add_rope_between(mesh, (0.28, 0.51, 0.01), (0.62, 0.05, -0.16), 0.008, "Rope", 5)
    add_rope_between(mesh, (-0.31, 0.48, 0.0), (-0.55, 0.04, 0.12), 0.008, "Rope", 5)


def enhance_signal_logs(mesh: Mesh) -> None:
    # A slipped log and two surviving lashings change the tidy fuel stack into a
    # storm-displaced repair/fuel resource without creating a new prop family.
    add_cylinder(mesh, (0.17, 0.085, 0.19), 0.040, 0.92, "Wood", 7, (0, 18, 78))
    add_torus(mesh, (-0.18, 0.12, 0.0), 0.145, 0.011, "Rope", 12, 4, (0, 90, 8))
    add_torus(mesh, ( 0.20, 0.12, 0.0), 0.140, 0.011, "Rope", 12, 4, (0, 90, -7))
    add_rope_between(mesh, (0.15, 0.12, 0.04), (0.52, 0.035, 0.31), 0.009, "Rope", 5)

    for center, size, euler in (
        ((-0.38, 0.115, -0.03), (0.044, 0.18, 0.038), (11, 22, -24)),
        ((-0.12, 0.120,  0.05), (0.046, 0.20, 0.040), (-9, -31, 21)),
        (( 0.24, 0.110, -0.06), (0.043, 0.17, 0.038), (14, 34, 18)),
        (( 0.44, 0.105,  0.08), (0.041, 0.16, 0.036), (-12, -16, -22)),
    ):
        add_splinter_wedge(mesh, center, size, euler, "Wood")


def enhance_signal_ropes(mesh: Mesh) -> None:
    # Partial coil plus a failed ground stake give the rope cluster a clear
    # "used under load" story rather than four pristine storage rings. Keep the
    # spill tails physically compact so the state remains a bounded dressing asset.
    add_torus(mesh, (0.42, 0.035, 0.14), 0.145, 0.010, "Rope", 12, 4, (90, 14, 0))
    add_cylinder(mesh, (-0.46, 0.19, -0.16), 0.026, 0.52, "Wood", 7, (5, 18, 18))
    add_rope_between(mesh, (-0.34, 0.08, -0.08), (-0.68, 0.025, -0.26), 0.010, "Rope", 5)
    add_rope_between(mesh, ( 0.22, 0.06,  0.08), ( 0.70, 0.025,  0.24), 0.010, "Rope", 5)
    add_rope_between(mesh, ( 0.40, 0.04,  0.14), ( 0.17, 0.025,  0.38), 0.009, "Rope", 5)


def enhance_signal_stones(mesh: Mesh) -> None:
    # A rope loop and three displaced stones turn the generic cluster into an
    # anchor/ballast read while staying entirely inside shared production materials.
    add_torus(mesh, (0.02, 0.085, 0.0), 0.245, 0.011, "Rope", 12, 4, (90, 7, 0))
    add_rope_between(mesh, (-0.18, 0.09, 0.02), (-0.52, 0.035, -0.28), 0.009, "Rope", 5)
    add_rope_between(mesh, ( 0.18, 0.09, 0.00), ( 0.56, 0.035,  0.24), 0.009, "Rope", 5)
    add_rock(mesh, (-0.50, 0.0,  0.25), (0.18, 0.13, 0.17), "Stone", 7, 0.71)
    add_rock(mesh, ( 0.48, 0.0, -0.24), (0.17, 0.12, 0.18), "Stone", 7, 1.13)
    add_rock(mesh, ( 0.09, 0.0,  0.52), (0.16, 0.11, 0.15), "Stone", 7, 1.61)


def refine(asset_id: str, variant: str) -> Mesh:
    normalized = normalize_variant(variant)
    mesh = baseline(asset_id, variant)
    if asset_id == "CS-015":
        enhance_damaged_beacon(mesh)
    elif asset_id == "PR-014" and normalized == "storm_damaged":
        enhance_signal_cloth(mesh)
    elif asset_id == "EN-019" and normalized == "logs":
        enhance_signal_logs(mesh)
    elif asset_id == "EN-019" and normalized == "ropes":
        enhance_signal_ropes(mesh)
    elif asset_id == "EN-019" and normalized == "stones":
        enhance_signal_stones(mesh)
    else:
        raise ValueError(f"Unsupported signal-finale target: {asset_id}/{variant}")

    unknown = {face[3] for face in mesh.faces} - SHARED_MATERIALS
    if unknown:
        raise ValueError(f"Signal-finale refinement introduced unknown materials: {sorted(unknown)}")
    return mesh


def main() -> int:
    if not MANIFEST.exists():
        raise SystemExit(f"Missing production manifest: {MANIFEST}")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    seen: set[tuple[str, str]] = set()
    total_vertices = 0
    total_faces = 0

    for entry in manifest:
        asset_id = str(entry.get("asset_id", ""))
        variant = str(entry.get("variant", "default"))
        normalized = normalize_variant(variant)
        if entry.get("kind") != "mesh":
            continue
        if asset_id == "CS-015":
            pass
        elif asset_id == "PR-014" and normalized == "storm_damaged":
            pass
        elif asset_id == "EN-019" and normalized in {"logs", "ropes", "stones"}:
            pass
        else:
            continue

        mesh = refine(asset_id, variant)
        write_obj(mesh, ROOT / entry["path"])
        seen.add((asset_id, normalized))
        total_vertices += len(mesh.verts)
        total_faces += len(mesh.faces)

    cs015 = [key for key in seen if key[0] == "CS-015"]
    expected = {
        ("PR-014", "storm_damaged"),
        ("EN-019", "logs"),
        ("EN-019", "ropes"),
        ("EN-019", "stones"),
    }
    if len(cs015) != 1 or not expected.issubset(seen) or len(seen) != 5:
        raise SystemExit(f"Signal-finale refinement coverage mismatch: {sorted(seen)}")

    print(f"Refined {len(seen)} signal-finale meshes: {total_vertices} vertices / {total_faces} faces")
    print("Added beacon failure braces/splinters, torn signal cloth, displaced fuel, used rope and anchor-stone load cues")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
