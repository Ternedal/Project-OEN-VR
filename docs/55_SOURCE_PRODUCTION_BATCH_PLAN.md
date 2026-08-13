# Source production batch plan — PROJECT ØEN

**Ejer:** ChatGPT  
**Unity integration:** Claude  
**Dato:** 2026-08-13

## Formål

Omsætte manifests til konkrete produktionsbatches, så source art/audio kan produceres i en rækkefølge der maksimerer testværdi og minimerer rework.

Dette dokument ændrer ikke gameplay-gates. Det bestemmer **hvad der giver mening at producere først** på ChatGPT-siden.

---

# Batchregel

Prioritet gives efter:

1. gameplay-readability
2. antal interactions der genbruger asset/cue
3. hvor stabil designkontrakten er
4. hvor lidt assetet afhænger af final level geometry
5. release 1 relevance

Derfor kommer icons/markers/rope/fire/shelter reference før full jungle beauty pass.

---

# A1 — Gameplay-readable source kit

**Kan produceres før M-Pre/M1, fordi assets er små, genbrugelige og designstabile.**

## 2D/UI source

- `UI_PLAYER_SYMBOL_A_001`
- `UI_PLAYER_SYMBOL_B_001`
- `UI_ACTION_ICON_SHELTER_001`
- `UI_ACTION_ICON_FIRE_001`
- `UI_ACTION_ICON_FOOD_001`
- `UI_ACTION_ICON_SIGNAL_001`
- `UI_ACTION_ICON_MEDICAL_001`
- `UI_ACTION_ICON_EXPLORE_001`
- `UI_STATUS_HEALTH_001`
- `UI_STATUS_FATIGUE_001`
- `UI_STATUS_INJURY_001`
- `UI_STATUS_WET_COLD_001`
- `TEX_WARNING_SHAPE_001`
- `TEX_SUCCESS_SHAPE_001`
- `TEX_PARTIAL_SHAPE_001`

## Physical/token source

- effort marker design A/B
- action-card base art
- rope tie/snap symbol set
- repair-node symbol

## Why first

- feeds planning mockups and future Unity UI
- minimal dependence on scene geometry
- accessibility can be QA'ed visually early

## Acceptance

- readable at reduced size
- shape + color differentiation
- consistent visual family
- source/provenance registered

---

# A2 — Core interaction source kit

**Produce as concept/source package, not final optimized Unity meshes.**

- `PRP_HEAVY_CRATE_001`
- `PRP_FIREPIT_001`
- `ITM_FIRESTEEL_001`
- `ITM_TINDER_001`
- `PRP_WIND_SHIELD_001`
- `PRP_SHELTER_BEAM_001`
- `PRP_SHELTER_ROPE_001`
- `PRP_SHELTER_TARP_001`
- `PRP_PLAN_TABLE_001`
- `ITM_ROPE_COIL_001`

## Source deliverable level

For each:

- silhouette/reference sheet
- key states
- intended grasp/interaction zones at product level
- material family
- color/shape cues

## Why before full environment

These props define interaction language and can be handed to Claude regardless of final island layout.

---

# A3 — Storm source kit

Prepare after/alongside M1 but before M5 implementation needs it.

## Visual/VFX source

- `VFX_RAIN_001`
- `VFX_WIND_DEBRIS_001`
- `VFX_FIRE_EMBERS_001`
- `VFX_FIRE_SMOKE_001`
- `VFX_IMPACT_001`
- `VFX_WETNESS_REFERENCE_001`
- `VFX_STORM_PHASE_REF_001`

## Structural states

- tarp dry/wet/torn
- beam intact/damaged
- signal stage 0-3
- fire dead/ember/small/strong

## Audio first pass

- wind L0-L3
- heavy rain
- fire state loops
- shelter creak low/high
- rope tension low/good/high
- partial collapse
- signal ignition/acknowledgement

## Gate

Source production can happen before final storm implementation; final mix/VFX polish waits device performance evidence.

---

# A4 — Release 1 camp environment

Target M5, after core geometry is sufficiently stable.

- beach/camp mood/reference
- wreck hero reference
- camp ground/material set
- shelter progression visuals
- radio
- signal frame
- neutral ending crate

## Avoid too early

Do not spend on:

- dense foliage variation
- noninteractive clutter
- tiny props
- highly specific final lighting bake assumptions

until greybox proves spatial layout.

---

# B1 — Full scenario environment

M6 support:

- jungle path kit
- ravine kit
- ridge vista
- gathering props
- food/fiber/herb resources
- ravine anchor/guide set

This batch should wait enough spatial evidence that its modular dimensions are useful.

---

# B2 — Event presentation source

- animal threat abstract cues
- roof leak state
- tool break state if system remains in scope
- dry fuel cache
- extra herb opportunity
- distant smoke cue
- radio narrative presentation

No full animal AI/art commitment required.

---

# C — Polish

- richer avatar/hand variations
- secondary environment variation
- additional material polish
- extra one-shot audio variants
- richer post-storm epilogue dressing

Only after functionality/performance holds.

---

# P — Private personalization

Produced outside repo after neutral package is green.

- ending photo
- final voice message
- memento 1-3

Follow `docs/41_PERSONALIZATION_PACKAGE_SPEC.md`.

---

# Audio production batches

## AU-1 — Interaction feedback

Highest priority:

- grab/place
- marker planning
- rope tension
- shelter snap/creak
- fire states
- reconnect/system UI

## AU-2 — Storm bed

- wind layers
- rain layers
- collapse
- signal/finale
- minimal music layers

## AU-3 — Scenario/world

- beach/camp
- jungle
- ravine/ridge
- animal threat
- radio source voice

## AU-4 — Polish

- extra variants
- richer adaptive music
- detailed environmental sweeteners

---

# Production tracker template

| ID | Batch | Source brief | Production | QA | Provenance | Claude handoff |
|---|---|---|---|---|---|---|
| `UI_PLAYER_SYMBOL_A_001` | A1 | Ready | Not started | — | Pending | — |
| `UI_PLAYER_SYMBOL_B_001` | A1 | Ready | Not started | — | Pending | — |
| `PRP_HEAVY_CRATE_001` | A2 | Ready | Not started | — | Pending | — |
| `PRP_FIREPIT_001` | A2 | Ready | Not started | — | Pending | — |

The table expands as actual files are produced.

---

# Source production acceptance

Do not mark a batch complete because files merely exist.

Batch complete means:

- all required IDs produced
- visual/audio family consistent
- source masters preserved
- readability QA passed
- provenance recorded
- filenames/IDs stable
- handoff package can be understood by Claude without product invention

---

# Immediate next source-production candidate

**A1 icon/symbol family** is the lowest-rework, highest-leverage first actual art batch.

It can be produced independently of final Unity geometry and used in planning/UI mockups immediately.
