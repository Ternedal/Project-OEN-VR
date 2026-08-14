# Adaptive music family selection + source materialization — PROJECT ØEN

**Source/product owner:** ChatGPT  
**Human gate:** real listener selection after complete candidate audition  
**Runtime/adaptive owner:** Claude  
**Status:** tooling only; no family selection or source approval claimed

The existing 14-candidate audition answers **what the reviewer hears in each candidate**. This lane answers the next separate question: **which, if any, candidate should represent each canonical music cue?**

It deliberately preserves a negative outcome. If no candidate is good enough, the correct result is `needs-new-source`, not a forced selection.

## 1. Complete the 14-candidate audition first

Use the existing flow:

```bash
python tools/prepare_music_candidate_review.py --output music_candidate_review.json
python tools/normalize_music_candidate_review.py \
  --input music_candidate_review.json \
  --output music_candidate_review.normalized.json \
  --require-complete
```

Normalized status remains:

`human-music-audition-evidence-unapproved`

## 2. Make exact candidate WAVs available

The original artifact may expire, but candidate bytes are reproducible from source. In the pinned reproducibility environment:

```bash
python -m pip install -r tools/requirements-music-repro.txt
python tools/generate_authored_adaptive_music.py \
  --output build/oen-authored-adaptive-music-v1 \
  --clean
```

The selection preparer verifies all 14 candidate WAV SHA-256 values against `content/audio/music_candidate_audit.source.json`. A mismatching regeneration/artifact is rejected.

## 3. Prepare human family selection

```bash
python tools/prepare_music_family_selection.py \
  --audition music_candidate_review.normalized.json \
  --candidate-dir build/oen-authored-adaptive-music-v1
```

Open:

`build/oen-authored-adaptive-music-v1/music_family_selection.html`

The five canonical targets are:

- `MUS_CAMP_BASE_001`
- `MUS_STORM_BASE_001`
- `MUS_STORM_PRESSURE_001`
- `MUS_SIGNAL_FINAL_001`
- `MUS_RESCUE_RELEASE_001`

A candidate is selectable only when its prior human audition has:

- `fit = keep`
- every exact applicable check = `pass`
- the same current audit family/target/hash binding

For each canonical family the selector records one of:

- `select`
- `needs-new-source`
- `needs-more-listening`

`MUS_Warning_LowPulse` remains visible in the original 14-candidate audition but has **no canonical target** and is excluded from family selection regardless of its audition score. Binding it later requires a separate product decision first.

## 4. Normalize selection evidence

```bash
python tools/normalize_music_family_selection.py \
  --input build/oen-authored-adaptive-music-v1/music_family_selection.json \
  --audition music_candidate_review.normalized.json \
  --output music_family_selection.normalized.json \
  --require-complete
```

Output status is deliberately:

`human-music-family-selection-evidence-unapproved`

A complete negative selection is valid evidence. `readyForSourceMaterialization` becomes true only when all five canonical families explicitly select one eligible exact candidate.

## 5. Materialize selected source identities

Only after a positive 5/5 selection:

```bash
python tools/materialize_music_selected_sources.py \
  --selection music_family_selection.normalized.json \
  --audition music_candidate_review.normalized.json \
  --candidate-dir build/oen-authored-adaptive-music-v1 \
  --output build/selected_music_source
```

The output filenames are the canonical cue IDs:

```text
MUS_CAMP_BASE_001.wav
MUS_STORM_BASE_001.wav
MUS_STORM_PRESSURE_001.wav
MUS_SIGNAL_FINAL_001.wav
MUS_RESCUE_RELEASE_001.wav
music_selected_source_receipt.json
```

Every output WAV is a byte-for-byte copy of the selected audited candidate and must have the identical SHA-256. The receipt explicitly records that source, derived-master and runtime approval are **not** promoted by copying.

## No hidden processing

Materialization performs no trim, loop edit, EQ, gain, resample, compression, stem split, crossfade or adaptive runtime treatment.

Any later source/master edit creates a new identity and needs documented processing plus another listening pass. Claude owns crossfades, ducking, mixer behavior, adaptive state logic and Quest/headset acceptance.
