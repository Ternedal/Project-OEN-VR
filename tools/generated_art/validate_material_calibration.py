#!/usr/bin/env python3
"""Static QA gate for the isolated dry/mid/storm Unity material calibration review."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EDITOR = ROOT / "src" / "unity" / "ProjectOen.Art" / "Editor"
BUILDER = EDITOR / "ProductionArtMaterialCalibrationBuilder.cs"
AUDIT = EDITOR / "ProductionArtMaterialCalibrationAudit.cs"
MENU = EDITOR / "ProductionArtReviewMenu.cs"
REVIEW = ROOT / "prototype" / "m0b-bootstrap" / "Review-ProductionArt.ps1"
BOOTSTRAP = ROOT / "prototype" / "m0b-bootstrap" / "Bootstrap-M0b.ps1"

SCENE = "Assets/ProjectOEN/ProductionArt/Scenes/MaterialCalibrationShowcase.unity"
MATERIALS = ("Wood", "Rope", "Tarp", "Metal", "Stone", "Leaf", "Cloth", "Mud", "Fire", "Char", "Water")


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
    paths = (BUILDER, AUDIT, MENU, REVIEW, BOOTSTRAP)
    for path in paths:
        if not path.exists():
            errors.append(f"missing material-calibration integration file: {path.relative_to(ROOT)}")

    if errors:
        print("Project ØEN Unity material calibration QA")
        for error in errors:
            print(" - " + error)
        return 1

    builder = BUILDER.read_text(encoding="utf-8")
    audit = AUDIT.read_text(encoding="utf-8")
    menu = MENU.read_text(encoding="utf-8")
    review = REVIEW.read_text(encoding="utf-8")
    bootstrap = BOOTSTRAP.read_text(encoding="utf-8")

    require(builder, (
        SCENE,
        'private const string MaterialRoot = "Assets/ProjectOEN/ProductionArt/UnityMaterials";',
        'private static readonly float[] ColumnWetness = { 0.00f, 0.40f, 0.78f };',
        'GameObject.CreatePrimitive(PrimitiveType.Sphere)',
        'renderer.sharedMaterial = materials[materialIndex];',
        'renderer.shadowCastingMode = ShadowCastingMode.Off;',
        'renderer.receiveShadows = false;',
        'root.SetActive(false);',
        'SerializedProperty scope = serialized.FindProperty("scopeRoot");',
        'scope.objectReferenceValue = root.transform;',
        'driver.SetWetness(wetness);',
        'driver.ApplyWetness();',
        'light.shadows = LightShadows.None;',
        'camera.orthographic = true;',
        'Collider collider = sample.GetComponent<Collider>();',
        'UnityEngine.Object.DestroyImmediate(collider);',
        'new GameObject("Calibration Labels")',
    ), "builder", errors)
    for material in MATERIALS:
        if f'"{material}"' not in builder:
            errors.append(f"builder: shared material family missing: {material}")
    reject(builder, (
        'BuildPipeline.BuildPlayer',
        'EditorBuildSettings.scenes =',
        'AddComponent<ParticleSystem>',
        'void Update(',
        'void LateUpdate(',
        'renderer.material =',
        'new Material(',
    ), "builder", errors)

    require(audit, (
        SCENE,
        'private const int ExpectedSampleCount = 33;',
        'private const int ExpectedWettableCountPerColumn = 9;',
        'private static readonly float[] ExpectedWetness = { 0.00f, 0.40f, 0.78f };',
        'drivers.Length != ExpectedWetness.Length',
        'sampleRenderers.Length != ExpectedSampleCount',
        'colliders.Length != 0',
        'particles.Length != 0',
        'lights.Length != 1',
        'lights[0].shadows != LightShadows.None',
        '!cameras[0].orthographic',
        'labelRoot.transform.childCount != 14',
        'EditorBuildSettings.scenes.Any',
        'scopeRoot != driver.transform',
        'driver.LastAffectedRendererCount != ExpectedWettableCountPerColumn',
        'renderer.sharedMaterial != expectedMaterial',
        'materialName != "Fire" && materialName != "Water"',
        'shouldBeWettable && propertyBlock.isEmpty',
        '!shouldBeWettable && !propertyBlock.isEmpty',
    ), "audit", errors)
    reject(audit, (
        'BuildPipeline.BuildPlayer',
        'EditorBuildSettings.scenes =',
        'void Update(',
        'void LateUpdate(',
    ), "audit", errors)

    require(menu, (
        SCENE,
        'Project OEN/Art/Open Material Calibration Showcase',
        'OpenMaterialCalibrationShowcase()',
    ), "review menu", errors)

    sequence = (
        'ProductionArtPrefabBuilder.BuildAll',
        'ProductionArtMaterialCalibrationBuilder.BuildShowcase',
        'ProductionArtMaterialCalibrationAudit.AuditShowcase',
        'ProductionArtStateCatalogBuilder.BuildAll',
    )
    for label, script in (("fast review", review), ("bootstrap", bootstrap)):
        require(script, (
            'ProductionArtMaterialCalibrationBuilder.cs',
            'ProductionArtMaterialCalibrationAudit.cs',
            SCENE.replace('/', '\\'),
        ), label, errors)
        ordered(script, sequence, label, errors)
        reject(script, ('EditorBuildSettings.scenes', 'BuildPipeline.BuildPlayer'), label + " calibration path", errors)

    print("Project ØEN Unity material calibration QA")
    print(f"  materials      : {len(MATERIALS)} shared production families")
    print("  columns        : dry 0.00 / mid 0.40 / storm 0.78")
    print("  samples        : 33 identical spheres")
    print("  wettable       : 9 families per scoped column; Fire + Water excluded")
    print("  scene budget   : 0 colliders / 0 particles / 1 shadowless light / orthographic camera")
    print("  integration    : fast review + M0b bootstrap + review menu")
    print("  build isolation: calibration scene excluded from build settings")
    if errors:
        print(f"\nFAILED with {len(errors)} issue(s):")
        for error in errors:
            print(" - " + error)
        return 1

    print("\nPASS: isolated dry/mid/storm material-calibration contract is wired and bounded.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
