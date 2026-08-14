# AU-1 synthetic feedback source

**Owner:** ChatGPT  
**Date:** 2026-08-13  
**Status:** 12 production WAV masters committed; reproducible generator retained

## Scope

AU-1 deliberately covers only cues that can be credibly produced procedurally:

- effort marker pickup/place/move
- plan ready/lock/conflict
- join success
- reconnect start/success
- generic confirm/warning/soft error

Generator:

```bash
python source_audio/au1/generate_au1.py --output /tmp/oen-au1
```

Committed output is in `production/`: mono PCM WAV, 48 kHz, 16-bit, plus a
manifest with duration, peak and SHA-256.

## Source and committed derivatives

The generator is the source master for this batch. It keeps the cues:

- deterministic
- reviewable
- regenerable without a binary source dependency
- easy to revise by changing actual synthesis parameters

The canonical waveform source remains the deterministic generator. Its 12 exact
WAV derivatives are now committed so Unity can import real audio files directly
without a separate generation step. CI regenerates them and compares their
bytes against the committed masters.

## Not covered

Do **not** use this generator as a fake replacement for naturalistic source material:

- rain ambience
- rope/fiber handling
- shelter creaks
- fire loops
- animal threat
- environmental ambience
- radio voice
- music

Those remain actual recording/library/generative-audio production work with provenance and QA.

## Product intent

Cues are short, soft and non-punitive. Planning feedback must feel tactile rather than timer-like. Warning/error cues are deliberately gentle; they should not sound like desktop OS errors.

## Claude boundary

Claude owns:

- final Unity import/compression
- mixer routing
- spatial/non-spatial binding
- runtime volume
- ducking
- Quest device audibility/comfort

If device testing shows a cue is masked or annoying, source synthesis can be revised without changing the cue ID.
