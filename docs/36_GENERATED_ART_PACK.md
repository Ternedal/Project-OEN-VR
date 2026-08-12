# Project ØEN — production-art pipeline

`Assets/ProjectOEN/ProductionArt/` is the implementation target. `Assets/ProjectOEN/GeneratedArtRuntime256/` is retained only as the compact/fallback tier.

## Current production output

The pipeline covers the canonical **148-row asset master** and currently produces:

- **206** separate production sprites;
- **192** dedicated refined non-VFX sprite states;
- **14** dedicated refined VFX texture states;
- **134** separate refined world-space OBJ meshes;
- **172,802 vertices / 76,868 faces** across the final refined world-mesh set;
- **5** separate 1024×1024 transparent RGBA ground decals — 3 puddle states + 2 shoreline-foam states;
- **11** shared Quest-friendly surface materials;
- **33** surface maps: 11 × (1024px albedo + 512px normal + 512px metallic/smoothness).

Every listed state/variant is an individual asset, not a collage or cropped mockup board.

## Complete 3D refinement coverage

The broad generator owns deterministic master-list coverage and stable paths/GUIDs, but it is no longer the final visual pass for any world mesh. **All 134 world-mesh variants are refined after broad generation:**

- **29 hero meshes** — tarp/presenning, supply/heavy boxes, portable radio, all shelter states, all campfire states and all handmade signal-beacon states;
- **25 environment meshes** — shipwreck, plank piles, beach stones, driftwood, palms, ground fronds, broadleaf bushes, vines and rock/ravine modules;
- **38 survival/tool meshes** — rope, poles, first aid, canteen, lantern, torch, resource bundles, signal cloth, cookpot, water collector, mallet, knife and traversal anchor;
- **42 remaining set-dressing/world meshes** — CS-016 radio-repair station plus barrel/rope debris, cliff/cave dressing, groundsheet, cooking/storage/signal/rain-catcher clusters, torch/path markers, storm debris, camp boundary rope and puddle/foam holder planes.

`refine_hero_joinery.py` adds readable rope lashings to shelter and beacon construction so the handmade wood/rope/tarp language survives VR viewing distance.

## Ground decals

EN-011 and EN-025 use minimal stable holder meshes plus true state-specific RGBA textures.

`Assets/ProjectOEN/ProductionArt/Decals/environment_set_dressing/` contains:

- puddle: small / medium / large;
- shoreline foam: calm / storm.

`ProductionArtDecalBuilder.cs` creates transparent unlit materials, applies the matching texture to each holder prefab, disables receive/cast shadows and removes colliders.

## 2D / UI refinement

The 206 production sprites remain separate Unity-importable PNGs across:

- branding & identity: **23**;
- wrist UI & player status: **40**;
- planning board & phase UI: **36**;
- resource/inventory support: **44**;
- interaction markers & helper UI: **30**;
- menus & meta screens: **19**;
- VFX support graphics: **14**.

`refine_ui_sprite_art.py` gives **192 non-VFX states** a dedicated category-aware pass: cool teal/metal wrist language, warm wood/brass planning language, rugged resource tokens, high-contrast world-space markers and restrained menu/branding framing. State variants get deterministic semantic pips/notches so distinct files cannot silently collapse to the same image. The VFX category is deliberately skipped by this UI pass and handled separately below.

`validate_ui_sprite_art.py` gates alpha/transparency, Unity sprite import metadata, dimensions, non-VFX state uniqueness, canonical UI constraints and exact category coverage. Hunger/Thirst, Malik, lighthouse and firearm direction are rejected from the UI production set.

## Dedicated VFX refinement

`refine_vfx_art.py` replaces the broad icon-like treatment of all **14 VFX states** with effect-oriented **1024×1024 RGBA textures**:

- `FX-001`: small / medium smoke as true **4×4 flipbook atlases**;
- `FX-002`: small / medium ember particle textures;
- `FX-003`: ash particle texture;
- `FX-004`: small / medium rain-splash textures;
- `FX-005`: wet-sheen material-helper mask;
- `FX-006`: near / far lightning overlays;
- `FX-007`: fire / lantern glow halos;
- `FX-008`: small / medium objective pulse rings.

`validate_vfx_art.py` verifies all 14 canonical states, 1024×1024 dimensions, alpha range/gutter, visible content, distinct state hashes and all 16 occupied cells in each smoke flipbook.

`ProductionArtVfxBuilder.cs` creates transparent unlit materials and lightweight effect prefabs. Smoke uses Unity Texture Sheet Animation with a 4×4 grid. The VFX layer deliberately adds **zero realtime lights, zero colliders, zero particle collision and zero shadows**. Particle counts are bounded per effect. Wet sheen stays a material-helper asset rather than being faked into a particle prefab.

## Diegetic VR UI prefabs

`ProductionArtDiegeticUiBuilder.cs` assembles four lightweight visual prefabs from the production sprites using `SpriteRenderer` — deliberately no Canvas/TMP dependency in this art layer:

1. `WristStatus_Diegetic.prefab` — Health, Fatigue, Cold/Wet, Injury plus Shelter/Fire/Signal status;
2. `PlanningBoard_Diegetic.prefab` — time slots, Gather/Build/Scout/Repair tokens, camp summary and objective;
3. `InteractionMarkers_Diegetic.prefab` — grab, two-hand carry, snap, objective, fire/shelter and planning markers;
4. `MetaStatus_Diegetic.prefab` — pause/reconnect visual support.

UI SpriteRenderers do not cast/receive realtime shadows. The art layer adds only one bounds collider on the planning board.

### Physical-scale UI review

`ProductionArtUiShowcaseBuilder.cs` creates a separate `DiegeticUiArtShowcase.unity` scene with the four UI prefabs at physical metre scale plus a visual 1m reference.

`ProductionArtUiShowcaseAudit.cs` opens the **actually imported** scene on the Unity machine and checks:

- 22–32 non-null production SpriteRenderers;
- no UI cast/receive shadows;
- max one collider;
- zero realtime lights and particle systems;
- physical-width bands for wrist, planning board, markers and meta status;
- scene excluded from Android build settings.

This is a structural/scale art gate, not a substitute for headset legibility/usability testing.

## Surface pipeline

`refine_material_textures.py` generates `wood`, `rope`, `tarp`, `metal`, `stone`, `leaf`, `cloth`, `mud`, `fire`, `char`, `water`.

Albedo maps are 1024px. Normal and metallic/smoothness maps are 512px. Unity `.meta` files are deterministic and normal maps are imported as normal textures.

## Unity integration

`ProductionArtPrefabBuilder.cs` creates URP/Lit materials with Standard fallback, wires the generated maps, builds category-preserving world prefabs, applies simple Quest-friendly bounds colliders and adds lightweight fire accents where appropriate.

`ProductionArtDecalBuilder.cs` wires the five puddle/shoreline decal prefabs.

`Bootstrap-M0b.ps1` and `Review-ProductionArt.ps1` now run the art sequence as:

**world prefabs → decals → production VFX → diegetic UI prefabs → physical UI showcase → physical UI audit → Stormnatten showcase → storm atmosphere → Quest 2 world-art audit**.

### Stormnatten visual-review scene

`ProductionArtShowcaseBuilder.cs` builds a separate `StormnattenArtShowcase.unity` scene from the actual generated prefabs. It deliberately does **not** alter M0b's `CoopGame.unity` Android build.

The enriched showcase exercises usable shelter, campfire, radio/crates, radio-repair station, camp dressing, signal hill, wreckage, vegetation, puddles and storm shoreline foam. `ProductionArtStormAtmosphereBuilder.cs` adds one local Quest-friendly rain volume: max 180 particles, stretched unlit alpha-blended streaks, no collision and no particle shadows.

`ProductionArtShowcaseAudit.cs` checks imported-scene proxies against repository Quest 2 limits: triangles hard fail >750k, renderer material-slot proxy hard fail >130, shadow-casting realtime lights >1 and active particle systems >10.

Neither `StormnattenArtShowcase.unity` nor `DiegeticUiArtShowcase.unity` is the M0b 72 Hz/network feasibility scene. `CoopGame.unity` remains the minimal Android gate.

## CI gates

`.github/workflows/generate-project-oen-art.yml` gates:

- PowerShell parse validation for both production-art entrypoints;
- canonical 148-ID master completeness;
- 206 production sprites and dedicated 192-state non-VFX refinement;
- all **14 dedicated VFX states** and smoke flipbook structure;
- Quest-conscious Unity VFX builder constraints;
- sprite alpha/import/state-uniqueness/canonical constraints;
- four diegetic UI prefab contracts;
- physical-scale UI showcase/audit wiring;
- PNG/OBJ validity and deterministic Unity metadata;
- 11-material / 33-map surface completeness/import contracts;
- hero, environment, survival/tool and remaining set-dressing refinement floors;
- five decal size/alpha/distinctness/import contracts;
- enriched Stormnatten showcase content;
- Unity material/prefab/decal/bootstrap wiring;
- storm atmosphere limits and Unity-side Quest 2 audit presence;
- strict separation from `CoopGame.unity` / the M0b Android build;
- generated documentation derived from actual final files.

Art CI is serialized per branch and rebases its deterministic generated commit on the latest branch head before push, preventing concurrent runs from rejecting otherwise-green output.

Actual Unity Editor import, VFX material/prefab build, physical-scale UI audit, world-art budget audit and headset profiling still require the machine with Unity/Quest; CI does not claim those runtime gates have passed.

## Canonical constraints retained

- Health, Fatigue, Injury and Cold/Wet are canonical player states; Hunger/Thirst assets are forbidden.
- Signal structure is a handmade signal beacon/stand, not a lighthouse.
- No firearms or full-combat asset direction.
- Quest 2 remains the runtime/performance baseline.
