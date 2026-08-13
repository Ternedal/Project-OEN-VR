# Source-art provenance index — PROJECT ØEN

**Opdateret:** 2026-08-13

Dette index peger på de autoritative per-pack provenance records. `docs/43_IP_AND_ASSET_PROVENANCE.md` beskriver den overordnede policy.

| Pack | Type | Klasse | Status | Autoritativ record |
|---|---|---|---|---|
| A1 UI/source kit | SVG source masters | `OWN` | Produced + source QA | `source_art/ui/a1/PROVENANCE.md` |
| Neutral fallback | SVG source masters | `OWN` | Produced + source QA | `source_art/neutral/PROVENANCE.md` |
| A2 core props | Source briefs only | `OWN` | Briefs ready; models not produced | `source_art/props/a2/PROVENANCE.md` |
| A3 storm VFX | SVG source masters/reference | `OWN` | Produced; runtime VFX pending | `source_art/vfx/a3/PROVENANCE.md` |

## Rule

A pack is not `release approved` merely because source exists. Final release status also requires:

- correct runtime use
- device/readability/performance QA where relevant
- no private/reference-only contamination
- any derived raster/model/audio asset traceable back to source

## Future packs

Planned:

- A4 camp environment
- B1 jungle/ravine/ridge environment
- B2 event presentation
- P private personalization (must remain outside repo)

Each future pack receives its own `PROVENANCE.md` before handoff.
