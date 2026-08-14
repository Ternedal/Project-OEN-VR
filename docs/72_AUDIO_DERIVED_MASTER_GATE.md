# Derived audio master gate — PROJECT ØEN

**Source QA owner:** ChatGPT  
**Creative edit:** human/operator  
**Human listening gate:** real reviewer  
**Runtime/device owner:** Claude  
**Status:** tooling only; no derived master is approved by this document

This lane begins only after an original has passed the explicit human source-approved gate.

A derived master is a **new audio identity** created by a documented edit. If no edit is needed, use the source-approved original directly; do not relabel identical bytes as a derived master.

## 1. Submit derived WAVs

Create `derived_master_submission.json`:

```json
{
  "version": 1,
  "status": "derived-master-submission-unvalidated",
  "masters": [
    {
      "masterId": "DM_EXAMPLE_001",
      "sourceKey": "main::AMB_EXAMPLE",
      "sourceApprovedSha256": "...",
      "filename": "dm_example_001.wav",
      "intendedUse": "clean ambience loop candidate",
      "editRecipe": [
        {
          "operation": "trim-and-fade",
          "details": "Trim selected clean region and apply documented edge fades."
        }
      ]
    }
  ]
}
```

Each master requires at least one explicit edit operation with details.

## 2. Technical intake

```bash
python tools/validate_audio_derived_master_submission.py \
  --submission derived_master_submission.json \
  --source-approved-receipt source_approved_receipt.json \
  --masters-dir path/to/derived \
  --output derived_master_technical_receipt.json
```

The validator checks actual WAV samples and requires:

- source key + source-approved SHA binding;
- derived SHA differs from source SHA;
- integer PCM WAV;
- 48 kHz;
- 24-bit;
- mono or stereo;
- zero full-scale samples;
- non-empty edit recipe.

Pass status is deliberately:

`derived-master-technical-intake-passed-not-listening-approved`

Technical success is not listening approval.

## 3. Repeat human listening on the derived bytes

```bash
python tools/prepare_audio_derived_master_review.py \
  --technical-receipt derived_master_technical_receipt.json \
  --submission derived_master_submission.json \
  --source-approved-receipt source_approved_receipt.json \
  --masters-dir path/to/derived
```

The preparer re-runs technical validation and refuses a stale receipt if source receipt, submission or derived bytes changed.

Open `derived_master_review.html`. Every derived WAV is reviewed again with all eight typed listening checks from the source-approval gate. Source listening approval is **not inherited through an edit**.

Human decisions:

- `approve-derived-master`
- `reject-derived-master`
- `needs-more-listening`

A complete negative result is valid evidence.

## 4. Normalize human evidence

```bash
python tools/normalize_audio_derived_master_review.py \
  --input derived_master_review.json \
  --technical-receipt derived_master_technical_receipt.json \
  --submission derived_master_submission.json \
  --source-approved-receipt source_approved_receipt.json \
  --masters-dir path/to/derived \
  --output derived_master_review.normalized.json \
  --require-complete
```

Eligibility requires reviewer alias + timestamp, explicit approval decision and all repeated typed checks. `MATERIAL_MATCH` must still be at least 3.

Normalized status remains:

`human-derived-master-review-evidence-evaluated-not-materialized`

## 5. Explicit derived-master-approved transition

Only eligible records can be materialized:

```bash
python tools/materialize_derived_master_approved_audio.py \
  --review derived_master_review.normalized.json \
  --technical-receipt derived_master_technical_receipt.json \
  --submission derived_master_submission.json \
  --source-approved-receipt source_approved_receipt.json \
  --masters-dir path/to/derived \
  --output build/derived_master_approved
```

The materializer independently revalidates all current bindings, reviewer identity, typed checks and derived hashes. It copies only eligible derived WAVs byte-for-byte and writes:

`derived-master-approved-materialized-from-human-gate`

Receipt records have:

- `sourceApproved=true`
- `derivedMasterApproved=true`
- `runtimeApproved=false`
- `releaseApproved=false`

## Boundary

This lane does not decide the creative edit, does not fabricate listening evidence, and does not perform Unity import, mixer/spatial work or Quest acceptance. Claude owns final runtime/device QA.
