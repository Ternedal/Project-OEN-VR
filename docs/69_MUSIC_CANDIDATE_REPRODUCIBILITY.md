# Adaptive music candidate reproducibility — PROJECT ØEN

**Owner:** ChatGPT  
**Runtime owner:** Claude  
**Status:** generator preserved; exact-byte CI required; no approval implied  
**Date:** 2026-08-14

## Why this exists

The 14 adaptive-music candidates audited in `content/audio/music_candidate_audit.source.json`
originated in PR #6 / Audio Validation run #180. The GitHub Actions artifact that carries
those candidate WAVs is retained only until **2026-08-20T06:50:10Z**.

The source generator is therefore preserved on `main` independently of PR #6's Unity/runtime
stack. No WAV binary is committed by this lane.

## Preserved source identity

`tools/generate_authored_adaptive_music.py` is copied byte-for-byte from PR #6 generator blob:

`e857bb1be24cc1de413f43e5b370fb133cb81b30`

The source run that produced the audited artifact reported:

- Ubuntu 24.04.4 LTS
- GitHub runner image `ubuntu-24.04`, image version `20260720.247.2`
- x86_64
- CPython `3.12.13`
- NumPy `2.3.5`
- generator version `1.0.0`

## Why exact SHA is the gate

A cross-environment check with CPython 3.13.5 + NumPy 2.3.5 reproduced **12/14**
candidate WAVs byte-for-byte. The two non-looping `MUS_Finale_Success` renders differed
at a small number of PCM bytes.

That means “same algorithm + same NumPy version” is not a sufficient identity claim across
arbitrary environments. Review evidence is attached to exact WAV hashes, so regenerated audio
must not silently inherit that review identity.

CI therefore rebuilds all 14 candidates under the closest preserved authoring environment and
requires every output byte count and SHA-256 to match `music_candidate_audit.source.json`.

If a future GitHub runner image causes hash drift, CI must fail. The correct response is to
investigate/re-audit the changed bytes, not relax the hash comparison.

## Run the exact check

```bash
python -m pip install -r tools/requirements-music-repro.txt
python tools/validate_music_candidate_reproducibility.py
```

The exact validator intentionally rejects a Python version other than 3.12.13, NumPy other than
2.3.5, or a non-x86_64 architecture.

## Approval boundary

Exact reproduction proves candidate identity only. It does **not** prove:

- human listening approval;
- source/master approval;
- that a candidate fits the canonical musical role;
- Unity/runtime binding;
- Quest/headset behavior;
- release approval.

`MUS_Warning_LowPulse` remains unmapped unless a separate product decision creates a canonical use.
