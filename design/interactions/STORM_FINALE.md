# Interaction brief — Storm finale

**Owner:** ChatGPT  
**Unity implementation:** Claude  
**Related:** PO-060/061/062 · M5 Release 1 · OQ-008 · `docs/05` · `docs/44`

## Player fantasy

The storm is the payoff to everything the players decided earlier.

It should feel like:

> “We are improvising under pressure with the camp we built.”

It must **not** feel like:

- five disconnected minigames
- arbitrary punishment
- a reflex test that ignores planning
- a long scripted sequence where one player watches
- a binary pass/fail gauntlet

## Global design rules

1. Every phase has two active roles.
2. Earlier camp/player state changes at least three concrete aspects of the storm.
3. Mistakes create cost and pressure; they rarely erase all progress.
4. Storm pacing rises, but instructions stay legible.
5. Physical tasks reuse interaction vocabulary learned earlier.
6. Phase 3 randomness weights are not finalized before OQ-008 evidence.
7. No phase requires unsafe roomscale movement.
8. Voice/music never masks critical partner communication.

---

# Pre-storm state read

Before phase 1, players should get a brief diegetic read of what they are taking into the storm:

- shelter state
- fire state
- relevant injury/condition
- signal readiness
- earned consequence tags

Do not show hidden numeric formulas.

The experience should support the sentence:

> “This is the camp we chose to bring into the storm.”

---

# Phase 1 — Wind / shelter

## Purpose

Immediately cash out shelter preparation.

## Roles

### Stabilizer

- holds beam/tarp structure in a broad safe zone
- reacts to gusts/structural movement

### Binder/repairer

- secures 2 rope points
- responds to damaged/loose node if earned by prior state

## Branching

Good shelter:

- fewer repair nodes
- broader stability margin
- lower time/fatigue pressure

Weak shelter:

- one additional visible complication
- faster creak/strain escalation
- still recoverable

## Assets/audio/copy

Assets:

- shelter frame/tarp/beam/rope
- repair nodes

Audio:

- wind L2/L3
- shelter creak low/high
- rope tension
- beam shift

Copy:

- `storm.phase1.title`
- `storm.phase1.objective`

## Fail-forward

A missed bind may:

- damage shelter further
- increase later collapse burden
- cost fatigue/time

But phase advances once a functional minimum is achieved.

---

# Phase 2 — Rain / fire

## Purpose

Force players to split attention between protecting the existing fire and retrieving/adding dry fuel.

## Roles

### Fire protector

- shields embers from wind/rain
- maintains recoverable fire state

### Fuel runner/handler

- retrieves dry fuel from a short bounded route or nearby cache
- returns it to fire

## Anti-passivity rule

The “runner” path must be short enough that protector is not simply holding a pose alone for a long period.

Possible product-safe rhythm:

1. protector stabilizes flame
2. partner retrieves one load
3. protector signals readiness
4. partner adds fuel
5. roles jointly stabilize recovery

## Branching

Strong fire:

- starts at small/strong state
- fewer recovery actions

Weak fire:

- starts at embers
- one extra fuel/recovery step

Wet/damaged camp state can add pressure but not a completely different interaction grammar.

## Assets/audio/copy

Assets:

- fire pit
- wind shield
- ember carrier/dry fuel cache

Audio:

- heavy rain
- fire wet hiss
- ember/small/strong loops
- fuel add

Copy:

- `storm.phase2.title`
- `storm.phase2.objective`

---

# Phase 3 — Earned consequence slot

## Purpose

Make an earlier choice return in a way players can understand.

## Candidate branches

- animal threat from `SCENT_HIGH`
- injury complication from untreated condition
- shelter-related quick repair if unresolved
- other documented event tags later

## Selection rule

Prefer **earned consequence** over arbitrary random complication.

Randomness may select among multiple valid earned consequences or vary severity, but players should be able to answer:

> “Why did this happen to us?”

with a meaningful earlier cause.

## OQ-008 dependency

The final random trigger/severity model waits for OQ-008 fairness evidence.

No Unity implementation should hardcode a final probability as a product decision before that evidence.

## Roles

Every selected branch must define two materially active roles.

Examples:

Animal:

- Player A maintains fire/noise/deterrent state
- Player B secures food/repairs disturbed container

Injury:

- Player A performs stabilization/treatment action
- Player B maintains light/material/physical support and manages environmental pressure

## Fail-forward

Consequence may worsen camp/player state or consume time. It should not unexpectedly end the whole scenario from one hidden die roll.

---

# Phase 4 — Partial collapse

## Purpose

Peak physical cooperation using the heavy-object grammar already proven earlier.

## Roles

### Lifter/stabilizer A

- takes one side/target

### Lifter/stabilizer B

- takes second side/target

After stabilization, one or both perform a short repair/snap step while the structure remains supported.

## Experience arc

1. structure gives way visibly/audio
2. players identify the same critical object
3. both grab
4. object/beam becomes controllable together
5. they move/stabilize into safe zone
6. repair points appear/become usable
7. functional repair locks
8. storm does not stop, but camp survives the peak

## Reuse rule

This should feel like a dramatic evolution of the intro heavy crate, not a brand-new physics system.

## Assets/audio

- shelter beam/structure
- repair nodes
- partial collapse VFX
- heavy grab/move/place
- collapse audio

## Technical dependency

Claude's M0b shared-object proof is a prerequisite to trusting this phase.

## Human acceptance

- both players immediately understand they must act together
- no single player can trivially solo the lift
- no long reset after a grip mistake

---

# Phase 5 — Signal / dawn

## Purpose

Turn survival into rescue. This is the emotional/mechanical payoff.

## Roles

### Flame protector/carrier

- protects or carries viable ember/fire source
- maintains it through final movement/placement

### Signal operator

- clears/prepares signal point
- receives/places fuel or activates final signal structure

Roles converge at ignition.

## Branching

Signal preparation from earlier days affects:

- how many setup steps remain
- ignition speed/reliability
- not whether players are allowed to try at all

A weak signal can be slower/more pressured but should remain legible and recoverable within the final window.

## Assets/audio/copy

Assets:

- ember carrier/fire source
- signal frame/fuel

Audio:

- storm final layer
- ignition
- radio acknowledgement
- rescue music release

Copy:

- `storm.phase5.title`
- `storm.phase5.objective`

## Win presentation

On signal success:

1. the world acknowledges it immediately
2. storm pressure begins to fall
3. rescue acknowledgement arrives
4. players get a beat to look at each other/the camp
5. epilogue/personalization opens

Do not instantly cut to a menu.

---

# Loss / retry

Loss should still produce a coherent explanation.

Possible reasons:

- both incapacitated
- signal window missed after fail-forward attempts
- fire/signal state irrecoverable under explicit rules

On loss:

- show causal summary
- offer retry from pre-storm checkpoint or approved later checkpoint
- do not force replay of the entire 35-45 minute scenario

Copy: `outcome.loss.*` / retry keys.

---

# Audio/music communication budget

Storm audio is dramatic but partner voice is primary.

Product requirement:

- interaction confirmation cues remain audible
- partner communication is not consistently masked by wind/music
- high-intensity mix should still allow simple spoken coordination

Claude owns actual mixer/ducking implementation.

---

# Accessibility

- all critical audio has visual equivalent
- no flashing/contrast effect may hide snap targets
- roles support seated/standing
- no forced camera motion
- phase transitions are announced visually + audio
- storm does not use color-only red/green success language

---

# Human test matrix

Test at least two pre-storm fixtures:

## Prepared

Shelter/fire in decent state, few negative tags.

## Pressed

Weak shelter/fire or one earned consequence.

Ask:

- What earlier choice changed the storm?
- When did you need your partner most?
- Did any phase feel random/unfair?
- Did either of you spend too long waiting?
- Did the final signal feel earned?

---

# Product acceptance criteria

Storm finale is product-correct when:

- each phase has two active roles
- at least three earlier state/choices produce visible consequence differences across the finale
- failure is mostly fail-forward
- phase 3 randomness has evidence-backed policy
- shared heavy-object payoff works as learned grammar
- signal is clearly the joint final objective
- after success/loss the players understand why
- sequence remains within target pacing and comfort envelope

Technical performance/network acceptance remains in Claude's M5 gate.
