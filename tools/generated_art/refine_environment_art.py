#!/usr/bin/env python3
"""Refine the visible Stormnatten environment around the hero assets.

The broad generator owns complete asset-master coverage. This deterministic pass
replaces the environment families that frame the canonical beach/camp/ravine
visual language with richer Quest-2-conscious geometry while preserving paths and
Unity GUIDs.

Families refined:
- EN-001 shipwreck hull chunks
- EN-002 broken plank piles
- EN-005 beach stone clusters
- EN-006 driftwood clusters
- EN-007 palm variants
- EN-008 palm-frond ground clutter
- EN-009 broadleaf bushes
- EN-010 vine clusters
- EN-012 rock-wall/ravine modules
"""
from __future__ import annotations

import json
import math
from pathlib import Path

from refine_hero_art import (
    Mesh,
    add_box,
    add_cylinder,
    add_rope_between,
    tp,
    write_obj,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROD = ROOT / "Assets" / "ProductionArt"
MANIFEST = PROD / "Docs" / "production_art_manifest.json"

ENV_IDS = {
    "EN-001", "EN-002", "EN-005", "EN-006", "EN-007",
    "EN-008", "EN-009", "EN-010", "EN-012",
}


def add_rock(m: Mesh, center, radius=(0.5, 0.35, 0.45), mat="Stone", segments=8, phase=0.0):
    """Low-poly irregular boulder with deterministic silhouette variation."""
    cx, cy, cz = center
    rx, ry, rz = radius
    rings = []
    for ring_i, y01 in enumerate((0.18, 0.52, 0.82)):
        y = cy + (y01 - 0.18) * (ry * 1.45)
        row = []
        for i in range(segments):
            a = 2 * math.pi * i / segments + phase
            wobble = 1.0 + 0.10 * math.sin(i * 2.17 + ring_i * 1.31 + phase * 3.0)
            taper = (0.90, 1.04, 0.72)[ring_i]
            row.append((cx + math.cos(a) * rx * wobble * taper,
                        y + math.sin(i * 1.73 + phase) * ry * 0.045,
                        cz + math.sin(a) * rz * (2.0 - wobble) * taper))
        rings.append(row)
    bottom = (cx, cy, cz)
    top = (cx + math.sin(phase) * rx * .08, cy + ry * 1.32, cz + math.cos(phase) * rz * .06)
    for i in range(segments):
        j = (i + 1) % segments
        a = m.v(bottom); b = m.v(rings[0][j]); c = m.v(rings[0][i]); m.tri(a,b,c,mat)
        m.quad(rings[0][i], rings[0][j], rings[1][j], rings[1][i], mat)
        m.quad(rings[1][i], rings[1][j], rings[2][j], rings[2][i], mat)
        a = m.v(top); b = m.v(rings[2][i]); c = m.v(rings[2][j]); m.tri(a,b,c,mat)


def add_leaf(m: Mesh, root, length, width, yaw, pitch=-8.0, mat="Leaf", droop=0.12):
    """One stylized lance leaf; Leaf material is double-sided in Unity."""
    r = math.radians(yaw)
    p = math.radians(pitch)
    dx = math.sin(r) * math.cos(p)
    dz = math.cos(r) * math.cos(p)
    dy = math.sin(p)
    sx = math.cos(r)
    sz = -math.sin(r)
    x, y, z = root
    mid = (x + dx * length * .48, y + dy * length * .48 + .04, z + dz * length * .48)
    tip = (x + dx * length, y + dy * length - droop, z + dz * length)
    left = (mid[0] + sx * width * .5, mid[1], mid[2] + sz * width * .5)
    right = (mid[0] - sx * width * .5, mid[1], mid[2] - sz * width * .5)
    a=m.v((x,y,z),(0,.5)); b=m.v(left,(.48,1)); c=m.v(tip,(1,.5)); d=m.v(right,(.48,0))
    m.tri(a,b,c,mat); m.tri(a,c,d,mat)
    add_cylinder(m, ((x+tip[0])*.5,(y+tip[1])*.5,(z+tip[2])*.5), .007, length*.96, "Wood", 5,
                 (90-pitch,0,-yaw))


def add_frond(m: Mesh, root, yaw, scale=1.0, mat="Leaf", droop=.18):
    x,y,z=root
    # strong midrib
    r=math.radians(yaw)
    end=(x+math.sin(r)*1.18*scale, y-.13*scale, z+math.cos(r)*1.18*scale)
    add_rope_between(m, root, end, .013*scale, "Wood", 6)
    for i in range(1,7):
        t=i/7.0
        bx=x+(end[0]-x)*t; by=y+(end[1]-y)*t; bz=z+(end[2]-z)*t
        span=(.30*(1-abs(t-.48)*1.1)+.06)*scale
        for side in (-1,1):
            add_leaf(m,(bx,by,bz), span, .11*scale, yaw+side*(64+7*i), -14-3*i, mat, droop*.35)


def shipwreck(variant: str) -> Mesh:
    m=Mesh(); large=variant=="large"
    length=4.2 if large else 3.1
    width=1.85 if large else 1.48
    height=1.7 if large else 1.35
    # keel and broken rising bow/stern spine
    add_cylinder(m,(0,.28,0),.085,length,"Wood",10,(0,0,90))
    # hull ribs along keel, each slightly different / broken
    rib_count=9 if large else 7
    for i in range(rib_count):
        t=i/(rib_count-1); x=-length*.43+t*length*.86
        rib_h=height*(.70+.20*math.sin(t*math.pi))
        half=width*(.42+.08*math.sin(t*math.pi))
        add_cylinder(m,(x,rib_h*.46,-half*.42),.048,rib_h,"Wood",8,(0,0,-18))
        add_cylinder(m,(x,rib_h*.46, half*.42),.048,rib_h,"Wood",8,(0,0, 18))
        add_cylinder(m,(x,.56,0),.042,width*.92,"Wood",8,(90,0,0))
    # longitudinal planks: deliberately incomplete to read as wreckage
    for side in (-1,1):
        for row in range(4):
            y=.28+row*.28
            z=side*(width*.34+row*.05)
            for seg in range(3):
                seg_len=length*(.24 if seg!=1 else .27)
                cx=-length*.29+seg*length*.29 + (row%2)*.08
                add_box(m,(cx,y,z),(seg_len,.075,.105),"Wood",(0,(-3+row*2)*side,side*(4+row)))
    # bent metal reinforcement straps and torn rope remnants
    for x in (-length*.23, length*.19):
        add_box(m,(x,.73,-width*.42),(.065,1.05,.055),"Metal",(0,0,-8))
        add_box(m,(x,.73, width*.42),(.065,1.05,.055),"Metal",(0,0, 8))
    add_rope_between(m,(-length*.28,.95,width*.43),(length*.05,.43,width*.56),.020,"Rope",7)
    # jagged broken planks escaping the hull silhouette
    add_box(m,(length*.48,.70,-.30),(.78,.075,.11),"Wood",(4,12,31))
    add_box(m,(-length*.47,.82,.26),(.68,.07,.10),"Wood",(-6,-18,-28))
    return m


def plank_pile(variant: str) -> Mesh:
    m=Mesh(); count={"small":6,"medium":9,"large":13}.get(variant,9)
    for i in range(count):
        layer=i//4; slot=i%4
        length=.88+.13*((i*3)%5)
        cx=(slot-1.5)*.24 + .05*math.sin(i*2.2)
        cz=(layer-.8)*.18
        yaw=(-34 + (i*47)%73)
        add_box(m,(cx,.055+layer*.085,cz),(length,.065,.105),"Wood",(0,yaw,(i%3-1)*4))
        if i%3==0:
            # exposed bent nail / bracket
            add_cylinder(m,(cx+.12,.11+layer*.085,cz-.03),.009,.10,"Metal",6,(0,0,14+i*5))
    if variant=="large":
        add_rope_between(m,(-.48,.24,-.18),(.55,.19,.22),.017,"Rope",7)
    return m


def stone_cluster(variant: str) -> Mesh:
    m=Mesh(); count={"small":4,"medium":7,"large":11}.get(variant,7)
    for i in range(count):
        a=i*2.399963; ring=.13+.16*math.sqrt(i)
        x=math.cos(a)*ring; z=math.sin(a)*ring
        scale=.20+.055*((i*5)%4)
        add_rock(m,(x,0,z),(scale*1.18,scale*.78,scale),"Stone",7+(i%3),i*.37)
    return m


def driftwood(variant: str) -> Mesh:
    m=Mesh(); count={"small":3,"medium":5,"large":7}.get(variant,5)
    for i in range(count):
        length=.70+.20*((i*7)%4)
        x=(i-count/2)*.15; z=.12*math.sin(i*1.7); yaw=(-45+(i*61)%100)
        add_cylinder(m,(x,.10+i*.018,z),.045+.008*(i%3),length,"Wood",8,(0,0,90+yaw))
        if i%2==0:
            # forked branch
            add_cylinder(m,(x+.08,.15,z+.02),.026,length*.42,"Wood",7,(18,yaw,48))
    return m


def palm(variant: str) -> Mesh:
    m=Mesh()
    if variant=="young": height=2.4; trunk=.105; crown=7
    elif variant=="broken": height=2.65; trunk=.145; crown=3
    else: height=4.15; trunk=.155; crown=9
    # segmented, gently curved trunk makes silhouette much less cylindrical
    segments=8 if height>3 else 6
    for i in range(segments):
        t=i/segments
        y=(i+.5)*height/segments
        x=.08*math.sin(t*2.3); z=.05*math.sin(t*3.1+.5)
        r=trunk*(1-.32*t)
        add_cylinder(m,(x,y,z),r,height/segments*1.08,"Wood",9,(2*math.sin(i),0,3*math.cos(i*.8)))
        if i%2==0:
            add_box(m,(x,y,z),(r*2.15,.025,r*2.15),"Rope",(0,i*31,0))
    top=(.08*math.sin(2.3),height+.02,.05*math.sin(3.6))
    if variant=="broken":
        add_box(m,(top[0],top[1]+.05,top[2]),(.28,.18,.25),"Char",(9,18,14))
    for i in range(crown):
        yaw=i*(360/max(crown,1)) + (11 if variant=="mature" else 0)
        add_frond(m,(top[0],top[1]-.03,top[2]),yaw,.78 if variant=="young" else 1.0,"Leaf",.22)
    if variant=="mature":
        for i in range(3):
            a=math.radians(i*120+22)
            add_rock(m,(top[0]+math.sin(a)*.15,height-.05,top[2]+math.cos(a)*.15),(.09,.10,.09),"Wood",7,i)
    return m


def frond_clutter(variant: str) -> Mesh:
    m=Mesh(); count=4 if variant=="small" else 7
    for i in range(count):
        x=(i-count/2)*.16; z=.12*math.sin(i*2.0)
        add_frond(m,(x,.035,z),-78+i*31,.52+.07*(i%3),"Leaf",.08)
    return m


def bush(variant: str) -> Mesh:
    m=Mesh(); stems={"small":5,"medium":8,"dense":13}.get(variant,8)
    scale={"small":.72,"medium":1.0,"dense":1.14}.get(variant,1.0)
    for i in range(stems):
        a=i*2.399963; r=.10+.045*(i%4)
        root=(math.cos(a)*r,.03,math.sin(a)*r)
        h=(.55+.12*((i*5)%4))*scale
        lean=(math.sin(a)*.15*h,h,math.cos(a)*.15*h)
        tip=(root[0]+lean[0],root[1]+lean[1],root[2]+lean[2])
        add_rope_between(m,root,tip,.013*scale,"Wood",6)
        for j in range(2,5):
            t=j/5
            p=(root[0]+lean[0]*t,root[1]+lean[1]*t,root[2]+lean[2]*t)
            add_leaf(m,p,.28*scale,.16*scale,math.degrees(a)+j*29,-10-j*4,"Leaf",.05)
            add_leaf(m,p,.24*scale,.14*scale,math.degrees(a)-j*33,-13-j*3,"Leaf",.05)
    return m


def vines(variant: str) -> Mesh:
    m=Mesh(); count={"short":3,"hanging":5,"dense":8}.get(variant,5)
    for i in range(count):
        x=(i-(count-1)/2)*.15
        h=.72+.14*(i%3) if variant!="short" else .48+.08*(i%2)
        # segmented curved vine rather than a straight rope
        prev=(x,h,0)
        for seg in range(1,7):
            t=seg/6
            cur=(x+.08*math.sin(t*math.pi*2+i), h*(1-t), .06*math.sin(t*math.pi+i*.7))
            add_rope_between(m,prev,cur,.010 if variant!="dense" else .012,"Rope",6)
            prev=cur
        if i%2==0:
            add_leaf(m,(prev[0],.18,prev[2]),.20,.10,25+i*41,-18,"Leaf",.04)
    return m


def rock_wall(variant: str) -> Mesh:
    m=Mesh()
    if variant=="ledge": rows=3; cols=5
    else: rows=4; cols=6
    for row in range(rows):
        for col in range(cols):
            x=(col-(cols-1)/2)*.62 + (row%2)*.18
            y=row*.42
            z=.07*math.sin(col*1.8+row)
            if variant=="corner" and col>cols//2:
                # rotate half the module into an L shape using x -> z
                x2=(cols//2-col)*.58
                z2=(col-cols//2)*.58
                add_rock(m,(.55+x2*.08,y,z2),( .38,.34,.30),"Stone",8,(row*7+col)*.21)
            else:
                add_rock(m,(x,y,z),(.36+.04*((col+row)%2),.33,.31),"Stone",8,(row*7+col)*.21)
    if variant=="ledge":
        for col in range(5):
            add_rock(m,((col-2)*.66,1.15,-.18),(.44,.24,.54),"Stone",8,col*.43)
    return m


def build(asset_id: str, variant: str) -> Mesh:
    if asset_id=="EN-001": return shipwreck(variant)
    if asset_id=="EN-002": return plank_pile(variant)
    if asset_id=="EN-005": return stone_cluster(variant)
    if asset_id=="EN-006": return driftwood(variant)
    if asset_id=="EN-007": return palm(variant)
    if asset_id=="EN-008": return frond_clutter(variant)
    if asset_id=="EN-009": return bush(variant)
    if asset_id=="EN-010": return vines(variant)
    if asset_id=="EN-012": return rock_wall(variant)
    raise KeyError(asset_id)


def main() -> int:
    if not MANIFEST.exists():
        raise SystemExit(f"Missing production manifest: {MANIFEST}")
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    refined=0; verts=0; tris=0; families=set()
    for entry in manifest:
        aid=str(entry.get("asset_id",""))
        if aid not in ENV_IDS or entry.get("kind")!="mesh":
            continue
        path=ROOT/entry["path"]
        mesh=build(aid,str(entry.get("variant","default")))
        write_obj(mesh,path)
        refined+=1; verts+=len(mesh.verts); tris+=len(mesh.faces); families.add(aid)
    missing=ENV_IDS-families
    if missing:
        raise SystemExit("Environment refinement missed asset families: "+", ".join(sorted(missing)))
    print(f"Refined {refined} environment meshes across {len(families)} families: {verts} vertices / {tris} triangles")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
