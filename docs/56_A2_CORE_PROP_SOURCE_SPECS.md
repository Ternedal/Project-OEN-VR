# A2 core prop source specifications — PROJECT ØEN

**Owner:** ChatGPT  
**Unity integration:** Claude  
**Dato:** 2026-08-13  
**Batch:** A2 fra `docs/55_SOURCE_PRODUCTION_BATCH_PLAN.md`

## Formål

Dette dokument definerer de centrale fysiske props på **source-/product-niveau** før egentlig 3D-produktion eller Unity-implementation.

Målene er design-startpunkter, ikke centimeterpræcise physics-kontrakter. Claude må justere runtime scale efter XR/reach-test, men må ikke ændre interaktionsintentionen uden at flagge det.

---

# Fælles regler

## Skala

Props skal føles menneskelige og gribbare i VR:

- grebzoner mindst ca. håndbredde
- vigtige sockets/knudepunkter overdimensioneres visuelt
- ingen kritisk manipulation kræver fingerprecision
- objects are readable at 1–3 m where relevant

## Materialer

Brug de fælles familier fra `docs/47_VISUAL_STYLE_BIBLE.md`:

- weathered wood
- rope/fiber
- tarp/cloth
- worn utility metal

## State readability

Gameplaykritiske states skal ændre mindst to af:

- silhouette/geometry
- position/tension
- surface/value
- animation/motion
- audio cue
- optional icon/shape

---

# 1. `PRP_HEAVY_CRATE_001` — tung kasse

## Product role

Åbningsinteraction og referencegrammar for senere storm-collapse shared-object work.

## Approx source scale

- width: ~0.9–1.1 m
- depth: ~0.55–0.7 m
- height: ~0.55–0.7 m

Enough that solo handling visually reads as awkward/heavy.

## Silhouette

- rectangular utility crate
- reinforced corners
- two clearly opposed grab handles
- top/lid visually distinct

## Grab zones

- one large handle/rail on each short side
- no tiny recessed handles
- handles visually symmetrical but Player A/B identity comes from player markers, not crate sides

## States

### Closed

- lid latched
- handles visible

### Carried

- no source mesh change required; weight communicated by motion/audio/runtime

### Placed

- stable orientation, lid accessible

### Open

- lid opens enough to expose starter content

## Contents layout intention

Starter content should be visually separated:

- firesteel
- cloth/tarp fragment
- map/route fragment
- radio / radio-related item

Exact content follows issue #8 fire-start disposition.

## Do not add

- brand marks
- military iconography that suggests a different narrative
- tiny inventory clutter

---

# 2. `PRP_FIREPIT_001` — camp firepit

## Product role

Central camp anchor and readable fire-state container.

## Approx scale

- diameter: ~0.75–0.95 m
- low profile; no need for players to crouch to interact

## Shape

- rough stone/charred wood ring
- one visually open interaction side or broad access zone
- enough negative space for tinder/fuel readability

## Required visual states

### Dead

- dark ash/cold fuel

### Embers

- concentrated ember source; no large flame

### Small

- low vulnerable flame

### Strong

- stable higher flame / broader warmth

## Interaction readability

Fuel placement area should be broad. The player should not need to insert wood into an exact slot.

## Storm readability

Rain/wet state must make vulnerability obvious without fully hiding embers.

---

# 3. `ITM_FIRESTEEL_001` — firesteel

## Product role

Short onboarding ignition tool if minimal fire-start is accepted.

## Approx scale

Intentionally oversized relative to real pocket firesteel:

- rod length ~18–24 cm
- grip ~10–14 cm

## Shape

- chunky utility grip
- bright/contrasting strike edge
- obvious “tool, not weapon” silhouette

## Interaction zone

Strike target should be visually obvious and larger than a real-world precision contact area.

## Required states

No durability states for minimal gift-scope proposal.

Possible cosmetic:

- clean
- used/sooty

but not gameplay-critical.

---

# 4. `ITM_TINDER_001` — tinder bundle

## Product role

Visible ignition target / first ember container.

## Approx scale

- ~20–30 cm loose bundle

## Shape

- open fibrous nest/bundle
- clearly different from wood/fiber resource bundles

## States

- dry/unlit
- spark/ember
- spent/wet if needed

The ember state must stay visible under wind/rain VFX.

---

# 5. `PRP_WIND_SHIELD_001` — fire shield

## Product role

Gives second player an active role during ignition/fire recovery.

## Approx scale

- ~35–50 cm wide
- ~30–45 cm high

## Shape

- improvised flat/curved shield made from board/cloth/frame
- one large handle

## Interaction rule

Player should understand orientation from shape. It must not be a featureless square requiring hidden angle math.

## State

No complex damage required in release scope.

---

# 6. `PRP_SHELTER_BEAM_001` — shelter beam

## Product role

Primary stabilizer object in shelter reinforcement and storm collapse.

## Approx scale

- length ~1.4–1.8 m
- cross-section exaggerated enough for grip/readability

## Grab zones

- at least two broad regions, not tiny handles
- visual wear/rope marks may indicate natural hold locations

## States

### Intact

straight enough to read stable

### Stressed/damaged

- visible split/bend/loosened binding point
- should not become gore-like/sharp visual hazard

## Reuse

The same beam grammar should work in calm construction and storm crisis.

---

# 7. `PRP_SHELTER_ROPE_001` / `ITM_ROPE_COIL_001`

## Product role

Core binding/tension language across shelter and ravine.

## Rope coil

Approx source diameter ~30–40 cm, readable loose end.

## Rope visual language

- chunky fiber
- visible twist
- no hair-thin line

## Binding points

Use deliberately oversized loop/node geometry.

## Tension states

### Loose

- sag
- relaxed curve

### Good

- clean controlled line

### High/strained

- taut line + visible fiber/attachment stress

Audio/guide supplements shape; no color-only tension.

## Source caution

Do not model a huge number of real rope segments just for realism. Claude owns runtime rope technique/performance.

---

# 8. `PRP_SHELTER_TARP_001` — shelter tarp

## Product role

Largest visual shelter-state indicator.

## Approx size

Source concept around 2–3 m span, adaptable to greybox geometry.

## Required states

### Dry / taut

- broad stable plane

### Wet

- darker/value shift
- heavier sag

### Loose/flapping

- one or more corners visibly uncontrolled

### Torn

- clear silhouette break / tear, not tiny texture scratch

## Interaction zones

Tie points should be visibly reinforced with loops/eyelets/knots large enough to target.

---

# 9. `PRP_PLAN_TABLE_001` — planning table

## Product role

Physical shared decision surface for action cards + four effort markers.

## Approx scale

- width ~1.0–1.3 m
- depth ~0.55–0.75 m
- working height must support standing and seated presentation through runtime adjustment/placement

## Surface layout

Must support:

- 4–6 visible action cards simultaneously
- four effort markers
- a clear “plan editable / ready / locked” state

## No walking requirement

All relevant cards must be reachable from each player's calibrated side/position or through safe table layout; players should not need to physically circle the table.

## Visual language

- weathered expedition/work surface
- clean card areas
- no tiny printed grid

## Related source

- `UI_ACTION_CARD_BASE_001.svg`
- effort marker SVGs
- action icons

---

# 10. `PRP_SIGNAL_FRAME_001` — signal frame

## Product role

Visible long-term rescue preparation and final objective.

## Approx scale

- clearly visible from camp at several metres
- mast/frame ~1.5–2.5 m visual height depending on final environment

## Progress states

### Stage 0

materials/empty base

### Stage 1

basic frame

### Stage 2

raised/stabilized structure

### Stage 3 / ready

fuel/cloth/visibility preparation clear

## Finale interaction

Final ignition/activation must happen in reachable lower interaction zone; do not require actual overhead reach.

---

# 11. Source sheet requirements per prop

Before actual 3D/model source is considered ready, each A2 prop should have:

- front/side/top or clear perspective views
- approximate scale reference
- required states
- grab/interaction zones marked at product level
- material family
- asset ID
- provenance

A generated concept image alone is not sufficient if required states/zones are missing.

---

# 12. A2 QA checklist

- [ ] heavy crate reads as two-person object
- [ ] firepit states are distinguishable
- [ ] firesteel interaction surface is obvious
- [ ] tinder is not confused with generic fiber resource
- [ ] wind shield has obvious orientation
- [ ] beam supports broad grip
- [ ] rope states read without color
- [ ] tarp damage changes silhouette
- [ ] plan table fits all cards/markers without tiny UI
- [ ] signal progress visible from camp
- [ ] no prop requires kneeling/overhead reach by design
- [ ] provenance entry prepared

---

# 13. Claude handoff boundary

Claude owns:

- actual collider geometry
- physics/kinematic behavior
- grab interactors
- runtime rope solution
- prefab hierarchy
- world scale tuning after device test
- material/shader implementation
- LOD/performance

ChatGPT owns the product-facing shapes, required states, source masters and interaction-readable zones above.
