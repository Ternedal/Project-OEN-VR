#!/usr/bin/env python3
"""Seventh fidelity pass: correct the over-massed V6 campfire flame silhouette.

V6's closed flame volumes passed all repository QA but visually merged into one large
orange sail in the actual OBJ review. This pass keeps the improved low stone ring/log
bed and replaces only the flame mass with separated, narrow organic tongues. No QA
thresholds are changed.
"""
from __future__ import annotations

import json
import math
import random
from pathlib import Path

from refine_mockup_fidelity import Mesh, add_irregular_rock, add_stick, write_obj
from refine_mockup_fidelity_v6 import add_teardrop_flame

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PROD=ROOT/"Assets"/"ProductionArt"
MANIFEST=PROD/"Docs"/"production_art_manifest.json"


def build_fire()->Mesh:
    m=Mesh(); rnd=random.Random(3107)
    for i in range(14):
        a=2*math.pi*i/14+rnd.uniform(-.055,.055); r=.305+rnd.uniform(-.018,.014)
        add_irregular_rock(
            m,(math.cos(a)*r,.035,math.sin(a)*r),
            (.070+rnd.uniform(-.009,.009),.040+rnd.uniform(-.006,.007),.065+rnd.uniform(-.009,.009)),
            3120+i,"Stone",4,9,
        )
    for a,b,s in [
        ((-.26,.100,-.15),(.26,.140,.15),3150),
        ((-.26,.135,.15),(.26,.100,-.15),3151),
        ((-.22,.165,-.025),(.22,.177,.035),3152),
        ((-.17,.088,.065),(.18,.115,-.075),3153),
    ]:
        add_stick(m,a,b,.039,"Char",s,10,4)
    for i in range(13):
        a=2*math.pi*i/13; rr=.050+.088*((i%4)/3)
        add_irregular_rock(m,(math.cos(a)*rr,.064+(i%2)*.006,math.sin(a)*rr),(.030,.012,.026),3170+i,"Fire" if i%3 else "Char",3,7)

    # Separated flame fingers: small footprints with visible dark gaps between them.
    flames=[
        ((-.045,.142,-.025),.37,.060,3201,12,7),
        (( .040,.144,.018),.32,.055,3202,12,7),
        (( .095,.146,-.045),.25,.043,3203,10,6),
        ((-.105,.145,.045),.23,.040,3204,10,6),
        (( .005,.150,.085),.20,.036,3205,10,6),
        ((-.015,.150,-.090),.18,.033,3206,10,6),
        (( .120,.147,.055),.15,.029,3207,9,5),
    ]
    for center,height,radius,seed,segments,rings in flames:
        add_teardrop_flame(m,center,height,radius,seed,segments,rings)
    return m


def main()->int:
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8")); count=0
    for e in manifest:
        if e.get("kind")!="mesh" or str(e.get("asset_id",""))!="CS-009": continue
        mesh=build_fire(); write_obj(mesh,ROOT/e["path"]); count+=1
    if count!=1: raise SystemExit(f"Expected one CS-009 strong-fire mesh, wrote {count}")
    print(f"Mockup fidelity v7: CS-009 separated organic flame tongues / {len(mesh.verts)} vertices / {len(mesh.faces)} faces")
    return 0

if __name__=="__main__": raise SystemExit(main())
