# Interaction brief — Ravine rescue

**Owner:** ChatGPT  
**Unity implementation:** Claude  
**Related:** `SEQ_RAVINE_RESCUE_001` · PO-056 · OQ-007/OQ-009

## Player fantasy

A tense two-person traversal where one player is physically exposed while the other actively keeps the situation safe.

The secondary role must feel consequential, not like watching a partner do a climbing minigame.

## Comfort clarification

The word “climb” in existing content is **fictional/gameplay language**, not a requirement for real-world climbing movement.

The sequence must obey project comfort rules:

- no required floor contact
- no real-world walking over a large area
- no sustained overhead reach
- no forced camera movement
- no need to lean dangerously outside guardian/boundary

The exposed player may traverse via bounded VR handholds/teleport-like anchored steps or another Claude-chosen Unity implementation, but product acceptance is based on the experience below.

## Roles

### Player A — traverser

- moves through 2-4 clear progression points
- chooses/uses the next safe hold/anchor
- may need to pause when rope support is poor

### Player B — belayer / guide

- controls or maintains rope tension
- reads safe-route cues that are easier/only available from their position
- communicates next safe point
- can prevent quality loss and reduce consequence severity

Roles may swap in later run/variant; OQ-009 determines whether broader role assignment becomes canonical.

## Sequence

1. Players reach ravine and identify a target/recovery objective.
2. Rope is attached to a clear anchor.
3. Traverser moves to first bounded point.
4. Belayer keeps tension in target zone.
5. Belayer communicates the next safe marker/route cue.
6. Traverser advances through short sequence.
7. At least one controlled complication may occur if tension/choice is poor.
8. Target/recovery object is secured.
9. Both return/resolve without replaying entire traversal from zero.

## Information asymmetry

The sequence should create useful communication by giving the players **different but complementary information**.

Examples:

- traverser sees local handhold geometry
- belayer sees tension state and route marker sequence

Do not hide information merely to manufacture confusion.

## Outcome model

### Critical success

- tension maintained well
- route communication efficient
- no injury/fatigue consequence

### Success

- rescue completed with normal cost

### Partial with cost

- rescue succeeds
- fatigue/minor injury/material cost added

### Fail-forward

- sequence reaches a safe recovery state
- player may take injury/fatigue or lose a resource
- no lethal sudden fall/fail state
- no forced full restart from ravine entrance

## Assets

- `ENV_RAVINE_001`
- `ITM_ROPE_COIL_001`
- `PRP_RAVINE_ANCHOR_001`
- `PRP_RAVINE_GUIDE_MARKERS_001`
- `TEX_TENSION_GUIDE_001`

## Audio

- `SFX_AMB_RAVINE_001`
- `SFX_ROPE_TENSION_LOW_001`
- `SFX_ROPE_TENSION_GOOD_001`
- `SFX_ROPE_TENSION_HIGH_001`
- `SFX_ROPE_TIE_001`

## Copy fallback

- `interaction.hold_steady`
- `interaction.too_much_tension`
- `interaction.good_tension`

Route communication should primarily be player-to-player, not narrator instructions.

## Accessibility

- route markers use shape/position + optional color
- tension has visual + audio feedback
- all hand/interaction points remain within calibrated reach
- no jump-scare drop or artificial camera pitch
- sequence can pause safely if either player needs a break

## Participation gate

Both roles must change at least one measurable aspect of the result.

A version fails product acceptance if:

- traverser can complete it almost unchanged while belayer does nothing
- belayer only presses a confirm button
- one player waits >20 sec without meaningful action

## Human test

Ask separately:

- What did your partner do that helped you?
- Could you tell when the rope/tension was good?
- Did you ever feel you were just waiting?
- Did the sequence feel physically unsafe/uncomfortable?

## Acceptance criteria for Claude

- bounded safe movement model
- both roles materially affect outcome
- no full restart on ordinary mistake
- tension/route state readable across both clients
- mixed seated/standing pair can complete it
- implementation does not silently decide OQ-009 role policy
