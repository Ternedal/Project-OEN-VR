# Non-Unity production completion — graphics and authored audio

**Owner:** ChatGPT
**Date:** 2026-08-14
**Scope:** source artwork, authored source audio, provenance, inventory and objective QA outside Unity

## Result

The repository no longer represents the release-critical visual source lane as briefs alone. Concrete production sources now cover the Camp, B1 environment/items, A5 utility/release items and props, base avatar, C1 epilogue overlay, storm VFX and AU-1 interaction feedback.

The extended completion batch closes fifteen previously reference-only or technically incomplete mesh handoffs:

- A2 grabbables: firesteel, tinder and rope coil;
- A5 items: cloth, map fragment, radio battery, repair mallet and ember carrier;
- B1 utility knife;
- A5 props: dry-fuel cache, firepit, signal fuel, waterproof ending crate and wind shield;
- C1 reuse-first epilogue overlay.

Every mesh in that batch has:

- metre-scale geometry;
- explicit UV coordinates;
- a matching MTL file;
- resolved project-owned PNG material references;
- named semantic parts for later Unity setup;
- deterministic regeneration and a CI validation contract.

## Objective acceptance

`tools/validate_extended_source_meshes.py` rejects missing OBJ/MTL files, reference-only inventory claims, unindexed faces, missing UVs, unresolved materials/textures, unexpected bounds and missing semantic parts.

`tools/generate_extended_source_meshes.py` is run in CI and the checkout must remain byte-clean afterwards. This proves that committed outputs match the deterministic authoring source.

The existing individual validators remain authoritative for the utility knife, repair mallet and ember carrier product contracts.

## Audio boundary

Twelve AU-1 interaction/UI production masters are committed and deterministically validated. Natural Foley, ambience, radio VO and music selection are not silently replaced by synthetic placeholders:

- 17 Foley cues require 73 real physical performances plus human review;
- 9 radio cues require 27 authorized voice takes plus human pronunciation/delivery review;
- acquired ambience and music candidates require human listening/source selection;
- Unity mix, spatialization and Quest audibility remain runtime/device work.

These are evidence gates, not missing automation. No generated file may claim to satisfy them.

## Runtime boundary

Production-source-ready does not mean Unity-integrated or release-approved. Prefabs, colliders, shaders, rigging, particles, runtime state binding, navigation, performance and Quest 2/3/3S visual acceptance remain Unity/device responsibilities.
