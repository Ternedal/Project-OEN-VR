# ChatGPT-workstream — PROJECT ØEN

**Ejer:** ChatGPT  
**Projektejer:** Anders  
**Opdateret:** 2026-08-13  
**Scope:** Alt uden for Unity jf. `AI_COLLABORATION_AGREEMENT.md`

## Arbejdsregel

ChatGPT ejer produkt/content/source/QA uden for Unity. Claude ejer Unity/runtime/editor/XR/Fusion/C#/build/device-runtime.

M0b + M-Pre blokerer **M1 runtime-implementation**. De blokerer ikke non-Unity sourceproduktion, content contracts, provenance, testværktøj eller handoff-forberedelse.

Human/device evidence må aldrig opfindes.

---

# Aktuelle gates

## M0b — issue #3

Per-client Quest-feasibility er bevist. Der mangler stadig faktisk to-headset-evidens for:

- remote head/hands
- compatibility mismatch rejection
- shared two-player box state
- 10× Q2↔Q3 lift uden permanent desync
- 72 Hz minimal network scene
- standby/reconnect-måling
- opdateret compatibility matrix

Issue #3 har en operationel capture-checkliste. Resultater ejes af Claude/Anders.

## M-Pre — issue #7

Ready-to-run, men **ikke kørt**. Tre faktiske menneskesessioner med mindst to par mangler.

Klar tooling:

- `prototype/m-pre/facilitator_runner.html`
- `prototype/m-pre/print_pack.html`
- `tools/evaluate_mpre.py`
- CI-kontrakt-tests for evaluator/runner/printpakke

AI/simulation kan ikke bestå gaten.

## Content scope — issue #8

Intro og Day 3 er nu løst på product/content-laget:

- `content/onboarding/stormnatten.onboarding.source.json`
- `content/phases/stormnatten.day3_planning.source.json`
- `content/contracts/issue8.reconciliation.source.json`
- `docs/62_ISSUE8_CANONICAL_CONTENT_RESOLUTION.md`

Canonical Day-3 planning bruger kun eksisterende actions:

- `INT_REINFORCE_ROOF_006`
- `INT_BUILD_SIGNAL_009`
- `INT_TREAT_INJURY_011`
- `INT_SECURE_SUPPLIES_005`

De gamle proposal-only IDs `INT_REPAIR_SHELTER_008` og `INT_COLLECT_DRY_FUEL_014` er superseded.

**Fire-start er stadig owner-gated:** `implementationAllowed=false`, ikke accepted gift scope, ingen timer ændret. Issue #8 forbliver åbent til Anders disponerer scope.

---

# Verificeret non-Unity source på main

## Art/source

- A1 UI/source kit
- A2 core props: **10 individual masters**
  - firesteel
  - tinder
  - rope coil
  - plan table
  - heavy crate
  - shelter beam
  - shelter frame
  - shelter rope
  - shelter tarp
  - signal frame
- A3 storm/VFX inkl. rope-strain
- A4 camp/wreck/radio/signal references
- B1 jungle/ravine/ridge + resource items + supply crate
- B2 event presentation for alle 10 events
- A5 source meshes/items/release UI
- material families
- P1/P2 handwear
- neutral fallback package

Source-ready er **ikke** Unity-integrated eller release-approved.

## Content/UX contracts

Canonical/machine-readable contracts omfatter bl.a.:

- dansk localization
- Stormnatten actions/events/event presentation
- planning/status UI binding
- release UI binding
- after-action presentation
- material families
- neutral personalization
- canonical onboarding
- canonical Day-3 planning
- issue #8 reconciliation
- audio acquisition/listening contracts

`examples/stormnatten.scenario.json` har stadig den ældre phase-list. Den store full-file connector-rewrite blev bevidst undgået. Ved den gated runtime/data-binding skal Claude synkronisere faseforløbet til:

`DAY2_PLANNING -> DAY3_PLANNING -> DAY3_STORM`

uden at genindføre stale proposal IDs.

---

# Naturalistisk audio — faktisk status

Audio er ikke længere kun en acquisition-plan.

## Acquired originals

GitHub Actions-run `31737461883` hentede tre licensverificerede CC0 originals uden at committe binær audio til Git:

### AMB_WIND_WORLD

- `park_ambience_wind.wav`
- SHA-256 `5c381856745b4706e7eba55eb9271a61a530e90c05df8126adb2db89ecfa6c5a`
- 48 kHz / 24-bit / stereo / 256.8 s

### AMB_RAIN_ALT

- `amb_rain2.flac`
- SHA-256 `c33d833842c88e9559882b35f6f149c3a96bbf236eb34491e36ea4cae8879985`
- 48 kHz / 16-bit / stereo / 733.0 s
- measured true peak +0.1 dBFS → attenuate/inspect before any derived processing

### SFX_FIRE_ALT

- `fire.wav`
- SHA-256 `85ca0cc60d0c037fff8b185e31ad1fcdbda6ce45eee17c3ee1318d1b8f59e330`
- 44.1 kHz / 32-bit / stereo / 29.26 s
- if approved, derived master requires quality resample to 48 kHz

Source of truth:

- `content/audio/acquisition_receipt.source.json`
- `content/audio/acquisition_technical_qa.source.json`
- `content/audio/listening_review_targets.source.json`
- `content/audio/listening_qa.source.json`

Objective review-navigation is prepared with representative quiet/typical/loud windows and exact peak timestamps.

**Ingen af de tre filer er human listening-approved, source-approved, derived-master-approved eller release-approved.**

## Additional direct candidates

`content/audio/acquisition_candidates.direct_extension.source.json` adds license-verified direct ocean/wood/cloth candidates. They are **not acquired** yet.

## Radio / music

- Radio VO: 9 cues × 3 takes specificeret; recording mangler.
- Music: direction/cue-sheet klar; actual composition/source mangler.

---

# Open Claude draft PRs — re-sync required before physical QA

## PR #5 — production art

Draft remains physical-QA-blocked.

Current branch comparison against main: **255 ahead / 214 behind** at review time.

A PR comment now requires:

- sync current main first
- rerun repo/art guards
- source-stamp physical evidence against the post-sync head
- preserve owner-gated fire-start semantics and canonical Day-3 content

## PR #6 — audio/runtime first playable

Draft remains physical-QA-blocked.

Current branch comparison against main: **188 ahead / 214 behind** at review time.

A PR comment now requires:

- sync current main first
- rerun Audio Validation and central guards
- regenerate/re-pin payload if sync changes staged artifact
- collect Unity/Quest evidence only against post-sync head/pin
- preserve acquired-original receipts without silently promoting them into the first-playable payload

Do not merge either draft based on old physical evidence or old `0 behind` PR text.

---

# CI / quality

Active guards include:

- Core tests
- Validate handoff
- Validate non-Unity sources
- Validate source inventory
- Validate M-Pre evaluator/runner/printpakke
- action placeholder-cost mirror
- AU-1 regeneration/validation
- event presentation validation

PR #17 (canonical onboarding/Day3) passed Core, handoff, non-Unity and source-inventory before merge.

---

# Known status/connector debt

- `content/source_inventory.source.json` is correct for A2=10 masters but still lags the newest audio acquisition + canonical issue #8 contract registrations; attempted full rewrite was filtered.
- `repo_status.md` remains older than this workstream.
- M-Pre CI still executes some runner tests twice under discovery due an older import; coverage is green, dedup is cosmetic debt.
- repair-mallet and ember-carrier attempts were not committed and must not be counted as delivered.
- no filtered/uncommitted artifact counts as production.

---

# Next real work

1. **M-Pre:** run 3 human sessions, then evaluate actual CSV.
2. **M0b:** ingest actual two-headset evidence from Claude/Anders.
3. **Issue #8:** Anders decides fire-start scope; reconcile hours only if scope changes.
4. **Audio:** human listening-QA the three acquired originals; only approved source may proceed to derived masters.
5. **Audio:** acquire remaining direct/field candidates where licensing and provenance stay explicit.
6. **Claude drafts #5/#6:** re-sync current main before authoritative physical QA.
7. Continue non-Unity source work only when a concrete missing master reduces implementation ambiguity; avoid art for art's sake.
8. M1 product/UX handoff only when both M0b + M-Pre are green.

---

# Arbejdsregel ved “kør videre”

1. check current main/issues/PRs/CI
2. take highest unblocked non-Unity task
3. do not edit Unity/runtime code
4. produce concrete source/contracts/tooling, not pseudo-progress
5. QA and preserve provenance
6. never invent human/device evidence
7. never promote acquired audio without the required listening gate
