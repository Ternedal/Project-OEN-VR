# 37 — Audio production pipeline

## Purpose

This document turns the runtime audio architecture into a reproducible production lane for Project ØEN. The goal is to keep source provenance, mastering, Unity import and Quest 2 constraints explicit instead of collecting anonymous WAV files in the project.

The current first-playable audio state is deliberately split between deterministic authored material, reproducibly built Public Domain/CC0 candidates, manually reviewed field recordings and bespoke Foley. A generated or technically valid candidate is never treated as mastered merely because it exists in an artifact.

## Production lanes

### Lane A — authored in repo

Use deterministic synthesis for sounds where realism is not the primary requirement and a consistent game identity matters more than field-recording authenticity.

Current authored set:

- UI/status pack: **65 WAV variations**
- gameplay-feedback/stinger pack: **66 WAV variations**
- adaptive-music candidate pack: **14 WAV variations across all 6 `MUS_*` events**
- authored total: **145 original WAV files** with no third-party samples

The authored generators and validators live under `tools/`; their authoritative manifests are:

- `content/audio/authored_audio_manifest.csv`
- `content/audio/authored_gameplay_stinger_manifest.csv`
- `content/audio/authored_adaptive_music_manifest.csv`

Source contract for authored PCM masters:

- 48 kHz
- 24-bit PCM WAV
- channel layout determined by the runtime role
- -3 dBFS peak ceiling where applicable
- deterministic generation

CI regenerates and validates all authored packs before first-playable staging.

### Lane B1 — CI-buildable Public Domain / CC0 environmental candidates

Use this lane to create reproducible technical candidates from explicitly reviewed, redistributable source recordings without requiring a service login.

The source registry is `content/audio/public_domain_environment_sources.csv`. Every source row records the canonical source page/direct endpoint, creator, accepted license state, verification data and pinned SHA-256. `tools/build_public_domain_environment_pack.py` refuses unapproved license states and refuses source bytes that differ from their pinned hash.

`content/audio/environment_candidate_build.csv` currently defines **28 environmental candidate WAVs** across these runtime events:

- `SFX_AMB_Beach_OceanNear` — 2
- `SFX_AMB_Beach_OceanFar` — 2
- `SFX_WTH_Rain_Light` — 1
- `SFX_WTH_Rain_Heavy` — 1
- `SFX_WTH_Storm_Wind` — 2
- `SFX_ENV_Fire_Idle` — 1
- `SFX_ENV_Fire_Low` — 1
- `SFX_AMB_Jungle_DayBed` — 1
- `SFX_NAT_Insect_CicadaCluster` — 4
- `SFX_WTH_Thunder_Far` — 3
- `SFX_AMB_Shore_Wash` — 10

Every derivative is 48 kHz / 24-bit PCM WAV and `PROVENANCE.csv` records both source and output hashes together with source page, creator and license.

The existing-source candidate audit is explicit and CI-guarded:

- `SFX_AMB_Shore_Wash` is accepted as a candidate build from `waves_pd`; the ten cuts are widely separated temporal selections and remain `candidate-headset-listen`.
- the old `wind_cc0` source is rejected for `SFX_AMB_Ridge_WindBed` because its perspective/length cannot support four authentic exposed-ridge long beds;
- the same source is rejected as proof of ten clean localized outdoor `SFX_WTH_Storm_WindGust` events;
- the old `fire_pd` source is rejected for 14 `SFX_ENV_Fire_Pop` variations because it is too short to prove fourteen genuine independent transients.

`tools/validate_public_domain_candidate_audit.py` fails CI if an accepted/rejected source pairing drifts away from those decisions.

**Important:** this remains a *candidate pack*, not a mastered environmental release. Technical normalization and provenance do not replace listening QA, seamless-loop editing or scene/headset approval.

Before promotion from candidate to production:

1. Listen to every full derivative on neutral headphones and Quest.
2. Reject speech, music, traffic, handling noise or source-specific contamination.
3. Edit loop-intended assets into genuinely seamless loops; do not rely on Unity looping a raw cut.
4. Verify Near/Far variants read as different distances rather than simple gain copies.
5. Check fire against the actual campfire visual scale and attenuation.
6. Check rain/wind/thunder under the complete storm and shelter mixes.
7. Change status only after the approved derivative is frozen and its production hash is recorded.

### Lane B2 — manually reviewed CC0 / Public Domain field recordings

Use real recordings from libraries such as Freesound when they offer materially better source quality than the CI-buildable set, especially for tropical ambience/fauna, rain-on-tarp, long natural wind, thunder, rough ocean, shore birds and fire transients.

This lane now has two distinct registries with different meanings:

- `content/audio/field_source_acquisition_plan.csv` — source-page-verified acquisition candidates for the **11 remaining field-source backlog events**. The plan currently contains **22 candidate mappings** and every event has at least one primary candidate.
- `content/audio/reviewed_field_recording_sources.csv` + `content/audio/reviewed_field_recording_jobs.csv` — originals that have entered the controlled reviewed-ingest lane and exact derivative jobs selected from them.

`field_source_acquisition_plan.csv` is authoritative for the remaining backlog discovery step. `field_recording_candidates.csv` remains a useful broader shortlist/history but must not be treated as proof that a source has passed the acquisition gate.

A source-page-verified acquisition candidate is **not** production audio. It means only that creator/title/license/format/duration and obvious suitability risks have been checked on the canonical page. Before it can become a reviewed source:

1. Download the canonical original; never use a preview/transcode as master.
2. Listen to the original and explicitly review the recorded risk flags.
3. Reconfirm creator, title and license on the exact source page.
4. Compute SHA-256 from the original bytes.
5. Add/promote the source in `reviewed_field_recording_sources.csv` and pin that SHA-256.
6. Select exact clean source regions by listening before any derivative job becomes `ready`.
7. Render 48 kHz / 24-bit PCM derivatives.
8. Listen again in headphones and Quest before promotion beyond candidate status.

`tools/validate_field_source_acquisition_plan.py` enforces acquisition-plan coverage in CI. It requires all 11 current `production_lane=field-source` backlog events to remain represented, checks variation-count parity, accepted licenses, source metadata, primary-candidate coverage and a minimum 120-second source threshold for primary long-bed candidates. It deliberately does not invent or require source SHA-256 before the original has actually been acquired.

The reviewed-source builder is `tools/build_reviewed_field_recording_pack.py`. It does not download authenticated library originals. With manually acquired files present it can audit `missing`, `needs-pin`, `hash-mismatch` and `verified`; production rendering refuses a `ready` source whose expected SHA-256 is absent or wrong.

See `docs/38_REVIEWED_FIELD_RECORDING_INGEST.md` and `docs/44_FIELD_SOURCE_ACQUISITION_GATE.md` for the exact ingest/promotion contracts.

### Lane C — bespoke Foley / recording

Prefer fresh recordings when a world interaction is visually specific to ØEN and generic libraries would weaken the tactile result.

The current recording plans cover:

- main Foley: **40 events / 388 selected variations**
- supplemental Foley: **13 events / 90 selected variations**

Examples include rope tension/release, tarp handling, wood/stone interactions, footsteps, threat foliage/branch/scrape cues, fire interactions, generic pickup/drop fallback and construction gestures.

These are recording plans, not produced assets. Variation sets must come from genuinely different performances/temporal events rather than one sample multiplied by pitch randomisation.

## Field-recording preparation

`tools/prepare_field_recording.py` is a controlled one-file ingest utility. It does not download anything. It requires a reviewed local source and ffmpeg, then creates a 48 kHz / 24-bit derivative with conservative loudness and optional mono downmix for 3D world emitters.

Examples:

```text
python tools/prepare_field_recording.py source.wav out.wav --kind bed
python tools/prepare_field_recording.py source.wav out_mono.wav --kind oneshot --spatial
```

For batch production from manually acquired and SHA-pinned reviewed originals, prefer `tools/build_reviewed_field_recording_pack.py` so source/output provenance remains explicit.

## Unity landing layout

Production derivatives land under semantic folders:

```text
Assets/ProjectOen/Audio/
├── 2D/
│   ├── OneShots/
│   │   ├── UI/
│   │   └── Status/
│   ├── Compressed/
│   │   └── Stingers/
│   └── Streaming/
│       ├── Ambience/
│       ├── Weather/
│       └── Music/
└── Spatial/
    ├── OneShots/
    │   ├── Environment/
    │   ├── Footsteps/
    │   ├── Nature/
    │   └── Crafting/
    └── Streaming/
        └── Environment/
```

`ProjectOenAudioImportPostprocessor` enforces the corresponding Quest-oriented Unity settings:

- `/Spatial/` forces mono
- `/Streaming/` uses Streaming + Vorbis
- `/OneShots/` uses Decompress On Load + ADPCM
- `/Compressed/` uses Compressed In Memory + Vorbis
- all files are imported at 48 kHz

A file outside one of these load-profile folders gets a warning and conservative compressed fallback.

## First-playable staging

The current combined CI-built Unity artifact is `oen-unity-first-playable-audio-v1` and contains:

- **173 WAV files**
- **47 populated runtime events out of 115 canonical events**
- **68 events still without produced WAVs**
- **0 unassigned missing events**

The staging pipeline combines the authored UI/status pack, authored gameplay/stinger pack, adaptive-music candidate pack and Public Domain/CC0 environment pack. Reviewed field sources are added only when their source/job rows are genuinely ready.

After extraction at the Unity project root, the Editor path is:

`Project Oen > Audio > Build + Install First Playable (One Click)`

The installer keeps a stable fail-closed minimum below the current additive artifact count, validates clip/event coverage, protects listener/service ownership and does not auto-save the scene.

## Review gates

### Per-file

- correct event/variation name
- no clipping
- clean start/end; no accidental edit clicks
- 48 kHz after preparation
- intended channel layout
- no obvious DC offset or unexpected silence
- source/provenance hash present for externally sourced recordings once they enter reviewed/production state

### Variation-set

- genuinely different transients/timing/textures
- no single sample dominates random selection
- pitch/volume randomisation remains subtle
- repeated triggering for 30–60 seconds does not expose a pattern

### VR world sound

- localization is credible with head rotation
- min/max distance is believable at physical scene scale
- no important cue disappears under surf/rain
- shelter transitions do not create phasey double-beds
- 3D sources remain mono unless there is a deliberate exception

### Quest 2

- profile simultaneous voices in the storm scene
- keep the baseline one-shot pool at 24 until measured otherwise
- confirm streaming beds do not produce audible stalls
- avoid expensive DSP as a substitute for good source placement
- approve ambience, thunder, shore wash and music in the actual headset rather than from desktop speakers alone

## Current status

Implemented and CI-guarded:

- 115-event production manifest / 788 planned variations
- runtime event/catalog/service layer and world-state routing
- authored UI/status, gameplay/stinger and adaptive-music candidate generation
- 145 authored WAV files across those packs
- verified Public Domain / CC0 source registry with pinned hashes
- 28-file environmental candidate build with provenance
- explicit audit of accepted/rejected existing environmental source roles
- field-source acquisition plan with 22 candidate mappings covering all 11 remaining field-source backlog events
- field-source acquisition validator
- reviewed-field source/job registry and SHA-gated derivative builder
- main and supplemental Foley recording plans
- Unity import postprocessor, asset/catalog population and one-click first-playable installer
- first-playable readiness reporting with zero unassigned events
- combined Unity artifact with 173 WAV / 47 events

Still required for production-quality completion:

- physical Unity 6000.4.10f1 import/compile and scene inspection
- Quest 2 listening/mix/performance approval
- headset approval and seamless-loop QA of current environmental/adaptive candidates
- canonical-original acquisition, listening and SHA-pinning for reviewed tarp/Amazon sources
- canonical-original acquisition, listening and SHA-pinning for the 11 field-source events now covered by the acquisition plan
- exact clean segment selection and reviewed derivative rendering for those sources
- physical recording/select/edit of 388 main + 90 supplemental Foley variations
- final imported-scene mix and repetition QA

A green CI run proves reproducibility and structural correctness. It does not replace the physical Unity, source-listening or Quest headset gates.
