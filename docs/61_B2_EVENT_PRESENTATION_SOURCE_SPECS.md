# B2 event presentation source specifications — PROJECT ØEN

**Owner:** ChatGPT  
**Runtime presentation:** Claude  
**Date:** 2026-08-13

## Purpose

Define how Stormnatten events become understandable world changes rather than invisible dice rolls or generic popups.

The event system may be data-driven, but players should perceive:

1. a telegraph or readable setup where appropriate
2. a visible/audible event state
3. a persistent consequence or resolved state when the fiction requires it

B2 provides source-side presentation material only. Runtime spawning, particles, animation, networking and state binding remain Claude work.

---

# 1. Global presentation rules

## Telegraph before consequence

Negative events should normally have at least one readable precursor unless surprise is explicitly the point and remains fair.

Examples:

- unsecured food -> scent/track/disturbance cues -> animal camp pressure
- weak shelter -> visible fastening weakness / increasing rain -> roof leak
- untreated injury -> known injury state -> later infection/fatigue pressure

## No invisible punishment

A player should not reasonably ask:

> “Why did that happen?”

without the after-action report being able to point to a prior state/action.

## World first, UI second

Prefer world/object state plus audio. UI/copy is fallback or clarification.

## Accessibility

Important event reads use at least two channels when practical:

- shape/state
- spatial placement/motion
- audio
- subtitle/copy

Color alone is never sufficient.

## Persistence

If an event changed the camp/world, the result should persist long enough to be understood. Do not instantly revert the visual state after the event callback fires.

---

# 2. Event mapping

| Event | Presentation source | Notes |
|---|---|---|
| `EVT_OPEN_FOOD_001` | existing food/storage state + later animal cues | setup must read as unsecured storage, not random penalty |
| `EVT_ANIMAL_CAMP_001` | `B2_ANIMAL_THREAT_CUES_001` | tracks/disturbed storage; no full animal AI/art promise |
| `EVT_SPLINTER_001` | reuse `UI_STATUS_INJURY_001` + local wood/sound feedback | no dedicated B2 art required initially |
| `EVT_UNTREATED_WOUND_001` | reuse injury/medical status + copy | known state before delayed consequence |
| `EVT_ROOF_LEAK_001` | `B2_ROOF_LEAK_STATE_001` | leak origin remains identifiable through rain |
| `EVT_TOOL_BREAK_001` | `B2_TOOL_BREAK_STATE_001` | authoring-only while durability remains deferred |
| `EVT_DRY_FUEL_FOUND_001` | `B2_DRY_FUEL_CACHE_001` | earned positive opportunity; readable before pickup |
| `EVT_EXTRA_HERBS_001` | `B2_EXTRA_HERBS_001` | clustered silhouette, not random ground clutter |
| `EVT_DISTANT_SMOKE_001` | `B2_DISTANT_SMOKE_001` | teaser only; never framed as current quest objective |
| `EVT_RADIO_FRAGMENT_001` | `B2_RADIO_FRAGMENT_PRESENTATION_001` | static -> signal-found -> voice/subtitle progression |

---

# 3. `B2_ANIMAL_THREAT_CUES_001`

Source intent:

- abstract tracks/prints
- disturbed food/storage shape
- optional movement/noise in foliage outside direct task area

Do **not** imply:

- combat loop
- animal health bar
- predator boss
- required character model

The threat is a camp/resource consequence, not an action game encounter.

---

# 4. `B2_ROOF_LEAK_STATE_001`

Required read:

- where water enters
- which shelter section is weak
- accumulated wetness/puddle consequence

Under storm VFX the leak origin must remain visible enough to support cooperative repair.

The leak should visually connect to prior shelter quality rather than appear as an arbitrary particle emitter.

---

# 5. `B2_TOOL_BREAK_STATE_001`

Status: **authoring-only while tool durability remains deferred**.

If the system remains out of gift scope, this source can stay unused without creating a missing-content error.

If enabled later:

- break point clearly visible
- fragments/alternate state communicate loss immediately
- required scenario progress remains possible through fail-forward alternative

---

# 6. Positive opportunities

## Dry fuel

`B2_DRY_FUEL_CACHE_001`

- protected/dry cover silhouette
- bundled sticks rather than loose random clutter
- reads as a coherent find from several steps away

## Extra herbs

`B2_EXTRA_HERBS_001`

- distinct clustered plant silhouette
- placement differentiated from generic jungle foliage
- opportunity must not require pixel-hunting

Positive events should feel discovered/earned, not like reward popups detached from the world.

---

# 7. Distant smoke

`B2_DISTANT_SMOKE_001`

Purpose:

- world activity/lore teaser
- something the two players can notice and discuss

Guardrail:

- no quest marker
- no “go there now” language
- no implication that failure to reach smoke blocks rescue

It must remain observational unless a future scope decision explicitly promotes it.

---

# 8. Radio fragments

`B2_RADIO_FRAGMENT_PRESENTATION_001`

Presentation sequence:

1. low/static state
2. signal-found cue
3. radio voice + subtitle
4. world/planning relevance remains visible after line finishes

Critical rescue information cannot be lost because of random selection or a short one-shot that a player misses while talking.

The radio should feel like a physical world object first; subtitle/copy supports accessibility and clarity.

---

# 9. Reused source instead of duplicate art

B2 deliberately reuses existing source families where they already communicate the state:

- injury -> A1 injury/medical source
- wet/cold -> A1 status source
- warning/partial/success -> A1 state shapes
- rain/wind/fire pressure -> A3 storm sources
- shelter/fire/signal physical states -> A2/A3 contracts

Do not create a new icon for every event merely because an event ID exists.

---

# 10. Source package

`source_art/events/b2/`:

- `B2_ANIMAL_THREAT_CUES_001.svg`
- `B2_ROOF_LEAK_STATE_001.svg`
- `B2_TOOL_BREAK_STATE_001.svg`
- `B2_DRY_FUEL_CACHE_001.svg`
- `B2_EXTRA_HERBS_001.svg`
- `B2_DISTANT_SMOKE_001.svg`
- `B2_RADIO_FRAGMENT_PRESENTATION_001.svg`
- `PROVENANCE.md`

---

# 11. Acceptance before runtime handoff

- every negative event has understandable causality/telegraphing where required
- event presentation does not promise mechanics outside scope
- positive opportunities are discoverable without UI hunting
- distant smoke remains narrative teaser, not false objective
- radio critical information cannot be silently missed
- all B2 source is project-original/provenance-recorded
- source remains implementation-agnostic enough for Quest 2 runtime decisions
