#!/usr/bin/env python3
"""Repo-side QA for the EN-023/EN-024 Stormnatten damage-story refinement."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from refine_set_dressing_art import ROOT, MANIFEST, build as build_set_dressing

EXPECTED = {
    ("EN-023", "broken_shelter_parts"): 300,
    ("EN-023", "loose_cloth"): 250,
    ("EN-024", "slack"): 250,
    ("EN-024", "taut"): 250,
}
ALLOWED_MATERIALS = {"Wood", "Rope", "Tarp", "Cloth"}
MAX_SPAN_GROWTH = 0.60


def mesh_bounds(vertices):
    if not vertices:
        return (0.0, 0.0, 0.0)
    xs = [v[0] for v in vertices]
    ys = [v[1] for v in vertices]
    zs = [v[2] for v in vertices]
    return (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))


def inspect_obj(path: Path):
    vertices = []
    faces = 0
    materials = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("v "):
            parts = line.split()
            vertices.append((float(parts[1]), float(parts[2]), float(parts[3])))
        elif line.startswith("f "):
            faces += 1
        elif line.startswith("usemtl "):
            materials.add(line.split(None, 1)[1])
    return vertices, faces, materials


def main() -> int:
    errors = []
    if not MANIFEST.exists():
        print(f"ERROR: missing manifest: {MANIFEST}")
        return 1

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries = {
        (str(entry.get("asset_id", "")), str(entry.get("variant", "default"))): entry
        for entry in manifest
        if entry.get("kind") == "mesh" and str(entry.get("asset_id", "")) in {"EN-023", "EN-024"}
    }

    if set(entries) != set(EXPECTED):
        errors.append(
            "storm-story variant coverage mismatch: expected "
            + str(sorted(EXPECTED)) + ", got " + str(sorted(entries))
        )

    print("Project ØEN Stormnatten damage-story geometry QA")
    print("  contract: visible extra geometry, canonical shared materials, bounded physical growth")

    blobs_by_family = {"EN-023": [], "EN-024": []}
    for key, min_delta_faces in EXPECTED.items():
        asset_id, variant = key
        entry = entries.get(key)
        if entry is None:
            continue

        path = ROOT / entry["path"]
        if not path.exists():
            errors.append(f"{asset_id}/{variant} missing refined OBJ: {path.relative_to(ROOT)}")
            continue

        baseline = build_set_dressing(asset_id, variant)
        baseline_faces = len(baseline.faces)
        baseline_vertices = len(baseline.verts)
        baseline_span = mesh_bounds(baseline.verts)

        vertices, final_faces, materials = inspect_obj(path)
        final_vertices = len(vertices)
        final_span = mesh_bounds(vertices)
        delta_faces = final_faces - baseline_faces
        delta_vertices = final_vertices - baseline_vertices

        if delta_faces < min_delta_faces:
            errors.append(
                f"{asset_id}/{variant} storm detail too weak: +{delta_faces} faces < +{min_delta_faces}"
            )
        if delta_vertices <= 0:
            errors.append(f"{asset_id}/{variant} did not add vertices over canonical baseline")

        unexpected_materials = materials - ALLOWED_MATERIALS
        if unexpected_materials:
            errors.append(
                f"{asset_id}/{variant} introduced noncanonical materials: {sorted(unexpected_materials)}"
            )

        if "Rope" not in materials:
            errors.append(f"{asset_id}/{variant} missing Rope after storm-story refinement")
        if asset_id == "EN-023" and variant == "broken_shelter_parts" and "Wood" not in materials:
            errors.append("EN-023/broken_shelter_parts missing Wood")
        if asset_id == "EN-023" and variant == "loose_cloth" and not ({"Tarp", "Cloth"} & materials):
            errors.append("EN-023/loose_cloth missing cloth/tarp material")

        for axis, (base, final) in enumerate(zip(baseline_span, final_span)):
            growth = final - base
            if growth > MAX_SPAN_GROWTH:
                errors.append(
                    f"{asset_id}/{variant} bounds grew too far on axis {axis}: +{growth:.3f}m > +{MAX_SPAN_GROWTH:.2f}m"
                )

        blob = path.read_bytes()
        blobs_by_family[asset_id].append(blob)
        print(
            f"  {asset_id}/{variant}: {baseline_faces}->{final_faces} faces "
            f"(+{delta_faces}), {baseline_vertices}->{final_vertices} verts (+{delta_vertices}), "
            f"span={tuple(round(v, 3) for v in final_span)}"
        )

    for asset_id, blobs in blobs_by_family.items():
        if len(blobs) != 2:
            errors.append(f"{asset_id} expected two refined state meshes, found {len(blobs)}")
        elif blobs[0] == blobs[1]:
            errors.append(f"{asset_id} storm states collapsed to byte-identical meshes")

    refiner = ROOT / "tools" / "generated_art" / "refine_storm_story_geometry.py"
    if not refiner.exists():
        errors.append("missing refine_storm_story_geometry.py")
    else:
        text = refiner.read_text(encoding="utf-8")
        for token in (
            "add_splinter_wedge",
            "enhance_broken_shelter_parts",
            "enhance_loose_cloth",
            "enhance_slack_boundary",
            "enhance_taut_boundary",
            "build_set_dressing(asset_id, variant)",
        ):
            if token not in text:
                errors.append(f"storm-story refiner missing contract token: {token}")
        for forbidden in ("random.", "time.time", "requests.", "urllib."):
            if forbidden in text:
                errors.append(f"storm-story refiner must stay deterministic/offline: {forbidden}")

    if errors:
        print(f"\nFAILED with {len(errors)} issue(s):")
        for error in errors:
            print(" - " + error)
        return 1

    print("\nPASS: Stormnatten damage-story meshes add readable breakage/tension detail without new materials or runaway bounds.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
