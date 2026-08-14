# Radio VO recording intake — PROJECT ØEN

**Source/session owner:** ChatGPT  
**Human gate:** performer + recording reviewer  
**Unity/runtime treatment:** Claude  
**Status:** intake tooling ready; no recording or approval claimed

The canonical queue defines 9 Danish radio cues and 3 clean takes per cue. This lane converts that into a deterministic **27-file** private recording session with technical validation and SHA-256 receipts.

## Prepare

```bash
python tools/prepare_radio_vo_session.py
```

This creates `PrivateContent/RadioVOSession/` with `recording_session.json`, `performer_provenance.json` and `takes/`. `PrivateContent/` is already gitignored.

## Naming

Raw takes use:

```text
VO_RADIO_NIGHT1_01__T01.wav
VO_RADIO_NIGHT1_01__T02.wav
VO_RADIO_NIGHT1_01__T03.wav
...
VO_RADIO_END_NEUTRAL_03__T03.wav
```

Raw takes are never silently renamed into the selected canonical dry master.

## Technical acceptance

Each take must be uncompressed integer PCM WAV, 48 kHz, 24-bit, mono, dry/unprocessed, with zero full-scale samples.

Duration is measured against the cue target, but a mismatch is a **warning**, not an automatic reject: delivery timing remains a human judgement.

## Provenance

Before intake, fill `performer_provenance.json` with source type, stable name/alias, permission/license basis, date, commercial-reuse answer, and `identifiablePublicPersonImitation: false`.

## Validate

```bash
python tools/validate_radio_vo_session.py
```

A clean 27/27 session receives status:

`technical-intake-passed-not-listening-approved`

and writes `radio_vo_intake_receipt.json` with per-take SHA-256, byte count, sample rate, bit depth, channels, duration, peak and full-scale sample count.

## Human gates remain

A human still must approve Danish pronunciation, tone/delivery, semantic parity, rights/provenance and select exactly one take per cue. Any edit to a selected dry master creates a new file identity/hash and requires review again.

## Claude boundary

Claude owns radio EQ/static/dropouts, spatialization, ducking, runtime binding, subtitle timing and Quest/headset intelligibility QA. Technical source intake proves none of those.
