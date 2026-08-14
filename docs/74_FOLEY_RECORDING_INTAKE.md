# Physical Foley recording intake — PROJECT ØEN

**Source owner:** ChatGPT / human recordist  
**Runtime/mix owner:** Claude  
**Status:** Operator + technical intake ready; no recording is claimed

## Purpose

The project already defines the physical material intent for heavy crate, rope/tarp and shelter timber in:

- `content/audio/foley_recording_queue.source.json`
- `content/audio/foley_session_reconciliation.source.json`
- `docs/58_AUDIO_SOURCE_PRODUCTION_SPEC.md`

This lane turns those contracts into a repeatable recording session without pretending that source audio exists before someone actually records it.

## Current capture shape

- 3 queue sessions
- 3 reconciled physical setups
- 13 canonical cue IDs
- **53 raw variation slots**
- WAV, 48 kHz, 24-bit integer PCM, mono
- no full-scale samples

The 53 slots are real physical performances. Do not satisfy variation count by copying a WAV, changing gain, pitching one take or renaming the same bytes.

Fire-start-specific recording is not included. `SFX_FIRESTEEL_STRIKE_001` remains outside this lane while issue #8 is owner-gated.

## 1. Prepare the private session

```bash
python tools/prepare_foley_session.py --output PrivateContent/FoleySession
```

This creates:

- `recording_session.json` — exact queue/reconciliation/contract bindings and all 53 expected paths
- `recording_board.html` — printable/operator-friendly capture board
- `foley_provenance.json` — blank provenance template, created only if it does not already exist
- `takes/<queue-session>/` directories

Preparation does **not** create fake WAVs and does not count as recording evidence.

`recording_session.json` is hash-bound to the current queue, reconciliation and session contract. If the source contracts change, regenerate the session before recording.

## 2. Fill provenance before final intake

Complete `foley_provenance.json` with:

- recordist alias
- recording timestamp
- recording chain
- rights statement
- commercial reuse decision
- source materials for each physical session
- coarse location class, not a street address
- explicit no-background-speech/no-background-music declarations
- notes

Existing provenance is never overwritten by `prepare_foley_session.py`.

## 3. Record the actual performances

Use `recording_board.html` and preserve the exact filenames/paths.

The three material families are:

1. heavy crate / wooden mass
2. rope + tarp under real physical tension
3. shelter timber / structural creak and shift

Capture raw, dry source audio. Do not bake runtime urgency, radio treatment, storm beds, EQ, compression or Unity processing into the only source master.

Target durations are navigation guidance. A duration outside the requested window is a **technical warning**, not automatic semantic rejection.

## 4. Run technical intake

```bash
python tools/validate_foley_session.py --session PrivateContent/FoleySession
```

On a complete technical pass it writes:

`PrivateContent/FoleySession/foley_intake_receipt.json`

with status:

`technical-intake-passed-not-listening-approved`

The validator checks:

- session bindings are still current
- exactly the expected WAV paths are used
- all 53 planned takes exist
- WAV is uncompressed integer PCM
- 48 kHz / 24-bit / mono
- no full-scale samples
- SHA-256 and byte count per raw take
- exact duplicate raw bytes are rejected
- provenance is complete
- target-duration differences are reported as warnings

## 5. What technical PASS does not mean

A technical pass does **not** prove:

- heavy objects sound heavy enough
- rope sounds like rope instead of cable
- tarp sounds like heavy shelter fabric
- low/high structural strain are perceptually distinct
- 53 variants have enough human-perceived variation
- a cue survives a weather bed
- a raw take is source-approved
- an edited cut is derived-master-approved
- Unity/Quest mix is acceptable

Those remain human listening and later runtime/device gates.

## Evidence boundary

Keep raw WAVs under private/local storage or an explicit evidence artifact; do not commit the 53 recording binaries to public Git history merely to prove the tooling works.

Any selected raw source remains immutable. Any trim, edit, EQ, denoise, gain, resample or composite creates a new file identity and must enter the documented derived-master + repeated-listening lane.
