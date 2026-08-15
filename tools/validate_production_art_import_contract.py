#!/usr/bin/env python3
"""Validate the case-safe ProductionArt root and isolated Unity assemblies."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART_ROOT = ROOT / "Assets" / "ProductionArt"
ART_SOURCE = ROOT / "src" / "unity" / "ProjectOen.Art"
RUNTIME_ASMDEF = ART_SOURCE / "ProjectOen.Art.asmdef"
EDITOR_ASMDEF = ART_SOURCE / "Editor" / "ProjectOen.Art.Editor.asmdef"
CONTRACT = ROOT / "docs" / "78_PRODUCTION_ART_IMPORT_CONTRACT.md"
GUID_IDENTITY = ROOT / "tools" / "generated_art" / "guid_identity.py"
sys.path.insert(0, str(GUID_IDENTITY.parent))
from guid_identity import stable_production_art_guid_path


def read_meta_guid(asset: Path) -> str:
    text = Path(str(asset) + ".meta").read_text(encoding="utf-8")
    match = re.search(r"^guid: ([0-9a-f]{32})$", text, re.MULTILINE)
    if not match:
        raise ValueError(f"missing Unity GUID in {asset.relative_to(ROOT)}.meta")
    return match.group(1)


def main() -> int:
    errors = []
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode("utf-8").split("\0")
    tracked = [path for path in tracked if path]
    by_casefold: dict[str, list[str]] = {}
    for path in tracked:
        by_casefold.setdefault(path.casefold(), []).append(path)
    for paths in by_casefold.values():
        if len(paths) > 1:
            errors.append("case-only path collision: " + " | ".join(paths))

    if not ART_ROOT.is_dir():
        errors.append("canonical Assets/ProductionArt root is missing")
    legacy = ROOT / "Assets" / "ProjectOEN" / "ProductionArt"
    if legacy.exists():
        errors.append("legacy production-art root still exists")

    scan_roots = [
        ROOT / "src" / "unity" / "ProjectOen.Art",
        ROOT / "tools" / "generated_art",
        ROOT / "prototype" / "m0b-bootstrap",
        ROOT / ".github" / "workflows" / "generate-project-oen-art.yml",
        ROOT / "docs" / "36_GENERATED_ART_PACK.md",
        ROOT / "Assets" / "ProductionArt" / "Docs",
    ]
    old_forward = "Assets/" + "ProjectOEN/ProductionArt"
    old_backslash = "Assets\\" + "ProjectOEN\\ProductionArt"
    for target in scan_roots:
        files = [target] if target.is_file() else [path for path in target.rglob("*") if path.is_file()]
        for path in files:
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            if old_forward in text or old_backslash in text:
                errors.append(f"legacy art-root reference: {path.relative_to(ROOT)}")

    try:
        runtime = json.loads(RUNTIME_ASMDEF.read_text(encoding="utf-8"))
        if runtime.get("name") != "ProjectOen.Art" or runtime.get("references") != []:
            errors.append("ProjectOen.Art runtime asmdef must be dependency-free and correctly named")
    except Exception as exc:
        errors.append(f"invalid runtime asmdef: {exc}")

    try:
        editor = json.loads(EDITOR_ASMDEF.read_text(encoding="utf-8"))
        if editor.get("name") != "ProjectOen.Art.Editor":
            errors.append("ProjectOen.Art.Editor asmdef has the wrong name")
        if editor.get("includePlatforms") != ["Editor"]:
            errors.append("ProjectOen.Art.Editor asmdef must be Editor-only")
        if editor.get("references") != ["ProjectOen.Art"]:
            errors.append("ProjectOen.Art.Editor asmdef must reference only ProjectOen.Art")
    except Exception as exc:
        errors.append(f"invalid editor asmdef: {exc}")

    generators = (
        ROOT / "tools" / "generated_art" / "generate_production_art.py",
        ROOT / "tools" / "generated_art" / "generate_mockup_atlas_expansion.py",
        ROOT / "tools" / "generated_art" / "refine_material_textures.py",
        ROOT / "tools" / "generated_art" / "refine_set_dressing_art.py",
    )
    for generator in generators:
        if "stable_production_art_guid_path" not in generator.read_text(encoding="utf-8"):
            errors.append(f"generator bypasses stable ProductionArt GUID identity: {generator.relative_to(ROOT)}")

    guid_samples = (
        (ART_ROOT / "Meshes" / "props_tools" / "pr-001_tarp_presenning__folded.obj", "ProjectOEN.ProductionArt.v2:"),
        (ART_ROOT / "Meshes" / "atlas_expansion" / "radio__communication" / "ax-com-001_handheld_radio__off.obj", "ProjectOEN.AtlasExpansion.v1:"),
        (ART_ROOT / "Materials" / "Textures" / "wood_normal.png", "ProjectOEN.Surface.v1:"),
        (ART_ROOT / "Decals" / "environment_set_dressing" / "en-011_wet_mud_puddle_decal_set__small.png", "ProjectOEN.ProductionArt.Decal.v1:"),
    )
    for asset, salt in guid_samples:
        try:
            identity = stable_production_art_guid_path(asset, ROOT)
            expected = hashlib.md5((salt + identity).encode()).hexdigest()
            actual = read_meta_guid(asset)
            if actual != expected:
                errors.append(f"unstable Unity GUID for {asset.relative_to(ROOT)}: {actual} != {expected}")
        except Exception as exc:
            errors.append(str(exc))

    contract_text = CONTRACT.read_text(encoding="utf-8", errors="replace")
    for token in (
        "at most `1.35x`",
        "`60 degree`",
        "`1024x1024`",
        "`512x512`",
        "ProductionArtWetnessDriver",
        "OenWeather",
        "CoopGame.cs",
    ):
        if token not in contract_text:
            errors.append(f"production-art contract missing decision token: {token}")

    print("Project OEN production-art import contract QA")
    print(f"  tracked paths : {len(tracked)}")
    print(f"  art files     : {sum(1 for path in tracked if path.startswith('Assets/ProductionArt/'))}")
    print("  assemblies    : ProjectOen.Art + Editor-only ProjectOen.Art.Editor")
    if errors:
        print(f"FAILED with {len(errors)} issue(s):")
        for error in errors:
            print(" - " + error)
        return 1
    print("PASS: art root is case-safe and the Unity art assemblies are isolated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
