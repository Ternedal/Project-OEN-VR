# UI & information architecture — PROJECT ØEN

**Product/UX owner:** ChatGPT  
**Unity implementation:** Claude  
**Dato:** 2026-08-13

## 1. Formål

Dette dokument beskriver **hvilken information spilleren skal have, hvor den hører hjemme, og hvornår den vises**.

Det beskriver ikke Unity-canvas, prefabs, render mode eller input implementation.

## 2. UX-princip

World first, overlay second.

Prioritet:

1. fysisk world state
2. diegetisk UI/props
3. kort contextual hint
4. non-diegetisk system UI

Et overlay må ikke erstatte en world state, hvis spilleren forventes at handle fysisk på den.

---

# 3. Information hierarchy

## Tier 1 — altid eller naturligt synlig

- partner presence
- critical interactables
- fire/shelter/signal physical state
- current immediate physical objective

## Tier 2 — glanceable on demand

- player health/fatigue/injury
- current phase/day
- effort/plan state
- connection warning

## Tier 3 — explicit menu

- comfort settings
- handedness
- diagnostics/build info
- leave session
- accessibility settings

## Tier 4 — post-action/post-run

- causal report
- outcome summary
- replay/retry

---

# 4. Surface map

| Surface | Type | Information | Must not contain |
|---|---|---|---|
| Camp world | world | shelter/fire/signal status | hidden numeric formulas |
| Planning table | diegetic | action choices, effort allocation | full inventory spreadsheet |
| Wrist status | diegetic | player condition, quick utilities | large menu trees |
| Radio | diegetic | narrative/forecast/signal | critical voice without subtitles |
| Lobby panel | non-diegetic/world hybrid | join/ready/version | gameplay strategy |
| Pause panel | non-diegetic | comfort, resume, return object, leave | hidden dev tools in release |
| Reconnect panel | non-diegetic | connection state/recovery | networking jargon |
| Subtitle band | non-diegetic | speaker + speech | noncritical clutter |
| After-action | non-diegetic/diegetic hybrid | causality/replay | blame score by default |

---

# 5. Lobby information architecture

## Primary state

Show only:

- title
- create/join choice

## Host state

Show:

- join code
- own ready state
- partner connection/ready state
- compatibility warning if needed

## Join state

Show:

- code input
- connection progress
- recoverable error

## Connected state

Show:

- player A/B identity
- both ready
- minimal device/version details behind diagnostics disclosure, not as visual noise

### Priority

The join code must be the most readable element in host state.

---

# 6. Setup/comfort IA

First launch exposes only high-value choices:

1. seated / standing
2. dominant hand
3. comfort defaults with an “ændr” option

Do not require every comfort setting before first play.

Full settings remain available from pause.

---

# 7. Wrist status

## Always-glanceable fields

- health
- fatigue
- injury indicator

## Conditional fields

- wet/cold modifier
- reconnect/pause utility
- return critical object utility

## Avoid

- exact hidden outcome probability
- long text descriptions
- resource spreadsheet

Player conditions should use:

**icon + shape/state + short label when expanded**.

---

# 8. Camp status — world first

## Shelter

Primary information = physical construction/damage.

Optional glance label may summarize:

- stable
- weak
- critical

## Fire

Primary information = fire visual/audio state.

Do not lead with “Fire Strength: 42”.

## Signal

Primary information = construction stage/readiness.

## Food/threat

Can use physical storage state + planning/status card summary.

---

# 9. Planning table IA

Each action card has:

### Required

- short action name
- icon
- effort cost
- qualitative gain
- qualitative risk/uncertainty only if known to players

### Optional after evidence

- condition warnings
- dependency indicator

### Avoid before evidence

- exact outcome percentages
- large tooltip walls
- internal state tags

## Effort state

Players should be able to answer at a glance:

- how many markers remain?
- where are they placed?
- is plan editable or locked?

---

# 10. Contextual interaction UI

Normal sequence:

1. world affordance
2. hover/target response
3. contextual fallback hint after inactivity

Do not display permanent button prompts everywhere.

Contextual hint must disappear after the action grammar is learned unless player continues struggling.

---

# 11. Storm IA

Storm UI should become **simpler**, not denser.

At each phase show only:

- phase title briefly
- immediate shared objective
- critical world targets

Camp history/causal detail waits until after-action.

## Bad storm UI

- three meters
- timer
- multiple quest objective lines
- player status cards
- action tutorial simultaneously

unless evidence proves all are necessary.

---

# 12. Reconnect state

When connection fails:

1. action transitions to safe pause
2. concise message appears
3. current recovery state visible
4. player has a clear fallback if recovery fails

No player-facing terms:

- authority
- protocol mismatch internals
- Photon region IDs
- snapshots/checksums

Diagnostics may expose those behind dev/diagnostic UI.

---

# 13. Error IA

Error message has three parts maximum:

1. what happened
2. what the game preserved/is doing
3. available next action

Example:

> **Checkpointet kunne ikke gemmes.**  
> Det forrige sikre punkt er bevaret.

Avoid generic modal stacks.

---

# 14. Subtitles

Subtitle unit includes:

- speaker label
- text
- optional directional cue

Settings:

- on/off where acceptable, but critical content must remain accessible
- normal/large/extra large
- background opacity

Voice source copy lives in `docs/40` / `content/localization/da.source.json`.

---

# 15. After-action IA

Order:

1. result
2. 2-4 strongest causal facts
3. optional individual titles if OQ-010 passes
4. retry/replay/exit

Do not dump the entire event journal.

## Causal card pattern

**What happened**  
short explanation of **because you chose...**

Example:

> **Dyrene fandt lejren**  
> I lod maden stå usikret på dag 1.

---

# 16. Diagnostics IA

Useful during development/release support, but hidden from normal flow.

May contain:

- game version
- build
- protocol
- content version/hash
- device/profile
- network region/ping
- export logs

Private personalization content must not be shown in diagnostics.

---

# 17. Screen/state inventory

| State | Required? | Owner of experience | Claude implementation |
|---|---:|---|---|
| Title/first launch | Yes | ChatGPT | Yes |
| Comfort setup | Yes | ChatGPT | Yes |
| Create/join lobby | Yes | ChatGPT | Yes |
| Ready/compatibility | Yes | ChatGPT | Yes |
| Pause | Yes | ChatGPT | Yes |
| Reconnect | Yes | ChatGPT | Yes |
| Critical error/recovery | Yes | ChatGPT | Yes |
| Subtitle presentation | Yes | ChatGPT copy/accessibility | Yes |
| Planning table | Yes | ChatGPT | Yes |
| Wrist status | Yes | ChatGPT | Yes |
| After-action | Yes | ChatGPT | Yes |
| Personalization epilogue | Yes | ChatGPT | Yes |
| Diagnostics | Dev/support | shared requirements | Yes |

---

# 18. UX acceptance criteria

A UI state is product-ready when:

- player knows the next meaningful action
- no critical information is hidden in dev terminology
- seated/standing does not change access
- text targets are VR-readable
- state is not color-only
- errors provide recovery
- copy key exists
- private/debug content is absent from normal release flow

Claude may optimize layout/implementation but should not remove an information requirement without flagging the product impact.
