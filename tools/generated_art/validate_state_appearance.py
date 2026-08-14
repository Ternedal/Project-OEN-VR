#!/usr/bin/env python3
"""Static QA gate for canonical damaged/wet production-art state appearance."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT / "src" / "unity" / "ProjectOen.Art" / "Runtime"
EDITOR = ROOT / "src" / "unity" / "ProjectOen.Art" / "Editor"
APPEARANCE = RUNTIME / "ProductionArtStateAppearance.cs"
WETNESS = RUNTIME / "ProductionArtWetnessDriver.cs"
BUILDER = EDITOR / "ProductionArtStateAppearanceBuilder.cs"
AUDIT = EDITOR / "ProductionArtStateAppearanceAudit.cs"
SHOWCASE = EDITOR / "ProductionArtShowcaseBuilder.cs"
REVIEW = ROOT / "prototype" / "m0b-bootstrap" / "Review-ProductionArt.ps1"
BOOTSTRAP = ROOT / "prototype" / "m0b-bootstrap" / "Bootstrap-M0b.ps1"

TARGETS = (
    ("PR-001", "damaged", "pr001-damaged"),
    ("PR-001", "wet", "pr001-wet"),
    ("CS-004", None, "cs004-damaged"),
    ("CS-005", None, "cs005-repaired"),
    ("CS-010", None, "cs010-nearly-out-wet"),
    ("CS-015", None, "cs015-storm-damaged"),
    ("EN-016", "worn", "en016-worn"),
    ("EN-016", "wet", "en016-wet"),
    ("PR-014", "worn", "pr014-worn"),
    ("PR-014", "storm-damaged", "pr014-storm-damaged"),
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
    paths = (APPEARANCE, WETNESS, BUILDER, AUDIT, SHOWCASE, REVIEW, BOOTSTRAP)
    for path in paths:
        if not path.exists():
            errors.append(f"missing state-appearance integration file: {path.relative_to(ROOT)}")

    if errors:
        print("Project ØEN state-specific storm appearance QA")
        for error in errors:
            print(" - " + error)
        return 1

    appearance = APPEARANCE.read_text(encoding="utf-8")
    wetness = WETNESS.read_text(encoding="utf-8")
    builder = BUILDER.read_text(encoding="utf-8")
    audit = AUDIT.read_text(encoding="utf-8")
    showcase = SHOWCASE.read_text(encoding="utf-8")
    review = REVIEW.read_text(encoding="utf-8")
    bootstrap = BOOTSTRAP.read_text(encoding="utf-8")

    require(appearance, (
        "public sealed class ProductionArtStateAppearance",
        "MaterialPropertyBlock",
        "public Color TintMultiplier",
        "public float NormalScaleMultiplier",
        "public float EmissionScale",
        "ApplyAppearance()",
        "RefreshWetnessDrivers()",
        'materialName != "Fire" && materialName != "Water"',
        'materialName == "Fire"',
        "authoredEmission * emissionScale",
        "driver.ApplyWetness();",
    ), "runtime appearance", errors)
    reject(appearance, (
        "void Update(",
        "void LateUpdate(",
        "new Material(",
        ".material =",
        "AddComponent<ParticleSystem>",
        "AddComponent<Light>",
    ), "runtime appearance", errors)

    require(wetness, (
        "renderer.GetComponentInParent<ProductionArtStateAppearance>()",
        "stateAppearance.TintMultiplier",
        "stateAppearance.NormalScaleMultiplier",
        "Color tint = Multiply(stateTint, wetTint);",
        "stateBumpScale * wetBumpScale",
    ), "global wetness composition", errors)
    reject(wetness, ("void Update(", "void LateUpdate(", "new Material("), "global wetness composition", errors)

    require(builder, (
        "ProductionArtStateAppearanceBuilder",
        "PrefabUtility.LoadPrefabContents",
        "PrefabUtility.SaveAsPrefabAsset",
        "root.AddComponent<ProductionArtStateAppearance>()",
        "appearance.Configure(spec.profileKey, spec.tint, spec.normalScale, spec.emissionScale);",
        'new ProfileSpec("CS-010", null, "cs010-nearly-out-wet"',
        "0.22f",
    ), "builder", errors)
    for asset_id, variant, key in TARGETS:
        if f'"{asset_id}"' not in builder:
            errors.append(f"builder: canonical target missing: {asset_id}")
        if variant is not None and f'"{variant}"' not in builder:
            errors.append(f"builder: canonical variant missing: {asset_id}/{variant}")
        if f'"{key}"' not in builder:
            errors.append(f"builder: profile key missing: {key}")
    reject(builder, (
        "BuildPipeline.BuildPlayer",
        "EditorBuildSettings.scenes =",
        "new Material(",
        ".material =",
        "void Update(",
        "void LateUpdate(",
    ), "builder", errors)

    require(audit, (
        "ProductionArtStateAppearanceBuilder.Profiles",
        "profiles.Length != 1",
        "appearance.gameObject != prefab",
        "Approximately(appearance.TintMultiplier, spec.tint)",
        "appearance.NormalScaleMultiplier - spec.normalScale",
        "appearance.EmissionScale - spec.emissionScale",
        "Unexpected state-appearance profile outside canonical target set",
        "totalProfiles != ProductionArtStateAppearanceBuilder.Profiles.Length",
    ), "audit", errors)
    reject(audit, ("BuildPipeline.BuildPlayer", "void Update(", "void LateUpdate("), "audit", errors)

    require(showcase, (
        '"Storm-Damaged Shelter"',
        '"Campfire Nearly Out Wet"',
        '"Wet Tarp"',
        '"Wet Camp Groundsheet"',
        '"Signal Beacon Storm Damaged"',
        '"Signal Cloth"',
    ), "Stormnatten showcase", errors)

    sequence = (
        "ProductionArtPrefabBuilder.BuildAll",
        "ProductionArtStateAppearanceBuilder.BuildAll",
        "ProductionArtStateAppearanceAudit.AuditAll",
        "ProductionArtMaterialCalibrationBuilder.BuildShowcase",
        "ProductionArtStateCatalogBuilder.BuildAll",
    )
    for label, script in (("fast review", review), ("bootstrap", bootstrap)):
        require(script, (
            "ProductionArtStateAppearanceBuilder.cs",
            "ProductionArtStateAppearanceAudit.cs",
        ), label, errors)
        ordered(script, sequence, label, errors)

    print("Project ØEN state-specific storm appearance QA")
    print(f"  canonical profiles : {len(TARGETS)}")
    print("  state set           : tarp damaged/wet; shelter damaged/repaired; campfire wet; beacon damaged; groundsheet worn/wet; signal cloth worn/damaged")
    print("  runtime             : event-driven MaterialPropertyBlock composition, no per-frame loop")
    print("  fire                : CS-010 emission scale 0.22; Fire/Water excluded from global wet tint")
    print("  integration         : fast review + M0b bootstrap before material calibration/state catalogs")
    if errors:
        print(f"\nFAILED with {len(errors)} issue(s):")
        for error in errors:
            print(" - " + error)
        return 1

    print("\nPASS: canonical state-specific storm appearance is explicit, bounded and composed with global wetness.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
