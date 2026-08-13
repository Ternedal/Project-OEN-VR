# A1 source-art provenance

**Class:** `OWN`  
**Created for:** PROJECT ØEN  
**Date:** 2026-08-13  
**Release status:** APPROVED AS SOURCE / runtime import pending Claude

## Origin

All SVG files in this folder were created specifically from PROJECT ØEN's own source briefs:

- `docs/38_SOURCE_ASSET_MANIFEST.md`
- `docs/47_VISUAL_STYLE_BIBLE.md`
- `docs/55_SOURCE_PRODUCTION_BATCH_PLAN.md`

No third-party icon pack, logo, illustration or traced source was used in the SVG path data.

## Files

### Identity/action/status

- `UI_PLAYER_SYMBOL_A_001.svg`
- `UI_PLAYER_SYMBOL_B_001.svg`
- `UI_ACTION_ICON_SHELTER_001.svg`
- `UI_ACTION_ICON_FIRE_001.svg`
- `UI_ACTION_ICON_FOOD_001.svg`
- `UI_ACTION_ICON_SIGNAL_001.svg`
- `UI_ACTION_ICON_MEDICAL_001.svg`
- `UI_ACTION_ICON_EXPLORE_001.svg`
- `UI_STATUS_HEALTH_001.svg`
- `UI_STATUS_FATIGUE_001.svg`
- `UI_STATUS_INJURY_001.svg`
- `UI_STATUS_WET_COLD_001.svg`
- `TEX_WARNING_SHAPE_001.svg`
- `TEX_SUCCESS_SHAPE_001.svg`
- `TEX_PARTIAL_SHAPE_001.svg`

### Planning/interaction UI

- `UI_EFFORT_MARKER_P1_001.svg`
- `UI_EFFORT_MARKER_P2_001.svg`
- `UI_ACTION_CARD_BASE_001.svg`
- `UI_WRIST_STATUS_FRAME_001.svg`
- `TEX_SNAP_PREVIEW_001.svg`
- `TEX_GRIP_INVITE_001.svg`
- `TEX_TENSION_GUIDE_001.svg`
- `TEX_REPAIR_NODE_001.svg`

## QA performed

- XML parse check on initial icon sources
- raster render check at source-scale
- combined visual contact-sheet review on dark background
- fatigue symbol revised after first review because its first silhouette read too much like a bag/weight item
- signal symbol revised to restore safe edge margin
- transparent background preserved where intended
- planning/feedback additions follow the same palette/shape language and require a second device/readability QA after Unity-derived raster/import exists

## Accessibility intent

- Player A/B: different outer shapes + different inner glyph + color
- success/warning/partial: circle/check, triangle/exclamation, split circle — not color only
- effort markers: different inner geometry + color
- tension guide: central safe zone + geometry/arrows, not only green/red
- status/action icons use materially different silhouettes

## Claude handoff boundary

Claude owns:

- Unity-compatible import/conversion
- atlas/runtime size
- compression
- material/UI binding
- device readability check

If Unity import requires rasterized PNG, these SVGs remain the source masters and the PNGs are derived assets.
