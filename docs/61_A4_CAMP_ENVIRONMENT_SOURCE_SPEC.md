# A4 camp environment source spec — PROJECT ØEN

**Owner:** ChatGPT  
**Unity scene/layout implementation:** Claude  
**Dato:** 2026-08-13  
**Batch:** A4 — Release 1 camp environment

## Formål

Definere campens rumlige **produkt- og source-art-kontrakt** uden at låse final Unity geometry før greybox/device evidence.

Campen er scenariets fælles karakter og skal gøre tre ting:

1. orientere spillerne uden minimap
2. vise konsekvenser fysisk
3. understøtte alle releasekritiske interactions uden unødvendig walking/reach

---

# 1. Camp fantasy

Campen begynder som:

> et udsat sted ved et vrag

og udvikler sig til:

> noget spillerne selv har gjort i stand til at modstå stormen.

Det visuelle payoff er derfor **forandringen af det samme sted**, ikke at spilleren låser en helt ny base op.

---

# 2. Spatial principles

## Compact but not cramped

Release 1 camp skal kunne forstås fra få stå-/teleportpositioner.

Undgå:

- lange tomme gåafstande
- skjulte gameplaystationer bag vegetation
- props placeret så spillere fysisk kolliderer i same-room setup
- smalle passager som kræver præcis roomscale navigation

## Landmark triangle

Tre primære landmarks:

1. **Vrag / heavy crate** — scenario origin / history
2. **Firepit** — social/status anchor
3. **Shelter** — shared construction / storm state

Signal frame ligger som fjerde, mere havvendt landmark og skaber progression mod finalen.

---

# 3. Conceptual layout

Not to scale; Unity dimensions remain tunable.

```text
                    JUNGLE / PATH
                         ↑

             [ SHELTER ]       [ SUPPLIES ]
                  \                /
                   \              /
                    [  FIREPIT  ]
                    /     |      \
                   /      |       \
          [ PLAN TABLE ]  |      [ WRIST/UTILITY ]
                          |
                     [ HEAVY CRATE ]
                          |
                       [ WRECK ]
                          |
            [ SIGNAL FRAME / SEA VIEW ]
                          ↓
                         SEA
```

This is a **relationship map**, not a Unity scene blueprint.

---

# 4. Player orientation contract

From firepit / central camp position, players should be able to visually identify:

- shelter
- wreck/crate area
- signal direction
- path out of camp

Planning table should be findable through deliberate placement/material language rather than a floating UI beacon.

---

# 5. Functional zones

## Zone A — Wreck / introduction

Contains:

- `ENV_BEACH_WRECK_001`
- `PRP_HEAVY_CRATE_001`
- starter item reveal

Experience:

- exposed
- messy
- first shared-object problem

Must not remain the main cluttered workspace after intro.

## Zone B — Fire / social anchor

Contains:

- `PRP_FIREPIT_001`
- fuel access
- short radio/listening proximity if radio lives nearby

Experience:

- most stable focal point
- warm direction anchor at night/storm

## Zone C — Shelter

Contains:

- frame/tarp/beam/rope
- repair nodes

Experience:

- visibly changes with build quality and damage
- enough clearance for two-player side-by-side roles

## Zone D — Planning table

Contains:

- planning surface
- action cards
- four markers

Experience:

- deliberate pause in physical survival
- both players can access from stable positions

## Zone E — Supplies

Contains:

- food
- wood/fiber bundles
- storage/crate/closure

Experience:

- visually readable “secured / unsecured” state
- source for food/scent consequences

## Zone F — Signal

Contains:

- signal frame progression
- final lower interaction/ignition zone

Experience:

- visible from camp
- sea/horizon alignment
- becomes stronger focal point toward Day 3

---

# 6. Reach / comfort envelope

Camp layout must be compatible with:

- standing pair
- seated pair
- mixed pair

Product rules:

- no critical object placed on ground solely for realism
- low resources can visually lie near ground but have accessible pickup representation
- shelter tie/repair nodes stay inside calibrated comfortable reach
- signal final activation is lower/reachable
- plan table does not require walking around

---

# 7. Navigation hierarchy

## Primary paths

- wreck ↔ fire
- fire ↔ shelter
- fire ↔ planning
- fire ↔ signal
- fire ↔ exit path

## Secondary

- shelter ↔ supplies
- planning ↔ supplies

Do not require a minimap for any camp route.

---

# 8. State progression

## Intro

Camp looks unfinished/exposed:

- wreck dominates
- shelter minimal
- signal absent/material-only
- fire dead/embers

## End Day 1

Players can visually compare:

- shelter improvement or lack thereof
- food/supplies security
- fire established

## End Day 2

Storm prep becomes visible:

- reinforced shelter states
- signal progression
- collected materials
- possible injury/wetness consequences

## Day 3

Camp should visually answer:

> “What did we invest in?”

without opening a status spreadsheet.

## Storm

Same camp becomes unstable:

- wetness
- loose/torn tarp
- debris
- fire vulnerability
- signal target

## Epilogue

Damage remains visible. Do not magically reset camp to pristine state after win.

---

# 9. Clutter budget

Gameplay objects take visual priority.

### Allowed clutter

- wreck fragments
- a few wood/fiber bundles
- cloth scraps
- small rocks/vegetation clusters

### Avoid early

- dozens of bottles/cans
- tiny noninteractive props around critical objects
- dense foliage directly behind rope/repair nodes
- decorative text labels

If a decorative asset could be confused for a pickup, either simplify it or make the pickup grammar stronger.

---

# 10. Visual sightline rules

## Fire ↔ shelter

Shelter silhouette/state visible from fire.

## Fire ↔ signal

Signal direction visible or strongly implied.

## Planning ↔ camp

Players can look up from table and reference physical shelter/fire/signal while discussing choices.

This is important: planning should remain grounded in the world, not become a detached menu scene.

---

# 11. Storm readability

During S3/S4 storm intensity:

- fire remains a warm anchor
- shelter repair target silhouette remains readable
- shared beam/object remains distinct from background
- signal remains findable in final phase

If final art/VFX violates these, reduce clutter/effect intensity before adding HUD guidance.

---

# 12. Same-room consideration

No assumption that physical players stand in the same exact real-world spot.

Virtual camp supports:

- safe teleport/bounded positions
- players occupying nearby virtual work positions without relying on real-world collision avoidance

Actual multiplayer locomotion/guardian behavior is Claude's implementation concern.

---

# 13. A4 source deliverables

Before full camp art production:

- top-down relationship reference
- 3–4 key sightline thumbnails/reference diagrams
- camp state sheet: intro / Day 2 / storm / epilogue
- material family reference
- clutter/do-not-clutter examples
- hero prop source from A2

A4 does **not** require:

- final vegetation density
- final lighting
- full wreck detail
- final mesh optimization

until greybox is stable enough.

---

# 14. Product QA

Ask from a static screenshot / greybox / headset:

1. Can you find shelter immediately?
2. Can you find the fire immediately?
3. Which direction is the sea/signal?
4. Where would you go to plan?
5. What changed in the camp since earlier?

If users cannot answer without floating labels, environment hierarchy is too weak.

---

# 15. Acceptance before Claude final-art handoff

- landmark triangle clear
- fire central anchor
- planning table visually connected to camp state
- signal is sea-facing progression landmark
- two-player workspaces have clearance
- critical objects within comfort envelope
- state changes physically readable
- storm does not make core targets disappear
- no final-art investment depends on unproven exact greybox dimensions
