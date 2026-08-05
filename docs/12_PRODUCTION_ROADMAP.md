# Produktionsroadmap

## Arbejdsmodel

Roadmappet er baseret på gennemførte gates, ikke kalenderløfter. En fase lukkes først, når dens acceptance criteria er demonstreret på fysiske headset.

## M-Pre - Kernehypotese-gate

**Estimat:** 10-20 timer  
**Mål:** Bevis at markørallokering skaber diskussion, ikke administration (R-003, OQ-006/007), før der bruges timer på platform og netværk.

Deliverables:

- Fladskærms-, papir- eller greybox-prototype af planlægnings- og konsekvensloopet.
- Ingen VR. Intet netværk. Intet Unity-krav.
- Observationsnoter fra mindst to eksterne testere.

Gate - alle fire skal være opfyldt:

1. Testerne diskuterer indbyrdes før mindst 3 af 4 markørallokeringer, uden udviklerforklaring.
2. Mindst én tester ytrer uopfordret uenighed eller tvivl om en prioritering.
3. Ved afsløret konsekvens reagerer mindst én tester på tidligere valg.
4. Ingen tester beskriver loopet som administration eller bogholderi ved efterspil.

**Stop/go:** Rødt på punkt 1 eller 3 udløser redesign af kerneloopet før alt andet arbejde. Potentiel besparelse ved rødt: hele M0-M2, ca. 250 timer.

Se ADR-021. Kræver to eksterne testere, jf. CR-007 og Q-004.

## M0 - Platform feasibility

**Estimat:** 60-100 timer  
**Mål:** Bevis engine-baseline og én kodebase/buildlane på Quest 2 og 3.

Deliverables:

- Engine-baseline-gate bestået, jf. `docs/06` §3 (ADR-020).
- Unity 6000.3.x project + pinned package candidates.
- Q2/Q3 build profiles.
- XR tracking/grab.
- Photon create/join.
- Head/hands replication.
- Heavy shared box proof.
- Compatibility matrix.

Gate:

- Samme scenario/protocol kan køre Q2↔Q3.
- 10 løftegentagelser uden permanent desync, målt kvantitativt jf. `docs/07` §14.
- 72 Hz i minimal scene.

**Stop/go:** Hvis engine-baseline-gaten fejler på både 6000.3.x og 6000.0.x, standses M0 og stackvalget genåbnes med ejerbeslutning.

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

## M5 - Storm vertical slice = RELEASE 1 (afsendbar gave)

**Estimat:** 70-110 timer

Dette er projektets primære gavemål, jf. ADR-022. Afslutningen af M5 skal være en gave, der kan gives som den er. Alt efter M5 er stretch.

- Tre stormfaser: vind -> regn/ild -> signal. Fase 3 (skade/dyr) og 4 (kollaps) er stretch, ikke Release 1-indhold.
- Two active roles per phase.
- Branches from shelter/fire/injury.
- Win/lose and retry from checkpoint.
- Performance soak.

Gate for Release 1: to personer gennemfører ende-til-ende i ét sammenhængende forløb uden udviklerindgriben; 20-minutters gentaget stormtest uden netværks- eller memoryfejl; 72 Hz stabilt på Quest 2; checkpoint-resume virker; komfortindstillinger nås inden for to klik fra pause.

## M6 - Full Stormnatten content (stretch)

**Estimat:** 70-115 timer

- Three complete days.
- Ravine rescue.
- Ten event definitions.
- Signal ending.
- Tutorial and subtitles.

Gate: median 35-45 minutter, ingen udviklerforklaring.

## M7 - Art/audio pass (stretch)

**Estimat:** 55-90 timer

- Consistent environment art.
- Lighting and VFX profiles.
- Audio layers and cues.
- Avatar/hand polish.

Gate: visuel polish uden performance regression.

## M8 - Personalization og udvidet gaverelease (stretch)

**Estimat:** 30-50 timer

- PersonalizationProfile.
- Private assets.
- Neutral fallback.
- Finale.
- Release channel guide.

Gate: clean install på begge brugeres headset og gennemførsel uden dev tools.

## M9 - QA and release candidate (stretch)

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
