#!/usr/bin/env python3
"""Static contract checks for Project OEN Unity audio Editor tooling.

This does not pretend to compile Unity. It protects the reflection/SerializedObject field-name
contract so private serialized field renames fail in CI instead of later during manual import.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(rel: str) -> str:
    path = ROOT / rel
    if not path.is_file():
        raise SystemExit(f"missing required file: {rel}")
    return path.read_text(encoding="utf-8")


def require(text: str, token: str, label: str) -> None:
    if token not in text:
        raise SystemExit(f"{label}: missing required token {token!r}")


def forbid(text: str, token: str, label: str) -> None:
    if token in text:
        raise SystemExit(f"{label}: forbidden token {token!r}")


def main() -> int:
    event_definition = read("src/unity/ProjectOen.Audio/AudioEventDefinition.cs")
    catalog = read("src/unity/ProjectOen.Audio/AudioCatalog.cs")
    profile = read("src/unity/ProjectOen.Audio/AudioAmbienceProfile.cs")
    controller = read("src/unity/ProjectOen.Audio/AudioAmbienceController.cs")
    router = read("src/unity/ProjectOen.Audio/AudioWorldStateRouter.cs")
    service = read("src/unity/ProjectOen.Audio/AudioService.cs")
    definition_builder = read("src/unity/ProjectOen.Audio.Editor/ProjectOenAudioFirstPlayableBuilder.cs")
    one_click = read("src/unity/ProjectOen.Audio.Editor/ProjectOenAudioOneClickFirstPlayableBuilder.cs")

    for token in (
        "_id", "_clips", "_output", "_loop", "_spatialBlend", "_volumeMin",
        "_volumeMax", "_pitchMin", "_pitchMax", "_priority", "_minDistance", "_maxDistance",
    ):
        require(event_definition, token, "AudioEventDefinition")
        require(definition_builder, f'FindProperty("{token}")', "first-playable definition builder")

    require(catalog, "_events", "AudioCatalog")
    require(definition_builder, 'FindProperty("_events")', "first-playable definition builder")

    for token in ("_definition", "_gain"):
        require(profile, token, "AudioAmbienceProfile")
        require(one_click, f'FindPropertyRelative("{token}")', "one-click builder")

    require(profile, "_layers", "AudioAmbienceProfile")
    require(one_click, 'FindProperty("_layers")', "one-click builder")
    require(controller, "_initialProfile", "AudioAmbienceController")
    require(one_click, 'FindProperty("_initialProfile")', "one-click builder")

    for token in (
        "_biomeAmbience", "_weatherAmbience", "_musicAmbience", "_biomes", "_storms",
        "_biome", "_dayPhase", "_stormPhase", "_sheltered",
    ):
        require(router, token, "AudioWorldStateRouter")
        require(one_click, f'FindProperty("{token}")', "one-click builder")

    for token in (
        "_biome", "_day", "_night", "_phase", "_weatherProfile", "_musicProfile",
        "_exteriorSnapshot", "_shelteredSnapshot",
    ):
        require(router, token, "AudioWorldStateRouter nested bindings")
        require(one_click, f'FindPropertyRelative("{token}")', "one-click builder")

    for token in ("_catalog", "_oneShotPoolSize"):
        require(service, token, "AudioService")
        require(one_click, f'FindProperty("{token}")', "one-click builder")

    require(definition_builder, 'FindProperty("_id").intValue = (int)group.Key', "numeric enum serialization")
    forbid(definition_builder, 'FindProperty("_id").enumValueIndex', "numeric enum serialization")

    require(one_click, 'Project Oen/Audio/Build First Playable (One Click)', "one-click menu")
    require(one_click, 'AudioRuntime_FirstPlayable.prefab', "runtime prefab")
    require(one_click, 'profileCount < 10', "generated profile audit")
    require(one_click, 'GetComponentsInChildren<AudioAmbienceController>(true).Length >= 3', "runtime controller audit")

    # First-playable v1 must fail closed if the 160-WAV / 45-event import is incomplete.
    require(one_click, 'ExpectedFirstPlayableClipCount = 160', "first-playable coverage gate")
    require(one_click, 'ExpectedFirstPlayableEventCount = 45', "first-playable coverage gate")
    require(one_click, 'MeasureCanonicalClipCoverage()', "first-playable coverage gate")
    require(one_click, 'incomplete first-playable audio import', "first-playable coverage gate")

    # Legacy aliases may appear only as explicit name exclusions while parsing filenames.
    require(one_click, 'name != "SFX_STS_Hunger_Warn"', "legacy alias exclusion")
    require(one_click, 'name != "SFX_STS_Thirst_Warn"', "legacy alias exclusion")
    forbid(one_click, 'AudioEventId.SFX_STS_Hunger_Warn', "active legacy alias use")
    forbid(one_click, 'AudioEventId.SFX_STS_Thirst_Warn', "active legacy alias use")

    print(
        "Unity audio editor contract OK: serialized field wiring, numeric IDs, "
        "one-click bootstrap, 160/45 coverage gate and canonical status usage"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
