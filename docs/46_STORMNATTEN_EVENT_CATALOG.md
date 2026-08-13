# Stormnatten event authoring catalog

**Ejer:** ChatGPT  
**Scenario:** `SCN_STORMNATTEN_001`  
**Dato:** 2026-08-13  
**Status:** Content authoring v0.1; numeric tuning waits M3/M4 evidence

## Formål

Scenario-biblen kræver mindst 10 event definitions. Repoet har hidtil kun én konkret standalone event JSON (`EVT_OPEN_FOOD_001`).

Dette katalog definerer den **canonical authoring-intention** for de ti events, før de alle gøres til runtime-data.

## Tuningregel

- triggers/tal her er qualitative eller fixture-level
- final probabilities/severity waits M3/M4 playtest
- OQ-008 controls randomness policy
- fail-forward is mandatory
- every delayed consequence must have an understandable earlier cause

---

# Event index

| ID | Navn | Type | Primær funktion |
|---|---|---|---|
| `EVT_OPEN_FOOD_001` | Åben/usikret mad | delayed setup | skaber `SCENT_HIGH` |
| `EVT_ANIMAL_CAMP_001` | Dyr ved lejren | delayed consequence | cash-out af scent valg |
| `EVT_SPLINTER_001` | Splint/småskade | immediate consequence | introducerer injury/treatment |
| `EVT_UNTREATED_WOUND_001` | Ubehandlet sår | delayed consequence | gør treatment tradeoff konkret |
| `EVT_ROOF_LEAK_001` | Taglækage | camp consequence | shelter choice → wet/cold |
| `EVT_TOOL_BREAK_001` | Knækket værktøj | resource/quality consequence | tool quality pressure |
| `EVT_DRY_FUEL_FOUND_001` | Tørt brændsel | positive opportunity | earned relief / fire prep |
| `EVT_EXTRA_HERBS_001` | Ekstra urter | positive opportunity | treatment buffer |
| `EVT_DISTANT_SMOKE_001` | Røg på afstand | narrative teaser | world mystery, no MVP branch |
| `EVT_RADIO_FRAGMENT_001` | Radiofragment | narrative progression | ship route / time pressure |

---

# 1. `EVT_OPEN_FOOD_001` — Åben/usikret mad

## Trigger intention

At dusk when food security is weak and players did not secure supplies.

Existing example JSON already defines:

- `SCENT_HIGH`
- increased camp threat
- optional immediate corrective choice
- delayed `EVT_ANIMAL_CAMP_001` at Night 2

## Telegraph

Before consequence:

- food container visually not sealed
- small sound/visual signs, not a hidden purely numeric flag

## Presentation

Copy:

- `event.food_open.warning`

Audio:

- use food/container disturbance cue family

## Player agency

If the event is discovered before Night 2, players may spend effort/action to secure it. Exact cost is tunable.

## Fail-forward

If they do nothing, game continues; risk returns later.

## Status

Standalone JSON exists. Needs alignment of cue IDs with `docs/39` when converted from fixture to production content.

---

# 2. `EVT_ANIMAL_CAMP_001` — Dyr ved lejren

## Trigger intention

Night 2 if `SCENT_HIGH` remains active.

## Purpose

Make Day 1 food-security choice return as a physical two-player consequence.

## Telegraph

Before full event:

- distant rustle/call
- food/container movement
- fire/camp reaction

## Roles

### Player A — deterrence/fire

Keeps fire/noise/light deterrent active.

### Player B — secure food

Closes/moves/repairs food storage.

Both roles must affect severity/outcome.

## Outcomes

### Good resolution

Animal retreats; food mostly safe.

### Partial

Animal retreats but food/shelter state worsens or time/fatigue cost occurs.

### Fail-forward

Food is lost/damaged or camp threat rises; scenario continues.

No combat system required.

## Assets

- food parcel/storage
- camp/fire
- optional abstract shadow/foliage reaction; no full creature required

## Audio

- `SFX_ANIMAL_DISTANT_001`
- `SFX_ANIMAL_CAMP_APPROACH_001`
- `SFX_ANIMAL_RETREAT_001`
- `SFX_FOOD_DISTURBED_001`

## Copy

- `event.animal.approach`

## Human gate

M4 tester should explain: “this happened because we left food unsecured.”

---

# 3. `EVT_SPLINTER_001` — Splint/småskade

## Trigger intention

A low-quality or poorly executed wood/tool action creates a minor hand injury.

## Purpose

Introduce injury as a manageable consequence, not a punishment spiral.

## Telegraph

- short impact/wood feedback
- visible player status change
- brief wrist/status cue

## Effects intention

- add minor injury tag
- small immediate cost
- unlock/relevance for `INT_FIND_HERBS_008` / `INT_TREAT_INJURY_011`

## Player agency

Players can choose whether to spend later effort treating it.

## Fail-forward

The current action still produces partial progress.

## Copy

Use short player-state wording, not graphic injury description.

## Safety/tone

No gore. Injury is readable but not visually disturbing.

---

# 4. `EVT_UNTREATED_WOUND_001` — Ubehandlet sår

## Trigger intention

A known injury remains untreated into a later wet/cold phase or storm threshold.

## Purpose

Cash out the earlier decision to postpone treatment.

## Telegraph

- injury remained visible in status
- wet/cold warnings before severity increases

## Effects intention

- add `INFECTION_RISK` or equivalent condition tag
- increase fatigue/penalty in later physical sequence
- never directly incapacitate from one hidden check

## Player roles if presented physically

One player treats/stabilizes; partner holds light/material/support if a treatment opportunity occurs.

## Copy

- `event.injury.untreated`

## Human gate

Player should be able to say: “we chose not to treat the injury.”

---

# 5. `EVT_ROOF_LEAK_001` — Taglækage

## Trigger intention

Night/storm if shelter remains below a tested threshold / `SHELTER_WEAK`.

## Purpose

Turn shelter quality into a concrete problem before/inside storm.

## Telegraph

- tarp begins to flap
- water drip/wetness
- creak/audio stress

## Roles

- stabilizer holds/tensions cover
- repairer closes/fastens 1-2 repair points

## Outcomes

Success:

- leak stopped

Partial:

- leak reduced but player/camp becomes wet

Fail-forward:

- `WET/COLD` modifier persists; game continues

## Assets/audio

Shelter/tarp/rope + heavy rain + creak/tarp cues.

## Copy

- `event.roof_leak.warning`

---

# 6. `EVT_TOOL_BREAK_001` — Knækket værktøj

## Trigger intention

Low durability/quality or severe partial failure on a relevant crafting/repair action.

## Purpose

Create a resource/quality consequence without softlocking progress.

## Rule

A broken tool may:

- reduce efficiency
- require an improvised alternative
- consume extra supplies/time

It must not make a required finale action impossible with no fallback.

## Telegraph

- visible damage before break where possible
- break sound + object state

## Player agency

Players can choose to repair/replace/improvise if the opportunity is available.

## Copy

- `event.tool.broken`

## Scope caution

Tool durability is deferred in current backlog (`PO-043`), so this event stays content-authoring-only until that system is confirmed in scope.

---

# 7. `EVT_DRY_FUEL_FOUND_001` — Tørt brændsel fundet

## Trigger intention

Positive exploration/gathering opportunity, especially after good scouting or camp preparation.

## Purpose

Give positive consequences and relief; event system must not only punish.

## Effect intention

- add usable dry-fuel opportunity/tag/resource
- make storm fire recovery easier

## Presentation

World-readable cache protected from rain.

## Copy

- `event.dry_fuel.found`

## Rule

The reward should be concrete in gameplay, not just score.

---

# 8. `EVT_EXTRA_HERBS_001` — Ekstra urter

## Trigger intention

Good exploration/foraging or contextual opportunity.

## Purpose

Create a small buffer against injury without removing the treatment tradeoff.

## Effect intention

- additional herb/treatment capacity
- optional prevention of later severe condition

## Presentation

Readable plant/forage area + inventory/world response.

## Copy

- `event.herbs.extra`

## Accessibility

Plant identification cannot rely on subtle color difference alone; use shape/placement/icon if required.

---

# 9. `EVT_DISTANT_SMOKE_001` — Røg på afstand

## Trigger intention

Exploration result Day 1/2.

## Purpose

Make the island feel larger and seed future content without creating a fake branch in MVP.

## Presentation

- distant smoke column / horizon cue
- optional short player comment/journal note

## Rule

MVP must **not** imply that players can reach a fully implemented settlement/NPC branch.

Good wording:

> “Der er røg i det fjerne.”

Avoid:

> “Find de andre overlevende nu.”

unless that route actually exists.

## Copy

- `event.smoke.distant`

## Future hook

May seed later scenario/DLC, but no current gameplay dependency.

---

# 10. `EVT_RADIO_FRAGMENT_001` — Radiofragment

## Trigger intention

Narrative checkpoint at Night 1 / Day 3 based on scenario progression, not arbitrary random roll.

## Purpose

Create time pressure and clear rescue objective.

## Night 1 content

Radio fragment reveals:

- shipping route resumes in roughly two days
- no guaranteed rescue

Source lines:

- `vo.radio.night1.01-03`

## Day 3 content

Second fragment confirms:

- passage at dawn
- poor visibility
- visual signal required

Source lines:

- `vo.radio.day3.01-03`

## Rule

Critical narrative progression should not be missable because of random event selection.

## Accessibility

All radio lines subtitled; objective is also represented visually/through planning information.

---

# Event-system content rules

## Positive/negative mix

At least some event selections should provide:

- opportunity
- relief
- information

not only damage/threat.

## Telegraphing

Delayed consequences need earlier clues so the after-action report confirms a story the players can recognize.

## No hidden hard fail

A single hidden random event should not directly produce an unrecoverable loss unless the players already had explicit, severe state warnings.

## Two-player rule

Any physical event sequence lasting more than a few seconds must define meaningful contributions for both players.

## Presentation fallback

Every event needs a fallback that can still communicate the state if a noncritical art/audio asset is unavailable.

## Localization

Event presentation uses keys from `docs/40`; new text must add a key rather than hardcoded runtime copy.

---

# Next authoring step

Once M3/M4 data model and tuning evidence are ready:

1. convert the catalog entries to `EventDefinition` JSON/data
2. validate against `schemas/event.schema.json`
3. add them to event pools
4. run dead-end/cycle validation
5. run A/B cause-effect human tests

The authoring intention above can be used immediately by Claude for interface expectations, but final numeric trigger/severity values are deliberately not locked here.
