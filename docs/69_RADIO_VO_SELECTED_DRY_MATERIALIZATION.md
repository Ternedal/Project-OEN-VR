# Radio VO selected dry materialization — PROJECT ØEN

**Owner:** ChatGPT / source QA  
**Input gate:** completed positive human take review  
**Status:** tooling only; no selected files exist in Git

This step converts a **positive, normalized human take review** into nine clearly named dry source files without changing a single audio sample.

It exists so the handoff from `T01/T02/T03` reviewer choices to canonical dry filenames is deterministic and auditable rather than a manual rename/copy operation.

## Prerequisite

The input must be produced by `tools/normalize_radio_vo_human_review.py` and contain:

- `status = human-review-evidence-unapproved`
- `reviewKind = radio-vo-human-take-selection`
- `readyForDryMasterSelection = true`
- bindings that still match the current session, 27-take technical receipt, performer provenance, queue, localization and all source take hashes

A complete **negative** human review is valid evidence but has `readyForDryMasterSelection = false` and is rejected by this materializer.

## Materialize

```bash
python tools/materialize_radio_vo_selected_dry.py \
  --review PrivateContent/RadioVOSession/radio_vo_human_review.normalized.json
```

Default output:

```text
PrivateContent/RadioVOSession/selected_dry/
  VO_RADIO_NIGHT1_01.wav
  VO_RADIO_NIGHT1_02.wav
  VO_RADIO_NIGHT1_03.wav
  VO_RADIO_DAY3_01.wav
  VO_RADIO_DAY3_02.wav
  VO_RADIO_DAY3_03.wav
  VO_RADIO_END_NEUTRAL_01.wav
  VO_RADIO_END_NEUTRAL_02.wav
  VO_RADIO_END_NEUTRAL_03.wav
  radio_vo_selected_dry_receipt.json
```

For each cue the tool verifies the chosen filename and SHA against the current technically accepted three-take set, copies that file byte-for-byte, then verifies that source SHA and output SHA remain identical.

## No hidden processing

This step performs **none** of the following:

- trim
- denoise
- gain change
- EQ
- resample
- compression
- radio/static/dropout treatment

The output is simply the explicitly human-selected dry source under the canonical filename.

The receipt status is:

`selected-dry-source-materialized-from-human-review-not-processed`

and explicitly records that source, derived-master and runtime approval have **not** been promoted.

## Overwrite safety

A non-empty target directory is rejected by default. Replacing an existing materialization requires explicit `--replace`; all validation occurs before the replacement is committed.

This prevents a rerun against a new review from silently overwriting the previous selected-source set.

## Next boundary

If these files need cleanup or other edits, those edits create new file hashes and become a separate derived-master step with documented processing and another listening pass.

Claude owns later radio EQ/static/dropouts, spatialization, ducking, runtime binding, subtitle timing and Quest/headset intelligibility QA.
