#!/usr/bin/env python3
"""Normalize MTL references for Project ØEN atlas-expansion OBJ files.

The shared production OBJ writer is intentionally optimized for canonical meshes two
levels below ProductionArt. Atlas-expansion meshes are grouped one level deeper by
category, so this post-pass rewrites only their `mtllib` line to the correct relative
path. No geometry, UVs, material assignments or Unity GUIDs are touched.
"""
from __future__ import annotations

import os
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PROD=ROOT/"Assets"/"ProductionArt"
MESH_ROOT=PROD/"Meshes"/"atlas_expansion"
MTL=PROD/"Materials"/"project_oen.mtl"


def main()->int:
    if not MTL.exists():
        raise SystemExit(f"Missing shared production MTL: {MTL}")
    objs=sorted(MESH_ROOT.rglob("*.obj"))
    if len(objs)!=24:
        raise SystemExit(f"Expected 24 atlas-expansion OBJ states, found {len(objs)}")
    changed=0
    for path in objs:
        rel=os.path.relpath(MTL,path.parent).replace(os.sep,"/")
        lines=path.read_text(encoding="utf-8").splitlines()
        found=False; out=[]
        for line in lines:
            if line.strip().startswith("mtllib "):
                out.append(f"mtllib {rel}"); found=True
            else:
                out.append(line)
        if not found:
            out.insert(0,f"mtllib {rel}")
        text="\n".join(out)+"\n"
        if text!=path.read_text(encoding="utf-8"):
            path.write_text(text,encoding="utf-8"); changed+=1
        resolved=(path.parent/rel).resolve()
        if resolved!=MTL.resolve() or not resolved.exists():
            raise SystemExit(f"Bad normalized MTL path: {path.relative_to(ROOT)} -> {rel}")
    print(f"Atlas-expansion MTL paths: verified {len(objs)} OBJ states; rewrote {changed}")
    return 0


if __name__=="__main__": raise SystemExit(main())
