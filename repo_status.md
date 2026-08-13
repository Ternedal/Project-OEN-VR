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

Ready-to-run-pakken ligger under `prototype/m-pre/`, inklusive tester-rekrutteringsmateriale.

Gaten kræver mindst tre gyldige sessioner med mindst to forskellige testerpar. Gavemodtageren må ikke være tester.

Tracker: GitHub issue #7.

### Content contract

GitHub issue #8 sporer tre reelle source-of-truth-gaps, fundet under content coverage-audit:

1. intro interactions i biblen vs. tom `INTRO.actions` i scenario JSON
2. Day 3 preparation i biblen vs. manglende tydelig Day 3 planning phase i scenario-data
3. fire-start som core onboarding-beat vs. `PO-044` deferred

Claude skal ikke vælge disse svar stiltiende gennem implementation.

---

## Core

`src/ProjectOen.Core` er et testbart, Unity-uafhængigt core-lag.

Senest dokumenterede fulde kørsel: **146 passed, 0 failed**, med CI på push. Et højere testtal må ikke opfindes uden evidens.

Core omfatter bl.a. typed IDs, kanonisk JSON, checksums, snapshots, ScenarioDirector, delayed events, outcome-regler, coop-solver, compatibility handshake, join codes, participation tracking, after-action report og scenario-loader.

## Unity-lag

Unity/Fusion-laget under `src/unity/` ejes af Claude.

Den gamle repo-status “Fusion-binding ukompileret” er ikke længere gældende: compile/build og flere on-device-inkrementer er dokumenteret. Cross-device-gaten er stadig åben.

---

# ChatGPT / non-Unity-sporet

Aktuel kø: `docs/36_CHATGPT_WORKSTREAM.md`.

Den tidligere “stoplinje indtil M-Pre” er **ophævet som for bred**.

Korrekt regel:

- M-Pre + M0b blokerer **M1 implementation**.
- Human evidence blokerer **evidensafhængige produktbeslutninger og balance**.
- De blokerer **ikke** specifikation, content authoring, source manifests, copy, QA-design, personalization contracts eller produktionsberedskab.

## Nye non-Unity leverancer 2026-08-13

### Gap/audit

- `docs/37_NON_UNITY_GAP_AUDIT.md`

### Art / source assets

- `docs/38_SOURCE_ASSET_MANIFEST.md`
- `docs/47_VISUAL_STYLE_BIBLE.md`

### Audio

- `docs/39_AUDIO_CUE_MANIFEST.md`

### UX / copy / localization

- `docs/40_UX_COPY_AND_LOCALIZATION_CATALOG.md`
- `content/localization/da.source.json`
- `docs/48_UI_INFORMATION_ARCHITECTURE.md`

### Personalization / gift

- `docs/41_PERSONALIZATION_PACKAGE_SPEC.md`
- `docs/45_GIFT_EXPERIENCE_AND_RELEASE_FLOW.md`

### QA / metrics

- `docs/42_HUMAN_QA_PLAYTEST_PACK.md`
- `docs/50_PRODUCT_TELEMETRY_AND_METRICS.md`

### IP / provenance

- `docs/43_IP_AND_ASSET_PROVENANCE.md`

### Content / narrative

- `docs/44_CONTENT_COVERAGE_MATRIX.md`
- `docs/46_STORMNATTEN_EVENT_CATALOG.md`
- `docs/49_AFTER_ACTION_AND_REPLAY_SPEC.md`

### Interaction handoffs

`design/interactions/` indeholder briefs for:

- planning table
- shelter reinforcement
- fire start
- ravine rescue
- storm finale

Disse beskriver player experience, begge roller, fail-forward, assets/audio/copy og acceptance criteria — **ikke Unity-arkitektur**.

---

# Hvad der fortsat mangler på ChatGPT-siden

Der er stadig væsentligt arbejde uden for Unity.

Næste ublokerede bølge omfatter bl.a.:

1. backlog ownership/status overlay
2. scope-bevidste løsningsforslag til issue #8
3. machine-readable content expansion uden balance-lock
4. source-production batches
5. narrative continuity pass
6. neutral fallback source package
7. content authoring templates
8. selektiv faktisk source art/audio-produktion, hvor rework-risikoen er acceptabel

Derudover afventer:

- M-Pre human data
- OQ-008/OQ-009/OQ-010 human data
- senere M3-M9 human playtests

## Gategrænse

**M1 åbner først efter grøn M0b + M-Pre.**

Det betyder ikke, at ChatGPT-sporet stopper. Det betyder, at produktionsberedskabet fortsætter uden at foregive evidens eller låse balancen.

---

## Hvad Anders konkret skal gøre

Parallelt med ChatGPTs fortsatte non-Unity-arbejde:

- få Claude til at afslutte M0b issue #3
- når det passer, skaf testerpar til M-Pre issue #7
- beslut kun issue #8-punkter, hvis det konkrete forslag ændrer valgt scope eller kræver produktejerens præference

Resten af den ublokerede non-Unity-kø fortsætter hos ChatGPT.

---

## Vigtige filer

- Indgang: `00_READ_ME_FIRST.md`
- Samarbejde: `AI_COLLABORATION_AGREEMENT.md`
- Claude: `CLAUDE.md`, `docs/32_OPUS_EXECUTION_PLAN.md`
- ChatGPT: `docs/36_CHATGPT_WORKSTREAM.md`
- Gap audit: `docs/37_NON_UNITY_GAP_AUDIT.md`
- Næste handling: `docs/29_NEXT_ACTION.md`
- M0b: issue #3, `src/unity/RUNBOOK_FUSION.md`, `config/COMPATIBILITY_MATRIX.md`
- M-Pre: issue #7, `docs/35_M_PRE_GREYBOX_GATE.md`, `prototype/m-pre/`
- Content reconciliation: issue #8
- Content coverage: `docs/44_CONTENT_COVERAGE_MATRIX.md`
- Source assets/audio: `docs/38_SOURCE_ASSET_MANIFEST.md`, `docs/39_AUDIO_CUE_MANIFEST.md`
- UX/localization: `docs/40_UX_COPY_AND_LOCALIZATION_CATALOG.md`, `content/localization/`
