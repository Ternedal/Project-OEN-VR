#!/usr/bin/env python3
"""Static contract checks for Project ØEN Unity production-art integration.

This intentionally does not claim to replace a real Unity Editor compile/run. It
protects the repo-side contract: refined material wiring, prefab construction,
Stormnatten showcase composition, Quest-conscious lighting and strict separation
from the minimal M0b CoopGame performance/network gate.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BUILDER = ROOT / "src" / "unity" / "ProjectOen.Art" / "Editor" / "ProductionArtPrefabBuilder.cs"
SHOWCASE = ROOT / "src" / "unity" / "ProjectOen.Art" / "Editor" / "ProductionArtShowcaseBuilder.cs"
BOOTSTRAP = ROOT / "prototype" / "m0b-bootstrap" / "Bootstrap-M0b.ps1"
COOP_SETUP = ROOT / "src" / "unity" / "App" / "CoopGameSetup.cs"

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

REQUIRED_SHOWCASE_TOKENS = (
    'StormnattenArtShowcase.unity',
    'RenderSettings.ambientMode = AmbientMode.Trilight',
    'RenderSettings.fog = true',
    'QualitySettings.shadowDistance = 24f',
    'key.shadows = LightShadows.Soft',
    'fill.shadows = LightShadows.None',
    '"cs-003_"',     # usable shelter
    '"cs-008_"',     # small campfire
    '"cs-013_"',     # complete handmade signal beacon, unlit
    '"pr-005_"',     # portable radio
    '"pr-004_"',     # supply crate
    '"pr-020_"',     # shared-carry box
    '"en-001_"',     # shipwreck anchor
    '"en-007_"',     # palms
    'MarkEnvironmentStatic',
)


def main() -> int:
    errors=[]

    if not BUILDER.exists():
        errors.append(f"Missing Unity art builder: {BUILDER.relative_to(ROOT)}")
        builder_text=""
    else:
        builder_text=BUILDER.read_text(encoding="utf-8")
        for token in REQUIRED_BUILDER_TOKENS:
            if token not in builder_text:
                errors.append(f"Unity art builder contract missing token: {token}")
        for name in MATERIAL_NAMES:
            if f'"{name}"' not in builder_text:
                errors.append(f"Unity art builder material catalog missing: {name}")

    if not SHOWCASE.exists():
        errors.append(f"Missing Stormnatten showcase builder: {SHOWCASE.relative_to(ROOT)}")
        showcase_text=""
    else:
        showcase_text=SHOWCASE.read_text(encoding="utf-8")
        for token in REQUIRED_SHOWCASE_TOKENS:
            if token not in showcase_text:
                errors.append(f"Showcase contract missing token: {token}")

        # Exactly one realtime shadow-casting source is the intentional showcase ceiling.
        shadow_casters=showcase_text.count("LightShadows.Soft") + showcase_text.count("LightShadows.Hard")
        if shadow_casters != 1:
            errors.append(f"Showcase must define exactly one shadow-casting realtime light, found {shadow_casters}")

        # The showcase is visual review only. Never put it into Android build settings here.
        if "EditorBuildSettings.scenes" in showcase_text or "BuildPipeline.BuildPlayer" in showcase_text:
            errors.append("Showcase builder must not modify build settings or build the Android player")

        # Do not light both campfire and signal beacon in the review scene: the selected
        # signal state is deliberately complete/unlit to keep runtime VFX/light pressure bounded.
        if '"cs-014_"' in showcase_text:
            errors.append("Showcase must use complete/unlit signal state (CS-013), not active CS-014")

    if not BOOTSTRAP.exists():
        errors.append("M0b bootstrap is missing")
    else:
        b=BOOTSTRAP.read_text(encoding="utf-8")
        bootstrap_tokens=(
            "ProductionArtPrefabBuilder.cs",
            "ProductionArtShowcaseBuilder.cs",
            "ProjectOen.Art.Editor.ProductionArtPrefabBuilder.BuildAll",
            "ProjectOen.Art.Editor.ProductionArtShowcaseBuilder.BuildShowcase",
            "Assets\\ProjectOEN\\ProductionArt",
            "Showcase-scenen er kun visual review",
        )
        for token in bootstrap_tokens:
            if token not in b:
                errors.append(f"Bootstrap production-art/showcase contract missing: {token}")

    # M0b's network/performance gate stays intentionally boring. Visual showcase work
    # must never change which scene CoopGameSetup builds into the APK.
    if not COOP_SETUP.exists():
        errors.append("CoopGameSetup.cs is missing")
    else:
        c=COOP_SETUP.read_text(encoding="utf-8")
        if 'const string ScenePath = SceneDir + "/CoopGame.unity"' not in c:
            errors.append("M0b CoopGame scene path contract changed")
        if "StormnattenArtShowcase" in c:
            errors.append("Stormnatten showcase leaked into minimal CoopGame M0b gate")
        if "BuildPipeline.BuildPlayer" not in c or "scenes = new[] { ScenePath }" not in c:
            errors.append("M0b Android build no longer explicitly builds only CoopGame.unity")

    print("Project ØEN Unity art integration QA")
    print(f"  material catalog : {len(MATERIAL_NAMES)}")
    print("  maps             : albedo + normal + metallic/smoothness")
    print("  showcase         : usable camp + radio + wreck + unlit beacon")
    print("  shadow casters   : exactly 1")
    print("  M0b separation   : CoopGame-only Android build")

    if errors:
        print(f"\nFAILED with {len(errors)} issue(s):")
        for e in errors: print(" - "+e)
        return 1

    print("\nPASS: Unity production-art and Stormnatten showcase contracts are intact.")
    return 0


if __name__=="__main__":
    sys.exit(main())
