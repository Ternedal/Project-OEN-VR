# Project ØEN — Audio one-click first playable

## Goal

After extracting the `oen-unity-first-playable-audio-v1` artifact at the Unity project root, the first-playable audio setup should require one Editor command rather than manual creation of dozens of ScriptableObjects and scene references.

Run:

`Project Oen > Audio > Build First Playable (One Click)`

## What the command does

1. Runs the existing first-playable definition/catalog builder.
2. Scans canonical numbered clips below `Assets/ProjectOen/Audio/`.
3. Creates or updates `AudioEventDefinition` assets and `AudioCatalog.asset`.
4. Creates missing baseline first-playable ambience/weather/music profiles.
5. Creates `AudioRuntime_FirstPlayable.prefab` with:
   - `AudioService` using the generated catalog and a 24-source Quest 2 baseline pool;
   - `BiomeAmbience`, `WeatherAmbience`, and `MusicAmbience` controllers;
   - `AudioWorldStateRouter` wired to those controllers;
   - a `WorldFauna` composition child ready for spatial random emitters.
6. Wires the available first-playable biome, storm, and adaptive-music profiles.
7. Reuses exact-name mixer snapshots if the real Unity project already contains them.
8. Runs a structural first-playable audit.

## Generated baseline profiles

The command creates these assets only when they are missing:

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

The current baseline intentionally does **not** invent Beach Night, Jungle Night, Ridge, or shelter content when approved clips are unavailable. Missing production states stay visibly incomplete rather than silently reusing unrelated sounds.

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

- Beach Day -> `SFX_AMB_Beach_OceanNear`
- Jungle Day -> `SFX_AMB_Jungle_DayBed`

Night bindings remain null until real approved night beds exist. This is deliberate fail-closed behaviour.

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

`tools/validate_audio_unity_editor_contract.py` checks the string-based `SerializedObject` contract used by the Editor builders. If a private serialized runtime field is renamed without updating the builders, CI fails rather than allowing the mismatch to reach manual Unity import.

This is a static contract check, **not** a claim that Unity has compiled the scripts. Physical Unity 6000.4.10f1 import/compile remains an explicit production gate.

## Manual Unity acceptance after generation

After running the one-click command in the real project:

1. Confirm `AudioRuntime_FirstPlayable.prefab` has no Missing Script references.
2. Open `AudioCatalog.asset` and confirm expected definitions are populated.
3. Run `Project Oen > Audio > Audit Audio Event Definitions`.
4. Run `Project Oen > Audio > Audit First Playable (One Click)`.
5. Instantiate the runtime prefab from the project bootstrap/composition root.
6. Exercise Beach Day, Jungle Day, and Calm -> Wind -> RainFire -> Signal transitions.
7. Confirm mixer routes/snapshots if the production mixer exists.
8. Perform headset listening and Quest 2 profiling before promoting candidate audio to mastered/production status.
