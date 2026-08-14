#!/usr/bin/env python3
"""Static contract gate for the bounded Stormnatten signal-finale micro-story."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FINALE = ROOT / "src" / "unity" / "ProjectOen.Art" / "Editor" / "ProductionArtSignalFinaleStoryBuilder.cs"
ATMOSPHERE = ROOT / "src" / "unity" / "ProjectOen.Art" / "Editor" / "ProductionArtStormAtmosphereBuilder.cs"
SHOWCASE = ROOT / "src" / "unity" / "ProjectOen.Art" / "Editor" / "ProductionArtShowcaseBuilder.cs"
REVIEW = ROOT / "prototype" / "m0b-bootstrap" / "Review-ProductionArt.ps1"
BOOTSTRAP = ROOT / "prototype" / "m0b-bootstrap" / "Bootstrap-M0b.ps1"

FINALE_REQUIRED = (
    'ExpectedStoryObjectCount = 8',
    'TriangleHardLimit = 50000',
    'MaterialSlotHardLimit = 32',
    'MaxStoryRadius = 2.45f',
    '"Collapsed Beacon Crossbrace", "pr-003_", "damaged"',
    '"Loaded Beacon Guy Rope", "en-024_", "taut"',
    '"Failed Beacon Guy Rope", "en-024_", "slack"',
    '"Scattered Signal Fuel", "en-019_", "logs"',
    '"Washed-Out Signal Rope", "en-004_", "small"',
    '"Loose Beacon Anchor Stones", "pr-010_", "small"',
    '"Storm-Torn Signal Cloth Debris", "en-023_", "loose_cloth"',
    '"Signal Hill Puddle", "en-011_", "small"',
    'FindPrefabStrict(spec.prefix, spec.token)',
    'throw new InvalidOperationException("Canonical signal finale prefab missing:',
    'StripRuntimeOnlyCost(instance);',
    'Vector2.Distance(new Vector2(spec.position.x, spec.position.z), FinaleCenter)',
    'root.GetComponentsInChildren<Collider>(true).Length != 0',
    'root.GetComponentsInChildren<Rigidbody>(true).Length != 0',
    'root.GetComponentsInChildren<ParticleSystem>(true).Length != 0',
    'root.GetComponentsInChildren<Light>(true).Length != 0',
    'root.GetComponentsInChildren<Animation>(true).Length != 0',
    'PrefabUtility.GetPrefabAssetPathOfNearestInstanceRoot',
)
FINALE_FORBIDDEN = (
    'void Update(',
    'void LateUpdate(',
    'AddComponent<ParticleSystem>',
    'AddComponent<Light>',
    'AddComponent<Rigidbody>',
    'EditorBuildSettings.scenes',
    'BuildPipeline.BuildPlayer',
    'CoopGame',
    '?? candidates[0]',
)
SHOWCASE_REQUIRED = (
    '"cs-015_"',
    '"pr-014_", "storm_damaged"',
    '"en-019_", "logs"',
    '"en-019_", "ropes"',
    '"en-019_", "stones"',
)


def main() -> int:
    errors = []
    for path, label in (
        (FINALE, "signal finale story builder"),
        (ATMOSPHERE, "storm atmosphere builder"),
        (SHOWCASE, "showcase builder"),
        (REVIEW, "fast review entrypoint"),
        (BOOTSTRAP, "M0b bootstrap entrypoint"),
    ):
        if not path.exists():
            errors.append(f"missing {label}: {path.relative_to(ROOT)}")
    if errors:
        print("ERROR: " + "; ".join(errors))
        return 1

    finale = FINALE.read_text(encoding="utf-8")
    atmosphere = ATMOSPHERE.read_text(encoding="utf-8")
    showcase = SHOWCASE.read_text(encoding="utf-8")
    review = REVIEW.read_text(encoding="utf-8")
    bootstrap = BOOTSTRAP.read_text(encoding="utf-8")

    for token in FINALE_REQUIRED:
        if token not in finale:
            errors.append(f"missing signal finale story contract: {token}")
    for token in FINALE_FORBIDDEN:
        if token in finale:
            errors.append(f"forbidden signal finale runtime/build token: {token}")
    for token in SHOWCASE_REQUIRED:
        if token not in showcase:
            errors.append(f"base signal composition lost canonical token: {token}")

    if finale.count('new StorySpec(') != 8:
        errors.append(f"signal finale story must contain exactly 8 authored specs, found {finale.count('new StorySpec(')}")
    if 'StaticEditorFlags.OccluderStatic' in finale:
        errors.append("small finale story props must not become occluder-static")

    camp_call = 'ProductionArtStormCampStoryBuilder.BuildIntoShowcase();'
    finale_call = 'ProductionArtSignalFinaleStoryBuilder.BuildIntoShowcase();'
    open_scene = 'var scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);'
    for token in (camp_call, finale_call, open_scene):
        if token not in atmosphere:
            errors.append(f"storm atmosphere integration missing: {token}")
    if all(token in atmosphere for token in (camp_call, finale_call, open_scene)):
        if not (atmosphere.index(camp_call) < atmosphere.index(finale_call) < atmosphere.index(open_scene)):
            errors.append("storm story order must be camp -> signal finale -> reopen scene for atmosphere")

    for text, label in ((review, "Review-ProductionArt.ps1"), (bootstrap, "Bootstrap-M0b.ps1")):
        for filename in ("ProductionArtStormCampStoryBuilder.cs", "ProductionArtSignalFinaleStoryBuilder.cs"):
            if filename not in text:
                errors.append(f"{label} must copy {filename} into the Unity project")

    print("Project ØEN signal-finale micro-story QA")
    print("  finale props    : 8 canonical, bounded around beacon")
    print("  scene cost      : <=50k triangles / <=32 material slots / no colliders, physics, particles, lights or animation")
    print("  integration     : camp story -> signal finale story -> rain/wetness")
    print("  Unity handoff   : both story builders copied by fast review + M0b bootstrap")

    if errors:
        print(f"\nFAILED with {len(errors)} issue(s):")
        for error in errors:
            print(" - " + error)
        return 1

    print("\nPASS: signal finale story is bounded, canonical, build-isolated and present in both Unity handoff paths.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
