# Project ØEN — Quest 2 audio pre-merge evidence

> **Post-merge status (2026-08-15):** PR #49 is integrated on `main`, but no Quest 2 listening/soak evidence is thereby claimed. The template and importer below remain the required fail-closed path for promoting the three physical Quest audio gates against the pinned 173/47 payload.

## Purpose

The three Quest 2 audio merge gates require real headset work. CI cannot listen, judge spatial perspective, or measure a device soak. It can, however, prevent incomplete or stale physical evidence from being promoted as a pass.

The committed non-passing template is:

`content/audio/quest2_premerge_evidence_template.json`

The validator/importer is:

`tools/import_audio_quest2_premerge_evidence.py`

The template is bound to the current pinned first-playable payload:

- device: `Quest 2`;
- profile: `Q2_BASE`;
- manifest SHA-256: `319b38b302465f4a7148adb562e9f2b9f12c80ef78d6456ae58d95fcce6e72f1`;
- clips/events: `173 / 47`.

If the first-playable payload changes, physical evidence for the old manifest must not be reused. Update/re-verify `content/audio/first_playable_artifact_pin.json`, regenerate the template binding, and rerun physical QA against the new build.

## Capture workflow

1. Copy `content/audio/quest2_premerge_evidence_template.json` to a working evidence file outside the template path.
2. Install the build containing the **pinned current first-playable artifact** on Quest 2.
3. Fill in:
   - `build_id`;
   - UTC `tested_utc`;
   - `tester`;
   - a concrete `evidence_reference` pointing to the device log, QA note, capture bundle, or equivalent.
4. Execute every functional-smoke item and change an item to `true` only when it was physically exercised successfully.
5. Listen through every mix category and change an item to `true` only after headset approval.
6. Run the audio-heavy storm path/soak for at least **20 minutes** on `Q2_BASE` with device metrics captured.
7. Fill in measured voice peak and metrics reference.
8. Set each section's `passed` field to `true` only after all its subordinate acceptance points are satisfied.
9. Run the importer read-only first.
10. Apply only after inspecting the evidence.

Read-only validation:

```bash
python tools/import_audio_quest2_premerge_evidence.py \
  --evidence build/audio-quest2-premerge-evidence.json
```

Apply accepted evidence to the three Quest rows:

```bash
python tools/import_audio_quest2_premerge_evidence.py \
  --evidence build/audio-quest2-premerge-evidence.json \
  --apply
```

The importer cannot promote any Unity gate.

## Functional smoke gate

All checks below are mandatory:

- Beach Day / Calm;
- Jungle Day / Calm;
- unavailable states resolve to silence rather than stale beds;
- Calm -> Wind -> RainFire -> Signal progression;
- exterior -> shelter -> exterior roundtrip;
- Jungle Day cicada state gating;
- RainFire distant-thunder state gating;
- listener-relative spatial behaviour while rotating/moving the head/player;
- no duplicate emitters/coroutines after repeated state changes;
- no missing important cues;
- no audible streaming stalls.

`functional_smoke.passed=true` is insufficient by itself. The importer requires every subordinate boolean to be `true`.

## Mix/listening gate

All checks below are mandatory in the headset:

- Shore Wash candidates;
- distant-thunder candidates;
- environmental beds;
- adaptive storm music;
- biome/weather/music transitions;
- loop seams acceptable;
- storm masking acceptable;
- no unacceptable clipping;
- no unacceptable contamination;
- spatial perspective/scale credible.

The purpose is not to call candidate material mastered. It is to establish that the exact first-playable payload proposed for merge is technically credible and not obviously broken on the target headset.

## Performance-soak gate

The thresholds come from `docs/08_PLATFORM_BUILD_PERFORMANCE.md`:

- device/profile: Quest 2 / `Q2_BASE`;
- hard display gate: **72 Hz**;
- storm soak: **at least 20 minutes**;
- audio streaming stalls: **0**;
- no sustained audio-induced frame regression;
- no material audio-related memory growth;
- simultaneous audio voices are measured;
- project target is **<24 simultaneous voices** — i.e. 23 or fewer is inside the target.

If measured peak voices are **24 or higher**, `voice_budget_exception` becomes mandatory. That field must explain why the measured exception is acceptable and should point to measured/profiling evidence. A blank exception at the 24-voice boundary or above is rejected.

`metrics_reference` is always required for a passing soak so the result is traceable to OVR Metrics/Meta tooling/Unity Profiler or equivalent device evidence.

## Fail-closed behaviour

`tools/import_audio_quest2_premerge_evidence.py` rejects at minimum:

- wrong device or profile;
- wrong/stale manifest SHA;
- wrong clip/event coverage;
- missing build/tester/evidence reference;
- non-UTC or missing test time;
- any incomplete functional-smoke checkbox;
- any incomplete listening checkbox;
- a soak shorter than 20 minutes;
- a target other than 72 Hz;
- any audio streaming stall;
- sustained audio-induced frame regression;
- material audio-related memory growth;
- missing measured voice count;
- 24+ voices without an explicit budget exception;
- missing metrics reference.

Audio Validation runs the importer in `--self-test` mode against a temporary QA registry. The self-test proves that valid synthetic structure is accepted, stale/short/24-voice-boundary-without-exception/incomplete evidence is rejected, only the three Quest gates can be promoted, and the three Unity rows remain untouched.

The synthetic self-test is **not physical evidence** and never mutates `content/audio/audio_premerge_qa.csv`.

## Physical acceptance sequence

After the three Unity gates and three Quest gates have real accepted evidence:

```bash
python tools/report_audio_merge_readiness.py --strict
```

Strict mode independently refuses a manually edited `passed` row unless its evidence marker comes from the correct category importer and is bound to the current pinned manifest/173/47 payload.

PR #49 has already landed the repository baseline after exact-head CI. Strict mode is still required before the integrated audio baseline may be described as physically accepted on Quest; merge status must not be confused with that acceptance state.
