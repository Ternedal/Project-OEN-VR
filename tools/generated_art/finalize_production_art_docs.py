#!/usr/bin/env python3
"""Finalize Project ØEN production-art documentation from actual generated outputs."""
from __future__ import annotations

import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PROD=ROOT/"Assets"/"ProjectOEN"/"ProductionArt"
MANIFEST=PROD/"Docs"/"production_art_manifest.json"
UI_REPORT=PROD/"Docs"/"ui_sprite_refinement.json"
VFX_REPORT=PROD/"Docs"/"vfx_refinement.json"
README=PROD/"Docs"/"README.md"


def obj_counts(path:Path):
    verts=faces=0
    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw.startswith("v "): verts+=1
        elif raw.startswith("f "): faces+=1
    return verts,faces


def main()->int:
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    sprites=[e for e in manifest if e.get("kind")=="sprite"]
    meshes=[e for e in manifest if e.get("kind")=="mesh"]
    total_v=total_f=0
    for e in meshes:
        v,f=obj_counts(ROOT/e["path"]); total_v+=v; total_f+=f

    decals=sorted((PROD/"Decals").rglob("*.png")) if (PROD/"Decals").exists() else []
    material_maps=sorted((PROD/"Materials"/"Textures").glob("*.png"))
    ui=json.loads(UI_REPORT.read_text(encoding="utf-8")) if UI_REPORT.exists() else {}
    vfx=json.loads(VFX_REPORT.read_text(encoding="utf-8")) if VFX_REPORT.exists() else {}
    ui_refined=int(ui.get("refined_count",0))
    ui_skipped_vfx=int(ui.get("intentionally_unmodified_vfx_count",0))
    vfx_refined=int(vfx.get("vfx_count",0))

    text=f'''# Project ØEN Production Art

Generated from the canonical **148-row asset master** and finalized after the complete refinement pipeline. Every listed state/variant is an individual Unity-importable file; runtime art is not sourced by cropping mockup boards.

## Current output

- Separate production sprites: **{len(sprites)}**
- Dedicated non-VFX sprite refinement: **{ui_refined}**
- Dedicated VFX texture refinement: **{vfx_refined}**
- Separate world meshes: **{len(meshes)}**
- Final world geometry: **{total_v:,} vertices / {total_f:,} faces**
- State-specific transparent ground decals: **{len(decals)}** (3 puddle + 2 shoreline foam)
- Shared Quest-friendly surface materials: **11**
- Surface texture maps: **{len(material_maps)}** — 1024px albedo + 512px normal + 512px metallic/smoothness
- Source: `tools/generated_art/asset_master.csv`

## 3D refinement coverage

All **134 world-mesh variants** receive a dedicated refinement pass after broad asset-master generation:

- **29 hero meshes** — tarp/presenning, supply/heavy boxes, radio, shelter, campfire and handmade signal beacon;
- **25 environment meshes** — shipwreck, planks, stones, driftwood, palms, fronds, bushes, vines and ravine/rock-wall modules;
- **38 survival/tool meshes** — rope, poles, first aid, canteen, lantern, torch, resource bundles, camp tools and traversal peg;
- **42 remaining set-dressing/world meshes** — radio-repair station, barrel/rope debris, camp/storage/signal/rain-catcher dressing, storm debris, boundary rope plus puddle/foam holder planes.

The 5 puddle/shoreline states also receive their own **1024×1024 RGBA decal textures** wired to transparent, non-shadowing, non-colliding holder prefabs.

## 2D / diegetic UI refinement

The production sprite set contains **{len(sprites)} separate PNG states** across branding, wrist/status, planning, resources, world-space interaction markers, menus/meta and VFX support. `refine_ui_sprite_art.py` refines **{ui_refined} non-VFX states** with category-aware wrist/planning/resource/marker language and deterministic state cues. It deliberately skips the **{ui_skipped_vfx} VFX states**, which are then handled by the dedicated VFX pass below.

`ProductionArtDiegeticUiBuilder` assembles four lightweight `SpriteRenderer` art prefabs with no Canvas/TMP dependency:

- `WristStatus_Diegetic.prefab`;
- `PlanningBoard_Diegetic.prefab`;
- `InteractionMarkers_Diegetic.prefab`;
- `MetaStatus_Diegetic.prefab`.

`ProductionArtUiShowcaseBuilder` creates a separate `DiegeticUiArtShowcase.unity` at physical metre scale. `ProductionArtUiShowcaseAudit` verifies the actually imported review scene on the Unity machine: non-null sprite renderers, no UI shadows, max one collider, zero lights/particles, bounded physical widths and exclusion from Android build settings.

## VFX refinement

`refine_vfx_art.py` replaces the broad treatment of all **{vfx_refined} VFX states** with effect-oriented 1024×1024 RGBA textures:

- 2 smoke states as true **4×4 flipbook atlases**;
- 2 ember particle states;
- ash particle;
- 2 rain-splash states;
- wet-sheen material mask;
- near/far lightning overlays;
- fire/lantern glow halos;
- small/medium objective pulse rings.

`ProductionArtVfxBuilder` creates transparent unlit materials and lightweight prefabs. Smoke uses 4×4 Texture Sheet Animation. VFX prefabs add **no realtime lights, colliders, particle collision or shadows**, and particle counts are bounded per effect. Wet sheen remains a material-helper asset rather than a fake particle prefab.

## Unity integration

`ProductionArtPrefabBuilder` creates URP/Lit materials (Standard fallback), applies albedo/normal/metallic-smoothness maps, builds category-preserving world prefabs and lightweight fire accents.

`ProductionArtDecalBuilder` converts EN-011 / EN-025 holder prefabs to transparent ground decals and removes colliders/shadows.

The art review order is: **world prefabs → decals → production VFX → diegetic UI → physical UI audit → Stormnatten showcase → storm atmosphere → Quest 2 world-art audit**.

The separate `StormnattenArtShowcase.unity` visual-review scene exercises hero, camp, repair, rain-catcher, signal-hill, shipwreck, vegetation, puddle and storm-foam assets. `DiegeticUiArtShowcase.unity` separately reviews UI at physical scale. Neither review scene is the minimal M0b `CoopGame.unity` Android gate.

CI gates cover canonical master completeness, PNG/OBJ structure, 192-state UI refinement, all 14 VFX texture states, VFX Unity builder constraints, state uniqueness/canonical UI constraints, all world refinement-family floors, decal alpha/import contracts, PowerShell syntax, diegetic-UI prefab/showcase contracts and Unity-side world/decal/showcase wiring. Actual Unity Editor import, physical-scale UI audit and imported-scene Quest 2 budget audit remain on-machine verification through `Bootstrap-M0b.ps1` or `Review-ProductionArt.ps1`.

Canonical constraints retained: Health/Fatigue/Injury/Cold-Wet only; no Hunger/Thirst HUD; handmade signal beacon rather than lighthouse; no firearms/full-combat direction; Quest 2 remains baseline.
'''
    README.write_text(text,encoding="utf-8")
    print(f"Finalized production-art README: {len(sprites)} sprites ({ui_refined} UI/non-VFX + {vfx_refined} VFX refined) / {len(meshes)} meshes / {total_v} vertices / {total_f} faces / {len(decals)} decals")
    return 0

if __name__=="__main__": raise SystemExit(main())
