# ProjectOen.Audio

Unity audio binding for Project ØEN.

The full Unity project is maintained outside this repository. Mirror runtime/editor scripts into the production project under `Assets/ProjectOen/Scripts/Audio/`; audio assets belong under `Assets/ProjectOen/Audio/`.

## Architecture

- `AudioEventId` — stable typed runtime IDs; never renumber existing values.
- `AudioEventDefinition` — clips, mixer route, spatial/playback settings and variation behavior.
- `AudioCatalog` — runtime event-definition collection.
- `AudioService` — scene-owned pooled one-shot service; intentionally **not** a singleton.
- `AudioLoopEmitter` — persistent physical emitters such as fire and rain-on-tarp.
- `AudioAmbienceProfile` / `AudioAmbienceController` — layered loop profiles and crossfades.
- `AudioWorldStateRouter` — biome/day, shelter, storm and adaptive-music routing.
- `AudioRandomEmitter` — intermittent spatial one-shots.
- `AudioWorldStateEmitterRouter` — state-aware lifecycle for random world emitters.
- `AudioWorldAnchorFollower` — explicit listener-relative anchor with no global runtime search.
- `AudioSurfaceTag` / `FootstepAudioEmitter` — surface-aware VR footsteps.
- `AudioFireStateEmitter` / `AudioTarpWeatherEmitter` — gameplay adapters for fire and shelter weather.
- `AudioFoleyProfile` / `AudioFoleyEmitter` — semantic object-Foley bindings.

Gameplay code depends on `IAudioService`, not clip paths.

## Preferred first-playable workflow

CI builds `oen-unity-first-playable-audio-v1`. The **current pack contains 163 WAV files across 46 populated runtime events**.

Extract the pack at the Unity project root, save/open the target gameplay scene, then run:

`Project Oen > Audio > Build + Install First Playable (One Click)`

The high-level command:

1. enforces the stable minimum import baseline of **160 canonical clips / 45 events** before mutating generated runtime content;
2. creates/updates canonical `AudioEventDefinition` assets and `AudioCatalog.asset`;
3. creates 11 missing generated first-playable profiles, including `FP_Biome_Silence`;
4. creates/reuses `AudioRuntime_FirstPlayable.prefab`;
5. installs exactly one generated runtime instance into the active saved scene;
6. refuses Prefab Mode, Play Mode, unsaved scenes, incomplete imports, duplicate `AudioService` ownership, and an existing manual runtime it does not own;
7. marks the scene dirty but never auto-saves it;
8. preserves generated profile/prefab tuning on rerun.

The current pack can grow beyond 160/45 without forcing the stable Editor safety floor to change every time another candidate is added.

Lower-level commands remain available for manual production integration:

- `Project Oen > Audio > Build First Playable (One Click)` — assets/prefab only, no scene install.
- `Project Oen > Audio > Build First-Playable Definitions + Catalog`.
- `Project Oen > Audio > Rebuild Selected Audio Catalog`.
- `Project Oen > Audio > Audit Audio Event Definitions`.
- `Project Oen > Audio > Audit First Playable (One Click)`.
- `Project Oen > Audio > Audit Active Scene Audio Runtime`.

See `docs/41_UNITY_FIRST_PLAYABLE_AUDIO_ASSEMBLY.md`, `docs/42_AUDIO_ONE_CLICK_FIRST_PLAYABLE.md`, and `docs/43_AUDIO_SCENE_INSTALL_AND_WORLD_FAUNA.md`.

## Generated runtime composition

The generated first-playable prefab contains:

- `AudioService`, one-shot pool baseline 24 for Quest 2;
- `BiomeAmbience` controller;
- `WeatherAmbience` controller;
- `MusicAmbience` controller;
- `AudioWorldStateRouter`;
- `WorldFauna` composition root.

Scene installation additionally creates/refreshes listener-relative world roots that require exactly one active `AudioListener`:

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

If the active scene has zero or multiple active listeners, both listener-relative roots remain disabled instead of guessing a target. `AudioWorldStateEmitterRouter` starts/stops emitters only in Play Mode and reacts to `AudioWorldStateRouter.StateChanged` rather than polling simulation state.

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

Explicit silence fallbacks prevent stale ambience from leaking across state changes.

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

Combined physical recording target: **53 events / 478 selected variations**. These recordings have **not** been physically captured yet.

The supplemental plan covers shelter beds, wing flaps, threat rustles/snaps/scrapes, fire interactions, generic pickup/drop and build placement/hammer actions. It stays separate so the established 40/388 main-Foley contract does not drift.

## First-playable readiness

`tools/report_audio_first_playable_readiness.py` makes the 115-event inventory fail closed. Audio Validation publishes `oen-audio-first-playable-readiness-v1` as CSV + Markdown.

Current readiness contract:

- canonical runtime events: **115**;
- produced candidate events: **46**;
- produced candidate WAVs represented by registries: **163**;
- still without produced WAVs: **69**;
- missing events without an explicit production lane: **0**.

Missing-event lanes:

- main physical Foley: **40 events**;
- supplemental physical Foley: **13 events**;
- reviewed field-source originals: **4 events**;
- new field-source discovery: **8 events**;
- pinned/public-domain candidate audit: **4 events**.

`SFX_NAT_Insect_CicadaCluster` and `SFX_WTH_Thunder_Far` already have produced candidates but also retain reviewed-source upgrade paths.

The readiness reporter canonicalizes the two historical manifest labels `SFX_STS_Hunger_Warn` / `SFX_STS_Thirst_Warn` to runtime `SFX_STS_Injury_Warn` / `SFX_STS_ColdWet_Warn` without rewriting the compatibility manifest.

## Produced artifacts

Audio Validation currently targets **six artifacts**:

1. `oen-audio-first-playable-readiness-v1` — readiness CSV/Markdown.
2. `oen-authored-ui-status-v1` — 65 original authored UI/status WAVs.
3. `oen-authored-gameplay-stingers-v1` — 66 original authored gameplay/stinger WAVs.
4. `oen-authored-adaptive-music-v1` — 14 stereo adaptive-music candidates across all six `MUS_*` events.
5. `oen-public-domain-environment-v0` — **18** technically normalized Public Domain/CC0 environmental candidates.
6. `oen-unity-first-playable-audio-v1` — combined Unity-root pack with **163 WAV / 46 events**.

Authored UI/status and gameplay/stinger packs contain no third-party samples. Adaptive music is procedurally authored and remains candidate material pending listening.

The environmental source registry pins upstream SHA-256 values and the build emits provenance. It now includes the Public Domain `Tonitrus.ogg` source with three `SFX_WTH_Thunder_Far` candidate cuts. These thunder cuts are technically built candidates, not headset-approved masters.

The combined Unity pack carries `FIRST_PLAYABLE_MANIFEST.csv` with SHA-256 for every staged WAV.

## Source-production backlog

Every currently missing runtime event has a lane. `content/audio/audio_production_backlog.csv` tracks the remaining 12 non-recording source tasks:

- **8 field-source** events requiring new authentic source discovery/capture;
- **4 public-domain-candidate audits** using already pinned `waves_pd`, `wind_cc0`, or `fire_pd` material where feasible.

The readiness validator rejects unknown events, lane overlaps, variation-count drift, or an unassigned missing event.

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

`SFX_STS_Injury_Warn` and `SFX_STS_ColdWet_Warn` retain stable numeric values 1100/1101. Hunger/Thirst names remain obsolete compatibility aliases only.

## Acceptance boundaries

Repo/CI work can validate manifests, deterministic authored generation, source hashes, encoding, readiness ownership, Editor serialized-field contracts and Unity pack staging. It does **not** replace physical Unity/Quest verification.

Remaining physical/production gates include:

- import + compile in Unity 6000.4.10f1;
- instantiate/inspect the generated scene runtime;
- confirm no Missing Script references;
- exercise Beach/Jungle and Calm -> Wind -> RainFire -> Signal transitions;
- verify cicada/thunder state gating and listener-relative placement;
- headset listening/mix approval for adaptive/environmental/thunder candidates;
- imported-scene seamless-loop QA;
- physically record/select/edit main 388 + supplemental 90 Foley variations;
- acquire/SHA-pin reviewed tarp/Amazon originals;
- source/approve remaining backlog material;
- Quest 2 performance and final mix pass.

Do not promote candidate audio to mastered/production status based on CI alone.
