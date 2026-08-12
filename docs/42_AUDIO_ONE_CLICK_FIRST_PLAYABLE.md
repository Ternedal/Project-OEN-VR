# Project ØEN — Audio one-click first playable

## Goal

After extracting the `oen-unity-first-playable-audio-v1` artifact at the Unity project root, the first-playable audio setup should require one Editor command rather than manual creation of dozens of ScriptableObjects and scene references.

Run:

`Project Oen > Audio > Build First Playable (One Click)`

## What the command does

1. Scans canonical numbered clips below `Assets/ProjectOen/Audio/` and refuses to continue unless the v1 import contains at least **160 clips across 45 runtime events**.
2. Runs the existing first-playable definition/catalog builder.
3. Creates or updates `AudioEventDefinition` assets and `AudioCatalog.asset`.
4. Creates missing baseline first-playable ambience/weather/music profiles.
5. Creates `AudioRuntime_FirstPlayable.prefab` with:
   - `AudioService` using the generated catalog and a 24-source Quest 2 baseline pool;
   - `BiomeAmbience`, `WeatherAmbience`, and `MusicAmbience` controllers;
   - `AudioWorldStateRouter` wired to those controllers;
   - a `WorldFauna` composition child ready for spatial random emitters.
6. Wires the available first-playable biome, storm, and adaptive-music profiles.
7. Wires unavailable biome/night/shelter states to an explicit empty profile so stale ambience cannot leak across state changes.
8. Reuses exact-name mixer snapshots if the real Unity project already contains them.
9. Runs a structural first-playable audit.

## Generated baseline profiles

The command creates these assets only when they are missing:

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

The current baseline intentionally does **not** invent Beach Night, Jungle Night, Ridge, Camp, or shelter content when approved clips are unavailable. Instead those states resolve to `FP_Biome_Silence`. This is deliberate fail-closed behaviour: missing audio becomes silence rather than accidentally retaining the previous biome bed or reusing unrelated sound.

## Non-destructive reruns

The definition builder refreshes clip membership because new approved variations need to appear automatically. Existing definition playback tuning is preserved except for clip membership, stable event ID, and missing mixer routing.

Generated profiles and `AudioRuntime_FirstPlayable.prefab` are different: once they exist, the one-click command leaves them untouched. This protects designer changes to gains, profile composition, component values, and prefab wiring. Delete a generated asset explicitly if the baseline should be regenerated from scratch.

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

When real approved beds become available, replace the silence bindings in the generated prefab/profile configuration during production integration.

## Import coverage gate

The one-click command does not trust an old `AudioCatalog.asset` as proof that the current audio artifact is present. It measures imported canonical `AudioClip` assets directly and stops before mutating generated runtime content unless it finds the current v1 baseline of at least **160 clips / 45 events**.

Legacy Hunger/Thirst enum aliases are explicitly excluded from canonical filename resolution; new assets and gameplay bindings remain Injury/ColdWet.

## Mixer behaviour

The builder does not manufacture a Unity `AudioMixer` through unsupported/internal Editor APIs. `AudioEventDefinition` routing is filled only when matching real mixer groups already exist. The runtime bootstrap similarly looks up the documented snapshot names and assigns them only when an existing mixer exposes exact matches.

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

`tools/validate_audio_unity_editor_contract.py` checks the string-based `SerializedObject` contract used by the Editor builders. It also verifies the 160/45 import gate, the explicit silence fallbacks, numeric event-ID serialization, and that legacy Hunger/Thirst aliases are only mentioned as exclusions rather than active runtime enum references.

If a private serialized runtime field is renamed without updating the builders, CI fails rather than allowing the mismatch to reach manual Unity import.

This is a static contract check, **not** a claim that Unity has compiled the scripts. Physical Unity 6000.4.10f1 import/compile remains an explicit production gate.

## Manual Unity acceptance after generation

After running the one-click command in the real project:

1. Confirm the command reports complete 160/45 import coverage.
2. Confirm `AudioRuntime_FirstPlayable.prefab` has no Missing Script references.
3. Open `AudioCatalog.asset` and confirm expected definitions are populated.
4. Run `Project Oen > Audio > Audit Audio Event Definitions`.
5. Run `Project Oen > Audio > Audit First Playable (One Click)`.
6. Instantiate the runtime prefab from the project bootstrap/composition root.
7. Exercise Beach Day, Jungle Day, missing Night/Ridge/Shelter states, and Calm -> Wind -> RainFire -> Signal transitions.
8. Confirm missing biome states crossfade to silence instead of retaining the previous bed.
9. Confirm mixer routes/snapshots if the production mixer exists.
10. Perform headset listening and Quest 2 profiling before promoting candidate audio to mastered/production status.
