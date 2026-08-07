# `src/` — Core-fundament i ren C#

Hvorfor koden ligger her og ikke i et Unity-projekt: `docs/06` §1 kræver selv, at gameplay-state er data-drevet og **kan testes uden headset**. Alt i denne mappe er `netstandard2.1` uden `UnityEngine`-referencer, så det kan bygges og testes i CI og i en sandbox — længe før editorversionen er afgjort af M0a.

Filerne flyttes 1:1 til `Assets/ProjectOen/Scripts/Core/` med en asmdef, når M0a er besvaret. Namespacet er allerede det endelige.

## Kør testene

```bash
dotnet test src/ProjectOen.Core.Tests/ProjectOen.Core.Tests.csproj
```

Seneste kørsel i sandbox: **38 passed, 0 failed.**

## Indhold

| Fil | Ansvar |
|---|---|
| `Ids/TypedIds.cs` | `ScenarioId`, `EventId`, `ItemId`, `RecipeId`, `InteractionId` med mønstrene fra `docs/10`. Opfylder `docs/16`s forbud mod string-baserede IDs |
| `Persistence/CanonicalJson.cs` | Kanonisk JSON: sorterede nøgler, ingen whitespace. Findes udelukkende for at gøre checksummen reproducerbar |
| `Persistence/SaveChecksum.cs` | Checksum-reglen fra `docs/10`, én implementering |
| `Persistence/AtomicSaveWriter.cs` | Skriveflowet fra `docs/06` §9: temp → verificér → backup → atomisk rename. Filsystemet bag et interface, så afbrudte skrivninger kan testes |
| `Scenario/ScenarioContract.cs` | Runtime-validering af ScenarioDefinition: actionCatalog-referencer, protokolversion, to roller pr. handling |
| `Scenario/ScenarioModel.cs` | Faser, lejr-, spiller- og scenariostate, indsatsøkonomi, delayed event queue |
| `Scenario/CommandsAndEvents.cs` | Command/event-mønstret fra `docs/06` §6. Klienten sender intents, aldrig resultater |
| `Scenario/ScenarioDirector.cs` | Fasemaskinen. Kun den må skifte fase. Idempotens via command-ID |
| `Scenario/OutcomeResolver.cs` | Udfaldsformlen med gulv-regel fra `docs/04` §9 |

## Den vigtigste test

`SaveChecksumTests.Matches_the_checksum_in_the_repository_test_vector` beregner checksummen for `examples/savegame.example.json` og sammenligner med den værdi, `tools/validate_handoff.py` skrev.

To uafhængige implementeringer — Python i CI, C# i runtime — giver samme resultat. Uden den test er checksum-reglen i `docs/10` en hensigt; med den er den en kontrakt. Divergerer de, ville save-filer blive afvist på tværs af tooling og spil, og fejlen ville først vise sig hos en spiller.

## Målingen der rettede reviewet

`OutcomeDistributionTests` simulerer 20 runs × 12 handlinger og måler udfaldsfordelingen.

Reviewet påstod, at den oprindelige otte-leddede formel ville klumpe, og anbefalede fire led. Målingen viste, at fire led klumpede *marginalt værre* (70,0 % mod 68,8 %) — antallet af led var ikke årsagen. Den var, at `penalty` blev trukket fra med fuld vægt fra en score, hvis positive led summerer til 1,0.

Efter rettelsen (begrænset modstandsvægt + gulv-regel fra `docs/04` §9): største enkelt-tier 47,5 %, alle fire kategorier forekommer. Påstanden er trukket tilbage i `docs/33`.

Testen fejler, hvis én tier dækker ≥70 %, hvis en kategori aldrig forekommer, eller hvis en perfekt udført sekvens kan blive `FailForward`.

## Hvad der bevidst IKKE ligger her

Alt der rører Unity eller Fusion. `ProjectOen.Interaction`, `ProjectOen.Networking` og `ProjectOen.Platform` kan ikke kompileres uden Editor og SDK, og skrives derfor først som kildefiler med eksplicit `UNVERIFIED-IN-SANDBOX`-markering — jf. `docs/32` fase 4.
