# Project ØEN — Foley production and Unity binding

Status: implementation-ready production contract. Actual recordings remain `recording-needed` until captured, edited, listened to and approved.

## 1. Scope

The dedicated Foley plan is `content/audio/foley_recording_plan.csv`.

It covers 40 physical events / 388 planned source variations:

- tarp: flap, handle, tension;
- rope: handle, tighten, creak, tension release;
- wood: pickup, drop, hit, break, chop;
- stone: pickup, drop, hit;
- leaves;
- water: small splash, large splash, pour;
- containers and crates;
- metal scrape/impact;
- all seven footstep surfaces;
- land, wade, swim, cloth and hand contact.

The plan intentionally specifies props, performance, microphone distance, take strategy and post rules. A count such as “12 wood hits” is not sufficient production direction by itself.

## 2. Runtime binding model

Do not reference individual AudioClips from gameplay prefabs.

Use:

1. `AudioFoleyProfile` — ScriptableObject mapping semantic actions to stable `AudioEventId` values;
2. `AudioFoleyEmitter` — scene/prefab bridge that resolves an action through the profile and asks the scene-owned `AudioService` to play it;
3. `AudioEventDefinition` — owns the variation pool and playback/spatial settings;
4. `AudioCatalog` — scene-level collection of definitions.

This keeps gameplay semantics independent from recordings and variation counts.

Example: a wooden resource prefab emits `AudioFoleyAction.Drop`; its Wood profile maps that to `SFX_ENV_Wood_Drop`; the definition chooses one of the approved Wood_Drop clips.

## 3. Default Foley profiles

In Unity run:

`Project Oen > Audio > Rebuild Default Foley Profiles`

This creates/updates assets under:

`Assets/ProjectOen/Audio/FoleyProfiles/`

Nine profiles are generated:

- Tarp
- Rope
- Wood
- Stone
- Water
- Container
- Crate
- Metal
- Fire

The generated profiles contain typed event mappings only. They do not contain AudioClips.

## 4. Prefab wiring

For an interactable object:

1. add `AudioFoleyEmitter`;
2. assign the scene-owned `AudioService`;
3. assign the relevant `AudioFoleyProfile`;
4. optionally assign a child transform as the emission point;
5. call the semantic method from the interaction/build system.

Inspector/UnityEvent-friendly parameterless methods include:

- `EmitPickup`
- `EmitDrop`
- `EmitImpact`
- `EmitHandle`
- `EmitOpen` / `EmitClose`
- `EmitTighten`
- `EmitCreak`
- `EmitTension` / `EmitTensionRelease`
- `EmitBreak` / `EmitChop`
- `EmitScrape`
- `EmitPour`
- `EmitSplashSmall` / `EmitSplashLarge`
- `EmitFlap`
- `EmitIgnite` / `EmitExtinguish` / `EmitAddFuel`

Code integrations can use `TryEmit(AudioFoleyAction)` or `TryEmitAt(...)`.

Missing service/profile/action mappings return false and must not stop gameplay.

## 5. Footsteps

Footsteps remain a specialized path because they are locomotion-driven rather than object-interaction-driven.

Use `AudioSurfaceTag` on walkable colliders/parents with one of:

- SandDry
- SandWet
- Dirt
- Rock
- Wood
- Leaves
- ShallowWater

`FootstepAudioEmitter` resolves the surface with a short downward ray and maps it to the matching typed event. Quest locomotion should continue to use movement distance rather than animation timing as the default driver.

## 6. Catalog population and audit

After approved clips have been imported and assigned to `AudioEventDefinition` assets:

1. select the `AudioCatalog` asset;
2. run `Project Oen > Audio > Rebuild Selected Audio Catalog`;
3. run `Project Oen > Audio > Audit Audio Event Definitions`.

The editor audit checks:

- `AudioEventId.None` definitions;
- duplicate typed IDs;
- empty/null clip arrays when rebuilding;
- duplicate clip references;
- clip names that do not start with the typed event ID.

The catalog builder sorts definitions by stable numeric event ID before writing the catalog.

No mutable runtime lookup is stored on the ScriptableObject; the scene-owned `AudioService` continues to build runtime lookup state during `Awake`.

## 7. Recording acceptance

A Foley variation is not production-ready merely because a WAV exists.

Before promotion from `recording-needed`:

- original recording must be lossless and preserved;
- edited derivative must be 48 kHz / 24-bit PCM WAV;
- transient must not clip;
- no speech, handling contamination, obvious room artefacts or irrelevant prop character;
- variation must be materially different from the other takes, not only pitch-shifted;
- perceived level must be consistent inside the event pool;
- harsh stone/metal transients must be checked in Quest headphones/headset speakers;
- all imported clips must pass event-definition/catalog audit;
- representative interactions must be listened to in the actual scene.

Do not promote synthetic placeholders or web previews as Foley masters.

## 8. Recording order

Recommended session order:

1. Wood + Stone — high gameplay frequency and useful for interaction tuning.
2. Footsteps — seven surfaces, highest repetition risk.
3. Tarp + Rope — key shelter identity and storm readability.
4. Water — shallow-water locomotion and survival interactions.
5. Containers + Crates + Metal — camp/resource handling.
6. Player cloth/hands/landing — subtle layer added only after object Foley is balanced.

Record substantially more takes than the final manifest count. The variation count is the selected delivery target, not the number of times the prop should be performed.

## 9. Validation

Repo-side check:

`python tools/validate_foley_recording_plan.py`

Expected result:

`Foley recording-plan validation OK: 40 events / 388 planned variations`

This validator compares every Foley event and variation count against `audio_asset_manifest.csv`.

Unity compilation, imported-asset audit, scene listening and Quest 2 profiling remain authoritative runtime gates.
