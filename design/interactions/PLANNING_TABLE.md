# Interaction brief — Planning table

**Owner:** ChatGPT  
**Unity implementation:** Claude  
**Related:** ADR-022 · M-Pre · PO-033/034/038 · `docs/35` · `docs/44`

## Player fantasy

To mennesker står omkring et fysisk planlægningsbord med for få muligheder til at gøre alt. Det interessante er samtalen og prioriteringen — ikke selve UI-manipulationen.

## Core experience

1. Dagens relevante action cards er synlige samtidig.
2. Fire effort markers ligger fysisk tilgængeligt.
3. Begge spillere kan tage, placere og flytte markører.
4. Placering er **tentativ**, indtil planen låses.
5. Begge kan se hele planen og hinandens ændringer.
6. Planen låses kun efter en tydelig fælles commit.

## Ikke-målet

Planning må ikke føles som:

- et inventory spreadsheet
- fire separate menuvalg
- en timerøvelse
- en quiz med ét oplagt korrekt svar
- et system hvor én spiller “betjener UI'et” for begge

## Roles

Planning har ikke faste primær/sekundærroller.

Begge skal kunne:

- foreslå
- flytte en markør
- pege på risiko/gevinst
- ændre mening
- initiere commit

M-Pre afgør, om denne symmetri faktisk skaber forhandling.

## Information on each action card

Minimum:

- navn
- effort cost
- category/icon
- kort qualitative risk cue
- kort qualitative expected-gain cue

Ingen endelige numeriske sandsynligheder vises, medmindre senere evidence viser at spillerne har brug for dem.

Source copy: `docs/40_UX_COPY_AND_LOCALIZATION_CATALOG.md`.

## Assets

- `PRP_PLAN_TABLE_001`
- `UI_EFFORT_MARKER_P1_001`
- `UI_EFFORT_MARKER_P2_001`
- `UI_ACTION_CARD_BASE_001`
- action icons fra `docs/38_SOURCE_ASSET_MANIFEST.md`

Player markers may have player identity through **symbol + color**, never color only.

## Audio

- `SFX_MARKER_PICKUP_001`
- `SFX_MARKER_PLACE_001`
- `SFX_MARKER_MOVE_001`
- `SFX_PLAN_READY_001`
- `SFX_PLAN_LOCK_001`
- `SFX_PLAN_CONFLICT_001`

Audio is tactile confirmation, not pressure.

## Feedback states

### Marker hover

- target/card reads as available
- no commitment implied

### Marker placed

- marker visibly belongs to card
- plan remains editable

### All effort allocated

- subtle “plan ready” affordance
- do not auto-lock

### Commit requested

- both players get a clear final-state view
- if the product chooses explicit two-player confirmation later, that must be a product decision rather than silent Unity behavior

### Plan locked

- markers stop being editable
- next phase transition is clear

## Conflict / race recovery

If both users change/confirm nearly simultaneously:

- never silently discard a visible placement
- show the final authoritative plan
- indicate that the plan changed before lock
- require the players to see the final state before action begins

Copy fallback: `planning.revision_changed`.

## Accessibility

- cards readable at natural VR distance
- no tiny text
- icon + label
- selection/lock not color-only
- all critical cards reachable seated and standing
- plan may not require physical walking around a table

## Human evidence

### Before Unity

M-Pre: at least 2/3 green sessions on real negotiation.

### In VR

M3 revalidation:

- pair completes one plan without developer explanation
- can explain what they chose not to do
- both interact with or materially influence planning
- no player reports that planning is mostly administrative

## Acceptance criteria for Claude handoff

Unity implementation is product-correct when:

- both players can manipulate visible marker state
- tentative vs locked state is unmistakable
- race/revision does not create hidden state
- physical layout supports seated/standing
- copy/audio/asset IDs above can be bound without inventing new product rules

## Open evidence

Do not finalize:

- optimal number of effort markers
- exact action-card information density
- automatic vs explicit commit style

until M-Pre/M3 evidence supports it.
