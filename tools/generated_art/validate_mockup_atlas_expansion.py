#!/usr/bin/env python3
"""Strict QA for the Project ØEN mockup-atlas expansion.

This gate complements, rather than changes, the stable 148-ID canonical production-art
validator. It proves that the additional families visible in the approved reference
atlas are actually materialized as separate Unity-importable files.
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from PIL import Image

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PROD=ROOT/"Assets"/"ProductionArt"
MANIFEST=PROD/"Docs"/"mockup_atlas_expansion_manifest.json"

EXPECTED_VARIANTS={
 "AX-BG-001":{"clear","golden_hour","storm"},
 "AX-BG-002":{"moonlit","firelit","lightning"},
 "AX-BG-003":{"calm","sunset","storm"},
 "AX-MAP-001":{"clean","marked","storm_route"},
 "AX-DOC-001":{"camp","storm_annotated","signal"},
 "AX-DOC-002":{"clean","annotated"},
 "AX-DOC-003":{"clean","storm_annotated"},
 "AX-WLD-001":{"default"},"AX-WLD-002":{"default"},"AX-WLD-003":{"default"},
 "AX-WLD-004":{"default"},"AX-WLD-005":{"default"},"AX-WLD-006":{"default"},"AX-WLD-007":{"default"},
 "AX-FOOD-001":{"whole","split"},"AX-FOOD-002":{"raw","cooked"},"AX-FOOD-003":{"mixed"},
 "AX-FOOD-004":{"raw","cooked"},"AX-FOOD-005":{"cooked"},
 "AX-SKY-001":{"calm","storm"},"AX-SKY-002":{"sun","moon"},"AX-SKY-003":{"calm","storm"},
 "AX-TOOL-001":{"clean","worn"},"AX-TOOL-002":{"clean","worn"},"AX-TOOL-003":{"clean","worn"},
 "AX-TOOL-004":{"clean","worn"},"AX-TOOL-005":{"clean","worn"},"AX-TOOL-006":{"clean","worn"},
 "AX-CRAFT-001":{"clean","storm"},"AX-CRAFT-002":{"stocked","used"},
 "AX-COM-001":{"off","active"},"AX-COM-002":{"folded","deployed"},
 "AX-COM-003":{"off","lit"},"AX-COM-004":{"coiled","loose"},
}
EXPECTED_CATEGORIES={
 "Key art & backgrounds","Maps & documents","Animals & wildlife","Food & cooking",
 "Weather & atmosphere","Tools & crafting","Radio & communication",
}


def parse_obj(path:Path,errors:list[str])->tuple[int,int]:
    verts=faces=0; mtllibs=[]; used=set()
    for n,raw in enumerate(path.read_text(encoding="utf-8",errors="strict").splitlines(),1):
        line=raw.strip()
        if line.startswith("v "): verts+=1
        elif line.startswith("f "):
            faces+=1
            for token in line.split()[1:]:
                try: idx=int(token.split('/')[0])
                except ValueError:
                    errors.append(f"Invalid OBJ index {token!r}: {path.relative_to(ROOT)}:{n}"); continue
                resolved=idx if idx>0 else verts+idx+1
                if resolved<1 or resolved>verts: errors.append(f"OBJ index out of range: {path.relative_to(ROOT)}:{n} -> {idx}")
        elif line.startswith("mtllib "): mtllibs.append(line.split(None,1)[1])
        elif line.startswith("usemtl "): used.add(line.split(None,1)[1])
    if verts<12 or faces<8: errors.append(f"Expansion mesh suspiciously small: {path.relative_to(ROOT)} v={verts} f={faces}")
    if not mtllibs: errors.append(f"Expansion mesh has no mtllib: {path.relative_to(ROOT)}")
    for rel in mtllibs:
        mtl=(path.parent/rel).resolve()
        if not mtl.exists():
            errors.append(f"Expansion mesh references missing MTL: {path.relative_to(ROOT)} -> {rel}"); continue
        defined={line.strip().split(None,1)[1] for line in mtl.read_text(encoding="utf-8",errors="replace").splitlines() if line.strip().startswith("newmtl ")}
        missing=used-defined
        if missing: errors.append(f"Expansion mesh uses undefined material(s): {path.relative_to(ROOT)} -> {sorted(missing)}")
    return verts,faces


def validate_sprite(path:Path,declared,errors:list[str])->None:
    try:
        with Image.open(path) as src:
            src.load(); rgba=src.convert("RGBA"); size=src.size; alpha=rgba.getchannel("A")
            if declared and list(size)!=list(declared): errors.append(f"Expansion sprite dimensions disagree: {path.relative_to(ROOT)} manifest={declared} actual={list(size)}")
            if min(size)<512: errors.append(f"Expansion sprite below 512px minimum: {path.relative_to(ROOT)} -> {size}")
            bbox=alpha.getbbox()
            if bbox is None: errors.append(f"Blank expansion sprite: {path.relative_to(ROOT)}"); return
            occupied=(bbox[2]-bbox[0])*(bbox[3]-bbox[1])/(size[0]*size[1])
            if occupied<.015: errors.append(f"Expansion sprite content too sparse: {path.relative_to(ROOT)} -> {occupied:.3%}")
            if alpha.getextrema()[1]<100: errors.append(f"Expansion sprite alpha peak too low: {path.relative_to(ROOT)} -> {alpha.getextrema()}")
    except Exception as exc:
        errors.append(f"Unreadable expansion sprite {path.relative_to(ROOT)}: {exc}")


def main()->int:
    errors=[]
    if not MANIFEST.exists():
        print(f"ERROR: expansion manifest missing: {MANIFEST}"); return 1
    data=json.loads(MANIFEST.read_text(encoding="utf-8")); entries=data.get("entries",[])
    if data.get("asset_id_count")!=34: errors.append(f"Expansion asset_id_count must be 34, got {data.get('asset_id_count')}")
    if data.get("entry_count")!=64 or len(entries)!=64: errors.append(f"Expansion must contain 64 entries, manifest={data.get('entry_count')} actual={len(entries)}")
    by=defaultdict(set); counts=Counter(); categories=set(); total_v=total_f=0; paths=set()
    for e in entries:
        aid=str(e.get("asset_id","")); variant=str(e.get("variant","")); kind=str(e.get("kind","")); category=str(e.get("category","")); rel=str(e.get("path",""))
        by[aid].add(variant); counts[kind]+=1; categories.add(category)
        if rel in paths: errors.append(f"Duplicate expansion output path: {rel}")
        paths.add(rel); path=ROOT/rel
        if not path.exists(): errors.append(f"Missing expansion output: {rel}"); continue
        meta=Path(str(path)+".meta")
        if not meta.exists(): errors.append(f"Missing expansion Unity .meta: {meta.relative_to(ROOT)}")
        else:
            text=meta.read_text(encoding="utf-8",errors="replace")
            if "guid:" not in text: errors.append(f"Expansion .meta missing GUID: {meta.relative_to(ROOT)}")
        if kind=="sprite": validate_sprite(path,e.get("dimensions"),errors)
        elif kind=="mesh":
            v,f=parse_obj(path,errors); total_v+=v; total_f+=f
        else: errors.append(f"Unexpected expansion kind {kind!r}: {rel}")
    if counts["sprite"]!=40 or counts["mesh"]!=24: errors.append(f"Expansion output mix must be 40 sprites + 24 meshes, got {dict(counts)}")
    if set(by)!=set(EXPECTED_VARIANTS): errors.append(f"Expansion IDs mismatch: missing={sorted(set(EXPECTED_VARIANTS)-set(by))}, unexpected={sorted(set(by)-set(EXPECTED_VARIANTS))}")
    for aid,expected in EXPECTED_VARIANTS.items():
        if by.get(aid,set())!=expected: errors.append(f"{aid} variants mismatch: expected={sorted(expected)} got={sorted(by.get(aid,set()))}")
    if categories!=EXPECTED_CATEGORIES: errors.append(f"Expansion categories mismatch: expected={sorted(EXPECTED_CATEGORIES)} got={sorted(categories)}")
    if total_v<2500 or total_f<1500: errors.append(f"Expansion mesh geometry suspiciously small overall: vertices={total_v}, faces={total_f}")

    print("Project ØEN mockup-atlas expansion QA")
    print(f"  asset families : {len(by)} / 34")
    print(f"  outputs        : {len(entries)} / 64")
    print(f"  sprites        : {counts['sprite']} / 40")
    print(f"  meshes         : {counts['mesh']} / 24")
    print(f"  mesh vertices  : {total_v}")
    print(f"  mesh faces     : {total_f}")
    if errors:
        print(f"\nFAILED with {len(errors)} issue(s):")
        for error in errors: print(" - "+error)
        return 1
    print("\nPASS: all atlas-expansion families are separate, nonblank, Unity-importable and structurally complete.")
    return 0


if __name__=="__main__": sys.exit(main())
