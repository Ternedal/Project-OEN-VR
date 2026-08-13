#!/usr/bin/env python3
"""Static content gate for the enriched Stormnatten production-art showcase."""
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SHOWCASE=ROOT/"src"/"unity"/"ProjectOen.Art"/"Editor"/"ProductionArtShowcaseBuilder.cs"

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


def main()->int:
    if not SHOWCASE.exists():
        print(f"ERROR: missing showcase builder: {SHOWCASE.relative_to(ROOT)}")
        return 1
    text=SHOWCASE.read_text(encoding="utf-8")
    errors=[]
    for token in REQUIRED:
        if token not in text: errors.append(f"missing showcase coverage token: {token}")
    for token in FORBIDDEN:
        if token in text: errors.append(f"forbidden showcase token: {token}")
    # Decal holders must never be marked as environment static/occluders in the showcase.
    for marker in ('"Wet Mud Puddle Large", false', '"Wet Mud Puddle Medium", false', '"Storm Shoreline Foam", false'):
        if marker not in text: errors.append(f"ground decal must remain non-static: {marker}")

    print("Project ØEN enriched Stormnatten showcase QA")
    print("  ground decals : puddle large + medium + storm shoreline")
    print("  camp pressure : damaged shelter + nearly-out wet fire + wet tarp/groundsheet")
    print("  camp dressing : radio repair + cooking + storage + rain catcher")
    print("  signal hill   : storm-damaged beacon/cloth + logs + ropes + stones")
    print("  beach/jungle  : wreck + rope debris + cliff grass + vegetation")
    if errors:
        print(f"\nFAILED with {len(errors)} issue(s):")
        for e in errors: print(" - "+e)
        return 1
    print("\nPASS: showcase exercises canonical storm-pressure production states and refined dressing without leaking into M0b build settings.")
    return 0

if __name__=="__main__": sys.exit(main())
