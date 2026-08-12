# Project ØEN — production-art pipeline

`Assets/ProjectOEN/ProductionArt/` is the implementation target. `Assets/ProjectOEN/GeneratedArtRuntime256/` is retained only as the compact/fallback tier.

## Current production output

The pipeline covers the canonical **148-row asset master** and currently produces:

- **206** separate production sprites;
- **134** separate world-space OBJ meshes;
- **172,802 vertices / 76,868 faces** across the final refined world-mesh set;
- **5** separate 1024×1024 transparent RGBA ground decals — 3 puddle states + 2 shoreline-foam states;
- **11** shared Quest-friendly surface materials;
- **33** surface maps: 11 × (1024px albedo + 512px normal + 512px metallic/smoothness).

Every listed state/variant is an individual asset, not a collage or cropped mockup board.

## Complete 3D refinement coverage

The broad generator still owns deterministic master-list coverage and stable paths/GUIDs, but it is no longer the final visual pass for any world mesh. **All 134 world-mesh variants are refined after broad generation:**

- **29 hero meshes** — tarp/presenning, supply/heavy boxes, portable radio, all shelter states, all campfire states and all handmade signal-beacon states;
- **25 environment meshes** — shipwreck, plank piles, beach stones, driftwood, palms, ground fronds, broadleaf bushes, vines and rock/ravine modules;
- **38 survival/tool meshes** — rope, poles, first aid, canteen, lantern, torch, resource bundles, signal cloth, cookpot, water collector, mallet, knife and traversal anchor;
- **42 remaining set-dressing/world meshes** — CS-016 radio-repair station plus barrel/rope debris, cliff/cave dressing, groundsheet, cooking/storage/signal/rain-catcher clusters, torch/path markers, storm debris, camp boundary rope and the puddle/foam holder planes.

`refine_hero_joinery.py` adds readable rope lashings to shelter and beacon construction so the handmade wood/rope/tarp language survives VR viewing distance.

## Ground decals

EN-011 and EN-025 are intentionally represented by minimal stable holder meshes plus true state-specific RGBA textures rather than pretending a generic Mud/Water material is enough.

`Assets/ProjectOEN/ProductionArt/Decals/environment_set_dressing/` contains:

- puddle: small / medium / large;
- shoreline foam: calm / storm.

`ProductionArtDecalBuilder.cs` creates transparent unlit materials, applies the matching texture to each holder prefab, disables receive/cast shadows and removes colliders. This keeps the effect cheap and avoids invisible collision slabs.

## Surface pipeline

`refine_material_textures.py` generates the shared material set:

`wood`, `rope`, `tarp`, `metal`, `stone`, `leaf`, `cloth`, `mud`, `fire`, `char`, `water`.

Albedo maps are 1024px. Normal and metallic/smoothness maps are 512px. Unity `.meta` files are deterministic and normal maps are imported as normal textures.

## Unity integration

`ProductionArtPrefabBuilder.cs`:

1. creates URP/Lit materials with Standard fallback;
2. wires albedo, normal and metallic/smoothness maps;
3. makes tarp, cloth, leaf and fire double-sided for VR readability;
4. enables emissive fire treatment;
5. replaces imported OBJ/MTL materials with production Unity materials;
6. creates category-preserving prefabs;
7. adds simple Quest-friendly bounds colliders;
8. adds lightweight non-shadowing fire accents to active fire/signal/torch states.

`ProductionArtDecalBuilder.cs` then wires the five puddle/shoreline decal prefabs before showcase creation.

### Stormnatten visual-review scene

`ProductionArtShowcaseBuilder.cs` builds a separate `StormnattenArtShowcase.unity` scene from the actual generated prefabs. It deliberately does **not** alter M0b's `CoopGame.unity` Android build.

The enriched showcase now exercises:

- usable shelter and small campfire;
- portable radio, supply crate and shared-carry box;
- CS-016 radio-repair station;
- worn groundsheet, cooking/storage dressing and all three rain-catcher components;
- complete/unlit handmade signal beacon plus signal-hill logs/ropes/stones;
- shipwreck, planks, broken barrel, rope debris, beach stones and driftwood;
- palms, fronds, bushes, vines and cliff-edge grass;
- large/medium puddle decals and storm shoreline foam;
- cool fog/ambient light with exactly one shadow-casting directional key and one non-shadowing fill.

`ProductionArtStormAtmosphereBuilder.cs` adds one local Quest-friendly rain volume: max 180 particles, stretched unlit alpha-blended rain streaks, no collision and no particle shadows.

### Unity-side Quest 2 art audit

`ProductionArtShowcaseAudit.cs` opens the **actually imported** showcase scene and measures conservative scene-level proxies:

- triangles: target ≤500k, hard fail >750k;
- renderer material slots as draw-call proxy: target ≤100, hard fail >130;
- shadow-casting realtime lights: hard fail >1;
- active particle systems: hard fail >10.

This does not replace headset profiling. Real Quest 2 frame timing/draw calls remain authoritative.

`Bootstrap-M0b.ps1` installs production art, builds prefabs, wires decals, generates the showcase, adds storm rain and runs the imported-scene budget audit. `Review-ProductionArt.ps1` provides the faster repeatable art-only path after initial bootstrap.

The important boundary remains explicit: **the visual-review scene is not the M0b 72 Hz/network feasibility scene**. `CoopGame.unity` remains minimal and is still the only scene built into the M0b APK.

## CI gates

`.github/workflows/generate-project-oen-art.yml` currently gates:

- PowerShell parse validation for both production-art entrypoints;
- canonical 148-ID master completeness;
- PNG/OBJ validity and deterministic Unity metadata;
- **11-material / 33-map** surface completeness/import contracts;
- hero geometry/state-family floors;
- environment refinement coverage/floors;
- survival/tool refinement coverage/floors;
- remaining set-dressing + CS-016 coverage/floors;
- five decal size/alpha/distinctness/import contracts;
- enriched Stormnatten showcase content;
- Unity material/prefab/decal/bootstrap wiring;
- storm atmosphere bounded to one no-collision/no-shadow rain system;
- presence/configuration of the Unity-side Quest 2 budget audit;
- strict separation from `CoopGame.unity` / the M0b Android build;
- generated documentation derived from the actual final files.

The latest full repo-side workflow passes all generation and static validation gates. Actual Unity Editor import, prefab/material compilation and imported-scene budget audit still require the machine with the licensed Unity Editor; this repository does not claim those have passed in CI.

## Next refinement frontier

The world-art pass is complete at repo level: **134/134 world-mesh variants have dedicated refinement coverage**. The next production frontier is the **206 separate 2D/UI/VFX sprites**: branding, wrist/status UI, planning board, resource/inventory support, interaction markers, menus/meta screens and VFX support. Those assets already exist as individual Unity-importable PNGs and have specialized broad-pass motifs, but they are the next layer to receive a dedicated readability/detail refinement pass.

## Canonical constraints retained

- Health, Fatigue, Injury and Cold/Wet are canonical player states; Hunger/Thirst assets are forbidden.
- Signal structure is a handmade signal beacon/stand, not a lighthouse.
- No firearms or full-combat asset direction.
- Quest 2 remains the runtime/performance baseline.
