#!/usr/bin/env python3
"""Second hero pass: add readable rope joinery to shelter and signal structures.

This is deliberately separate from the broad hero-shape pass: joinery is a visual
language in ØEN (salvaged wood + rope + tarp), and can be tuned independently.
"""
from __future__ import annotations

import json
from pathlib import Path

import refine_hero_art as hero

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROD = ROOT / "Assets" / "ProjectOEN" / "ProductionArt"
MANIFEST = PROD / "Docs" / "production_art_manifest.json"
TARGETS = {*(f"CS-{i:03d}" for i in range(1, 6)), *(f"CS-{i:03d}" for i in range(11, 16))}


def shelter_with_joinery(stage: int) -> hero.Mesh:
    m = hero.shelter_stage(stage)
    # Lash the four A-frame/ridge joints. These loops remain visible at Quest scale.
    for p in [(-.38,1.45,-.70),(.38,1.45,-.70),(-.38,1.45,.70),(.38,1.45,.70)]:
        hero.add_torus(m,p,.075,.014,"Rope",12,4,(90,0,0))
    if stage >= 2:
        for p in [(-.64,.28,-.70),(.64,.28,-.70),(-.64,.28,.70),(.64,.28,.70)]:
            hero.add_torus(m,p,.060,.012,"Rope",10,4,(90,0,0))
    return m


def beacon_with_joinery(stage: int) -> hero.Mesh:
    m = hero.beacon_stage(stage)
    # The base must already read as handmade construction in state 1.
    for p in [(-.50,.34,-.32),(.50,.34,-.32),(-.50,.34,.32),(.50,.34,.32)]:
        hero.add_torus(m,p,.075,.013,"Rope",12,4,(90,0,0))
    if stage >= 3:
        for p in [(-.43,1.48,-.30),(.43,1.48,-.30),(-.43,1.48,.30),(.43,1.48,.30)]:
            hero.add_torus(m,p,.065,.012,"Rope",10,4,(90,0,0))
    return m


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    changed = 0
    for entry in manifest:
        aid = str(entry.get("asset_id", ""))
        if aid not in TARGETS or entry.get("kind") != "mesh":
            continue
        n = int(aid.split("-")[1])
        mesh = shelter_with_joinery(n) if n <= 5 else beacon_with_joinery(n - 10)
        hero.write_obj(mesh, ROOT / entry["path"])
        changed += 1
    print(f"Added readable rope joinery to {changed} hero construction meshes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
