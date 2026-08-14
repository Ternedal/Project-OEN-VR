#!/usr/bin/env python3
"""Validate the extended item, prop and epilogue production mesh batch."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED = {
    "source_art/props/a2/ITM_FIRESTEEL_001.obj": (80, (0.349, 0.142, 0.127), {"ReadableFerroRod", "BroadStrikeZone", "OversizePrimaryGrip", "TetherRing"}),
    "source_art/props/a2/ITM_TINDER_001.obj": (300, (0.270, 0.142, 0.254), {"BroadDryFiber_1", "NestSilhouette", "EmberInsertionTarget"}),
    "source_art/props/a2/ITM_ROPE_COIL_001.obj": (500, (0.622, 0.158, 0.408), {"ChunkyCarryCoil", "ReadableLooseEnd", "OversizeEndLoop", "CarryBand"}),
    "source_art/items/a5/ITM_CLOTH_001.obj": (40, (0.320, 0.251, 0.136), {"FoldedClothBase", "ReadableFoldLayerA", "PrimaryGripEdge"}),
    "source_art/items/a5/ITM_MAP_FRAGMENT_001.obj": (40, (0.365, 0.250, 0.042), {"FictionalMapSurface", "ReadableRouteLine", "PrimaryGripMargin"}),
    "source_art/items/a5/ITM_RADIO_BATTERY_001.obj": (50, (0.170, 0.105, 0.274), {"BatteryBody", "KeyedSocketRailLeft", "TerminalPositive", "PrimaryGripBand"}),
    "source_art/items/a5/ITM_HAMMER_001.obj": (40, (0.174, 0.090, 0.339), {"grip_swell", "contact_face_left", "contact_face_right"}),
    "source_art/items/a5/ITM_EMBER_CARRIER_001.obj": (70, (0.340, 0.330, 0.158), {"carrier_body", "heat_guard", "grip_bar", "ember_bed"}),
    "source_art/items/b1/ITM_KNIFE_001.obj": (36, (0.310, 0.066, 0.050), {"grip_core", "cutting_edge", "finger_guard", "blunt_nose"}),
    "source_art/props/a5/PRP_DRY_FUEL_CACHE_001.obj": (50, (0.720, 0.557, 0.562), {"ProtectedCacheBody", "WeatherCover", "DryStatePanel", "LargePullHandle"}),
    "source_art/props/a5/PRP_FIREPIT_001.obj": (250, (0.920, 0.220, 0.902), {"RingStone_1", "ColdLogA", "ColdLogB", "EmberStateSocket"}),
    "source_art/props/a5/PRP_SIGNAL_FUEL_001.obj": (40, (0.827, 0.275, 0.480), {"SignalFuelLog_1", "HighVisibilityCarryWrap", "SignalFrameAttachmentLoop"}),
    "source_art/props/a5/PRP_WATERPROOF_ENDING_CRATE_001.obj": (70, (0.920, 0.627, 0.665), {"WaterproofCrateBody", "BroadGasket", "NeutralMementoSlot", "PrivatePayloadSlotCover", "DeliberateRevealLatch"}),
    "source_art/props/a5/PRP_WIND_SHIELD_001.obj": (65, (0.533, 0.429, 0.207), {"CurvedShieldSlat_1", "TopOrientationRail", "LargeHandle"}),
    "source_art/environment/c1/ENV_EPILOGUE_001.obj": (260, (7.000, 1.550, 6.000), {"ExistingCampFootprint", "StormReleasePath", "EpilogueFocus", "EndingCrateSocket", "DawnDirectionMarker", "SignalCausalityAnchor"}),
}


def validate_obj(relative: str, contract: tuple[int, tuple[float, float, float], set[str]]) -> list[str]:
    errors: list[str] = []
    minimum_vertices, expected_bounds, required_parts = contract
    path = ROOT / relative
    mtl_path = path.with_suffix(".mtl")
    if not path.is_file():
        return [f"{relative}: missing OBJ"]
    if not mtl_path.is_file():
        return [f"{relative}: missing MTL"]

    vertices: list[tuple[float, float, float]] = []
    uv_count = 0
    face_count = 0
    parts: set[str] = set()
    materials: set[str] = set()
    text = path.read_text(encoding="utf-8")
    if f"mtllib {mtl_path.name}" not in text:
        errors.append(f"{relative}: incorrect or missing mtllib")
    for line in text.splitlines():
        if line.startswith("v "):
            vertices.append(tuple(map(float, line.split()[1:4])))
        elif line.startswith("vt "):
            uv_count += 1
        elif line.startswith(("o ", "g ")):
            parts.add(line[2:].strip())
        elif line.startswith("usemtl "):
            materials.add(line[7:].strip())
        elif line.startswith("f "):
            face_count += 1
            for token in line.split()[1:]:
                match = re.fullmatch(r"(\d+)/(\d+)", token)
                if not match:
                    errors.append(f"{relative}: face lacks explicit UV index: {token}")
                    continue
                vertex_index, uv_index = map(int, match.groups())
                if not 1 <= vertex_index <= len(vertices) or not 1 <= uv_index <= uv_count:
                    errors.append(f"{relative}: out-of-range face index: {token}")
    if len(vertices) < minimum_vertices:
        errors.append(f"{relative}: {len(vertices)} vertices, expected at least {minimum_vertices}")
    if not uv_count or not face_count or not materials:
        errors.append(f"{relative}: missing UV, face or material assignments")
    missing_parts = required_parts - parts
    if missing_parts:
        errors.append(f"{relative}: missing semantic parts {sorted(missing_parts)}")
    if vertices:
        bounds = tuple(
            max(vertex[axis] for vertex in vertices) - min(vertex[axis] for vertex in vertices)
            for axis in range(3)
        )
        for axis, (actual, expected) in enumerate(zip(bounds, expected_bounds)):
            if abs(actual - expected) > 0.002:
                errors.append(f"{relative}: axis {axis} bound {actual:.3f}, expected {expected:.3f}")

    mtl_text = mtl_path.read_text(encoding="utf-8")
    defined_materials = set(re.findall(r"^newmtl\s+(.+)$", mtl_text, re.MULTILINE))
    if materials - defined_materials:
        errors.append(f"{relative}: undefined materials {sorted(materials - defined_materials)}")
    for texture_reference in re.findall(r"^map_Kd\s+(.+)$", mtl_text, re.MULTILINE):
        texture = (mtl_path.parent / texture_reference.strip()).resolve()
        if not texture.is_file() or texture.suffix.lower() != ".png":
            errors.append(f"{relative}: missing PNG texture {texture_reference}")
    return errors


def validate_inventory() -> list[str]:
    errors: list[str] = []
    data = json.loads((ROOT / "content/source_inventory.source.json").read_text(encoding="utf-8"))
    packages = {package["id"]: package for package in data["packages"]}
    required = {
        "A2_CORE_PROPS": {"ITM_FIRESTEEL_001", "ITM_TINDER_001", "ITM_ROPE_COIL_001"},
        "B1_WORLD_ITEMS": {"ITM_KNIFE_001"},
        "A5_ITEMS": {"ITM_CLOTH_001", "ITM_MAP_FRAGMENT_001", "ITM_RADIO_BATTERY_001", "ITM_EMBER_CARRIER_001", "ITM_HAMMER_001"},
        "A5_PROP_MESHES": {"PRP_WIND_SHIELD_001", "PRP_DRY_FUEL_CACHE_001", "PRP_SIGNAL_FUEL_001", "PRP_FIREPIT_001", "PRP_WATERPROOF_ENDING_CRATE_001"},
        "C1_EPILOGUE": {"ENV_EPILOGUE_001"},
    }
    for package_id, expected_ids in required.items():
        package = packages.get(package_id, {})
        actual = set(package.get("productionMeshIds", []))
        if not expected_ids <= actual:
            errors.append(f"inventory {package_id}: missing productionMeshIds {sorted(expected_ids - actual)}")
    contracts = {entry["id"]: entry for entry in data["contentContracts"]}
    for contract_id in ("EMBER_CARRIER", "REPAIR_MALLET", "UTILITY_KNIFE", "EPILOGUE_ENVIRONMENT_REFERENCE"):
        if contracts.get(contract_id, {}).get("status") != "production-source-ready-unity-pending":
            errors.append(f"inventory {contract_id}: status is not production-source-ready-unity-pending")
    return errors


def main() -> int:
    errors: list[str] = []
    for relative, contract in EXPECTED.items():
        errors.extend(validate_obj(relative, contract))
    errors.extend(validate_inventory())
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"Extended source mesh validation FAILED: {len(errors)} error(s).")
        return 1
    print(
        "Extended production sources OK: 15 OBJ/MTL assets have metre-scale bounds, "
        "UVs, semantic parts, resolved PNG materials and current inventory status."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
