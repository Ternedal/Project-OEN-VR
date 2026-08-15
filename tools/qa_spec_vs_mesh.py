#!/usr/bin/env python3
"""CI gate: compare all runtime ProductionArt meshes with explicit meter specs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def longest_dimension(path: Path) -> float:
    axes = ([], [], [])
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("v "):
            fields = line.split()
            for index in range(3):
                axes[index].append(float(fields[index + 1]))
    if not axes[0]:
        raise ValueError(f"OBJ has no vertices: {path}")
    return max(max(axis) - min(axis) for axis in axes)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mesh-root", type=Path, default=ROOT / "Assets" / "ProductionArt" / "Meshes")
    parser.add_argument("--spec", type=Path, default=ROOT / "content" / "items" / "runtime_mesh_scale_specs.json")
    args = parser.parse_args()

    mesh_root = args.mesh_root.resolve()
    payload = json.loads(args.spec.resolve().read_text(encoding="utf-8"))
    entries = {entry["path"]: entry for entry in payload["entries"]}
    actual_paths = {path.relative_to(mesh_root).as_posix(): path for path in mesh_root.rglob("*.obj")}
    errors = []

    for relative in sorted(set(entries) - set(actual_paths)):
        errors.append(f"spec points to missing mesh: {relative}")
    for relative in sorted(set(actual_paths) - set(entries)):
        errors.append(f"mesh has no scale spec: {relative}")

    portable = 0
    for relative in sorted(set(entries) & set(actual_paths)):
        entry = entries[relative]
        actual = longest_dimension(actual_paths[relative])
        target = float(entry["target_longest_m"])
        tolerance = float(entry["tolerance_m"])
        if entry["scale_class"] != "authored_world_scale":
            portable += 1
        if abs(actual - target) > tolerance:
            errors.append(f"{relative}: {actual:.4f} m outside {target:.4f} +/- {tolerance:.4f} m")

    convention = payload.get("portable_scale_convention", {})
    if convention.get("maximum_readability_oversize_ratio") != 1.35:
        errors.append("portable scale convention must retain the approved 1.35x readability ceiling")
    if convention.get("unity_transform_scale") != 1.0:
        errors.append("runtime mesh specs must import at Unity transform scale 1.0")

    print("Project OEN runtime mesh scale QA")
    print(f"  specs     : {len(entries)}")
    print(f"  meshes    : {len(actual_paths)}")
    print(f"  portable  : {portable}")
    if errors:
        print(f"FAILED with {len(errors)} issue(s):")
        for error in errors:
            print(" - " + error)
        return 1
    print("PASS: every runtime mesh matches its explicit meter-scale contract.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
