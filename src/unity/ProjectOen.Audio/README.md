# ProjectOen.Audio

Unity audio binding for Project ØEN.

The full Unity project is maintained outside this repository. Mirror runtime/editor scripts into the production project under `Assets/ProjectOen/Scripts/Audio/`; audio assets belong under `Assets/ProjectOen/Audio/`.

## Architecture

- `AudioEventId` — stable typed runtime IDs; never renumber existing values.
- `AudioEventDefinition` — clips, mixer route, spatial/playback settings and variation behavior.
- `AudioCatalog` — current runtime event-definition collection.
- `AudioService` — scene-owned pooled one-shot service; intentionally **not** a singleton.
- `AudioLoopEmitter` — persistent physical emitters such as fire and rain-on-tarp.
- `AudioAmbienceProfile` / `AudioAmbienceController` — layered loop profiles and crossfades; settled ambience is restored after runtime disable/re-enable.
- `AudioAmbienceZone` — occupancy-aware ambience trigger; multiple XR/player colliders do not cause premature exit transitions.
- `AudioWorldStateRouter` — biome/day, shelter, storm and adaptive-music routing.
- `AudioRandomEmitter` — intermittent spatial one-shots.
- `AudioWorldStateEmitterRouter` — state-aware lifecycle for random world emitters.
- `AudioWorldAnchorFollower` — explicit listener-relative anchor with no global runtime search.
- `AudioSurfaceTag` / `FootstepAudioEmitter` — surface-aware VR footsteps.
- `AudioFireStateEmitter` / `AudioTarpWeatherEmitter` — gameplay adapters for fire and shelter weather.
- `AudioFoleyProfile` / `AudioFoleyEmitter` — semantic object-Foley bindings.

Gameplay code depends on `IAudioService`, not clip paths.

## Preferred first-playable workflow

CI builds `oen-unity-first-playable-audio-v1`. The **current pack contains 173 WAV files across 47 populated runtime events**.

Extract the pack at the Unity project root so `FIRST_PLAYABLE_MANIFEST.csv` remains at project root, save/open the target gameplay scene, allow Unity import to finish, then run:

`Project Oen > Audio > Build + Install First Playable (One Click)`

The high-level path:

1. verifies `FIRST_PLAYABLE_MANIFEST.csv` before mutating generated assets;
2. checks every manifested WAV by byte count, SHA-256 and imported `AudioClip` identity;
3. rejects duplicate event/variation identities and stale/unmanaged canonical WAVs from older extractions;
4. enforces the stable minimum baseline of **160 canonical clips / 45 events** while accepting additive current coverage;
5. creates/updates canonical `AudioEventDefinition` assets and builds `AudioCatalog.asset` from only current manifested events;
6. clears clips from stale definitions that are no longer in the current manifest while preserving their tuning/history assets;
7. synchronizes 11 generated first-playable profile memberships and preserves gains for still-valid layers;
8. creates/reuses `AudioRuntime_FirstPlayable.prefab`;
9. installs exactly one generated runtime instance into the active saved scene;
10. refuses Prefab Mode, Play Mode, unsaved scenes, manifest/catalog mismatch, incomplete/stale imports, duplicate `AudioService` ownership and an existing manual runtime it does not own;
11. marks the scene dirty but never auto-saves it;
12. requires unambiguous listener ownership for listener-relative world emitters.

Lower-level build/install/audit commands remain available, but they enforce the same manifest integrity boundary rather than acting as bypasses.

See:

- `docs/41_UNITY_FIRST_PLAYABLE_AUDIO_ASSEMBLY.md`
- `docs/42_AUDIO_ONE_CLICK_FIRST_PLAYABLE.md`
- `docs/43_AUDIO_SCENE_INSTALL_AND_WORLD_FAUNA.md`
- `docs/45_AUDIO_PREMERGE_ACCEPTANCE.md`

## Generated runtime composition

The generated first-playable prefab contains:

- `AudioService`, one-shot pool baseline 24 for Quest 2;
- `BiomeAmbience` controller;
- `WeatherAmbience` controller;
- `MusicAmbience` controller;
- `AudioWorldStateRouter`;
- a `WorldFauna` composition child.

Scene installation creates/refreshes two listener-relative roots that require exactly one active `AudioListener`:

### WorldFauna / JungleDay_Cicadas

- event: `SFX_NAT_Insect_CicadaCluster`;
- biome: Jungle;
- day: Day;
- storm: Calm;
- exterior only;
- cadence: 14–34 s;
- horizontal radius: 18 m;
- vertical jitter: 2.5 m.

### WorldWeather / RainFire_ThunderFar

- event: `SFX_WTH_Thunder_Far`;
- biome-independent;
- day/night-independent;
- storm: RainFire;
- exterior only;
- cadence: 18–42 s;
- horizontal radius: 32 m;
- vertical jitter: 10 m.

If the active scene has zero or multiple active listeners, both listener-relative roots are disabled rather than guessing a target, and the active-scene audit reports failure. `AudioWorldStateEmitterRouter` starts/stops emitters only in Play Mode and reacts to `AudioWorldStateRouter.StateChanged` rather than polling simulation state.

## World-state routing

Release-1 storm progression is:

1. `Calm`
2. `Wind`
3. `RainFire`
4. `Signal`

Generated first-playable mappings use only audio that actually exists:

- Beach Day -> `SFX_AMB_Beach_OceanNear`.
- Jungle Day -> `SFX_AMB_Jungle_DayBed`.
- unavailable Beach/Jungle Night, Ridge, Camp and shelter states -> `FP_Biome_Silence`.
- Calm -> empty weather/music profiles.
- Wind -> storm wind + `MUS_Storm_Phase1`.
- RainFire -> stronger wind/rain + `MUS_Storm_Phase2` plus listener-relative distant-thunder transients outdoors.
- Signal -> strongest first-pass storm bed + `MUS_Storm_Phase3`.

Generated profile membership is synchronized on rerun. Existing gains for requested layers that are still valid are retained; unavailable/removed layers disappear. This avoids stale profiles when the staged first-playable artifact grows or shrinks.

Expected optional production mixer snapshots remain:

- `MX_CalmExterior`
- `MX_CalmShelter`
- `MX_StormWindExterior`
- `MX_StormWindShelter`
- `MX_StormRainExterior`
- `MX_StormRainShelter`
- `MX_StormSignalExterior`
- `MX_StormSignalShelter`

The builder reuses matching mixer groups/snapshots when they exist; it does not manufacture a production mixer through unsupported/internal APIs.

## Fire and tarp integration

### Campfire

Wire `AudioFireStateEmitter` to:

- fire loop emitter (`SFX_ENV_Fire_Low` / `SFX_ENV_Fire_Idle`);
- random fire-pop emitter once `SFX_ENV_Fire_Pop` is produced;
- gameplay calls `SetBurnIntensity`, `OnIgnited`, `OnWoodAdded`, `OnExtinguished`.

### Tarp/weather

Wire `AudioTarpWeatherEmitter` to:

- local rain-on-tarp loop;
- tarp flap random emitter;
- authoritative `SetWeather(wind01, rain01)` updates;
- `OnTarpHandled()` and `OnTensionChanged()` interactions.

The local tarp emitter remains separate from the broad 2D weather bed so the shelter has a physical VR location.

## Object Foley

Interactable prefabs use `AudioFoleyEmitter` + an `AudioFoleyProfile`; they never reference individual clips. `AudioService` owns variation selection centrally.

Physical recording is intentionally split into two validated contracts:

- **main Foley:** `content/audio/foley_recording_plan.csv` — **40 events / 388 selected variations**;
- **supplemental Foley:** `content/audio/supplemental_foley_recording_plan.csv` — **13 events / 90 selected variations**.

Combined physical recording target: **53 events / 478 selected variations**. These recordings have not been physically captured yet and remain explicit later production work rather than fake-completed assets.

## Current first-playable readiness

`tools/report_audio_first_playable_readiness.py` owns the 115-event inventory.

Current contract:

- canonical runtime events: **115**;
- produced candidate events: **47**;
- produced candidate WAVs represented by registries: **173**;
- still without produced WAVs: **68**;
- missing events without an explicit production lane: **0**;
- main Foley: **40 events / 388 variations**;
- supplemental Foley: **13 events / 90 variations**;
- remaining field-source backlog: **11 events**, all covered by a source-page-verified acquisition plan but not yet source-ready;
- reviewed-field lane retains tarp/Amazon source upgrades/jobs that require original download, listening and SHA pinning.

`SFX_NAT_Insect_CicadaCluster` and `SFX_WTH_Thunder_Far` already have produced candidates while retaining higher-quality reviewed-source upgrade paths.

The readiness reporter canonicalizes the historical manifest labels `SFX_STS_Hunger_Warn` / `SFX_STS_Thirst_Warn` to runtime `SFX_STS_Injury_Warn` / `SFX_STS_ColdWet_Warn` without rewriting compatibility data.

## Produced artifacts

Audio Validation publishes six artifact groups:

1. `oen-audio-first-playable-readiness-v1` — first-playable readiness plus merge-readiness CSV/Markdown reports.
2. `oen-authored-ui-status-v1` — 65 original authored UI/status WAVs.
3. `oen-authored-gameplay-stingers-v1` — 66 original authored gameplay/stinger WAVs.
4. `oen-authored-adaptive-music-v1` — 14 stereo adaptive-music candidates across all six `MUS_*` events.
5. `oen-public-domain-environment-v0` — **28** technically normalized Public Domain/CC0 environmental candidates with provenance.
6. `oen-unity-first-playable-audio-v1` — combined Unity-root pack with **173 WAV / 47 events** plus `FIRST_PLAYABLE_MANIFEST.csv`.

Authored UI/status and gameplay/stinger packs contain no third-party samples. Adaptive music is procedurally authored and remains candidate material pending headset listening.

The environmental source registry pins upstream SHA-256 values and derivative provenance. The environment pack includes ocean, rain, wind, fire, Jungle Day, cicada, distant-thunder and shoreline-wash candidate material. Technical build success is not headset/mastering approval.

## Source-production backlog

Every currently missing runtime event has a lane. `content/audio/audio_production_backlog.csv` now contains **11 field-source events**, all represented in `content/audio/field_source_acquisition_plan.csv` by at least one primary page-verified redistributable candidate.

The sources still require canonical-original acquisition, listening, SHA-256 pinning and exact segment review before those runtime events become produced. CI intentionally does not download previews or pretend page metadata is production audio.

## Quest profile

Baseline:

- source WAV: 48 kHz;
- local 3D one-shots/emitters: mono;
- intentional 2D beds/music/stingers: stereo where appropriate;
- long ambience/music loops: Vorbis + Streaming;
- short repeated SFX: ADPCM + Decompress On Load;
- one-shot pool: 24 until Quest 2 profiling justifies more;
- no convolution reverb or expensive baseline DSP;
- prefer source placement over heavy processing for depth.

## Canonical player statuses

New runtime/gameplay code uses only:

- Health
- Fatigue
- Injury
- Cold/Wet

`SFX_STS_Injury_Warn` and `SFX_STS_ColdWet_Warn` retain stable numeric values 1100/1101. Hunger/Thirst names remain obsolete compatibility aliases only and are rejected from current first-playable filenames/manifests.

## Pre-merge boundary

`content/audio/audio_premerge_qa.csv` contains the six deliberately physical merge gates. `tools/report_audio_merge_readiness.py` publishes their state in CI and supports a final strict mode.

The first-playable audio foundation remains merge-blocked until there is evidence for:

1. Unity 6000.4.10f1 import + compile;
2. first-playable manifest/catalog/profile audit;
3. active gameplay-scene audit;
4. Quest 2 functional audio smoke test;
5. Quest 2 headset mix/listening approval of the current 173-WAV artifact;
6. Quest 2 audio-heavy performance soak against the project 72 Hz gate.

Run after evidence has been recorded:

```bash
python tools/report_audio_merge_readiness.py --strict
```

Full-production field-source/Foley recording remains explicit post-first-playable work. It is not re-labelled as complete merely to make this foundation PR mergeable.

Do not promote candidate audio to mastered/production status based on CI alone.
