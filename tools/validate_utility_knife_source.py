#!/usr/bin/env python3
from pathlib import Path
import json, re

ROOT = Path(__file__).resolve().parents[1]
OBJ = ROOT / "source_art/items/b1/ITM_KNIFE_001.obj"
CONTRACT = ROOT / "content/items/itm_knife.source.json"

def main():
    errors = []
    text = OBJ.read_text(encoding="utf-8")
    vertices = []
    groups = {
        line.split(maxsplit=1)[1]
        for line in text.splitlines()
        if line.startswith(("g ", "o "))
    }
    for line in text.splitlines():
        if line.startswith("v "):
            _, x, y, z = line.split()
            vertices.append((float(x), float(y), float(z)))
    if not vertices:
        errors.append("no vertices")
    else:
        xs, ys, zs = zip(*vertices)
        bounds = (max(xs)-min(xs), max(ys)-min(ys), max(zs)-min(zs))
        if bounds[0] > 0.31 or bounds[1] > 0.07 or bounds[2] > 0.05:
            errors.append(f"unexpected bounds {bounds}")
        if bounds[0] < 0.20:
            errors.append(f"tool too short/readability risk {bounds[0]:.3f}m")
    for required in ("grip_core","cutting_edge","finger_guard","blunt_nose"):
        if required not in groups:
            errors.append(f"missing group {required}")
    data = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if data.get("status") != "production-source-ready-unity-pending":
        errors.append("bad contract status")
    nwa = " ".join(data["productIntent"].get("nonWeaponAffordance", [])).lower()
    if "blunt" not in nwa or "combat" not in nwa:
        errors.append("non-weapon affordance contract incomplete")
    if errors:
        for e in errors:
            print("ERROR:", e)
        return 1
    print(f"Utility knife source OK: {len(vertices)} vertices; groups={sorted(groups)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
