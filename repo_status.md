# Repository status

- Handoff baseline: **v2.1** (review v1.0 behandlet og merget)
- Review state: **alle 10 review-fund lukket.** CR-002 lukket 2026-08-08 (M0a on-device → DROP_Q1_RUNTIME); CR-005 lukket samme dag (P1-scope valgt: gaveversion = 997 t)
- Implementation state: **Core-lag komplet og bevist** — `src/ProjectOen.Core`, 146 tests grønne, kørt i CI på hvert push (senest grøn 08-08 07:25)
- Unity-projekt: **oprettet** (`ProjektOenApp`, Unity `6000.4.10f1` + OpenXR + Fusion 2.0.12). M0b-binding kompilerer og kører on-device
- **M0a AFGJORT 2026-08-08:** Quest 2 kører OpenXR (72 fps, Vulkan, head-tracking OK); Quest 1 crasher (SIGABRT i libopenxr_loader.so) → **DROP_Q1_RUNTIME**. Evidens: `prototype/m0a-openxr-smoke/RESULTAT.md`. **Næste gate: M0b** (Unity-projekt + Photon-session)
- Quest policy: Q2 performancegulv (EOL dec. 2027), Q3/3S enhanced parity. **Q1-lanen er droppet** (DROP_Q1_RUNTIME, ADR-004 superseded / ADR-019 accepted) - Q1 er højst en frossen sideload-demo, aldrig en test- eller runtime-lane

## Hvad ejeren skal gøre

1. ~~Kør M0a~~ — **gjort 08-08**: Q2 grøn, Q1 crasher → `DROP_Q1_RUNTIME`. Evidens i `prototype/m0a-openxr-smoke/RESULTAT.md`.
2. ~~Udfyld `RESULTAT.md` og meld beslutning~~ — **gjort 08-08**: `DROP_Q1_RUNTIME`.
3. ~~Vælg P1-scope (Q-004)~~ — **gjort 08-08**: alle 55 P1-items sat til `In`/`Defer`; gaveversion = 997 t.
4. Opret M0-issuet fra [`docs/30_M0_ISSUE_BODY.md`](docs/30_M0_ISSUE_BODY.md) — tokenet mangler `issues`-scope.
5. ~~Opret Notion-projektsiden~~ — **gjort 08-08**: [projektsiden er oprettet](https://app.notion.com/p/3b6e6b11bf7b812c96fbfb85f84385a1) fra `docs/34`, ajourført til repoets faktiske stand (146 tests, M0a-automatisering, main).

## Hvad der er bygget

| Lag | Sted | Status |
|---|---|---|
| Core-logik | `src/ProjectOen.Core` | 146 tests grønne, CI-kørt |
| M0a-hardwarepakke | `prototype/m0a-openxr-smoke/` | Klar til Anders |
| Fusion-binding | `src/unity/` | **Ukompileret.** Markeret `UNVERIFIED-IN-SANDBOX` |

Se [`src/README.md`](src/README.md) for hvad Core dækker, og [`docs/33_OUTCOME_FORMULA_EVIDENCE.md`](docs/33_OUTCOME_FORMULA_EVIDENCE.md) for tre fejl, testene fandt i dokumenter, der så rigtige ud på skrift.

## Filer

- Eksekveringsplan: [`docs/32_OPUS_EXECUTION_PLAN.md`](docs/32_OPUS_EXECUTION_PLAN.md)
- Review: [`review/CLAUDE_RAW_REVIEW.md`](review/CLAUDE_RAW_REVIEW.md)
- Dispositioner: [`review/RESPONSE_MATRIX.md`](review/RESPONSE_MATRIX.md)
