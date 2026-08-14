# Provenance — B1 environment references and production pack

**Pack:** B1 jungle/ravine/ridge references + OBJ/MTL/PNG production sources
**Owner:** ChatGPT  
**Class:** `OWN`  
**Date:** 2026-08-13

## Reference files

- `B1_JUNGLE_READABILITY_001.svg`
- `B1_RAVINE_READABILITY_001.svg`
- `B1_RIDGE_READABILITY_001.svg`
- `PRP_RAVINE_ANCHOR_001.svg`
- `PRP_RAVINE_GUIDE_MARKERS_001.svg`

## Origin

All reference and production files in this pack are project-original and authored specifically for PROJECT ØEN.

They do not contain:

- third-party maps
- traced game screenshots
- real-world logos
- stock illustration fragments
- copyrighted photographs

## Intended use

The SVGs are source/readability references. Concrete metre-scaled UV-mapped geometry and project-owned texture sources are committed under `production/` for `ENV_JUNGLE_PATH_001`, `ENV_RAVINE_001`, `ENV_RIDGE_001`, `PRP_RAVINE_ANCHOR_001` and `PRP_RAVINE_GUIDE_MARKERS_001`.

The ravine prop masters define the product-visible anchor/guide language referenced by `design/interactions/RAVINE_RESCUE.md`; Unity navigation, colliders and runtime implementation remain separate.

Derived assets may be created from them, but release provenance must preserve the link back to this record.

## Product constraints carried by the source

- jungle must not become a maze
- ravine must preserve two active roles and fail-forward recovery
- ravine route information uses shape + position/order, not color alone
- ridge must provide foresight without forcing dangerous VR edge behavior
- return/navigation landmarks remain readable

## Release status

`OWN` provenance does not mean release-approved. Runtime/device/readability/performance acceptance remains required where applicable.
