# Mockup reference panel recovery

These category panels are repository-side raster inputs for the Project OEN atlas-expansion refinement pass.

During the 2026-08-14 production-art resync, seven JPEG payloads were accidentally committed as invalid 9–18 byte text blobs. The production V2 sprite outputs and review renders were intact. The recovery path in `tools/generated_art/refine_mockup_atlas_expansion_raster_v2.py` now:

- rejects missing, undecodable or undersized category panels;
- reconstructs six category panels deterministically from the committed, reviewed V2 sprite families;
- reconstructs the radio panel from the committed radio-repair art;
- writes valid JPEG files before rebuilding and validating all 40 atlas-expansion sprites;
- keeps `art_payloads/**` inside the full art-workflow trigger.

The recovered panels preserve the reviewed V2 pixels and make CI reproducible again. They are recovery derivatives, not a claim that the accidentally lost original raw JPEG bytes were recovered.
