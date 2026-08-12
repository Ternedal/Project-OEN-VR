#!/usr/bin/env python3
"""Quality gate for the refined Stormnatten environment production meshes."""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROD = ROOT / "Assets" / "ProjectOEN" / "ProductionArt"
MANIFEST = PROD / "Docs" / "production_art_manifest.json"

TARGETS = {
    "EN-001": {"variants": {"large", "medium"}, "min_faces": 420, "materials": {"Wood", "Metal", "Rope"}},
    "EN-002": {"variants": {"small", "medium", "large"}, "min_faces": 70, "materials": {"Wood", "Metal"}},
    "EN-005": {"variants": {"small", "medium", "large"}, "min_faces": 150, "materials": {"Stone"}},
    "EN-006": {"variants": {"small", "medium", "large"}, "min_faces": 100, "materials": {"Wood"}},
    "EN-007": {"variants": {"young", "mature", "broken"}, "min_faces": 450, "materials": {"Wood", "Leaf"}},
    "EN-008": {"variants": {"small", "medium"}, "min_faces": 220, "materials": {"Wood", "Leaf"}},
    "EN-009": {"variants": {"small", "medium", "dense"}, "min_faces": 150, "materials": {"Wood", "Leaf"}},
    "EN-010": {"variants": {"short", "hanging", "dense"}, "min_faces": 300, "materials": {"Rope", "Leaf"}},
    "EN-012": {"variants": {"straight", "corner", "ledge"}, "min_faces": 700, "materials": {"Stone"}},
}


def inspect_obj(path: Path):
    verts=faces=0; materials=set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        line=raw.strip()
        if line.startswith("v "): verts+=1
        elif line.startswith("f "): faces+=1
        elif line.startswith("usemtl "): materials.add(line.split(None,1)[1])
    return verts,faces,materials


def main() -> int:
    errors=[]
    if not MANIFEST.exists():
        print(f"ERROR: missing manifest: {MANIFEST}")
        return 1

    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    by_id=defaultdict(list)
    for entry in manifest:
        aid=str(entry.get("asset_id",""))
        if aid in TARGETS and entry.get("kind")=="mesh":
            by_id[aid].append(entry)

    total_meshes=total_verts=total_faces=0
    print("Project ØEN Stormnatten environment-art QA")
    for aid,spec in TARGETS.items():
        entries=by_id.get(aid,[])
        variants={str(e.get("variant","default")) for e in entries}
        missing=spec["variants"]-variants
        unexpected=variants-spec["variants"]
        if missing: errors.append(f"{aid} missing variants: {sorted(missing)}")
        if unexpected: errors.append(f"{aid} unexpected variants: {sorted(unexpected)}")

        family_faces=0
        for entry in entries:
            path=ROOT/entry["path"]
            variant=str(entry.get("variant","default"))
            if not path.exists():
                errors.append(f"{aid}/{variant} missing OBJ: {path.relative_to(ROOT)}")
                continue
            verts,faces,mats=inspect_obj(path)
            total_meshes+=1; total_verts+=verts; total_faces+=faces; family_faces+=faces
            if faces < spec["min_faces"]:
                errors.append(f"{aid}/{variant} too simple: {faces} faces < {spec['min_faces']}")
            missing_mats=spec["materials"]-mats
            if missing_mats:
                errors.append(f"{aid}/{variant} missing readable materials: {sorted(missing_mats)}")
            if verts <= faces:
                errors.append(f"{aid}/{variant} suspicious geometry ratio: {verts} vertices / {faces} faces")

        print(f"  {aid}: {len(entries)} variants / {family_faces} faces")

    if total_meshes < 25:
        errors.append(f"Expected at least 25 refined environment meshes, found {total_meshes}")

    print(f"  total: {total_meshes} meshes / {total_verts} vertices / {total_faces} faces")
    if errors:
        print(f"\nFAILED with {len(errors)} issue(s):")
        for e in errors: print(" - "+e)
        return 1

    print("\nPASS: Stormnatten environment refinement is complete and above geometry/material floors.")
    return 0

if __name__=="__main__":
    sys.exit(main())
