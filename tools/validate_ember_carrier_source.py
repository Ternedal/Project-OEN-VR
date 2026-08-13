#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REL_OBJ = Path("source_art/items/a5/ITM_EMBER_CARRIER_001.obj")
REL_MTL = Path("source_art/items/a5/ITM_EMBER_CARRIER_001.mtl")
REL_SVG = Path("source_art/items/a5/ITM_EMBER_CARRIER_001.svg")
REL_CONTRACT = Path("content/items/itm_ember_carrier.source.json")

def validate(root: Path = ROOT) -> list[str]:
    errors = []
    paths = [root/REL_OBJ, root/REL_MTL, root/REL_SVG, root/REL_CONTRACT]
    for p in paths:
        if not p.is_file(): errors.append(f"missing {p.relative_to(root)}")
    if errors: return errors
    text = (root/REL_OBJ).read_text(encoding="utf-8")
    vertices, face_count, groups = [], 0, set()
    for line in text.splitlines():
        if line.startswith("v "): vertices.append(tuple(float(x) for x in line.split()[1:4]))
        elif line.startswith("f "):
            face_count += 1; ids = [int(x.split("/")[0]) for x in line.split()[1:]]
            if len(set(ids)) < 3: errors.append("degenerate face")
        elif line.startswith("o "): groups.add(line[2:].strip())
    if len(vertices) < 24: errors.append("unexpectedly small mesh")
    if face_count < 18: errors.append("unexpectedly few faces")
    if "grip_bar" not in groups: errors.append("missing named grip_bar object")
    if vertices:
        xs,ys,zs=zip(*vertices); bounds=(max(xs)-min(xs),max(ys)-min(ys),max(zs)-min(zs))
        if not (0.32 <= bounds[0] <= 0.36): errors.append(f"width bound unexpected: {bounds[0]:.3f}")
        if not (0.32 <= bounds[1] <= 0.34): errors.append(f"depth bound unexpected: {bounds[1]:.3f}")
        if not (0.14 <= bounds[2] <= 0.18): errors.append(f"height bound unexpected: {bounds[2]:.3f}")
    mtl=(root/REL_MTL).read_text(encoding="utf-8")
    for name in ["carrier_body","heat_guard","grip","ember_bed"]:
        if f"newmtl {name}" not in mtl: errors.append(f"missing material {name}")
    svg=(root/REL_SVG).read_text(encoding="utf-8")
    for token in ["ITM_EMBER_CARRIER_001","COLD","EMBER","LIT","PRIMARY GRIP"]:
        if token not in svg: errors.append(f"SVG missing {token}")
    contract=json.loads((root/REL_CONTRACT).read_text(encoding="utf-8"))
    if contract.get("id") != "ITM_EMBER_CARRIER_001": errors.append("contract id mismatch")
    states=[s.get("id") for s in contract.get("logicalStates",[])]
    if states != ["cold","ember","lit"]: errors.append(f"state order mismatch: {states}")
    grips=contract.get("gripZones",[])
    if not grips or grips[0].get("id") != "PRIMARY_FRONT_HANDLE": errors.append("primary grip contract missing")
    cb=contract.get("approxBoundsMetres",{})
    if abs(cb.get("depthY",0)-0.33) > 0.005: errors.append(f"contract depth drift: {cb.get('depthY')}")
    return errors

def main() -> int:
    errors=validate()
    if errors:
        for e in errors: print("EMBER CARRIER INVALID:",e,file=sys.stderr)
        return 1
    print("Ember carrier source OK."); return 0

if __name__ == "__main__": raise SystemExit(main())
