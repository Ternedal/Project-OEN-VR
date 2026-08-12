#!/usr/bin/env python3
"""Static contract checks for Project ØEN Unity production-art integration.

This intentionally does not claim to replace a real Unity Editor compile/run. It
protects the repo-side contract: refined material wiring, prefab construction,
Stormnatten showcase composition, Quest-conscious lighting/weather, an actual
Unity-import budget audit, and strict separation from the minimal M0b CoopGame gate.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EDITOR = ROOT / "src" / "unity" / "ProjectOen.Art" / "Editor"
BUILDER = EDITOR / "ProductionArtPrefabBuilder.cs"
SHOWCASE = EDITOR / "ProductionArtShowcaseBuilder.cs"
ATMOSPHERE = EDITOR / "ProductionArtStormAtmosphereBuilder.cs"
AUDIT = EDITOR / "ProductionArtShowcaseAudit.cs"
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
    '"cs-003_"',
    '"cs-008_"',
    '"cs-013_"',
    '"pr-005_"',
    '"pr-004_"',
    '"pr-020_"',
    '"en-001_"',
    '"en-007_"',
    'MarkEnvironmentStatic',
)

REQUIRED_ATMOSPHERE_TOKENS = (
    'StormnattenArtShowcase.unity',
    'Storm Rain Volume',
    'Universal Render Pipeline/Particles/Unlit',
    'main.maxParticles = 180',
    'emission.rateOverTime = 135f',
    'shape.shapeType = ParticleSystemShapeType.Box',
    'velocity.space = ParticleSystemSimulationSpace.World',
    'renderer.renderMode = ParticleSystemRenderMode.Stretch',
    'renderer.shadowCastingMode = ShadowCastingMode.Off',
    'renderer.receiveShadows = false',
)

REQUIRED_AUDIT_TOKENS = (
    'StormnattenArtShowcase.unity',
    'TriangleTarget = 500000',
    'TriangleHardLimit = 750000',
    'DrawCallProxyTarget = 100',
    'DrawCallProxyHardLimit = 130',
    'ShadowCasterHardLimit = 1',
    'ParticleSystemHardLimit = 10',
    'mesh.triangles.LongLength / 3L',
    'rendererMaterialSlots(draw-call proxy)',
    'l.shadows != LightShadows.None',
    'Quest 2 showcase budget hard gate failed',
)


def require_tokens(errors, label, path, tokens):
    if not path.exists():
        errors.append(f"Missing {label}: {path.relative_to(ROOT)}")
        return ""
    text=path.read_text(encoding="utf-8")
    for token in tokens:
        if token not in text:
            errors.append(f"{label} contract missing token: {token}")
    return text


def main() -> int:
    errors=[]

    builder_text=require_tokens(errors,"Unity art builder",BUILDER,REQUIRED_BUILDER_TOKENS)
    if builder_text:
        for name in MATERIAL_NAMES:
            if f'"{name}"' not in builder_text:
                errors.append(f"Unity art builder material catalog missing: {name}")

    showcase_text=require_tokens(errors,"Showcase",SHOWCASE,REQUIRED_SHOWCASE_TOKENS)
    if showcase_text:
        shadow_casters=showcase_text.count("LightShadows.Soft") + showcase_text.count("LightShadows.Hard")
        if shadow_casters != 1:
            errors.append(f"Showcase must define exactly one shadow-casting realtime light, found {shadow_casters}")
        if "EditorBuildSettings.scenes" in showcase_text or "BuildPipeline.BuildPlayer" in showcase_text:
            errors.append("Showcase builder must not modify build settings or build the Android player")
        if '"cs-014_"' in showcase_text:
            errors.append("Showcase must use complete/unlit signal state (CS-013), not active CS-014")

    atmosphere_text=require_tokens(errors,"Storm atmosphere",ATMOSPHERE,REQUIRED_ATMOSPHERE_TOKENS)
    if atmosphere_text:
        if atmosphere_text.count("AddComponent<ParticleSystem>") != 1:
            errors.append("Storm atmosphere must author exactly one particle system")
        if "LightShadows.Soft" in atmosphere_text or "LightShadows.Hard" in atmosphere_text:
            errors.append("Storm atmosphere must not add another shadow-casting light")
        if "BuildPipeline.BuildPlayer" in atmosphere_text or "EditorBuildSettings.scenes" in atmosphere_text:
            errors.append("Storm atmosphere pass must not touch Android build settings")
        if "ParticleSystemCollision" in atmosphere_text or ".collision" in atmosphere_text:
            errors.append("Storm rain must not add particle collision work on Quest 2 review path")

    audit_text=require_tokens(errors,"Showcase budget audit",AUDIT,REQUIRED_AUDIT_TOKENS)
    if audit_text:
        if "BuildPipeline.BuildPlayer" in audit_text or "EditorBuildSettings.scenes" in audit_text:
            errors.append("Budget audit must not alter Android build settings")
        if "EditorApplication.Exit(0)" in audit_text:
            errors.append("Budget audit must not force-success the Unity batch process")

    if not BOOTSTRAP.exists():
        errors.append("M0b bootstrap is missing")
    else:
        b=BOOTSTRAP.read_text(encoding="utf-8")
        bootstrap_tokens=(
            "ProductionArtPrefabBuilder.cs",
            "ProductionArtShowcaseBuilder.cs",
            "ProductionArtStormAtmosphereBuilder.cs",
            "ProductionArtShowcaseAudit.cs",
            "ProjectOen.Art.Editor.ProductionArtPrefabBuilder.BuildAll",
            "ProjectOen.Art.Editor.ProductionArtShowcaseBuilder.BuildShowcase",
            "ProjectOen.Art.Editor.ProductionArtStormAtmosphereBuilder.AddStormAtmosphere",
            "ProjectOen.Art.Editor.ProductionArtShowcaseAudit.AuditShowcase",
            "Assets\\ProjectOEN\\ProductionArt",
            "Showcase-scenen er kun visual review",
            "Quest 2 art-budgetaudit",
        )
        for token in bootstrap_tokens:
            if token not in b:
                errors.append(f"Bootstrap production-art/showcase contract missing: {token}")

    if not COOP_SETUP.exists():
        errors.append("CoopGameSetup.cs is missing")
    else:
        c=COOP_SETUP.read_text(encoding="utf-8")
        if 'const string ScenePath = SceneDir + "/CoopGame.unity"' not in c:
            errors.append("M0b CoopGame scene path contract changed")
        if "StormnattenArtShowcase" in c or "Storm Rain Volume" in c:
            errors.append("Stormnatten visual-review content leaked into minimal CoopGame M0b gate")
        if "BuildPipeline.BuildPlayer" not in c or "scenes = new[] { ScenePath }" not in c:
            errors.append("M0b Android build no longer explicitly builds only CoopGame.unity")

    print("Project ØEN Unity art integration QA")
    print(f"  material catalog : {len(MATERIAL_NAMES)}")
    print("  maps             : albedo + normal + metallic/smoothness")
    print("  showcase         : usable camp + radio + wreck + unlit beacon")
    print("  shadow casters   : exactly 1")
    print("  storm weather    : 1 local rain system / max 180 / no collision / no shadows")
    print("  Unity hard audit : 750k tris / 130 draw proxy / 1 shadow / 10 particle systems")
    print("  M0b separation   : CoopGame-only Android build")

    if errors:
        print(f"\nFAILED with {len(errors)} issue(s):")
        for e in errors: print(" - "+e)
        return 1

    print("\nPASS: Unity production-art, showcase, storm and budget-audit contracts are intact.")
    return 0


if __name__=="__main__":
    sys.exit(main())
