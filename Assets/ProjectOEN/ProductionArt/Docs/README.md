# Project ØEN Production Art

Generated from the canonical **148-row asset master** and finalized after the complete refinement pipeline. Every listed state/variant is an individual Unity-importable file; runtime art is not sourced by cropping mockup boards.

## Current output

- Separate production sprites: **206**
- Separate world meshes: **134**
- Final world geometry: **172,802 vertices / 76,868 faces**
- State-specific transparent ground decals: **5** (3 puddle + 2 shoreline foam)
- Shared Quest-friendly surface materials: **11**
- Surface texture maps: **33** — 1024px albedo + 512px normal + 512px metallic/smoothness
- Source: `tools/generated_art/asset_master.csv`

## Refinement coverage

All **134 world-mesh variants** receive a refinement pass after broad asset-master generation:

- **29 hero meshes** — tarp/presenning, supply/heavy boxes, radio, shelter, campfire and handmade signal beacon;
- **25 environment meshes** — shipwreck, planks, stones, driftwood, palms, fronds, bushes, vines and ravine/rock-wall modules;
- **38 survival/tool meshes** — rope, poles, first aid, canteen, lantern, torch, resource bundles, camp tools and traversal peg;
- **42 remaining set-dressing/world meshes** — radio-repair station, barrel/rope debris, camp/storage/signal/rain-catcher dressing, storm debris, boundary rope plus the puddle/foam holder planes.

The 5 puddle/shoreline states also receive their own **1024×1024 RGBA decal textures**. Unity wires those textures to transparent, non-shadowing, non-colliding holder prefabs.

## Unity integration

`ProductionArtPrefabBuilder` creates URP/Lit materials (Standard fallback), applies albedo/normal/metallic-smoothness maps, builds category-preserving prefabs with simple Quest-friendly bounds colliders, and adds lightweight fire accents where appropriate.

`ProductionArtDecalBuilder` converts EN-011 / EN-025 holder prefabs to transparent ground decals and removes their colliders/shadows.

The separate `StormnattenArtShowcase.unity` visual-review scene exercises hero, camp, repair, rain-catcher, signal-hill, shipwreck, vegetation, puddle and storm-foam assets. It remains outside the minimal M0b `CoopGame.unity` Android build.

CI gates cover canonical master completeness, PNG/OBJ structure, all refinement-family floors, decal alpha/import contracts, PowerShell syntax and Unity-side prefab/decal/showcase wiring. Actual Unity Editor import and the imported-scene Quest 2 budget audit remain on-machine verification through `prototype/m0b-bootstrap/Bootstrap-M0b.ps1` or `Review-ProductionArt.ps1`.

Canonical constraints retained: Health/Fatigue/Injury/Cold-Wet only; no Hunger/Thirst HUD; handmade signal beacon rather than lighthouse; no firearms/full-combat direction; Quest 2 remains baseline.
