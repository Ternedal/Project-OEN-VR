#!/usr/bin/env python3
"""Generate the remaining production-ready non-Unity source meshes.

This batch closes source-reference-only gaps for priority interactables and the
reuse-first epilogue.  Meshes are metre-scaled, UV mapped and split into named
semantic parts.  Unity colliders, shaders, rigging and device QA remain runtime
work and are intentionally not encoded here.
"""

from __future__ import annotations

import math
from pathlib import Path

from generate_camp_source_meshes import Obj


ROOT = Path(__file__).resolve().parents[1]
A2 = ROOT / "source_art" / "props" / "a2"
A5_ITEMS = ROOT / "source_art" / "items" / "a5"
B1_ITEMS = ROOT / "source_art" / "items" / "b1"
A5_PROPS = ROOT / "source_art" / "props" / "a5"
C1 = ROOT / "source_art" / "environment" / "c1"

A2_MTL = """# PROJECT OEN A2 item production materials; Unity shaders remain runtime-owned.
newmtl MAT_WOOD
Kd 0.52 0.34 0.20
map_Kd production/textures/MAT_WEATHERED_WOOD_001.png
newmtl MAT_METAL
Kd 0.18 0.19 0.18
map_Kd production/textures/MAT_WORN_IRON_001.png
newmtl MAT_FIBER
Kd 0.66 0.54 0.35
map_Kd production/textures/MAT_AGED_CANVAS_001.png
newmtl MAT_TINDER
Kd 0.43 0.27 0.14
map_Kd production/textures/MAT_WEATHERED_WOOD_001.png
newmtl MAT_EMBER
Kd 0.72 0.24 0.08
map_Kd production/textures/MAT_AGED_CANVAS_001.png
"""

A5_ITEM_MTL = """# PROJECT OEN A5 item production materials; Unity shaders remain runtime-owned.
newmtl MAT_WOOD
Kd 0.52 0.34 0.20
map_Kd ../../props/a2/production/textures/MAT_WEATHERED_WOOD_001.png
newmtl MAT_METAL
Kd 0.18 0.19 0.18
map_Kd ../../props/a2/production/textures/MAT_WORN_IRON_001.png
newmtl MAT_CANVAS
Kd 0.58 0.47 0.35
map_Kd ../../props/a2/production/textures/MAT_AGED_CANVAS_001.png
newmtl MAT_PAPER
Kd 0.72 0.65 0.48
map_Kd ../../props/a2/production/textures/MAT_AGED_CANVAS_001.png
newmtl MAT_EMBER
Kd 0.73 0.25 0.07
map_Kd ../../props/a2/production/textures/MAT_AGED_CANVAS_001.png
newmtl MAT_DARK
Kd 0.09 0.08 0.07
map_Kd ../../props/a2/production/textures/MAT_WORN_IRON_001.png
newmtl carrier_body
Kd 0.18 0.19 0.18
map_Kd ../../props/a2/production/textures/MAT_WORN_IRON_001.png
newmtl heat_guard
Kd 0.27 0.25 0.22
map_Kd ../../props/a2/production/textures/MAT_WORN_IRON_001.png
newmtl grip
Kd 0.09 0.08 0.07
map_Kd ../../props/a2/production/textures/MAT_AGED_CANVAS_001.png
newmtl ember_bed
Kd 0.73 0.25 0.07
map_Kd ../../props/a2/production/textures/MAT_AGED_CANVAS_001.png
"""

B1_ITEM_MTL = """# PROJECT OEN B1 utility item production materials; Unity shaders remain runtime-owned.
newmtl MAT_GRIP
Kd 0.25 0.22 0.18
map_Kd ../../props/a2/production/textures/MAT_AGED_CANVAS_001.png
newmtl MAT_METAL
Kd 0.27 0.29 0.28
map_Kd ../../props/a2/production/textures/MAT_WORN_IRON_001.png
newmtl MAT_EDGE
Kd 0.44 0.46 0.43
map_Kd ../../props/a2/production/textures/MAT_WORN_IRON_001.png
"""

A5_PROP_MTL = """# PROJECT OEN A5 prop production materials; Unity shaders remain runtime-owned.
newmtl MAT_WOOD
Kd 0.52 0.34 0.20
map_Kd ../a2/production/textures/MAT_WEATHERED_WOOD_001.png
newmtl MAT_METAL
Kd 0.18 0.19 0.18
map_Kd ../a2/production/textures/MAT_WORN_IRON_001.png
newmtl MAT_STONE
Kd 0.29 0.29 0.27
map_Kd ../a2/production/textures/MAT_BEACH_STONE_001.png
newmtl MAT_CANVAS
Kd 0.60 0.50 0.37
map_Kd ../a2/production/textures/MAT_AGED_CANVAS_001.png
newmtl MAT_CHAR
Kd 0.08 0.07 0.06
map_Kd ../a2/production/textures/MAT_WORN_IRON_001.png
"""

C1_MTL = """# PROJECT OEN reuse-first epilogue source materials; Unity shaders remain runtime-owned.
newmtl MAT_SAND_DRY
Kd 0.62 0.54 0.39
map_Kd ../a4/production/textures/MAT_CAMP_DRY_SAND_001.png
newmtl MAT_SAND_WET
Kd 0.31 0.31 0.27
map_Kd ../a4/production/textures/MAT_CAMP_WET_SAND_001.png
newmtl MAT_WOOD
Kd 0.49 0.32 0.20
map_Kd ../../props/a2/production/textures/MAT_WEATHERED_WOOD_001.png
newmtl MAT_STONE
Kd 0.29 0.29 0.27
map_Kd ../../props/a2/production/textures/MAT_BEACH_STONE_001.png
newmtl MAT_CANVAS
Kd 0.62 0.53 0.39
map_Kd ../../props/a2/production/textures/MAT_AGED_CANVAS_001.png
newmtl MAT_METAL
Kd 0.20 0.21 0.20
map_Kd ../../props/a2/production/textures/MAT_WORN_IRON_001.png
"""


def mesh(name: str, out: Path, mtl: str) -> Obj:
    out.mkdir(parents=True, exist_ok=True)
    return Obj(name, out, mtl)


def firesteel() -> Path:
    o = mesh("ITM_FIRESTEEL_001", A2, A2_MTL)
    o.material("MAT_METAL")
    o.beam("ReadableFerroRod", (-0.065, 0.085, 0), (0.115, 0.085, 0), 0.027)
    o.box("BroadStrikeZone", (0.105, 0.085, 0), (0.045, 0.064, 0.054))
    o.material("MAT_WOOD")
    o.box("OversizePrimaryGrip", (-0.125, 0.085, 0), (0.115, 0.095, 0.078))
    o.material("MAT_METAL")
    o.torus("TetherRing", (-0.185, 0.085, 0), 0.027, 0.009, 12, 5)
    o.box("SeparatedStrikerPlate", (0.015, 0.155, 0.075), (0.12, 0.05, 0.025))
    return o.write()


def tinder() -> Path:
    o = mesh("ITM_TINDER_001", A2, A2_MTL)
    o.material("MAT_TINDER")
    for index, (angle, y, length) in enumerate(
        ((-0.75, 0.07, 0.25), (-0.35, 0.10, 0.27), (0.10, 0.12, 0.24), (0.48, 0.08, 0.26), (0.82, 0.11, 0.22)), 1
    ):
        dx, dz = math.cos(angle) * length / 2, math.sin(angle) * length / 2
        o.beam(f"BroadDryFiber_{index}", (-dx, y, -dz), (dx, y + 0.025, dz), 0.038)
    o.material("MAT_FIBER")
    for y, radius in ((0.045, 0.105), (0.08, 0.095), (0.115, 0.082)):
        o.torus("NestSilhouette", (0, y, 0), radius, 0.022, 16, 6)
    o.material("MAT_EMBER")
    o.box("EmberInsertionTarget", (0, 0.155, 0), (0.085, 0.025, 0.085))
    return o.write()


def rope_coil() -> Path:
    o = mesh("ITM_ROPE_COIL_001", A2, A2_MTL)
    o.material("MAT_FIBER")
    for y, radius in ((0.035, 0.18), (0.07, 0.17), (0.105, 0.16), (0.14, 0.15)):
        o.torus("ChunkyCarryCoil", (0, y, 0), radius, 0.024, 20, 6)
    o.beam("ReadableLooseEnd", (0.14, 0.145, 0.02), (0.34, 0.055, 0.11), 0.046)
    o.torus("OversizeEndLoop", (0.34, 0.055, 0.11), 0.06, 0.018, 12, 5)
    o.material("MAT_WOOD")
    o.box("CarryBand", (0, 0.16, 0), (0.10, 0.025, 0.39))
    return o.write()


def cloth_item() -> Path:
    o = mesh("ITM_CLOTH_001", A5_ITEMS, A5_ITEM_MTL)
    o.material("MAT_CANVAS")
    o.box("FoldedClothBase", (0, 0, 0.035), (0.32, 0.24, 0.07))
    o.box("ReadableFoldLayerA", (-0.035, 0.015, 0.078), (0.25, 0.20, 0.035))
    o.box("ReadableFoldLayerB", (0.055, -0.015, 0.108), (0.19, 0.16, 0.025))
    o.material("MAT_PAPER")
    o.beam("BroadFoldSeamA", (-0.14, -0.08, 0.126), (0.12, 0.07, 0.126), 0.018)
    o.beam("BroadFoldSeamB", (-0.11, 0.07, 0.127), (0.12, -0.07, 0.127), 0.018)
    o.material("MAT_DARK")
    o.box("PrimaryGripEdge", (0, -0.122, 0.065), (0.19, 0.018, 0.07))
    return o.write()


def map_fragment() -> Path:
    o = mesh("ITM_MAP_FRAGMENT_001", A5_ITEMS, A5_ITEM_MTL)
    o.material("MAT_PAPER")
    o.box("FictionalMapSurface", (0, 0, 0.008), (0.36, 0.25, 0.016))
    o.beam("FoldRidgeLeft", (-0.06, -0.12, 0.019), (-0.06, 0.12, 0.019), 0.012)
    o.beam("FoldRidgeRight", (0.07, -0.12, 0.019), (0.07, 0.12, 0.019), 0.012)
    o.material("MAT_METAL")
    o.beam("ReadableRouteLine", (-0.14, -0.07, 0.028), (0.13, 0.07, 0.028), 0.015)
    o.box("SignalDestinationShape", (0.12, 0.075, 0.033), (0.055, 0.055, 0.018))
    o.material("MAT_CANVAS")
    o.box("PrimaryGripMargin", (-0.175, 0, 0.026), (0.02, 0.13, 0.025))
    return o.write()


def radio_battery() -> Path:
    o = mesh("ITM_RADIO_BATTERY_001", A5_ITEMS, A5_ITEM_MTL)
    o.material("MAT_METAL")
    o.box("BatteryBody", (0, 0, 0.12), (0.16, 0.085, 0.24))
    o.box("KeyedSocketRailLeft", (-0.067, 0, 0.105), (0.026, 0.105, 0.105))
    o.box("KeyedSocketRailRight", (0.067, 0, 0.145), (0.026, 0.105, 0.105))
    o.material("MAT_WOOD")
    o.box("TerminalPositive", (-0.042, 0, 0.257), (0.032, 0.05, 0.034))
    o.box("TerminalNegative", (0.042, 0, 0.257), (0.032, 0.05, 0.034))
    o.material("MAT_CANVAS")
    o.box("LargePowerGlyph", (0, -0.047, 0.145), (0.07, 0.012, 0.085))
    o.material("MAT_DARK")
    o.box("PrimaryGripBand", (0, 0, 0.045), (0.17, 0.095, 0.055))
    return o.write()


def repair_mallet() -> Path:
    o = mesh("ITM_HAMMER_001", A5_ITEMS, A5_ITEM_MTL)
    o.material("MAT_WOOD")
    o.box("handle_core", (0, 0, 0.145), (0.048, 0.048, 0.29))
    o.material("MAT_DARK")
    o.box("grip_swell", (0, 0, 0.066), (0.065, 0.065, 0.125))
    o.material("MAT_METAL")
    o.box("head_core", (0, 0, 0.304), (0.134, 0.086, 0.070))
    o.box("contact_face_left", (-0.077, 0, 0.304), (0.020, 0.086, 0.068))
    o.box("contact_face_right", (0.077, 0, 0.304), (0.020, 0.086, 0.068))
    o.material("MAT_CANVAS")
    o.box("repair_identity_band", (0, -0.041, 0.304), (0.075, 0.012, 0.045))
    return o.write()


def ember_carrier() -> Path:
    o = mesh("ITM_EMBER_CARRIER_001", A5_ITEMS, A5_ITEM_MTL)
    o.material("carrier_body")
    o.box("carrier_body", (0, 0, 0.045), (0.34, 0.24, 0.09))
    o.material("heat_guard")
    o.box("heat_guard", (0, 0.15, 0.098), (0.30, 0.03, 0.120))
    o.box("front_guard", (0, -0.15, 0.098), (0.30, 0.03, 0.120))
    o.material("grip")
    o.box("grip_post_left", (-0.095, -0.15, 0.125), (0.030, 0.030, 0.066))
    o.box("grip_post_right", (0.095, -0.15, 0.125), (0.030, 0.030, 0.066))
    o.box("grip_bar", (0, -0.15, 0.151), (0.22, 0.030, 0.014))
    o.material("ember_bed")
    o.box("ember_bed", (0, 0, 0.101), (0.22, 0.14, 0.022))
    for index, x in enumerate((-0.065, 0, 0.065), 1):
        o.box(f"raised_ember_shape_{index}", (x, 0, 0.125 + 0.006 * (index % 2)), (0.038, 0.052, 0.040))
    return o.write()


def utility_knife() -> Path:
    o = mesh("ITM_KNIFE_001", B1_ITEMS, B1_ITEM_MTL)
    o.material("MAT_GRIP")
    o.box("grip_core", (-0.0675, 0, 0), (0.165, 0.058, 0.046))
    o.material("MAT_METAL")
    o.box("blade_core", (0.080, 0, 0), (0.130, 0.040, 0.030))
    o.box("blunt_nose", (0.150, 0, 0), (0.020, 0.044, 0.038))
    o.box("finger_guard", (0.017, 0, 0), (0.025, 0.066, 0.050))
    o.material("MAT_EDGE")
    o.box("cutting_edge", (0.080, -0.023, -0.014), (0.115, 0.010, 0.012))
    return o.write()


def dry_fuel_cache() -> Path:
    o = mesh("PRP_DRY_FUEL_CACHE_001", A5_PROPS, A5_PROP_MTL)
    o.material("MAT_WOOD")
    o.box("ProtectedCacheBody", (0, 0.23, 0), (0.66, 0.46, 0.48))
    for index, z in enumerate((-0.15, 0, 0.15), 1):
        o.beam(f"DryFuelLog_{index}", (-0.23, 0.31, z), (0.23, 0.31, z), 0.09)
    o.material("MAT_CANVAS")
    o.box("WeatherCover", (0, 0.50, 0), (0.72, 0.08, 0.54))
    o.box("DryStatePanel", (0, 0.545, -0.18), (0.30, 0.025, 0.12))
    o.material("MAT_METAL")
    o.beam("LargePullHandle", (-0.14, 0.41, -0.265), (0.14, 0.41, -0.265), 0.055)
    return o.write()


def a5_firepit() -> Path:
    o = mesh("PRP_FIREPIT_001", A5_PROPS, A5_PROP_MTL)
    o.material("MAT_STONE")
    for index in range(14):
        angle = 2 * math.pi * index / 14
        o.cylinder(f"RingStone_{index + 1}", (0.36 * math.cos(angle), 0.105, 0.36 * math.sin(angle)), 0.10, 0.21, 8)
    o.material("MAT_CHAR")
    o.beam("ColdLogA", (-0.28, 0.16, -0.20), (0.28, 0.16, 0.20), 0.10)
    o.beam("ColdLogB", (-0.28, 0.17, 0.20), (0.28, 0.17, -0.20), 0.10)
    o.cylinder("EmberStateSocket", (0, 0.08, 0), 0.30, 0.05, 14)
    return o.write()


def signal_fuel() -> Path:
    o = mesh("PRP_SIGNAL_FUEL_001", A5_PROPS, A5_PROP_MTL)
    o.material("MAT_WOOD")
    for index, (x, z) in enumerate(((-0.12, -0.10), (0.02, 0.02), (0.14, -0.03), (-0.02, 0.13)), 1):
        o.beam(f"SignalFuelLog_{index}", (-0.28 + x, 0.10 + index * 0.045, z), (0.28 + x, 0.14 + index * 0.045, z), 0.10)
    o.material("MAT_CANVAS")
    o.box("HighVisibilityCarryWrap", (0, 0.26, 0), (0.15, 0.035, 0.48))
    o.material("MAT_METAL")
    o.beam("SignalFrameAttachmentLoop", (-0.13, 0.31, 0), (0.13, 0.31, 0), 0.05)
    return o.write()


def waterproof_ending_crate() -> Path:
    o = mesh("PRP_WATERPROOF_ENDING_CRATE_001", A5_PROPS, A5_PROP_MTL)
    o.material("MAT_WOOD")
    o.box("WaterproofCrateBody", (0, 0.25, 0), (0.82, 0.50, 0.58))
    o.box("RaisedWaterproofLid", (0, 0.55, 0), (0.86, 0.10, 0.62))
    for x in (-0.36, 0.36):
        o.box("CornerProtection", (x, 0.28, 0), (0.075, 0.54, 0.63))
    o.material("MAT_CANVAS")
    o.box("BroadGasket", (0, 0.495, 0), (0.79, 0.035, 0.55))
    o.box("NeutralMementoSlot", (-0.18, 0.615, 0), (0.25, 0.025, 0.20))
    o.box("PrivatePayloadSlotCover", (0.18, 0.615, 0), (0.25, 0.025, 0.20))
    o.material("MAT_METAL")
    o.box("DeliberateRevealLatch", (0, 0.48, -0.325), (0.18, 0.16, 0.05))
    for x in (-0.43, 0.43):
        o.beam("BroadCarryHandle", (x, 0.24, -0.12), (x, 0.24, 0.12), 0.06)
    return o.write()


def a5_wind_shield() -> Path:
    o = mesh("PRP_WIND_SHIELD_001", A5_PROPS, A5_PROP_MTL)
    o.material("MAT_METAL")
    for index, (x, z, offset) in enumerate(((-0.18, 0.035, -0.06), (-0.09, 0.005, -0.025), (0, 0, 0), (0.09, 0.005, 0.025), (0.18, 0.035, 0.06)), 1):
        o.beam(f"CurvedShieldSlat_{index}", (x - 0.045, 0.03, z), (x + 0.045, 0.41, z + offset), 0.085)
    o.beam("TopOrientationRail", (-0.24, 0.42, 0.04), (0.24, 0.42, 0.04), 0.045)
    o.material("MAT_WOOD")
    o.beam("LargeHandle", (-0.10, 0.20, 0.11), (0.10, 0.20, 0.11), 0.055)
    o.beam("HandleMountLeft", (-0.10, 0.14, 0.07), (-0.10, 0.26, 0.11), 0.055)
    o.beam("HandleMountRight", (0.10, 0.14, 0.07), (0.10, 0.26, 0.11), 0.055)
    return o.write()


def epilogue_environment() -> Path:
    o = mesh("ENV_EPILOGUE_001", C1, C1_MTL)
    o.material("MAT_SAND_WET")
    o.box("ExistingCampFootprint", (0, 0.015, 0), (7.0, 0.03, 6.0))
    o.material("MAT_SAND_DRY")
    for index, (x, z, sx, sz) in enumerate(((-2.1, -1.6, 1.5, 1.0), (0, -1.8, 1.8, 1.2), (2.1, -1.4, 1.4, 1.1), (-1.8, 0.4, 1.7, 1.5), (0.2, 0.5, 2.0, 1.7), (2.2, 0.7, 1.3, 1.4)), 1):
        o.box(f"RecedingWetnessPatch_{index}", (x, 0.035, z), (sx, 0.025, sz))
    o.box("StormReleasePath", (0, 0.055, 1.95), (1.4, 0.035, 2.0))
    o.material("MAT_STONE")
    for index in range(10):
        angle = 2 * math.pi * index / 10
        o.cylinder(f"EpilogueFireRing_{index + 1}", (0.30 * math.cos(angle), 0.10, 0.30 * math.sin(angle)), 0.085, 0.16, 8)
    o.material("MAT_WOOD")
    o.beam("EpilogueFocus", (-0.85, 0.22, -0.75), (0.85, 0.22, -0.75), 0.18)
    o.beam("CampHistoryBench", (-1.2, 0.20, 0.85), (0.1, 0.20, 1.15), 0.16)
    o.material("MAT_CANVAS")
    o.box("EndingCrateSocket", (1.55, 0.055, 0.95), (0.95, 0.04, 0.72))
    o.box("DawnDirectionMarker", (0, 0.07, 2.75), (1.8, 0.04, 0.22))
    o.material("MAT_METAL")
    o.beam("SignalCausalityAnchor", (2.25, 0.05, -1.45), (2.25, 1.55, -1.45), 0.09)
    o.beam("SignalCausalityCrossbar", (1.95, 1.25, -1.45), (2.55, 1.25, -1.45), 0.08)
    o.beam("DawnSightline", (0, 0.09, 1.75), (0, 0.09, 2.9), 0.07)
    return o.write()


def main() -> None:
    files = [
        firesteel(), tinder(), rope_coil(), cloth_item(), map_fragment(), radio_battery(),
        repair_mallet(), ember_carrier(), utility_knife(), dry_fuel_cache(), a5_firepit(),
        signal_fuel(), waterproof_ending_crate(), a5_wind_shield(), epilogue_environment(),
    ]
    print("\n".join(str(path.relative_to(ROOT)) for path in files))


if __name__ == "__main__":
    main()
