#!/usr/bin/env python3
"""Static contract checks for Project ØEN Unity production-art integration.

This intentionally does not replace a real Unity Editor compile/run. It protects
repo-side world material/prefab/decal/showcase wiring, the serialized art-review
sequence and strict separation from the minimal M0b CoopGame gate. Dedicated UI
validators own the detailed diegetic-UI prefab/physical-scale contracts.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
EDITOR=ROOT/"src"/"unity"/"ProjectOen.Art"/"Editor"
BUILDER=EDITOR/"ProductionArtPrefabBuilder.cs"
DECAL_BUILDER=EDITOR/"ProductionArtDecalBuilder.cs"
SHOWCASE=EDITOR/"ProductionArtShowcaseBuilder.cs"
ATMOSPHERE=EDITOR/"ProductionArtStormAtmosphereBuilder.cs"
AUDIT=EDITOR/"ProductionArtShowcaseAudit.cs"
REVIEW_MENU=EDITOR/"ProductionArtReviewMenu.cs"
BOOTSTRAP=ROOT/"prototype"/"m0b-bootstrap"/"Bootstrap-M0b.ps1"
REVIEW_SCRIPT=ROOT/"prototype"/"m0b-bootstrap"/"Review-ProductionArt.ps1"
COOP_SETUP=ROOT/"src"/"unity"/"App"/"CoopGameSetup.cs"

REQUIRED_BUILDER_TOKENS=(
    'Shader.Find("Universal Render Pipeline/Lit")','Shader.Find("Standard")',
    'BuildOrUpdateProductionMaterials','ApplyProductionMaterials','"_BaseMap"',
    '"_BumpMap"','"_MetallicGlossMap"','"_EmissionColor"','"_Cull"',
    'AddSimpleBoundsCollider','AddQuestFriendlyActiveFireIfNeeded',
    'slug + "_albedo.png"','slug + "_normal.png"','slug + "_metallic_smoothness.png"',
)
MATERIAL_NAMES=("Wood","Rope","Tarp","Metal","Stone","Leaf","Cloth","Mud","Fire","Char","Water")

REQUIRED_DECAL_TOKENS=(
    'Assets/ProjectOEN/ProductionArt/Decals/environment_set_dressing',
    'Assets/ProjectOEN/ProductionArt/Prefabs/environment_set_dressing',
    'Universal Render Pipeline/Unlit','Unlit/Transparent','Sprites/Default',
    'StartsWith("en-011_"','StartsWith("en-025_"','built != 5',
    'renderer.shadowCastingMode = ShadowCastingMode.Off','renderer.receiveShadows = false',
    'DestroyImmediate(collider)','material.EnableKeyword("_SURFACE_TYPE_TRANSPARENT")','RenderQueue.Transparent',
)

REQUIRED_SHOWCASE_TOKENS=(
    'StormnattenArtShowcase.unity','RenderSettings.ambientMode = AmbientMode.Trilight',
    'RenderSettings.fog = true','QualitySettings.shadowDistance = 24f',
    'key.shadows = LightShadows.Soft','fill.shadows = LightShadows.None',
    '"cs-003_"','"cs-008_"','"cs-013_"','"pr-005_"','"pr-004_"','"pr-020_"',
    '"en-001_"','"en-007_"','MarkEnvironmentStatic',
)
REQUIRED_ATMOSPHERE_TOKENS=(
    'StormnattenArtShowcase.unity','Storm Rain Volume','Universal Render Pipeline/Particles/Unlit',
    'main.maxParticles = 180','emission.rateOverTime = 135f',
    'shape.shapeType = ParticleSystemShapeType.Box','velocity.space = ParticleSystemSimulationSpace.World',
    'renderer.renderMode = ParticleSystemRenderMode.Stretch','renderer.shadowCastingMode = ShadowCastingMode.Off',
    'renderer.receiveShadows = false','BlendMode.SrcAlpha','BlendMode.OneMinusSrcAlpha',
)
REQUIRED_AUDIT_TOKENS=(
    'StormnattenArtShowcase.unity','TriangleTarget = 500000','TriangleHardLimit = 750000',
    'DrawCallProxyTarget = 100','DrawCallProxyHardLimit = 130','ShadowCasterHardLimit = 1',
    'ParticleSystemHardLimit = 10','mesh.triangles.LongLength / 3L',
    'rendererMaterialSlots(draw-call proxy)','l.shadows != LightShadows.None',
    'Quest 2 showcase budget hard gate failed',
)
REQUIRED_REVIEW_MENU_TOKENS=('Open Stormnatten Art Showcase','StormnattenArtShowcase.unity','EditorSceneManager.OpenScene')

REQUIRED_REVIEW_SCRIPT_TOKENS=(
    '"Decals"','ProductionArtDecalBuilder.cs','ProductionArtDiegeticUiBuilder.cs',
    'ProductionArtUiShowcaseBuilder.cs','ProductionArtUiShowcaseAudit.cs',
    'ProductionArtPrefabBuilder.BuildAll','ProductionArtDecalBuilder.BuildAll',
    'ProductionArtDiegeticUiBuilder.BuildAll','ProductionArtUiShowcaseBuilder.BuildShowcase',
    'ProductionArtUiShowcaseAudit.AuditShowcase','ProductionArtShowcaseBuilder.BuildShowcase',
    'ProductionArtStormAtmosphereBuilder.AddStormAtmosphere','ProductionArtShowcaseAudit.AuditShowcase',
    'ProductionArtReviewMenu.OpenShowcase','[switch]$OpenEditor',
    'M0b CoopGame/build settings er ikke aendret',
)


def require_tokens(errors,label,path,tokens):
    if not path.exists():
        errors.append(f"Missing {label}: {path.relative_to(ROOT)}")
        return ""
    text=path.read_text(encoding="utf-8")
    for token in tokens:
        if token not in text: errors.append(f"{label} contract missing token: {token}")
    return text


def main()->int:
    errors=[]
    builder_text=require_tokens(errors,"Unity art builder",BUILDER,REQUIRED_BUILDER_TOKENS)
    if builder_text:
        for name in MATERIAL_NAMES:
            if f'"{name}"' not in builder_text: errors.append(f"Unity art builder material catalog missing: {name}")

    decal_text=require_tokens(errors,"Ground decal builder",DECAL_BUILDER,REQUIRED_DECAL_TOKENS)
    if decal_text:
        if "AddComponent<BoxCollider>" in decal_text: errors.append("Ground decal builder must not create colliders")
        if "LightShadows.Soft" in decal_text or "LightShadows.Hard" in decal_text: errors.append("Ground decals must not add shadow-casting lights")
        if "BuildPipeline.BuildPlayer" in decal_text or "EditorBuildSettings.scenes" in decal_text: errors.append("Ground decal builder must not alter Android build settings")

    showcase_text=require_tokens(errors,"Showcase",SHOWCASE,REQUIRED_SHOWCASE_TOKENS)
    if showcase_text:
        shadow_casters=showcase_text.count("LightShadows.Soft")+showcase_text.count("LightShadows.Hard")
        if shadow_casters!=1: errors.append(f"Showcase must define exactly one shadow-casting realtime light, found {shadow_casters}")
        if "EditorBuildSettings.scenes" in showcase_text or "BuildPipeline.BuildPlayer" in showcase_text: errors.append("Showcase builder must not modify build settings or build Android player")
        if '"cs-014_"' in showcase_text: errors.append("Showcase must use complete/unlit signal state (CS-013), not active CS-014")

    atmosphere_text=require_tokens(errors,"Storm atmosphere",ATMOSPHERE,REQUIRED_ATMOSPHERE_TOKENS)
    if atmosphere_text:
        if atmosphere_text.count("AddComponent<ParticleSystem>")!=1: errors.append("Storm atmosphere must author exactly one particle system")
        if "LightShadows.Soft" in atmosphere_text or "LightShadows.Hard" in atmosphere_text: errors.append("Storm atmosphere must not add another shadow-casting light")
        if "BuildPipeline.BuildPlayer" in atmosphere_text or "EditorBuildSettings.scenes" in atmosphere_text: errors.append("Storm atmosphere pass must not touch Android build settings")
        if "ParticleSystemCollision" in atmosphere_text or ".collision" in atmosphere_text: errors.append("Storm rain must not add particle collision work on Quest 2 review path")

    audit_text=require_tokens(errors,"Showcase budget audit",AUDIT,REQUIRED_AUDIT_TOKENS)
    if audit_text:
        if "BuildPipeline.BuildPlayer" in audit_text or "EditorBuildSettings.scenes" in audit_text: errors.append("Budget audit must not alter Android build settings")
        if "EditorApplication.Exit(0)" in audit_text: errors.append("Budget audit must not force-success Unity batch process")

    review_menu_text=require_tokens(errors,"Review menu",REVIEW_MENU,REQUIRED_REVIEW_MENU_TOKENS)
    if review_menu_text and ("BuildPipeline.BuildPlayer" in review_menu_text or "EditorBuildSettings.scenes" in review_menu_text):
        errors.append("Review menu must only open the showcase, never alter build settings")

    review=require_tokens(errors,"Fast art review script",REVIEW_SCRIPT,REQUIRED_REVIEW_SCRIPT_TOKENS)
    if review:
        for token in ("M0bConfigure.Configure","BuildPipeline.BuildPlayer","CoopGameSetup.SetupAndBuild","Packages\\manifest.json"):
            if token in review: errors.append(f"Fast art review loop must not mutate/rebuild M0b platform path: {token}")
        names=(
            "ProductionArtPrefabBuilder.BuildAll","ProductionArtDecalBuilder.BuildAll",
            "ProductionArtDiegeticUiBuilder.BuildAll","ProductionArtUiShowcaseBuilder.BuildShowcase",
            "ProductionArtUiShowcaseAudit.AuditShowcase","ProductionArtShowcaseBuilder.BuildShowcase",
            "ProductionArtStormAtmosphereBuilder.AddStormAtmosphere","ProductionArtShowcaseAudit.AuditShowcase",
            "ProductionArtReviewMenu.OpenShowcase",
        )
        pos=[review.find(n) for n in names]
        if min(pos)<0 or pos!=sorted(pos):
            errors.append("Fast art review order must be world -> decals -> UI prefabs -> UI scene/audit -> Stormnatten -> storm -> budget audit -> optional editor open")

    if not BOOTSTRAP.exists():
        errors.append("M0b bootstrap is missing")
    else:
        b=BOOTSTRAP.read_text(encoding="utf-8")
        bootstrap_tokens=(
            '"Decals"',"ProductionArtPrefabBuilder.cs","ProductionArtDecalBuilder.cs",
            "ProductionArtDiegeticUiBuilder.cs","ProductionArtUiShowcaseBuilder.cs","ProductionArtUiShowcaseAudit.cs",
            "ProductionArtShowcaseBuilder.cs","ProductionArtStormAtmosphereBuilder.cs","ProductionArtShowcaseAudit.cs",
            "ProjectOen.Art.Editor.ProductionArtPrefabBuilder.BuildAll",
            "ProjectOen.Art.Editor.ProductionArtDecalBuilder.BuildAll",
            "ProjectOen.Art.Editor.ProductionArtDiegeticUiBuilder.BuildAll",
            "ProjectOen.Art.Editor.ProductionArtUiShowcaseBuilder.BuildShowcase",
            "ProjectOen.Art.Editor.ProductionArtUiShowcaseAudit.AuditShowcase",
            "ProjectOen.Art.Editor.ProductionArtShowcaseBuilder.BuildShowcase",
            "ProjectOen.Art.Editor.ProductionArtStormAtmosphereBuilder.AddStormAtmosphere",
            "ProjectOen.Art.Editor.ProductionArtShowcaseAudit.AuditShowcase",
            "Assets\\ProjectOEN\\ProductionArt","Begge review-scener er visual review",
        )
        for token in bootstrap_tokens:
            if token not in b: errors.append(f"Bootstrap production-art/showcase contract missing: {token}")
        sequence=(
            "ProductionArtPrefabBuilder.BuildAll","ProductionArtDecalBuilder.BuildAll",
            "ProductionArtDiegeticUiBuilder.BuildAll","ProductionArtUiShowcaseBuilder.BuildShowcase",
            "ProductionArtUiShowcaseAudit.AuditShowcase","ProductionArtShowcaseBuilder.BuildShowcase",
            "ProductionArtStormAtmosphereBuilder.AddStormAtmosphere","ProductionArtShowcaseAudit.AuditShowcase",
        )
        pos=[b.find(n) for n in sequence]
        if min(pos)<0 or pos!=sorted(pos): errors.append("Bootstrap art sequence is out of order")

    if not COOP_SETUP.exists():
        errors.append("CoopGameSetup.cs is missing")
    else:
        c=COOP_SETUP.read_text(encoding="utf-8")
        if 'const string ScenePath = SceneDir + "/CoopGame.unity"' not in c: errors.append("M0b CoopGame scene path contract changed")
        if "StormnattenArtShowcase" in c or "DiegeticUiArtShowcase" in c or "Storm Rain Volume" in c: errors.append("Visual-review content leaked into minimal CoopGame M0b gate")
        if "BuildPipeline.BuildPlayer" not in c or "scenes = new[] { ScenePath }" not in c: errors.append("M0b Android build no longer explicitly builds only CoopGame.unity")

    print("Project ØEN Unity art integration QA")
    print(f"  material catalog : {len(MATERIAL_NAMES)}")
    print("  ground decals    : 3 puddle + 2 shoreline / no colliders or shadows")
    print("  diegetic UI      : prefabs + separate physical-scale review/audit")
    print("  Stormnatten      : enriched showcase + bounded storm + Quest 2 hard audit")
    print("  review order     : world -> decals -> UI -> UI audit -> Stormnatten -> audit")
    print("  M0b separation   : CoopGame-only Android build")
    if errors:
        print(f"\nFAILED with {len(errors)} issue(s):")
        for e in errors: print(" - "+e)
        return 1
    print("\nPASS: Unity production-art integration and review-loop contracts are intact.")
    return 0

if __name__=="__main__": sys.exit(main())
