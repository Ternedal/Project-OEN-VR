#!/usr/bin/env python3
"""Quality gate for remaining world/set-dressing refinement and true decal textures."""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from PIL import Image, ImageChops

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PROD=ROOT/"Assets"/"ProjectOEN"/"ProductionArt"
MANIFEST=PROD/"Docs"/"production_art_manifest.json"
DECAL_ROOT=PROD/"Decals"/"environment_set_dressing"

TARGETS={
 "CS-016":({"broken","mid_repair","repaired"},90,{"Wood","Metal"}),
 "EN-003":({"closed","broken"},400,{"Wood","Metal"}),
 "EN-004":({"small","medium"},500,{"Rope"}),
 "EN-011":({"small","medium","large"},2,set()),
 "EN-013":({"short","dense"},180,{"Wood","Leaf"}),
 "EN-014":({"straight","corner","arch"},500,{"Stone"}),
 "EN-015":({"stones","branches"},120,{"Stone"}),
 "EN-016":({"clean","worn","wet"},90,{"Cloth","Rope"}),
 "EN-017":({"pot","crate","utensils"},70,{"Wood"}),
 "EN-018":({"crate","sack","poles"},30,set()),
 "EN-019":({"logs","ropes","stones"},70,set()),
 "EN-020":({"frame","cloth","basin"},60,set()),
 "EN-021":({"unlit","lit"},120,{"Wood","Metal"}),
 "EN-022":({"plain","cloth_marked"},30,{"Wood"}),
 "EN-023":({"broken_shelter_parts","loose_cloth"},70,set()),
 "EN-024":({"slack","taut"},100,{"Wood","Rope"}),
 "EN-025":({"calm","storm"},2,set()),
}
DECAL_VARIANTS={
 "EN-011":{"small","medium","large"},
 "EN-025":{"calm","storm"},
}


def inspect_obj(path:Path):
    verts=faces=0; mats=set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        s=raw.strip()
        if s.startswith("v "): verts+=1
        elif s.startswith("f "): faces+=1
        elif s.startswith("usemtl "): mats.add(s.split(None,1)[1])
    return verts,faces,mats


def expected_decal_path(entry:dict)->Path:
    mesh_stem=Path(entry["path"]).stem
    return DECAL_ROOT/(mesh_stem+".png")


def inspect_decal(path:Path):
    with Image.open(path) as im:
        rgba=im.convert("RGBA")
        alpha=rgba.getchannel("A")
        bbox=alpha.getbbox()
        extrema=alpha.getextrema()
        nonzero=sum(1 for px in alpha.getdata() if px>0)
        opaqueish=sum(1 for px in alpha.getdata() if px>180)
        rgb=rgba.convert("RGB")
        return rgba.size,bbox,extrema,nonzero,opaqueish,rgb.getbbox()


def main()->int:
    errors=[]
    if not MANIFEST.exists():
        print(f"ERROR: missing manifest: {MANIFEST}")
        return 1
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8")); by=defaultdict(list)
    for e in manifest:
        aid=str(e.get("asset_id",""))
        if aid in TARGETS and e.get("kind")=="mesh": by[aid].append(e)

    total_meshes=total_v=total_f=0
    print("Project ØEN remaining set-dressing/world-art QA")
    for aid,(expected,min_faces,required_mats) in TARGETS.items():
        entries=by.get(aid,[]); variants={str(e.get("variant","default")) for e in entries}
        if variants!=expected:
            errors.append(f"{aid} variants mismatch: expected {sorted(expected)}, got {sorted(variants)}")
        family_faces=0
        for e in entries:
            variant=str(e.get("variant","default")); path=ROOT/e["path"]
            if not path.exists(): errors.append(f"{aid}/{variant} missing OBJ"); continue
            v,f,mats=inspect_obj(path); total_meshes+=1; total_v+=v; total_f+=f; family_faces+=f
            if f<min_faces: errors.append(f"{aid}/{variant} too simple: {f} faces < {min_faces}")
            missing=required_mats-mats
            if missing: errors.append(f"{aid}/{variant} missing materials: {sorted(missing)}")
            if v<=f and aid not in DECAL_VARIANTS:
                errors.append(f"{aid}/{variant} suspicious geometry ratio: {v} vertices / {f} faces")
        print(f"  {aid}: {len(entries)} variants / {family_faces} faces")

    if total_meshes!=42:
        errors.append(f"Expected exactly 42 refined set-dressing/world meshes, found {total_meshes}")

    decal_count=0
    for aid,variants in DECAL_VARIANTS.items():
        for e in by.get(aid,[]):
            variant=str(e.get("variant","default")); path=expected_decal_path(e)
            if variant not in variants: continue
            decal_count+=1
            if not path.exists():
                errors.append(f"{aid}/{variant} missing transparent decal texture: {path.relative_to(ROOT)}")
                continue
            meta=Path(str(path)+".meta")
            if not meta.exists(): errors.append(f"{aid}/{variant} missing decal .meta")
            else:
                mt=meta.read_text(encoding="utf-8")
                if "alphaIsTransparency: 1" not in mt or "enableMipMap: 1" not in mt:
                    errors.append(f"{aid}/{variant} decal importer contract missing alpha/mips")
            size,bbox,extrema,nonzero,opaqueish,rgb_bbox=inspect_decal(path)
            if size!=(1024,1024): errors.append(f"{aid}/{variant} decal must be 1024x1024, got {size}")
            if bbox is None or nonzero<12000: errors.append(f"{aid}/{variant} decal has too little visible alpha content")
            if extrema[0]!=0 or extrema[1]<100: errors.append(f"{aid}/{variant} decal alpha lacks transparent edge / useful range: {extrema}")
            if nonzero>=1024*1024*.90: errors.append(f"{aid}/{variant} decal alpha covers almost entire texture; not a cutout decal")
            if rgb_bbox is None: errors.append(f"{aid}/{variant} decal contains no RGB content")

    # Ensure variants do not accidentally collapse to byte-identical textures.
    for aid in DECAL_VARIANTS:
        paths=[expected_decal_path(e) for e in by.get(aid,[]) if expected_decal_path(e).exists()]
        blobs=[p.read_bytes() for p in paths]
        if len(blobs)!=len(set(blobs)):
            errors.append(f"{aid} decal variants are byte-identical; states must be visually distinct")

    if decal_count!=5: errors.append(f"Expected exactly 5 state-specific decal textures, found {decal_count}")

    print(f"  total world: {total_meshes} meshes / {total_v} vertices / {total_f} faces")
    print(f"  decals     : {decal_count} individual RGBA textures")
    if errors:
        print(f"\nFAILED with {len(errors)} issue(s):")
        for e in errors: print(" - "+e)
        return 1
    print("\nPASS: remaining set dressing, CS-016 and transparent decal assets are production-ready at repo level.")
    return 0

if __name__=="__main__": sys.exit(main())
