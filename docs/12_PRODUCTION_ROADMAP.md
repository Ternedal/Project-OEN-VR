# Produktionsroadmap

## Arbejdsmodel

Roadmappet er baseret på gennemførte gates, ikke kalenderløfter. En fase lukkes først, når dens acceptance criteria er demonstreret på fysiske headset.

## M0 - Platform feasibility

**Estimat:** 60-100 timer  
**Mål:** Bevis én kodebase/buildlane på Quest 1, 2 og 3.

Deliverables:

- Unity project + pinned package candidates.
- Q1/Q2/Q3 build profiles.
- XR tracking/grab.
- Photon create/join.
- Head/hands replication.
- Heavy shared box proof.
- Compatibility matrix.

Gate:

- Samme scenario/protocol kan køre Q1↔Q2 og Q2↔Q3.
- 10 løftegentagelser uden permanent desync.
- 72 Hz i minimal scene.

**Stop/go:** Hvis Quest 1 kræver så stor dependency fork, at shared gameplaykode ikke kan bevares, nedgraderes kravet til separat testdemo eller droppes efter ejergodkendelse.

## M1 - Interaction foundation

**Estimat:** 35-55 timer

- XR rig, locomotion og calibration.
- Grab/snap abstractions.
- Two-hand stabilization.
- Haptics/feedback.
- Seated/standing checks.

Gate: alle kerneinteraktioner kan udføres 10 gange af to testere uden reset.

## M2 - Multiplayer foundation

**Estimat:** 45-70 timer

- Lobby/join code/ready.
- Player rig replication.
- Authority rules.
- Compatibility handshake.
- Disconnect/reconnect skeleton.
- Network debug UI.

Gate: 10 session cycles og state transfer uden skjult divergence.

## M3 - One-day prototype

**Estimat:** 55-85 timer

- Dawn/planning/action/dusk/night.
- Four effort markers.
- Resources/player/camp state.
- Shelter interaction.
- Checkpoint/save.

Gate: ekstern test kan gennemføre én dag uden forklaring og oplever et reelt prioriteringsvalg.

## M4 - Consequence verticality

**Estimat:** 40-65 timer

- Event definitions and delayed queue.
- Open food -> animal chain.
- Injury/treatment.
- Weather profiles.
- After-action causal report.

Gate: tester kan forklare mindst én forsinket konsekvens.

## M5 - Storm vertical slice

**Estimat:** 70-110 timer

- Three storm phases minimum.
- Two active roles per phase.
- Branches from shelter/fire/injury.
- Win/lose and retry from checkpoint.
- Performance soak.

Gate: 20-minute repeated storm test uden netværks- eller memoryfejl; 72 Hz Quest 2.

## M6 - Full Stormnatten content

**Estimat:** 70-115 timer

- Three complete days.
- Ravine rescue.
- Ten event definitions.
- Signal ending.
- Tutorial and subtitles.

Gate: median 35-45 minutter, ingen udviklerforklaring.

## M7 - Art/audio pass

**Estimat:** 55-90 timer

- Consistent environment art.
- Lighting and VFX profiles.
- Audio layers and cues.
- Avatar/hand polish.

Gate: visuel polish uden performance regression.

## M8 - Personalization and gift release

**Estimat:** 30-50 timer

- PersonalizationProfile.
- Private assets.
- Neutral fallback.
- Finale.
- Release channel + Quest 1 sideload guide.

Gate: clean install på begge brugeres headset og gennemførsel uden dev tools.

## M9 - QA and release candidate

**Estimat:** 40-70 timer

- Regression matrix.
- Comfort and accessibility pass.
- Soak and standby tests.
- Save migration/rollback.
- P0/P1 closure.

## Samlet interval og estimatmodel

Summen af faseintervallerne er **500-810 timer** for den fokuserede, polerede gaveversion. Det forudsætter hård scopekontrol, genbrug eller køb af passende assets og at P2-opgaver kan udskydes.

Backlog-workbooken er en bredere engineering-plan og summerer til cirka **1.447 timer**. Den inkluderer alle P0/P1/P2-opgaver, ekstra tooling, gentagne device-tests, maksimal hardening og optional polish. Den må derfor ikke bruges som den forventede gave-dato uden først at vælge et konkret release-scope.

Planlægningsregel:

- **P0:** releasekritisk eller blocker.
- **P1:** forventet kvalitet til gaveversionen, men skal prioriteres aktivt.
- **P2:** optional polish eller reduktionskandidat.
- En milepæl er ikke “færdig”, fordi alle dens P1/P2-opgaver er lukket; den er færdig, når dens gate er bevist.

## Scope ladder

Hvis projektet bliver for stort, skæres i denne rækkefølge:

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
