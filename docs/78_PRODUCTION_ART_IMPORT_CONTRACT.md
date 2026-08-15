# Production-art import contract

Status: approved non-Unity integration contract, 2026-08-15.

## Roots and ownership

- Production payload: `Assets/ProductionArt`.
- Runtime/editor source: `src/unity/ProjectOen.Art`.
- Unity installation target for source: `Assets/ProjectOen/Unity/ProjectOen.Art`.
- `ProductionArtWetnessDriver` owns wetness for production-art props through shared-material `MaterialPropertyBlock` values.
- `OenWeather` / `Oen/Surface` owns terrain only: beach, sea, jungle and ridge.
- Neither system may write the other system's material family.

The spelling and casing above are canonical. No legacy uppercase project-root variant is supported.

## Portable scale

Production meshes use meters and import at Unity transform scale `1.0`.

Portable objects use physically plausible real-world dimensions. Readability may enlarge a target by at most `1.35x`; presentation-scale enlargement is forbidden. One-hand precision objects remain near true scale, ordinary one-hand props receive only a modest visibility allowance, and two-hand tools retain realistic reach.

Every runtime OBJ has an explicit target and tolerance in `content/items/runtime_mesh_scale_specs.json`. `tools/qa_spec_vs_mesh.py` is the CI gate. The normalization pass runs after geometry refinement so all variants retain stable dimensions.

## Model normals

OBJ sources intentionally omit `vn` records. `ProductionArtModelImporter` is authoritative and calculates area/angle-weighted normals at a `60 degree` smoothing angle plus MikkTSpace tangents on every platform. Unity defaults must not be relied on.

## Material budget

The Q2 baseline is at most three unique material slots per mesh. A mesh above the limit must have an exact path, material list and substantive reason in `content/materials/production_art_material_budget_exceptions.json`. Missing, stale or mismatched exceptions fail `tools/qa_meshes.py`.

Exceptions preserve current multi-surface state/silhouette fidelity; they are not blanket release approval. The Unity batching proxy, the MPB-aware SRP proxy and physical Quest profiling remain required evidence.

## Surface maps and wetness

Production world surfaces use `1024x1024` albedo maps and `512x512` tangent-space normal plus metallic/smoothness maps. This is the intended Q2 production resolution. The design-token `2048` value is a maximum, not a mandatory hero size.

`GeneratedArtRuntime256` is a separate compact sprite/fallback lane; its `256px` cap is intentional and does not define production world-surface resolution.

The shared MTL links both `map_Kd` and `map_Bump`. Unity's prefab builder also loads the normal maps explicitly, so `ProductionArtWetnessDriver._BumpScale` has a real texture input and is not a no-op.

## Protected Unity lane

This contract does not change render settings, lighting, skybox, fog, lightning, Unity packages or `src/unity/App/CoopGame.cs`. Physical Quest, cross-device, listening, Foley, VO and human-test gates remain open until their real evidence exists.
