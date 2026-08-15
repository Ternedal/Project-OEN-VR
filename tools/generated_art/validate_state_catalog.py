#!/usr/bin/env python3
"""Repo-side QA for Project ØEN runtime production-art state catalogs."""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PROD=ROOT/"Assets"/"ProductionArt"
MANIFEST=PROD/"Docs"/"production_art_manifest.json"
RUNTIME=ROOT/"src"/"unity"/"ProjectOen.Art"/"Runtime"
EDITOR=ROOT/"src"/"unity"/"ProjectOen.Art"/"Editor"/"ProductionArtStateCatalogBuilder.cs"
BOOT=ROOT/"prototype"/"m0b-bootstrap"/"Bootstrap-M0b.ps1"
REVIEW=ROOT/"prototype"/"m0b-bootstrap"/"Review-ProductionArt.ps1"

RUNTIME_FILES=(
    "ProductionArtSpriteStateSet.cs",
    "ProductionArtSpriteStateController.cs",
    "ProductionArtPrefabStateSet.cs",
    "ProductionArtPrefabStateController.cs",
)
FORBIDDEN_RUNTIME=("UnityEditor","Photon","Fusion","UnityEngine.XR","NetworkBehaviour","Hunger","Thirst","Malik","Lighthouse")


def main()->int:
    errors=[]
    if not MANIFEST.exists():
        print("ERROR: production manifest missing")
        return 1
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    by_id={}
    for e in manifest:
        aid=str(e.get("asset_id",""))
        by_id.setdefault(aid,set()).add(str(e.get("kind","")))
    sprite_ids={aid for aid,kinds in by_id.items() if "sprite" in kinds}
    mesh_ids={aid for aid,kinds in by_id.items() if "mesh" in kinds}
    if len(by_id)!=148: errors.append(f"Expected 148 canonical asset IDs in production manifest, found {len(by_id)}")
    if len(sprite_ids)!=87: errors.append(f"Expected 87 sprite asset IDs, found {len(sprite_ids)}")
    if len(mesh_ids)!=61: errors.append(f"Expected 61 world/mesh asset IDs, found {len(mesh_ids)}")
    overlap=sprite_ids & mesh_ids
    if overlap: errors.append(f"Asset IDs unexpectedly span both sprite and mesh kinds: {sorted(overlap)}")

    runtime_text={}
    for name in RUNTIME_FILES:
        path=RUNTIME/name
        if not path.exists():
            errors.append(f"Missing runtime state file: {path.relative_to(ROOT)}")
            continue
        text=path.read_text(encoding="utf-8")
        runtime_text[name]=text
        for token in FORBIDDEN_RUNTIME:
            if token in text: errors.append(f"Runtime state file {name} must not depend on/contain: {token}")

    sprite_set=runtime_text.get("ProductionArtSpriteStateSet.cs","")
    for token in ("TryGetSprite","ContainsState","IReadOnlyList<Entry>","Configure(string id"):
        if token not in sprite_set: errors.append(f"Sprite state set missing contract token: {token}")
    sprite_controller=runtime_text.get("ProductionArtSpriteStateController.cs","")
    for token in ("SetState(string stateKey)","targetRenderer.sprite = sprite","HasState(string stateKey)","StateSet => stateSet"):
        if token not in sprite_controller: errors.append(f"Sprite state controller missing contract token: {token}")

    prefab_set=runtime_text.get("ProductionArtPrefabStateSet.cs","")
    for token in ("TryGetPrefab","ContainsState","IReadOnlyList<Entry>","Configure(string id"):
        if token not in prefab_set: errors.append(f"Prefab state set missing contract token: {token}")
    prefab_controller=runtime_text.get("ProductionArtPrefabStateController.cs","")
    for token in ("SetState(string stateKey)","Instantiate(prefab, mount, false)","Destroy(currentInstance)","HasState(string stateKey)"):
        if token not in prefab_controller: errors.append(f"Prefab state controller missing contract token: {token}")

    if not EDITOR.exists():
        errors.append(f"Missing state catalog builder: {EDITOR.relative_to(ROOT)}")
        builder=""
    else:
        builder=EDITOR.read_text(encoding="utf-8")
        required=(
            'ManifestPath = "Assets/ProductionArt/Docs/production_art_manifest.json"',
            'SpriteRoot = "Assets/ProductionArt/StateSets/Sprites"',
            'WorldRoot = "Assets/ProductionArt/StateSets/World"',
            'CompositeRoot = "Assets/ProductionArt/StateSets/Composite"',
            '.Where(e => e.kind == "sprite")','.Where(e => e.kind == "mesh")','.GroupBy(e => e.asset_id)',
            'AssetDatabase.LoadAssetAtPath<Sprite>(entry.path)',
            'MeshToPrefabPath(entry.path)','prefabPath.Length - 4',
            '"WORLD-SHELTER"','Pair("foundation", "CS-001")','Pair("repaired_reinforced", "CS-005")',
            '"WORLD-CAMPFIRE"','Pair("laid_unlit", "CS-006")','Pair("nearly_out_wet", "CS-010")',
            '"WORLD-SIGNAL-BEACON"','Pair("base", "CS-011")','Pair("storm_damaged", "CS-015")',
            'JsonUtility.FromJson<ManifestWrapper>',
        )
        for token in required:
            if token not in builder: errors.append(f"State catalog builder missing token: {token}")
        for forbidden in ("Photon","Fusion","NetworkBehaviour","Hunger","Thirst","Malik","Lighthouse"):
            if forbidden in builder: errors.append(f"State catalog builder must not depend on/contain: {forbidden}")
        if builder.count("BuildComposite(entries,")!=3: errors.append("State catalog builder must define exactly three semantic construction composites")
        if builder.count('Pair("')<15: errors.append("Composite construction catalog must map all 15 CS-001..CS-015 states")

    for path,label,log_name in (
        (BOOT,"bootstrap","production-art-state-catalog.log"),
        (REVIEW,"review","review-art-state-catalog.log"),
    ):
        if not path.exists(): errors.append(f"Missing {label} script"); continue
        text=path.read_text(encoding="utf-8")
        for token in (
            'src\\unity\\ProjectOen.Art\\Runtime\\*.cs',
            'ProductionArtStateCatalogBuilder.cs',
            'ProjectOen.Art.Editor.ProductionArtStateCatalogBuilder.BuildAll',
            log_name,
            'Assets\\ProductionArt\\StateSets',
        ):
            if token not in text: errors.append(f"{label} state-catalog integration missing token: {token}")
        world=text.find("ProductionArtPrefabBuilder.BuildAll")
        state=text.find("ProductionArtStateCatalogBuilder.BuildAll")
        decal=text.find("ProductionArtDecalBuilder.BuildAll")
        if min(world,state,decal)<0 or not (world < state < decal):
            errors.append(f"{label} must build world prefabs -> state catalogs -> decals")

    print("Project ØEN runtime art state-catalog QA")
    print(f"  canonical IDs     : {len(by_id)}")
    print(f"  sprite state sets : {len(sprite_ids)}")
    print(f"  world state sets  : {len(mesh_ids)}")
    print("  composite sets    : 3 x 5 states (shelter / campfire / signal beacon)")
    print("  runtime deps      : UnityEngine only; no Editor/Photon/Fusion/XR coupling")
    if errors:
        print(f"\nFAILED with {len(errors)} issue(s):")
        for e in errors: print(" - "+e)
        return 1
    print("\nPASS: runtime art state-catalog source/integration contract is complete for all 148 canonical asset IDs.")
    return 0

if __name__=="__main__": sys.exit(main())
