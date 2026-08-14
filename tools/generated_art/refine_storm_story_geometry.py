#!/usr/bin/env python3
"""Add VR-readable storm-consequence detail to the canonical EN-023/EN-024 meshes.

This deterministic post-pass deliberately runs after refine_set_dressing_art.py. It
rebuilds the two storm-story families from the canonical set-dressing generators,
then adds a bounded amount of geometry that reads from Quest interaction distance:

- EN-023 broken shelter parts: snapped poles, splinter wedges and torn lashings;
- EN-023 loose cloth: torn fringe, failed corner lashings and loose rope tails;
- EN-024 slack rope: post lashings, failed tension tail and collapsed ground coil;
- EN-024 taut rope: post lashings, braced stakes and a secondary loaded strand.

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
    tp,
    write_obj,
)
from refine_set_dressing_art import ROOT, MANIFEST, build as build_set_dressing

TARGETS = {"EN-023", "EN-024"}


def add_splinter_wedge(
    mesh: Mesh,
    center: tuple[float, float, float],
    size: tuple[float, float, float],
    euler: tuple[float, float, float],
    material: str = "Wood",
) -> None:
    """Add a low-cost triangular-prism splinter with a sharp readable tip."""
    width, height, depth = size
    local = [
        (-width / 2, -height / 2, -depth / 2),
        ( width / 2, -height / 2, -depth / 2),
        (0.0,          height / 2, -depth / 2),
        (-width / 2, -height / 2,  depth / 2),
        ( width / 2, -height / 2,  depth / 2),
        (0.0,          height / 2,  depth / 2),
    ]
    points = [tp(point, center, euler) for point in local]
    indices = [mesh.v(point) for point in points]
    a, b, c, d, e, f = indices
    mesh.tri(a, b, c, material)
    mesh.tri(f, e, d, material)
    mesh.tri(a, d, e, material); mesh.tri(a, e, b, material)
    mesh.tri(b, e, f, material); mesh.tri(b, f, c, material)
    mesh.tri(c, f, d, material); mesh.tri(c, d, a, material)


def add_post_brace(mesh: Mesh, ground, post, radius: float = 0.022) -> None:
    add_rope_between(mesh, ground, post, radius, "Wood", 7)


def enhance_broken_shelter_parts(mesh: Mesh) -> None:
    # Three visibly snapped poles break up the previous flat plank pile silhouette.
    add_cylinder(mesh, (-0.43, 0.18, -0.12), 0.034, 0.72, "Wood", 7, (8, 24, 66))
    add_cylinder(mesh, ( 0.03, 0.17,  0.16), 0.032, 0.64, "Wood", 7, (-10, -31, 72))
    add_cylinder(mesh, ( 0.42, 0.15, -0.04), 0.030, 0.56, "Wood", 7, (12, 42, 81))

    # Low-poly wedges suggest freshly split fibres at several different scales.
    splinters = [
        ((-0.56, 0.115, -0.16), (0.055, 0.22, 0.045), (18, 21, -24)),
        ((-0.34, 0.135,  0.14), (0.045, 0.18, 0.040), (-12, -18, 31)),
        ((-0.06, 0.120, -0.08), (0.050, 0.24, 0.045), (8, 35, 18)),
        (( 0.17, 0.145,  0.18), (0.052, 0.20, 0.042), (-9, -28, -20)),
        (( 0.39, 0.125, -0.15), (0.047, 0.19, 0.040), (14, 16, 27)),
        (( 0.57, 0.110,  0.11), (0.043, 0.17, 0.038), (-16, 37, -26)),
    ]
    for center, size, euler in splinters:
        add_splinter_wedge(mesh, center, size, euler)

    # Two surviving lash points plus several torn tails tell where the structure failed.
    add_torus(mesh, (-0.31, 0.145, -0.10), 0.085, 0.010, "Rope", 12, 4, (90, 18, 12))
    add_torus(mesh, ( 0.32, 0.135,  0.12), 0.075, 0.010, "Rope", 12, 4, (90, -22, -9))
    add_rope_between(mesh, (-0.39, 0.13, -0.08), (-0.63, 0.035, -0.31), 0.009, "Rope", 5)
    add_rope_between(mesh, (-0.24, 0.13, -0.10), (-0.10, 0.025, -0.38), 0.008, "Rope", 5)
    add_rope_between(mesh, ( 0.28, 0.12,  0.12), ( 0.46, 0.028,  0.34), 0.008, "Rope", 5)
    add_rope_between(mesh, ( 0.36, 0.12,  0.10), ( 0.68, 0.030,  0.25), 0.009, "Rope", 5)


def enhance_loose_cloth(mesh: Mesh) -> None:
    # Torn fringe adds asymmetric silhouette instead of a single tidy damaged tarp plane.
    fringe = [
        ((-0.46, 0.005, 0.37), (0.075, 0.22, 0.035), (18, 4, -10)),
        ((-0.30, 0.002, 0.39), (0.065, 0.17, 0.032), (11, -7, 9)),
        ((-0.10, 0.000, 0.40), (0.082, 0.25, 0.034), (20, 6, -6)),
        (( 0.16, 0.004, 0.39), (0.070, 0.19, 0.032), (14, -5, 11)),
        (( 0.36, 0.008, 0.37), (0.078, 0.23, 0.034), (19, 8, -12)),
        (( 0.51, 0.010, 0.34), (0.060, 0.16, 0.030), (12, -10, 7)),
    ]
    for center, size, euler in fringe:
        add_box(mesh, center, size, "Cloth", euler)

    # One corner is still lashed; the opposite side has visibly failed into long tails.
    add_torus(mesh, (-0.52, 0.075, -0.28), 0.070, 0.009, "Rope", 12, 4, (90, 8, 4))
    add_torus(mesh, ( 0.47, 0.068,  0.25), 0.064, 0.009, "Rope", 12, 4, (90, -13, -6))
    add_rope_between(mesh, (-0.57, 0.07, -0.29), (-0.92, 0.020, -0.55), 0.009, "Rope", 5)
    add_rope_between(mesh, (-0.50, 0.06, -0.25), (-0.74, 0.018, -0.66), 0.008, "Rope", 5)
    add_rope_between(mesh, ( 0.50, 0.06,  0.26), ( 0.86, 0.018,  0.55), 0.009, "Rope", 5)
    add_rope_between(mesh, ( 0.44, 0.05,  0.22), ( 0.66, 0.016,  0.68), 0.008, "Rope", 5)


def add_boundary_lashings(mesh: Mesh) -> None:
    add_torus(mesh, (-0.70, 0.64, 0.0), 0.074, 0.010, "Rope", 12, 4, (90, 0, 0))
    add_torus(mesh, ( 0.70, 0.64, 0.0), 0.074, 0.010, "Rope", 12, 4, (90, 0, 0))


def enhance_slack_boundary(mesh: Mesh) -> None:
    add_boundary_lashings(mesh)
    # A failed centre tail and mud-level coil make the slack state narratively explicit.
    add_rope_between(mesh, (0.00, 0.44, 0.00), (-0.05, 0.17, 0.13), 0.010, "Rope", 5)
    add_rope_between(mesh, (-0.05, 0.17, 0.13), (0.18, 0.025, 0.22), 0.009, "Rope", 5)
    add_torus(mesh, (0.23, 0.030, 0.20), 0.145, 0.012, "Rope", 14, 4, (90, 16, 0))

    # One brace has slipped while the other still supports its post.
    add_post_brace(mesh, (-0.96, 0.02, 0.22), (-0.70, 0.53, 0.0), 0.021)
    add_post_brace(mesh, ( 0.92, 0.02, -0.16), (0.70, 0.50, 0.0), 0.020)


def enhance_taut_boundary(mesh: Mesh) -> None:
    add_boundary_lashings(mesh)
    # Braces and a second loaded strand make the tension state read as deliberate reinforcement.
    # Keep the brace feet inside the 0.60 m per-axis physical-growth QA envelope.
    add_post_brace(mesh, (-0.94, 0.02, 0.24), (-0.70, 0.56, 0.0), 0.023)
    add_post_brace(mesh, ( 0.94, 0.02, -0.24), (0.70, 0.56, 0.0), 0.023)

    points = [(-0.70, 0.585, 0.030), (-0.35, 0.580, 0.028), (0.0, 0.575, 0.030),
              (0.35, 0.580, 0.028), (0.70, 0.585, 0.030)]
    for start, end in zip(points, points[1:]):
        add_rope_between(mesh, start, end, 0.010, "Rope", 6)


def refine(asset_id: str, variant: str) -> Mesh:
    mesh = build_set_dressing(asset_id, variant)
    if asset_id == "EN-023" and variant == "broken_shelter_parts":
        enhance_broken_shelter_parts(mesh)
    elif asset_id == "EN-023" and variant == "loose_cloth":
        enhance_loose_cloth(mesh)
    elif asset_id == "EN-024" and variant == "slack":
        enhance_slack_boundary(mesh)
    elif asset_id == "EN-024" and variant == "taut":
        enhance_taut_boundary(mesh)
    else:
        raise ValueError(f"Unsupported storm-story target: {asset_id}/{variant}")
    return mesh


def main() -> int:
    if not MANIFEST.exists():
        raise SystemExit(f"Missing production manifest: {MANIFEST}")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    refined = 0
    total_vertices = 0
    total_faces = 0
    seen: set[tuple[str, str]] = set()

    for entry in manifest:
        asset_id = str(entry.get("asset_id", ""))
        variant = str(entry.get("variant", "default"))
        if asset_id not in TARGETS or entry.get("kind") != "mesh":
            continue

        mesh = refine(asset_id, variant)
        write_obj(mesh, ROOT / entry["path"])
        refined += 1
        total_vertices += len(mesh.verts)
        total_faces += len(mesh.faces)
        seen.add((asset_id, variant))

    expected = {
        ("EN-023", "broken_shelter_parts"),
        ("EN-023", "loose_cloth"),
        ("EN-024", "slack"),
        ("EN-024", "taut"),
    }
    if seen != expected:
        missing = sorted(expected - seen)
        extra = sorted(seen - expected)
        raise SystemExit(f"Storm-story refinement coverage mismatch; missing={missing} extra={extra}")

    print(f"Refined {refined} Stormnatten damage-story meshes: {total_vertices} vertices / {total_faces} faces")
    print("Added readable splinters, torn lashings, failed rope tails and loaded boundary-rope bracing")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
