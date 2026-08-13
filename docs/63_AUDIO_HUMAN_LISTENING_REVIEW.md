# Audio human listening review — acquired originals + PR #6 candidates

**Owner lane:** ChatGPT / Anders source review  
**Runtime/mix owner:** Claude after source approval  
**Status:** ready for human listening; nothing in this document is automatically approved

## Purpose

There are now two real, inspectable audio lanes:

1. three license-verified CC0 **originals acquired outside Git history** and documented on `main`;
2. PR #6's public-domain/CC0 **derived environmental candidate pack**, independently downloaded and hash-audited.

This review decides only whether individual sources/candidates deserve promotion to the next audio-production stage. It does **not** prove Unity integration, Quest spatialization, final mix or release readiness.

---

# A. Main-acquired originals

Source of truth:

- `content/audio/acquisition_receipt.source.json`
- `content/audio/acquisition_technical_qa.source.json`
- `content/audio/listening_review_targets.source.json`
- `content/audio/listening_qa.source.json`

## A1. Wind — `AMB_WIND_WORLD`

File: `park_ambience_wind.wav`  
SHA-256: `5c381856745b4706e7eba55eb9271a61a530e90c05df8126adb2db89ecfa6c5a`

Start with:

- 50–60 s — objectively quiet region
- 80–90 s — objectively typical region
- 30–40 s — objectively loud region
- 115.156 s — inspect around global sample peak

Listen for:

- birds / local wildlife that makes the recording geographically specific
- traffic, voices or handling contamination
- exposed-island character rather than sheltered park character
- useful gust bodies/tails for editing
- speech masking

## A2. Rain — `AMB_RAIN_ALT`

File: `amb_rain2.flac`  
SHA-256: `c33d833842c88e9559882b35f6f149c3a96bbf236eb34491e36ea4cae8879985`

Start with:

- 470–480 s — objectively quiet region
- 430–440 s — objectively typical region
- 330–340 s — objectively loud region
- **202.877 s — mandatory peak inspection**

Technical warning:

- measured true peak reaches about **+0.1 dBFS**
- do not normalize upward
- attenuate before any derived processing

Listen for:

- enclosure/roof/window coloration
- recorder handling or nearby object noise
- loop/slice usefulness
- whether the intensity belongs in the intended storm layers
- speech masking

## A3. Fire — `SFX_FIRE_ALT`

File: `fire.wav`  
SHA-256: `85ca0cc60d0c037fff8b185e31ad1fcdbda6ce45eee17c3ee1318d1b8f59e330`

Start with:

- 5–10 s
- 10–15 s
- 15–20 s
- 11.635 s — global peak region

Listen for:

- indoor fireplace / room identity
- whether the fire size fits a small improvised camp fire
- transient variety
- loop seam potential
- speech masking

If accepted, a derived master must be resampled from 44.1 kHz to 48 kHz with a quality resampler, then listened again.

---

# B. PR #6 environmental candidate artifact

Artifact source:

- PR #6 — `agent/audio-foundation-v1`
- Audio Validation #180 environmental candidate artifact ID `9171323145`
- downloaded artifact SHA-256 `e3029dc5e25fc38bdee64f71aed5d2c7f9381e65cb57524dfb2d3340ac1258aa`

Main-side independent audit:

- `content/audio/pr6_environment_artifact_audit.source.json`
- `content/audio/pr6_environment_artifact_technical_qa.source.json`

Verified:

- 28 WAVs / 28 provenance rows
- 28 unique output hashes
- 28/28 hashes match `PROVENANCE.csv`
- 0 missing / 0 hash mismatches
- all files 48 kHz / 24-bit PCM
- no objective true-peak clipping blocker; highest measured true peak is about −3 dBFS
- every file remains `candidate-headset-listen`

## B1. First priority — Fire Idle vs Fire Low

Compare at matched playback gain and without relying on filenames:

- `SFX_ENV_Fire_Idle_01.wav`
- `SFX_ENV_Fire_Low_01.wav`

Objective finding:

- same 8.916 s duration
- both about −25.2 LUFS
- both about −3.0 dBTP
- normalized spectral-shape similarity ≈ 0.9981
- RMS-envelope correlation ≈ 0.9999
- full decoded sample correlation ≈ 0.9841

They are not byte-identical, but they are objectively extremely similar.

**Pass only if the listener can reliably describe a meaningful fire-state difference at matched gain.** If the difference is merely subtle EQ/processing or the label is needed to tell them apart, re-derive or collapse one state.

## B2. Second priority — Ocean Near vs Ocean Far

Both perspective groups derive from the same `waves_pd` source.

Review at matched gain. A louder file must not automatically count as "near".

Pass only if perspective/distance reads meaningfully differently in context.

## B3. Third priority — Shore Wash pool

There are 10 unique ~7 s cuts, all derived from `waves_pd`.

Review as a **randomized rapid sequence**, not one file at a time with labels visible.

Listen for:

- repeated wave timing/signatures
- obvious same-source repetition
- enough distinct attack/body/tail shapes for a ten-variation pool

If repetition is obvious, keep only the genuinely distinct cuts rather than preserving variation count for its own sake.

## B4. Remaining groups

Review:

- 2 × Storm Wind — common source, objectively different envelopes
- 4 × Cicada Cluster — common source
- 3 × Thunder Far — common source
- Rain Light / Rain Heavy
- Jungle Day Bed

Check contamination, biome fit, perspective, repetition and speech space per `content/audio/listening_qa.source.json`.

---

# Human review record

For every file/group record:

- reviewer/date
- exact filename/event/variation
- source SHA-256 or candidate output SHA-256
- applicable listening checks
- concrete notes
- one disposition:
  - `source-approved` / `candidate-pass`
  - `rejected`
  - `needs-more-listening`

A rejection must say why. An approval must preserve the hash/provenance it applies to.

## Hard rules

- Technical QA is not listening QA.
- Do not overwrite originals.
- Do not edit and silently keep the original hash.
- Derived masters require their own new hash + listening pass.
- PR #6 remains physical-QA-blocked and must sync current `main` before authoritative Unity/Quest evidence.
- Source approval is not Unity-integrated or release-approved.
