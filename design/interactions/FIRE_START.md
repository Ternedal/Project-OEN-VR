# Interaction brief — Fire start

**Owner:** ChatGPT  
**Unity implementation:** Claude  
**Related:** Scenario Beat 1 · PO-044 · `docs/05` · `docs/44`

## Player fantasy

The first fire is a small survival victory: one player creates the spark, the other makes it possible for the spark to survive.

The interaction should teach the core rule of PROJECT ØEN:

> physical execution + cooperation matter together.

## Scope note

The scenario bible treats first fire as onboarding-critical, while backlog item `PO-044` is currently deferred. This brief does **not** change backlog scope. It makes the intended interaction explicit so the later scope decision is informed rather than accidental.

## Roles

### Player A — shield

- positions a wind shield / hands-off object near tinder
- tracks wind direction cue
- keeps the tinder in a broad protected zone

### Player B — igniter

- holds firesteel
- makes 1-3 clear strike gestures against an oversized strike zone
- feeds the first ember when it catches

Roles may swap if the first attempt struggles.

## Sequence

1. Tinder is visibly placed in the firepit.
2. Wind makes the unprotected state visibly/audio unstable.
3. Shield player creates a protected zone.
4. Igniter strikes firesteel.
5. A poor strike may create no spark; a good strike creates visible spark/ember.
6. If protection is weak, ember degrades rather than disappearing instantly.
7. Players add dry fuel.
8. Fire transitions to a stable small/strong state.

## Outcome model

### Critical success

- good protection
- clean strike(s)
- ember survives immediately
- minimal tinder/fatigue cost

### Success

- fire catches normally

### Partial with cost

- ember survives but needs extra fuel/time
- tinder quality/resources reduced

### Fail-forward

- players create recoverable embers or learn/read a clear local failure state
- no full sequence reset after one bad motion

Exact outcome thresholds/tuning wait gameplay evidence.

## Assets

- `PRP_FIREPIT_001`
- `ITM_FIRESTEEL_001`
- `ITM_TINDER_001`
- `PRP_WIND_SHIELD_001`
- `ITM_WOOD_BUNDLE_001`

## Audio

- `SFX_FIRESTEEL_STRIKE_001`
- `SFX_FIRE_IGNITION_001`
- `SFX_FIRE_EMBERS_001`
- `SFX_FIRE_SMALL_001`
- `SFX_FIRE_STRONG_001`
- `SFX_FIRE_FUEL_ADD_001`

## Copy fallback

- `hint.fire.protect_tinder`
- `hint.fire.strike`
- `hint.fire.together`
- `hint.fire.embers`
- `hint.fire.success`

Hints appear only after inactivity/failed affordance discovery, not immediately as tutorial subtitles.

## Feedback contract

### Wind protection

Must be readable through at least two channels:

- tinder/flame motion
- audio state
- optional world guide/shape

### Spark success

- visible spark
- short sound/haptic
- ember state persists long enough to read

### Stable fire

- obvious world-state change
- warm ambience/lighting intention
- audio state increases

Lighting implementation belongs to Claude.

## Comfort

- no rapid repetitive striking
- no forceful arm swings
- strike zone large enough to avoid precision frustration
- shield does not require sustained awkward wrist angle
- all objects usable seated and standing

## Pacing

First successful sequence should be short. If players need repeated fire-start later, later instances can be abbreviated because the interaction grammar is already learned.

## Human QA

Observe:

- does shield player understand they materially affect success?
- does igniter know where/how to strike without verbal explanation?
- do failures communicate recovery?
- does either player feel like a prop-holder?

## Acceptance criteria for Claude

- both players can affect quality
- ember/failure states are continuous/readable, not binary mystery
- no bad strike forces a full restart
- critical information has non-audio equivalent
- interaction works for mixed seated/standing pair
