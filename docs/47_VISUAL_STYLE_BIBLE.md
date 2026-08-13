# Visual style bible — PROJECT ØEN

**Creative owner:** ChatGPT  
**Unity rendering/integration:** Claude  
**Dato:** 2026-08-13

## 1. Visuel tese

PROJECT ØEN skal ligne et sted, to mennesker **kan forstå med kroppen**.

Stilen er:

- stiliseret
- håndbygget
- rå men varm
- dramatisk uden horror
- readable på standalone VR

Det er ikke:

- fotorealistisk survival
- blank cartoon/toy world
- cluttered realism
- UI-heavy sci-fi
- tropical holiday postcard

## 2. Fire art pillars

### A. Tydelig silhuet før detalje

Et vigtigt objekt skal kunne genkendes uden små textures.

### B. Campen er den fælles karakter

Shelter, fire og signal ændrer fysisk udtryk med state.

### C. Tryghed vs. storm

Samme ø skifter emotionel identitet gennem lys, vind, wetness og deformation — ikke gennem et helt andet art set.

### D. Alt gameplaykritisk kan aflæses uden farve alene

Shape, position, animation, audio og evt. icon støtter state.

---

# 3. Shape language

## Safe / usable

- brede former
- afrundede hjørner hvor praktisk
- tydelige greb
- stabile diagonaler/horisontaler

## Unstable / damaged

- forskudte linjer
- asymmetri
- slapt/twisted reb
- tarp der flapper
- splinter/knæk i silhuet

## Danger

- mere spidse/jagged accents
- rust/advarsel shape
- bevægelse/lyd frem for konstant rød glow

## Interaction targets

- cirkel/knude/socket-lignende grammatik
- samme snap-affordance på tværs af shelter/signal/repair

---

# 4. Proposed palette tokens

Hex values are **source-art reference**, not a requirement for Unity post-processing.

| Token | Reference | Brug |
|---|---|---|
| `CAMP_AMBER` | `#D59A52` | warmth/fire/safe emphasis |
| `SAND_LIGHT` | `#C8B58D` | beach/neutral surfaces |
| `MOSS_MUTED` | `#66745C` | foliage/camp materials |
| `OCEAN_GREYBLUE` | `#55717A` | sea/sky/exploration |
| `STORM_BLUEGREY` | `#3F5360` | storm/weather |
| `RUST_ALERT` | `#A85E48` | damage/warning accent |
| `WARM_WHITE` | `#E8E0CF` | interaction readability/text |
| `CHARCOAL` | `#282C2D` | dark UI/outline/contrast |

Rules:

- do not communicate success/fail with `MOSS` vs `RUST` alone
- preserve readable contrast under storm desaturation
- fire amber should remain a directional anchor during dark/storm phases

---

# 5. Material language

## Wood

- weathered
- broad grain, not noisy microdetail
- source variation through value/roughness and vertex/color masks

## Rope/fiber

- oversized enough to read tension/twist
- bundled fibers implied, not expensive strand simulation

## Tarp/cloth

- patched/utilitarian
- dry/wet/torn states visually distinct
- edges and tie points readable

## Metal

- limited to tools/radio/crates
- worn utilitarian surface
- no chrome/sci-fi sheen

## Rock

- stylized planes and strong silhouettes
- ravine route readability more important than geological realism

## Foliage

- grouped masses
- a few recognizable leaf silhouettes
- no dense alpha-noise wall that hides interactables

Unity master materials and actual shader implementation belong to Claude.

---

# 6. Zone identity

## Strand / Camp

Emotion: exposed but increasingly safe.

Landmark:

- wreck + fire

Visual ingredients:

- pale sand
- weathered wreck wood
- dark sea debris
- warm fire as focal point
- shelter grows visibly across progress

Navigation rule:

From key camp positions, player should orient toward fire/wreck without minimap.

## Jungle path

Emotion: enclosed, useful, uncertain.

Landmark:

- crooked tree / stone gateway

Visual ingredients:

- muted green masses
- readable path edge
- resource opportunities separated from background clutter

## Ravine

Emotion: exposure and cooperation.

Landmark:

- rock profile + rope anchor

Visual ingredients:

- cooler values
- vertical depth cue
- large readable route markers

## Ridge

Emotion: information/reward.

Landmark:

- open sea vista / signal route

Visual ingredients:

- reduced foliage
- strong horizon
- readable weather/ship direction

## Storm camp

Emotion: same place under pressure.

Do not replace camp with a wholly new scene identity. Instead change:

- wetness
- tarp movement
- debris
- broken/loose states
- fire visibility
- sky/value range

This lets earlier preparation remain visually legible.

---

# 7. Camp state readability

## Shelter integrity

### Strong

- taut tarp
- straight beam
- clean tied ropes

### Medium

- small sag
- one loose tie
- occasional creak

### Weak

- obvious sag/twist
- flap/tear
- unstable beam
- repair nodes visually available

## Fire strength

### Dead

- cold ash/dark fuel

### Embers

- localized glow, soft smoke

### Small

- low flame, vulnerable motion

### Strong

- stable flame, broader warm light intent

## Signal progress

Progress is visible as construction state:

- base/parts
- raised frame
- prepared fuel/cloth
- ready signal

Avoid an abstract progress bar as primary representation.

---

# 8. UI material language

Diegetic UI uses the same world materials, but cleaner.

## Planning cards

- weathered but readable card/board surface
- high-contrast icon + short label
- physical effort tokens
- no tiny flavor text

## Wrist status

- utilitarian band/tag
- few large state icons
- status should be glanceable

## Radio

- physical controls
- signal state in world
- subtitles remain non-diegetic for accessibility

## Non-diegetic menus

- clean field-journal influence
- not fake handwritten font at readability cost
- large controller targets
- minimal decoration

---

# 9. Icon grammar

All icons should pass silhouette test at small size.

Suggested shape anchors:

- shelter: roof/triangle
- fire: flame/ember
- food: parcel/container, not detailed meal
- signal: mast/rays
- medical: bandage/leaf + cross-like neutral aid symbol where appropriate
- explore: path/peak/eye-line
- fatigue: descending bar/weight shape
- injury: wrapped hand/marked limb

Do not use only hue to differentiate categories.

---

# 10. Player identity

MVP identity:

- floating/stylized hands
- optional simple torso
- Player A/B have unique **symbol + color**

No gender/body type must be inferred from hand model unless Anders later chooses explicit characters.

No Meta Avatar dependency required.

---

# 11. Damage / injury tone

No gore.

Damage language:

- splinter/bandage
- dirt/wear
- taped repair
- limp object state, not body horror

Player injury should be readable through status/animation/feedback without making physical VR control intentionally unpleasant.

---

# 12. VFX direction

## Rain

Readable streak/droplet field; density changes with phase.

## Wind

World reaction first:

- tarp
- foliage
- loose fibers/debris

rather than opaque screen effects.

## Embers/fire

Strong point-of-interest cue during storm; keep interaction targets visible.

## Collapse

Short debris/dust burst; never obscure both players' target for long.

## Wetness

Global look shift / source reference, not dozens of unique wet asset variants.

Runtime implementation/performance choices belong to Claude.

---

# 13. Texture/detail budget — source-side principles

- avoid unique 4K texture for every prop
- design for shared families/atlases
- hero items get detail only where players inspect them closely
- background assets prioritize silhouette/value
- avoid micro-normal/detail that disappears on Quest 2

Claude defines final import resolution/compression based on profiling.

---

# 14. Personalization visual rules

Personal photos/mementos should look intentionally placed, not pasted onto UI.

Use:

- physical frame/card/crate insert
- material consistent with world
- simple lighting/readability

Neutral fallback must look equally intentional.

Private images are never source references for general environment art.

---

# 15. Visual QA questions

For every screenshot/playtest view:

1. Where is the intended focus?
2. Can you identify the interaction target without reading text?
3. Can shelter/fire/signal state be understood?
4. Are player A/B distinguishable without color alone?
5. Does storm VFX hide snap/grab cues?
6. Is anything detailed but functionally unreadable?
7. Does a purchased/generated asset break the shared style?

---

# 16. Source-art deliverables

Source production should follow `docs/38_SOURCE_ASSET_MANIFEST.md`.

For hero/gameplay assets, ChatGPT handoff should include at least:

- ID
- purpose
- silhouette/front view or usable 2D master
- state variants
- material family
- color/shape cues
- provenance

Claude then chooses Unity-side representation.

---

# 17. Art gate

This bible authorizes **design consistency**, not mass production.

Before expensive full art pass:

- M-Pre planning hypothesis green
- relevant gameplay greybox proven
- key interaction geometry stable enough not to invalidate source art

However, gameplay-readable A-priority source assets may be produced earlier when needed for testing/handoff.
