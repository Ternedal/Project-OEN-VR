#!/usr/bin/env python3
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
M=ROOT/"docs/38_SOURCE_ASSET_MANIFEST.md"
I=ROOT/"content/source_inventory.source.json"
EXPECTED={
"ENV_EPILOGUE_001":"source_art/environment/c1/ENV_EPILOGUE_001.svg",
"PRP_FIREPIT_001":"source_art/props/a5/PRP_FIREPIT_001.obj",
"PRP_WATERPROOF_ENDING_CRATE_001":"source_art/props/a5/PRP_WATERPROOF_ENDING_CRATE_001.obj",
"ITM_EMBER_CARRIER_001":"source_art/items/a5/ITM_EMBER_CARRIER_001.obj",
"ITM_KNIFE_001":"source_art/items/b1/ITM_KNIFE_001.obj",
"ITM_HAMMER_001":"source_art/items/a5/ITM_HAMMER_001.obj",
"VFX_ROPE_STRAIN_001":"source_art/vfx/a3/VFX_ROPE_STRAIN_001.svg",
"CHR_HAND_P1_001":"source_art/avatar/base/CHR_HAND_P1_001.svg",
"CHR_HAND_P2_001":"source_art/avatar/base/CHR_HAND_P2_001.svg",
"CHR_TORSO_BASE_001":"source_art/avatar/base/CHR_TORSO_BASE_001.svg"}
def line(text,aid): return next((x for x in text.splitlines() if f"`{aid}`" in x),"")
def main():
    errors=[]; text=M.read_text(encoding="utf-8")
    for aid,path in EXPECTED.items():
        l=line(text,aid)
        if path not in l: errors.append(f"manifest path missing {aid}")
        if not (ROOT/path).exists(): errors.append(f"source missing {aid}")
    for aid,phrase in {
      "ENV_EPILOGUE_001":"Spec klar","PRP_WATERPROOF_ENDING_CRATE_001":"Spec klar",
      "ITM_EMBER_CARRIER_001":"ikke committed","ITM_KNIFE_001":"Mangler produktion",
      "ITM_HAMMER_001":"ikke committed","VFX_ROPE_STRAIN_001":"Mangler særskilt",
      "CHR_HAND_P1_001":"Mangler produktion","CHR_HAND_P2_001":"Mangler produktion",
      "CHR_TORSO_BASE_001":"Mangler produktion"}.items():
        if phrase.lower() in line(text,aid).lower(): errors.append(f"stale {aid}")
    inv=json.loads(I.read_text(encoding="utf-8"))
    pk={p.get("id"):p for p in inv.get("packages",[])}
    if "ITM_KNIFE_001" not in pk.get("B1_WORLD_ITEMS",{}).get("producedIds",[]): errors.append("knife inventory")
    if pk.get("CHARACTER_TORSO",{}).get("producedIds")!=["CHR_TORSO_BASE_001"]: errors.append("torso inventory")
    if pk.get("C1_EPILOGUE",{}).get("producedIds")!=["ENV_EPILOGUE_001"]: errors.append("epilogue inventory")
    if errors:
        for e in errors: print("ERROR:",e)
        return 1
    print("V15 source closeout OK.")
    return 0
if __name__=="__main__": raise SystemExit(main())
