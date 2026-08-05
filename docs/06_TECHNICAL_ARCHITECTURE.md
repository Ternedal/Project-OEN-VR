# Teknisk arkitektur

## 1. Arkitekturmål

- Én kodebase for Quest 2/3.
- Platformforskelle isoleres i buildprofiler og adapters.
- Gameplay-state er data-drevet og kan testes uden headset, hvor det er muligt.
- Netværk må ikke være dybt flettet ind i alle gameplayklasser.
- Scenarioet skal kunne køres deterministisk nok til reproducerbar QA.
- Ingen stor framework-suppe. Få tydelige moduler og explicit dependencies.

## 2. Foreslået stack

| Lag | Teknologi | Status |
|---|---|---|
| Engine | Unity 6 LTS 6000.3.x, endelig patch låses efter M0 | Foreslået (ADR-020) |
| Render | URP med Render Graph, Vulkan | Foreslået |
| XR runtime | OpenXR via Unity OpenXR Plugin | Foreslået (ADR-020) |
| Interaktion | XR Interaction Toolkit 3.x | Foreslået |
| Input | Unity Input System | Foreslået |
| Multiplayer | Photon Fusion 2.1 Shared Mode | Foreslået (kræver Realtime 5) |
| Content | ScriptableObjects + JSON schema/export | Accepteret retning |
| Scene loading | Addressables/additive scenes, lokalt content i gaveversion | Foreslået |
| Tests | Unity Test Framework + PlayMode integration + fysisk device suite | Foreslået |
| CI | GitHub Actions til validering; Windows self-hosted runner til Unity builds hvis nødvendigt | Foreslået |

## 3. Platformspike M0

Før stacken betragtes som låst, bygges et minimalt projekt med:

- XR Origin.
- Controller tracking.
- Grab af én kube.
- Photon lobby/join code.
- Head/hand replication.
- Shared ownership af én tung kasse.
- BuildInfo og compatibility hash.

Det installeres fysisk på Quest 2 og Quest 3. Med ADR-019 er Quest 1-lanen bortfaldet, og der er derfor kun én package lock. To-manifest-forken (`modern`/`legacy-q1`) er udgået.

### Verifikationsgate for engine-baseline (ADR-020)

Skal bestås inden for M0's første ca. 8 timer, før resten af spiket fortsætter:

1. Tomt Unity 6000.3.x-projekt med URP, Android/Vulkan, bygger og kører på Quest 2.
2. XRI 3.x XR Origin-rig med grab, teleport og snap turn fungerer på device.
3. Photon Fusion 2.1 importeret med Asset Serialization = Force Text; to klienter forbinder i Shared Mode.
4. Tom scene holder 72 Hz stabilt på Quest 2.

Fejler gaten, falder valget til Unity 6000.0.x LTS. Kun ved dobbelt fejl overvejes 2022.3.45 som eksplicit accepteret teknisk gæld.

## 4. Modulopdeling

### `ProjectOen.Core`

- IDs, result types, clocks, random seed abstraction.
- Ingen Unity sceneafhængighed hvor muligt.

### `ProjectOen.Gameplay`

- ScenarioDirector.
- Phase state machine.
- Resource, player og camp state.
- Actions, events, consequences.
- Win/lose evaluation.

### `ProjectOen.Interaction`

- Grab, snap, two-hand stabilisation.
- Interaction steps og quality scoring.
- Haptics/feedback adapters.

### `ProjectOen.Networking`

- Session lifecycle.
- Network player rig.
- Authority requests.
- Replicated gameplay commands/state.
- Reconnect and compatibility.

### `ProjectOen.Platform`

- Device detection.
- Quality profile.
- Refresh rate.
- Feature flags.
- Build/channel metadata.

### `ProjectOen.Persistence`

- Save snapshots.
- Migration.
- Atomic write and validation.

### `ProjectOen.Content`

- ScriptableObject definitions.
- Validators.
- Localization keys.
- Personalization loader.

### `ProjectOen.UI`

- Diegetic status.
- Menus and accessibility.
- Debug panels behind development flag.

### `ProjectOen.Tests`

- EditMode, PlayMode and scenario simulations.

## 5. State machine

Top-level states:

- Boot
- PlatformValidation
- Lobby
- Calibration
- LoadingScenario
- Playing
- PausedForReconnect
- Results
- FatalError

Scenario states:

- Intro
- Dawn
- Planning
- ResolvePlan
- ActionSequence
- Dusk
- Night
- Storm
- Signal
- Epilogue

Kun `ScenarioDirector` må skifte scenariofase. Andre systemer sender commands/events.

## 6. Command/event pattern

Eksempler:

- `PlaceEffortMarkerCommand`
- `ConfirmPlanCommand`
- `BeginActionCommand`
- `CompleteInteractionStepCommand`
- `ApplyResourceDeltaCommand`
- `ScheduleDelayedEventCommand`

Domæneevents:

- `PlanLocked`
- `ActionResolved`
- `InjuryApplied`
- `CampTagAdded`
- `DelayedEventTriggered`
- `CheckpointCreated`

Commands valideres af authority. Events bruges til UI, audio, telemetry og save journal.

## 7. Data ownership

- `SessionState`: Photon/session-lag.
- `ScenarioState`: autoritativ delt gameplaystate.
- `PlayerState`: authority for logiske statusværdier, ikke rå pose.
- `PoseState`: hver klient har authority over eget head/hands.
- `InteractableState`: authority skifter efter definerede regler.
- `CosmeticState`: lokal eller derived, replikeres ikke medmindre nødvendigt.

## 8. Fysikstrategi

Rå netværksfysik begrænses. Fysiske sekvenser modelleres som:

- Lokal håndpose og visuel feedback.
- Netværket sender targets, greb-state og quality samples.
- En autoritativ state machine afgør resultatet.
- Tunge fælles objekter bruger kinematic target solving og stabiliserede constraints.
- Destruktion og kollaps afspilles som synkroniserede sekvenser, ikke fuldt emergent rigidbody-kaos.

## 9. Save-model

Checkpoint er et immutable snapshot med:

- schema version.
- build compatibility hash.
- scenario ID/version/seed.
- current phase.
- player/camp/resources.
- completed actions.
- event queue og tags.
- spawned persistent object states.
- personalization profile ID, ikke private assetdata.

Write flow:

1. Serialize til temp-fil.
2. Validate checksum.
3. Rename atomisk til active save.
4. Behold forrige checkpoint som backup.

## 10. Scene- og contentstrategi

- Boot og lobby er små selvstændige scener.
- Camp er persistent under scenarioet.
- Action-zoner indlæses additivt.
- Maksimalt camp + én fuld action-zone resident på Quest 2.
- Addressables bruges primært til lokal organisering og loading; remote content er uden for gaveversionen.
- Shared assets har LOD0-2.

## 11. Dependency rules

- Gameplay må ikke referere direkte til Photon-klasser.
- Platform-lag må ikke indeholde scenarielogik.
- UI læser view models/events, ikke ScriptableObjects direkte under runtime.
- Content definitions er immutable i runtime.
- Ingen global singleton med skjult scene-state. En lille bootstrap/service registry er acceptabel.

## 12. Debuggability

Development build viser:

- build/profile/device.
- current phase and seed.
- Photon region/ping/session.
- authority owner per selected object.
- resource/camp/player state.
- event queue.
- frame timing and memory watermark.

En `DebugScenarioConsole` kan springe til dag/fase, injicere event-tags og tvinge save/reconnect.

## 13. Security/privacy

- Photon App ID og ikke-hemmelige client settings må ligge i build; service secrets må ikke.
- Personlige billeder/lyd ligger uden for public repo.
- Logs må ikke indeholde navne, fri voice eller asset paths med private oplysninger.
- Join codes er korte og private, ikke sikker autentificering. Gaveversionen har lav trusselsmodel; offentlig version kræver stærkere entitlement/session policy.
