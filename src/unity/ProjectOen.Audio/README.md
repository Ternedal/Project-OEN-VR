# ProjectOen.Audio

Unity audio-binding for Øen.

## Placement in the real Unity project

Mirror these files under:

`Assets/ProjectOen/Scripts/Audio/`

Audio source assets themselves belong under:

`Assets/ProjectOen/Audio/`

The repository stores this module because the full Unity project is maintained outside the repo, matching the existing `src/unity/App` convention.

## Architecture

- `AudioEventId`: stable typed runtime IDs. Never renumber existing values.
- `AudioEventDefinition`: ScriptableObject definition data: clips, mixer route, spatial settings and randomization.
- `AudioCatalog`: collection of event definitions.
- `AudioService`: scene-owned, pooled one-shot playback service. It is intentionally **not** a singleton.
- `AudioLoopEmitter`: scene component for persistent physical emitters such as campfire and rain-on-tarp.
- `AudioAmbienceProfile`: layered ambience definition for a biome/state such as beach day, jungle night or shelter windy.
- `AudioAmbienceController`: two-bank ambience player that crossfades profiles without hard cuts.
- `AudioAmbienceZone`: trigger volume for biome, shelter and location transitions.
- `AudioRandomEmitter`: intermittent spatial one-shots for fauna, fire pops, shoreline washes, branch snaps and gusts.
- `AudioSurfaceTag`: material marker for walkable colliders.
- `FootstepAudioEmitter`: Quest-friendly distance-driven footsteps with ground probing and surface-specific events.

Gameplay code depends on `IAudioService`, not concrete clip paths.

## Minimum scene setup

Create one scene object called `AudioRuntime` and add:

1. `AudioService`
   - assign the production `AudioCatalog`
   - leave one-shot pool at 24 for the Quest 2 baseline
2. `AudioAmbienceController`
   - assign `AMB_Beach_Day` as the initial profile for the prototype beach scene
   - start with 4 second crossfades
3. Child object `WorldFauna`
   - add one or more `AudioRandomEmitter` components
   - reference the scene `AudioService`

Do not use `DontDestroyOnLoad` or convert these components into global singletons. A scene/bootstrap composition root should own them.

## Recommended ambience profiles

Create these ScriptableObjects first:

### AMB_Beach_Day

- `SFX_AMB_Beach_OceanNear` — gain 1.00
- `SFX_AMB_Beach_CoastalWind` — gain 0.55
- `SFX_AMB_Beach_PalmCanopy` — gain 0.30

### AMB_Jungle_Day

- `SFX_AMB_Jungle_DayBed` — gain 0.90
- `SFX_AMB_Jungle_CanopyWind` — gain 0.35
- `SFX_AMB_Jungle_DeepBed` — gain 0.25

### AMB_Jungle_Night

- `SFX_AMB_Jungle_NightBed` — gain 1.00
- `SFX_AMB_Jungle_DeepBed` — gain 0.30

### AMB_Shelter_Calm

- `SFX_AMB_Shelter_Calm` — gain 1.00
- optionally retain a low exterior ocean/jungle bed at gain 0.15–0.25

### AMB_Shelter_Windy

- `SFX_AMB_Shelter_Windy` — gain 1.00
- exterior wind bed — gain 0.30–0.45
- use a physical `AudioLoopEmitter` for `SFX_WTH_Rain_OnTarp` when rain is active

Storm phase ambience should be driven by gameplay/weather state rather than only by trigger zones.

## World emitters

Useful starting configurations:

- Shoreline: `SFX_AMB_Shore_Wash`, delay 3–9 s, radius 8 m.
- Beach fauna: `SFX_NAT_Bird_ShoreCall`, delay 9–24 s, radius 16 m.
- Jungle fauna: bird/cicada/frog events, separate emitters with different delay ranges.
- Threat suggestion: `SFX_NAT_Animal_RustleNear`, `BranchSnapFar`, `ScrapeFar`, sparse 15–45 s delays.
- Campfire: `SFX_ENV_Fire_Pop`, delay 1.5–6 s, radius 0.4 m on top of the persistent fire loop.
- Storm: `SFX_WTH_Storm_WindGust`, delay 4–13 s, radius 12 m.

Avoid synchronising emitters. Their independent random clocks are part of the anti-repetition strategy.

## Footsteps in VR

Attach `FootstepAudioEmitter` to the locomotion rig and set `movementReference` to the rig/root that translates through the world, not to a controller hand.

Recommended prototype values:

- step distance: 0.72 m
- minimum speed: 0.15 m/s
- teleport reset: 2.5 m
- ray start height: 0.35 m
- ray distance: 1.6 m

Add `AudioSurfaceTag` to walkable colliders or their parents. Supported baseline surfaces are dry sand, wet sand, dirt, rock, wood, leaves and shallow water.

If the final locomotion system exposes authoritative step timing, disable `driveFromDistance` and call `EmitStep()` directly instead.

## Quest profile

Baseline:

- 48 kHz source WAV.
- Mono for local 3D one-shots and emitters.
- Stereo for non-spatial beds/music.
- Long ambience/music loops: Vorbis + Streaming.
- Short repeated SFX: ADPCM + Decompress On Load.
- Pool size begins at 24 one-shots and must be profiled on Quest 2 before increasing.
- No convolution reverb or expensive runtime DSP in the baseline profile.
- Prefer world-space source placement over expensive effect processing to sell depth.

## First playable audio acceptance check

A first playable passes the audio layer when all of these are true:

- moving from beach to jungle produces a smooth ambience transition with no hard cut
- entering/exiting the shelter changes the acoustic bed coherently
- footsteps audibly change on at least sand, wood and shallow water
- campfire has a stable loop plus non-synchronised pops
- fauna one-shots are spatial and do not repeat at a visibly fixed cadence
- storm can layer wind, rough ocean, rain and tarp rain without clipping the master bus
- disabling or missing an individual audio event fails silently rather than breaking gameplay

## Status

Runtime architecture, production manifest, biome crossfades, randomized world emitters and surface footsteps are implemented. Final mastered recordings remain `production-needed`; no placeholder clip is represented as production audio.
