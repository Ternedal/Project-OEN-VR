# Foley human review and source approval — PROJECT ØEN

**Source/review owner:** ChatGPT + human reviewer  
**Runtime/mix owner:** Claude  
**Status:** Review + explicit source-promotion tooling ready; no recording or human approval is claimed

## Purpose

`docs/74_FOLEY_RECORDING_INTAKE.md` ends at technical intake. A technically valid WAV can still be the wrong material, a weak variation or unreadable under storm/weather.

This lane adds the human evidence gate between a completed 73-take recording session and any `source-approved` state.

## Preconditions

The session must contain a passing:

`foley_intake_receipt.json`

with status:

`technical-intake-passed-not-listening-approved`

The review tooling revalidates the receipt against:

- current Foley queue/reconciliation/session contract
- `recording_session.json`
- `foley_provenance.json`
- all 73 actual WAV SHA-256 values

If any take, provenance or session binding changed after technical intake, review preparation fails closed.

## 1. Prepare the review board

```bash
python tools/prepare_foley_human_review.py \
  --session PrivateContent/FoleySession
```

This creates:

- `foley_human_review.template.json`
- `foley_human_review_board.html`

The browser board exposes all 73 raw takes grouped under 17 canonical cue families. No human decision is prefilled.

## 2. Human review model

### Per raw take

Choose exactly one:

- `keep`
- `needs-rerecord`
- `needs-more-listening`

Every planned variation is a distinct physical performance. A weak or duplicate-feeling performance should not be marked `keep` merely to satisfy count.

### Per cue family

Choose exactly one:

- `accept-current-set`
- `needs-rerecord`
- `needs-more-listening`

Then complete the eight canonical listening-QA checks from `content/audio/listening_qa.source.json`:

- CONTAMINATION
- MATERIAL_MATCH — 1–5
- LOOP_OR_SLICE
- NOISE_FLOOR
- TRANSIENT_QUALITY
- SPACE_IDENTITY
- VARIATION_VALUE — 1–5
- SPEECH_SPACE

Foley adds one extra mandatory cue-family check:

- `UNDER_WEATHER_READABILITY`

For this check, compare the cue against a representative weather bed at intended game-like level. Partner speech remains the higher mix priority. The browser board does not synthesize or fake this listening condition.

## 3. Normalize evidence

Export `foley_human_review.json` from the board, then run:

```bash
python tools/normalize_foley_human_review.py \
  --session PrivateContent/FoleySession \
  --input foley_human_review.json \
  --output foley_human_review.normalized.json \
  --require-complete
```

A complete negative review is valid evidence. For example, a `needs-rerecord` take or `MATERIAL_MATCH=2` normalizes successfully but yields:

`readyForSourceMaterialization=false`

## Positive eligibility

Source materialization requires all of the following at the same time:

- reviewer alias present
- review timestamp present
- provenance still hash-matches technical intake
- `commercialReuseAllowed=true`
- all 73 take decisions = `keep`
- all 17 cue decisions = `accept-current-set`
- all typed checks complete
- MATERIAL_MATCH >= 3 for every cue
- VARIATION_VALUE >= 3 for every cue
- all pass-required listening checks pass
- UNDER_WEATHER_READABILITY = pass for every cue
- all 73 current raw WAV hashes still match the technical receipt

## 4. Explicit source-approved materialization

Only after a positive normalized review:

```bash
python tools/materialize_foley_source_approved.py \
  --session PrivateContent/FoleySession \
  --review foley_human_review.normalized.json \
  --output PrivateContent/FoleyApproved
```

The materializer **recomputes eligibility**. Manually changing a JSON field to `readyForSourceMaterialization=true` cannot bypass the gate.

On success it copies all 73 raw WAVs byte-for-byte to:

`source_approved/{cueId}/{filename}`

and writes:

`foley_source_approved_receipt.json`

The operation performs no trim, EQ, denoise, gain, resample, layering, loop edit or transcoding.

## State boundary after promotion

A successful Foley source materialization means only:

- human-approved raw source identity exists
- original bytes are preserved
- provenance and review evidence are bound

It does **not** mean:

- a derived/edit master is approved
- Unity integration exists
- Quest mix/performance is accepted
- release approval exists

Any later edit enters the project-wide derived-master technical + repeated-human-listening gate.

## Fire-start boundary

`SFX_FIRESTEEL_STRIKE_001` and other fire-start-specific capture remain outside this lane while issue #8 is owner-gated. This tooling must not silently turn the fire-start interaction into accepted gift scope.
