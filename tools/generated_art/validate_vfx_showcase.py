#!/usr/bin/env python3
"""Static contract for the isolated Project ØEN production-VFX review scene/audit."""
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
EDITOR=ROOT/"src"/"unity"/"ProjectOen.Art"/"Editor"
BUILDER=EDITOR/"ProductionArtVfxShowcaseBuilder.cs"
AUDIT=EDITOR/"ProductionArtVfxShowcaseAudit.cs"
BOOT=ROOT/"prototype"/"m0b-bootstrap"/"Bootstrap-M0b.ps1"
REVIEW=ROOT/"prototype"/"m0b-bootstrap"/"Review-ProductionArt.ps1"


def require(path,label,tokens,errors):
    if not path.exists(): errors.append(f"Missing {label}: {path.relative_to(ROOT)}"); return ""
    text=path.read_text(encoding="utf-8")
    for t in tokens:
        if t not in text: errors.append(f"{label} missing contract token: {t}")
    return text


def main():
    errors=[]
    b=require(BUILDER,"VFX showcase builder",(
        "ProductionVfxShowcase.unity","Production VFX Review Grid","VFX Review Camera",
        "fx_001_small_smoke.prefab","fx_001_medium_smoke.prefab",
        "fx_002_small_ember.prefab","fx_002_medium_ember.prefab","fx_003_single_ash.prefab",
        "fx_004_small_rain_splash.prefab","fx_004_medium_rain_splash.prefab",
        "fx_006_near_lightning.prefab","fx_006_far_lightning.prefab",
        "fx_007_fire_glow.prefab","fx_007_lantern_glow.prefab",
        "fx_008_small_objective_pulse.prefab","fx_008_medium_objective_pulse.prefab",
        "Wet Sheen Helper","DestroyCollider(basePlane)","DestroyCollider(sheen)",
        "renderer.shadowCastingMode = ShadowCastingMode.Off","renderer.receiveShadows = false",
    ),errors)
    a=require(AUDIT,"VFX showcase audit",(
        "ProductionVfxShowcase.unity","ExpectedParticleSystems = 7","ExpectedBillboardSprites = 6",
        "MaxParticlesPerSystem = 28","main.playOnAwake","ps.collision.enabled",
        "sheet.numTilesX != 4","sheet.numTilesY != 4","colliders != 0",
        "GetComponents<Light>()","EditorBuildSettings.scenes",
    ),errors)
    for label,text in (("builder",b),("audit",a)):
        for bad in ("BuildPipeline.BuildPlayer","CoopGame.unity","AddComponent<Light>"):
            if bad in text: errors.append(f"VFX showcase {label} must not touch/add: {bad}")

    for path,label,buildlog,auditlog in (
        (BOOT,"bootstrap","production-art-vfx-showcase.log","production-art-vfx-audit.log"),
        (REVIEW,"review","review-art-vfx-showcase.log","review-art-vfx-audit.log"),
    ):
        s=require(path,label,(
            "ProductionArtVfxShowcaseBuilder.cs","ProductionArtVfxShowcaseAudit.cs",
            "ProductionArtVfxShowcaseBuilder.BuildShowcase","ProductionArtVfxShowcaseAudit.AuditShowcase",
            buildlog,auditlog,
        ),errors)
        if s:
            vfx=s.find("ProductionArtVfxBuilder.BuildAll")
            scene=s.find("ProductionArtVfxShowcaseBuilder.BuildShowcase")
            audit=s.find("ProductionArtVfxShowcaseAudit.AuditShowcase")
            ui=s.find("ProductionArtDiegeticUiBuilder.BuildAll")
            if min(vfx,scene,audit,ui)<0 or not (vfx < scene < audit < ui):
                errors.append(f"{label} order must be VFX build -> VFX showcase -> VFX audit -> diegetic UI")

    print("Project ØEN isolated VFX showcase QA")
    print("  particle systems : 7")
    print("  billboards       : 6")
    print("  wet sheen helper : 1 material review")
    print("  max particles    : <=28/system")
    print("  lights/colliders : 0")
    print("  Android build    : excluded")
    if errors:
        print(f"\nFAILED with {len(errors)} issue(s):")
        for e in errors: print(" - "+e)
        return 1
    print("\nPASS: isolated VFX review/audit contract is intact.")
    return 0

if __name__=="__main__": sys.exit(main())
