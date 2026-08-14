# Radio VO human take review — PROJECT ØEN

**Owner:** ChatGPT / source QA  
**Human gate:** real reviewer listening to real recorded takes  
**Status:** tooling only; no take selected or approved by this document

This lane starts **after** `tools/validate_radio_vo_session.py` has produced a clean 27/27 `radio_vo_intake_receipt.json` with status `technical-intake-passed-not-listening-approved`.

It turns the remaining human work into hash-bound evidence without deciding the result for the reviewer.

## Prepare the review

```bash
python tools/prepare_radio_vo_human_review.py
```

The tool verifies before opening a review lane:

- technical receipt is a clean 27/27 pass;
- every current take file still matches the SHA-256 in that receipt;
- receipt cue/take/filename identities still match the canonical 9 × 3 queue;
- `recording_session.json` is V2+ and contains the canonical spoken text used for recording;
- current `content/localization/da.source.json` still matches that recorded spoken text exactly;
- performer provenance, queue, localization, recording-session and intake-receipt identities are all hash-bound.

If any of those conditions drift, preparation fails rather than letting an old take be reviewed against new text or stale metadata.

A successful preparation writes inside the private session root:

- `radio_vo_human_review.template.json`
- `radio_vo_human_review.html`

The HTML board plays T01/T02/T03 for each cue and shows canonical text, delivery direction and critical semantic.

## Human decisions

For each of the nine cues, the reviewer chooses exactly one of:

- `select`
- `needs-rerecord`
- `needs-more-listening`

If `select` is chosen, one of that cue's three technically accepted filenames must be selected.

Every cue also records all four human checks:

- `PRONUNCIATION`
- `DELIVERY`
- `SEMANTIC_PARITY`
- `NO_CRITICAL_ADLIB`

Each check may be `pass`, `fail` or `needs-more-listening` with an observation note.

The reviewer also records a stable reviewer alias and one rights/provenance decision:

- `accepted`
- `rejected`
- `needs-review`

A **negative** complete result is valid evidence. For example, one cue can be `needs-rerecord` with `DELIVERY=fail`. Tooling must preserve that result rather than coercing it into a selection.

## Normalize evidence

After exporting `radio_vo_human_review.json` from the browser board:

```bash
python tools/normalize_radio_vo_human_review.py \
  --input PrivateContent/RadioVOSession/radio_vo_human_review.json \
  --output PrivateContent/RadioVOSession/radio_vo_human_review.normalized.json \
  --require-complete
```

The normalizer re-verifies the entire current session and exact bindings before accepting the export.

Normalized status is deliberately:

`human-review-evidence-unapproved`

The result contains `readyForDryMasterSelection: true` **only** when:

- reviewer alias is non-empty;
- rights/provenance is `accepted`;
- all nine cue decisions are `select`;
- every selected filename belongs to the correct three-take set;
- every selected SHA matches the technical intake receipt;
- all 36 human checks are `pass`.

`readyForDryMasterSelection` is a source-selection handoff condition. It is not derived-master approval, radio-treatment approval, Unity integration, Quest intelligibility evidence or release approval.

## Next boundary

If the result is positive, exact selected dry source bytes can be materialized in a separate deterministic step. Any edit/cleanup creates a new hash and requires another listening pass.

If any cue needs rerecording, record replacement takes, re-run technical intake, and prepare a **new** human review against the new receipt. Do not carry an old selection across changed take hashes.

Claude remains owner of radio EQ/static/dropouts, spatialization, ducking, runtime binding, subtitle timing and physical Quest listening QA.
