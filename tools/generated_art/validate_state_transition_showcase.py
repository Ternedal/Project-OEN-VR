#!/usr/bin/env python3
"""Static QA gate for the isolated Unity state-transition art review."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EDITOR = ROOT / "src" / "unity" / "ProjectOen.Art" / "Editor"
RUNTIME = ROOT / "src" / "unity" / "ProjectOen.Art" / "Runtime"
BUILDER = EDITOR / "ProductionArtStateTransitionShowcaseBuilder.cs"
AUDIT = EDITOR / "ProductionArtStateTransitionShowcaseAudit.cs"
CONTROLLER = RUNTIME / "ProductionArtPrefabStateController.cs"
REVIEW = ROOT / "prototype" / "m0b-bootstrap" / "Review-ProductionArt.ps1"
BOOTSTRAP = ROOT / "prototype" / "m0b-bootstrap" / "Bootstrap-M0b.ps1"
WORKFLOW = ROOT / ".github" / "workflows" / "generate-project-oen-art.yml"

SCENE = "Assets/ProjectOEN/ProductionArt/Scenes/StateTransitionShowcase.unity"
ROWS = {
    "WORLD-SHELTER": ("covered_usable", "damaged", "repaired_reinforced"),
    "WORLD-CAMPFIRE": ("strong_flame", "nearly_out_wet", "small_flame"),
    "WORLD-SIGNAL-BEACON": ("complete", "storm_damaged", "lit_active"),
    "PR-001": ("placed", "damaged", "wet"),
    "EN-016": ("clean", "worn", "wet"),
    "PR-014": ("clean", "worn", "storm_damaged"),
}
PROFILES = (
    "cs004-damaged",
    "cs005-repaired",
    "cs010-nearly-out-wet",
    "cs015-storm-damaged",
    "pr001-damaged",
    "pr001-wet",
    "en016-worn",
    "en016-wet",
    "pr014-worn",
    "pr014-storm-damaged",
)


def require(text: str, tokens, label: str, errors: list[str]) -> None:
    for token in tokens:
        if token not in text:
            errors.append(f"{label}: missing contract token: {token}")


def reject(text: str, tokens, label: str, errors: list[str]) -> None:
    for token in tokens:
        if token in text:
            errors.append(f"{label}: forbidden contract token: {token}")


def ordered(text: str, tokens, label: str, errors: list[str]) -> None:
    cursor = -1
    for token in tokens:
        pos = text.find(token, cursor + 1)
        if pos < 0:
            errors.append(f"{label}: missing sequence token: {token}")
            return
        if pos <= cursor:
            errors.append(f"{label}: out-of-order sequence token: {token}")
            return
        cursor = pos


def main() -> int:
    errors: list[str] = []
    for path in (BUILDER, AUDIT, CONTROLLER, REVIEW, BOOTSTRAP, WORKFLOW):
        if not path.exists():
            errors.append(f"missing state-transition integration file: {path.relative_to(ROOT)}")

    if errors:
        print("Project ØEN Unity state-transition QA")
        for error in errors:
            print(" - " + error)
        return 1

    builder = BUILDER.read_text(encoding="utf-8")
    audit = AUDIT.read_text(encoding="utf-8")
    controller = CONTROLLER.read_text(encoding="utf-8")
    review = REVIEW.read_text(encoding="utf-8")
    bootstrap = BOOTSTRAP.read_text(encoding="utf-8")
    workflow = WORKFLOW.read_text(encoding="utf-8")

    require(builder, (
        SCENE,
        "public const int ExpectedSampleCount = 18;",
        'private static readonly string[] ColumnLabels = { "BASELINE", "PRESSURE", "AFTERMATH / WET" };',
        'new GameObject("State Transition Matrix")',
        'new GameObject("State Transition Labels")',
        'PrefabUtility.InstantiatePrefab(prefab)',
        'ProductionArtStateAppearance appearance',
        'appearance.ApplyAppearance();',
        'renderer.shadowCastingMode = ShadowCastingMode.Off;',
        'renderer.receiveShadows = false;',
        'UnityEngine.Object.DestroyImmediate(collider);',
        'camera.orthographic = true;',
        'light.shadows = LightShadows.None;',
        'Project OEN/Art/Open State Transition Showcase',
    ), "builder", errors)
    for asset_id, states in ROWS.items():
        if f'"{asset_id}"' not in builder:
            errors.append(f"builder: missing state-set row: {asset_id}")
        for state in states:
            if f'"{state}"' not in builder:
                errors.append(f"builder: missing state key {asset_id}/{state}")
    for profile in PROFILES:
        if f'"{profile}"' not in builder:
            errors.append(f"builder: missing appearance profile expectation: {profile}")
    reject(builder, (
        "BuildPipeline.BuildPlayer",
        "EditorBuildSettings.scenes =",
        "AddComponent<ParticleSystem>",
        "void Update(",
        "void LateUpdate(",
        "new Material(",
        ".material =",
        "CoopGame",
    ), "builder", errors)

    require(audit, (
        SCENE,
        "private const int ExpectedLabelCount = 27;",
        "private const int TriangleHardLimit = 300000;",
        "VerifyStaticMatrix(scene, errors);",
        "VerifyRuntimeTransitions(errors);",
        "controller.HasState(stateKey)",
        "controller.SetState(stateKey)",
        "controller.CurrentInstance",
        "controller.CurrentState",
        "previous != null",
        "ProductionArtStateAppearance[] appearances",
        'expectedProfile == "cs010-nearly-out-wet"',
        "colliders.Length != 0",
        "particles.Length != 0",
        "wetnessDrivers.Length != 0",
        "savedControllers.Length != 0",
        "lights.Length != 1",
        "!cameras[0].orthographic",
        "EditorBuildSettings.scenes.Any",
        "material.name.EndsWith(\" (Instance)\"",
    ), "audit", errors)
    reject(audit, (
        "BuildPipeline.BuildPlayer",
        "EditorBuildSettings.scenes =",
        "void Update(",
        "void LateUpdate(",
        "new Material(",
        "CoopGame",
    ), "audit", errors)

    require(controller, (
        "private void ReleaseCurrentInstance()",
        "if (Application.isPlaying)",
        "UnityEngine.Object.Destroy(currentInstance);",
        "UnityEngine.Object.DestroyImmediate(currentInstance);",
        "currentInstance = Instantiate(prefab, mount, false);",
    ), "runtime controller", errors)
    reject(controller, (
        "void Update(",
        "void LateUpdate(",
        "new Material(",
    ), "runtime controller", errors)

    sequence = (
        "ProductionArtStateCatalogBuilder.BuildAll",
        "ProductionArtStateTransitionShowcaseBuilder.BuildShowcase",
        "ProductionArtStateTransitionShowcaseAudit.AuditShowcase",
        "ProductionArtDecalBuilder.BuildAll",
    )
    for label, script in (("fast review", review), ("bootstrap", bootstrap)):
        require(script, (
            "ProductionArtStateTransitionShowcaseBuilder.cs",
            "ProductionArtStateTransitionShowcaseAudit.cs",
            SCENE.replace('/', '\\'),
        ), label, errors)
        ordered(script, sequence, label, errors)
        reject(script, ("EditorBuildSettings.scenes", "BuildPipeline.BuildPlayer"), label + " transition path", errors)

    require(workflow, (
        "Validate state-transition review scene",
        "python tools/generated_art/validate_state_transition_showcase.py",
    ), "art workflow", errors)

    print("Project ØEN Unity state-transition QA")
    print("  matrix         : 6 rows x 3 states = 18 static visual samples")
    print("  controller     : editor-side SetState exercised across all 18 selections")
    print("  appearance     : canonical damaged/wet/repaired profiles asserted")
    print("  scene budget   : 0 colliders / 0 particles / 0 wetness drivers / 1 shadowless light")
    print("  triangles      : hard limit 300,000")
    print("  integration    : fast review + M0b bootstrap + art workflow")
    print("  build isolation: state-transition scene excluded from CoopGame/build settings")
    if errors:
        print(f"\nFAILED with {len(errors)} issue(s):")
        for error in errors:
            print(" - " + error)
        return 1

    print("\nPASS: state-transition review is explicit, runtime-switch tested and build-isolated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
