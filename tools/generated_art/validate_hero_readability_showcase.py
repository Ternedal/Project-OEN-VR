#!/usr/bin/env python3
"""Static CI contract for the isolated physical-scale hero-readability review scene."""
from __future__ import annotations
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EDITOR = ROOT / "src" / "unity" / "ProjectOen.Art" / "Editor"
BUILDER = EDITOR / "ProductionArtHeroReadabilityShowcaseBuilder.cs"
AUDIT = EDITOR / "ProductionArtHeroReadabilityShowcaseAudit.cs"
MENU = EDITOR / "ProductionArtReviewMenu.cs"
REVIEW = ROOT / "prototype" / "m0b-bootstrap" / "Review-ProductionArt.ps1"
BOOT = ROOT / "prototype" / "m0b-bootstrap" / "Bootstrap-M0b.ps1"
WORKFLOW = ROOT / ".github" / "workflows" / "generate-project-oen-art.yml"
COOP = ROOT / "src" / "unity" / "App" / "CoopGameSetup.cs"

SCENE = "Assets/ProjectOEN/ProductionArt/Scenes/HeroReadabilityShowcase.unity"
SAMPLES = (
    ("PR-002", "loose"),
    ("PR-005", "repaired"),
    ("PR-007", "full"),
    ("PR-008", "off"),
    ("PR-017", "clean"),
    ("PR-018", "clean"),
    ("PR-019", "inactive"),
    ("PR-004", "closed"),
    ("PR-020", "idle"),
    ("PR-001", "placed"),
    ("WORLD-SHELTER", "covered_usable"),
    ("WORLD-SIGNAL-BEACON", "complete"),
)


def read(path: Path, label: str, errors: list[str]) -> str:
    if not path.exists():
        errors.append(f"Missing {label}: {path.relative_to(ROOT)}")
        return ""
    return path.read_text(encoding="utf-8")


def need(text: str, label: str, tokens: tuple[str, ...], errors: list[str]) -> None:
    for token in tokens:
        if token not in text:
            errors.append(f"{label} missing contract token: {token}")


def main() -> int:
    errors: list[str] = []
    builder = read(BUILDER, "hero-readability builder", errors)
    audit = read(AUDIT, "hero-readability audit", errors)
    menu = read(MENU, "review menu", errors)
    review = read(REVIEW, "fast review", errors)
    boot = read(BOOT, "M0b bootstrap", errors)
    workflow = read(WORKFLOW, "art workflow", errors)
    coop = read(COOP, "CoopGame setup", errors)

    need(builder, "hero-readability builder", (
        SCENE,
        "ExpectedSampleCount = 12",
        "ProductionArtPrefabStateSet",
        "PrefabUtility.InstantiatePrefab",
        "instance.transform.localScale = Vector3.one",
        "AlignToGround(instance)",
        "CombinedRendererBounds",
        "Hero Readability Scale Reference",
        "PrimitiveType.Cube",
        "new Vector3(0.035f, 1.00f, 0.035f)",
        "LightShadows.None",
        "camera.orthographic = false",
        "camera.fieldOfView = 48f",
        "StripReviewOnlyCost",
        "DestroyImmediate(collider)",
        "ShadowCastingMode.Off",
    ), errors)
    if builder and builder.count("new HeroSpec(") != len(SAMPLES):
        errors.append(f"hero-readability builder must define exactly {len(SAMPLES)} HeroSpec rows")
    for asset_id, state in SAMPLES:
        if builder and (f'"{asset_id}"' not in builder or f'"{state}"' not in builder):
            errors.append(f"hero-readability builder missing canonical sample: {asset_id}/{state}")
    if builder:
        for forbidden in ("void Update(", "void LateUpdate(", "BuildPipeline.BuildPlayer", "EditorBuildSettings.scenes", "AddComponent<ParticleSystem>", "AddComponent<Animation>", "AddComponent<Animator>"):
            if forbidden in builder:
                errors.append(f"hero-readability builder violates isolated static-review contract: {forbidden}")

    need(audit, "hero-readability audit", (
        "ScenePath = ProductionArtHeroReadabilityShowcaseBuilder.ScenePath",
        "TriangleHardLimit = 250000",
        "RendererHardLimit = 90",
        "ExpectedSampleCount",
        "EditorBuildSettings.scenes",
        "SceneComponents<Collider>(scene).Length != 0",
        "SceneComponents<ParticleSystem>(scene).Length != 0",
        "SceneComponents<Animation>(scene).Length != 0",
        "SceneComponents<Animator>(scene).Length != 0",
        "SceneComponents<ProductionArtWetnessDriver>(scene).Length != 0",
        "SceneComponents<ProductionArtPrefabStateController>(scene).Length != 0",
        "cameras[0].orthographic",
        "Hero Readability Scale Reference",
        "renderer.bounds.size.y - 1f",
        "sample.transform.localScale",
        "Quaternion authoredRotation = sample.transform.localRotation",
        "sample.transform.localRotation = Quaternion.identity",
        "sample.transform.localRotation = authoredRotation",
        "spec.minDimension",
        "spec.maxDimension",
        "bounds.min.y",
        "mesh.triangles.LongLength / 3L",
        "scene excluded from build settings",
    ), errors)
    if audit and "EditorApplication.Exit(0)" in audit:
        errors.append("hero-readability audit must not force success")

    need(menu, "review menu", (
        SCENE,
        "Open Hero Readability Showcase",
        "OpenHeroReadabilityShowcase",
        "Open State Transition Showcase",
        "OpenStateTransitionShowcase",
    ), errors)

    for text, label in ((review, "fast review"), (boot, "M0b bootstrap")):
        need(text, label, (
            "ProductionArtHeroReadabilityShowcaseBuilder.cs",
            "ProductionArtHeroReadabilityShowcaseAudit.cs",
            "ProductionArtHeroReadabilityShowcaseBuilder.BuildShowcase",
            "ProductionArtHeroReadabilityShowcaseAudit.AuditShowcase",
            "HeroReadabilityShowcase.unity",
        ), errors)

    need(workflow, "art workflow", (
        "Validate hero prop physical-scale readability",
        "python tools/generated_art/validate_hero_readability_showcase.py",
    ), errors)

    if coop and any(token in coop for token in ("HeroReadabilityShowcase", "Hero Readability", "ProductionArtHeroReadabilityShowcaseBuilder")):
        errors.append("hero-readability visual-review content leaked into CoopGame M0b gate")

    print("Project ØEN hero-readability showcase QA")
    print(f"  canonical samples : {len(SAMPLES)}")
    print("  scale contract    : 1:1 root scale + 1 metre reference + renderer bounds")
    print("  review isolation  : 0 colliders/particles/animations/wetness, 0 realtime shadows")
    print("  build separation  : HeroReadabilityShowcase is visual review only")
    if errors:
        print(f"\nFAILED with {len(errors)} issue(s):")
        for error in errors:
            print(" - " + error)
        return 1
    print("\nPASS: hero prop/world-anchor physical-scale readability contract is intact.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
