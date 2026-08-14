# Adaptive music candidate audition — PROJECT ØEN

**Source/product owner:** ChatGPT  
**Origin:** audited candidate artifact from draft PR #6  
**Runtime/adaptive implementation:** Claude  
**Status:** audition-ready candidates; no source approval claimed

## Why this exists

`main` has a complete music direction but no approved source masters. Draft PR #6 already produced a separate artifact of original procedural candidate music. Re-composing another pack before listening would create waste.

This lane preserves the candidates as **external audition material** without merging PR #6's Unity/runtime stack.

## Audited artifact

- workflow: Audio Validation #180
- source head: `6b3d22f4b7a3e100fa7d237331b66225e55d0f4f`
- artifact: `oen-authored-adaptive-music-v1`
- 14 WAV files
- 48 kHz / 24-bit / stereo
- original deterministic procedural generation
- no third-party samples embedded
- 14/14 WAV SHA-256 values independently matched the pack manifest

The artifact and its generator still require human listening before production promotion.

## Canonical audition mapping

Candidate families are auditioned against existing canonical product roles:

- `MUS_Camp_WarmTexture` → `MUS_CAMP_BASE_001`
- `MUS_Storm_Phase1` → `MUS_STORM_BASE_001`
- `MUS_Storm_Phase2` → `MUS_STORM_PRESSURE_001`
- `MUS_Storm_Phase3` → `MUS_SIGNAL_FINAL_001`
- `MUS_Finale_Success` → `MUS_RESCUE_RELEASE_001`

`MUS_Warning_LowPulse` is **not mapped**. No canonical runtime cue exists for that family on `main`; it may be auditioned but not bound or promoted without a separate product decision.

## Human audition

Create a blank hash-bound form:

```bash
python tools/prepare_music_candidate_review.py --output music_candidate_review.json
```

For every file assess:

- speech space / partner communication
- genre fit
- dramaturgy fit
- technical structure
- loop seam for looping candidates or ending shape for finale candidates
- overall keep / maybe / reject

Normalize completed evidence:

```bash
python tools/normalize_music_candidate_review.py \
  --input music_candidate_review.json \
  --output music_candidate_review.normalized.json \
  --require-complete
```

A passing normalized result is deliberately named:

`human-music-audition-evidence-unapproved`

It is evidence, not automatic source promotion.

## Promotion boundary

Even after an audition, source promotion requires an explicit selection per canonical family, stable source/generator provenance, and a final source/master identity. Claude then owns adaptive runtime implementation, crossfades/ducking, mixer behavior and Quest/headset QA.
