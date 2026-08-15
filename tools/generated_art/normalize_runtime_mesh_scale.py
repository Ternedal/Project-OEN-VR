#!/usr/bin/env python3
"""Normalize every ProductionArt OBJ to its checked-in physical-size contract."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MESH_ROOT = ROOT / "Assets" / "ProductionArt" / "Meshes"
SPEC_PATH = ROOT / "content" / "items" / "runtime_mesh_scale_specs.json"

# Uniform group factors preserve the relative dimensions of visual state variants.
# Targets were selected from ordinary real-world sizes with a modest VR readability
# allowance; they replace the previous 2-4x presentation scale.
PORTABLE_FACTORS = {
    "atlas_expansion/radio__communication/ax-com-001_handheld_radio__": (0.3633, "two_hand_portable"),
    "atlas_expansion/tools__crafting/ax-tool-001_survival_axe__": (0.7310, "two_hand_tool"),
    "atlas_expansion/tools__crafting/ax-tool-002_machete__": (0.6035, "one_hand_tool"),
    "atlas_expansion/tools__crafting/ax-tool-003_hand_saw__": (0.5965, "one_hand_tool"),
    "atlas_expansion/tools__crafting/ax-tool-004_shovel__": (0.7975, "two_hand_tool"),
    "atlas_expansion/tools__crafting/ax-tool-005_binoculars__": (0.4835, "two_hand_portable"),
    "atlas_expansion/tools__crafting/ax-tool-006_compass__": (0.3125, "one_hand_precision"),
    "props_tools/pr-005_portable_radio__": (0.3226, "two_hand_portable"),
    "props_tools/pr-007_metal_canteen__": (0.3647, "one_hand_portable"),
    "props_tools/pr-008_oil_lantern__": (0.4492, "one_hand_portable"),
    "props_tools/pr-009_torch__": (0.5909, "one_hand_tool"),
    "props_tools/pr-013_cloth_bundle__": (0.6870, "one_hand_portable"),
    "props_tools/pr-017_tool_hammer_mallet__": (0.5056, "one_hand_tool"),
    "props_tools/pr-018_knife_cutting_tool__": (0.4789, "one_hand_precision"),
}


def vertices(path: Path) -> list[tuple[float, float, float]]:
    result = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("v "):
            fields = line.split()
            result.append((float(fields[1]), float(fields[2]), float(fields[3])))
    return result


def longest_dimension(path: Path) -> float:
    points = vertices(path)
    if not points:
        raise ValueError(f"OBJ has no vertices: {path.relative_to(ROOT)}")
    axes = list(zip(*points))
    return max(max(axis) - min(axis) for axis in axes)


def portable_policy(relative: str) -> tuple[float, str] | None:
    normalized = relative.replace("\\", "/")
    for prefix, policy in PORTABLE_FACTORS.items():
        if normalized.startswith(prefix):
            return policy
    return None


def initialize_spec() -> None:
    entries = []
    for path in sorted(MESH_ROOT.rglob("*.obj")):
        relative = path.relative_to(MESH_ROOT).as_posix()
        actual = longest_dimension(path)
        policy = portable_policy(relative)
        factor, scale_class = policy if policy else (1.0, "authored_world_scale")
        target = actual * factor
        entries.append({
            "path": relative,
            "scale_class": scale_class,
            "target_longest_m": round(target, 6),
            "tolerance_m": round(max(0.002, target * 0.01), 6),
        })

    payload = {
        "schema_version": 1,
        "unit": "meter",
        "portable_scale_convention": {
            "summary": "Physical real-world scale with only a modest readability allowance; never presentation-scale enlargement.",
            "maximum_readability_oversize_ratio": 1.35,
            "unity_transform_scale": 1.0,
        },
        "entries": entries,
    }
    SPEC_PATH.parent.mkdir(parents=True, exist_ok=True)
    SPEC_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(entries)} runtime mesh scale specs to {SPEC_PATH.relative_to(ROOT)}")


def normalize() -> None:
    payload = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    changed = 0
    for entry in payload["entries"]:
        path = MESH_ROOT / entry["path"]
        actual = longest_dimension(path)
        target = float(entry["target_longest_m"])
        factor = target / actual
        if abs(factor - 1.0) <= 1e-7:
            continue

        output = []
        for line in path.read_text(encoding="utf-8", errors="strict").splitlines():
            if line.startswith("v "):
                fields = line.split()
                x, y, z = (float(fields[i]) * factor for i in range(1, 4))
                output.append(f"v {x:.6f} {y:.6f} {z:.6f}")
            else:
                output.append(line)
        path.write_text("\n".join(output) + "\n", encoding="utf-8")
        changed += 1
    print(f"Normalized {changed} of {len(payload['entries'])} production meshes to their physical-size specs")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--initialize-spec", action="store_true")
    args = parser.parse_args()
    if args.initialize_spec:
        initialize_spec()
    normalize()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
