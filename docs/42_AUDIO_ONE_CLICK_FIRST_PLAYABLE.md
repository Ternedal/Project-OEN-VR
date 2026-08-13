# Project ØEN — Audio one-click first playable

## Goal

After extracting the `oen-unity-first-playable-audio-v1` artifact at the Unity project root, first-playable audio setup should require one Editor command rather than manual creation of dozens of ScriptableObjects and scene references — without allowing stale WAVs or stale generated profiles from an older artifact to survive unnoticed.

Run:

`Project Oen > Audio > Build First Playable (One Click)`

For the complete saved-scene path, use:

`Project Oen > Audio > Build + Install First Playable (One Click)`

## What the command does

1. Reads `FIRST_PLAYABLE_MANIFEST.csv` from the Unity project root.
2. Verifies every manifested WAV by path, byte count, SHA-256 and imported `AudioClip` identity.
3. Rejects duplicate event/variation rows and extra canonical WAVs under `Assets/ProjectOen/Audio` that are absent from the current manifest.
4. Refuses to continue unless the verified import contains at least the stable first-playable floor of **160 clips across 45 runtime events**. The current CI artifact contains **173 clips / 47 events**.
5. Rebuilds `AudioEventDefinition` clip membership and `AudioCatalog.asset` from only the verified current manifest.
6. Clears clip arrays on old definitions that are no longer present, while preserving those assets for tuning/history.
7. Synchronizes the 11 generated baseline ambience/weather/music profiles to currently available loop events.
8. Preserves existing gain tuning for generated profile layers that remain valid while adding/removing layer membership deterministically.
9. Creates `AudioRuntime_FirstPlayable.prefab` only if it does not already exist.
10. Wires available first-playable biome, storm and adaptive-music profiles.
11. Wires unavailable biome/night/shelter states to an explicit empty profile so stale ambience cannot leak across state changes.
12. Reuses exact-name mixer snapshots if the real Unity project already contains them.
13. Runs structural first-playable audits.

## Generated baseline profiles

The synchronized generated set is:

- `FP_Biome_Silence`
- `FP_Biome_Beach_Day`
- `FP_Biome_Jungle_Day`
- `FP_Weather_Calm`
- `FP_Weather_Wind`
- `FP_Weather_RainFire`
- `FP_Weather_Signal`
- `FP_Music_Calm`
- `FP_Music_Wind`
- `FP_Music_RainFire`
- `FP_Music_Signal`

The current baseline intentionally does **not** invent Beach Night, Jungle Night, Ridge, Camp or shelter content when approved clips are unavailable. Those states resolve to `FP_Biome_Silence`. Missing audio becomes silence rather than retaining the previous biome bed or reusing unrelated sound.

## Deterministic reruns without wiping tuning

There are three different ownership rules:

**AudioEventDefinition assets:** existing playback tuning is preserved. Event ID and clip membership follow the current verified staged artifact; missing mixer routing may be filled. If an event disappears from the current manifest, its old definition asset may remain but its clip array is cleared and it is excluded from the runtime catalog.

**Generated first-playable profiles:** these are generated composition assets, so their layer membership is synchronized every rerun. This prevents a profile generated from an older smaller artifact from remaining stale. Existing gain values are preserved for requested layers that still exist; new layers receive the baseline default gain; removed/unavailable layers are removed.

**`AudioRuntime_FirstPlayable.prefab`:** once it exists, its prefab composition remains preserved. Delete/regenerate it explicitly only when the baseline prefab itself should be recreated. Because it references the generated profile assets, synchronized profile membership propagates without replacing the prefab.

## Current default storm mapping

| Storm phase | Weather profile | Music profile |
| --- | --- | --- |
| Calm | empty | empty |
| Wind | `SFX_WTH_Storm_Wind` | `MUS_Storm_Phase1` |
| RainFire | storm wind + heavy rain | `MUS_Storm_Phase2` |
| Signal | stronger storm wind + heavy rain | `MUS_Storm_Phase3` |

These mappings are first-playable starting points, not final mix approval.

## Current default biome mapping

| State | First-playable profile |
| --- | --- |
| Beach Day | `SFX_AMB_Beach_OceanNear` |
| Jungle Day | `SFX_AMB_Jungle_DayBed` |
| Beach Night | `FP_Biome_Silence` |
| Jungle Night | `FP_Biome_Silence` |
| Ridge Day/Night | `FP_Biome_Silence` |
| Camp Day/Night | `FP_Biome_Silence` |
| Shelter Day/Night | `FP_Biome_Silence` |

When real approved beds become available, the generated profile specification can intentionally promote them. A rerun will then synchronize the generated profiles instead of requiring deletion of stale assets.

## Manifest/import integrity gate

The builder does not trust an old `AudioCatalog.asset`, imported clip count or filenames alone as proof that the current artifact is present.

`ProjectOenAudioFirstPlayableManifestAudit` checks:

- `FIRST_PLAYABLE_MANIFEST.csv` exists at project root;
- its schema is exact;
- every event ID is current/canonical;
- every variation and destination is unique;
- every expected file exists and has the pinned byte count;
- every expected file has the pinned SHA-256;
- Unity has imported each expected file as a matching `AudioClip`;
- no additional canonical WAV exists under the audio tree outside the current manifest.

The final point is important for upgrades: extracting a newer artifact over an older tree may leave files that no longer belong to the new build. Those files now stop the rebuild instead of silently entering the catalog.

Legacy Hunger/Thirst enum aliases are explicitly excluded from current manifest/filename resolution; new assets and gameplay bindings remain Injury/ColdWet.

## Mixer behaviour

The builder does not manufacture a Unity `AudioMixer` through unsupported/internal Editor APIs. `AudioEventDefinition` routing is filled only when matching real mixer groups already exist. The runtime bootstrap similarly looks up documented snapshot names and assigns them only when an existing mixer exposes exact matches.

Expected snapshot names remain:

- `MX_CalmExterior`
- `MX_CalmShelter`
- `MX_StormWindExterior`
- `MX_StormWindShelter`
- `MX_StormRainExterior`
- `MX_StormRainShelter`
- `MX_StormSignalExterior`
- `MX_StormSignalShelter`

## CI guard

`tools/validate_audio_unity_editor_contract.py` statically protects:

- SerializedObject private-field names;
- manifest/hash audit presence;
- stale definition cleanup;
- catalog/manifest parity checks;
- generated profile synchronization + preserved valid-layer gains;
- the stable 160/45 compatibility floor;
- explicit silence fallbacks;
- numeric event-ID serialization;
- legacy-alias exclusion;
- scene/runtime/listener ownership rules.

If these contracts drift, CI fails before manual Unity import.

This is a static contract check, **not** a claim that Unity has compiled the scripts. Physical Unity 6000.4.10f1 import/compile remains an explicit production gate.

## Manual Unity acceptance after generation

After extracting the current artifact into the real Unity project:

1. Confirm `FIRST_PLAYABLE_MANIFEST.csv` is at project root and allow import to finish.
2. Run `Project Oen > Audio > Build First Playable (One Click)`.
3. Confirm the manifest/hash audit passes and reports the current imported coverage.
4. Confirm `AudioRuntime_FirstPlayable.prefab` has no Missing Script references.
5. Open `AudioCatalog.asset` and confirm its event count matches the manifest event count.
6. Run `Project Oen > Audio > Audit Audio Event Definitions` if available in the host project.
7. Run `Project Oen > Audio > Audit First Playable (One Click)` and require manifest/coverage/catalog/profiles/prefab status to be clean.
8. Run `Project Oen > Audio > Build + Install First Playable (One Click)` in the saved target gameplay scene.
9. Run `Project Oen > Audio > Audit Active Scene Audio Runtime` and require exactly one generated runtime, one active listener and both listener-bound world anchors.
10. Exercise Beach Day, Jungle Day, missing Night/Ridge/Shelter states and Calm -> Wind -> RainFire -> Signal transitions.
11. Confirm missing biome states crossfade to silence instead of retaining the previous bed.
12. Confirm mixer routes/snapshots if the production mixer exists.
13. Perform headset listening and Quest 2 profiling before promoting candidate audio to mastered/production status.
