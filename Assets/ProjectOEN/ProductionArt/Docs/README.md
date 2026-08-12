# Project ØEN Production Art

Generated from the canonical 148-row asset master and refined by the hero/surface pipeline. Every listed state/variant is exported as an individual Unity-importable file.

- Separate production sprites: **206**
- Separate world meshes: **134**
- Full production geometry after hero refinement: **81,858 vertices / 38,602 faces**
- Refined Stormnatten hero meshes: **29** across tarp, crates, radio, shelter, campfire and handmade signal beacon families
- Hero geometry after rope-joinery pass: **47,564 vertices / 22,422 faces**
- Shared surface materials: **11**
- Surface texture maps: **33** — 1024px albedo + 512px normal + 512px metallic/smoothness
- Source: `tools/generated_art/asset_master.csv`

The production pass uses coherent handmade wood/rope/tarp/metal/stone materials, diegetic-first UI, warm camp accents and cool storm accents. Shelter and signal structures receive readable rope joinery; active fire states use lightweight emissive/fire geometry and runtime accents. No Hunger/Thirst HUD assets are generated.

The Unity prefab builder creates URP/Lit materials from the generated maps (with Standard fallback), applies them to imported OBJ renderers, builds category-preserving prefabs with simple Quest-friendly bounds colliders, and adds lightweight fire accents where appropriate.

Surface set: wood, rope, tarp, metal, stone, leaf, cloth, mud, fire, char, water.

CI gates cover master-list completeness, PNG/OBJ structure, surface-map import contracts, hero geometry floors and Unity-side material/prefab wiring. Actual Unity Editor import/build remains an on-machine verification step through `prototype/m0b-bootstrap/Bootstrap-M0b.ps1`.
