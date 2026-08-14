# Typed human audio source approval gate — PROJECT ØEN

**Source owner:** ChatGPT  
**Human gate:** real listener  
**Runtime/device owner:** Claude  
**Status:** tooling only; no source is approved by this document

The existing V2 main/extension/field reviews are deliberately kept as **preliminary shortlist evidence**. They are not retroactively reinterpreted as the final source-approval gate.

This is important because `content/audio/listening_qa.source.json` requires `MATERIAL_MATCH >= 3`, while the older shortlist formats were designed around candidate-pass or keep/maybe/reject rather than a typed 1–5 approval score.

## 1. Complete preliminary review

Use the existing audition pack and normalizers. Eligible upstream shortlist decisions are:

- main originals: `candidate-pass`
- extension source selection: `keep`
- field backlog selection: `keep`

All other upstream outcomes remain valid evidence but do not enter the source-approval board.

## 2. Prepare typed source approval review

```bash
python tools/prepare_audio_source_approval_review.py \
  --upstream main_review.normalized.json \
  --upstream extension_review.normalized.json \
  --upstream field_review.normalized.json \
  --pack-root path/to/project-oen-audio-source-audition
```

Pass only the upstream review files that actually exist. At least one shortlisted source is required.

Before generating the review board, the tool revalidates each upstream source against current committed acquisition/shortlist provenance and verifies the **actual audition-pack bytes** against the committed SHA-256.

Open:

`source_approval_review.html`

## 3. Typed checks

Every shortlisted source receives all eight explicit checks:

- `CONTAMINATION` — pass/fail
- `MATERIAL_MATCH` — **1–5**
- `LOOP_OR_SLICE` — pass/fail/not-applicable
- `NOISE_FLOOR` — pass/fail
- `TRANSIENT_QUALITY` — pass/fail/not-applicable
- `SPACE_IDENTITY` — pass/fail
- `VARIATION_VALUE` — **1–5**
- `SPEECH_SPACE` — pass/fail/not-applicable

The human source decision is one of:

- `approve-source`
- `reject-source`
- `needs-more-listening`

A complete negative review is valid evidence.

## 4. Normalize approval evidence

```bash
python tools/normalize_audio_source_approval_review.py \
  --input path/to/source_approval_review.json \
  --upstream main_review.normalized.json \
  --upstream extension_review.normalized.json \
  --upstream field_review.normalized.json \
  --pack-root path/to/project-oen-audio-source-audition \
  --output source_approval_review.normalized.json \
  --require-complete
```

Normalized status is:

`human-source-approval-evidence-evaluated-not-materialized`

A source receives `sourceApprovedEligible=true` only when the explicit human decision is `approve-source`, license/source-page provenance is present, all typed checks are complete, contamination/noise/space pass, material match is at least 3, and the allowed pass/N/A rules are satisfied.

An `approve-source` decision with `MATERIAL_MATCH=2` is therefore preserved as human evidence but is **not** source-approval eligible.

## 5. Explicit source-approved state transition

Eligibility is still evidence. The explicit state transition happens only when original bytes are materialized:

```bash
python tools/materialize_source_approved_audio.py \
  --approval source_approval_review.normalized.json \
  --upstream main_review.normalized.json \
  --upstream extension_review.normalized.json \
  --upstream field_review.normalized.json \
  --pack-root path/to/project-oen-audio-source-audition \
  --output build/source_approved
```

The materializer independently recomputes eligibility, verifies current provenance and source bytes, then copies only eligible originals byte-for-byte. Archive-member originals remain in their acquired codec; there is no hidden WAV conversion.

Receipt status:

`source-approved-original-materialized-from-human-gate`

The receipt marks each copied original `sourceApproved=true` while explicitly leaving:

- `derivedMasterApproved=false`
- `runtimeApproved=false`
- `releaseApproved=false`

## 6. No hidden derived work

This gate performs no trim, segmentation, denoise, resample, EQ, gain, loop editing or transcoding.

Derived masters remain a separate step. Any edit creates a new file hash and requires a documented processing recipe plus another listening pass before `derived-master-approved` can be claimed.

Claude continues to own Unity import/mixer/spatial/runtime and Quest listening acceptance.
