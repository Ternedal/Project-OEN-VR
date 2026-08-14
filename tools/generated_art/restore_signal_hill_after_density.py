#!/usr/bin/env python3
"""Restore canonical EN-019 signal-hill finale geometry after world-density dressing.

World-density deliberately enriches generic set dressing, but EN-019 is governed by
a stricter finale/load-story contract. Rebuild only its three canonical variants from
the authoritative signal-finale refiner so dense scene dressing cannot overwrite the
used-rope / slipped-log / ballast story. CS-015 and PR-014 are intentionally untouched.
"""
from __future__ import annotations

import json
from pathlib import Path

from refine_signal_finale_geometry import refine, normalize_variant
from refine_hero_art import write_obj
from refine_set_dressing_art import ROOT, MANIFEST

TARGET_VARIANTS = {"logs", "ropes", "stones"}


def main() -> int:
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    seen=set(); total_vertices=total_faces=0
    for entry in manifest:
        if entry.get("kind")!="mesh" or str(entry.get("asset_id",""))!="EN-019":
            continue
        variant=str(entry.get("variant","default")); normalized=normalize_variant(variant)
        if normalized not in TARGET_VARIANTS:
            continue
        mesh=refine("EN-019",variant)
        write_obj(mesh,ROOT/entry["path"])
        seen.add(normalized); total_vertices+=len(mesh.verts); total_faces+=len(mesh.faces)
    if seen!=TARGET_VARIANTS:
        raise SystemExit(f"EN-019 signal-hill restore coverage mismatch: {sorted(seen)}")
    print(f"Restored authoritative EN-019 signal-hill finale geometry: {len(seen)} variants / {total_vertices} vertices / {total_faces} faces")
    return 0


if __name__=="__main__": raise SystemExit(main())
