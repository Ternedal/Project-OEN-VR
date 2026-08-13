# Source-art provenance index — PROJECT ØEN

**Opdateret:** 2026-08-13

Dette index peger på de autoritative per-pack provenance records. `docs/43_IP_AND_ASSET_PROVENANCE.md` beskriver den overordnede policy.

| Pack | Type | Klasse | Status | Autoritativ record |
|---|---|---|---|---|
| A1 UI/source kit | SVG source masters | `OWN` | Produced + source QA | `source_art/ui/a1/PROVENANCE.md` |
| Neutral fallback | SVG source masters | `OWN` | Produced + source QA | `source_art/neutral/PROVENANCE.md` |
| A2 core props | briefs + concept/reference + selected individual SVG masters | `OWN` | Reference produced; selected individual masters produced | `source_art/props/a2/PROVENANCE.md` |
| A3 storm VFX | SVG source masters/reference | `OWN` | Produced; runtime VFX pending | `source_art/vfx/a3/PROVENANCE.md` |
| A4 camp environment | layout/state + landmark/prop references | `OWN` | Expanded source reference produced; final world art pending | `source_art/environment/a4/PROVENANCE.md` |
| B1 jungle/ravine/ridge | readability/reference + interaction prop SVG | `OWN` | Produced source reference; runtime world pending | `source_art/environment/b1/PROVENANCE.md` |
| B1 resource items | item/bundle SVG source | `OWN` | Resource source set produced | `source_art/items/b1/PROVENANCE.md` |
| B1 utility props | SVG source master | `OWN` | Supply-container source produced + visually QA'ed | `source_art/props/b1/PROVENANCE.md` |
| B2 event presentation | event/state SVG source | `OWN` | Produced + mapped to all 10 events | `source_art/events/b2/PROVENANCE.md` |
| Base material references | 3 SVG reference boards + source contract | `OWN` | Seven material families covered at source-reference level | `source_art/materials/base/PROVENANCE.md` |
| A5 external prop meshes | OBJ source meshes | `OWN` | Three external source meshes produced | `source_art/props/a5/PROVENANCE.md` |
| A5 source items | SVG source masters | `OWN` | Three source items produced | `source_art/items/a5/PROVENANCE.md` |
| A5 release UI | SVG source masters | `OWN` | Six release UI source surfaces produced | `source_art/ui/a5/PROVENANCE.md` |

## Rule

A pack is not `release approved` merely because source exists. Final release status also requires:

- correct runtime use
- device/readability/performance QA where relevant
- no private/reference-only contamination
- any derived runtime asset traceable back to source

## Remaining source areas

Still intentionally open:

- additional B1/world utility source where it materially reduces Unity guesswork
- remaining individual/core source masters where a brief exists but no committed master exists
- final 3D source only where greybox/runtime proves it useful
- naturalistic Foley/ambience source audio
- radio VO recording/source
- music production/source
- richer environment/polish after geometry/performance evidence
- avatar/hand source beyond the existing player-identity symbols
- private personalization source outside the public repo

`content/source_inventory.source.json` is authoritative for machine-readable production status. A generated-but-uncommitted artifact is never treated as produced.

Each new source-art pack receives or updates its own `PROVENANCE.md` before handoff.
