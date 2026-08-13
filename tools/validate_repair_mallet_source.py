#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OBJ=Path("source_art/items/a5/ITM_HAMMER_001.obj")
MTL=Path("source_art/items/a5/ITM_HAMMER_001.mtl")
SVG=Path("source_art/items/a5/ITM_HAMMER_001.svg")
CONTRACT=Path("content/items/itm_repair_mallet.source.json")

def validate(root:Path=ROOT):
    errors=[]
    for rel in [OBJ,MTL,SVG,CONTRACT]:
        if not (root/rel).is_file(): errors.append(f"missing {rel}")
    if errors:return errors
    text=(root/OBJ).read_text(encoding="utf-8"); vs=[]; groups=set(); faces=0
    for line in text.splitlines():
        if line.startswith("v "):
            _,x,y,z=line.split();vs.append((float(x),float(y),float(z)))
        elif line.startswith("o "): groups.add(line[2:])
        elif line.startswith("f "):
            faces+=1; ids=[int(x) for x in line.split()[1:]]
            if len(set(ids))<3: errors.append("degenerate face")
    for g in ["grip_swell","contact_face_left","contact_face_right"]:
        if g not in groups: errors.append(f"missing group {g}")
    if vs:
        xs,ys,zs=zip(*vs); b=(max(xs)-min(xs),max(ys)-min(ys),max(zs)-min(zs))
        if not (0.16<=b[0]<=0.18): errors.append(f"width unexpected {b[0]:.3f}")
        if not (0.08<=b[1]<=0.09): errors.append(f"depth unexpected {b[1]:.3f}")
        if not (0.32<=b[2]<=0.35): errors.append(f"height unexpected {b[2]:.3f}")
    svg=(root/SVG).read_text(encoding="utf-8")
    for token in ["BROAD CONTACT","PRIMARY GRIP","utility, not weapon silhouette"]:
        if token not in svg: errors.append(f"SVG missing {token}")
    c=json.loads((root/CONTRACT).read_text(encoding="utf-8"))
    if c.get("id")!="ITM_HAMMER_001": errors.append("contract id mismatch")
    if len(c.get("contactZones",[]))!=2: errors.append("expected two contact zones")
    if not c.get("gripZones") or c["gripZones"][0].get("id")!="PRIMARY_HANDLE_GRIP": errors.append("primary grip missing")
    return errors

def main():
    e=validate()
    if e:
        for x in e: print("REPAIR MALLET INVALID:",x,file=sys.stderr)
        return 1
    print("Repair mallet source OK."); return 0
if __name__=="__main__":raise SystemExit(main())
