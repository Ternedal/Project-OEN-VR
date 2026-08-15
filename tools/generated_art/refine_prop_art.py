#!/usr/bin/env python3
"""Refine the remaining Project ØEN survival/tool prop families.

Hero props (tarp/crate/radio/heavy box) are handled by refine_hero_art.py. This pass
upgrades the rest of the visible carried/camp props so the production pack no longer
falls back to generic broad-pass geometry around the hero assets.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

from refine_hero_art import (
    Mesh, add_box, add_cylinder, add_torus, add_tarp, add_rope_between,
    add_flame_cross, write_obj,
)
from refine_environment_art import add_rock, add_leaf

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PROD=ROOT/"Assets"/"ProductionArt"
MANIFEST=PROD/"Docs"/"production_art_manifest.json"

PROP_IDS={f"PR-{i:03d}" for i in range(2,20)}-{"PR-004","PR-005"}


def rope_coil(variant:str)->Mesh:
    m=Mesh(); scale=.86 if variant=="carried" else 1.0
    for i in range(5):
        add_torus(m,(0,.06+i*.028,0),.27*scale+i*.006,.018,"Rope",20,6,(90,0,i*7))
    tail_a=(.26*scale,.11,.02); tail_b=(.48*scale,.06,.22 if variant!="placed" else .36)
    add_rope_between(m,tail_a,tail_b,.018,"Rope",7)
    if variant=="placed":
        add_rope_between(m,tail_b,(.72,.035,.48),.015,"Rope",7)
    return m


def wood_poles(variant:str)->Mesh:
    m=Mesh(); damaged=variant=="damaged"
    count=6
    for i in range(count):
        x=(i-2.5)*.105; z=.045*math.sin(i*1.8); length=1.42-.08*(i%3)
        angle=(i-2.5)*2.5 + (12 if damaged and i==4 else 0)
        add_cylinder(m,(x,.13,z),.045,length,"Wood",8,(0,0,90+angle))
    for x in (-.25,.24):
        add_torus(m,(x,.14,0),.13,.016,"Rope",14,5,(0,90,0))
    if damaged:
        add_box(m,(.35,.16,.06),(.32,.07,.07),"Char",(0,0,28))
    if variant=="placed":
        add_box(m,(0,.035,-.13),(1.50,.035,.09),"Wood",(0,2,0))
    return m


def first_aid(variant:str)->Mesh:
    m=Mesh(); opened=variant=="open"
    add_box(m,(0,.18,0),(.66,.32,.44),"Cloth")
    for x in (-.31,.31): add_box(m,(x,.18,0),(.045,.30,.46),"Rope")
    add_box(m,(0,.19,-.225),(.20,.16,.025),"Cloth")
    add_box(m,(0,.19,-.241),(.055,.18,.012),"Fire")
    add_box(m,(0,.19,-.242),(.18,.055,.012),"Fire")
    add_rope_between(m,(-.20,.35,0),(.20,.35,0),.018,"Rope",7)
    if opened:
        add_box(m,(0,.48,.15),(.64,.055,.43),"Cloth",(-28,0,0))
        for i in range(3): add_box(m,(-.19+i*.19,.34,-.08),(.13,.04,.21),"Cloth",(0,i*5-5,0))
        add_cylinder(m,(.19,.38,.02),.025,.24,"Metal",7,(0,0,90))
    return m


def canteen(variant:str)->Mesh:
    m=Mesh(); full=variant=="full"
    add_cylinder(m,(0,.27,0),.20,.48,"Metal",12)
    add_box(m,(0,.27,-.175),(.34,.30,.08),"Cloth")
    add_cylinder(m,(0,.55,0),.085,.11,"Metal",10)
    add_cylinder(m,(0,.64,0),.095,.08,"Metal",10)
    add_rope_between(m,(-.18,.47,0),(-.29,.10,0),.018,"Rope",7)
    add_rope_between(m,( .18,.47,0),( .29,.10,0),.018,"Rope",7)
    if full:
        add_cylinder(m,(0,.67,0),.055,.018,"Water",10)
    return m


def lantern(variant:str)->Mesh:
    m=Mesh(); lit=variant=="lit"
    add_cylinder(m,(0,.10,0),.20,.13,"Metal",12)
    add_cylinder(m,(0,.55,0),.17,.10,"Metal",12)
    for x,z in ((-.14,0),(.14,0),(0,-.14),(0,.14)):
        add_cylinder(m,(x,.34,z),.012,.40,"Metal",6)
    for ang in (0,90): add_box(m,(0,.34,0),(.28,.34,.012),"Water",(0,ang,0))
    add_torus(m,(0,.69,0),.18,.014,"Metal",18,5,(90,0,0))
    if lit:
        add_flame_cross(m,(0,.18,0),.23,.11)
    return m


def torch(variant:str)->Mesh:
    m=Mesh(); lit=variant in ("lit","dying")
    add_cylinder(m,(0,.48,0),.045,.92,"Wood",8)
    for i in range(4): add_torus(m,(0,.91+i*.035,0),.085-i*.006,.012,"Cloth",12,4,(90,0,i*9))
    if lit:
        add_flame_cross(m,(0,1.00,0),.34 if variant=="lit" else .19,.15 if variant=="lit" else .10)
    if variant=="dying": add_box(m,(0,.99,0),(.13,.07,.13),"Char")
    return m


def stone_pile(variant:str)->Mesh:
    m=Mesh(); count={"small":4,"medium":7,"large":11}.get(variant,7)
    for i in range(count):
        a=i*2.399963; ring=.10+.11*math.sqrt(i); s=.14+.025*(i%4)
        add_rock(m,(math.cos(a)*ring,0,math.sin(a)*ring),(s*1.15,s*.75,s),"Stone",7+(i%2),i*.41)
    return m


def palm_leaf_pile(variant:str)->Mesh:
    m=Mesh(); count=5 if variant=="small" else 9
    for i in range(count):
        yaw=-72+i*(144/max(1,count-1)); root=((i-count/2)*.04,.025,.02*math.sin(i))
        add_leaf(m,root,.68+.04*(i%3),.20,yaw,-16-(i%3)*4,"Leaf",.10)
        add_rope_between(m,root,(root[0]+math.sin(math.radians(yaw))*.60,.02,root[2]+math.cos(math.radians(yaw))*.60),.008,"Wood",5)
    return m


def scrap_bundle(variant:str)->Mesh:
    m=Mesh(); count=6 if variant=="small" else 10
    for i in range(count):
        x=(i-count/2)*.055; y=.05+(i%3)*.045; z=.04*math.sin(i*1.7)
        if i%2==0: add_box(m,(x,y,z),(.54,.035,.075),"Metal",(0,-32+(i*29)%64,(i%3-1)*8))
        else: add_cylinder(m,(x,y,z),.018,.62,"Metal",7,(0,0,55+(i*17)%70))
    add_torus(m,(0,.11,0),.18,.014,"Rope",14,5,(90,0,0))
    return m


def cloth_bundle(variant:str)->Mesh:
    m=Mesh(); layers=3 if variant=="small" else 5
    for i in range(layers):
        add_box(m,(0,.035+i*.055,0),(.62-.035*i,.045,.36+.02*(i%2)),"Cloth",(0,(-1)**i*6,(-1)**i*2))
    add_torus(m,(0,.10,0),.16,.014,"Rope",14,5,(90,0,0))
    return m


def signal_flag(variant:str)->Mesh:
    m=Mesh(); damaged=variant in ("storm-damaged","storm_damaged")
    add_cylinder(m,(-.36,.55,0),.026,1.12,"Wood",7)
    p0=(-.33,.92,0); p1=(.42,.84,0); p2=(.38,.40,0); p3=(-.33,.48,0)
    if damaged:
        a=m.v(p0); b=m.v(p1); c=m.v((.12,.63,0)); m.tri(a,b,c,"Cloth")
        a=m.v(p0); b=m.v((.12,.63,0)); c=m.v(p3); m.tri(a,b,c,"Cloth")
        add_rope_between(m,(.14,.62,0),(.34,.31,.08),.010,"Cloth",5)
    else:
        m.quad(p0,p1,p2,p3,"Cloth")
    add_rope_between(m,(-.32,.88,0),(-.32,.43,0),.010,"Rope",6)
    if variant=="worn": add_box(m,(.08,.61,-.01),(.18,.015,.04),"Char",(0,12,18))
    return m


def cookpot(variant:str)->Mesh:
    m=Mesh(); cooking=variant=="cooking"
    add_cylinder(m,(0,.18,0),.27,.32,"Metal",14)
    add_torus(m,(0,.35,0),.255,.018,"Metal",18,5,(90,0,0))
    add_torus(m,(0,.50,0),.34,.012,"Metal",18,5,(0,0,0))
    add_rope_between(m,(-.25,.38,0),(-.31,.58,0),.012,"Metal",6)
    add_rope_between(m,( .25,.38,0),( .31,.58,0),.012,"Metal",6)
    if cooking:
        add_cylinder(m,(0,.355,0),.21,.018,"Water",14)
        add_box(m,(.05,.38,-.03),(.22,.018,.06),"Leaf",(0,24,0))
    return m


def water_collector(variant:str)->Mesh:
    m=Mesh(); collecting=variant=="collecting"; full=variant=="full"
    for x,z,ang in ((-.48,-.35,-13),(.48,-.35,13),(-.48,.35,-13),(.48,.35,13)):
        add_cylinder(m,(x,.48,z),.035,1.05,"Wood",7,(0,0,ang))
    add_tarp(m,(0,.78,0),1.18,.82,"Tarp",.15,6,False,collecting or full)
    add_cylinder(m,(0,.16,0),.30,.28,"Metal",12)
    if collecting or full:
        add_cylinder(m,(0,.31,0),.245,.016,"Water",12)
    if collecting:
        for x,z in ((-.18,-.05),(.10,.02),(.25,.08)):
            add_cylinder(m,(x,.53,z),.010,.18,"Water",5)
    return m


def mallet(variant:str)->Mesh:
    m=Mesh(); worn=variant=="worn"
    add_cylinder(m,(0,.38,0),.045,.76,"Wood",8)
    add_box(m,(0,.78,0),(.48,.22,.24),"Stone" if worn else "Wood",(0,0,0))
    add_torus(m,(0,.64,0),.07,.012,"Rope",12,4,(90,0,0))
    if worn: add_box(m,(.18,.80,-.12),(.12,.035,.035),"Char",(0,0,18))
    return m


def knife(variant:str)->Mesh:
    m=Mesh(); worn=variant=="worn"
    add_box(m,(0,.12,0),(.14,.24,.085),"Wood")
    add_torus(m,(0,.15,0),.06,.009,"Rope",12,4,(90,0,0))
    p=[(-.06,.23,0),(.06,.23,0),(.035,.56,0),(-.008,.65,0),(-.06,.55,0)]
    for a,b,c in ((0,1,2),(0,2,4),(4,2,3)):
        ia=m.v(p[a]); ib=m.v(p[b]); ic=m.v(p[c]); m.tri(ia,ib,ic,"Metal")
    if worn: add_box(m,(.012,.42,-.010),(.04,.18,.016),"Char",(0,0,8))
    return m


def anchor_peg(variant:str)->Mesh:
    m=Mesh(); active=variant=="active"
    add_cylinder(m,(0,.34,0),.055,.72,"Metal",9)
    add_box(m,(0,.70,0),(.34,.08,.08),"Metal")
    add_torus(m,(0,.59,0),.13,.018,"Rope",16,5,(90,0,0))
    if active:
        add_rope_between(m,(.12,.59,0),(.62,.18,.22),.018,"Rope",7)
        add_rock(m,(.05,0,.02),(.22,.15,.20),"Stone",7,.3)
    return m


def build(asset_id:str,variant:str)->Mesh:
    return {
        "PR-002":rope_coil,"PR-003":wood_poles,"PR-006":first_aid,"PR-007":canteen,
        "PR-008":lantern,"PR-009":torch,"PR-010":stone_pile,"PR-011":palm_leaf_pile,
        "PR-012":scrap_bundle,"PR-013":cloth_bundle,"PR-014":signal_flag,"PR-015":cookpot,
        "PR-016":water_collector,"PR-017":mallet,"PR-018":knife,"PR-019":anchor_peg,
    }[asset_id](variant)


def main()->int:
    if not MANIFEST.exists(): raise SystemExit(f"Missing production manifest: {MANIFEST}")
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    refined=verts=tris=0; families=set()
    for entry in manifest:
        aid=str(entry.get("asset_id",""))
        if aid not in PROP_IDS or entry.get("kind")!="mesh": continue
        mesh=build(aid,str(entry.get("variant","default")))
        write_obj(mesh,ROOT/entry["path"])
        refined+=1; verts+=len(mesh.verts); tris+=len(mesh.faces); families.add(aid)
    missing=PROP_IDS-families
    if missing: raise SystemExit("Prop refinement missed families: "+", ".join(sorted(missing)))
    print(f"Refined {refined} survival/tool prop meshes across {len(families)} families: {verts} vertices / {tris} triangles")
    return 0

if __name__=="__main__": raise SystemExit(main())
