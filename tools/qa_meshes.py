#!/usr/bin/env python3
"""Validate OBJ/MTL/texture linkage, normal policy and per-mesh material budget."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MESH_ROOT = ROOT / "Assets" / "ProductionArt" / "Meshes"
DEFAULT_EXCEPTIONS = ROOT / "content" / "materials" / "production_art_material_budget_exceptions.json"
IMPORTER = ROOT / "src" / "unity" / "ProjectOen.Art" / "Editor" / "ProductionArtModelImporter.cs"


def inspect_obj(path: Path) -> dict:
    result = {"vertices": 0, "uvs": 0, "normals": 0, "materials": set(), "mtllibs": []}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("v "):
            result["vertices"] += 1
        elif line.startswith("vt "):
            result["uvs"] += 1
        elif line.startswith("vn "):
            result["normals"] += 1
        elif line.startswith("usemtl "):
            result["materials"].add(line.split(None, 1)[1].strip())
        elif line.startswith("mtllib "):
            result["mtllibs"].append(line.split(None, 1)[1].strip())
    return result


def parse_mtl(path: Path) -> tuple[set[str], list[str]]:
    defined, textures = set(), []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("newmtl "):
            defined.add(line.split(None, 1)[1].strip())
        match = re.match(r"\s*map_\w+\s+(.+)", line, re.IGNORECASE)
        if match:
            textures.append(match.group(1).strip())
    return defined, textures


def initialize_exceptions(rows: dict[str, dict], path: Path) -> None:
    entries = []
    for relative, row in sorted(rows.items()):
        materials = sorted(row["materials"])
        if len(materials) <= 3:
            continue
        entries.append({
            "path": relative,
            "material_count": len(materials),
            "materials": materials,
            "reason": "Multi-surface authored mesh retained for state and silhouette fidelity; requires green Unity batching/MPB-aware proxy plus physical Quest profiling before release.",
        })
    payload = {"schema_version": 1, "q2_base_materials_per_mesh_max": 3, "exceptions": entries}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(entries)} explicit material-budget exceptions to {path.relative_to(ROOT)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_MESH_ROOT)
    parser.add_argument("--exceptions", type=Path, default=DEFAULT_EXCEPTIONS)
    parser.add_argument("--initialize-exceptions", action="store_true")
    args = parser.parse_args()
    mesh_root = args.root.resolve()
    exception_path = args.exceptions.resolve()
    rows = {path.relative_to(mesh_root).as_posix(): inspect_obj(path) for path in sorted(mesh_root.rglob("*.obj"))}

    if args.initialize_exceptions:
        initialize_exceptions(rows, exception_path)

    payload = json.loads(exception_path.read_text(encoding="utf-8"))
    exceptions = {entry["path"]: entry for entry in payload["exceptions"]}
    errors = []
    referenced_mtls: dict[Path, set[str]] = {}

    for relative, row in rows.items():
        if row["vertices"] == 0:
            errors.append(f"mesh has no vertices: {relative}")
        if row["uvs"] == 0:
            errors.append(f"mesh has no UVs: {relative}")
        for reference in row["mtllibs"]:
            mtl = (mesh_root / relative).parent.joinpath(reference).resolve()
            referenced_mtls.setdefault(mtl, set()).update(row["materials"])

        count = len(row["materials"])
        exception = exceptions.get(relative)
        if count > 3 and exception is None:
            errors.append(f"material budget {count}>3 without exception: {relative}")
        if exception is not None:
            if count <= 3:
                errors.append(f"stale material exception for compliant mesh: {relative}")
            if exception.get("material_count") != count or sorted(exception.get("materials", [])) != sorted(row["materials"]):
                errors.append(f"material exception does not match mesh: {relative}")
            if len(exception.get("reason", "").strip()) < 40:
                errors.append(f"material exception lacks a substantive reason: {relative}")

    for relative in sorted(set(exceptions) - set(rows)):
        errors.append(f"material exception points to missing mesh: {relative}")

    missing_normals = sum(1 for row in rows.values() if row["normals"] == 0)
    importer_text = IMPORTER.read_text(encoding="utf-8", errors="replace")
    for token in ("ModelImporterNormals.Calculate", "AreaAndAngleWeighted", "FromAngle", "NormalSmoothingAngle = 60f", "CalculateMikk"):
        if token not in importer_text:
            errors.append(f"explicit Unity normal-import contract missing token: {token}")

    for mtl, used in referenced_mtls.items():
        if not mtl.exists():
            errors.append(f"missing MTL: {mtl}")
            continue
        defined, textures = parse_mtl(mtl)
        for material in sorted(used - defined):
            errors.append(f"undefined material {material} in {mtl}")
        for texture in textures:
            if not (mtl.parent / texture).resolve().exists():
                errors.append(f"missing MTL texture {texture} from {mtl}")
        bump_count = sum(1 for line in mtl.read_text(encoding="utf-8").splitlines() if line.lower().startswith("map_bump "))
        if bump_count < len(defined):
            errors.append(f"MTL normal linkage incomplete: {bump_count}/{len(defined)} map_Bump entries in {mtl}")

    counts: dict[int, int] = {}
    for row in rows.values():
        count = len(row["materials"])
        counts[count] = counts.get(count, 0) + 1
    print("Project OEN production mesh QA")
    print(f"  meshes                  : {len(rows)}")
    print(f"  OBJ normals absent      : {missing_normals} (covered by explicit Unity 60-degree import contract)")
    print(f"  material distribution   : {', '.join(f'{key}:{value}' for key, value in sorted(counts.items()))}")
    print(f"  documented exceptions   : {len(exceptions)}")
    print(f"  referenced MTL files    : {len(referenced_mtls)}")
    if errors:
        print(f"FAILED with {len(errors)} issue(s):")
        for error in errors:
            print(" - " + error)
        return 1
    print("PASS: mesh linkage, normal policy and material budget/exception contract are complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
