# ChatGPT-workstream — PROJECT ØEN

**Ejer:** ChatGPT  
**Projektejer:** Anders  
**Opdateret:** 2026-08-13  
**Scope:** Alt uden for Unity jf. `AI_COLLABORATION_AGREEMENT.md`

## Arbejdsregel

M0b + M-Pre blokerer **M1-implementation**, ikke det parallelle non-Unity-produktionsspor.

Human/device evidence blokerer kun de valg, balanceparametre og acceptance gates, som faktisk kræver evidensen. ChatGPT fortsætter derfor med source-art, audio-source, content authoring, UX/copy, QA, provenance, narrative og handoff-forberedelse uden at ændre Unity-runtime.

Den machine-readable produktionsstatus er:

`content/source_inventory.source.json`

---

# Aktuelle gates

## M0b — Claude / Unity

Tracker: GitHub issue #3. Cross-device/device evidence mangler fortsat.

## M-Pre — ChatGPT / produkt

Tracker: GitHub issue #7. Testpakken er ready-to-run; der mangler tre menneskelige sessioner med mindst to forskellige par.

## Content contract

Tracker: GitHub issue #8.

- intro → eksplicit onboarding-sequence foreslået
- Day 3 → eksplicit planning phase foreslået
- minimal fire-start → source/spec/reference klar, men gave-scope kræver Anders' disposition

Proposal-data under `content/proposals/` er fortsat `proposal-not-canonical`.

---

# Leveret non-Unity foundation

Produkt/design/QA-pakken dækker bl.a.:

- source asset/audio manifests
- dansk UX/copy/localization
- personalization/privacy/neutral fallback
- human QA M1-M9
- IP/provenance
- Stormnatten content coverage og 10-event catalog
- visual style/UI IA
- gift/release-flow
- telemetry/metrics
- backlog ownership overlay
- narrative continuity
- content-contract proposals
- source production batch plan

Interaction handoffs findes for planning, shelter, fire, ravine og stormfinale.

---

# Faktisk source-art på main

## A1

Gameplay-readable UI/source kit med action/status-symboler, effort markers, action-card base og interaction feedback.

## Neutral fallback

Fictional chart, compass, route card og signal tag. Neutral baseline er source-komplet bortset fra faktisk radiooptagelse; runtime fallback ejes af Claude.

## A2 core interaction source

- briefs + concept sheets for core props
- individuelle source masters:
  - `ITM_FIRESTEEL_001.svg`
  - `ITM_TINDER_001.svg`
  - `ITM_ROPE_COIL_001.svg`

Firesteel-reference gør **ikke** issue #8 canonical.

## A3 storm

Rain/debris/embers/smoke/impact/wetness/storm-phase source references.

## A4 camp

Camp layout/state plus separate source references for:

- wreck landmark
- camp ground/material readability
- radio states
- signal frame progression

## B1

Environment/readability source for jungle/ravine/ridge, ravine anchor/guide markers samt resource items:

- wood
- fiber
- herbs
- food
- general supplies

Ny world-prop source:

- `PRP_SUPPLY_CRATE_001.svg` — sealed/open shared-resource container; visuelt QA'et og rettet før merge

## B2

Event-presentation source for alle ti events plus machine-readable event→presentation mapping.

## A5

### External source meshes

`source_art/props/a5/`:

- `PRP_WIND_SHIELD_001.obj`
- `PRP_DRY_FUEL_CACHE_001.obj`
- `PRP_SIGNAL_FUEL_001.obj`

### Source items

`source_art/items/a5/`:

- `ITM_CLOTH_001.svg`
- `ITM_MAP_FRAGMENT_001.svg`
- `ITM_RADIO_BATTERY_001.svg`

### Release UI source set

`source_art/ui/a5/`:

- join-code
- reconnect
- first-launch setup
- pause
- connected/ready
- subtitle band

Unity layout/input/accessibility binding og headset-distance QA forbliver Claude.

---

# Audio/source-status

## AU-1

Deterministisk generator til 12 korte UI/system feedback cues med CI-verifikation.

## Foley

`content/audio/foley_recording_queue.source.json` er recording-ready med cue-ID, variantantal, filnavne, target length og 48 kHz / 24-bit krav.

## Ambience

`content/audio/ambience_acquisition_queue.source.json` dækker wind L0-L3, rain, beach/camp, jungle, ravine og camp night.

Naturalistisk Foley/ambience er ikke markeret som produceret WAV før reel recording/source acquisition og provenance findes.

## Radio VO

`content/audio/radio_vo_recording_queue.source.json` er recording-ready:

- 9 cues
- 3 takes per cue
- dry 48 kHz / 24-bit mono masters
- delivery/length/localization/provenance QA

## Musik

Direction/cue-sheet er klar; faktisk composition/source er fortsat åben og bør ikke foregives færdig før timing/evidence gør cue-længder meningsfulde.

---

# Machine-readable content

Aktuelle source contracts omfatter:

- dansk localization
- Stormnatten actions + placeholder cost mirror
- ten-event authoring
- event→presentation mapping
- neutral personalization
- onboarding/Day 3 proposals
- Foley/ambience/radio recording queues
- after-action presentation contract
- samlet source inventory

`content/outcomes/after_action.presentation.source.json` binder Core's authoritative causal data til produktregler for outcome, causal highlights, team story, retry/replay og accessibility. Individuelle titler er `off` indtil OQ-010 støtter dem.

---

# CI / kvalitet

Aktive guards omfatter bl.a.:

- non-Unity source validation
- handoff validation
- Core tests
- action placeholder-cost mirror
- AU-1 source regeneration/validation
- event presentation validation

Source-art bliver visuelt QA'et før merge, når layout/readability kræver det. Senest fangede QA tekst-overflow i supply-crate source, som blev rettet før merge.

---

# Repo hygiene

Tidligere tracked `src/**/bin/` build/test outputs er ryddet fra repoet via PR #12.

- 89 genererede filer fjernet
- `.gitignore` dækkede allerede `src/**/bin/`
- Core tests var grønne efter cleanup

Denne gæld er lukket.

---

# Evidens der stadig ikke må opfindes

- M-Pre / issue #7
- OQ-008 fairness/randomness
- OQ-009 role assignment
- OQ-010 after-action competition
- M3/M4 numeric balance/tuning
- M3-M9 human gates
- M0b/device gates

---

# Næste aktive ChatGPT-bølge

Prioritet, medmindre repo/evidence ændrer den:

1. fortsæt stabile B1/world source assets uden at duplikere eksisterende environment/ravine source
2. reconcile source inventory/provenance efter hver produceret batch
3. få source-inventory path/produced-status automatisk valideret i CI, når connectoren tillader validator-scriptet
4. actual audio source production/acquisition: Foley → ambience → radio VO; ingen fake WAV-status
5. yderligere machine-readable presentation/content contracts, hvor de reducerer Unity-gætteri
6. richer environment/polish først når geometry/device evidence reducerer rework-risiko
7. private personalization source uden for public repo senere
8. M1 implementation handoff når både M0b + M-Pre er grønne

## Kendte connector-blokeringer

- `ITM_EMBER_CARRIER_001` source blev genereret som blob, men commit blev konsekvent filtreret; den tælles derfor **ikke** som leveret.
- repair-mallet source blev genereret som blob, men er ikke committed; den tælles derfor **ikke** som leveret.

Der omgås ikke sikkerhedsfiltre, og ucommittede artifacts tælles aldrig som produktion.

---

# Arbejdsregel ved “kør videre”

1. kontrollér seneste repo/issues/CI
2. brug `content/source_inventory.source.json` som produktionsstatus
3. tag højeste ublokerede non-Unity-opgave
4. ændr ikke Unity-filer
5. producer konkrete artifacts/source frem for kun planer
6. QA egne leverancer og registrér provenance
7. opfind aldrig human/device-evidens

> **Gates bestemmer hvad der må låses. De betyder ikke, at ChatGPTs produktionsspor skal stå stille.**
