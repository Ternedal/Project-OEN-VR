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

Per-klient feasibility er dokumenteret on-device:

- Unity `6000.4.10f1` + OpenXR
- Photon Fusion 2.0.12 forbinder
- `NetworkPlayerRig` spawner med authority
- head-tracking er non-zero via `InputDevices`
- coop solver / greb→kasse-kæden kører on-device

**M0 er ikke lukket endnu.** Følgende kræver stadig cross-device-/to-headset-evidens:

1. head/hands replication mellem to klienter
2. handshake-afvisning ved mismatch
3. delt kasse i korrekt to-spiller-state
4. 10× Q2↔Q3-løft uden permanent desync (PO-025)
5. 72 Hz i minimal netværksscene
6. standby/reconnect-måling (CR-009)

Source of truth for testen: `src/unity/RUNBOOK_FUSION.md` og `config/COMPATIBILITY_MATRIX.md`.

GitHub issue **#3** følger nu den aktuelle Q2/Q3-M0-gate.

### M-Pre — produktgate

M-Pre (ADR-022 / PO-110) er endnu **ikke kørt med mennesker**.

Ready-to-run-pakken er oprettet under `prototype/m-pre/`:

- `README.md`
- `FACILITATOR_SCRIPT.md`
- `TASK_CARDS.md`
- `SESSION_SHEET.md`
- `RESULT_TEMPLATE.md`

Gaten kræver mindst tre gyldige sessioner med mindst to forskellige testerpar. Gavemodtageren må ikke være tester.

## Core

`src/ProjectOen.Core` er et testbart, Unity-uafhængigt core-lag.

Senest dokumenterede fulde kørsel i `src/README.md`: **146 passed, 0 failed**, med CI på push. Senere ændringer skal fortsat verificeres af CI; dette dokument gætter ikke et højere testtal uden evidens.

Core omfatter bl.a. typed IDs, kanonisk JSON, checksums, snapshots, ScenarioDirector, delayed events, outcome-regler, coop-solver, compatibility handshake, join codes, participation tracking, after-action report og scenario-loader.

## Unity-lag

Unity/Fusion-laget ligger under `src/unity/` og ejes af Claude.

Den tidligere statuslinje “Fusion-binding ukompileret” er forældet: repoets M0b-evidens dokumenterer compile/build og flere on-device inkrementer. Cross-device-gaten ovenfor er stadig åben.

## ChatGPT-sporet

Aktuel plan og mangelliste ligger i `docs/36_CHATGPT_WORKSTREAM.md`.

Næste ikke-Unity-arbejde:

1. M-Pre ready-to-run-pakke — **færdig**
2. status-/roadmapoprydning — **i gang**
3. M-Pre mennesketest — **afventer testere**
4. OQ-008 randomness A/B-testdesign — **næste ublokerede opgave**
5. M1 produkt-/UX-handoff — efter grøn M-Pre
6. source asset/audio manifests — efter relevante gates

## Hvad Anders konkret skal gøre

- Få Claude til at følge `CLAUDE.md` + `AI_COLLABORATION_AGREEMENT.md` og afslutte M0b's to-headset-gate.
- Når det passer, skaf to testere ad gangen til M-Pre; materialet kræver ellers ingen forberedelse ud over fire ens markører og en d6.
- Send M-Pre-rådata tilbage til ChatGPT, så gate, OQ-006/OQ-007, backlog og næste handoff kan dispositioneres.

## Vigtige filer

- Samarbejde: `AI_COLLABORATION_AGREEMENT.md`
- ChatGPT-workstream: `docs/36_CHATGPT_WORKSTREAM.md`
- Næste handling: `docs/29_NEXT_ACTION.md`
- M0 issue-body/source: `docs/30_M0_ISSUE_BODY.md`
- M0b runbook: `src/unity/RUNBOOK_FUSION.md`
- Compatibility matrix: `config/COMPATIBILITY_MATRIX.md`
- M-Pre gate: `docs/35_M_PRE_GREYBOX_GATE.md`
- M-Pre materiale: `prototype/m-pre/`
