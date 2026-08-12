#!/usr/bin/env python3
"""Quality gate for refined Project ØEN survival/tool prop meshes."""
from __future__ import annotations
import json, sys
from collections import defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
MANIFEST=ROOT/"Assets"/"ProjectOEN"/"ProductionArt"/"Docs"/"production_art_manifest.json"

TARGETS={
 "PR-002":({"loose","carried","placed"},900,{"Rope"}),
 "PR-003":({"bundle","placed","damaged"},300,{"Wood","Rope"}),
 "PR-006":({"closed","open"},90,{"Cloth","Rope"}),
 "PR-007":({"full","empty"},120,{"Metal","Cloth","Rope"}),
 "PR-008":({"off","lit"},180,{"Metal","Water"}),
 "PR-009":({"unlit","lit","dying"},350,{"Wood","Cloth"}),
 "PR-010":({"small","medium","large"},150,{"Stone"}),
 "PR-011":({"small","medium"},90,{"Leaf","Wood"}),
 "PR-012":({"small","medium"},120,{"Metal","Rope"}),
 "PR-013":({"small","medium"},120,{"Cloth","Rope"}),
 "PR-014":({"clean","worn","storm_damaged"},45,{"Cloth","Wood","Rope"}),
 "PR-015":({"empty","cooking"},250,{"Metal"}),
 "PR-016":({"empty","collecting","full"},250,{"Wood","Tarp","Metal"}),
 "PR-017":({"clean","worn"},100,{"Wood","Rope"}),
 "PR-018":({"clean","worn"},90,{"Wood","Metal","Rope"}),
 "PR-019":({"inactive","active"},150,{"Metal","Rope"}),
}

def inspect(path:Path):
    v=f=0; mats=set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        s=raw.strip()
        if s.startswith("v "): v+=1
        elif s.startswith("f "): f+=1
        elif s.startswith("usemtl "): mats.add(s.split(None,1)[1])
    return v,f,mats

def main()->int:
    errors=[]
    if not MANIFEST.exists(): print("ERROR: missing production manifest"); return 1
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8")); by=defaultdict(list)
    for e in manifest:
        aid=str(e.get("asset_id",""))
        if aid in TARGETS and e.get("kind")=="mesh": by[aid].append(e)
    total_meshes=total_v=total_f=0
    print("Project ØEN survival/tool prop-art QA")
    for aid,(expected,min_faces,required_mats) in TARGETS.items():
        entries=by.get(aid,[]); variants={str(e.get("variant","default")) for e in entries}
        if variants!=expected:
            errors.append(f"{aid} variants mismatch: expected {sorted(expected)}, got {sorted(variants)}")
        family_faces=0
        for e in entries:
            variant=str(e.get("variant","default")); path=ROOT/e["path"]
            if not path.exists(): errors.append(f"{aid}/{variant} missing OBJ"); continue
            v,f,mats=inspect(path); total_meshes+=1; total_v+=v; total_f+=f; family_faces+=f
            if f<min_faces: errors.append(f"{aid}/{variant} too simple: {f} faces < {min_faces}")
            missing=required_mats-mats
            if missing: errors.append(f"{aid}/{variant} missing materials: {sorted(missing)}")
            if v<=f: errors.append(f"{aid}/{variant} suspicious geometry ratio: {v} vertices / {f} faces")
        print(f"  {aid}: {len(entries)} variants / {family_faces} faces")
    if total_meshes!=38: errors.append(f"Expected exactly 38 refined survival/tool meshes, found {total_meshes}")
    print(f"  total: {total_meshes} meshes / {total_v} vertices / {total_f} faces")
    if errors:
        print(f"\nFAILED with {len(errors)} issue(s):")
        for e in errors: print(" - "+e)
        return 1
    print("\nPASS: survival/tool prop refinement is complete and above geometry/material floors.")
    return 0

if __name__=="__main__": sys.exit(main())
