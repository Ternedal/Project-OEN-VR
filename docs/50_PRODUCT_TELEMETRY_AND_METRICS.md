# Product telemetry & metrics — PROJECT ØEN

**Product owner:** ChatGPT  
**Runtime implementation:** Claude  
**Dato:** 2026-08-13  
**Privacy model:** Local-first; ingen cloud analytics nødvendig i gaveversionen

## Formål

Projektet har allerede tekniske logs, aktiv-deltagelseslogik og causal journal i Core. Dette dokument definerer **hvilke produktmålinger vi faktisk har brug for**, hvorfor de måles, og hvilke data der ikke skal indsamles.

Målet er ikke analytics for analytics' skyld. Målingerne skal hjælpe med at besvare konkrete spørgsmål:

- forstår spillerne målet?
- skaber planning et reelt valg?
- er begge aktive?
- hvilke interactions skaber friktion?
- er consequence chains forståelige?
- holder scenariet 35-45 minutter?
- hvor falder replaylysten?

---

# 1. Privacy principles

Gift scope behøver ingen cloud telemetry.

Standard:

- metrics lagres lokalt
- eksport sker manuelt ved test/support
- session ID er random/anonym
- ingen fulde navne
- ingen private personalization strings/audio/images
- ingen automatisk voice recording/transcription
- ingen precise location/device account identity

Human comfort surveys ligger i playtest-noter og skal ikke automatisk kobles til identitet.

---

# 2. Product metric groups

## A. Session funnel

Spørgsmål: kommer to spillere faktisk fra launch til gameplay uden hjælp?

Mål:

- app launch → lobby visible
- lobby visible → partner connected
- partner connected → both ready
- both ready → scenario start
- join attempts
- join failures by normalized reason
- setup completion

Suggested event names:

- `session_launch`
- `lobby_visible`
- `session_create`
- `session_join_attempt`
- `session_join_success`
- `session_join_failure`
- `players_ready`
- `scenario_start`

No join code itself needs to be logged.

---

## B. Onboarding comprehension

Spørgsmål: lærer spillerne interaction grammar uden verbal developer-help?

Mål:

- time to first partner orientation
- time to first teleport
- first successful grab
- first shared heavy-object grab
- number of hints triggered
- number of critical-object returns/resets
- time from scenario start to understood objective (human observation, not automatically inferred)

Suggested events:

- `tutorial_step_started`
- `tutorial_step_completed`
- `hint_triggered`
- `critical_object_returned`

Human gate remains source of truth for “understood objective”. Runtime telemetry is supporting evidence only.

---

# 3. Planning metrics

## Important limitation

Runtime telemetry can measure **what players did**, not whether their conversation was meaningful.

M-Pre and later human observation remain authoritative for negotiation quality.

Useful automated measures:

- planning phase duration
- marker placements
- marker moves/reassignments
- plan revisions
- time from all markers allocated → plan lock
- number of invalid lock attempts
- action allocation distribution

Suggested events:

- `planning_started`
- `effort_marker_placed`
- `effort_marker_moved`
- `plan_revision`
- `plan_lock_attempt`
- `plan_locked`

## Derived metrics

- median planning time by day
- average marker moves per plan
- revisions per plan
- number of actions considered before lock, if observable without logging pointer noise

Do **not** infer “good cooperation” from many marker moves. High movement can also mean confusing UI.

---

# 4. Active participation

Core already contains `ActiveParticipationTracker`-style logic and the design gates require:

- both active ≥70% of action time
- design target: passive period <12s
- test failure boundary: >20s

Runtime summary per action/run should expose:

- active time Player A
- active time Player B
- both-active time
- longest passive period per player
- count passive periods >12s
- count passive periods >20s

Suggested summary event:

- `participation_summary`

Player-facing game does not need to show these numbers.

---

# 5. Interaction friction metrics

For each releasecritical interaction:

- interaction ID
- start/end
- outcome tier
- number of local retries/recoveries
- hint count
- reset count
- time to completion
- quality samples only where already part of authoritative gameplay logic

Suggested events:

- `interaction_started`
- `interaction_recovery`
- `interaction_completed`
- `interaction_abandoned`

Avoid logging raw hand positions unless specifically needed for a temporary debugging build. Product analytics do not require them.

---

# 6. Scenario pacing

Track durations:

- intro
- planning each day
- action phases
- nights
- storm phases 1-5
- epilogue
- after-action
- total scenario time

Suggested events:

- `phase_started`
- `phase_completed`

Derived:

- median full run 35-45 min target at M6
- longest phase
- variance between prepared vs pressed storm runs

---

# 7. Decision/consequence metrics

The event journal is authoritative for causal state.

Useful per run:

- actions selected
- relevant tags added/removed
- delayed events scheduled
- delayed events fired
- storm complications selected
- causal facts included in after-action

Suggested events or export fields:

- `gameplay_choice_committed`
- `delayed_event_scheduled`
- `delayed_event_fired`
- `storm_complication_started`
- `causal_report_generated`

## Product purpose

Use data to compare what players *experienced* with what after-action claims caused it.

Do not turn this into a hidden player scoring system.

---

# 8. Event fairness support

For OQ-008/human fairness testing, record enough to know what happened:

- candidate consequence set
- selected consequence ID
- whether selection was deterministic/weighted/random according to current test variant
- known earned tags/conditions

Do not use these logs to declare randomness fair. Human fairness/agency ratings remain required.

---

# 9. Hint / UX friction

Per key/state:

- hint triggered
- time before hint
- repeated hint
- UI validation failure
- return/reset action

Derived:

- most-triggered hints
- interactions requiring repeated hints
- phases with most UI errors

This helps identify where UI is rescuing unclear world design.

---

# 10. Reconnect / recovery product metrics

Technical detail belongs to Claude, but product summary should include:

- connection lost phase
- recovery succeeded yes/no
- time to recovery
- checkpoint fallback used yes/no
- session abandoned after failure yes/no

Suggested events:

- `peer_connection_lost`
- `reconnect_started`
- `reconnect_succeeded`
- `reconnect_failed`
- `checkpoint_resume_started`
- `checkpoint_resume_succeeded`

No IP address or account identifier required.

---

# 11. Save/retry metrics

Useful for release testing:

- checkpoint written
- checkpoint validation failure
- checkpoint resumed
- pre-storm retry selected
- full replay selected

Suggested events:

- `checkpoint_saved`
- `checkpoint_save_failed`
- `checkpoint_resumed`
- `storm_retry_selected`
- `scenario_replay_selected`

---

# 12. Outcome / replay intent

Automated:

- strong win / pressed win / loss
- retry selected
- replay selected
- exit selected

Human survey:

- “Har I lyst til at prøve igen?”
- why/why not

Automated replay click is not a substitute for qualitative motivation.

---

# 13. Comfort metrics

Comfort is a **human-reported measure**, not inferred from motion.

Use `docs/42_HUMAN_QA_PLAYTEST_PACK.md` ratings at 15/30/45 min:

- nausea
- eye strain
- dizziness
- arm/shoulder fatigue
- reach frustration
- mental overload

Runtime may provide phase/time markers so survey results can be correlated to game sections.

---

# 14. Technical performance boundary

Claude owns actual performance telemetry implementation:

- frame time
- CPU/GPU
- memory
- thermal
- network stats

Product needs phase labels so performance spikes can be mapped to:

- planning
- ravine
- storm phase 1-5
- epilogue

Do not duplicate technical metrics into a second independent system if Unity tooling already records them.

---

# 15. Local export format — conceptual

A test export should contain:

```json
{
  "sessionId": "random-id",
  "build": "...",
  "contentVersion": "...",
  "devices": ["Q2", "Q3"],
  "scenarioId": "SCN_STORMNATTEN_001",
  "events": [],
  "summaries": {
    "phaseDurations": {},
    "participation": {},
    "outcome": "..."
  }
}
```

Exact schema/file format is an implementation choice, but private personalization content must not be embedded.

---

# 16. Product dashboard for manual test review

A lightweight post-test summary should answer:

1. Run duration
2. Outcome
3. Planning duration/revisions
4. Both-active percentage + passive outliers
5. Top hint triggers
6. Top interaction retries/resets
7. Delayed consequences that fired
8. Storm branches
9. Reconnect/recovery incidents
10. Replay/retry selected

This can initially be a generated text/JSON report; no polished analytics UI is required.

---

# 17. Data retention

Development/test exports may be retained only as long as useful for QA/history.

If shared outside Anders' own environment:

- remove tester names
- remove private content
- review logs for paths/device identifiers

Gift release does not require continuous analytics retention.

---

# 18. Metrics anti-goals

Do not add metrics for:

- engagement streaks
- monetization
- behavioral advertising
- personal profiling
- voice sentiment
- relationship scoring
- “which partner is better”

They do not serve the product and create unnecessary privacy/experience costs.

---

# 19. Acceptance criteria

Product telemetry is correctly specified when:

- every metric answers a known product/QA question
- no private personalization data is required
- human judgments are not replaced by fake automated proxies
- active participation and causal report can be exported per run
- phase timing supports 35-45 min validation
- reconnect/retry paths are measurable
- Claude can implement/extend logging without inventing product metrics
