# Source-art provenance index — PROJECT ØEN

**Opdateret:** 2026-08-14

Dette index peger på de autoritative per-pack provenance records. `docs/43_IP_AND_ASSET_PROVENANCE.md` beskriver den overordnede policy.

| Pack | Type | Klasse | Status | Autoritativ record |
|---|---|---|---|---|
| A1 UI/source kit | SVG source masters | `OWN` | Produced + source QA | `source_art/ui/a1/PROVENANCE.md` |
| Neutral fallback | SVG source masters | `OWN` | Produced + source QA | `source_art/neutral/PROVENANCE.md` |
| A2 core props | briefs + SVG + UV-mapped OBJ/MTL/PNG production pack | `OWN` | 17 production mesh sources; Unity/device work pending | `source_art/props/a2/PROVENANCE.md` |
| A3 storm VFX | SVG + deterministic PNG sprite masters | `OWN` | Seven production sprites; runtime VFX pending | `source_art/vfx/a3/PROVENANCE.md` |
| A4 camp environment | layout/state + UV-mapped OBJ/MTL/PNG production pack | `OWN` | Three environment production meshes; Unity assembly pending | `source_art/environment/a4/PROVENANCE.md` |
| B1 jungle/ravine/ridge | references + UV-mapped OBJ/MTL/PNG production pack | `OWN` | Five environment/interaction production meshes; runtime pending | `source_art/environment/b1/PROVENANCE.md` |
| B1 resource items | SVG + UV-mapped OBJ/MTL production sources | `OWN` | Six grabbable production meshes | `source_art/items/b1/PROVENANCE.md` |
| B1 utility props | SVG source master | `OWN` | Supply-container source produced + visually QA'ed | `source_art/props/b1/PROVENANCE.md` |
| B2 event presentation | event/state SVG source | `OWN` | Produced + mapped to all 10 events | `source_art/events/b2/PROVENANCE.md` |
| Base material references | 3 SVG reference boards + source contract | `OWN` | Seven material families covered at source-reference level | `source_art/materials/base/PROVENANCE.md` |
| A5 external prop meshes | UV-mapped OBJ/MTL/PNG-reference sources | `OWN` | Five production prop meshes | `source_art/props/a5/PROVENANCE.md` |
| A5 source items | SVG + UV-mapped OBJ/MTL production sources | `OWN` | Five production item meshes | `source_art/items/a5/PROVENANCE.md` |
| A5 release UI | SVG source masters | `OWN` | Six release UI source surfaces produced | `source_art/ui/a5/PROVENANCE.md` |
| Base avatar | SVG + UV-mapped OBJ/MTL production sources | `OWN` | Torso plus P1/P2 glove pairs produced | `source_art/avatar/base/AVATAR_PRODUCTION_README.md` |
| C1 epilogue | SVG + UV-mapped OBJ/MTL reuse-first overlay | `OWN` | Production environment overlay produced | `source_art/environment/c1/ENV_EPILOGUE_001.PROVENANCE.md` |

## Rule

A pack is not `release approved` merely because source exists. Final release status also requires:

- correct runtime use
- device/readability/performance QA where relevant
- no private/reference-only contamination
- any derived runtime asset traceable back to source

## Remaining source areas

Still intentionally open:

- Unity-specific prefab, collider, rig, shader, particle, LOD and runtime binding work
- richer environment/polish only after device geometry/performance evidence proves it useful
- naturalistic Foley/ambience source audio
- radio VO recording/source
- music production/source
- private personalization source outside the public repo

`content/source_inventory.source.json` is authoritative for machine-readable production status. A generated-but-uncommitted artifact is never treated as produced.

Each new source-art pack receives or updates its own `PROVENANCE.md` before handoff.
