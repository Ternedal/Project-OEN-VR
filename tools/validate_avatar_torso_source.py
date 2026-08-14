#!/usr/bin/env python3
from pathlib import Path
import json, re
ROOT = Path(__file__).resolve().parents[1]
OBJ = ROOT/"source_art/avatar/base/CHR_TORSO_BASE_001.obj"
DATA = ROOT/"content/avatar/chr_torso_base.source.json"

def main():
    errors=[]
    text=OBJ.read_text(encoding="utf-8")
    verts=[]
    for line in text.splitlines():
        if line.startswith("v "):
            _,x,y,z=line.split()
            verts.append((float(x),float(y),float(z)))
    if len(verts)!=8:
        errors.append(f"expected 8 vertices, got {len(verts)}")
    if "g torso_reference" not in text:
        errors.append("missing torso_reference group")
    if verts:
        xs,ys,zs=zip(*verts)
        bounds=(max(xs)-min(xs),max(ys)-min(ys),max(zs)-min(zs))
        if not (0.35 <= bounds[0] <= 0.55 and 0.15 <= bounds[1] <= 0.30 and 0.40 <= bounds[2] <= 0.60):
            errors.append(f"unexpected torso bounds {bounds}")
    d=json.loads(DATA.read_text(encoding="utf-8"))
    if d.get("status")!="source-reference-ready-unity-pending":
        errors.append("bad status")
    pi=d.get("productIntent",{})
    if pi.get("mustNotRequire")!="Meta Avatar dependency":
        errors.append("Meta Avatar independence not explicit")
    if set(pi.get("trackedParts",[])) != {"head","left hand","right hand"}:
        errors.append("tracked part contract unexpected")
    if errors:
        for e in errors: print("ERROR:",e)
        return 1
    print("Avatar torso source reference OK: neutral silhouette and ownership boundaries valid.")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
