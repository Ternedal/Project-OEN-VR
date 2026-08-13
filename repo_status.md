# Repository status

**Opdateret:** 2026-08-13

## Baseline

- Baseline: **v2.1**.
- Alle 10 reviewfund er lukket.
- Quest 2 = performance-/kvalitetsgulv.
- Quest 3/3S = enhanced parity.
- Quest 1 = droppet runtime/testlane (`DROP_Q1_RUNTIME`).
- Gaveversion = **1.012 t**; 439 t deferred efter v1.0.
- M5 = Release 1.
- Arbejdsdeling: `AI_COLLABORATION_AGREEMENT.md` — Claude = Unity, ChatGPT = alt andet.

---

# Aktuelle gates

## M0b — Claude/Unity

Tracker: GitHub issue #3.

Per-client feasibility er dokumenteret. Cross-device evidence mangler fortsat:

1. head/hands replication
2. handshake mismatch rejection
3. shared box korrekt to-player state
4. 10× Q2↔Q3 lift uden permanent desync
5. 72 Hz minimal network scene
6. standby/reconnect measurement
7. compatibility matrix completion

## M-Pre — ChatGPT/produkt

Tracker: GitHub issue #7.

Ready-to-run package findes i `prototype/m-pre/`; menneskedata mangler.

## Content contract

Tracker: GitHub issue #8.

Løsningsforslag:

- intro → explicit onboarding sequence
- Day 3 → explicit planning phase
- minimal fire-start → source/spec ready, men gift-scope kræver Anders' disposition

Proposal-data under `content/proposals/` er mærket `proposal-not-canonical`.

---

# Core / Unity

`src/ProjectOen.Core` har senest dokumenteret **146 passed, 0 failed**.

Unity/Fusion-laget ejes af Claude. Den gamle status “Fusion ukompileret” er historisk og ikke længere gældende; M0b cross-device er den reelle åbne tekniske gate.

---

# ChatGPT / non-Unity — aktiv produktion

M0b + M-Pre blokerer **M1-implementation**, ikke ChatGPTs source/content/UX/QA-arbejde.

Aktuel source of truth: `docs/36_CHATGPT_WORKSTREAM.md`.

## Produkt/design/QA leveret

Dokumentpakke `docs/37`–`docs/56` dækker bl.a.:

- non-Unity gap audit
- source asset manifest
- audio cue manifest
- dansk UX/copy/localization
- personalization/privacy
- human QA M1-M9
- IP/provenance
- Stormnatten content coverage
- gift/release flow
- 10-event authoring catalog
- visual style bible
- UI information architecture
- after-action/replay
- product telemetry
- backlog ownership/status overlay
- content-contract proposal
- narrative continuity
- neutral fallback package
- source production batches
- A2 core prop source specs

## Interaction handoffs

`design/interactions/`:

- planning table
- shelter reinforcement
- fire start
- ravine rescue
- storm finale

## Machine-readable source content

`content/`:

- `localization/da.source.json`
- `actions/stormnatten.actions.source.json`
- `events/stormnatten.events.source.json`
- `personalization/neutral_profile.source.json`
- proposal-data for onboarding/Day 3

## Authoring templates

`templates/content/`:

- event
- interaction
- action card
- source asset handoff
- audio cue handoff

---

# Faktisk source-art på main

## A1 UI/source kit

`source_art/ui/a1/` indeholder projekt-originale SVG source masters for:

- Player A/B identity
- action/status icons
- effort markers
- action-card base
- wrist status frame
- snap/grip/tension/repair feedback
- warning/success/partial state shapes

Pakken er visuelt QA'et, efterfølgende rettet hvor nødvendigt og har egen provenance.

## Neutral fallback source-art

`source_art/neutral/`:

- fictional ending chart
- compass memento
- route card
- signal tag

Alle er `OWN` provenance og kræver ingen private eller tredjeparts assets.

---

# Non-Unity CI

Ny validator:

- `tools/validate_non_unity_sources.py`
- `.github/workflows/non-unity-source-validation.yml`

Validerer JSON/source contracts, localization references, icon/audio IDs, SVG parse/viewBox, provenance, proposal isolation og simple private-content guardrails.

**Første CI-run er grøn.**

---

# Hvad der fortsat mangler på ChatGPT-siden

Der er fortsat betydeligt arbejde:

1. A2 prop handoff/source packages
2. A3 storm VFX/reference source
3. AU-1 actual audio source production/strategy
4. central provenance expansion for producerede packs
5. fortsat machine-readable authoring
6. neutral radio VO source/strategy
7. senere A4/B environment source efter geometry/gates er stabile nok
8. private personalization source senere
9. human design/playtest evidence
10. M1 handoff assembly når M0b + M-Pre er grønne

## Gategrænse

**M1 åbner først efter grøn M0b + M-Pre.**

Det stopper ikke non-Unity-produktionssporet.

---

# Anders' parallelle handlinger

- Claude fortsætter issue #3.
- M-Pre testerpar skaffes til issue #7, når det passer.
- Fire-start-scope i issue #8 kræver Anders' beslutning, før det må tælle ind i gaveversionen.

Resten af den ublokerede ChatGPT-kø fortsætter uden at vente på de tre punkter.
