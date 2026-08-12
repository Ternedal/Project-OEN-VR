# Project ØEN — generated production-art pipeline

`Assets/ProjectOEN/ProductionArt/` is now the implementation target. `Assets/ProjectOEN/GeneratedArtRuntime256/` is retained only as the compact/fallback tier.

## Current production output

The pipeline covers the canonical 148-row asset master and currently produces:

- **206** separate production sprites;
- **134** separate world-space OBJ meshes;
- **81,858 vertices / 38,602 faces** across the final production mesh set after hero refinement;
- **29 refined Stormnatten hero meshes** with **47,564 vertices / 22,422 faces** after rope-joinery refinement;
- **11** shared Quest-friendly surface materials;
- **33** surface maps: 11 × (1024px albedo + 512px normal + 512px metallic/smoothness).

Every listed state/variant is an individual asset, not a collage or cropped mockup board.

## Hero refinement

The broad generator guarantees asset-master coverage. `tools/generated_art/refine_hero_art.py` then spends additional geometry on the world-space assets that dominate Stormnatten and the gameplay mockups:

- tarp / presenning;
- supply crate and shared-carry heavy box;
- portable radio;
- all five shelter construction/damage states;
- all five campfire states;
- all five handmade signal-beacon states.

`tools/generated_art/refine_hero_joinery.py` adds readable rope lashings to shelter and beacon construction so the handmade wood/rope/tarp visual language survives Quest-scale viewing.

## Surface pipeline

`tools/generated_art/refine_material_textures.py` generates the shared material set:

`wood`, `rope`, `tarp`, `metal`, `stone`, `leaf`, `cloth`, `mud`, `fire`, `char`, `water`.

Albedo maps are 1024px. Normal and metallic/smoothness maps are 512px. Unity `.meta` files are deterministic and normal maps are imported as normal textures.

## Unity integration

`src/unity/ProjectOen.Art/Editor/ProductionArtPrefabBuilder.cs`:

1. creates or updates URP/Lit materials with Standard fallback;
2. wires the generated albedo, normal and metallic/smoothness maps;
3. makes tarp, cloth, leaf and fire double-sided for VR readability;
4. enables emissive fire treatment;
5. replaces imported OBJ/MTL materials with the production Unity materials;
6. creates category-preserving prefabs;
7. adds simple Quest-friendly bounds colliders;
8. adds lightweight non-shadowing fire accents to active fire/signal/torch states.

`prototype/m0b-bootstrap/Bootstrap-M0b.ps1` mirrors ProductionArt into the generated `ProjektOenApp` Unity project, installs the prefab builder and invokes it in a Unity batch session.

## CI gates

`.github/workflows/generate-project-oen-art.yml` regenerates and checks the complete pack. Current gates cover:

- canonical 148-ID master completeness;
- PNG/OBJ validity and Unity metadata;
- **11-material / 33-map** surface completeness and importer contracts;
- hero geometry/detail floors and state-family coverage;
- Unity material/prefab/bootstrap wiring contract.

The current repo-side pipeline passes every generation and validation gate. Actual Unity Editor import/build remains an on-machine verification step because this CI workflow does not run a licensed Unity Editor.

## Canonical constraints retained

- Health, Fatigue, Injury and Cold/Wet are canonical player states; Hunger/Thirst assets are forbidden.
- Signal structure is a handmade signal beacon/stand, not a lighthouse.
- No firearms or full-combat asset direction.
- Quest 2 remains the runtime/performance baseline.
