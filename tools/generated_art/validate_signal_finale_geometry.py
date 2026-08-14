#!/usr/bin/env python3
"""QA gate for the canonical Stormnatten signal-finale mesh refinement."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from refine_signal_finale_geometry import (
    MANIFEST,
    ROOT,
    SHARED_MATERIALS,
    baseline,
    normalize_variant,
    refine,
)

MIN_FACE_DELTA = {
    ("CS-015", "*"): 360,
    ("PR-014", "storm_damaged"): 250,
    ("EN-019", "logs"): 220,
    ("EN-019", "ropes"): 180,
    ("EN-019", "stones"): 120,
}
MAX_FACE_DELTA = 900
MAX_AXIS_GROWTH = 0.65


def bounds(mesh):
    xs = [v[0] for v in mesh.verts]
    ys = [v[1] for v in mesh.verts]
    zs = [v[2] for v in mesh.verts]
    return (
        (min(xs), max(xs)),
        (min(ys), max(ys)),
        (min(zs), max(zs)),
    )


def span(b):
    return tuple(axis[1] - axis[0] for axis in b)


def parse_obj(path: Path):
    vertices = 0
    faces = 0
    materials = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("v "):
            vertices += 1
        elif line.startswith("f "):
            faces += 1
        elif line.startswith("usemtl "):
            materials.add(line.split(None, 1)[1].strip())
    return vertices, faces, materials


def minimum_for(asset_id: str, variant: str) -> int:
    return MIN_FACE_DELTA.get((asset_id, variant), MIN_FACE_DELTA.get((asset_id, "*"), 10**9))


def main() -> int:
    if not MANIFEST.exists():
        print(f"ERROR: missing production manifest: {MANIFEST}")
        return 1

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors = []
    seen = []
    hashes = {}
    rows = []

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

        base = baseline(asset_id, variant)
        final = refine(asset_id, variant)
        face_delta = len(final.faces) - len(base.faces)
        vert_delta = len(final.verts) - len(base.verts)
        base_span = span(bounds(base))
        final_span = span(bounds(final))
        axis_growth = tuple(f - b for f, b in zip(final_span, base_span))

        minimum = minimum_for(asset_id, normalized)
        if face_delta < minimum:
            errors.append(f"{asset_id}/{normalized}: face delta {face_delta} < {minimum}")
        if face_delta > MAX_FACE_DELTA:
            errors.append(f"{asset_id}/{normalized}: face delta {face_delta} > {MAX_FACE_DELTA}")
        if vert_delta <= 0:
            errors.append(f"{asset_id}/{normalized}: no added vertices")
        for axis_name, growth in zip("XYZ", axis_growth):
            if growth > MAX_AXIS_GROWTH + 1e-6:
                errors.append(f"{asset_id}/{normalized}: {axis_name}-span growth {growth:.3f} > {MAX_AXIS_GROWTH:.2f} m")

        materials = {face[3] for face in final.faces}
        unknown = materials - SHARED_MATERIALS
        if unknown:
            errors.append(f"{asset_id}/{normalized}: unknown shared materials {sorted(unknown)}")

        path = ROOT / entry["path"]
        if not path.exists():
            errors.append(f"{asset_id}/{normalized}: generated OBJ missing: {path.relative_to(ROOT)}")
        else:
            actual_vertices, actual_faces, actual_materials = parse_obj(path)
            if actual_vertices != len(final.verts) or actual_faces != len(final.faces):
                errors.append(
                    f"{asset_id}/{normalized}: OBJ counts {actual_vertices}/{actual_faces} != expected {len(final.verts)}/{len(final.faces)}"
                )
            if actual_materials != materials:
                errors.append(f"{asset_id}/{normalized}: OBJ material set {sorted(actual_materials)} != expected {sorted(materials)}")
            hashes[(asset_id, normalized)] = hashlib.sha256(path.read_bytes()).hexdigest()

        seen.append((asset_id, normalized))
        rows.append((asset_id, normalized, len(base.faces), len(final.faces), face_delta, vert_delta, final_span))

    if len(seen) != 5:
        errors.append(f"expected exactly 5 signal-finale targets, found {len(seen)}: {sorted(seen)}")
    if len([x for x in seen if x[0] == "CS-015"]) != 1:
        errors.append("expected exactly one CS-015 mesh")
    required = {
        ("PR-014", "storm_damaged"),
        ("EN-019", "logs"),
        ("EN-019", "ropes"),
        ("EN-019", "stones"),
    }
    if not required.issubset(set(seen)):
        errors.append(f"missing canonical signal-finale targets: {sorted(required - set(seen))}")
    if len(set(hashes.values())) != len(hashes):
        errors.append("signal-finale target OBJ files must remain state-distinct")

    print("Project ØEN signal-finale geometry QA")
    print("  contract: visible failure/tension geometry, shared materials, <=0.65 m per-axis growth")
    for asset_id, variant, before, after, delta, vdelta, final_span in rows:
        print(
            f"  {asset_id}/{variant}: {before}->{after} faces (+{delta}), +{vdelta} verts, "
            f"span=({final_span[0]:.3f}, {final_span[1]:.3f}, {final_span[2]:.3f})"
        )

    if errors:
        print(f"\nFAILED with {len(errors)} issue(s):")
        for error in errors:
            print(" - " + error)
        return 1

    print("\nPASS: signal-finale meshes add readable structural failure/load cues without new materials or runaway bounds.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
