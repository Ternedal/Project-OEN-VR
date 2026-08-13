# A3 storm source specifications — PROJECT ØEN

**Owner:** ChatGPT  
**Runtime VFX/rendering:** Claude  
**Dato:** 2026-08-13  
**Batch:** A3 fra `docs/55_SOURCE_PRODUCTION_BATCH_PLAN.md`

## Formål

Definere stormens visuelle source-materiale og intensitetsprogression før runtime VFX bygges i Unity.

Dette dokument beskriver **hvad stormen skal kommunikere** og hvilke source textures/reference-states der er nødvendige. Claude vælger particle systems, shaders, post effects, pooling og performance implementation.

---

# 1. Storm progression

Stormen skal føles som én sammenhængende front, ikke fem forskellige effect presets.

## S0 — warning / pre-storm

- stronger directional wind
- foliage/tarp response
- cooler ambient value
- few loose particles/debris
- no heavy rain wall yet

Player read:

> “Noget er på vej.”

## S1 — wind phase

- frequent gusts
- tarp and rope motion is primary feedback
- light debris crosses environment
- visibility still good enough for repair points

Player read:

> “Strukturen er under pres.”

## S2 — rain/fire phase

- rain becomes dominant
- surface wetness visible
- ember/fire remains a strong warm anchor
- avoid full-screen opacity that hides hands/targets

Player read:

> “Ilden er sårbar.”

## S3 — consequence/peak pressure

- combine existing layers rather than inventing a new visual language
- local event VFX may appear (food disturbance, shelter failure, etc.)
- intensity high but task targets remain readable

Player read:

> “Tidligere problemer rammer nu.”

## S4 — collapse

- one short localized debris/dust/cloth response
- structure movement provides the main drama
- impact effect must clear quickly

Player read:

> “Grib den sammen — nu.”

## S5 — dawn/signal

- precipitation/wind begins to break enough to create contrast
- signal/ember/fire becomes focal
- horizon value opens gradually
- rescue acknowledgement occurs before full calm

Player read:

> “Det her er vinduet.”

---

# 2. `VFX_RAIN_001`

## Source deliverables

- 1–2 streak textures with transparent background
- optional droplet/splash sprite set for close world contacts
- intensity reference sheet S0/S1/S2/S3/S5

## Visual rules

- directional with wind
- not a uniform screen overlay
- keep centre interaction zone readable
- no constant bright streak clutter

## Accessibility

Rain intensity cannot be the only cue for storm phase; phase title/world/audio also communicate state.

---

# 3. `VFX_WIND_DEBRIS_001`

## Source deliverables

Small atlas of 4–8 silhouettes:

- leaf fragment
- small cloth/fiber strip
- light twig
- sand/dust fleck group

## Rules

- use sparse readable shapes
- no large debris crossing the player's face repeatedly
- debris direction supports wind direction
- gameplay target zones stay clear

---

# 4. `VFX_FIRE_EMBERS_001`

## Source deliverables

- 3–5 ember sprites
- glow/value reference
- ember-to-small-fire transition reference

## Rules

- ember source remains readable under rain
- fewer larger readable embers preferred to noisy spark cloud
- no bright screen-filling bloom source assumption

---

# 5. `VFX_FIRE_SMOKE_001`

## Source deliverables

- 3–5 soft smoke sprite shapes
- dry/small vs wet/smothered reference

## Product state

- strong stable fire: lighter consistent smoke
- wet/smothered: denser lower unstable smoke

Smoke must not obscure the partner or interaction target for long.

---

# 6. `VFX_IMPACT_001`

## Source deliverables

- dust puff sprite
- small wood-fiber/debris shapes
- optional rope/fiber snap accent

## Use

- beam shift
- partial collapse
- heavy placement

## Rule

Impact is brief punctuation; physical object movement remains the main event.

---

# 7. `VFX_WETNESS_REFERENCE_001`

This is a **look/state reference**, not a mandate for one shader solution.

Required comparisons:

- tarp dry → wet
- wood dry → wet
- sand dry → rain-darkened
- rock dry → wet

Source goals:

- value darkens moderately
- highlights/roughness intent increases where appropriate
- no mirror-like plastic wetness
- state remains compatible with stylized materials

Claude owns actual wetness shader/material implementation.

---

# 8. `VFX_ROPE_STRAIN_001`

Optional source accent:

- tiny fiber/dust flecks at extreme tension

Must never be the primary tension signal.

Primary signals remain:

- rope geometry/tension
- source guide shape
- audio

---

# 9. Storm sky / horizon reference

No photoreal sky requirement.

Source reference stages:

- calm muted blue-grey
- pressure front / darker horizon band
- storm overcast
- dawn break behind cloud

Signal phase should gain a visual direction toward the sea/horizon without becoming a cutscene.

---

# 10. Readability budget

During peak storm, the following must remain visually readable:

1. partner hands/head presence
2. current shared object
3. rope/snap/repair target
4. fire/ember state
5. signal target in final phase

If VFX masks one of these, reduce VFX density before adding more UI.

---

# 11. Performance-aware source design

Source-side principles supporting Quest 2:

- small reusable sprite families
- no requirement for unique high-resolution simulation textures per phase
- reuse rain/wind/fire families with parameter changes
- source texture transparency kept simple where possible
- world motion/prop animation carries part of the storm intensity

Runtime batching/particles/overdraw measurements belong to Claude.

---

# 12. A3 source package structure

Planned:

```text
source_art/vfx/a3/
  README.md
  PROVENANCE.md
  STORM_PHASE_REFERENCE.md
  VFX_RAIN_001.*
  VFX_WIND_DEBRIS_001.*
  VFX_FIRE_EMBERS_001.*
  VFX_FIRE_SMOKE_001.*
  VFX_IMPACT_001.*
  VFX_WETNESS_REFERENCE_001.*
```

File extension depends on the produced source (SVG/PNG/reference sheet). Unity-derived/runtime assets are Claude's responsibility.

---

# 13. Acceptance before Claude handoff

- storm phases read as progression of one system
- interaction targets remain readable at S3/S4
- source sprites have transparent masters where appropriate
- wetness references do not imply a specific Unity shader
- all source files have provenance
- no copyrighted storm/photo texture is used without license record
- source pack can scale down if Quest 2 overdraw/performance requires it
