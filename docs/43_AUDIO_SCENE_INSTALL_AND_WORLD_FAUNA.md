# Project ØEN — Active-scene audio install, WorldFauna and WorldWeather

## Goal

The first-playable audio lane should move from a **verified current staged artifact** to a usable scene runtime without manual duplication, hidden global lookup, stale generated state or spatial emitters stuck at world origin.

Primary command:

`Project Oen > Audio > Build + Install First Playable (One Click)`

This command runs the first-playable asset builder and then installs/configures the generated runtime in the active saved scene.

A lower-level direct install remains available:

`Project Oen > Audio > Install First-Playable Runtime Into Active Scene`

It does **not** bypass integrity checks: the direct path independently verifies the staged manifest/import and catalog parity before mutating the scene.

## Scene ownership and integrity rules

The installer fails closed when any of these are true:

- the Editor is entering or already in Play Mode;
- the Editor is in Prefab Mode;
- there is no valid loaded active scene;
- the active scene has not been saved yet;
- `FIRST_PLAYABLE_MANIFEST.csv` is absent/invalid;
- a manifested WAV is missing, changed, not imported or has a SHA-256/byte-count mismatch;
- an extra canonical WAV exists in `Assets/ProjectOen/Audio` outside the current manifest;
- fewer than the stable minimum baseline of 160 verified canonical clips / 45 events are present;
- `AudioCatalog.asset` is missing or its event count differs from the verified current manifest;
- the generated runtime prefab is missing;
- more than one `AudioService` already exists in the active scene;
- one existing `AudioService` exists but is not owned by the generated first-playable prefab.

The current CI-built pack contains **173 WAV / 47 events**. The 160/45 number is a stable compatibility floor; exact current staged membership is still controlled by the manifest and hash checks.

The installer never creates a second audio runtime beside an existing manual runtime.

It marks the scene dirty after a successful install/update but deliberately does **not** save it. Scene save remains an explicit user/editor action after audit/listening.

## Generated scene runtime

The generated prefab remains:

`Assets/ProjectOen/Audio/GeneratedFirstPlayable/Runtime/AudioRuntime_FirstPlayable.prefab`

The scene installer keeps the prefab connection by using Unity's prefab-instantiation path for the destination scene. It then applies scene-specific overrides that cannot live in the prefab asset itself.

The expected active-scene composition contains:

- exactly one `AudioService` owned by the generated prefab instance;
- exactly one `AudioWorldStateRouter`;
- three ambience controllers from the generated prefab;
- `WorldFauna` with listener-relative anchor, state router and random emitter;
- `WorldWeather` with listener-relative anchor, state router and random emitter;
- exactly one active scene `AudioListener` before the world-relative lane is accepted.

Use:

`Project Oen > Audio > Audit Active Scene Audio Runtime`

after installation.

The audit is now fail-closed: ambiguous listener ownership is `FAILED`, not a warning that can still result in overall `OK`.

## Listener-relative world emitters

Spatial intermittent fauna and weather transients should surround the player, not the static audio-runtime origin. The scene installer therefore finds active `AudioListener` components inside the active scene.

When exactly one active listener exists:

- both `AudioWorldAnchorFollower` components are explicitly assigned that listener transform;
- both bound roots must be active for scene audit success;
- followers track horizontal listener movement;
- `WorldFauna` and `WorldWeather` are enabled.

When zero or multiple active listeners exist:

- no listener is guessed;
- both listener-relative roots are disabled;
- the installer logs the ownership problem;
- the active-scene audit fails;
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

The pinned Public Domain thunder source contributes three current `SFX_WTH_Thunder_Far` candidate variations to the environmental pack. They remain `candidate-headset-listen` until physical listening approval.

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

## Reruns

Reruns have explicit ownership semantics:

- the current staged WAV payload is revalidated by manifest/hash before mutation;
- definition clip membership and catalog membership are synchronized to the current verified artifact;
- generated profile membership is synchronized while gains for still-valid layers are preserved;
- the generated runtime prefab asset itself is preserved if it already exists;
- if no generated runtime exists in the active scene, one is instantiated;
- if exactly one generated runtime already exists, it is reused and scene-specific WorldFauna/WorldWeather wiring is refreshed;
- if another/manual audio runtime owns the scene, installation stops rather than overwriting it.

This prevents both stale first-playable assets and duplicate scene ownership while retaining deliberate designer tuning.

## Manual acceptance sequence

After importing the current Unity pack and running Build + Install in a saved gameplay scene:

1. require the first-playable manifest/import audit to pass;
2. require `AudioCatalog.asset` event count to match the current manifest;
3. confirm there is exactly one active `AudioListener` and exactly one generated-prefab-owned `AudioService`;
4. confirm both `WorldFauna` and `WorldWeather` are enabled and their followers reference the listener;
5. run `Project Oen > Audio > Audit Active Scene Audio Runtime` and require `status=OK`;
6. enter Play Mode in Beach/Calm and confirm cicadas are inactive;
7. switch to Jungle/Day/Calm and confirm cicadas can emit around the listener;
8. switch to Wind and confirm cicadas stop;
9. switch to RainFire outdoors and confirm distant thunder can emit while cicadas remain stopped;
10. set sheltered state and confirm the thunder emitter stops;
11. return to exterior and verify state routing resumes without duplicate coroutines or runtime objects;
12. run the full ambience/storm transition set and listen for stale beds, abrupt cuts, phasing and loop seams;
13. perform Quest 2 headset listening and performance profiling before candidate promotion/merge acceptance.

## Current verification boundary

CI statically validates:

- serialized field names and numeric enum handling;
- manifest/SHA integrity gate presence;
- stale-definition cleanup and catalog membership ownership;
- generated-profile synchronization;
- duplicate-service/manual-runtime guards;
- stable minimum coverage guard;
- Play/Prefab Mode and saved-scene guards;
- catalog/manifest parity;
- explicit single-listener ownership and active listener-bound anchors;
- no auto-save behavior;
- cicada and RainFire thunder state mappings;
- edit-mode coroutine protection;
- world-state notification wiring.

This does **not** claim Unity 6000.4.10f1 has physically imported/compiled the scripts or that the generated scene has been listened to/profiled on Quest 2. Those are the remaining physical gates, not missing software implementation.
