# Interaction brief — Shelter reinforcement

**Owner:** ChatGPT  
**Unity implementation:** Claude  
**Related:** PO-042 · PO-060 · `INT_BUILD_SHELTER_003` · `INT_REINFORCE_ROOF_006`

## Player fantasy

Shelter is the shared character of the camp. Reinforcement should feel like two people physically making a fragile structure trustworthy — not like filling a crafting progress bar.

## Core roles

### Player A — stabilizer

- positions/holds beam or tarp edge in a broad stability zone
- responds to wind/weight movement
- can improve or worsen quality continuously

### Player B — binder

- routes rope through large readable points
- creates 2 required secure bindings
- optional third binding may improve quality after core success

Roles can be swapped before or between steps.

## Sequence

1. Weak/damaged shelter state is visibly readable.
2. Players bring beam/rope/tarp to the repair area.
3. Stabilizer places and holds beam/tarp.
4. Binder routes rope through first large snap path.
5. First binding establishes partial structural stability.
6. Second binding creates functional shelter success.
7. Optional quality action may be offered if pacing allows.
8. World state changes physically; players see/hear the shelter become more stable.

## Success model

### Critical success

- two required bindings are clean
- stability stayed high
- little wasted motion/time
- optional quality step may be completed

### Success

- shelter becomes functionally reinforced
- minor wobble/inefficiency acceptable

### Partial with cost

- shelter holds but remains visibly imperfect
- later storm has a concrete extra complication or lower buffer
- no full reset

### Fail-forward

- sequence still produces some reinforcement/progress
- cost becomes fatigue, material loss, a weak tag or later repair burden
- players never repeat the entire long sequence from zero solely due to one slip

Exact numerical state deltas remain data/tuning, not interaction design.

## No-reset rule

A lost grip or missed rope point causes:

- quality degradation
- time/material/fatigue consequence
- local recovery

It must **not** restart the full structure unless the entire object is intentionally reset.

## Assets

- `PRP_SHELTER_FRAME_001`
- `PRP_SHELTER_TARP_001`
- `PRP_SHELTER_BEAM_001`
- `PRP_SHELTER_ROPE_001`
- `TEX_TENSION_GUIDE_001`
- `TEX_SNAP_PREVIEW_001`
- `TEX_REPAIR_NODE_001`

## Audio

- `SFX_SHELTER_CREAK_LOW_001`
- `SFX_SHELTER_CREAK_HIGH_001`
- `SFX_ROPE_TENSION_LOW_001`
- `SFX_ROPE_TENSION_GOOD_001`
- `SFX_ROPE_TENSION_HIGH_001`
- `SFX_ROPE_TIE_001`
- `SFX_SHELTER_SNAP_SUCCESS_001`

## Copy fallback

Normal interaction should be learnable visually. Hint fallback may use:

- `interaction.hold_steady`
- `interaction.too_much_tension`
- `interaction.good_tension`
- `interaction.snap_ready`
- `interaction.partial`

## Accessibility / comfort

- all rope points within calibrated reach
- no required kneeling
- no long overhead hold
- stabilization zone should tolerate different arm lengths
- binder path uses large targets
- secondary role always changes quality/stability; never “watch while partner ties”
- color feedback always paired with shape/position/audio

## Duration target

A single reinforcement interaction should normally be a **short focused physical sequence**, not >30 seconds of repeated movement.

If more building is needed, later repetitions should use assisted repetition/abstraction rather than identical full manual work.

## Storm reuse

Storm phase 1 may reuse the learned vocabulary:

- beam stabilization
- rope tension
- quick repair nodes

But storm version should be shorter and more pressured, not introduce a brand-new rope grammar.

## Human test questions

- Did both players feel necessary?
- Did they understand what made the structure more stable?
- Could they recover after a mistake without confusion?
- Did anyone hold an uncomfortable pose too long?

## Acceptance criteria for Claude

- both roles materially influence outcome/quality
- partial progress survives ordinary mistakes
- states are visually/audio readable
- seated/standing mixed pair can complete it
- no >20s involuntary passive period
- all source IDs can be bound without Claude inventing gameplay rules
