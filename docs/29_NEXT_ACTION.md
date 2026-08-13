# Næste handling

**Opdateret:** 2026-08-13

Projektet har nu to parallelle arbejdsstrømme jf. `AI_COLLABORATION_AGREEMENT.md`.

## Claude — Unity-sporet

Claude ejer M0b-arbejdet i Unity.

Næste verificerbare gate er de resterende to-headset-tests i `src/unity/RUNBOOK_FUSION.md` og `config/COMPATIBILITY_MATRIX.md`:

1. head/hands replikeres mellem to klienter
2. handshake afviser version/content mismatch korrekt
3. delt kasse går i `HeldByTwo` og har identisk state
4. 10× Q2↔Q3-løft uden permanent desync (PO-025)
5. 72 Hz i minimal netværksscene
6. reconnect-/standby-vinduet måles (CR-009)

Claude må ikke markere disse som verificeret uden faktisk device-evidens.

## ChatGPT — produkt/design/asset-sporet

Den næste produktgate er **M-Pre** (ADR-022 / PO-110).

Ready-to-run-materialet ligger i `prototype/m-pre/`:

1. `README.md`
2. `FACILITATOR_SCRIPT.md`
3. `TASK_CARDS.md`
4. `SESSION_SHEET.md`
5. `RESULT_TEMPLATE.md`

Selve gaten kræver mindst tre menneskelige sessioner med mindst to forskellige par. Gavemodtageren må ikke bruges som tester.

Mens M-Pre afventer testere fortsætter ChatGPT efter `docs/36_CHATGPT_WORKSTREAM.md`, først med OQ-008-testdesign og derefter de øvrige ublokerede ikke-Unity-opgaver.

## Når M-Pre er grøn

1. Overfør rådata til `docs/35_M_PRE_GREYBOX_GATE.md`.
2. Behandl/luk OQ-006 og OQ-007 i `docs/19_OPEN_QUESTIONS.md`.
3. Markér PO-110 færdig i backlog/tracker.
4. Nedskalér PO-039 til VR-genverifikation som foreskrevet i M-Pre-protokollen.
5. ChatGPT laver M1 produkt-/UX-handoff.
6. Claude implementerer M1 i Unity.

## Når M-Pre er rød

Start ikke M1-gameplayarbejde. Redesign kerneloopets tradeoff og kør M-Pre igen.

## Fælles regel

Ingen dyr art-/contentmasseproduktion før de relevante greybox-gates er grønne. Source-assets og lyd produceres i den rækkefølge, som den godkendte workstream og roadmap kræver.
