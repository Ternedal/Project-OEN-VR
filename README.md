# PROJECT ØEN — STRANDET SAMMEN

Et originalt, scenariebaseret VR-overlevelsesspil for præcis to spillere.

Projektet udvikles med **Meta Quest 2 som autoritativ performancebaseline** og fuld brugbarhed på **Quest 3/Quest 3S** med additive forbedringer. Quest 1 er udgået som runtime/testlane (`DROP_Q1_RUNTIME`, 2026-08-08).

> **Status 2026-08-13:** Aktiv udvikling. Review og baseline er behandlet, Core har 146 grønne tests, M0a er lukket, M0b er bevist per klient og mangler cross-device-gaten. M-Pre er klar til mennesketest.

## Start her

1. [`00_READ_ME_FIRST.md`](00_READ_ME_FIRST.md) — aktuel source-of-truth-indgang.
2. [`AI_COLLABORATION_AGREEMENT.md`](AI_COLLABORATION_AGREEMENT.md) — Claude/ChatGPT-arbejdsdeling.
3. [`repo_status.md`](repo_status.md) — kort aktuel status.
4. Claude/Unity: [`CLAUDE.md`](CLAUDE.md) + [`docs/32_OPUS_EXECUTION_PLAN.md`](docs/32_OPUS_EXECUTION_PLAN.md).
5. ChatGPT/produkt: [`docs/36_CHATGPT_WORKSTREAM.md`](docs/36_CHATGPT_WORKSTREAM.md).

`01_PROMPT_FOR_CLAUDE.md` er arkiveret review v1.0-materiale og er ikke den aktuelle arbejdsordre.

## Produktmål

Første fulde scenario er **Stormnatten**:

- to spillere og fælles sejr/nederlag
- cirka 30-45 minutters spilletid
- fælles planlægning, fysisk VR-arbejde og forsinkede konsekvenser
- aktiv rolle til begge spillere gennem forløbet
- stiliseret standalone-VR, ikke open world
- original IP

## Aktuelle gates

### M0b — platform/netværk

Per-client M0b er bevist. Der mangler cross-device-evidens for:

- head/hands-replikering
- compatibility mismatch-afvisning
- delt coop-kasse
- 10× Q2↔Q3-løft uden permanent desync
- 72 Hz i minimal netværksscene
- standby/reconnect-måling

Dette er **Claude/Unity-sporet**.

### M-Pre — kernehypotesen

M-Pre tester uden VR, om fire indsatsmarkører skaber reel forhandling og prioritering mellem to spillere frem for administration.

Ready-to-run-pakken ligger under [`prototype/m-pre/`](prototype/m-pre/).

Gaten kræver mindst tre menneskelige sessions med mindst to forskellige par. Dette er **ChatGPT/produkt-sporet** sammen med Anders.

**M1 starter først, når både M0b og M-Pre er grønne.**

## Samarbejdsmodel

- **Claude = Unity:** Unity-projekt, C#/runtime/editor, XR/OpenXR/Fusion, scenes/prefabs, integration, builds, profiling og Unity-side QA.
- **ChatGPT = alt andet:** produkt/design, specs, source-assets, audio-materiale, roadmap, design-tests og produkt-QA.
- Anders er produktejer og har sidste ord.

Se [`AI_COLLABORATION_AGREEMENT.md`](AI_COLLABORATION_AGREEMENT.md) for detaljerne.

## Centrale dokumenter

| Dokument | Formål |
|---|---|
| [`docs/04_GAME_DESIGN_DEEP_DIVE.md`](docs/04_GAME_DESIGN_DEEP_DIVE.md) | Kerne-loop, handlinger, ressourcer og fail-forward |
| [`docs/05_STORMNATTEN_CONTENT_BIBLE.md`](docs/05_STORMNATTEN_CONTENT_BIBLE.md) | Første scenario og contentretning |
| [`docs/06_TECHNICAL_ARCHITECTURE.md`](docs/06_TECHNICAL_ARCHITECTURE.md) | State-, persistence- og modularkitektur |
| [`docs/07_MULTIPLAYER_NETWORKING.md`](docs/07_MULTIPLAYER_NETWORKING.md) | Photon Fusion, authority og reconnect |
| [`docs/08_PLATFORM_BUILD_PERFORMANCE.md`](docs/08_PLATFORM_BUILD_PERFORMANCE.md) | Quest 2/3-strategi og performancebudget |
| [`docs/11_ART_AUDIO_UI_DIRECTION.md`](docs/11_ART_AUDIO_UI_DIRECTION.md) | Visuel, audio- og UI-retning |
| [`docs/12_PRODUCTION_ROADMAP.md`](docs/12_PRODUCTION_ROADMAP.md) | Milepæle og stop/go-gates |
| [`docs/13_TEST_QA_ACCEPTANCE.md`](docs/13_TEST_QA_ACCEPTANCE.md) | Testmatrix og releasekriterier |
| [`docs/18_DECISION_LOG.md`](docs/18_DECISION_LOG.md) | Accepterede beslutninger/ADR'er |
| [`docs/35_M_PRE_GREYBOX_GATE.md`](docs/35_M_PRE_GREYBOX_GATE.md) | Kernehypotesens menneskelige gate |
| [`docs/36_CHATGPT_WORKSTREAM.md`](docs/36_CHATGPT_WORKSTREAM.md) | Ikke-Unity workstream og næste produktarbejde |

## Repositorystruktur

| Sti | Formål |
|---|---|
| `docs/` | Produktkrav, GDD, arkitektur, platform, roadmap og QA |
| `src/ProjectOen.Core/` | Testbar runtime/core-logik uden UnityEngine-afhængighed |
| `src/unity/` | Unity/Fusion-kilde og runbooks |
| `prototype/` | M0- og design-/playtestprototyper |
| `config/` | Compatibility og runtimekontrakter |
| `schemas/` | JSON Schema |
| `examples/` | Valide dataeksempler |
| `review/` | Historisk review og response matrix |
| `.github/` | PR-, issue- og CI-konfiguration |
| `tools/` | Valideringsværktøjer |

## Roadmap i korte træk

- **M0:** platform- og netværksfeasibility
- **M-Pre:** kernehypotese uden VR
- **M1:** interaction foundation
- **M2:** multiplayer hardening
- **M3:** one-day prototype
- **M4:** delayed consequences
- **M5:** storm vertical slice / **Release 1**
- **M6:** fuld Stormnatten
- **M7:** art/audio pass
- **M8:** personalisering/gaveleverance
- **M9:** release candidate/QA

## Validering

```bash
python -m pip install -r tools/requirements-validation.txt
python tools/validate_handoff.py
```

Core-tests:

```bash
dotnet test src/ProjectOen.Core.Tests/ProjectOen.Core.Tests.csproj
```

## Arbejdsprincip

Dokumenterne er source of truth, men ændringer skal være sporbare:

1. dokumentér fund eller prototypebevis
2. opdatér relevant ADR i `docs/18_DECISION_LOG.md`, hvis en accepteret beslutning ændres
3. opdatér berørte specs/backlog/status
4. kør relevante tests/validatorer

> **Bevis før polish. Måling slår antagelse.**

## Rettigheder

Projektmaterialet er privat og ikke open source. Se [`LICENSE`](LICENSE).
