#!/usr/bin/env python3
"""Mockup-fidelity detail pass for non-hero survival props.

Adds large, readable wear/assembly cues to the carried and camp props that appear
throughout the approved Project ØEN mockups. The goal is not extra micro-detail;
it is tactile VR silhouette, believable lashings, repairs, soot, straps and scavenged
construction while keeping the existing shared material set and canonical paths.
"""
from __future__ import annotations
import json, math
from pathlib import Path

from refine_hero_art import add_box, add_cylinder, add_torus, add_rope_between, write_obj
from refine_prop_art import build as build_prop
from refine_environment_art import add_rock, add_leaf

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PROD=ROOT/"Assets"/"ProductionArt"
MANIFEST=PROD/"Docs"/"production_art_manifest.json"
TARGETS={"PR-002","PR-003","PR-006","PR-007","PR-008","PR-009","PR-010","PR-011","PR-012","PR-013","PR-015","PR-016"}


def rope(mesh,variant):
    add_torus(mesh,(.04,.105,-.02),.19,.010,"Rope",16,4,(90,0,17))
    add_rope_between(mesh,(.18,.10,.05),(.63,.035,-.30),.010,"Rope",6)
    add_box(mesh,(-.18,.075,.13),(.13,.035,.06),"Mud",(0,22,-3))


def poles(mesh,variant):
    for i,x in enumerate((-.36,-.15,.11,.34)):
        add_cylinder(mesh,(x,.18,.03*math.sin(i)),.018,.30,"Wood",6,(16,i*23,54 if i%2 else -48))
    for x in (-.25,.24): add_box(mesh,(x,.16,-.12),(.075,.055,.12),"Char",(0,12,5))


def first_aid(mesh,variant):
    # Buckles, dirty bottom edge, chunky handle wrap and exterior repair tape.
    for x in (-.20,.20):
        add_box(mesh,(x,.20,-.253),(.095,.10,.024),"Metal",(0,0,0))
        add_box(mesh,(x,.20,-.270),(.040,.14,.018),"Rope",(0,0,0))
    for x in (-.13,0,.13): add_torus(mesh,(x,.36,0),.035,.008,"Rope",10,4,(0,0,90))
    add_box(mesh,(.24,.11,-.252),(.16,.034,.020),"Mud",(0,-9,-4))
    if variant=="open": add_box(mesh,(-.12,.38,.03),(.20,.020,.13),"Cloth",(0,18,4))


def canteen(mesh,variant):
    add_torus(mesh,(0,.61,0),.105,.010,"Rope",14,4,(90,0,0))
    add_rope_between(mesh,(.075,.63,0),(.23,.44,.03),.008,"Rope",5)
    add_box(mesh,(-.14,.24,-.222),(.12,.11,.020),"Char",(0,-12,8))
    add_box(mesh,(.10,.39,.183),(.16,.045,.025),"Mud",(0,18,-6))


def lantern(mesh,variant):
    # Top chimney, diagonal cage braces and soot cap.
    add_cylinder(mesh,(0,.68,0),.10,.18,"Metal",12)
    add_cylinder(mesh,(0,.80,0),.07,.08,"Char",10)
    for yaw in (45,135): add_box(mesh,(0,.36,0),(.020,.46,.32),"Metal",(0,yaw,0))
    add_torus(mesh,(0,.56,0),.185,.008,"Metal",16,4,(90,0,0))
    if variant=="lit": add_box(mesh,(0,.23,-.015),(.055,.20,.055),"Fire",(0,12,3))


def torch(mesh,variant):
    for y in (.84,.89,.94,.99): add_torus(mesh,(0,y,0),.090,.008,"Rope",12,4,(90,0,y*7))
    add_box(mesh,(.03,.94,.00),(.13,.22,.11),"Char",(0,13,8))
    add_box(mesh,(0,.38,-.050),(.055,.30,.020),"Rope",(0,0,-4))


def stones(mesh,variant):
    # A little wet organic contamination avoids the showroom rock-pile look.
    count=2 if variant=="small" else 4
    for i in range(count):
        a=i*2.1; add_leaf(mesh,(math.cos(a)*.18,.05,math.sin(a)*.18),.19,.085,40+i*77,-38,"Leaf",.04)
    add_box(mesh,(.08,.035,-.12),(.22,.018,.14),"Mud",(0,16,0))


def leaves(mesh,variant):
    add_torus(mesh,(0,.075,0),.18,.011,"Rope",16,4,(90,0,8))
    add_rope_between(mesh,(-.28,.05,.02),(.29,.04,-.02),.008,"Rope",5)
    add_leaf(mesh,(.06,.08,.05),.62,.19,104,-28,"Leaf",.12)


def scrap(mesh,variant):
    for i,(x,z,ang) in enumerate(((-.30,.18,24),(.12,-.20,-38),(.34,.12,62))):
        add_box(mesh,(x,.12,z),(.30,.028,.10),"Char",(0,ang,8-7*i))
        add_cylinder(mesh,(x+.06,.16,z),.010,.20,"Metal",6,(0,0,42+i*13))
    add_rope_between(mesh,(-.25,.14,-.12),(.38,.12,.18),.009,"Rope",5)


def cloth(mesh,variant):
    add_box(mesh,(.11,.12,-.12),(.26,.018,.16),"Cloth",(0,18,-4))
    add_box(mesh,(-.17,.15,.09),(.21,.018,.11),"Char",(0,-24,5))
    add_rope_between(mesh,(-.25,.08,0),(.26,.075,.02),.007,"Rope",5)


def pot(mesh,variant):
    # Soot band, side grips and battered lid nearby/above.
    add_torus(mesh,(0,.12,0),.274,.010,"Char",18,4,(90,0,0))
    for side in (-1,1):
        x=side*.28; add_box(mesh,(x,.24,0),(.075,.12,.16),"Metal",(0,0,0))
        add_torus(mesh,(side*.34,.24,0),.09,.010,"Metal",12,4,(0,0,90))
    add_cylinder(mesh,(.12,.47,.06),.22,.025,"Metal",14,(0,0,0))
    add_box(mesh,(.12,.50,.06),(.10,.055,.10),"Wood",(0,18,0))


def collector(mesh,variant):
    for p in ((-.48,.78,-.35),(.48,.78,-.35),(-.48,.78,.35),(.48,.78,.35)):
        add_torus(mesh,p,.050,.008,"Rope",12,4,(90,0,0))
        add_rope_between(mesh,p,(p[0]*1.18,.04,p[2]*1.22),.008,"Rope",5)
    for p in ((-.45,.74,-.31),(.45,.74,-.31),(-.45,.74,.31),(.45,.74,.31)):
        add_rope_between(mesh,p,(0,.34,0),.005,"Rope",5)
    if variant in ("collecting","full"):
        add_box(mesh,(.05,.33,-.04),(.16,.012,.09),"Water",(0,17,0))


def enhance(aid,mesh,variant):
    {"PR-002":rope,"PR-003":poles,"PR-006":first_aid,"PR-007":canteen,"PR-008":lantern,
     "PR-009":torch,"PR-010":stones,"PR-011":leaves,"PR-012":scrap,"PR-013":cloth,
     "PR-015":pot,"PR-016":collector}[aid](mesh,variant)


def main():
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8")); count=verts=faces=0; seen=set()
    for e in manifest:
        aid=str(e.get("asset_id","")); variant=str(e.get("variant","default"))
        if aid not in TARGETS or e.get("kind")!="mesh": continue
        mesh=build_prop(aid,variant); enhance(aid,mesh,variant); write_obj(mesh,ROOT/e["path"])
        count+=1;verts+=len(mesh.verts);faces+=len(mesh.faces);seen.add(aid)
    missing=TARGETS-seen
    if missing: raise SystemExit("Mockup prop pass missed: "+", ".join(sorted(missing)))
    print(f"Mockup prop pass: {count} meshes / {len(seen)} families / {verts} vertices / {faces} faces"); return 0

if __name__=="__main__": raise SystemExit(main())
