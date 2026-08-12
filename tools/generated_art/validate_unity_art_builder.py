#!/usr/bin/env python3
"""Static contract checks for the Unity production-art prefab/material builder.

This does not pretend to replace an actual Unity Editor compile/run. It protects the
repo-side contract so the bootstrap cannot silently stop wiring the generated surface
maps or core Quest-friendly prefab behavior.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BUILDER = ROOT / "src" / "unity" / "ProjectOen.Art" / "Editor" / "ProductionArtPrefabBuilder.cs"
BOOTSTRAP = ROOT / "prototype" / "m0b-bootstrap" / "Bootstrap-M0b.ps1"

REQUIRED_BUILDER_TOKENS = (
    'Shader.Find("Universal Render Pipeline/Lit")',
    'Shader.Find("Standard")',
    'BuildOrUpdateProductionMaterials',
    'ApplyProductionMaterials',
    '"_BaseMap"',
    '"_BumpMap"',
    '"_MetallicGlossMap"',
    '"_EmissionColor"',
    '"_Cull"',
    'AddSimpleBoundsCollider',
    'AddQuestFriendlyActiveFireIfNeeded',
    'slug + "_albedo.png"',
    'slug + "_normal.png"',
    'slug + "_metallic_smoothness.png"',
)
MATERIAL_NAMES = ("Wood","Rope","Tarp","Metal","Stone","Leaf","Cloth","Mud","Fire","Char","Water")


def main() -> int:
    errors=[]
    if not BUILDER.exists():
        print(f"ERROR: missing Unity art builder: {BUILDER}")
        return 1
    text=BUILDER.read_text(encoding="utf-8")
    for token in REQUIRED_BUILDER_TOKENS:
        if token not in text:
            errors.append(f"Unity art builder contract missing token: {token}")
    for name in MATERIAL_NAMES:
        if f'"{name}"' not in text:
            errors.append(f"Unity art builder material catalog missing: {name}")

    if not BOOTSTRAP.exists():
        errors.append("M0b bootstrap is missing")
    else:
        b=BOOTSTRAP.read_text(encoding="utf-8")
        for token in ("ProductionArtPrefabBuilder.cs", "ProjectOen.Art.Editor.ProductionArtPrefabBuilder.BuildAll", "Assets\\ProjectOEN\\ProductionArt"):
            if token not in b:
                errors.append(f"Bootstrap no longer installs/builds production art: missing {token}")

    print("Project ØEN Unity art wiring QA")
    print(f"  material catalog : {len(MATERIAL_NAMES)}")
    print("  URP/fallback     : required")
    print("  maps             : albedo + normal + metallic/smoothness")
    print("  bootstrap        : production art + prefab build")
    if errors:
        print(f"\nFAILED with {len(errors)} issue(s):")
        for e in errors: print(" - "+e)
        return 1
    print("\nPASS: Unity-side production-art wiring contract is intact.")
    return 0


if __name__=="__main__":
    sys.exit(main())
