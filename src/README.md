# `src/` — Core-fundament i ren C#

Hvorfor koden ligger her og ikke i et Unity-projekt: `docs/06` §1 kræver selv, at gameplay-state er data-drevet og **kan testes uden headset**. Alt i denne mappe er `netstandard2.1` uden `UnityEngine`-referencer, så det kan bygges og testes i CI og i en sandbox — længe før editorversionen er afgjort af M0a.

Filerne flyttes 1:1 til `Assets/ProjectOen/Scripts/Core/` med en asmdef, når M0a er besvaret. Namespacet er allerede det endelige.

## Kør testene

```bash
dotnet test src/ProjectOen.Core.Tests/ProjectOen.Core.Tests.csproj
```

Seneste kørsel i sandbox: **88 passed, 0 failed.**

## Indhold

| Fil | Ansvar |
|---|---|
| `Ids/TypedIds.cs` | `ScenarioId`, `EventId`, `ItemId`, `RecipeId`, `InteractionId` med mønstrene fra `docs/10`. Opfylder `docs/16`s forbud mod string-baserede IDs |
| `Persistence/CanonicalJson.cs` | Kanonisk JSON: sorterede nøgler, ingen whitespace. Findes udelukkende for at gøre checksummen reproducerbar |
| `Persistence/SaveChecksum.cs` | Checksum-reglen fra `docs/10`, én implementering |
| `Persistence/AtomicSaveWriter.cs` | Skriveflowet fra `docs/06` §9: temp → verificér → backup → atomisk rename. Filsystemet bag et interface, så afbrudte skrivninger kan testes |
| `Persistence/ScenarioSnapshot.cs` | Fuld capture/restore af scenariostate. Lukker PR 5 i `docs/20` |
| `Scenario/ScenarioContract.cs` | Runtime-validering af ScenarioDefinition: actionCatalog-referencer, protokolversion, to roller pr. handling |
| `Scenario/ScenarioModel.cs` | Faser, lejr-, spiller- og scenariostate, indsatsøkonomi, delayed event queue |
| `Scenario/CommandsAndEvents.cs` | Command/event-mønstret fra `docs/06` §6. Klienten sender intents, aldrig resultater |
| `Scenario/ScenarioDirector.cs` | Fasemaskinen. Kun den må skifte fase. Idempotens via command-ID |
| `Scenario/OutcomeResolver.cs` | Udfaldsformlen med gulv-regel fra `docs/04` §9 |
| `Numerics/Vec3.cs` | Minimal vektortype, så solvermatematik kan testes uden `UnityEngine` |
| `Interaction/CoopSolver.cs` | Kinematisk coop-solver: dæmpet midtpunkt, hastighedsloft, gradvist kvalitetsfald |
| `Networking/CompatibilityHandshake.cs` | De seks felter fra `docs/07` §5. Dækker COMPAT-001 og COMPAT-002 |
| `Networking/JoinCode.cs` | Alfabet uden forvekslingstegn, normalisering af det folk faktisk taster |
| `Telemetry/ActiveParticipation.cs` | Måler "begge aktive ≥70 %" og passive perioder. Lukker CR-007 |
| `Telemetry/AfterActionReport.cs` | Årsagskæden fra `docs/04` §10. Bygges kun af event-journalen |

## Den vigtigste test

`SaveChecksumTests.Matches_the_checksum_in_the_repository_test_vector` beregner checksummen for `examples/savegame.example.json` og sammenligner med den værdi, `tools/validate_handoff.py` skrev.

To uafhængige implementeringer — Python i CI, C# i runtime — giver samme resultat. Uden den test er checksum-reglen i `docs/10` en hensigt; med den er den en kontrakt. Divergerer de, ville save-filer blive afvist på tværs af tooling og spil, og fejlen ville først vise sig hos en spiller.

## Målingen der rettede reviewet

`OutcomeDistributionTests` simulerer 20 runs × 12 handlinger og måler udfaldsfordelingen.

Reviewet påstod, at den oprindelige otte-leddede formel ville klumpe, og anbefalede fire led. Målingen viste, at fire led klumpede *marginalt værre* (70,0 % mod 68,8 %) — antallet af led var ikke årsagen. Den var, at `penalty` blev trukket fra med fuld vægt fra en score, hvis positive led summerer til 1,0.

Efter rettelsen (begrænset modstandsvægt + gulv-regel fra `docs/04` §9): største enkelt-tier 47,5 %, alle fire kategorier forekommer. Påstanden er trukket tilbage i `docs/33`.

Testen fejler, hvis én tier dækker ≥70 %, hvis en kategori aldrig forekommer, eller hvis en perfekt udført sekvens kan blive `FailForward`.

## Anden måling: coop-solveren

`CoopSolverTests` afslørede, at hastighedsloftet gjorde én-hånds- og to-hånds-tilstanden identiske, så snart objektet var mere end få centimeter væk. Hele "tung kasse kræver to spillere"-mekanikken ville kun kunne mærkes tæt på målet. Rettet med `SingleHandSpeedFactor`. Skrevet op i `docs/33`.

## CR-007 er nu indfriet, ikke bare lovet

Reviewet krævede, at "begge spillere aktive" måles i stedet for observeres, og `docs/13` blev opdateret til at love det. `ActiveParticipationTracker` gør det nu faktisk.

Testen der betyder mest: en sekvens hvor gennemsnittet ser fint ud (75 % begge aktive) men skjuler en sammenhængende passiv periode på 25 sekunder. Andels-gaten alene ville godkende den. Rapporten fanger den, fordi den også tæller perioder over 12 s (designregel) og 20 s (testgrænse) hver for sig.

Efterspilsrapporten producerer linjer som:

> `Dag 2: EVT_ANIMAL_AT_CAMP_002 — fordi I lod maden stå åben på dag 1 (SCENT_HIGH).`

Det er M4's gate i `docs/12` — "tester kan forklare mindst én forsinket konsekvens" — som noget der kan verificeres frem for vurderes.

## Save round-trip — PR 5

`ScenarioSnapshotTests` spiller til nat 1, skriver et checkpoint gennem den atomiske writer, læser det tilbage fra disk og genoptager. Det forsinkede event udløses præcis én gang — også hvis man genoptager fra det samme checkpoint to gange.

Det, der gør snapshottet noget værd, er ikke serialiseringen. Det er, at `HandledCommands` og eventkøens `Fired`-flag følger med. Uden dem ville et resume udløse forsinkede events igen, og en gentaget command efter reconnect ville tælle to gange. Det er SAVE-001 i `docs/13`, hele vejen igennem.

En test læser `schemas/savegame.schema.json` direkte og verificerer, at snapshottets feltsæt holder sig inden for det, skemaet tillader (`additionalProperties: false`) og indeholder alt påkrævet. CI og runtime kan dermed ikke blive uenige om, hvad en gyldig save er.

## Hvad der bevidst IKKE ligger her

Alt der rører Unity eller Fusion. Det ligger i [`../src/unity/`](../src/unity/README.md) som ukompilerede kildefiler med eksplicit `UNVERIFIED-IN-SANDBOX`-markering og konkrete API-antagelser pr. fil.

Grænsen er ikke vilkårlig. Alt hvad der kan verificeres, er flyttet hertil og testet — solvermatematikken, handshake-reglerne, join code-normaliseringen, fasemaskinen, målingerne. Fusion-laget transporterer data og træffer ingen beslutninger.
