# Project OEN — Adaptive music candidate pack v1

## Purpose

This pack supplies original, sample-free candidate music for the existing adaptive music layer. It is intentionally sparse and subordinate to diegetic audio. It is **not** promoted to mastered/production status until headset listening and in-scene mix approval are complete.

## Contents

| Event | Variations | Duration | Loop | Intent |
|---|---:|---:|---|---|
| `MUS_Camp_WarmTexture` | 3 | 90 s | yes | warm, unresolved camp texture |
| `MUS_Warning_LowPulse` | 3 | 60 s | yes | low-state warning pulse |
| `MUS_Storm_Phase1` | 2 | 90 s | yes | wind-phase pressure |
| `MUS_Storm_Phase2` | 2 | 90 s | yes | rain/fire-phase tension |
| `MUS_Storm_Phase3` | 2 | 90 s | yes | signal-phase maximum tension |
| `MUS_Finale_Success` | 2 | 24 s | no | short success resolution |

Total: **6 events / 14 WAV files / 1,038 seconds**.

## Technical profile

- 48 kHz / 24-bit PCM WAV
- stereo only; this is the non-spatial music layer
- -6 dBFS peak target to preserve headroom for weather, fire, tarp and gameplay cues
- no third-party samples
- deterministic procedural synthesis
- NumPy dependency pinned in `tools/requirements-audio-authoring.txt`
- loop tracks use oscillator frequencies rounded to integer cycle counts over the complete file duration
- no forced fade-to-silence on loop tracks
- finale tracks are intentionally non-looping and use a long release

## Local build

```bash
python -m pip install -r tools/requirements-audio-authoring.txt
python tools/generate_authored_adaptive_music.py \
  --clean \
  --output build/oen-authored-adaptive-music-v1 \
  --zip build/oen-authored-adaptive-music-v1.zip
python tools/validate_authored_adaptive_music.py \
  --input build/oen-authored-adaptive-music-v1
```

## QA contract

`validate_authored_adaptive_music.py` requires:

- exact event/variation counts from this candidate pack
- stereo 48 kHz / 24-bit PCM
- exact expected durations
- peak around -6 dBFS
- bounded RMS level
- non-identical stereo channels
- no duplicate WAV payloads
- bounded wrap discontinuity for all 12 looping files
- `candidate-headset-listen` status in the pack manifest

## Unity usage

The existing `AudioWorldStateRouter` remains authoritative for when the profiles play:

- Calm: silence or `MUS_Camp_WarmTexture`
- Wind: `MUS_Storm_Phase1`
- RainFire: `MUS_Storm_Phase2`
- Signal: `MUS_Storm_Phase3`

`MUS_Warning_LowPulse` is reserved for low-state warning treatment and must not become a constant exploration bed. `MUS_Finale_Success` is a one-shot finale cue.

## Promotion gate

Before any clip is marked mastered:

1. listen to every full file on headphones and Quest headset;
2. verify no audible seam in the 12 looping tracks;
3. audition transitions Calm -> Wind -> RainFire -> Signal in-scene;
4. mix under simultaneous ocean/wind/rain/fire/tarp layers;
5. verify critical interaction/status cues remain intelligible;
6. profile decompression/streaming behavior on Quest 2;
7. only then bind approved clips into production `AudioEventDefinition` assets.
