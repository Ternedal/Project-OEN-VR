#!/usr/bin/env python3
"""Require each declared produced source ID to have a direct or mapped backing file."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "content" / "source_inventory.source.json"
REFERENCE_MAP = ROOT / "content" / "source_inventory.reference_map.source.json"
SUFFIXES = {".svg", ".obj", ".fbx", ".gltf", ".glb", ".png", ".tif", ".tiff", ".wav", ".json"}


def main() -> int:
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    reference_data = json.loads(REFERENCE_MAP.read_text(encoding="utf-8"))
    mappings = reference_data.get("mappings", {})
    errors: list[str] = []
    package_ids: set[str] = set()

    for package in inventory.get("packages", []):
        if not isinstance(package, dict):
            errors.append("package entry is not an object")
            continue
        pid = package.get("id")
        path_value = package.get("path")
        if not isinstance(pid, str) or not pid:
            errors.append("package without id")
            continue
        if pid in package_ids:
            errors.append(f"duplicate package id: {pid}")
        package_ids.add(pid)
        if not isinstance(path_value, str) or not path_value:
            errors.append(f"{pid}: missing path")
            continue
        package_path = ROOT / path_value
        if not package_path.exists():
            errors.append(f"{pid}: missing package path {path_value}")
            continue

        source_paths = [p for p in package_path.rglob("*") if p.is_file() and p.suffix.lower() in SUFFIXES]
        stems = {p.stem for p in source_paths}

        for field in ("producedIds", "individualMasterIds"):
            values = package.get(field)
            if values is None:
                continue
            if not isinstance(values, list) or not values:
                errors.append(f"{pid}: invalid {field}")
                continue
            if len(values) != len(set(values)):
                errors.append(f"{pid}: duplicate values in {field}")

        for asset_id in package.get("individualMasterIds") or []:
            if not isinstance(asset_id, str) or asset_id not in stems:
                errors.append(f"{pid}: individual master has no exact backing file: {asset_id}")

        produced = package.get("producedIds") or []
        package_map = mappings.get(pid, {})
        if not isinstance(package_map, dict):
            errors.append(f"{pid}: reference map must be an object")
            package_map = {}

        for mapped_id in package_map:
            if mapped_id not in produced:
                errors.append(f"{pid}: orphan mapped id {mapped_id}")

        for asset_id in produced:
            if not isinstance(asset_id, str) or not asset_id:
                errors.append(f"{pid}: invalid producedId {asset_id!r}")
                continue
            if asset_id in stems:
                continue
            rel = package_map.get(asset_id)
            if not isinstance(rel, str) or not rel:
                errors.append(f"{pid}: producedId has no direct or mapped backing file: {asset_id}")
                continue
            rel_path = Path(rel)
            if rel_path.is_absolute() or ".." in rel_path.parts:
                errors.append(f"{pid}: unsafe mapped path for {asset_id}: {rel}")
                continue
            mapped = package_path / rel_path
            if not mapped.is_file() or mapped.suffix.lower() not in SUFFIXES:
                errors.append(f"{pid}: mapped backing file missing/unsupported for {asset_id}: {rel}")

    for mapped_package in mappings:
        if mapped_package not in package_ids:
            errors.append(f"orphan mapped package: {mapped_package}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Source inventory backing OK: all declared IDs resolve to direct or mapped source files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
