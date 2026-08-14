#!/usr/bin/env python3
"""Generate production source meshes for the B1 shared world-item set."""

from __future__ import annotations

from pathlib import Path

from generate_camp_source_meshes import Obj


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "source_art" / "items" / "b1" / "production"

MTL = """# B1 source materials; final Unity shaders remain runtime-owned.
newmtl MAT_WOOD
Kd 0.49 0.34 0.24
map_Kd ../../../props/a2/production/textures/MAT_WEATHERED_WOOD_001.png
newmtl MAT_FIBER
Kd 0.68 0.61 0.43
map_Kd ../../../props/a2/production/textures/MAT_AGED_CANVAS_001.png
newmtl MAT_FOLIAGE
Kd 0.34 0.48 0.29
map_Kd ../../../props/a2/production/textures/MAT_AGED_CANVAS_001.png
newmtl MAT_CANVAS
Kd 0.45 0.39 0.29
map_Kd ../../../props/a2/production/textures/MAT_AGED_CANVAS_001.png
newmtl MAT_METAL
Kd 0.19 0.22 0.22
map_Kd ../../../props/a2/production/textures/MAT_WORN_IRON_001.png
"""


def item(name: str) -> Obj:
    return Obj(name, OUT, MTL)


def wood_bundle():
    o = item("ITM_WOOD_BUNDLE_001")
    logs = [(-.05,.12,-.10),(.02,.17,.02),(-.03,.22,.11),(.04,.27,-.04),(-.02,.31,.07)]
    for index,(x,y,z) in enumerate(logs,1):
        o.beam(f"ReadableLog_{index}",(-.34+x,y,z),(.34+x,y+.06,z+.03),.09)
    o.material("MAT_FIBER")
    o.beam("FrontBinding",(-.18,.07,-.16),(-.18,.37,.17),.045)
    o.beam("RearBinding",(.18,.08,-.16),(.18,.38,.17),.045)
    return o.write()


def fiber_bundle():
    o = item("ITM_FIBER_BUNDLE_001"); o.material("MAT_FIBER")
    for y,r in ((.04,.20),(.075,.19),(.11,.18),(.145,.17),(.18,.16)):
        o.torus("BraidedFiberMass",(0,y,0),r,.022,20,6)
    o.beam("DistinctLooseFiber",(.10,.18,.10),(.34,.25,.02),.035)
    o.material("MAT_CANVAS"); o.beam("BundleTie",(-.22,.16,0),(.22,.16,0),.045)
    return o.write()


def herb_bundle():
    o = item("ITM_HERB_BUNDLE_001"); o.material("MAT_FOLIAGE")
    tips=[(-.20,.52,-.04),(-.10,.62,.05),(0,.67,-.02),(.11,.60,.04),(.21,.50,-.04)]
    for index,tip in enumerate(tips,1):
        o.beam(f"HerbStem_{index}",(0,.06,0),tip,.026)
        tx,ty,tz=tip
        o.beam(f"BroadLeafA_{index}",(tx*.55,ty*.55,tz),(tx-.09,ty-.10,tz+.04),.065)
        o.beam(f"BroadLeafB_{index}",(tx*.66,ty*.66,tz),(tx+.09,ty-.08,tz-.04),.065)
    o.material("MAT_FIBER"); o.beam("ReadableBundleTie",(-.16,.16,0),(.16,.16,0),.045)
    o.material("MAT_CANVAS"); o.box("SimpleLabel",(0,.10,-.055),(.16,.09,.018))
    return o.write()


def food_parcel():
    o = item("ITM_FOOD_PARCEL_001"); o.material("MAT_CANVAS")
    o.box("SealedParcel",(0,.20,0),(.50,.40,.38)); o.box("FoldedTop",(0,.43,0),(.43,.08,.33))
    o.material("MAT_FIBER")
    o.box("CrossStrapLong",(0,.475,0),(.08,.025,.40)); o.box("CrossStrapWide",(0,.477,0),(.52,.028,.07))
    o.material("MAT_WOOD"); o.box("ReadableFoodSeal",(0,.49,-.055),(.12,.025,.12))
    return o.write()


def general_supplies():
    o = item("ITM_GENERAL_SUPPLIES_001"); o.material("MAT_METAL")
    o.box("SharedKitBody",(0,.22,0),(.56,.42,.34)); o.box("FrontPocket",(-.13,.22,-.18),(.21,.16,.035)); o.box("FrontPocket",(.14,.22,-.18),(.17,.16,.035))
    o.beam("LargeCarryHandle",(-.15,.44,0),(.15,.44,0),.055)
    o.beam("HandleMount",(-.15,.38,0),(-.15,.47,0),.055); o.beam("HandleMount",(.15,.38,0),(.15,.47,0),.055)
    o.material("MAT_CANVAS"); o.box("BulkCategoryA",(-.13,.46,0),(.18,.12,.22)); o.box("BulkCategoryB",(.13,.46,0),(.16,.16,.19))
    return o.write()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    files=[wood_bundle(),fiber_bundle(),herb_bundle(),food_parcel(),general_supplies()]
    print("\n".join(str(path.relative_to(ROOT)) for path in files))


if __name__ == "__main__":
    main()
