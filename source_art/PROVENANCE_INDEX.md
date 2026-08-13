# Source-art provenance index — PROJECT ØEN

**Opdateret:** 2026-08-13

Dette index peger på de autoritative per-pack provenance records. `docs/43_IP_AND_ASSET_PROVENANCE.md` beskriver den overordnede policy.

| Pack | Type | Klasse | Status | Autoritativ record |
|---|---|---|---|---|
| A1 UI/source kit | SVG source masters | `OWN` | Produced + source QA | `source_art/ui/a1/PROVENANCE.md` |
| Neutral fallback | SVG source masters | `OWN` | Produced + source QA | `source_art/neutral/PROVENANCE.md` |
| A2 core props | briefs + concept/reference SVG | `OWN` | Source/reference produced; final 3D models pending | `source_art/props/a2/PROVENANCE.md` |
| A3 storm VFX | SVG source masters/reference | `OWN` | Produced; runtime VFX pending | `source_art/vfx/a3/PROVENANCE.md` |
| A4 camp environment | layout/state reference SVG | `OWN` | Produced source reference; final world art pending | `source_art/environment/a4/PROVENANCE.md` |
| B1 jungle/ravine/ridge | readability/reference SVG | `OWN` | Produced source reference; runtime world pending | `source_art/environment/b1/PROVENANCE.md` |
| B2 event presentation | event/state SVG source | `OWN` | Produced + mapped to all 10 events | `source_art/events/b2/PROVENANCE.md` |

## Rule

A pack is not `release approved` merely because source exists. Final release status also requires:

- correct runtime use
- device/readability/performance QA where relevant
- no private/reference-only contamination
- any derived raster/model/audio asset traceable back to source

## Remaining source areas

Still intentionally open:

- final A2 3D/source model production where required
- naturalistic Foley/ambience/weather/fire source audio
- radio VO recording/source
- music production/source
- richer environment/polish only after geometry/performance evidence
- private personalization source outside the public repo

Each new pack receives its own `PROVENANCE.md` before handoff.
