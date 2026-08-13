# Næste handling

**Opdateret:** 2026-08-13

Projektet har to parallelle gates **og** et fortsat non-Unity-produktionsspor jf. `AI_COLLABORATION_AGREEMENT.md`.

## Claude — Unity-sporet

Aktuel tracker: **GitHub issue #3**.

Claude ejer M0b-arbejdet i Unity. Resterende verificerbare gate:

1. head/hands replikeres mellem to klienter
2. handshake afviser version/content mismatch korrekt
3. delt kasse går i korrekt to-spiller-state med identisk state
4. 10× Q2↔Q3-løft uden permanent desync (`PO-025`)
5. 72 Hz i minimal netværksscene
6. reconnect-/standby-vinduet måles (`CR-009`)
7. faktiske resultater føres i `config/COMPATIBILITY_MATRIX.md`

Source of truth: `src/unity/RUNBOOK_FUSION.md`, `config/COMPATIBILITY_MATRIX.md` og issue #3.

Claude må ikke markere punkterne verificeret uden faktisk device-evidens.

---

## ChatGPT / Anders — M-Pre-gaten

Aktuel tracker: **GitHub issue #7**.

M-Pre (ADR-022 / PO-110) er ready-to-run. Gaten kræver mindst tre menneskelige sessioner med mindst to forskellige par; gavemodtageren må ikke bruges som tester.

Materiale: `prototype/m-pre/`.

OQ-008, OQ-009 og OQ-010 har separate testprotokoller og afventer menneskedata.

---

## ChatGPT — aktivt non-Unity-produktionsspor

**Dette spor stopper ikke, mens M0b/M-Pre afventer.**

M0b + M-Pre blokerer M1-implementation, men ikke produktionsberedskab.

Aktuel source of truth:

- gap audit: `docs/37_NON_UNITY_GAP_AUDIT.md`
- workstream: `docs/36_CHATGPT_WORKSTREAM.md`
- backlog overlay: `docs/51_BACKLOG_OWNERSHIP_AND_STATUS_OVERLAY.md`

Allerede leveret i den nye bølge:

- source asset manifest
- audio cue manifest
- UX/copy/localization catalog + dansk JSON source
- personalization/privacy package spec
- human QA pack M1-M9
- IP/provenance workflow
- Stormnatten content coverage matrix
- releasekritiske interaction briefs
- gift/release flow
- 10-event authoring catalog
- visual style bible
- UI/information architecture
- after-action/replay spec
- product telemetry/metrics spec

### Næste ublokerede ChatGPT-arbejde

1. scope-bevidste løsningsforslag til content issue #8
2. narrative continuity pass på hele Stormnatten
3. neutral fallback source package
4. content authoring templates
5. source production batches for art/audio
6. selektiv faktisk source asset/audio-produktion, hvor rework-risikoen er lav
7. fortsat machine-readable content expansion uden at låse balance

---

## Content-contract — issue #8

Tre uoverensstemmelser skal løses før relevant M3/M6 implementation:

1. intro bible vs. tom `INTRO.actions`
2. Day 3 preparation vs. manglende tydelig Day 3 planning phase i scenario-data
3. fire-start som onboarding-core vs. `PO-044` deferred

ChatGPT forbereder løsninger. Hvis løsningen ændrer den valgte 1.012 t-gaveversion eller accepted scope, afgør Anders det.

Claude må ikke løse dem stiltiende i Unity.

---

## Når M-Pre er grøn

1. behandl OQ-006/OQ-007 på evidens
2. opdatér backlog/status
3. saml eksisterende M1 UX/product-materiale til en konkret Claude-handoff
4. M1 implementation kan starte **kun hvis M0b også er grøn**

## Når M-Pre er rød

Start ikke M1. Redesign kerneloopets tradeoff efter `docs/35_M_PRE_GREYBOX_GATE.md` og kør gaten igen.

---

## Fælles gategrænse

**M1 åbner først efter grøn M0b + M-Pre.**

Det er en implementation-gate — ikke en stoplinje for ChatGPTs source/content/UX/QA-arbejde.

Dyr fuld environment-art, endelig audio polish og balance-tuning venter fortsat på relevante gameplay-gates, men specifikation og selektiv gameplay-readable source production må fortsætte.
