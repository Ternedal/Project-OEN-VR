# Radio VO recording intake — PROJECT ØEN

**Source/session owner:** ChatGPT  
**Human gate:** performer + recording reviewer  
**Unity/runtime treatment:** Claude  
**Status:** intake/operator tooling ready; no recording or approval claimed

The canonical queue defines 9 Danish radio cues and 3 clean takes per cue. This lane converts that into a deterministic **27-file** private recording session with canonical spoken text, an operator board, technical validation and SHA-256 receipts.

## Prepare

```bash
python tools/prepare_radio_vo_session.py
```

This creates `PrivateContent/RadioVOSession/` with:

- `recording_session.json`
- `recording_board.html`
- `performer_provenance.json`
- `takes/`

`PrivateContent/` is already gitignored.

`recording_session.json` resolves every cue's `localizationKey` against `content/localization/da.source.json` and stores the canonical Danish `spokenText` in every take slot. Preparation fails closed if any of the nine radio localization keys is missing or blank. This prevents a performer from recording from a stale hand-copied script.

Open `recording_board.html` in a browser or print it. For each cue it shows:

- exact canonical Danish line
- delivery direction
- critical semantic that must survive the take
- target duration range
- all three required take filenames

The line is authoritative. Delivery direction controls tone, not wording.

Re-running preparation does not overwrite an already edited `performer_provenance.json`.

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

The operator board and canonical-text binding make recording safer; they do not constitute a recording, listening decision or permission decision.

## Claude boundary

Claude owns radio EQ/static/dropouts, spatialization, ducking, runtime binding, subtitle timing and Quest/headset intelligibility QA. Technical source intake proves none of those.
