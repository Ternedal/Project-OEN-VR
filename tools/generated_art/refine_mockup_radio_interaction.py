#!/usr/bin/env python3
"""Compose mockup-fidelity PR-005 radio geometry with the established VR interaction cues.

The mockup pass intentionally replaces the old boxy radio silhouette. This adapter
re-applies the proven chunky controls/handle wrapping to that new silhouette instead
of lowering the interaction-readability gate or reverting the visual improvement.
"""
from __future__ import annotations

import json
from pathlib import Path

from refine_mockup_fidelity import build, write_obj
from refine_interaction_readability import add_radio_interaction_detail

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PROD=ROOT/"Assets"/"ProjectOEN"/"ProductionArt"
MANIFEST=PROD/"Docs"/"production_art_manifest.json"


def main():
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8")); count=verts=faces=0
    for e in manifest:
        if e.get("kind")!="mesh" or str(e.get("asset_id",""))!="PR-005": continue
        variant=str(e.get("variant","default")); mesh=build("PR-005",variant)
        add_radio_interaction_detail(mesh,variant)
        write_obj(mesh,ROOT/e["path"]); count+=1; verts+=len(mesh.verts); faces+=len(mesh.faces)
    if count!=4: raise SystemExit(f"Expected 4 PR-005 radio states, rebuilt {count}")
    print(f"Composed mockup radio + VR interaction cues: {count} states / {verts} vertices / {faces} faces")
    return 0

if __name__=="__main__": raise SystemExit(main())
