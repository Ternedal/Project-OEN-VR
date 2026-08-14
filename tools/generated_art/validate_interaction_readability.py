#!/usr/bin/env python3
"""Quality gate for the interaction-readable Project ØEN hero/tool refinement pass."""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from refine_hero_art import build as build_hero
from refine_prop_art import build as build_prop

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROD = ROOT / "Assets" / "ProjectOEN" / "ProductionArt"
MANIFEST = PROD / "Docs" / "production_art_manifest.json"

TARGET_IDS = {"PR-004", "PR-005", "PR-017", "PR-018", "PR-019", "PR-020"}
HERO_IDS = {"PR-004", "PR-005", "PR-020"}
EXPECTED_VARIANTS = {
    "PR-004": 3,
    "PR-005": 4,
    "PR-017": 2,
    "PR-018": 2,
    "PR-019": 2,
    "PR-020": 3,
}
MIN_VERTEX_DELTA = {
    "PR-004": 280,
    "PR-005": 780,
    "PR-017": 390,
    "PR-018": 240,
    "PR-019": 450,
    "PR-020": 380,
}
REQUIRED_MATERIALS = {
    "PR-004": {"Wood", "Metal", "Rope"},
    "PR-005": {"Metal", "Char", "Rope", "Cloth"},
    "PR-017": {"Wood", "Rope"},
    "PR-018": {"Wood", "Metal", "Rope"},
    "PR-019": {"Metal", "Rope"},
    "PR-020": {"Wood", "Metal", "Rope"},
}
ALLOWED_MATERIALS = {"Wood", "Rope", "Tarp", "Metal", "Stone", "Leaf", "Cloth", "Mud", "Fire", "Char", "Water"}


def parse_obj(path: Path):
    vertices = []
    faces = 0
    materials = set()
    for raw in path.read_text(encoding="utf-8", errors="strict").splitlines():
        line = raw.strip()
        if line.startswith("v "):
            parts = line.split()
            vertices.append(tuple(float(x) for x in parts[1:4]))
        elif line.startswith("f "):
            faces += 1
        elif line.startswith("usemtl "):
            materials.add(line.split(None, 1)[1].strip())
    return vertices, faces, materials


def max_dimension(points) -> float:
    if not points:
        return 0.0
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    zs = [p[2] for p in points]
    return max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))


def base_mesh(asset_id: str, variant: str):
    return build_hero(asset_id, variant) if asset_id in HERO_IDS else build_prop(asset_id, variant)


def main() -> int:
    if not MANIFEST.exists():
        print(f"ERROR: missing manifest: {MANIFEST}")
        return 1

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries = [e for e in manifest if e.get("kind") == "mesh" and e.get("asset_id") in TARGET_IDS]
    errors = []
    coverage = Counter()
    total_delta = 0

    for entry in entries:
        aid = str(entry["asset_id"])
        variant = str(entry.get("variant", "default"))
        path = ROOT / entry["path"]
        coverage[aid] += 1
        if not path.exists():
            errors.append(f"Missing interaction-refined OBJ: {entry['path']}")
            continue

        vertices, faces, materials = parse_obj(path)
        baseline = base_mesh(aid, variant)
        delta_v = len(vertices) - len(baseline.verts)
        delta_f = faces - len(baseline.faces)
        total_delta += max(0, delta_v)

        if delta_v < MIN_VERTEX_DELTA[aid]:
            errors.append(
                f"{aid}/{variant} lost readable interaction geometry: vertex delta {delta_v} < {MIN_VERTEX_DELTA[aid]}"
            )
        if delta_f <= 0:
            errors.append(f"{aid}/{variant} interaction pass did not increase face count")

        missing_mats = REQUIRED_MATERIALS[aid] - materials
        if missing_mats:
            errors.append(f"{aid}/{variant} missing interaction materials: {sorted(missing_mats)}")
        unexpected = materials - ALLOWED_MATERIALS
        if unexpected:
            errors.append(f"{aid}/{variant} introduced non-shared materials: {sorted(unexpected)}")

        output_size = max_dimension(vertices)
        baseline_size = max_dimension(baseline.verts)
        size_limit = max(baseline_size * 1.30, baseline_size + .35)
        if output_size > size_limit:
            errors.append(
                f"{aid}/{variant} interaction geometry expanded physical bounds too far: {output_size:.3f}m > {size_limit:.3f}m"
            )

        # State-specific cues remain meaningful rather than collapsing to one mesh treatment.
        if aid == "PR-005" and variant in ("active", "repaired") and "Fire" not in materials:
            errors.append(f"{aid}/{variant} must retain its bright radio state cue")
        if aid == "PR-017" and variant == "worn" and "Char" not in materials:
            errors.append("PR-017/worn must retain a visible worn striking-face cue")
        if aid == "PR-019" and variant == "active" and "Stone" not in materials:
            errors.append("PR-019/active must retain its braced anchor cue")

    for aid, expected in EXPECTED_VARIANTS.items():
        if coverage[aid] != expected:
            errors.append(f"Interaction refinement coverage drift for {aid}: {coverage[aid]} != {expected}")

    if len(entries) != sum(EXPECTED_VARIANTS.values()):
        errors.append(f"Unexpected interaction-refinement entry count: {len(entries)}")
    if total_delta < 6500:
        errors.append(f"Aggregate interaction-readable geometry delta unexpectedly small: {total_delta} vertices")

    print("Project ØEN interaction-readability QA")
    print(f"  refined mesh states : {len(entries)}")
    print(f"  family coverage     : {dict(coverage)}")
    print(f"  added vertices      : {total_delta}")

    if errors:
        print(f"\nFAILED with {len(errors)} issue(s):")
        for error in errors:
            print(" - " + error)
        return 1

    print("\nPASS: hero crates, radio and hand tools retain bounded, shared-material VR interaction cues.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
