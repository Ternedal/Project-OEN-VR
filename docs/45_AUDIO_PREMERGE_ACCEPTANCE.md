# Project ØEN — Audio pre-merge acceptance

## Purpose

PR #6 is a first-playable audio foundation, not a claim that all 115 runtime events already have final mastered source material. The repository therefore separates two things that must not be conflated:

1. **merge blockers for this audio foundation** — physical Unity/Quest validation of the code and current 173-WAV / 47-event artifact;
2. **explicit full-production backlog** — field-source originals and Foley that remain real future production work and are already assigned to concrete registries/plans.

The machine-readable merge gate is:

`content/audio/audio_premerge_qa.csv`

The report command is:

```bash
python tools/report_audio_merge_readiness.py \
  --csv build/audio-merge-readiness.csv \
  --markdown build/audio-merge-readiness.md
```

Normal CI reports the gate state but does not deliberately turn otherwise-correct software CI red merely because a Quest is not attached to GitHub Actions.

After every physical gate has been executed and its evidence recorded, run:

```bash
python tools/report_audio_merge_readiness.py --strict
```

Strict mode must return zero before the physical merge gate is considered satisfied.

## Why this is the merge boundary

Everything that can be proved reproducibly without the real Unity project/device is now CI-owned:

- canonical audio IDs/manifests;
- authored pack determinism;
- Public Domain/CC0 source hashes and environmental derivative provenance;
- explicit source acceptance/rejection decisions;
- field-source acquisition coverage for every remaining field-source backlog event;
- Foley recording-plan coverage;
- first-playable readiness lane coverage with zero unassigned missing events;
- staged artifact count/event count and duplicate event/variation rejection;
- `FIRST_PLAYABLE_MANIFEST.csv` generation with per-WAV byte count and SHA-256;
- Unity Editor static serialized-field contract;
- fail-closed manifest/hash audit before Unity catalog or scene mutation;
- stale `AudioEventDefinition` clip cleanup;
- current-manifest-only catalog membership;
- generated profile membership synchronization while preserving valid-layer gains;
- scene/runtime ownership rules;
- explicit listener ownership and listener-relative fauna/weather routing;
- one-click and direct-install parity on integrity checks;
- no scene auto-save.

The remaining merge gates require a real Unity Editor and/or Quest 2 and cannot honestly be synthesized by CI.

## Six required physical gates

### 1. `unity_import_compile`

Use Unity **6000.4.10f1** with the actual Project ØEN project.

Acceptance:

- extract the current `oen-unity-first-playable-audio-v1` at the Unity project root;
- `FIRST_PLAYABLE_MANIFEST.csv` remains at project root;
- allow asset import to finish;
- `ProjectOen.Audio` and `ProjectOen.Audio.Editor` compile with zero errors;
- no Missing Script references appear in the generated audio assets/runtime.

Record concrete evidence in `audio_premerge_qa.csv`, for example the Unity log path, captured console export, build/run identifier, or committed QA note.

### 2. `unity_first_playable_audit`

Run:

`Project Oen > Audio > Build First Playable (One Click)`

Then:

`Project Oen > Audio > Audit First Playable (One Click)`

Acceptance:

- manifest/import integrity passes;
- current verified coverage is accepted;
- `AudioCatalog.asset` event count equals the current manifest event count;
- all 11 generated profiles exist;
- generated profile membership audit is clean;
- runtime prefab has the expected service/router/controller composition.

A rerun over an older generated state is valuable here: it should synchronize generated profile membership rather than retaining stale content.

### 3. `unity_active_scene_audit`

In the **saved target gameplay scene**, run:

`Project Oen > Audio > Build + Install First Playable (One Click)`

Then:

`Project Oen > Audio > Audit Active Scene Audio Runtime`

Acceptance:

- audit reports `status=OK`;
- exactly one `AudioService`, owned by the generated first-playable prefab instance;
- exactly one `AudioWorldStateRouter`;
- exactly one active scene `AudioListener`;
- both active listener-relative world anchors target that listener;
- no duplicate/manual audio runtime is overwritten;
- scene is dirty but not silently saved.

### 4. `quest2_functional_smoke`

On Quest 2 / `Q2_BASE`, exercise at minimum:

- Beach Day / Calm;
- Jungle Day / Calm;
- missing Night/Ridge/Camp/Shelter states;
- Calm -> Wind -> RainFire -> Signal;
- exterior -> sheltered -> exterior;
- Jungle Day cicada enable/disable behavior;
- RainFire distant-thunder enable/disable behavior;
- head rotation and player movement around spatial emitters.

Acceptance:

- unavailable biome states resolve to silence rather than stale beds;
- no duplicate emitters/coroutines appear after repeated state changes;
- localization follows the listener correctly;
- no important cue vanishes because of broken routing;
- no audible streaming stalls or hard state-transition bugs.

### 5. `quest2_mix_listening`

Listen to the **current artifact**, not a remembered/older build.

Pay particular attention to:

- `SFX_AMB_Shore_Wash` candidate set;
- `SFX_WTH_Thunder_Far` candidate set;
- ocean/rain/wind/fire/jungle environmental candidates;
- adaptive storm music;
- transitions between biome/weather/music layers;
- candidate loop seams;
- masking under the storm mix;
- clipping, contamination, wrong perspective or implausible spatial scale.

The first-playable PR does not require every future missing runtime event to be recorded before merge, but the material that **is currently shipped by this artifact** must be listenable and technically credible on the target headset.

### 6. `quest2_performance_soak`

Use the project platform budget in `docs/08_PLATFORM_BUILD_PERFORMANCE.md`.

Acceptance:

- Quest 2 retains the project 72 Hz gate through the audio-heavy storm path/soak;
- no sustained audio-induced frame regression;
- no streaming starvation/stalls;
- simultaneous voice behaviour remains within the documented Quest baseline unless measured evidence justifies a deliberate budget change;
- no material audio-related memory growth during the soak.

## Recording evidence

`audio_premerge_qa.csv` allows exactly these statuses:

- `pending-physical`
- `passed`
- `failed`

There is intentionally no generic `waived` state. If a gate is no longer required, change the policy deliberately in code/review rather than bypassing it with a one-word waiver.

`passed` and `failed` both require non-empty evidence. Evidence should be specific enough that a later reviewer can identify what was tested: log path, build/run ID, committed QA report, device capture reference, or similar.

## Full-production work that remains explicit after the first-playable merge boundary

The following work remains visible in the production registries and is **not** re-labelled as finished merely to make this PR mergeable:

- the 11 field-source backlog events: originals still require acquisition, listening and SHA-256 pinning before reviewed derivative production;
- reviewed tarp/Amazon originals and exact segment selection;
- main Foley: 40 events / 388 selected variations;
- supplemental Foley: 13 events / 90 selected variations;
- later headset/mastering approval for every future newly produced source asset.

Those lanes should continue in focused production PRs after the first-playable foundation is accepted. This keeps PR #6 reviewable and mergeable without pretending hundreds of physical recordings have already happened.

## Merge decision

The audio foundation is at its intended merge boundary when all of the following are true:

- automated PR workflows are green on the current head;
- `python tools/report_audio_merge_readiness.py --strict` succeeds;
- the PR has no unresolved review blockers;
- the PR is deliberately moved out of draft state by the maintainer.

Until then, the PR should remain draft. Do not merge merely because the generated WAV/build pipelines are green.
