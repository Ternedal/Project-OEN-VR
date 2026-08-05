# PROJECT ØEN - STRANDET SAMMEN

Et originalt, scenariebaseret VR-overlevelsesspil for præcis to spillere.

Projektet udvikles med **Meta Quest 2 som autoritativ baseline**, en reduceret **Quest 1 legacy-testlane** og fuld brugbarhed på **Quest 3/Quest 3S** med valgfrie visuelle forbedringer.

> Status: Design-, arkitektur- og produktionsbaseline. Der findes endnu ikke et Unity-projekt i repositoryet.

## Start her

1. Læs [`00_READ_ME_FIRST.md`](00_READ_ME_FIRST.md).
2. Ved Claude-review: brug [`01_PROMPT_FOR_CLAUDE.md`](01_PROMPT_FOR_CLAUDE.md).
3. Læs den samlede specifikation i [`PROJECT_OEN_MASTER_HANDOFF_v2.0.pdf`](PROJECT_OEN_MASTER_HANDOFF_v2.0.pdf) eller [`.docx`](PROJECT_OEN_MASTER_HANDOFF_v2.0.docx).
4. Start ikke egentlig produktion før M0-platformspiket i [`docs/20_IMPLEMENTATION_START_ORDER.md`](docs/20_IMPLEMENTATION_START_ORDER.md) er bestået.

## Produktmål

Første leverance er scenariet **Stormnatten**:

- to spillere og fælles sejr/nederlag
- tre døgn og cirka 30-45 minutters spilletid
- fælles planlægning, fysisk VR-arbejde og forsinkede konsekvenser
- aktiv rolle til begge spillere gennem hele forløbet
- stiliseret standalone-VR, ikke open world
- original IP; ingen direkte digital kopi af et eksisterende brætspil

## Repositorystruktur

| Sti | Formål |
|---|---|
| `docs/` | Produktkrav, GDD, arkitektur, platform, roadmap og QA |
| `schemas/` | JSON Schema for scenarioer, events, recipes, saves og personalisering |
| `examples/` | Valide dataeksempler |
| `diagrams/` | Mermaid-diagrammer for system, state, authority og build |
| `review/` | Claude-reviewskabelon og svarmatrix |
| `config/` | Labels og Unity-checklister |
| `.github/` | PR-, issue- og CI-konfiguration |
| `tools/` | Validering og manifestgenerering |
| `reference/` | Tidligere v1.1-referenceleverance |

## Centrale gates

- **M0:** Samme minimale code/content lane starter og kan forbindes på Quest 1, Quest 2 og Quest 3.
- **M2:** Stabil private-session, authority, kompatibilitetshåndtryk og fælles tohåndsobjekt.
- **M3:** Én komplet dag kan spilles uden udviklerforklaring.
- **M5:** Stormens vertical slice holder performance og netværksstabilitet.
- **M9:** P0/P1-fejl er lukket, og fuld enhedsmatrix er dokumenteret.

## Validering

```bash
python tools/validate_handoff.py
```

Scriptet validerer JSON Schema, alle JSON-eksempler og pakkens checksum-manifest.

## Arbejdsprincip

Dokumenterne er source of truth, men ikke urørlige. Ændringer skal være sporbare:

1. dokumentér fund eller prototypebevis
2. opdatér relevant ADR i `docs/18_DECISION_LOG.md`
3. opdatér berørte specs og backlog
4. regenerér manifestet med `python tools/rebuild_manifest.py`

## Rettigheder

Projektmaterialet er privat og ikke open source. Se [`LICENSE`](LICENSE).
