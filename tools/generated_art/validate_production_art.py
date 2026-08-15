#!/usr/bin/env python3
"""Strict QA gate for Project ØEN generated production art.

This validator exists to prevent the repository from claiming a complete art pass when
files are missing, blank, structurally invalid, or no longer cover the canonical asset
master. It intentionally validates the generated deliverables rather than trusting
summary counts written by the generator.
"""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MASTER = HERE / "asset_master.csv"
PROD = ROOT / "Assets" / "ProductionArt"
MANIFEST = PROD / "Docs" / "production_art_manifest.json"

MUST_HAVE_IDS = {
    "UI-002", "UI-003", "UI-004", "UI-005",
    "PR-001", "PR-002", "PR-003", "PR-004", "PR-005",
    "CS-001", "CS-002", "CS-003", "CS-004", "CS-005",
    "CS-006", "CS-007", "CS-008", "CS-009", "CS-010",
    "CS-011", "CS-012", "CS-013", "CS-014", "CS-015",
    "EN-001", "EN-007", "EN-009", "EN-012",
}
FORBIDDEN_CANONICAL_TERMS = ("hunger", "thirst")


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def load_master() -> list[dict[str, str]]:
    with MASTER.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def validate_png(path: Path, declared_dimensions, errors: list[str]) -> None:
    try:
        with Image.open(path) as im:
            im.load()
            width, height = im.size
            if im.mode not in ("RGBA", "LA", "P") and "A" not in im.getbands():
                fail(errors, f"Sprite has no alpha-capable mode: {path} ({im.mode})")
            if declared_dimensions and [width, height] != list(declared_dimensions):
                fail(errors, f"Manifest dimensions disagree for {path}: manifest={declared_dimensions}, actual={[width, height]}")
            if min(width, height) < 512:
                fail(errors, f"Production sprite below 512px minimum dimension: {path} ({width}x{height})")

            rgba = im.convert("RGBA")
            alpha = rgba.getchannel("A")
            bbox = alpha.getbbox()
            if bbox is None:
                fail(errors, f"Completely transparent/blank sprite: {path}")
                return

            occupied = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
            total = width * height
            if occupied / total < 0.01:
                fail(errors, f"Sprite content occupies under 1% of canvas: {path}")
    except Exception as exc:
        fail(errors, f"Could not decode PNG {path}: {exc}")


def parse_obj(path: Path, errors: list[str]) -> tuple[int, int]:
    vertices = 0
    faces = 0
    referenced_materials: set[str] = set()
    mtllibs: list[str] = []

    try:
        lines = path.read_text(encoding="utf-8", errors="strict").splitlines()
    except Exception as exc:
        fail(errors, f"Could not read OBJ {path}: {exc}")
        return 0, 0

    for line_no, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("v "):
            vertices += 1
        elif line.startswith("f "):
            faces += 1
            tokens = line.split()[1:]
            if len(tokens) < 3:
                fail(errors, f"OBJ face has <3 vertices: {path}:{line_no}")
                continue
            for token in tokens:
                idx_text = token.split("/", 1)[0]
                try:
                    idx = int(idx_text)
                except ValueError:
                    fail(errors, f"Invalid OBJ face index {token!r}: {path}:{line_no}")
                    continue
                resolved = idx if idx > 0 else vertices + idx + 1
                if resolved < 1 or resolved > vertices:
                    fail(errors, f"OBJ face index out of range ({idx}) at {path}:{line_no}, vertices={vertices}")
        elif line.startswith("usemtl "):
            referenced_materials.add(line.split(None, 1)[1].strip())
        elif line.startswith("mtllib "):
            mtllibs.append(line.split(None, 1)[1].strip())

    if vertices == 0:
        fail(errors, f"OBJ has zero vertices: {path}")
    if faces == 0:
        fail(errors, f"OBJ has zero faces: {path}")

    for rel in mtllibs:
        mtl = (path.parent / rel).resolve()
        if not mtl.exists():
            fail(errors, f"OBJ references missing MTL: {path} -> {rel}")
            continue
        defined = set()
        for raw in mtl.read_text(encoding="utf-8", errors="replace").splitlines():
            if raw.strip().startswith("newmtl "):
                defined.add(raw.strip().split(None, 1)[1])
        missing = sorted(referenced_materials - defined)
        if missing:
            fail(errors, f"OBJ references undefined material(s) in {mtl}: {missing}")

    return vertices, faces


def main() -> int:
    errors: list[str] = []

    if not MASTER.exists():
        print(f"ERROR: canonical master missing: {MASTER}")
        return 1
    if not MANIFEST.exists():
        print(f"ERROR: production manifest missing: {MANIFEST}")
        return 1

    master = load_master()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    master_ids = {row["asset_id"].strip() for row in master}
    if len(master) != 148 or len(master_ids) != 148:
        fail(errors, f"Canonical asset master expected 148 unique rows, got rows={len(master)}, unique_ids={len(master_ids)}")

    produced_by_id: dict[str, list[dict]] = defaultdict(list)
    counts = Counter()
    total_vertices = 0
    total_faces = 0

    for entry in manifest:
        asset_id = str(entry.get("asset_id", "")).strip()
        kind = str(entry.get("kind", "")).strip().lower()
        rel = str(entry.get("path", "")).strip()
        if not asset_id or not kind or not rel:
            fail(errors, f"Malformed manifest entry: {entry}")
            continue

        produced_by_id[asset_id].append(entry)
        counts[kind] += 1
        path = ROOT / rel
        if not path.exists():
            fail(errors, f"Manifest path missing on disk: {rel}")
            continue

        lower_rel = rel.lower()
        if any(term in lower_rel for term in FORBIDDEN_CANONICAL_TERMS):
            fail(errors, f"Forbidden noncanonical Hunger/Thirst asset present: {rel}")

        meta = Path(str(path) + ".meta")
        if not meta.exists():
            fail(errors, f"Unity .meta missing: {meta.relative_to(ROOT)}")

        if kind == "sprite":
            if path.suffix.lower() != ".png":
                fail(errors, f"Sprite manifest entry is not PNG: {rel}")
            else:
                validate_png(path, entry.get("dimensions"), errors)
        elif kind == "mesh":
            if path.suffix.lower() != ".obj":
                fail(errors, f"Mesh manifest entry is not OBJ: {rel}")
            else:
                v, f = parse_obj(path, errors)
                total_vertices += v
                total_faces += f

    missing_ids = sorted(master_ids - set(produced_by_id))
    if missing_ids:
        fail(errors, f"Master asset IDs with no production output: {missing_ids}")

    unexpected_ids = sorted(set(produced_by_id) - master_ids)
    if unexpected_ids:
        fail(errors, f"Manifest contains IDs not in canonical master: {unexpected_ids}")

    missing_required = sorted(MUST_HAVE_IDS - set(produced_by_id))
    if missing_required:
        fail(errors, f"Required core gameplay asset IDs missing: {missing_required}")

    if counts["sprite"] < 180:
        fail(errors, f"Too few production sprites: {counts['sprite']} (expected >=180)")
    if counts["mesh"] < 120:
        fail(errors, f"Too few production meshes: {counts['mesh']} (expected >=120)")
    if total_vertices < 10_000 or total_faces < 5_000:
        fail(errors, f"World mesh geometry suspiciously small: vertices={total_vertices}, faces={total_faces}")

    # Material maps live in Materials/Textures; recurse deliberately so layout changes do not fake a zero count.
    material_pngs = sorted((PROD / "Materials").rglob("*.png"))
    if len(material_pngs) < 10:
        fail(errors, f"Too few shared material textures: {len(material_pngs)} (expected >=10)")
    for tex in material_pngs:
        if not Path(str(tex) + ".meta").exists():
            fail(errors, f"Unity .meta missing for material texture: {tex.relative_to(ROOT)}")

    required_globs = {
        "tarp/presenning": "Meshes/props_tools/pr-001_tarp_presenning*.obj",
        "rope": "Meshes/props_tools/pr-002_rope_coil*.obj",
        "supply crate": "Meshes/props_tools/pr-004_supply_crate*.obj",
        "portable radio": "Meshes/props_tools/pr-005_portable_radio*.obj",
        "shelter": "Meshes/construction_states/cs-00[1-5]_shelter*.obj",
        "campfire": "Meshes/construction_states/cs-00[6-9]_campfire*.obj",
        "signal beacon": "Meshes/construction_states/cs-01[1-5]_signal_beacon*.obj",
        "shipwreck": "Meshes/environment_set_dressing/en-001_shipwreck_hull_chunk*.obj",
    }
    for label, pattern in required_globs.items():
        if not list(PROD.glob(pattern)):
            fail(errors, f"Required mockup/world asset family missing: {label} ({pattern})")

    print("Project ØEN production-art QA")
    print(f"  canonical master rows : {len(master)}")
    print(f"  manifest entries      : {len(manifest)}")
    print(f"  sprites               : {counts['sprite']}")
    print(f"  meshes                : {counts['mesh']}")
    print(f"  mesh vertices         : {total_vertices}")
    print(f"  mesh faces            : {total_faces}")
    print(f"  material textures     : {len(material_pngs)}")

    if errors:
        print(f"\nFAILED with {len(errors)} issue(s):")
        for message in errors:
            print(" - " + message)
        return 1

    print("\nPASS: production art covers the canonical master and passed structural QA.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
