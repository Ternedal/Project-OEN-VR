#!/usr/bin/env python3
"""Validate source inventory and cross-file non-Unity source links."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "content" / "source_inventory.source.json"
LOCALIZATION = ROOT / "content" / "localization" / "da.source.json"
UI_SURFACES = ROOT / "content" / "ui" / "release_ui_surfaces.source.json"
MATERIALS = ROOT / "content" / "materials" / "material_families.source.json"
ERRORS: list[str] = []
SUFFIXES = {".svg", ".obj", ".fbx", ".gltf", ".glb", ".png", ".tif", ".tiff", ".wav", ".json"}


def fail(msg: str) -> None:
    ERRORS.append(msg)


def load_json(path: Path, owner: str):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        fail(f"{owner}: cannot parse {path.relative_to(ROOT)}: {exc}")
        return None


def resolve(value, owner):
    if not isinstance(value, str) or not value:
        fail(f"{owner}: missing path")
        return None
    path = ROOT / value
    if not path.exists():
        fail(f"{owner}: missing {value}")
        return None
    return path


def files(path: Path):
    if path.is_file():
        return [path]
    return [p for p in path.rglob("*") if p.is_file() and p.suffix.lower() in SUFFIXES]


def validate_inventory(data) -> tuple[set[str], set[str]]:
    packages: set[str] = set()
    for package in data.get("packages", []):
        pid = package.get("id")
        if not isinstance(pid, str) or not pid:
            fail("package without id")
            continue
        if pid in packages:
            fail(f"duplicate package id: {pid}")
        packages.add(pid)
        path = resolve(package.get("path"), pid)
        if path is None:
            continue
        src = files(path)
        produced = package.get("producedIds")
        if produced is not None and (not isinstance(produced, list) or not produced):
            fail(f"{pid}: invalid producedIds")
        elif isinstance(produced, list) and len(src) < len(produced):
            fail(f"{pid}: {len(produced)} producedIds but {len(src)} source files")
        individual = package.get("individualMasterIds")
        if isinstance(individual, list):
            stems = {p.stem for p in src}
            for asset_id in individual:
                if asset_id not in stems:
                    fail(f"{pid}: missing individual master {asset_id}")

    contracts: set[str] = set()
    for contract in data.get("contentContracts", []):
        cid = contract.get("id")
        if not isinstance(cid, str) or not cid:
            fail("content contract without id")
            continue
        if cid in contracts:
            fail(f"duplicate content contract id: {cid}")
        contracts.add(cid)
        resolve(contract.get("path"), cid)
    return packages, contracts


def validate_release_ui() -> None:
    if not UI_SURFACES.exists():
        return
    data = load_json(UI_SURFACES, "RELEASE_UI_SURFACES")
    loc = load_json(LOCALIZATION, "LOCALIZATION_DA")
    if not isinstance(data, dict) or not isinstance(loc, dict):
        return
    strings = loc.get("strings")
    if not isinstance(strings, dict):
        fail("LOCALIZATION_DA: strings must be an object")
        return

    surface_ids: set[str] = set()
    for surface in data.get("surfaces", []):
        sid = surface.get("id")
        if not isinstance(sid, str) or not sid:
            fail("RELEASE_UI_SURFACES: surface without id")
            continue
        if sid in surface_ids:
            fail(f"RELEASE_UI_SURFACES: duplicate surface id {sid}")
        surface_ids.add(sid)
        source = resolve(surface.get("source"), sid)
        if source is not None and source.stem != sid:
            fail(f"{sid}: source stem does not match surface id ({source.stem})")
        keys = surface.get("copyKeys")
        if not isinstance(keys, list):
            fail(f"{sid}: copyKeys must be a list")
            continue
        for key in keys:
            if key not in strings:
                fail(f"{sid}: missing localization key {key}")


def validate_materials() -> None:
    if not MATERIALS.exists():
        return
    data = load_json(MATERIALS, "MATERIAL_FAMILIES")
    if not isinstance(data, dict):
        return
    family_ids: set[str] = set()
    for family in data.get("families", []):
        fid = family.get("id")
        if not isinstance(fid, str) or not fid:
            fail("MATERIAL_FAMILIES: family without id")
            continue
        if fid in family_ids:
            fail(f"MATERIAL_FAMILIES: duplicate family id {fid}")
        family_ids.add(fid)
        resolve(family.get("sourceReference"), fid)


def main() -> int:
    data = load_json(DATA, "SOURCE_INVENTORY")
    if not isinstance(data, dict):
        for err in ERRORS:
            print(f"ERROR: {err}")
        return 1

    packages, contracts = validate_inventory(data)
    validate_release_ui()
    validate_materials()

    if ERRORS:
        for err in ERRORS:
            print(f"ERROR: {err}")
        print(f"Source inventory validation FAILED: {len(ERRORS)} error(s).")
        return 1

    print(f"Source inventory OK: {len(packages)} packages, {len(contracts)} contracts; UI/material links valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
