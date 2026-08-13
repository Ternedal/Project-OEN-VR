#!/usr/bin/env python3
"""Global static contract for Project ØEN Unity production-art integration.

Dedicated validators own detailed VFX/UI/world quality. This gate protects the
shared integration order, core material/decal/storm contracts, event-driven wet
surface response and strict separation from the minimal M0b CoopGame Android gate.
"""
from __future__ import annotations
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
EDITOR=ROOT/"src"/"unity"/"ProjectOen.Art"/"Editor"
RUNTIME=ROOT/"src"/"unity"/"ProjectOen.Art"/"Runtime"
BUILDER=EDITOR/"ProductionArtPrefabBuilder.cs"
DECAL=EDITOR/"ProductionArtDecalBuilder.cs"
SHOWCASE=EDITOR/"ProductionArtShowcaseBuilder.cs"
ATMOS=EDITOR/"ProductionArtStormAtmosphereBuilder.cs"
WETNESS=RUNTIME/"ProductionArtWetnessDriver.cs"
AUDIT=EDITOR/"ProductionArtShowcaseAudit.cs"
MENU=EDITOR/"ProductionArtReviewMenu.cs"
BOOT=ROOT/"prototype"/"m0b-bootstrap"/"Bootstrap-M0b.ps1"
REVIEW=ROOT/"prototype"/"m0b-bootstrap"/"Review-ProductionArt.ps1"
COOP=ROOT/"src"/"unity"/"App"/"CoopGameSetup.cs"
MATERIALS=("Wood","Rope","Tarp","Metal","Stone","Leaf","Cloth","Mud","Fire","Char","Water")
WETTABLE=("Wood","Rope","Tarp","Metal","Stone","Leaf","Cloth","Mud","Char")


def need(path,label,tokens,errors):
    if not path.exists(): errors.append(f"Missing {label}: {path.relative_to(ROOT)}"); return ""
    text=path.read_text(encoding="utf-8")
    for t in tokens:
        if t not in text: errors.append(f"{label} missing contract token: {t}")
    return text


def ordered(text,names):
    pos=[text.find(n) for n in names]
    return min(pos)>=0 and pos==sorted(pos)


def main():
    errors=[]
    b=need(BUILDER,"world prefab builder",(
        'Shader.Find("Universal Render Pipeline/Lit")','Shader.Find("Standard")',
        'BuildOrUpdateProductionMaterials','ApplyProductionMaterials','"_BaseMap"','"_BumpMap"',
        '"_MetallicGlossMap"','AddSimpleBoundsCollider','AddQuestFriendlyActiveFireIfNeeded',
        'slug + "_albedo.png"','slug + "_normal.png"','slug + "_metallic_smoothness.png"',
    ),errors)
    for m in MATERIALS:
        if b and f'"{m}"' not in b: errors.append(f"World material catalog missing: {m}")

    wet=need(WETNESS,"runtime wetness driver",(
        '[ExecuteAlways]','[DisallowMultipleComponent]','MaterialPropertyBlock',
        'SetWetness(float value)','ApplyWetness()','GetPropertyBlock','SetPropertyBlock',
        'GetRootGameObjects','"_BaseColor"','"_Color"','"_BumpScale"',
        'Color.Lerp(Color.white, profile.wetTint, wetness)',
        'Mathf.Lerp(1f, profile.wetBumpScale, wetness)',
    ),errors)
    for m in WETTABLE:
        if wet and f'case "{m}":' not in wet: errors.append(f"Wetness profile missing: {m}")
    if wet:
        for forbidden in ('void Update(', 'void LateUpdate(', 'renderer.material', '.sharedMaterials ='):
            if forbidden in wet: errors.append(f"Wetness driver violates event-driven/shared-material contract: {forbidden}")
        if 'case "Fire":' in wet or 'case "Water":' in wet:
            errors.append("Wetness driver must not override Fire or Water material response")

    d=need(DECAL,"ground decal builder",(
        'Assets/ProjectOEN/ProductionArt/Decals/environment_set_dressing',
        'Universal Render Pipeline/Unlit','Unlit/Transparent','StartsWith("en-011_"','StartsWith("en-025_"',
        'built != 5','renderer.shadowCastingMode = ShadowCastingMode.Off','renderer.receiveShadows = false',
        'DestroyImmediate(collider)','RenderQueue.Transparent',
    ),errors)
    if d and any(x in d for x in ("AddComponent<BoxCollider>","LightShadows.Soft","LightShadows.Hard","BuildPipeline.BuildPlayer")):
        errors.append("Ground decal builder violates no-collider/no-shadow/no-build contract")

    s=need(SHOWCASE,"Stormnatten showcase",(
        'StormnattenArtShowcase.unity','RenderSettings.ambientMode = AmbientMode.Trilight','RenderSettings.fog = true',
        'QualitySettings.shadowDistance = 24f','key.shadows = LightShadows.Soft','fill.shadows = LightShadows.None',
        '"cs-003_"','"cs-008_"','"cs-013_"','"pr-005_"','"en-001_"','"en-007_"','MarkEnvironmentStatic',
    ),errors)
    if s:
        shadows=s.count("LightShadows.Soft")+s.count("LightShadows.Hard")
        if shadows!=1: errors.append(f"Stormnatten showcase must define exactly one shadow caster, found {shadows}")
        if "BuildPipeline.BuildPlayer" in s or "EditorBuildSettings.scenes" in s: errors.append("Stormnatten showcase must not alter build settings")

    a=need(ATMOS,"storm atmosphere",(
        'StormnattenArtShowcase.unity','Storm Rain Volume','Storm Surface Wetness',
        'Universal Render Pipeline/Particles/Unlit','main.maxParticles = 180','emission.rateOverTime = 135f',
        'ParticleSystemShapeType.Box','ParticleSystemRenderMode.Stretch','ShadowCastingMode.Off',
        'BlendMode.SrcAlpha','BlendMode.OneMinusSrcAlpha',
        'AddComponent<ProductionArtWetnessDriver>','ShowcaseWetness = 0.78f','SetWetness(ShowcaseWetness)',
    ),errors)
    if a and (a.count("AddComponent<ParticleSystem>")!=1 or ".collision" in a or "ParticleSystemCollision" in a):
        errors.append("Storm atmosphere must remain one no-collision particle system")
    if a and a.count("AddComponent<ProductionArtWetnessDriver>") != 1:
        errors.append("Storm atmosphere must create exactly one scene-wide wetness driver")

    audit=need(AUDIT,"Stormnatten budget audit",(
        'TriangleHardLimit = 750000','DrawCallProxyHardLimit = 130','ShadowCasterHardLimit = 1',
        'ParticleSystemHardLimit = 10','mesh.triangles.LongLength / 3L','Quest 2 showcase budget hard gate failed',
    ),errors)
    if audit and "EditorApplication.Exit(0)" in audit: errors.append("Budget audit must not force success")

    menu=need(MENU,"review menu",(
        'Open Stormnatten Art Showcase','Open Diegetic UI Art Showcase','Open Production VFX Showcase',
        'StormnattenArtShowcase.unity','DiegeticUiArtShowcase.unity','ProductionVfxShowcase.unity','EditorSceneManager.OpenScene',
    ),errors)
    if menu and ("BuildPipeline.BuildPlayer" in menu or "EditorBuildSettings.scenes" in menu): errors.append("Review menu must not touch build settings")

    review=need(REVIEW,"fast review",(
        'ProductionArtPrefabBuilder.BuildAll','ProductionArtDecalBuilder.BuildAll','ProductionArtVfxBuilder.BuildAll',
        'ProductionArtVfxShowcaseBuilder.BuildShowcase','ProductionArtVfxShowcaseAudit.AuditShowcase',
        'ProductionArtDiegeticUiBuilder.BuildAll','ProductionArtUiShowcaseBuilder.BuildShowcase','ProductionArtUiShowcaseAudit.AuditShowcase',
        'ProductionArtShowcaseBuilder.BuildShowcase','ProductionArtStormAtmosphereBuilder.AddStormAtmosphere','ProductionArtShowcaseAudit.AuditShowcase',
        'ProductionArtReviewMenu.OpenShowcase','M0b CoopGame/build settings er ikke aendret',
    ),errors)
    sequence=(
        'ProductionArtPrefabBuilder.BuildAll','ProductionArtDecalBuilder.BuildAll','ProductionArtVfxBuilder.BuildAll',
        'ProductionArtVfxShowcaseBuilder.BuildShowcase','ProductionArtVfxShowcaseAudit.AuditShowcase',
        'ProductionArtDiegeticUiBuilder.BuildAll','ProductionArtUiShowcaseBuilder.BuildShowcase','ProductionArtUiShowcaseAudit.AuditShowcase',
        'ProductionArtShowcaseBuilder.BuildShowcase','ProductionArtStormAtmosphereBuilder.AddStormAtmosphere','ProductionArtShowcaseAudit.AuditShowcase',
        'ProductionArtReviewMenu.OpenShowcase',
    )
    if review:
        if not ordered(review,sequence): errors.append("Fast review art sequence is out of order")
        for bad in ("M0bConfigure.Configure","BuildPipeline.BuildPlayer","Packages\\manifest.json"):
            if bad in review: errors.append(f"Fast review must not mutate M0b platform path: {bad}")

    boot=need(BOOT,"M0b bootstrap",(
        'ProductionArtPrefabBuilder.BuildAll','ProductionArtDecalBuilder.BuildAll','ProductionArtVfxBuilder.BuildAll',
        'ProductionArtVfxShowcaseBuilder.BuildShowcase','ProductionArtVfxShowcaseAudit.AuditShowcase',
        'ProductionArtDiegeticUiBuilder.BuildAll','ProductionArtUiShowcaseBuilder.BuildShowcase','ProductionArtUiShowcaseAudit.AuditShowcase',
        'ProductionArtShowcaseBuilder.BuildShowcase','ProductionArtStormAtmosphereBuilder.AddStormAtmosphere','ProductionArtShowcaseAudit.AuditShowcase',
        'Alle tre review-scener er visual review',
    ),errors)
    boot_sequence=sequence[:-1]
    if boot and not ordered(boot,boot_sequence): errors.append("M0b bootstrap art sequence is out of order")

    coop=need(COOP,"CoopGame setup",('const string ScenePath = SceneDir + "/CoopGame.unity"','BuildPipeline.BuildPlayer','scenes = new[] { ScenePath }'),errors)
    if coop and any(x in coop for x in ("StormnattenArtShowcase","DiegeticUiArtShowcase","ProductionVfxShowcase","Storm Rain Volume","Storm Surface Wetness")):
        errors.append("Visual-review content leaked into minimal CoopGame M0b gate")

    print("Project ØEN global Unity art integration QA")
    print(f"  world materials : {len(MATERIALS)}")
    print(f"  wettable mats   : {len(WETTABLE)} (event-driven MaterialPropertyBlock)")
    print("  review scenes   : VFX + physical UI + Stormnatten")
    print("  review order    : world -> decals -> VFX/audit -> UI/audit -> Stormnatten/audit")
    print("  M0b separation  : CoopGame-only Android build")
    if errors:
        print(f"\nFAILED with {len(errors)} issue(s):")
        for e in errors: print(" - "+e)
        return 1
    print("\nPASS: global Unity production-art integration contract is intact.")
    return 0

if __name__=="__main__": sys.exit(main())
