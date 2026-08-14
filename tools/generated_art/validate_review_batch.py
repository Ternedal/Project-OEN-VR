#!/usr/bin/env python3
"""Static contract for the one-shot on-machine Unity production-art verification path."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BATCH = ROOT / "src/unity/ProjectOen.Art/Editor/ProductionArtBatchVerification.cs"
REVIEW = ROOT / "prototype/m0b-bootstrap/Review-ProductionArt.ps1"
RUNBOOK = ROOT / "prototype/m0b-bootstrap/RUNBOOK.md"
WORKFLOW = ROOT / ".github/workflows/generate-project-oen-art.yml"

ORDERED_METHODS = (
    "ProductionArtPrefabBuilder.BuildAll",
    "ProductionArtStateAppearanceBuilder.BuildAll",
    "ProductionArtStateAppearanceAudit.AuditAll",
    "ProductionArtMaterialCalibrationBuilder.BuildShowcase",
    "ProductionArtMaterialCalibrationAudit.AuditShowcase",
    "ProductionArtStateCatalogBuilder.BuildAll",
    "ProductionArtStateTransitionShowcaseBuilder.BuildShowcase",
    "ProductionArtStateTransitionShowcaseAudit.AuditShowcase",
    "ProductionArtHeroReadabilityShowcaseBuilder.BuildShowcase",
    "ProductionArtHeroReadabilityShowcaseAudit.AuditShowcase",
    "ProductionArtDecalBuilder.BuildAll",
    "ProductionArtVfxBuilder.BuildAll",
    "ProductionArtVfxShowcaseBuilder.BuildShowcase",
    "ProductionArtVfxShowcaseAudit.AuditShowcase",
    "ProductionArtDiegeticUiBuilder.BuildAll",
    "ProductionArtUiShowcaseBuilder.BuildShowcase",
    "ProductionArtUiShowcaseAudit.AuditShowcase",
    "ProductionArtShowcaseBuilder.BuildShowcase",
    "ProductionArtStormAtmosphereBuilder.AddStormAtmosphere",
    "ProductionArtStormFxBuilder.AddStormMotionFx",
    "ProductionArtWindResponseBuilder.AddWindResponse",
    "ProductionArtShowcaseAudit.AuditShowcase",
    "VerifyReviewSceneInventory",
)

SCENES = (
    "ProductionVfxShowcase.unity",
    "DiegeticUiArtShowcase.unity",
    "MaterialCalibrationShowcase.unity",
    "StateTransitionShowcase.unity",
    "HeroReadabilityShowcase.unity",
    "StormnattenArtShowcase.unity",
)

BATCH_REQUIRED = (
    'public static class ProductionArtBatchVerification',
    'public const string ReportFileName = "ProjectOEN-ArtVerification.json"',
    'public static void RunAll()',
    'AssetDatabase.SaveAssets();',
    'AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);',
    'EditorBuildSettings.scenes',
    'AssetDatabase.LoadAssetAtPath<SceneAsset>(scenePath)',
    'Visual-review scene leaked into enabled build settings',
    'JsonUtility.ToJson(report, true)',
    'File.WriteAllText(path',
    'report.status = "PASS"',
    'report.status = "FAIL"',
    '[ProjectOEN.Art.Batch] PASS',
    '[ProjectOEN.Art.Batch] FAIL',
)

REVIEW_REQUIRED = (
    '[switch]$OneShot',
    '"ProductionArtBatchVerification.cs"',
    'if ($OneShot)',
    'ProjectOen.Art.Editor.ProductionArtBatchVerification.RunAll',
    'ProjectOEN-ArtVerification.json',
    'review-art-verification.json',
    'review-art-one-shot.log',
    'ConvertFrom-Json',
    '$report.status -ne "PASS"',
    '[int]$report.failed -ne 0',
)

WORKFLOW_REQUIRED = (
    '- name: Validate one-shot Unity production-art verification',
    'run: python tools/generated_art/validate_review_batch.py',
)


def read(path: Path, label: str, errors: list[str]) -> str:
    if not path.exists():
        errors.append(f"missing {label}: {path.relative_to(ROOT)}")
        return ""
    return path.read_text(encoding="utf-8")


def require(text: str, tokens: tuple[str, ...], label: str, errors: list[str]) -> None:
    for token in tokens:
        if token not in text:
            errors.append(f"{label} missing contract token: {token}")


def main() -> int:
    errors: list[str] = []
    batch = read(BATCH, "Unity batch runner", errors)
    review = read(REVIEW, "review PowerShell", errors)
    runbook = read(RUNBOOK, "M0b runbook", errors)
    workflow = read(WORKFLOW, "art workflow", errors)

    require(batch, BATCH_REQUIRED, "batch runner", errors)
    require(review, REVIEW_REQUIRED, "review script", errors)
    require(workflow, WORKFLOW_REQUIRED, "art workflow", errors)

    for scene in SCENES:
        if scene not in batch:
            errors.append(f"batch runner missing review-scene inventory entry: {scene}")

    cursor = -1
    for method in ORDERED_METHODS:
        position = batch.find(method, cursor + 1)
        if position < 0:
            errors.append(f"batch runner missing ordered method: {method}")
            continue
        if position <= cursor:
            errors.append(f"batch runner method order drifted at: {method}")
        cursor = position

    run_step_count = len(re.findall(r'RunStep\("\d{2} ', batch))
    if run_step_count != 23:
        errors.append(f"batch runner must contain exactly 23 numbered RunStep calls; found {run_step_count}")

    for forbidden in (
        "BuildPipeline.BuildPlayer",
        "EditorApplication.Exit",
        "Application.Quit",
        "Thread.Sleep",
        "void Update(",
        "void LateUpdate(",
    ):
        if forbidden in batch:
            errors.append(f"batch runner must remain review-only/event-driven; forbidden token: {forbidden}")

    one_shot = review.find("if ($OneShot)")
    fallback = review.find('Run-UnityArtStep "Bygger production-art prefabs"')
    if one_shot < 0 or fallback < 0 or one_shot >= fallback:
        errors.append("one-shot branch must execute before the established per-step fallback")
    if review.count('"ProductionArtBatchVerification.cs"') != 1:
        errors.append("review script must copy ProductionArtBatchVerification.cs exactly once")

    if "-OneShot" not in runbook:
        errors.append("runbook must document -OneShot")
    if "review-art-verification.json" not in runbook:
        errors.append("runbook must document review-art-verification.json")
    if "debug" not in runbook.lower() or "fallback" not in runbook.lower():
        errors.append("runbook must retain the old mode as a debug fallback")

    print("Project ØEN one-shot Unity production-art verification QA")
    print("  Unity process : 1 batchmode editor process")
    print("  ordered steps : 23 build/audit/inventory steps")
    print("  review scenes : 6 required and build-isolated")
    print("  report        : ProjectOEN-ArtVerification.json -> review-art-verification.json")
    print("  fallback      : established per-step Unity mode retained")

    if errors:
        print(f"\nFAILED with {len(errors)} issue(s):")
        for error in errors:
            print(" - " + error)
        return 1

    print("\nPASS: one-shot on-machine verification path is explicit, ordered, reportable and build-isolated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
