# Content contract resolution proposal — issue #8

**Ejer:** ChatGPT  
**Dato:** 2026-08-13  
**Status:** Forslag — må ikke ændre accepted scope stiltiende

## Formål

`docs/44_CONTENT_COVERAGE_MATRIX.md` identificerede tre konkrete inkonsistenser mellem scenario-bibel, scenario-data og backlog.

Dette dokument foreslår den mindst risikable løsning for hver, med fokus på:

- ingen skjult Unity-specialkode
- mindst mulig scope-vækst
- bevaret player experience
- sporbar data/content-kontrakt

---

# 1. Intro contract

## Problemet

Scenario-biblen definerer et konkret intro-/onboardingforløb:

1. find partner
2. teleport
3. grab
4. shared heavy crate
5. open crate
6. obtain starter items
7. first fire
8. first effort marker

Men `examples/stormnatten.scenario.json` har:

```json
{
  "id": "INTRO",
  "type": "intro",
  "checkpoint": false,
  "actions": []
}
```

Det efterlader implementationen uklar: er introen data-driven, eller er den et special-case flow i Unity?

## Muligheder

### A — Put every intro interaction into normal action catalog

Fordele:

- maksimal data-uniformitet

Ulemper:

- onboarding sequence er ikke samme type som daily effort actions
- risikerer at overbelaste `actionCatalog` med tutorial-only semantics
- kan skabe kunstig kobling til effort/outcome-systemet

### B — Define an explicit `onboardingSequence` contract

Fordele:

- introen er stadig data-/content-deklareret
- adskiller tutorial progression fra daily action economy
- Claude slipper for hidden special-case product logic
- kan referere til de samme interaction IDs/briefs uden at gøre dem til planning actions

Ulemper:

- kræver schema/content-model extension

### C — Leave INTRO empty and document “Unity handles it”

Fordele:

- hurtigst

Ulemper:

- dårligst source-of-truth
- produktlogik flytter ind i Unity
- strider mod samarbejdsmodellen

## Anbefaling

**B — explicit onboarding sequence.**

Conceptual content contract:

```json
"onboardingSequence": [
  "ONB_FIND_PARTNER",
  "ONB_TELEPORT",
  "ONB_GRAB",
  "ONB_HEAVY_CRATE",
  "ONB_OPEN_CRATE",
  "ONB_FIRST_FIRE",
  "ONB_FIRST_MARKER"
]
```

De konkrete schemafelter/Runtime-model ændrer Claude kun efter en accepteret data-contract change. ChatGPT ejer sequence semantics og interaction briefs.

### Scope effect

Lav/moderat. Dette er primært en kontrakt-/bindingændring, ikke en ny featurefamilie.

---

# 2. Day 3 planning

## Problemet

Scenario-biblen kræver:

> “4-6 minutters sidste planlægning. Spillerne skal vælge mellem signal, lejr, medicin og mad.”

Current scenario phase list går fra `DAY2_PLANNING` til `DAY3_STORM`.

Det betyder, at en af scenariets vigtigste tradeoffs ikke er repræsenteret i data.

## Muligheder

### A — Add `DAY3_PLANNING`

Fordele:

- direkte match med bible/game loop
- same planning mechanic reused
- clean checkpoint/pre-storm boundary
- no hidden special case

Ulemper:

- kræver phase/data update og relevant action availability

### B — Fold Day 3 planning into first storm phase

Fordele:

- færre phases

Ulemper:

- blandet strategic planning og physical crisis
- svækker deliberate final tradeoff
- svært at måle planning separat

### C — Remove Day 3 planning from bible

Fordele:

- mindre content

Ulemper:

- fjerner en central “last window” decision
- svækker payoff til 3-day structure

## Anbefaling

**A — add explicit `DAY3_PLANNING`.**

Conceptual phase:

```json
{
  "id": "DAY3_PLANNING",
  "type": "planning",
  "checkpoint": true,
  "actions": [
    "INT_REINFORCE_ROOF_006",
    "INT_BUILD_SIGNAL_009",
    "INT_TREAT_INJURY_011",
    "INT_SECURE_SUPPLIES_005"
  ]
}
```

Action set er **illustrativt, ikke endeligt**. Availability skal drives af current state/unlocks, og numeric balance venter M3/M4.

### Scope effect

Lav, hvis det genbruger existing planning/action systems og actions. Det er content/data, ikke en ny mechanic.

---

# 3. Fire-start scope

## Problemet

`docs/05` og `docs/09` gør first fire til del af onboarding. Det lærer players:

- simultaneous two-player roles
- physical execution
- fire as camp state

Men `PO-044 Fire-start interaction` er `P1 / Defer`.

Vi kan ikke både love interactionen i canonical intro og samtidig holde implementationen ude af gift scope.

## Muligheder

### A — Promote full PO-044 into gift scope

Fordele:

- bible bevares fuldt

Ulemper:

- scope +16h ifølge nuværende backlog-estimat
- kan påvirke 1.012h accepted gift scope

### B — Add a minimal onboarding fire interaction inside existing release-critical interaction vocabulary

Definition:

- short shield + firesteel sequence
- only required states: tinder → ember → stable fire
- no general-purpose fire-start system, durability, repeated crafting depth
- reused later only if cheap

Fordele:

- bevarer narrative/player-experience function
- mindre end full PO-044 intent
- no need for deeper crafting system

Ulemper:

- kræver backlog re-estimation/new scoped sub-item
- must be explicit so “minimal” does not grow into full system

### C — Remove manual fire-start from onboarding

Alternative:

- players discover already recoverable embers/fire
- first coop task is shielding/fueling rather than ignition

Fordele:

- no new firesteel interaction
- lower scope

Ulemper:

- weaker survival fantasy
- existing firesteel/intro content must change
- loses a clean demonstration of dual-role physical cooperation

## Anbefaling

**B — minimal onboarding fire sequence, explicitly scoped.**

Product contract:

- 10-20 second target interaction
- Player A shields tinder/embers
- Player B performs simple firesteel strike
- 1-3 strike attempts max before assist/fail-forward
- no durability system
- no complex recipe
- no requirement that every later fire is manually restarted
- states needed: tinder / ember / small stable fire

This reuses source/audio/copy already specified in:

- `design/interactions/FIRE_START.md`
- `docs/38_SOURCE_ASSET_MANIFEST.md`
- `docs/39_AUDIO_CUE_MANIFEST.md`
- `docs/40_UX_COPY_AND_LOCALIZATION_CATALOG.md`

### Scope effect

**Requires Anders approval**, because it changes the selected backlog scope unless an existing included task is reduced correspondingly.

Recommended action:

- create a small explicit gift-scope sub-item / replace part of deferred `PO-044`
- estimate it with Claude after M1 interaction foundation exists
- preserve total gift scope by cutting equal/lower-value P1 polish if necessary

Do not silently count all 16h of current PO-044 as included.

---

# 4. Proposed disposition

| Gap | Recommendation | Owner approval needed? | Unity work now? |
|---|---|---:|---:|
| Intro contract | explicit onboarding-sequence data contract | No product preference, but data-contract review needed | No, M1/M3 gated |
| Day 3 planning | add explicit Day 3 planning phase | No material scope increase expected | No, content/data later |
| Fire-start | minimal onboarding fire variant | **Yes — scope impact** | No, estimate/implement after gates |

---

# 5. What ChatGPT can do before approval

Without changing accepted scope, ChatGPT may:

- write onboarding sequence semantics
- write Day 3 planning content/card copy
- keep fire-start source/spec ready
- prepare revised JSON/schema diff as a proposal

ChatGPT should **not**:

- mark PO-044 In
- alter 1.012h total
- claim fire-start is releasecritical accepted

until Anders accepts the scope change.

---

# 6. Definition of done for issue #8

1. intro contract accepted and reflected in data/schema/spec
2. Day 3 planning represented consistently
3. fire-start disposition explicitly accepted (include minimal / remove / other)
4. backlog/scope reconciled if hours change
5. Claude receives the final contract, not this unresolved options document
