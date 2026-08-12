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
    random_emitter = read("src/unity/ProjectOen.Audio/AudioRandomEmitter.cs")
    world_anchor = read("src/unity/ProjectOen.Audio/AudioWorldAnchorFollower.cs")
    emitter_router = read("src/unity/ProjectOen.Audio/AudioWorldStateEmitterRouter.cs")
    definition_builder = read("src/unity/ProjectOen.Audio.Editor/ProjectOenAudioFirstPlayableBuilder.cs")
    one_click = read("src/unity/ProjectOen.Audio.Editor/ProjectOenAudioOneClickFirstPlayableBuilder.cs")
    scene_installer = read("src/unity/ProjectOen.Audio.Editor/ProjectOenAudioSceneInstaller.cs")

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
        "_shelterDay", "_shelterNight", "_biome", "_dayPhase", "_stormPhase", "_sheltered",
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
    require(one_click, 'ExpectedGeneratedProfileCount = 11', "generated profile audit")
    require(one_click, 'profileCount < ExpectedGeneratedProfileCount', "generated profile audit")
    require(one_click, 'GetComponentsInChildren<AudioAmbienceController>(true).Length >= 3', "runtime controller audit")

    # Stable minimum first-playable baseline. Current artifacts may contain more clips/events.
    require(one_click, 'ExpectedFirstPlayableClipCount = 160', "first-playable coverage gate")
    require(one_click, 'ExpectedFirstPlayableEventCount = 45', "first-playable coverage gate")
    require(one_click, 'MeasureCanonicalClipCoverage()', "first-playable coverage gate")
    require(one_click, 'incomplete first-playable audio import', "first-playable coverage gate")

    # Missing biome-state content must crossfade to an explicit empty profile rather than
    # accidentally leaving the previous biome bed playing.
    require(one_click, '"FP_Biome_Silence"', "silent biome fallback")
    require(one_click, 'routerObject.FindProperty("_shelterDay").objectReferenceValue = biomeSilence', "shelter silence fallback")
    require(one_click, 'routerObject.FindProperty("_shelterNight").objectReferenceValue = biomeSilence', "shelter silence fallback")
    require(one_click, 'biomes.arraySize = 4', "complete biome fallback bindings")
    require(one_click, 'AudioBiome.Ridge', "complete biome fallback bindings")
    require(one_click, 'AudioBiome.Camp', "complete biome fallback bindings")

    # World-state dependent emitters must react to the existing authoritative audio state.
    require(router, 'public event Action StateChanged', "world-state notifications")
    for setter in ("SetBiome", "SetDayPhase", "SetStormPhase", "SetSheltered"):
        require(router, setter, "world-state notifications")
    require(router, 'StateChanged?.Invoke()', "world-state notifications")
    require(emitter_router, '_worldState', "world emitter router")
    require(emitter_router, '_bindings', "world emitter router")
    require(emitter_router, '_matchBiome', "world emitter optional biome gate")
    require(emitter_router, '_stormPhase', "world emitter storm gate")
    require(emitter_router, 'StateChanged += Apply', "world emitter router subscription")
    require(emitter_router, 'StateChanged -= Apply', "world emitter router subscription")
    require(emitter_router, 'state.Sheltered', "world emitter shelter gating")
    require(emitter_router, 'Application.isPlaying', "world emitter edit-mode guard")

    # World anchor follows an explicit scene-assigned listener target and never searches globally.
    require(world_anchor, 'public void Configure(Transform target', "world audio anchor")
    require(world_anchor, 'public Transform Target => _target', "world audio anchor")
    forbid(world_anchor, 'Camera.main', "world audio anchor")
    forbid(world_anchor, 'FindFirstObjectByType', "world audio anchor")
    forbid(world_anchor, 'FindObjectOfType', "world audio anchor")

    # Scene installer is the high-level one-click path. It must preserve scene ownership,
    # refuse duplicates/stale imports, keep listener ambiguity silent, and not auto-save scenes.
    require(scene_installer, 'Project Oen/Audio/Build + Install First Playable (One Click)', "scene one-click menu")
    require(scene_installer, 'EditorApplication.isPlayingOrWillChangePlaymode', "scene install play-mode guard")
    require(scene_installer, 'PrefabStageUtility.GetCurrentPrefabStage()', "scene install prefab-stage guard")
    require(scene_installer, 'string.IsNullOrWhiteSpace(scene.path)', "scene install saved-scene guard")
    require(scene_installer, 'ExpectedFirstPlayableClipCount = 160', "scene install coverage guard")
    require(scene_installer, 'ExpectedFirstPlayableEventCount = 45', "scene install coverage guard")
    require(scene_installer, 'services.Count > 1', "scene duplicate-service guard")
    require(scene_installer, 'PrefabUtility.InstantiatePrefab(prefab, scene)', "scene prefab install")
    require(scene_installer, 'EditorSceneManager.MarkSceneDirty(scene)', "scene dirty tracking")
    forbid(scene_installer, 'EditorSceneManager.SaveScene', "scene auto-save prohibition")
    require(scene_installer, 'listeners.Count == 1', "listener ownership guard")
    require(scene_installer, 'root.SetActive(false)', "listener ambiguity silence")
    require(scene_installer, 'WorldFaunaName = "WorldFauna"', "WorldFauna root")
    require(scene_installer, 'WorldWeatherName = "WorldWeather"', "WorldWeather root")
    require(scene_installer, 'followers.Count >= 2', "two listener-relative world roots")
    require(scene_installer, 'emitterRouters.Count >= 2', "two world-state emitter routers")
    require(scene_installer, 'randomEmitters.Count >= 2', "two random world emitters")

    # First real world transient lanes: calm Jungle Day cicadas + biome-independent RainFire thunder.
    require(scene_installer, 'AudioEventId.SFX_NAT_Insect_CicadaCluster', "first world-fauna event")
    require(scene_installer, 'new Vector2(14f, 34f)', "cicada cadence")
    require(scene_installer, 'AudioEventId.SFX_WTH_Thunder_Far', "first world-weather event")
    require(scene_installer, 'new Vector2(18f, 42f)', "distant thunder cadence")
    require(scene_installer, 'AudioStormPhase.RainFire', "distant thunder storm phase")
    require(scene_installer, 'false,\n                AudioDayPhase.Day,\n                false,\n                AudioStormPhase.RainFire', "distant thunder biome/day independence")
    require(scene_installer, 'FindProperty("_playOnEnable").boolValue = false', "state-owned random emitter")

    for token in ("_audioService", "_events", "_delaySeconds", "_horizontalRadius", "_verticalJitter", "_playOnEnable"):
        require(random_emitter, token, "AudioRandomEmitter")
        require(scene_installer, f'FindProperty("{token}")', "scene random-emitter wiring")

    for token in ("_emitter", "_biome", "_matchBiome", "_dayPhase", "_matchDayPhase", "_stormPhase", "_exteriorOnly"):
        require(emitter_router, token, "AudioWorldStateEmitterRouter binding")
        require(scene_installer, f'FindPropertyRelative("{token}")', "scene emitter-router wiring")

    # Legacy aliases may appear only as explicit name exclusions while parsing filenames.
    require(one_click, 'name != "SFX_STS_Hunger_Warn"', "legacy alias exclusion")
    require(one_click, 'name != "SFX_STS_Thirst_Warn"', "legacy alias exclusion")
    forbid(one_click, 'AudioEventId.SFX_STS_Hunger_Warn', "active legacy alias use")
    forbid(one_click, 'AudioEventId.SFX_STS_Thirst_Warn', "active legacy alias use")
    forbid(scene_installer, 'AudioEventId.SFX_STS_Hunger_Warn', "scene active legacy alias use")
    forbid(scene_installer, 'AudioEventId.SFX_STS_Thirst_Warn', "scene active legacy alias use")

    print(
        "Unity audio editor contract OK: serialized wiring, numeric IDs, one-click bootstrap/install, "
        "160/45 minimum coverage, silent fallbacks, listener-relative fauna/weather transients and canonical statuses"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
