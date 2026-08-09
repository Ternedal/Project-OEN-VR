# Produktionsroadmap

## Arbejdsmodel

Roadmappet er baseret på gennemførte gates, ikke kalenderløfter. En fase lukkes først, når dens acceptance criteria er demonstreret på fysiske headset.

## M0 - Platform- og netværksfeasibility

**Estimat:** 160-200 timer (backlogsum: 176 t over 19 items)  
**Mål:** Bevis én kodebase/buildlane **og** en fungerende to-klient-session på Quest 2 og 3.

M0 optager de session- og replikationsopgaver, der tidligere lå i M2 (PO-017, PO-018, PO-019, PO-020, PO-022, PO-025). Begrundelse: M0's gate kunne ikke bevises af M0's egne opgaver, hvilket flyttede stop/go på projektets største risiko til efter ca. 250 timer.

### M0a - Afgjort 2026-08-08

Den tomme OpenXR-scene blev installeret fysisk. Quest 2: immersiv, 71,8 fps, Vulkan, head-tracking valid.
Quest 1: deterministisk SIGABRT i `libopenxr_loader.so` før første frame.

Resultat: `DROP_Q1_RUNTIME`. Exit-kriteriet i `docs/14` er udløst; Q1 er frossen sideload-demo, og
hovedprojektet bygges på Unity 6 LTS. Vulkan/GLES3-spiket (OQ-003) er droppet sammen med lanen.

### M0b - Deliverables

- Unity project + pinned package candidates (editor låses her, ikke før).
- Q2/Q3 build profiles.
- XR tracking/grab.
- Photon create/join med privat join code.
- Compatibility handshake.
- Head/hands replication.
- Heavy shared box proof (`CoopObjectController`).
- Compatibility matrix.

Gate:

- Samme scenario/protocol kan køre Q2↔Q3.
- 10 løftegentagelser uden permanent desync.
- 72 Hz i minimal scene.

**Stop/go:** Afgøres ved afslutningen af M0, ikke efter et timeloft. Quest 1-delen er allerede afgjort: lanen er droppet efter ejergodkendelse (`DROP_Q1_RUNTIME`, 2026-08-08).

## M1 - Interaction foundation

**Estimat:** 80-100 timer (backlogsum: 89 t)

- XR rig, locomotion og calibration.
- Grab/snap abstractions.
- Two-hand stabilization.
- Haptics/feedback.
- Seated/standing checks.

Gate: alle kerneinteraktioner kan udføres 10 gange af to testere uden reset.

## M2 - Multiplayer hardening

**Estimat:** 90-120 timer (backlogsum: 98 t over 8 items)

Session- og replikationsgrundlaget er bevist i M0. M2 hærder det.

- Ready-flow og lobby-UX.
- Authority rules for lette objekter.
- Disconnect/reconnect og safe pause.
- Checkpoint schema/checksum og snapshot-resync.
- Network debug UI.
- Packet loss/latency og failure injection.
- Måling af standby → netværkstab på Q2/Q3, som sætter reconnect-vinduet (jf. CR-009).

Gate: 10 session cycles og state transfer uden skjult divergence.

## M3 - One-day prototype

**Estimat:** 230-280 timer i fuld backlog (P0-delen: 112 t) — afhænger af P1-udvælgelsen

- Dawn/planning/action/dusk/night.
- Four effort markers.
- Resources/player/camp state.
- Shelter interaction.
- Checkpoint/save.

Gate: ekstern test kan gennemføre én dag uden forklaring og oplever et reelt prioriteringsvalg.

## M4 - Consequence verticality

**Estimat:** 140-170 timer i fuld backlog (P0-delen: 86 t)

- Event definitions and delayed queue.
- Open food -> animal chain.
- Injury/treatment.
- Weather profiles.
- After-action causal report.

Gate: tester kan forklare mindst én forsinket konsekvens.

## M5 - Storm vertical slice

**Estimat:** 120-150 timer (backlogsum: 130 t, heraf 88 t P0)

- Three storm phases minimum.
- Two active roles per phase.
- Branches from shelter/fire/injury.
- Win/lose and retry from checkpoint.
- Performance soak.

Gate: 20-minute repeated storm test uden netværks- eller memoryfejl; 72 Hz Quest 2.

## M6 - Full Stormnatten content

**Estimat:** 200-250 timer i fuld backlog (P0-delen: 28 t) — den mest scopefølsomme milepæl

- Three complete days.
- Ravine rescue.
- Ten event definitions.
- Signal ending.
- Tutorial and subtitles.

Gate: median 35-45 minutter, ingen udviklerforklaring.

## M7 - Art/audio pass

**Estimat:** 140-180 timer i fuld backlog (P0-delen: 24 t)

- Consistent environment art.
- Lighting and VFX profiles.
- Audio layers and cues.
- Avatar/hand polish.

Gate: visuel polish uden performance regression.

## M8 - Personalization and gift release

**Estimat:** 80-100 timer (backlogsum: 86 t)

- PersonalizationProfile.
- Private assets.
- Neutral fallback.
- Finale.
- Release channel (Alpha/private til Q2/Q3).

Gate: clean install på begge brugeres headset og gennemførsel uden dev tools.

## M9 - QA and release candidate

**Estimat:** 85-110 timer (backlogsum: 90 t, heraf 82 t P0)

- Regression matrix.
- Comfort and accessibility pass.
- Soak and standby tests.
- Save migration/rollback.
- P0/P1 closure.

## Samlet interval og estimatmodel

**Revideret 2026-08-06 (CR-005).** De to estimatmodeller var tidligere parallelle og uden afbildning mellem sig: roadmappet lovede 500-810 timer, mens backloggens milepælssummer var op til tre gange højere for samme milepæl (fx M3: 55-85 t mod 260 t). Roadmapintervallerne er nu bundet til backloggens faktiske itemsummer, og backloggen har fået kolonnen `Gaveversion`.

Aktuel tilstand efter reviewet:

| Model | Sum | Status |
|---|---:|---|
| Aktiv backlog (107 items) | 1.436 t | Fuld engineering-plan, maksimal hardening. 3 Q1-items (28 t) droppet |
| `Gaveversion = In` (45 P0-items) | 634 t | Kritisk sti — låst, releasekritisk pr. `docs/12`s egen P0-definition |
| `Gaveversion = TBD` (56 P1-items) | 712 t | **Skal vælges af ejeren.** Indtil da findes der ikke et forsvarligt gaveestimat |
| `Gaveversion = Defer` (9 P2-items) | 127 t | Efter v1.0 |

Det tidligere tal på 500-810 timer var top-down og kunne hverken forsvares eller spores. Det genindsættes først, når P1-udvælgelsen er foretaget — som `634 t + summen af de valgte P1-items`.

Planlægningsregel:

- **P0:** releasekritisk eller blocker.
- **P1:** forventet kvalitet til gaveversionen, men skal prioriteres aktivt.
- **P2:** optional polish eller reduktionskandidat.
- En milepæl er ikke “færdig”, fordi alle dens P1/P2-opgaver er lukket; den er færdig, når dens gate er bevist.

## Scope ladder

Hvis projektet bliver for stort, skæres i denne rækkefølge:

0. ~~**Quest 1-lanen**~~ - **skåret 2026-08-08** (`DROP_Q1_RUNTIME`). Projektets dyreste valgfrie del er allerede fjernet; næste skæring starter derfor ved punkt 1.
1. Ekstra eventvariation.
2. Avanceret avatar/IK.
3. Parallelle fjernekspeditioner.
4. Quest 3 visuelle enhancements.
5. Individuelle ambitioner.
6. Fjernvoice.
7. Ekstra miljøzone.

Der skæres **ikke** først i:

- to aktive spillerroller,
- planlægning/konsekvens,
- checkpoint/reconnect,
- Quest 2-performance,
- Stormfinalens branches.

## Efter gaveversion

### v1.1

- Flere events og vejrvarianter.
- Personlige ambitioner.
- Photon Voice.

### v1.5 - Vraget

- Tidevandszone og salvage.
- Nyt scenario på 30-45 min.

### v2.0 - mulig offentlig udgave

- Tre scenarier.
- Neutral fortælling.
- Store onboarding/release/privacy/legal passes.
- Offentlig distribution og mulig monetisering.
