# Reviewed field-recording ingest

This lane is for high-quality originals that cannot be fetched reproducibly by CI, especially authenticated library downloads such as Freesound originals.

## Non-negotiable rules

- Never use preview/transcode audio as a production master.
- Only use source rows with an explicit redistributable license accepted by the project (`CC0`, `CC0-1.0`, or `Public-Domain`).
- Keep the original outside Git until redistribution has been deliberately approved.
- Compute and pin SHA-256 before changing a source row to `ready`.
- Jobs stay blocked until listening review has selected exact segments and removed contamination.
- Derived production candidates are always 48 kHz / 24-bit PCM WAV.
- Spatial world emitters should normally be mono. Ambience beds may remain stereo when the recording actually contains useful stereo information.
- `candidate-*` is not the same as mastered. Quest headset listening and scene approval remain required.

## Registries

- `content/audio/reviewed_field_recording_sources.csv` records source-page provenance, creator, license, expected original filename, hash and readiness.
- `content/audio/reviewed_field_recording_jobs.csv` maps a reviewed original to exact Project OEN event IDs, variations, trims, channel layout, filtering and landing paths.

The initial registry covers preferred rain-on-tarp and Amazon rainforest sources already selected for the project.

## Audit originals

Place manually downloaded originals in one local directory, then run:

```bash
python tools/build_reviewed_field_recording_pack.py \
  --source-dir /path/to/reviewed-originals \
  --audit-sources
```

The audit reports `missing`, `needs-pin`, `hash-mismatch`, or `verified` for every registered source. When a new original reports `needs-pin`, verify the source page/license and then copy that SHA-256 into the source registry. Do not pin a hash solely because a file happened to download successfully.

Use `--strict-audit` in a controlled local QA step when every registered original is expected to be present.

## Promote a source/job to ready

1. Download the original from its canonical source page while authenticated where required.
2. Listen to the unmodified original.
3. Confirm creator/license/source page.
4. Run the source audit and record SHA-256.
5. Update the source row to `status=ready`.
6. For each derivative, choose exact `start_seconds` / `duration_seconds` after listening and set the job row to `status=ready`.
7. Build derivatives.
8. Listen again in headphones and Quest before promoting beyond candidate status.

## Build reviewed derivatives

```bash
python tools/build_reviewed_field_recording_pack.py \
  --source-dir /path/to/reviewed-originals \
  --clean \
  --output build/oen-reviewed-field-recordings \
  --zip build/oen-reviewed-field-recordings.zip
```

The builder refuses `ready` sources without a valid SHA-256, verifies the original before ffmpeg runs, normalizes derivatives conservatively, verifies 48 kHz/channel layout with ffprobe, and writes `PROVENANCE.csv` containing both source and output hashes.

## Current blocked jobs

The first reviewed batch intentionally remains blocked until originals are available and listened to:

- `SFX_WTH_Rain_OnTarp` variations 01–03
- `SFX_WTH_Thunder_Far` variation 01 extracted from a tarp/thunder recording
- `SFX_AMB_Jungle_NightBed` variation 01
- `SFX_NAT_Bird_JungleCall` variation 01
- `SFX_NAT_Frog_Call` variation 01
- `SFX_NAT_Insect_CicadaCluster` variations 05–08

No preview audio should be substituted to make those rows look complete.
