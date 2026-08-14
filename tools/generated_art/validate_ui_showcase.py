#!/usr/bin/env python3
"""Static contract for Project ØEN diegetic-UI physical-scale review scene/audit."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EDITOR = ROOT / "src" / "unity" / "ProjectOen.Art" / "Editor"
BUILDER = EDITOR / "ProductionArtUiShowcaseBuilder.cs"
AUDIT = EDITOR / "ProductionArtUiShowcaseAudit.cs"
BOOT = ROOT / "prototype" / "m0b-bootstrap" / "Bootstrap-M0b.ps1"
REVIEW = ROOT / "prototype" / "m0b-bootstrap" / "Review-ProductionArt.ps1"


def need(path, tokens, errors):
    if not path.exists():
        errors.append(f"missing: {path.relative_to(ROOT)}")
        return ""
    text = path.read_text(encoding="utf-8")
    for token in tokens:
        if token not in text:
            errors.append(f"{path.name} missing: {token}")
    return text


def main():
    errors=[]
    b=need(BUILDER, (
        "DiegeticUiArtShowcase.unity",
        "WristStatus_Diegetic.prefab",
        "PlanningBoard_Diegetic.prefab",
        "InteractionMarkers_Diegetic.prefab",
        "MetaStatus_Diegetic.prefab",
        "1m Scale Reference",
        "DestroyImmediate(collider)",
        "ProductionArtUiShowcaseBuilder",
    ), errors)
    a=need(AUDIT, (
        "DiegeticUiArtShowcase.unity",
        "MinSpriteRenderers = 22",
        "MaxSpriteRenderers = 32",
        "MaxColliders = 1",
        "Wrist Status - physical scale",
        "Planning Board - physical scale",
        "Interaction Markers - physical scale",
        "Meta Status - physical scale",
        "0.15f, 0.50f",
        "0.60f, 1.20f",
        "0.40f, 0.90f",
        "0.30f, 0.80f",
        "EditorBuildSettings.scenes",
        "shadowCastingMode != ShadowCastingMode.Off",
        "GetComponents<Light>()",
        "GetComponents<ParticleSystem>()",
    ), errors)
    boot=need(BOOT, (
        "ProductionArtUiShowcaseBuilder.cs",
        "ProductionArtUiShowcaseAudit.cs",
        "ProductionArtUiShowcaseBuilder.BuildShowcase",
        "ProductionArtUiShowcaseAudit.AuditShowcase",
    ), errors)
    review=need(REVIEW, (
        "ProductionArtUiShowcaseBuilder.cs",
        "ProductionArtUiShowcaseAudit.cs",
        "ProductionArtUiShowcaseBuilder.BuildShowcase",
        "ProductionArtUiShowcaseAudit.AuditShowcase",
    ), errors)

    for label,text in (("builder",b),("audit",a)):
        for forbidden in ("BuildPipeline.BuildPlayer", "CoopGame.unity", "M0bConfigure.Configure"):
            if forbidden in text:
                errors.append(f"UI showcase {label} must not touch M0b/build path: {forbidden}")

    for label,text in (("bootstrap",boot),("review",review)):
        ui_prefab=text.find("ProductionArtDiegeticUiBuilder.BuildAll")
        ui_scene=text.find("ProductionArtUiShowcaseBuilder.BuildShowcase")
        ui_audit=text.find("ProductionArtUiShowcaseAudit.AuditShowcase")
        storm_scene=text.find("ProductionArtShowcaseBuilder.BuildShowcase")
        if min(ui_prefab,ui_scene,ui_audit,storm_scene) < 0 or not (ui_prefab < ui_scene < ui_audit < storm_scene):
            errors.append(f"{label} order must be diegetic UI -> UI showcase -> UI audit -> Stormnatten showcase")

    print("Project ØEN diegetic UI physical-scale showcase QA")
    print("  scene          : DiegeticUiArtShowcase.unity")
    print("  sprite renderers: 22..32")
    print("  colliders       : <=1")
    print("  lights/particles: 0")
    print("  build settings  : excluded")
    if errors:
        print(f"\nFAILED with {len(errors)} issue(s):")
        for e in errors: print(" - "+e)
        return 1
    print("\nPASS: repo-side physical-scale UI showcase/audit contract is intact.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
