# Audio field-backlog human review — PROJECT ØEN

**Owner lane:** ChatGPT / human source review  
**Runtime/mix owner:** Claude after explicit source approval  
**Status:** ready for human listening; nothing in this document is automatically approved

## Source under review

Target: `SFX_NAT_NIGHT_CRICKET_ALT_01`  
Runtime-event candidate: `SFX_NAT_Insect_NightChirp`  
File: `cricketsounds090613.wav`  
SHA-256: `ecc088a3d1ab967202b63a92836dadc47bd08c8ab3f17d8527f620264aa5faf9`  
License: CC0

Committed receipt: `content/audio/acquisition_field_backlog_receipt.source.json`.

Objective QA already records:

- PCM 16-bit stereo
- 44.1 kHz
- 38.542472 s
- no clipped samples
- peak about -20.9 dBFS
- very high L/R correlation; useful stereo width is unproven

Those facts are **not** a creative/source approval.

## Human listening focus

Review at a realistic playback level and record concrete notes for:

1. `CONTAMINATION` — laptop-mic/handling noise, voices, room noise or unrelated events.
2. `MATERIAL_MATCH` — does the insect character fit the intended island/night biome without relying on filename knowledge?
3. `LOOP_OR_SLICE` — are there usable chirp clusters/slices without obvious repetition?
4. `NOISE_FLOOR` — is the low-level recording clean enough after realistic gain staging?
5. `SPACE_IDENTITY` — does recording perspective/room character conflict with an outdoor night source?
6. `VARIATION_VALUE` — can enough genuinely distinct chirp groups be derived for the intended runtime event?
7. `SPEECH_SPACE` — would a bed/layer leave adequate room for partner and radio speech?

## Review input

Start from:

`content/audio/field_backlog_human_review.template.json`

Allowed dispositions:

- `candidate-pass`
- `reject`
- `needs-more-listening`
- `unreviewed`

Normalize the completed export with:

```bash
python tools/normalize_audio_field_backlog_review.py \
  --input field_backlog_review.json \
  --output field_backlog_review.normalized.json \
  --require-complete
```

The normalizer verifies the exact committed SHA-256 binding and check coverage. Its output status is `human-review-evidence-unapproved`; it **never** promotes `source-approved` automatically.

## If the source is later approved

The original is 44.1 kHz. Preserve the exact original bytes and hash. Create at most one documented derived 48 kHz project master where appropriate, assign a new SHA-256, and repeat listening QA on that derived file before any `derived-master-approved` status.

## Hard boundaries

- Acquisition/objective QA is not listening QA.
- A normalized review is evidence, not source approval.
- Source approval is not Unity integration.
- Claude owns final mix, spatialization, compression/import and Quest device listening QA.
