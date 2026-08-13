# ChatGPT-workstream — PROJECT ØEN

**Ejer:** ChatGPT  
**Projektejer:** Anders  
**Opdateret:** 2026-08-13  
**Scope:** Alt uden for Unity jf. `AI_COLLABORATION_AGREEMENT.md`

## Formål

Denne fil er det løbende overblik over de ikke-Unity-opgaver, ChatGPT ejer, og den rækkefølge de udføres i.

Den overstyrer ikke source-of-truth-hierarkiet i `00_READ_ME_FIRST.md`. Unity/runtime/editor, XR/Fusion, builds, profiling og Unity-side QA tilhører Claude.

---

# Aktuel situation

## Verificeret / på plads

- Kritisk Claude-review er behandlet; alle 10 fund er lukket.
- Baseline er v2.1.
- Quest 1-runtime/testlane er droppet (`DROP_Q1_RUNTIME`).
- Quest 2 er performancegulv; Quest 3/3S er enhanced parity.
- Gaveversionens valgte scope er 1.012 t.
- M-Pre er accepteret som gate via ADR-022.
- Release 1 er fastlagt til M5 via ADR-023.
- M0b er bevist per klient; resterende cross-device-evidens tilhører Claude/Anders-sporet.
- M-Pre ready-to-run-pakken findes under `prototype/m-pre/`.
- OQ-008, OQ-009 og OQ-010 har konkrete testprotokoller under `prototype/design-tests/`.
- GitHub issue #3 beskriver den aktuelle Q2/Q3-M0b-gate.
- Root- og handoff-dokumenter er ajourført til aktiv udvikling og den nye Claude/ChatGPT-arbejdsdeling.

## Det vigtigste, der mangler

1. **M-Pre er ikke kørt.** Kernehypotesen er ikke bevist med mennesker.
2. **M0b er ikke lukket cross-device.** Det kræver to headset og er Claude/Anders-sporet.
3. **OQ-008/OQ-009/OQ-010 mangler menneskedata.** Protokollerne er klare; AI-vurdering må ikke erstatte resultatet.
4. **OQ-007 kan kun delvist besvares af M-Pre.** Rolledata fra OQ-009 skal indgå.
5. **Endelig art/audio/source-asset-masseproduktion er gate-blokeret.**
6. Senere produktejerinput er stadig åbent: same-room vs remote-first, finalens tone, neutral/personlig karakterisering, standardsværhedsgrad og launch-sprog.

---

# P0 — udført / afventer evidens

## C-001 — M-Pre ready-to-run — FÆRDIG

`prototype/m-pre/` indeholder:

- `README.md`
- `FACILITATOR_SCRIPT.md`
- `TASK_CARDS.md`
- `SESSION_SHEET.md`
- `RESULT_TEMPLATE.md`

## C-002 — Status-/roadmapoprydning — FÆRDIG

Ajourført bl.a.:

- `docs/29_NEXT_ACTION.md`
- `repo_status.md`
- `docs/12_PRODUCTION_ROADMAP.md`
- GitHub issue #3

## C-004 — Repository guidance cleanup — FÆRDIG

Ajourført 2026-08-13:

- `CLAUDE.md`
- `00_READ_ME_FIRST.md`
- `README.md`
- `PROJECT_OEN_MASTER_HANDOFF_v2.0.md`
- `02_CLAUDE_UPLOAD_AND_RETURN_GUIDE.md` (arkiveret)
- `docs/20_IMPLEMENTATION_START_ORDER.md`
- `docs/32_OPUS_EXECUTION_PLAN.md`
- `docs/34_NOTION_PROJECT_PAGE.md`

Resultat: root-dokumenterne sender ikke længere Claude tilbage til review v1.0 eller videre til M1 uden M-Pre.

## C-003 — Kør M-Pre med mennesker — AFVENTER

Krav:

- mindst 3 sessions
- mindst 2 forskellige par
- ikke gavemodtageren
- rå målinger efter `docs/35_M_PRE_GREYBOX_GATE.md`

Når data kommer tilbage:

1. udfyld §10 i `docs/35_M_PRE_GREYBOX_GATE.md`
2. afgør `GRØNT` / `RØDT`
3. behandl OQ-006/OQ-007 på evidens
4. opdatér roadmap/backlog/status

---

# P1 — designforsøg klar, afventer mennesker

## C-010 — Randomness / OQ-008 — PROTOKOL FÆRDIG

`prototype/design-tests/OQ-008_RANDOMNESS_FAIRNESS.md`

## C-011 — Roller / OQ-009 — PROTOKOL FÆRDIG

`prototype/design-tests/OQ-009_ROLE_ASSIGNMENT.md`

## C-012 — Efterspils-konkurrence / OQ-010 — PROTOKOL FÆRDIG

`prototype/design-tests/OQ-010_AFTER_ACTION_COMPETITION.md`

Ingen af spørgsmålene lukkes uden menneskedata.

---

# P2 — åbner efter grøn M-Pre

## C-020 — M1 product/UX-handoff til Claude

ChatGPT leverer:

- player experience for locomotion, grab, snap og tohåndsobjekter
- comfort-krav
- seated/standing-adfærd
- feedback/haptics-intention
- acceptance criteria fra spillerperspektivet

Claude vælger og implementerer Unity-løsningen.

## C-021 — Source asset manifest

Autoritativ liste over nødvendige source-assets med ID, kategori, gameplayfunktion, visuel retning, format, variantbehov, milestone, status og Unity-handoff.

## C-022 — Audio cue manifest

Katalog over ambience, interaction feedback, storm, shelter/fire, UI og finale med prioritet og fallback.

---

# Aktuel kø

| ID | Opgave | Status | Blokering |
|---|---|---|---|
| C-001 | M-Pre ready-to-run-pakke | **Færdig** | — |
| C-002 | Status-/roadmapoprydning | **Færdig** | — |
| C-004 | Repository guidance cleanup | **Færdig** | — |
| C-003 | M-Pre mennesketest | **Afventer** | 3 sessions |
| C-010 | OQ-008 testdesign | **Færdig** | menneskedata |
| C-011 | OQ-009 testdesign | **Færdig** | menneskedata |
| C-012 | OQ-010 testdesign | **Færdig** | målbrugerdata |
| C-020 | M1 product/UX-handoff | Planlagt | grøn M-Pre + M0b før M1 |
| C-021 | Source asset manifest | Planlagt | relevant grøn gate |
| C-022 | Audio cue manifest | Planlagt | relevant grøn gate |

---

# Arbejdsregel ved “kør videre”

1. læs `repo_status.md`
2. læs denne fil
3. kontroller seneste commits/gates
4. tag højeste ublokerede ChatGPT-opgave
5. ændr ikke Unity-filer
6. lever konkrete resultater frem for spekulativ planlægning
7. opdatér denne workstream ved statusskift

## Nuværende stoplinje

Der er nu ingen vigtig ikke-Unity-produktbeslutning, der bør afgøres på skrift alene.

Det næste evidensskabende arbejde er:

- Claude/Anders: M0b cross-device
- Anders/testere: M-Pre
- senere: OQ-008/OQ-009/OQ-010 mennesketests

Når M-Pre og M0b er grønne, åbner C-020.

> **Bevis spillets beslutninger før vi polerer dem.**
