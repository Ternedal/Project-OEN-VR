# 37 — Audio production pipeline

## Purpose

This document turns the runtime audio architecture into a reproducible production lane for Project ØEN. The goal is to keep source provenance, mastering, Unity import and Quest 2 constraints explicit instead of collecting anonymous WAV files in the project.

## Production lanes

### Lane A — authored in repo

Use deterministic synthesis for sounds where realism is not the primary requirement and a consistent game identity matters more than field-recording authenticity.

Current v1 pack:

- all UI hover/select/back/error sounds
- page/map/inventory interactions
- radio click/static
- Health/Fatigue/Injury/Cold-Wet status feedback

`tools/generate_authored_audio_pack.py` emits 65 original WAV files. No third-party samples are embedded. CI regenerates the pack, verifies format/determinism and publishes `oen-authored-ui-status-v1.zip` as an Actions artifact.

Source contract:

- 48 kHz
- 24-bit PCM WAV
- mono
- -3 dBFS peak ceiling
- deterministic generation

`content/audio/authored_audio_manifest.csv` is the authoritative list for this pack.

### Lane B — CC0 field recordings

Use real recordings for environmental material where procedural synthesis would sound artificial in VR:

- ocean and shoreline
- jungle beds and fauna
- rain and rain-on-tarp
- campfire beds and crackles
- natural wind and storm gusts
- thunder

Candidates are recorded in `content/audio/field_recording_candidates.csv`. A candidate is not production audio merely because it is listed. Before ingest:

1. Open the original source page.
2. Verify the license on that exact item.
3. Record creator/title/source URL/license.
4. Listen for speech, music, traffic, handling noise and other contamination.
5. Reject material that creates obvious loops or source-specific artefacts in headset.
6. Keep the original source file outside the Unity runtime folder.

Freesound candidates that require login are intentionally not auto-downloaded by CI.

### Lane C — bespoke Foley / recording

Prefer fresh recordings when a world interaction is visually specific to ØEN and generic libraries would weaken the tactile result:

- rope tension/release
- tarp handling/flaps
- wood pickup/drop/chop/break
- stone pickup/drop/hit
- crate/container actions
- build hammer/place
- footsteps for the final art surfaces

These should be recorded as variation sets, not one sample with pitch randomisation pretending to be a set.

## Field-recording preparation

`tools/prepare_field_recording.py` is the controlled ingest step. It does not download anything. It requires a reviewed local source and ffmpeg, then creates a 48 kHz / 24-bit derivative with conservative loudness and optional mono downmix for 3D world emitters.

Examples:

```text
python tools/prepare_field_recording.py source.wav out.wav --kind bed
python tools/prepare_field_recording.py source.wav out_mono.wav --kind oneshot --spatial
```

Keep the reviewed source/provenance record alongside the derivative metadata. Do not overwrite the original recording.

## Unity landing layout

The Unity project should receive production derivatives under these semantic folders:

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

## Review gates

### Per-file

- correct event/variation name
- no clipping
- clean start/end; no accidental edit clicks
- source rate 48 kHz after preparation
- intended channel layout
- no obvious DC offset or unexpected silence

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

## Current status

Implemented:

- 115-event production manifest
- runtime event/catalog/service layer
- biome/day-night/weather/music routing
- footsteps, fire, tarp and random world emitters
- authored UI/status generator: 65 WAV variations
- authored-pack deterministic QA
- CI-built downloadable authored ZIP artifact
- CC0 field-recording shortlist
- field-recording preparation tool
- Unity import postprocessor

Still required for the full sound pack:

- reviewed and edited environmental recordings
- bespoke Foley variation sets
- final stingers/adaptive music masters
- Unity asset definitions/catalog population with real clips
- imported-scene and Quest 2 listening/performance pass
