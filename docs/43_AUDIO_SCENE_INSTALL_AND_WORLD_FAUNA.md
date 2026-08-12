# Project ØEN — Active-scene audio install and WorldFauna

## Goal

The first-playable audio lane should move from imported WAV files to a usable scene runtime without manual duplication, hidden global lookup, or a prefab that emits spatial ambience from world origin.

Primary command:

`Project Oen > Audio > Build + Install First Playable (One Click)`

This command first runs the existing first-playable asset builder and then installs/configures the generated runtime in the active saved scene.

## Scene ownership rules

The installer fails closed when any of these are true:

- the Editor is in Prefab Mode;
- there is no valid loaded active scene;
- the active scene has not been saved yet;
- fewer than 160 canonical first-playable clips / 45 events are imported;
- the generated runtime prefab is missing;
- more than one `AudioService` already exists in the active scene;
- one existing `AudioService` exists but is not owned by the generated first-playable prefab.

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
- `WorldFauna`;
- `AudioWorldAnchorFollower` on `WorldFauna`;
- `AudioWorldStateEmitterRouter` on `WorldFauna`;
- at least one state-aware `AudioRandomEmitter`.

Use:

`Project Oen > Audio > Audit Active Scene Audio Runtime`

to inspect this contract after installation.

## Listener-relative WorldFauna

Spatial intermittent fauna should surround the player, not the static audio-runtime origin. The scene installer therefore finds active `AudioListener` components inside the active scene.

When exactly one active listener exists:

- `AudioWorldAnchorFollower` is explicitly assigned that listener transform;
- the follower tracks horizontal listener movement;
- `WorldFauna` is enabled.

When zero or multiple active listeners exist:

- no listener is guessed;
- `WorldFauna` is disabled;
- the installer logs a warning;
- rerunning the installer after listener ownership is fixed rebinds and re-enables the fauna root.

`AudioWorldAnchorFollower` never performs global runtime searches (`Camera.main`, `FindFirstObjectByType`, etc.). Scene composition owns the reference.

## First state-aware fauna lane

The first real available spatial nature event in the 160-WAV first-playable pack is:

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

When biome/day/storm/shelter state changes, `AudioWorldStateRouter.StateChanged` notifies `AudioWorldStateEmitterRouter`, which starts or stops the intermittent emitter. This avoids polling and keeps the authoritative gameplay/world state outside the audio subsystem.

## Why storm phase is explicit

A Jungle Day fauna emitter should not continue unchanged through the storm finale. Each WorldFauna binding therefore has an explicit `AudioStormPhase` match. The first cicada binding resolves to `Calm`; Wind, RainFire and Signal stop the emitter.

Future bird/frog/animal emitters should get their own state bindings rather than being globally active by default.

## Non-destructive reruns

The high-level workflow preserves the existing generated profile/prefab assets produced by the first-playable builder. Scene installation is idempotent with respect to runtime ownership:

- if no generated runtime exists in the scene, it instantiates one;
- if exactly one generated runtime already exists, it reuses it and refreshes scene-specific WorldFauna wiring;
- if another/manual audio runtime owns the scene, it stops rather than overwriting it.

## Current verification boundary

CI statically validates the serialized field names, menu contract, duplicate-service guard, 160/45 coverage guard, explicit listener ownership, no auto-save behavior, cicada state mapping, and world-state notification wiring.

This does **not** claim that Unity 6000.4.10f1 has physically imported/compiled the scripts or that the generated scene instance has been listened to in Quest 2. Those remain physical production gates.
