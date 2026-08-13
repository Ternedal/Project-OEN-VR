# Repository status

**Opdateret:** 2026-08-13

## Baseline og beslutninger

- Handoff baseline: **v2.1** (review v1.0 behandlet og merget).
- Review state: **alle 10 review-fund lukket**.
- Quest policy: Quest 2 er performancegulv; Quest 3/3S er enhanced parity.
- Quest 1 er droppet som runtime/testlane (`DROP_Q1_RUNTIME`, ADR-019 accepted).
- P1-scope er valgt: gaveversion **1.012 t** inkl. M-Pre/PO-110; 439 t er udskudt til efter v1.0.
- M-Pre er accepteret via ADR-022.
- M5 er Release 1 via ADR-023.
- Samarbejdsmodel: `AI_COLLABORATION_AGREEMENT.md` — Claude = Unity, ChatGPT = alt andet.

## Aktuelle gates

### M0b — Unity/networking

Per-client feasibility er dokumenteret on-device:

- Unity `6000.4.10f1` + OpenXR
- Photon Fusion `2.0.12` forbinder
- `NetworkPlayerRig` spawner med authority
- head-tracking er non-zero via `InputDevices`
- coop solver / greb→kasse-kæden kører on-device

**M0 er ikke lukket endnu.** Følgende kræver stadig cross-device-/to-headset-evidens:

1. head/hands replication mellem to klienter
2. handshake-afvisning ved mismatch
3. delt kasse i korrekt to-spiller-state
4. 10× Q2↔Q3-løft uden permanent desync (`PO-025`)
5. 72 Hz i minimal netværksscene
6. standby/reconnect-måling (`CR-009`)
7. faktiske resultater i `config/COMPATIBILITY_MATRIX.md`

Source of truth: `src/unity/RUNBOOK_FUSION.md`, `config/COMPATIBILITY_MATRIX.md` og GitHub issue #3.

Dette er Claude/Unity-sporet.

### M-Pre — produktgate

M-Pre (ADR-022 / PO-110) er **klar, men endnu ikke kørt med mennesker**.

Ready-to-run-pakken ligger under `prototype/m-pre/`:

- `README.md`
- `FACILITATOR_SCRIPT.md`
- `TASK_CARDS.md`
- `SESSION_SHEET.md`
- `RESULT_TEMPLATE.md`

Gaten kræver mindst tre gyldige sessioner med mindst to forskellige testerpar. Gavemodtageren må ikke være tester.

Dette er ChatGPT/produkt-sporet sammen med Anders.

## Core

`src/ProjectOen.Core` er et testbart, Unity-uafhængigt core-lag.

Senest dokumenterede fulde kørsel: **146 passed, 0 failed**, med CI på push. Et højere testtal må ikke opfindes uden evidens.

Core omfatter bl.a. typed IDs, kanonisk JSON, checksums, snapshots, ScenarioDirector, delayed events, outcome-regler, coop-solver, compatibility handshake, join codes, participation tracking, after-action report og scenario-loader.

## Unity-lag

Unity/Fusion-laget under `src/unity/` ejes af Claude.

Den gamle repo-status “Fusion-binding ukompileret” er ikke længere gældende: compile/build og flere on-device-inkrementer er dokumenteret. Cross-device-gaten er stadig åben.

## ChatGPT-sporet

Aktuel plan: `docs/36_CHATGPT_WORKSTREAM.md`.

Færdigt 2026-08-13:

- M-Pre ready-to-run-pakke
- status-/roadmapoprydning
- root/master/handoff-guidance-oprydning
- OQ-008 randomness-testprotokol
- OQ-009 rolletestprotokol
- OQ-010 efterspils-konkurrenceprotokol

Root-dokumenterne (`00_READ_ME_FIRST.md`, `README.md`, `CLAUDE.md`, master handoff, implementeringsrækkefølge og Claude execution plan) er nu rettet til den aktuelle M0b/M-Pre-tilstand. Review v1.0-materiale er markeret som historik, hvor relevant.

## Aktuel stoplinje

Der er ingen vigtig ikke-Unity-produktbeslutning, som bør afgøres uden menneskedata.

Det næste evidensskabende arbejde er:

1. **Claude/Anders:** luk M0b cross-device.
2. **Anders/testere:** kør M-Pre.
3. **ChatGPT:** behandl M-Pre-data, når de findes.
4. **Mennesketest:** OQ-008/OQ-009/OQ-010, når deres forudsætninger er til stede.

**M1 åbner først efter grøn M0b + M-Pre.**

Derefter åbner ChatGPT C-020 (M1 player-experience/UX-handoff) og senere de relevante source asset/audio manifests.

## Hvad Anders konkret skal gøre

- Få Claude til at følge `CLAUDE.md` + `AI_COLLABORATION_AGREEMENT.md` og afslutte M0b's to-headset-gate.
- Når det passer, skaf to testere ad gangen til M-Pre; materialet kræver ellers kun fire ens markører og en d6.
- Send M-Pre-rådata tilbage til ChatGPT, så gate, OQ-006/OQ-007, backlog og næste handoff kan dispositioneres.

## Vigtige filer

- Indgang: `00_READ_ME_FIRST.md`
- Samarbejde: `AI_COLLABORATION_AGREEMENT.md`
- Claude: `CLAUDE.md`, `docs/32_OPUS_EXECUTION_PLAN.md`
- ChatGPT: `docs/36_CHATGPT_WORKSTREAM.md`
- Næste handling: `docs/29_NEXT_ACTION.md`
- M0b: GitHub issue #3, `src/unity/RUNBOOK_FUSION.md`, `config/COMPATIBILITY_MATRIX.md`
- M-Pre: `docs/35_M_PRE_GREYBOX_GATE.md`, `prototype/m-pre/`
- Design-tests: `prototype/design-tests/`
