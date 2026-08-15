#!/usr/bin/env python3
"""Static repo contract for lightweight Project ØEN diegetic VR UI prefabs."""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BUILDER = ROOT / "src" / "unity" / "ProjectOen.Art" / "Editor" / "ProductionArtDiegeticUiBuilder.cs"
BOOTSTRAP = ROOT / "prototype" / "m0b-bootstrap" / "Bootstrap-M0b.ps1"
REVIEW = ROOT / "prototype" / "m0b-bootstrap" / "Review-ProductionArt.ps1"

REQUIRED_BUILDER = (
    'SpriteRoot = "Assets/ProductionArt/Sprites"',
    'OutputRoot = "Assets/ProductionArt/UiPrefabs"',
    'BuildWristStatus();',
    'BuildPlanningBoard();',
    'BuildInteractionMarkerSet();',
    'BuildMetaStatusPanel();',
    'WristStatus_Diegetic.prefab',
    'PlanningBoard_Diegetic.prefab',
    'InteractionMarkers_Diegetic.prefab',
    'MetaStatus_Diegetic.prefab',
    '"ui-002_"', '"ui-003_"', '"ui-004_"', '"ui-005_"',
    '"ui-012_"', '"ui-013_"', '"ui-014_"',
    '"pl-003_"', '"pl-004_"', '"pl-005_"', '"pl-006_"',
    '"wk-001_"', '"wk-002_"', '"wk-003_"', '"wk-005_"',
    '"wk-010_"', '"wk-011_"', '"wk-013_"',
    'SpriteRenderer',
    'renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off',
    'renderer.receiveShadows = false',
    'targetWidthMeters',
)

FORBIDDEN_BUILDER = (
    'using UnityEngine.UI', 'UnityEngine.UI.', 'AddComponent<Canvas>',
    'AddComponent<CanvasScaler>', 'AddComponent<GraphicRaycaster>',
    'TextMeshPro', 'TMPro.', 'BuildPipeline.BuildPlayer',
    'EditorBuildSettings.scenes', 'Hunger', 'Thirst', 'Malik', 'Lighthouse',
)


def require(path: Path, label: str, tokens, errors):
    if not path.exists():
        errors.append(f"Missing {label}: {path.relative_to(ROOT)}")
        return ""
    text = path.read_text(encoding="utf-8")
    for token in tokens:
        if token not in text:
            errors.append(f"{label} missing contract token: {token}")
    return text


def main() -> int:
    errors=[]
    builder=require(BUILDER,"diegetic UI builder",REQUIRED_BUILDER,errors)
    if builder:
        for token in FORBIDDEN_BUILDER:
            if token in builder:
                errors.append(f"diegetic UI builder must not depend on/contain: {token}")
        if builder.count("SavePrefab(root, OutputRoot +") != 4:
            errors.append("diegetic UI builder must save exactly four top-level visual prefabs")
        if builder.count("AddComponent<BoxCollider>") > 1:
            errors.append("diegetic UI art layer should only add the planning-board bounds collider")

    bootstrap=require(BOOTSTRAP,"M0b bootstrap",(
        "ProductionArtDiegeticUiBuilder.cs",
        "ProjectOen.Art.Editor.ProductionArtDiegeticUiBuilder.BuildAll",
        "production-art-diegetic-ui.log",
        "ProductionArtUiShowcaseBuilder.BuildShowcase",
        "ProductionArtUiShowcaseAudit.AuditShowcase",
    ),errors)
    review=require(REVIEW,"fast art review",(
        "ProductionArtDiegeticUiBuilder.cs",
        "ProjectOen.Art.Editor.ProductionArtDiegeticUiBuilder.BuildAll",
        "review-art-diegetic-ui.log",
        "UI prefabs: Assets\\ProductionArt\\UiPrefabs",
        "ProductionArtUiShowcaseBuilder.BuildShowcase",
        "ProductionArtUiShowcaseAudit.AuditShowcase",
    ),errors)

    for label,text in (("M0b bootstrap",bootstrap),("Fast review",review)):
        if text:
            prefab_pos=text.find("ProductionArtPrefabBuilder.BuildAll")
            ui_pos=text.find("ProductionArtDiegeticUiBuilder.BuildAll")
            ui_scene_pos=text.find("ProductionArtUiShowcaseBuilder.BuildShowcase")
            storm_pos=text.find("ProductionArtShowcaseBuilder.BuildShowcase")
            if min(prefab_pos,ui_pos,ui_scene_pos,storm_pos) < 0 or not (prefab_pos < ui_pos < ui_scene_pos < storm_pos):
                errors.append(f"{label} must build world prefabs -> diegetic UI -> UI review -> Stormnatten showcase")

    if review:
        for forbidden in ("M0bConfigure.Configure", "BuildPipeline.BuildPlayer", "Packages\\manifest.json"):
            if forbidden in review:
                errors.append(f"Fast art review must not mutate M0b platform path: {forbidden}")

    print("Project ØEN diegetic VR UI builder QA")
    print("  visual prefabs : 4")
    print("  renderer path  : SpriteRenderer (no Canvas/TMP dependency)")
    print("  canonical UI   : Health / Fatigue / Injury / Cold-Wet + camp states")
    print("  build order    : world -> diegetic UI -> physical-scale audit -> Stormnatten")
    print("  Quest intent   : no UI shadows; one board collider only")
    if errors:
        print(f"\nFAILED with {len(errors)} issue(s):")
        for error in errors: print(" - "+error)
        return 1
    print("\nPASS: diegetic UI art-prefab integration contract is intact.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
