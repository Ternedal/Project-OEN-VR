#!/usr/bin/env python3
"""Static content gate for the enriched Stormnatten production-art showcase."""
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SHOWCASE=ROOT/"src"/"unity"/"ProjectOen.Art"/"Editor"/"ProductionArtShowcaseBuilder.cs"
STORY=ROOT/"src"/"unity"/"ProjectOen.Art"/"Editor"/"ProductionArtStormCampStoryBuilder.cs"
ATMOSPHERE=ROOT/"src"/"unity"/"ProjectOen.Art"/"Editor"/"ProductionArtStormAtmosphereBuilder.cs"

REQUIRED=(
    'BuildGroundWeatherAccents();',
    'BuildCampDressing();',
    '"en-011_", "large"',
    '"en-011_", "medium"',
    '"en-025_", "storm"',
    '"cs-016_", "mid_repair"',
    '"en-016_", "wet"',
    '"en-017_", "pot"',
    '"en-018_", "sack"',
    '"en-020_", "frame"',
    '"en-020_", "cloth"',
    '"en-020_", "basin"',
    '"en-023_", "loose_cloth"',
    '"en-019_", "logs"',
    '"en-019_", "ropes"',
    '"en-019_", "stones"',
    '"en-004_", "medium"',
    '"en-013_", "dense"',
    '"cs-004_"',
    '"cs-010_"',
    '"pr-001_", "wet"',
    '"cs-015_"',
    '"pr-014_", "storm_damaged"',
    '"en-001_", "large"',
    '"Storm-Damaged Shelter"',
    '"Campfire Nearly Out Wet"',
    '"Wet Tarp"',
    '"Wet Camp Groundsheet"',
    '"Signal Beacon Storm Damaged"',
    '"Signal Cloth"',
)
FORBIDDEN=(
    '"cs-003_"',
    '"cs-008_"',
    '"cs-013_"',
    '"cs-014_"',
    '"en-016_", "worn"',
    '"pr-014_", "worn"',
    'lighthouse',
    'Hunger',
    'Thirst',
    'BuildPipeline.BuildPlayer',
    'EditorBuildSettings.scenes',
)

STORY_REQUIRED=(
    'ExpectedStoryObjectCount = 9',
    '"Collapsed Shelter Crossbrace", "en-023_", "broken_shelter_parts"',
    '"Storm-Torn Shelter Debris", "en-023_", "broken_shelter_parts"',
    '"Shelter Guy Rope Under Load", "en-024_", "taut"',
    '"Shelter Rope Failure", "en-024_", "slack"',
    '"Snapped Wood Bundle", "pr-003_", "damaged"',
    '"Overturned Storage Crate", "en-018_", "crate"',
    '"Scattered Cooking Utensils", "en-017_", "utensils"',
    '"Camp Rope Washout", "en-004_", "small"',
    '"Shelter Foot Puddle", "en-011_", "small"',
    'FindPrefabStrict(spec.prefix, spec.token)',
    'throw new InvalidOperationException("Canonical story prefab missing:',
    'StripRuntimeOnlyCost(instance);',
    'TriangleHardLimit = 60000',
    'MaterialSlotHardLimit = 36',
    'root.GetComponentsInChildren<Collider>(true).Length != 0',
    'root.GetComponentsInChildren<Rigidbody>(true).Length != 0',
    'root.GetComponentsInChildren<ParticleSystem>(true).Length != 0',
    'root.GetComponentsInChildren<Light>(true).Length != 0',
    'root.GetComponentsInChildren<Animation>(true).Length != 0',
    'PrefabUtility.GetPrefabAssetPathOfNearestInstanceRoot',
)
STORY_FORBIDDEN=(
    'void Update(',
    'void LateUpdate(',
    'AddComponent<ParticleSystem>',
    'AddComponent<Light>',
    'AddComponent<Rigidbody>',
    '?? candidates[0]',
)
ATMOSPHERE_REQUIRED=(
    'ProductionArtStormCampStoryBuilder.BuildIntoShowcase();',
    'var scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);',
)


def main()->int:
    errors=[]
    for path,label in ((SHOWCASE,"showcase builder"),(STORY,"storm camp story builder"),(ATMOSPHERE,"storm atmosphere builder")):
        if not path.exists():
            errors.append(f"missing {label}: {path.relative_to(ROOT)}")
    if errors:
        print("ERROR: "+"; ".join(errors))
        return 1

    text=SHOWCASE.read_text(encoding="utf-8")
    story=STORY.read_text(encoding="utf-8")
    atmosphere=ATMOSPHERE.read_text(encoding="utf-8")
    errors=[]

    for token in REQUIRED:
        if token not in text: errors.append(f"missing showcase coverage token: {token}")
    for token in FORBIDDEN:
        if token in text: errors.append(f"forbidden showcase token: {token}")

    # Decal holders must never be marked as environment static/occluders in the base showcase.
    for marker in ('"Wet Mud Puddle Large", false', '"Wet Mud Puddle Medium", false', '"Storm Shoreline Foam", false'):
        if marker not in text: errors.append(f"ground decal must remain non-static: {marker}")

    for token in STORY_REQUIRED:
        if token not in story: errors.append(f"missing storm camp micro-story contract: {token}")
    for token in STORY_FORBIDDEN:
        if token in story: errors.append(f"forbidden storm camp micro-story runtime cost/fallback: {token}")
    for token in ATMOSPHERE_REQUIRED:
        if token not in atmosphere: errors.append(f"storm atmosphere must integrate micro-story before atmosphere build: {token}")

    # Story positions are deliberately bounded around the camp rather than spreading
    # a second environment layer across the whole showcase.
    if story.count('new StorySpec(') != 9:
        errors.append(f"storm camp story must contain exactly 9 authored specs, found {story.count('new StorySpec(')}")
    if 'StaticEditorFlags.OccluderStatic' in story:
        errors.append("small storm story props must not become occluder-static")

    print("Project ØEN enriched Stormnatten showcase QA")
    print("  ground decals : puddle large + medium + storm shoreline")
    print("  camp pressure : damaged shelter + nearly-out wet fire + wet tarp/groundsheet")
    print("  camp microstory: 9 bounded physical consequences; broken parts + rope strain/failure + displaced gear + local puddle")
    print("  camp dressing : radio repair + cooking + storage + rain catcher")
    print("  signal hill   : storm-damaged beacon/cloth + logs + ropes + stones")
    print("  beach/jungle  : wreck + rope debris + cliff grass + vegetation")
    if errors:
        print(f"\nFAILED with {len(errors)} issue(s):")
        for e in errors: print(" - "+e)
        return 1
    print("\nPASS: showcase exercises canonical storm-pressure states plus a bounded deterministic camp-consequence story without leaking runtime cost into M0b build settings.")
    return 0

if __name__=="__main__": sys.exit(main())
