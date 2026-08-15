# Project ØEN — production-art pipeline

`Assets/ProductionArt/` is the implementation target. `Assets/ProjectOEN/GeneratedArtRuntime256/` is retained only as the compact/fallback tier.

## Current production output

The pipeline covers the canonical **148-row asset master** and currently produces:

- **206** separate production sprites;
- **192** dedicated refined non-VFX sprite states;
- **14** dedicated refined VFX texture states;
- **134** separate refined world-space OBJ meshes;
- **185,716 vertices / 83,074 faces** across the final refined world-mesh set;
- **5** separate 1024×1024 transparent RGBA ground decals — 3 puddle states + 2 shoreline-foam states;
- **11** shared Quest-friendly surface materials;
- **33** surface maps: 11 × (1024px albedo + 512px normal + 512px metallic/smoothness).

Every listed state/variant is an individual Unity-importable asset, not a collage or cropped mockup board.

## Complete 3D refinement coverage

The broad generator owns deterministic master-list coverage and stable paths/GUIDs, but it is no longer the final visual pass for any world mesh. **All 134 world-mesh variants are refined after broad generation:**

- **29 hero meshes** — tarp/presenning, supply/heavy boxes, portable radio, all shelter states, all campfire states and all handmade signal-beacon states;
- **25 environment meshes** — shipwreck, plank piles, beach stones, driftwood, palms, ground fronds, broadleaf bushes, vines and rock/ravine modules;
- **38 survival/tool meshes** — rope, poles, first aid, canteen, lantern, torch, resource bundles, signal cloth, cookpot, water collector, mallet, knife and traversal anchor;
- **42 remaining set-dressing/world meshes** — CS-016 radio-repair station plus barrel/rope debris, cliff/cave dressing, groundsheet, cooking/storage/signal/rain-catcher clusters, torch/path markers, storm debris, camp boundary rope and puddle/foam holder planes.

`refine_hero_joinery.py` adds readable rope lashings to shelter and beacon construction so the handmade wood/rope/tarp language survives VR viewing distance.

### VR-readable interaction geometry

`refine_interaction_readability.py` post-processes **16 interaction-critical states across six prop families** without introducing new materials or paths:

- PR-004 supply crate — larger latch, hinges and end grips;
- PR-005 portable radio — larger controls, frequency scale, carry handle and state-readable indicators;
- PR-017 mallet — grip zone, stop rings and pommel;
- PR-018 knife — guard, pommel, lanyard eye and grip detail;
- PR-019 anchor peg — stop collar, rope loop and active anchoring cue;
- PR-020 shared-carry heavy box — stronger primary and lower two-person grip zones.

The pass adds **8,064 vertices** across those 16 states while retaining the existing shared-material contract and bounded physical dimensions. `validate_interaction_readability.py` compares the generated meshes against their canonical baselines and rejects state collapse, missing detail or runaway bounds.

### Stormnatten camp damage-story geometry

`refine_storm_story_geometry.py` runs after the general set-dressing refinement and upgrades the four canonical EN-023/EN-024 states used by the Stormnatten camp micro-story:

- **EN-023 broken shelter parts** — snapped poles, split/splinter wedges, surviving lash points and torn rope tails;
- **EN-023 loose cloth** — asymmetric torn fringe, surviving corner lashings and failed long rope tails;
- **EN-024 slack boundary rope** — post lashings, failed centre tail, mud-level collapsed coil and slipped bracing;
- **EN-024 taut boundary rope** — post lashings, bracing stakes and a secondary loaded strand that makes tension readable at VR distance.

The resulting face deltas over the canonical set-dressing baselines are **+404 / +344 / +400 / +344 faces** respectively. `validate_storm_story_geometry.py` requires real extra geometry, shared canonical materials only, distinct state meshes and at most **0.60 m per-axis span growth** over the baseline. The QA gate is intentionally stricter than merely checking that the files changed.

### Signal-finale failure/load geometry

`refine_signal_finale_geometry.py` adds a second bounded structural-damage pass to the canonical signal-finale assets, again without introducing new material families, textures or paths:

- **PR-014 storm-damaged signal cloth** — ragged cloth fingers, surviving lashings and failed rope tails: **+300 faces**;
- **CS-015 storm-damaged signal beacon** — failed braces, split timber/splinters, surviving lash points and loaded rope tails: **+464 faces**;
- **EN-019 logs** — slipped/split signal fuel plus surviving bundle lashings: **+272 faces**;
- **EN-019 ropes** — partial coil, failed ground stake and compact used-under-load spill tails: **+184 faces**;
- **EN-019 stones** — displaced anchor/ballast stones tied together by visible rope load cues: **+262 faces**.

`validate_signal_finale_geometry.py` compares all five meshes with their canonical source-generator baselines. It requires exact target coverage, meaningful face/vertex deltas, shared production materials only, state-distinct output, exact generated OBJ agreement and no more than **0.65 m per-axis span growth**. The EN-019 rope refinement was physically pulled inward to satisfy this bound rather than weakening the gate.

## Ground decals

EN-011 and EN-025 use minimal stable holder meshes plus true state-specific RGBA textures.

`Assets/ProductionArt/Decals/environment_set_dressing/` contains:

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

`refine_surface_weathering.py` adds deterministic material-specific wear and wet-environment variation without changing material paths or GUIDs. Runtime storm wetness remains event-driven through `ProductionArtWetnessDriver` and `MaterialPropertyBlock`; Fire and Water are intentionally excluded from global wet tint.

`MaterialCalibrationShowcase.unity` provides isolated dry / mid / storm columns for all 11 shared material families. The repo-side gate verifies the calibration contract; the Unity-side audit remains authoritative for actual imported material behaviour.

## Unity integration and review flow

`ProductionArtPrefabBuilder.cs` creates URP/Lit materials with Standard fallback, wires the generated maps, builds category-preserving world prefabs, applies simple Quest-friendly bounds colliders and adds lightweight fire accents where appropriate.

`ProductionArtStateAppearanceBuilder.cs` attaches explicit bounded appearance profiles to canonical damaged/wet/repaired states. `ProductionArtPrefabStateController.SetState()` preserves these profiles during state changes.

`ProductionArtDecalBuilder.cs` wires the five puddle/shoreline decal prefabs.

`Bootstrap-M0b.ps1` and `Review-ProductionArt.ps1` now exercise the production-art sequence broadly as:

**world prefabs/materials → state appearance/catalogs → decals/VFX/UI specialist reviews → material calibration → state-transition and hero-readability reviews → Stormnatten showcase → camp micro-story → signal-finale micro-story → atmosphere/motion/wind → Quest 2 world-art audit**.

Both handoff scripts explicitly copy **both** `ProductionArtStormCampStoryBuilder.cs` and `ProductionArtSignalFinaleStoryBuilder.cs` into the Unity project. This closes a real handoff gap where the atmosphere builder referenced the camp story type without the fast-review/bootstrap copy list guaranteeing that the source file was present.

Specialist review scenes remain separate from `CoopGame.unity`; the M0b Android build stays the minimal feasibility/performance path.

### Stormnatten visual-review scene

`ProductionArtShowcaseBuilder.cs` builds `StormnattenArtShowcase.unity` from actual generated prefabs. The canonical pressure-state composition uses:

- storm-damaged shelter;
- nearly-out / wet campfire;
- wet tarp;
- wet camp groundsheet;
- storm-damaged signal beacon;
- storm-damaged signal cloth.

`ProductionArtStormCampStoryBuilder.cs` adds a deterministic **nine-prop physical consequence layer** around the camp: two broken-shelter clusters, a loaded guy rope, a failed/slack rope, damaged wood stock, overturned storage, scattered utensils, rope washout and a shelter-foot puddle. The story layer is rebuilt idempotently and adds **no lights, particles, colliders, rigidbodies or Animation/Animator components**. Its own Unity-side authoring gate limits the layer to **60,000 triangles and 36 renderer material slots**.

`ProductionArtSignalFinaleStoryBuilder.cs` adds a separate deterministic **eight-prop failure field** around the storm-damaged beacon: collapsed crossbrace, loaded guy rope, failed guy rope, scattered signal fuel, washed-out signal rope, loose anchor stones, torn signal-cloth debris and a signal-hill puddle. It resolves canonical prefab variants strictly, keeps every prop within **2.45 m** of the finale centre, strips colliders/rigidbodies/particles/lights/Animation/Animator components, and enforces **50,000 triangles / 32 renderer material slots** for the layer.

`ProductionArtStormAtmosphereBuilder.cs` rebuilds the camp story first, then the signal-finale story, then reopens the showcase and adds one bounded local rain volume plus the scene-wide event-driven storm wetness driver. `ProductionArtStormFxBuilder.cs` adds bounded wind debris, camp splashes and the two-billboard near/far lightning rig with one shared non-shadowing flash light. `ProductionArtWindResponseBuilder.cs` adds nine renderer-culled legacy animation clips for cloth, rope and vegetation motion.

`ProductionArtShowcaseAudit.cs` checks the actually imported scene against repository Quest 2 limits: triangles hard fail >750k, renderer material-slot proxy >130, shadow-casting realtime lights >1, active particle systems >10, Animation components >12, exactly one storm wetness driver, canonical damaged/wet states and the bounded storm motion/wind contracts.

The repo-side Python gates validate source/wiring contracts only. Actual Unity scene generation, C# compilation, imported-scene audits, visual overlap/readability and Quest 2 frame timing still require the Unity/Quest machine.

## Review scenes

The production-art review package includes isolated scenes for:

- `ProductionVfxShowcase.unity` — particle/billboard/VFX texture inspection;
- `DiegeticUiArtShowcase.unity` — physical metre-scale diegetic UI inspection;
- `MaterialCalibrationShowcase.unity` — 11 material families at dry/mid/storm wetness;
- `StateTransitionShowcase.unity` — 6 rows × 3 canonical state transitions;
- `HeroReadabilityShowcase.unity` — 12 canonical hand/heavy/world-anchor samples at 1:1 scale;
- `StormnattenArtShowcase.unity` — integrated production-art/storm composition.

These are review scenes, not gameplay build scenes.

## CI gates

`.github/workflows/generate-project-oen-art.yml` gates:

- PowerShell parse validation for both production-art entrypoints;
- canonical 148-ID master completeness;
- 206 production sprites and dedicated 192-state non-VFX refinement;
- all **14 dedicated VFX states** and smoke flipbook structure;
- Quest-conscious Unity VFX builder/showcase constraints;
- sprite alpha/import/state-uniqueness/canonical constraints;
- four diegetic UI prefab contracts and physical-scale UI review wiring;
- PNG/OBJ validity and deterministic Unity metadata;
- 11-material / 33-map surface completeness plus weathering contracts;
- isolated dry/mid/storm material-calibration contract;
- state-specific storm appearance profiles and composition with global wetness;
- state-transition review/controller contract;
- 12-sample hero physical-scale readability contract;
- 16-state VR interaction-readability mesh delta/material/bounds contract;
- hero, environment, survival/tool and remaining set-dressing refinement floors;
- **Stormnatten EN-023/EN-024 camp damage-story geometry deltas, canonical materials, state uniqueness and ≤0.60 m per-axis growth**;
- **five signal-finale mesh deltas/material/state/bounds checks with ≤0.65 m per-axis growth**;
- **eight-prop signal-finale story contract with 2.45 m radius, 50k triangles, 32 material slots and no runtime-cost components**;
- five decal size/alpha/distinctness/import contracts;
- enriched Stormnatten showcase + nine-prop camp micro-story coverage;
- six specialist review-scene/global Unity wiring contract;
- explicit CoopGame leak checks for both storm story layers;
- strict separation from `CoopGame.unity` / the M0b Android build;
- generated documentation derived from actual final files.

Art CI is serialized per branch and rebases its deterministic generated commit on the latest branch head before push, preventing concurrent runs from rejecting otherwise-green output.

## Runtime-verification boundary

Repository CI proves deterministic generation and static contracts. It does **not** run a licensed Unity Editor or a Quest headset. The following remain physical on-machine gates:

- Unity C# import/compile;
- generation/save of the review `.unity` scenes;
- Unity-side material/state/showcase audits;
- HMD-scale readability and visual overlap;
- authoritative draw calls/frame timing on Quest 2.

## Canonical constraints retained

- Health, Fatigue, Injury and Cold/Wet are canonical player states; Hunger/Thirst assets are forbidden.
- Signal structure is a handmade signal beacon/stand, not a lighthouse.
- No firearms or full-combat asset direction.
- Quest 2 remains the runtime/performance baseline.
