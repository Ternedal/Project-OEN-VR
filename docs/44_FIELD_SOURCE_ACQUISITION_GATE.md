# Field-source acquisition gate

This document closes the source-discovery gap between `audio_production_backlog.csv` and reviewed field-recording ingest without pretending that a web page is a production master.

## Current state

The field-source backlog contains 11 runtime events. `content/audio/field_source_acquisition_plan.csv` now gives every one of those events at least one primary source-page-verified candidate, plus secondary candidates where useful.

A source-page-verified candidate means only that the canonical source page has been checked for creator, title, license, format, sample rate, bit depth/channel metadata, duration and obvious suitability risks. It is **not** equivalent to a reviewed or production-ready source.

## Hard gates

A candidate may move from acquisition into `reviewed_field_recording_sources.csv` only after all of the following are true:

1. The canonical original has been downloaded from the source page. Preview/transcoded playback is never a production source.
2. The original has been listened to end-to-end or across every region intended for extraction.
3. Contamination called out in `risk_flags` has been checked explicitly: speech, traffic, birds, rain, waves, recorder artifacts, clipping, indoor perspective or other event-specific problems.
4. The source-page creator/title/license still matches the acquisition row.
5. SHA-256 has been computed from the downloaded original and pinned in `reviewed_field_recording_sources.csv`.
6. Exact trim regions have been selected by listening before any `reviewed_field_recording_jobs.csv` row becomes `ready`.
7. Derivatives are rendered as 48 kHz / 24-bit PCM WAV and then listened to again in headphones and on Quest.

## CI contract

Run:

```bash
python tools/validate_field_source_acquisition_plan.py
```

The validator enforces that:

- every current `production_lane=field-source` backlog event is covered;
- no stale event outside the field-source backlog is silently carried in the plan;
- target variation counts match the backlog;
- every event has at least one primary page-verified source candidate;
- only `CC0`, `CC0-1.0` or `Public-Domain` candidates are active;
- source metadata and review instructions are present;
- primary ambience/storm beds have at least a 120-second source candidate;
- the next action always preserves canonical-original download rather than a preview shortcut.

The validator intentionally does **not** require a SHA-256 yet. That belongs to the reviewed-ingest gate after the original exists locally.

## Highest-value candidates

The current shortlist deliberately favors real field recordings rather than generated ambience:

- beach palm canopy: real offshore wind through palm trees;
- jungle canopy: long Cambodian canopy-wind recording, with thunder/artifact regions explicitly flagged for rejection;
- ridge wind: a real hilltop ORTF wind recording, supplemented by a separate exposed-field candidate;
- rough ocean: strong Atlantic wind and large waves, with a second close coastal storm recording;
- storm gusts: outdoor coastal gust material plus a much longer gusty-wind fallback;
- near thunder: several independent CC0 field recordings plus a long storm source for additional event discovery;
- shore birds: two independent coastal bird sources, with speech contamination explicitly gated;
- night insects: long cricket recordings intended for genuine temporal selections rather than pitch-only duplication;
- fire pops: two separate two-minute Zoom H6 fireplace recordings, to be mined only for natural unique wood transients.

## What remains blocked

The source-discovery task is now structured, but the 11 events remain `source-needed` on purpose. They must not be counted as produced until original files are acquired, listened to, hashed, segmented, rendered and Quest-QA'd.

This keeps readiness reporting honest while making the next production pass deterministic: download the primary candidates first, audit/pin them, then promote only clean segments into reviewed jobs.
