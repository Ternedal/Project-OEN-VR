# Project ØEN Production Art

Generated from the canonical **148-row asset master** and finalized after the complete refinement pipeline. Every listed state/variant is an individual Unity-importable file; runtime art is not sourced by cropping mockup boards.

## Current output

- Separate production sprites: **206**
- Dedicated non-VFX sprite refinement: **192**
- Dedicated VFX texture refinement: **14**
- Separate world meshes: **134**
- Final world geometry: **380,013 vertices / 185,786 faces**
- State-specific transparent ground decals: **5** (3 puddle + 2 shoreline foam)
- Shared Quest-friendly surface materials: **11**
- Surface texture maps: **33** — 1024px albedo + 512px normal + 512px metallic/smoothness
- Source: `tools/generated_art/asset_master.csv`

## 3D refinement coverage

All **134 world-mesh variants** receive a dedicated refinement pass after broad asset-master generation:

- **29 hero meshes** — tarp/presenning, supply/heavy boxes, radio, shelter, campfire and handmade signal beacon;
- **25 environment meshes** — shipwreck, planks, stones, driftwood, palms, fronds, bushes, vines and ravine/rock-wall modules;
- **38 survival/tool meshes** — rope, poles, first aid, canteen, lantern, torch, resource bundles, camp tools and traversal peg;
- **42 remaining set-dressing/world meshes** — radio-repair station, barrel/rope debris, camp/storage/signal/rain-catcher dressing, storm debris, boundary rope plus puddle/foam holder planes.

The 5 puddle/shoreline states also receive their own **1024×1024 RGBA decal textures** wired to transparent, non-shadowing, non-colliding holder prefabs.

## 2D / diegetic UI refinement

The production sprite set contains **206 separate PNG states** across branding, wrist/status, planning, resources, world-space interaction markers, menus/meta and VFX support. `refine_ui_sprite_art.py` refines **192 non-VFX states** with category-aware wrist/planning/resource/marker language and deterministic state cues. It deliberately skips the **14 VFX states**, which are then handled by the dedicated VFX pass below.

`ProductionArtDiegeticUiBuilder` assembles four lightweight `SpriteRenderer` art prefabs with no Canvas/TMP dependency:

- `WristStatus_Diegetic.prefab`;
- `PlanningBoard_Diegetic.prefab`;
- `InteractionMarkers_Diegetic.prefab`;
- `MetaStatus_Diegetic.prefab`.

`ProductionArtUiShowcaseBuilder` creates a separate `DiegeticUiArtShowcase.unity` at physical metre scale. `ProductionArtUiShowcaseAudit` verifies the actually imported review scene on the Unity machine: non-null sprite renderers, no UI shadows, max one collider, zero lights/particles, bounded physical widths and exclusion from Android build settings.

## VFX refinement

`refine_vfx_art.py` replaces the broad treatment of all **14 VFX states** with effect-oriented 1024×1024 RGBA textures:

- 2 smoke states as true **4×4 flipbook atlases**;
- 2 ember particle states;
- ash particle;
- 2 rain-splash states;
- wet-sheen material mask;
- near/far lightning overlays;
- fire/lantern glow halos;
- small/medium objective pulse rings.

`ProductionArtVfxBuilder` creates transparent unlit materials and lightweight prefabs. Smoke uses 4×4 Texture Sheet Animation. VFX prefabs add **no realtime lights, colliders, particle collision or shadows**, and particle counts are bounded per effect. Wet sheen remains a material-helper asset rather than a fake particle prefab.

`ProductionArtVfxShowcaseBuilder` creates a separate `ProductionVfxShowcase.unity` so VFX review cost never leaks into Stormnatten or M0b. The scene contains **7 particle systems**, **6 billboard effects** and a wet-sheen material review. `ProductionArtVfxShowcaseAudit` verifies the actually imported Unity scene: max 28 particles per system, smoke 4×4 flipbooks, zero lights/colliders/shadows and exclusion from Android build settings.

## Unity integration

`ProductionArtPrefabBuilder` creates URP/Lit materials (Standard fallback), applies albedo/normal/metallic-smoothness maps, builds category-preserving world prefabs and lightweight fire accents.

`ProductionArtDecalBuilder` converts EN-011 / EN-025 holder prefabs to transparent ground decals and removes colliders/shadows.

The art review order is: **world prefabs → decals → production VFX → isolated VFX showcase/audit → diegetic UI → physical UI audit → Stormnatten showcase → storm atmosphere → Quest 2 world-art audit**.

The three generated review scenes are:

- `ProductionVfxShowcase.unity` — isolated VFX structure/budget review;
- `DiegeticUiArtShowcase.unity` — physical-scale UI review;
- `StormnattenArtShowcase.unity` — world/camp/environment review.

All remain outside the minimal M0b `CoopGame.unity` Android gate. `ProductionArtReviewMenu` exposes direct Unity menu entries for all three scenes.

CI gates cover canonical master completeness, PNG/OBJ structure, 192-state UI refinement, all 14 VFX texture states, Unity VFX builder/showcase constraints, state uniqueness/canonical UI constraints, all world refinement-family floors, decal alpha/import contracts, PowerShell syntax, diegetic-UI prefab/showcase contracts and Unity-side world/decal/showcase wiring. Actual Unity Editor import, isolated VFX audit, physical-scale UI audit and imported-scene Quest 2 world-art audit remain on-machine verification through `Bootstrap-M0b.ps1` or `Review-ProductionArt.ps1`.

Canonical constraints retained: Health/Fatigue/Injury/Cold-Wet only; no Hunger/Thirst HUD; handmade signal beacon rather than lighthouse; no firearms/full-combat direction; Quest 2 remains baseline.
