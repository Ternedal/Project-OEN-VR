#!/usr/bin/env python3
"""Validate source inventory paths and claimed source coverage."""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "content" / "source_inventory.source.json"
ERRORS: list[str] = []
SUFFIXES = {".svg", ".obj", ".fbx", ".gltf", ".glb", ".png", ".tif", ".tiff", ".wav", ".json"}

def fail(msg: str) -> None: ERRORS.append(msg)

def resolve(value, owner):
    if not isinstance(value, str) or not value:
        fail(f"{owner}: missing path"); return None
    path = ROOT / value
    if not path.exists(): fail(f"{owner}: missing {value}"); return None
    return path

def files(path: Path):
    if path.is_file(): return [path]
    return [p for p in path.rglob("*") if p.is_file() and p.suffix.lower() in SUFFIXES]

def main() -> int:
    try: data = json.loads(DATA.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ERROR: cannot parse inventory: {exc}"); return 1

    seen = set()
    for package in data.get("packages", []):
        pid = package.get("id")
        if not isinstance(pid, str) or not pid: fail("package without id"); continue
        if pid in seen: fail(f"duplicate package id: {pid}")
        seen.add(pid)
        path = resolve(package.get("path"), pid)
        if path is None: continue
        src = files(path)
        produced = package.get("producedIds")
        if produced is not None and (not isinstance(produced, list) or not produced): fail(f"{pid}: invalid producedIds")
        elif isinstance(produced, list) and len(src) < len(produced): fail(f"{pid}: {len(produced)} producedIds but {len(src)} source files")
        individual = package.get("individualMasterIds")
        if isinstance(individual, list):
            stems = {p.stem for p in src}
            for asset_id in individual:
                if asset_id not in stems: fail(f"{pid}: missing individual master {asset_id}")

    contracts = set()
    for contract in data.get("contentContracts", []):
        cid = contract.get("id")
        if not isinstance(cid, str) or not cid: fail("content contract without id"); continue
        if cid in contracts: fail(f"duplicate content contract id: {cid}")
        contracts.add(cid); resolve(contract.get("path"), cid)

    if ERRORS:
        for err in ERRORS: print(f"ERROR: {err}")
        return 1
    print(f"Source inventory OK: {len(seen)} packages, {len(contracts)} contracts.")
    return 0

if __name__ == "__main__": sys.exit(main())
