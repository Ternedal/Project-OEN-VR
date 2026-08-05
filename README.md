# PROJECT ØEN - STRANDET SAMMEN

Et originalt, scenariebaseret VR-overlevelsesspil for præcis to spillere.

Projektet udvikles med **Meta Quest 2 som autoritativ baseline**, en reduceret **Quest 1 legacy-testlane** og fuld brugbarhed på **Quest 3/Quest 3S** med valgfrie visuelle forbedringer.

> Status: Design-, arkitektur- og produktionsbaseline. Der findes endnu ikke et Unity-projekt i repositoryet.

## Start her

1. Læs [`00_READ_ME_FIRST.md`](00_READ_ME_FIRST.md).
2. Ved Claude-review: brug [`01_PROMPT_FOR_CLAUDE.md`](01_PROMPT_FOR_CLAUDE.md).
3. Læs [`docs/01_EXECUTIVE_HANDOFF.md`](docs/01_EXECUTIVE_HANDOFF.md), efterfulgt af gameplay-, scenario-, arkitektur- og platformkapitlerne i `docs/`.
4. Start ikke egentlig produktion før Claude-reviewet er behandlet og rækkefølgen i [`docs/20_IMPLEMENTATION_START_ORDER.md`](docs/20_IMPLEMENTATION_START_ORDER.md) er godkendt.

## Produktmål

Første leverance er scenariet **Stormnatten**:

- to spillere og fælles sejr/nederlag
- tre døgn og cirka 30-45 minutters spilletid
- fælles planlægning, fysisk VR-arbejde og forsinkede konsekvenser
- aktiv rolle til begge spillere gennem hele forløbet
- stiliseret standalone-VR, ikke open world
- original IP; ingen direkte digital kopi af et eksisterende brætspil

## Centrale dokumenter

| Dokument | Formål |
|---|---|
| [`docs/04_GAME_DESIGN_DEEP_DIVE.md`](docs/04_GAME_DESIGN_DEEP_DIVE.md) | Kerne-loop, handlinger, ressourcer og fail-forward |
| [`docs/05_STORMNATTEN_CONTENT_BIBLE.md`](docs/05_STORMNATTEN_CONTENT_BIBLE.md) | Det første komplette scenario |
| [`docs/06_TECHNICAL_ARCHITECTURE.md`](docs/06_TECHNICAL_ARCHITECTURE.md) | Unity-, state-, persistence- og modularkitektur |
| [`docs/07_MULTIPLAYER_NETWORKING.md`](docs/07_MULTIPLAYER_NETWORKING.md) | Photon Fusion, authority og reconnect |
| [`docs/08_PLATFORM_BUILD_PERFORMANCE.md`](docs/08_PLATFORM_BUILD_PERFORMANCE.md) | Quest 1/2/3-strategi og performancebudget |
| [`docs/12_PRODUCTION_ROADMAP.md`](docs/12_PRODUCTION_ROADMAP.md) | Milepæle M0-M9 og stop/go-gates |
| [`docs/13_TEST_QA_ACCEPTANCE.md`](docs/13_TEST_QA_ACCEPTANCE.md) | Testmatrix og releasekriterier |
| [`review/CLAUDE_REVIEW_TEMPLATE.md`](review/CLAUDE_REVIEW_TEMPLATE.md) | Formatet for Claudes review |

## Repositorystruktur

| Sti | Formål |
|---|---|
| `docs/` | Produktkrav, GDD, arkitektur, platform, roadmap og QA |
| `schemas/` | JSON Schema for scenarioer, events, recipes, saves og personalisering |
| `examples/` | Valide dataeksempler |
| `review/` | Claude-reviewskabelon og svarmatrix |
| `.github/` | PR-, issue- og CI-konfiguration |
| `tools/` | Valideringsværktøjer |

## Centrale gates

- **M0:** Samme minimale code/content lane starter og kan forbindes på Quest 1, Quest 2 og Quest 3.
- **M2:** Stabil private-session, authority, kompatibilitetshåndtryk og fælles tohåndsobjekt.
- **M3:** Én komplet dag kan spilles uden udviklerforklaring.
- **M5:** Stormens vertical slice holder performance og netværksstabilitet.
- **M9:** P0/P1-fejl er lukket, og fuld enhedsmatrix er dokumenteret.

## Validering

```bash
python -m pip install -r tools/requirements-validation.txt
python tools/validate_handoff.py
```

Scriptet validerer de centrale dokumenter, JSON Schema og alle JSON-eksempler.

## Arbejdsprincip

Dokumenterne er source of truth, men ikke urørlige. Ændringer skal være sporbare:

1. dokumentér fund eller prototypebevis
2. opdatér relevant ADR i `docs/18_DECISION_LOG.md`
3. opdatér berørte specs og backlog
4. kør validering før merge

## Rettigheder

Projektmaterialet er privat og ikke open source. Se [`LICENSE`](LICENSE).
