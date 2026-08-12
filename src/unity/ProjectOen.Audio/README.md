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
- `AudioLoopEmitter`: runtime-switchable scene component for persistent physical emitters such as campfire and rain-on-tarp.
- `AudioAmbienceProfile`: layered ambience definition for a biome/state such as beach day, jungle night or shelter windy.
- `AudioAmbienceController`: two-bank ambience player that crossfades profiles without hard cuts.
- `AudioAmbienceZone`: trigger volume for biome, shelter and location transitions.
- `AudioRandomEmitter`: intermittent spatial one-shots for fauna, fire pops, shoreline washes, branch snaps and gusts; cadence can be adjusted at runtime.
- `AudioSurfaceTag`: material marker for walkable colliders.
- `FootstepAudioEmitter`: Quest-friendly distance-driven footsteps with ground probing and surface-specific events.
- `AudioWorldStateRouter`: separates biome/day-night ambience from weather/storm ambience and selects mixer snapshots.
- `AudioFireStateEmitter`: maps fire intensity and fire interactions to low/burning loops, pops, ignition, wood-add and extinguish events.
- `AudioTarpWeatherEmitter`: maps normalized wind/rain to local flap cadence and rain-on-tarp gain.

Gameplay code depends on `IAudioService`, not concrete clip paths.

## Minimum scene setup

Create one scene object called `AudioRuntime` and add:

1. `AudioService`
   - assign the production `AudioCatalog`
   - leave one-shot pool at 24 for the Quest 2 baseline
2. two `AudioAmbienceController` components or child objects
   - `BiomeAmbience` for location/day-night beds
   - `WeatherAmbience` for storm/weather beds
3. `AudioWorldStateRouter`
   - wire both ambience controllers
   - assign biome day/night profiles
   - assign four storm bindings: Calm, Wind, RainFire, Signal
4. child object `WorldFauna`
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
- use the physical tarp emitter for `SFX_WTH_Rain_OnTarp` when rain is active

Storm phase ambience is driven by gameplay/weather state rather than only by trigger zones.

## World-state routing

`AudioWorldStateRouter` mirrors the small set of audio-relevant world states instead of owning simulation state.

### Biome/day layer

Use `SetBiome()` and `SetDayPhase()` from the authoritative world/phase system. The router crossfades only the biome controller.

Baseline mappings:

- Beach + Day -> `AMB_Beach_Day`
- Beach + Night -> `AMB_Beach_Night`
- Jungle + Day -> `AMB_Jungle_Day`
- Jungle + Night -> `AMB_Jungle_Night`
- Ridge + Day/Night -> ridge variants
- `SetSheltered(true)` overrides the exterior profile with shelter day/night while retaining the exterior biome for exit

### Storm layer

Release-1 storm progression is represented as:

1. `Calm`
2. `Wind`
3. `RainFire`
4. `Signal`

Each phase has its own weather `AudioAmbienceProfile` plus optional exterior/sheltered `AudioMixerSnapshot` references. Keep Calm wired to an empty or near-silent weather profile so the weather layer can crossfade back to silence cleanly.

Suggested mixer snapshots:

- `MX_CalmExterior`
- `MX_CalmShelter`
- `MX_StormWindExterior`
- `MX_StormWindShelter`
- `MX_StormRainExterior`
- `MX_StormRainShelter`
- `MX_StormSignalExterior`
- `MX_StormSignalShelter`

The shelter snapshots should primarily rebalance/muffle exterior ambience rather than add expensive DSP. Quest 2 remains the baseline.

## Campfire integration

Put `AudioFireStateEmitter` on the campfire root and wire:

- `AudioLoopEmitter` -> persistent fire loop source
- `AudioRandomEmitter` -> `SFX_ENV_Fire_Pop`
- low definition -> `SFX_ENV_Fire_Low`
- burning definition -> `SFX_ENV_Fire_Idle`

Gameplay integration surface:

- `SetBurnIntensity(0..1)` for authoritative continuous fire state
- `OnIgnited()` after successful ignition
- `OnWoodAdded()` when fuel is added
- `OnExtinguished()` when the fire is put out by player action/weather

The emitter automatically slows fire pops in the Low state and stops all persistent fire audio when Off.

## Tarp/weather integration

Put `AudioTarpWeatherEmitter` on the shelter/tarp root and wire:

- `AudioLoopEmitter` -> `SFX_WTH_Rain_OnTarp`
- `AudioRandomEmitter` -> `SFX_ENV_Tarp_Flap`

Call `SetWeather(wind01, rain01)` from the authoritative weather/storm system. Wind increases flap frequency; rain controls the local rain-on-tarp gain. Use `OnTarpHandled()` and `OnTensionChanged()` for direct player interactions.

This local emitter is deliberately separate from the broad 2D weather bed so the player can hear where the shelter physically is in VR.

## World emitters

Useful starting configurations:

- Shoreline: `SFX_AMB_Shore_Wash`, delay 3–9 s, radius 8 m.
- Beach fauna: `SFX_NAT_Bird_ShoreCall`, delay 9–24 s, radius 16 m.
- Jungle fauna: bird/cicada/frog events, separate emitters with different delay ranges.
- Threat suggestion: `SFX_NAT_Animal_RustleNear`, `BranchSnapFar`, `ScrapeFar`, sparse 15–45 s delays.
- Campfire: `SFX_ENV_Fire_Pop`, runtime cadence 3–8 s when burning and 8–16 s when low.
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

## Canonical player statuses

Audio follows the same canonical player-status vocabulary as the production art direction:

- Health
- Fatigue
- Injury
- Cold/Wet

`SFX_STS_Injury_Warn` and `SFX_STS_ColdWet_Warn` retain numeric values 1100/1101. The original Hunger/Thirst enum names remain only as obsolete compatibility aliases until the production-manifest row labels are regenerated; new gameplay code must not use them.

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
- day/night changes replace the relevant biome bed without restarting unrelated weather layers
- entering/exiting the shelter changes the acoustic bed and mixer balance coherently
- footsteps audibly change on at least sand, wood and shallow water
- campfire follows Off/Low/Burning state and has non-synchronised pops
- tarp flap cadence increases with wind and rain-on-tarp gain follows rain intensity
- fauna one-shots are spatial and do not repeat at a visibly fixed cadence
- storm phases can progress Calm -> Wind -> RainFire -> Signal without hard-cutting biome ambience
- storm can layer wind, rough ocean, rain and tarp rain without clipping the master bus
- disabling or missing an individual audio event fails silently rather than breaking gameplay

## Status

Runtime architecture, production manifest, biome/day-night and storm routing, mixer-snapshot routing, campfire/tarp state adapters, randomized world emitters and surface footsteps are implemented. Final mastered recordings remain `production-needed`; no placeholder clip is represented as production audio.
