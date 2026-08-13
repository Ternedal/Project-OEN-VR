# Næste handling

**Opdateret:** 2026-08-13

Projektet har to parallelle gates jf. `AI_COLLABORATION_AGREEMENT.md`.

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

## ChatGPT / Anders — produktsporet

Aktuel tracker: **GitHub issue #7**.

Den næste produktgate er **M-Pre** (ADR-022 / PO-110).

Ready-to-run-materialet ligger i `prototype/m-pre/`:

1. `README.md`
2. `FACILITATOR_SCRIPT.md`
3. `TASK_CARDS.md`
4. `SESSION_SHEET.md`
5. `RESULT_TEMPLATE.md`

Selve gaten kræver mindst tre menneskelige sessioner med mindst to forskellige par. Gavemodtageren må ikke bruges som tester.

OQ-008, OQ-009 og OQ-010 har allerede konkrete testprotokoller under `prototype/design-tests/`; de afventer menneskedata og skal ikke “løses” af mere AI-planlægning.

## Når M-Pre er grøn

1. Overfør rådata til `docs/35_M_PRE_GREYBOX_GATE.md`.
2. Behandl OQ-006/OQ-007 på den faktiske evidens.
3. Markér PO-110 færdig i backlog/tracker.
4. Nedskalér PO-039 til VR-genverifikation som foreskrevet i M-Pre-protokollen.
5. Opdatér `repo_status.md` og `docs/36_CHATGPT_WORKSTREAM.md`.
6. Åbn C-020: ChatGPT laver M1 product/UX-handoff.
7. Claude implementerer M1 i Unity — forudsat at M0b også er grøn.

## Når M-Pre er rød

Start ikke M1. Redesign kerneloopets tradeoff efter `docs/35_M_PRE_GREYBOX_GATE.md` og kør gaten igen.

## Fælles stoplinje

**M1 åbner først efter grøn M0b + M-Pre.**

Ingen dyr art-/contentmasseproduktion før de relevante greybox-gates er grønne.
