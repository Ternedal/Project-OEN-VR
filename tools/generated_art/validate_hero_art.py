#!/usr/bin/env python3
"""Quality gate for the refined Project ØEN hero world assets."""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROD = ROOT / "Assets" / "ProjectOEN" / "ProductionArt"
MANIFEST = PROD / "Docs" / "production_art_manifest.json"

HERO_IDS = {
    "PR-001", "PR-004", "PR-005", "PR-020",
    "CS-001", "CS-002", "CS-003", "CS-004", "CS-005",
    "CS-006", "CS-007", "CS-008", "CS-009", "CS-010",
    "CS-011", "CS-012", "CS-013", "CS-014", "CS-015",
}

# Individual files must be materially richer than the broad coverage pass.
MIN_VERTICES = {
    "PR-001": 400,
    "PR-004": 500,
    "PR-005": 650,
    "PR-020": 500,
    "shelter": 400,
    "campfire": 500,
    "beacon": 350,
}


def parse_obj(path: Path):
    vertices = faces = 0
    materials = set()
    for raw in path.read_text(encoding="utf-8", errors="strict").splitlines():
        line = raw.strip()
        if line.startswith("v "):
            vertices += 1
        elif line.startswith("f "):
            faces += 1
        elif line.startswith("usemtl "):
            materials.add(line.split(None, 1)[1].strip())
    return vertices, faces, materials


def family(aid: str) -> str:
    if aid.startswith("PR-"):
        return aid
    n = int(aid.split("-")[1])
    if 1 <= n <= 5:
        return "shelter"
    if 6 <= n <= 10:
        return "campfire"
    return "beacon"


def main() -> int:
    if not MANIFEST.exists():
        print(f"ERROR: missing manifest: {MANIFEST}")
        return 1

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries = [e for e in manifest if e.get("kind") == "mesh" and e.get("asset_id") in HERO_IDS]
    errors = []
    counts = Counter()
    total_v = total_f = 0

    for entry in entries:
        aid = str(entry["asset_id"])
        path = ROOT / entry["path"]
        if not path.exists():
            errors.append(f"Missing refined hero OBJ: {entry['path']}")
            continue
        v, f, mats = parse_obj(path)
        fam = family(aid)
        counts[fam] += 1
        total_v += v; total_f += f
        floor = MIN_VERTICES[fam]
        if v < floor:
            errors.append(f"Hero mesh too simple: {path.name}: {v} vertices < {floor}")
        if f < 150:
            errors.append(f"Hero mesh too simple: {path.name}: {f} faces < 150")
        if aid in {"PR-001", "PR-004", "PR-005", "PR-020"} and len(mats) < 2:
            errors.append(f"Hero prop lacks material layering: {path.name}: {sorted(mats)}")

    # Coverage guarantees for every hero family/state.
    expected = {
        "PR-001": 4,
        "PR-004": 3,
        "PR-005": 4,
        "PR-020": 3,
        "shelter": 5,
        "campfire": 5,
        "beacon": 5,
    }
    for fam, minimum in expected.items():
        if counts[fam] < minimum:
            errors.append(f"Hero refinement coverage incomplete for {fam}: {counts[fam]} < {minimum}")

    # Active visual states must contain the dedicated Fire material.
    for entry in entries:
        aid = str(entry["asset_id"])
        if aid not in {"CS-008", "CS-009", "CS-014"}:
            continue
        _, _, mats = parse_obj(ROOT / entry["path"])
        if "Fire" not in mats:
            errors.append(f"Active fire state missing Fire material: {entry['path']}")

    # Aggregate floor catches accidental broad simplification.
    if total_v < 18000 or total_f < 8500:
        errors.append(f"Refined hero geometry unexpectedly small: vertices={total_v}, faces={total_f}")

    print("Project ØEN hero-art QA")
    print(f"  hero mesh files : {len(entries)}")
    print(f"  vertices        : {total_v}")
    print(f"  faces           : {total_f}")
    print(f"  family coverage : {dict(counts)}")

    if errors:
        print(f"\nFAILED with {len(errors)} issue(s):")
        for e in errors:
            print(" - " + e)
        return 1

    print("\nPASS: hero props and Stormnatten construction states meet refinement floors.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
