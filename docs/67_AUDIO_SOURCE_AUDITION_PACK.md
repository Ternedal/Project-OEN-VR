# Audio source audition pack

This is the reproducible human-listening handoff for acquired non-Unity audio sources.

## Why this exists

The project intentionally stores licenses, hashes, source-selection rules and review contracts in Git, while acquired audio bytes remain outside Git history in GitHub Actions artifacts. Previously a reviewer had to manually combine multiple artifacts before listening. `tools/build_audio_source_audition_pack.py` turns the committed receipts plus artifact ZIPs into one local review pack without transcoding or inventing approval.

## Build

Download the acquisition artifact ZIPs named by the committed receipts/evidence runs, then run:

```bash
python tools/build_audio_source_audition_pack.py \
  --artifact path/to/base.zip \
  --artifact path/to/extension.zip \
  --artifact path/to/field-run-1.zip \
  --artifact path/to/field-run-2.zip \
  --artifact path/to/field-run-3.zip \
  --artifact path/to/field-run-4.zip \
  --out-dir build/audio-source-audition \
  --zip-output build/project-oen-audio-source-audition.zip
```

The builder derives the expected source set from:

- `content/audio/acquisition_receipt.source.json`
- `content/audio/acquisition_extension_receipt.source.json`
- `content/audio/acquisition_extension_member_shortlist.source.json`
- `content/audio/acquisition_field_backlog_receipt.source.json`
- `content/audio/listening_review_targets.source.json`
- `content/audio/listening_qa.source.json`

It fails if an expected source/member is missing or if its SHA-256 differs from the committed receipt/shortlist.

## Artifact wrapper vs source identity

GitHub may produce a new artifact ZIP wrapper when the acquisition workflow is rerun even when the original source bytes are identical. The default policy therefore records wrapper identity but makes **source-byte SHA-256** the decisive inclusion gate.

For forensic reproduction of a historical acquisition run, add:

```bash
--require-pinned-artifact-wrapper
```

That mode rejects any artifact ZIP whose wrapper SHA-256 is not listed in the committed receipts/evidence runs.

## Human review boundary

Open `review.html` from the generated directory. It exports:

- `audio_main_review.json`
- `audio_extension_review.json`
- `audio_field_review.json`

Those exports are deliberately compatible with the existing V2 normalizers. A successful normalization remains `human-review-evidence-unapproved`; it is **not** `source-approved`, `derived-master-approved`, Unity-integrated or release-approved.

The builder never edits/transcodes acquired audio and never pre-fills human decisions.
