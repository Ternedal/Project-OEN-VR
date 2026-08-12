# Project ØEN — Active-scene audio install, WorldFauna and WorldWeather

## Goal

The first-playable audio lane should move from imported WAV files to a usable scene runtime without manual duplication, hidden global lookup, or spatial emitters stuck at world origin.

Primary command:

`Project Oen > Audio > Build + Install First Playable (One Click)`

This command first runs the existing first-playable asset builder and then installs/configures the generated runtime in the active saved scene.

## Scene ownership rules

The installer fails closed when any of these are true:

- the Editor is entering or already in Play Mode;
- the Editor is in Prefab Mode;
- there is no valid loaded active scene;
- the active scene has not been saved yet;
- fewer than the stable minimum baseline of 160 canonical clips / 45 events are imported;
- the generated runtime prefab is missing;
- more than one `AudioService` already exists in the active scene;
- one existing `AudioService` exists but is not owned by the generated first-playable prefab.

The current CI-built pack may contain more than the minimum baseline. The installer uses the stable minimum as a fail-closed compatibility floor rather than forcing Editor code changes every time a reviewed candidate adds coverage.

It never creates a second audio runtime beside an existing manual runtime.

The installer marks the scene dirty after a successful install/update but deliberately does **not** save it. Scene save remains an explicit user/editor action.

## Generated scene runtime

The generated prefab remains:

`Assets/ProjectOen/Audio/GeneratedFirstPlayable/Runtime/AudioRuntime_FirstPlayable.prefab`

The scene installer keeps the prefab connection by using Unity's prefab-instantiation path for the destination scene. It then applies scene-specific overrides that cannot live in the prefab asset itself.

The expected active-scene composition contains:

- one `AudioService`;
- one `AudioWorldStateRouter`;
- three ambience controllers from the generated prefab;
- `WorldFauna` with listener-relative anchor, state router and random emitter;
- `WorldWeather` with listener-relative anchor, state router and random emitter.

Use:

`Project Oen > Audio > Audit Active Scene Audio Runtime`

to inspect this contract after installation.

## Listener-relative world emitters

Spatial intermittent fauna and weather transients should surround the player, not the static audio-runtime origin. The scene installer therefore finds active `AudioListener` components inside the active scene.

When exactly one active listener exists:

- both `AudioWorldAnchorFollower` components are explicitly assigned that listener transform;
- the followers track horizontal listener movement;
- `WorldFauna` and `WorldWeather` are enabled.

When zero or multiple active listeners exist:

- no listener is guessed;
- both listener-relative roots are disabled;
- the installer logs warnings;
- rerunning the installer after listener ownership is fixed rebinds and re-enables them.

`AudioWorldAnchorFollower` never performs global runtime searches (`Camera.main`, `FindFirstObjectByType`, etc.). Scene composition owns the references.

## State-aware fauna lane

The first real available spatial nature event is:

`SFX_NAT_Insect_CicadaCluster`

The scene installer creates/configures:

`WorldFauna/JungleDay_Cicadas`

Baseline behavior:

- biome: `Jungle`;
- day phase: `Day`;
- storm phase: `Calm`;
- exterior only;
- randomized cadence: 14–34 seconds;
- horizontal emission radius: 18 m around the listener-relative anchor;
- vertical jitter: 2.5 m;
- `playOnEnable = false` because lifecycle ownership belongs to `AudioWorldStateEmitterRouter`.

The four cicada source variations remain selected centrally by `AudioService` / `AudioEventDefinition`; the scene emitter references the event ID, not individual clips.

A Jungle Day fauna emitter should not continue unchanged through the storm. The cicada binding resolves only to `Calm`; Wind, RainFire and Signal stop it automatically.

## State-aware distant thunder lane

The pinned Public Domain `Tonitrus.ogg` source adds three current `SFX_WTH_Thunder_Far` candidate variations to the environmental pack. They remain `candidate-headset-listen` until physical listening approval.

The scene installer creates/configures:

`WorldWeather/RainFire_ThunderFar`

Baseline behavior:

- biome-independent;
- day/night-independent;
- storm phase: `RainFire`;
- exterior only;
- randomized cadence: 18–42 seconds;
- horizontal emission radius: 32 m around the listener-relative anchor;
- vertical jitter: 10 m;
- `playOnEnable = false`.

This deliberately avoids firing distant thunder in Calm/Wind or while the player is sheltered. Signal currently stops this first-pass random-thunder lane rather than assuming the final finale mix should retain the same cadence.

`AudioWorldStateEmitterRouter` supports optional biome/day matching plus an explicit storm phase. This allows fauna to be location-specific while weather transients can be biome-independent without duplicating simulation state.

## Runtime lifecycle

`AudioWorldStateRouter.StateChanged` notifies dependent `AudioWorldStateEmitterRouter` components whenever biome, day phase, storm phase or shelter state changes.

`AudioWorldStateEmitterRouter` starts/stops intermittent emitters only while `Application.isPlaying`. Edit-mode installation/configuration therefore cannot accidentally start `AudioRandomEmitter` coroutines.

## Non-destructive reruns

The high-level workflow preserves the existing generated profile/prefab assets produced by the first-playable builder. Scene installation is idempotent with respect to runtime ownership:

- if no generated runtime exists in the scene, it instantiates one;
- if exactly one generated runtime already exists, it reuses it and refreshes scene-specific WorldFauna/WorldWeather wiring;
- if another/manual audio runtime owns the scene, it stops rather than overwriting it.

## Manual acceptance sequence

After importing the current Unity pack and running Build + Install in a saved gameplay scene:

1. confirm there is exactly one active `AudioListener` and one `AudioService`;
2. confirm both `WorldFauna` and `WorldWeather` are enabled and their followers reference the listener;
3. enter Play Mode in Beach/Calm and confirm cicadas are inactive;
4. switch to Jungle/Day/Calm and confirm cicadas can emit around the listener;
5. switch to Wind and confirm cicadas stop;
6. switch to RainFire outdoors and confirm distant thunder can emit while cicadas remain stopped;
7. set sheltered state and confirm the thunder emitter stops;
8. return to exterior and verify state routing resumes without creating duplicate coroutines or runtime objects;
9. perform headset listening and Quest 2 profiling before promoting the candidates.

## Current verification boundary

CI statically validates serialized field names, menu contract, duplicate-service guard, stable minimum coverage guard, Play/Prefab Mode guards, explicit listener ownership, no auto-save behavior, cicada and RainFire thunder state mappings, edit-mode coroutine protection, and world-state notification wiring.

This does **not** claim that Unity 6000.4.10f1 has physically imported/compiled the scripts or that the generated scene instance has been listened to in Quest 2. Those remain physical production gates.
