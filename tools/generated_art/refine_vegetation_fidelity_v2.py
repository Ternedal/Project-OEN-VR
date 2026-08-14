#!/usr/bin/env python3
"""Clean broadleaf/pinnate rebuild for Project ØEN tropical vegetation.

The dense-scene review showed that adding detail on top of the old procedural plants
still left a twig/needle silhouette. This pass therefore rebuilds EN-007..EN-010 from
clean geometry whose *first read* matches the approved atlas:

- palms use curved tapered trunks and layered pinnate fronds with broad leaflets;
- ground fronds use fern/palm-like compound leaves rather than starburst sticks;
- bushes are foliage masses with only a few hidden woody stems;
- vines are hanging rope stems carrying large alternating tropical leaves.

All canonical OBJ paths/GUIDs and the existing shared material families are preserved.
The geometry remains deterministic and comfortably inside the existing repo-side
Quest review budgets.
"""
from __future__ import annotations

import json
import math
import random
from pathlib import Path

from refine_mockup_fidelity import Mesh, add_cylinder_between, add_torus, write_obj

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PROD=ROOT/"Assets"/"ProjectOEN"/"ProductionArt"
MANIFEST=PROD/"Docs"/"production_art_manifest.json"
TARGETS={"EN-007","EN-008","EN-009","EN-010"}


def vadd(a,b): return (a[0]+b[0],a[1]+b[1],a[2]+b[2])
def vmul(a,s): return (a[0]*s,a[1]*s,a[2]*s)
def vsub(a,b): return (a[0]-b[0],a[1]-b[1],a[2]-b[2])
def norm(a):
    l=math.sqrt(a[0]*a[0]+a[1]*a[1]+a[2]*a[2]) or 1.0
    return (a[0]/l,a[1]/l,a[2]/l)


def add_double_quad(m:Mesh,a,b,c,d,mat="Leaf"):
    m.quad(a,b,c,d,mat)
    m.quad(d,c,b,a,mat)


def add_leaf_card(m:Mesh,base,tip,width:float,mat="Leaf",twist:float=0.0):
    """Tapered two-sided leaf with a broad mid-body and pointed tip."""
    direction=norm(vsub(tip,base))
    # A stable side vector. Blend horizontal and vertical side vectors so leaves
    # never collapse to a line from common headset angles.
    horizontal=norm((-direction[2],0.0,direction[0]))
    up_side=norm((direction[1],-direction[0],0.18))
    t=math.sin(math.radians(twist))
    side=norm((horizontal[0]*(1-abs(t))+up_side[0]*t,
               horizontal[1]*(1-abs(t))+up_side[1]*t,
               horizontal[2]*(1-abs(t))+up_side[2]*t))
    q1=vadd(base,vmul(side,width*.18)); q2=vadd(base,vmul(side,-width*.18))
    mid=vadd(base,vmul(vsub(tip,base),.56))
    q3=vadd(mid,vmul(side,-width*.52)); q4=vadd(mid,vmul(side,width*.52))
    add_double_quad(m,q1,q2,q3,q4,mat)
    # second taper section to the pointed tip
    add_double_quad(m,q4,q3,tip,tip,mat)


def curve_points(root,yaw,length,lift,droop,bend=0.0,segments=8):
    a=math.radians(yaw); dx,dz=math.cos(a),math.sin(a); px,pz=-dz,dx
    pts=[]
    for i in range(segments+1):
        t=i/segments
        lateral=math.sin(t*math.pi)*bend
        pts.append((root[0]+dx*length*t+px*lateral,
                    root[1]+math.sin(t*math.pi)*lift-droop*(t**1.65),
                    root[2]+dz*length*t+pz*lateral))
    return pts


def add_pinnate_frond(m:Mesh,root,yaw,length,lift,droop,seed,leaf_pairs=9,leaf_scale=1.0,mat="Leaf",spine_mat="Wood"):
    rnd=random.Random(seed)
    pts=curve_points(root,yaw,length,lift,droop,bend=rnd.uniform(-.07,.07),segments=10)
    for a,b in zip(pts[:-1],pts[1:]):
        add_cylinder_between(m,a,b,.0075 if length<1 else .010,spine_mat,5)
    a=math.radians(yaw); dx,dz=math.cos(a),math.sin(a); sx,sz=-dz,dx
    for j in range(1,leaf_pairs+1):
        t=.10+.78*j/(leaf_pairs+1)
        idx=min(len(pts)-2,max(1,int(t*(len(pts)-1))))
        base=pts[idx]
        taper=(math.sin(math.pi*t)**.46)
        leaflet_len=(.24+.16*taper)*leaf_scale*(.85+rnd.random()*.22)
        leaflet_w=(.10+.055*taper)*leaf_scale
        forward=.055*length*(1-t)
        for sign in (-1,1):
            tip=(base[0]+sx*leaflet_len*sign+dx*forward,
                 base[1]-.035-.075*t+rnd.uniform(-.018,.018),
                 base[2]+sz*leaflet_len*sign+dz*forward)
            add_leaf_card(m,base,tip,leaflet_w,mat,twist=sign*(18+7*(j%3)))
    # broad terminal leaflet closes the frond silhouette
    prev=pts[-3]; tip=pts[-1]
    add_leaf_card(m,prev,tip,.15*leaf_scale,mat,twist=12)


def add_trunk(m:Mesh,h:float,young=False,broken=False):
    pts=[(0,.02,0),(.05,h*.23,.01),(.10,h*.47,-.025),(.04,h*.70,.045),(.12,h,.02)]
    if broken:
        pts[-1]=(.18,h*.92,.06)
    r0=.145 if not young else .105
    radii=[r0,r0*.91,r0*.80,r0*.68,r0*.55]
    for i in range(len(pts)-1):
        add_cylinder_between(m,pts[i],pts[i+1],radii[i],"Wood",10,radii[i+1])
    scars=7 if young else 10
    for i in range(1,scars+1):
        t=i/(scars+1); seg=min(3,int(t*4)); local=(t*4)-seg
        a=pts[seg]; b=pts[min(seg+1,4)]
        center=(a[0]*(1-local)+b[0]*local,a[1]*(1-local)+b[1]*local,a[2]*(1-local)+b[2]*local)
        add_torus(m,center,radii[seg]*1.015,.006,"Wood",12,4,"y")
    return pts[-1]


def build_palm(variant:str)->Mesh:
    m=Mesh(); young=variant=="young"; broken=variant=="broken"
    h=2.75 if young else (3.15 if broken else 4.05)
    crown=add_trunk(m,h,young,broken)
    n=9 if young else (9 if broken else 14)
    for i in range(n):
        yaw=i*360/n+(i%3-1)*7
        length=(.88 if young else 1.36)*(1+.08*math.sin(i*1.7))
        if broken and i in (2,6): length*=.62
        add_pinnate_frond(m,crown,yaw,length,.19+.07*(i%3),.30+.07*(i%4),700+i,leaf_pairs=8 if young else 10,leaf_scale=.82 if young else 1.0)
    # younger upright spear leaves create crown height and layered depth
    for i,yaw in enumerate((20,140,260)):
        add_pinnate_frond(m,crown,yaw,.72 if young else .92,.48,.10,760+i,leaf_pairs=6,leaf_scale=.72)
    if not young:
        # small coconut cluster; Wood keeps material vocabulary stable
        for i,yaw in enumerate((15,105,205,300)):
            a=math.radians(yaw)
            c=(crown[0]+math.cos(a)*.115,crown[1]-.13,crown[2]+math.sin(a)*.115)
            add_cylinder_between(m,(c[0],c[1]-.035,c[2]),(c[0],c[1]+.035,c[2]),.052,"Wood",8,.055)
    if broken:
        # one hanging dead frond keeps the state visibly damaged
        add_pinnate_frond(m,(crown[0]-.02,crown[1]-.08,crown[2]),310,.80,.04,.58,790,leaf_pairs=6,leaf_scale=.62)
    return m


def build_ground_fronds(variant:str)->Mesh:
    m=Mesh(); medium=variant=="medium"; n=10 if medium else 6
    for i in range(n):
        a=i*2.399963; r=.06+.045*math.sqrt(i+1)
        root=(math.cos(a)*r,.025,math.sin(a)*r)
        # short Wood petiole is mostly hidden under foliage but satisfies the physical stem read
        stem_tip=(root[0]+math.cos(a)*.10,.08,root[2]+math.sin(a)*.10)
        add_cylinder_between(m,root,stem_tip,.010,"Wood",5)
        add_pinnate_frond(m,stem_tip,math.degrees(a)+18*(i%2),.56 if medium else .44,.12,.16,820+i,leaf_pairs=7 if medium else 6,leaf_scale=.58 if medium else .50)
    return m


def add_branch(m:Mesh,a,b,r=.014):
    # a few hidden woody stems; foliage remains the dominant silhouette
    add_cylinder_between(m,a,b,r,"Wood",6,r*.72)


def build_bush(variant:str)->Mesh:
    m=Mesh(); scale={"small":.72,"medium":1.0,"dense":1.30}.get(variant,1.0)
    rnd=random.Random("bush:"+variant)
    branches=5 if variant=="small" else (7 if variant=="medium" else 9)
    for i in range(branches):
        yaw=i*360/branches+rnd.uniform(-18,18); a=math.radians(yaw)
        top=(math.cos(a)*.23*scale,.48*scale+rnd.uniform(-.05,.11)*scale,math.sin(a)*.23*scale)
        add_branch(m,(0,.02,0),top,.013*scale)
    leaves=34 if variant=="small" else (54 if variant=="medium" else 82)
    for i in range(leaves):
        # Golden-angle sphere/hemisphere distribution creates a lush mass without clumps of stems.
        a=i*2.399963+rnd.uniform(-.16,.16)
        t=(i+.5)/leaves
        y=(.10+.53*(t**.72))*scale
        radial=(.16+.27*math.sin(math.pi*t)**.65)*scale
        base=(math.cos(a)*radial*.72,y,math.sin(a)*radial*.72)
        outward=(math.cos(a),rnd.uniform(-.16,.20),math.sin(a))
        length=(.26+.08*(i%4))*scale
        tip=(base[0]+outward[0]*length,base[1]+outward[1]*length,base[2]+outward[2]*length)
        add_leaf_card(m,base,tip,(.17+.035*(i%3))*scale,"Leaf",twist=(-28+14*(i%5)))
    # crown leaves close the top and make the plant read as a broadleaf shrub at distance
    for i in range(9 if variant!="dense" else 13):
        yaw=i*(360/(9 if variant!="dense" else 13))+11
        a=math.radians(yaw); base=(0,.52*scale,0)
        tip=(math.cos(a)*.38*scale,.58*scale+(.05 if i%2 else .0),math.sin(a)*.38*scale)
        add_leaf_card(m,base,tip,.22*scale,"Leaf",twist=20*((i%3)-1))
    return m


def build_vines(variant:str)->Mesh:
    m=Mesh(); n={"short":5,"hanging":8,"dense":12}.get(variant,8)
    rnd=random.Random("vines:"+variant)
    for i in range(n):
        x=(i-(n-1)/2)*.095
        top=.52 if variant=="short" else (.86+.06*(i%4))
        pts=[]
        for s in range(8):
            t=s/7
            pts.append((x+.055*math.sin(t*math.pi*2+i*.8),top*(1-t),.055*math.sin(t*math.pi+i*.57)))
        for a,b in zip(pts[:-1],pts[1:]): add_cylinder_between(m,a,b,.007 if variant!="dense" else .0085,"Rope",5)
        for j,t in enumerate((.16,.31,.47,.63,.78,.90)):
            idx=min(6,max(1,int(t*7))); base=pts[idx]
            yaw=28+i*31+j*79
            ang=math.radians(yaw); length=.22+.035*((i+j)%3)
            tip=(base[0]+math.cos(ang)*length,base[1]-.035-.025*(j%2),base[2]+math.sin(ang)*length)
            add_leaf_card(m,base,tip,.13,"Leaf",twist=(-24+12*((i+j)%5)))
    return m


def build(aid:str,variant:str)->Mesh:
    if aid=="EN-007": return build_palm(variant)
    if aid=="EN-008": return build_ground_fronds(variant)
    if aid=="EN-009": return build_bush(variant)
    if aid=="EN-010": return build_vines(variant)
    raise KeyError(aid)


def main()->int:
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8")); count=verts=faces=0; seen=set()
    for e in manifest:
        aid=str(e.get("asset_id","")); variant=str(e.get("variant","default"))
        if aid not in TARGETS or e.get("kind")!="mesh": continue
        mesh=build(aid,variant); write_obj(mesh,ROOT/e["path"])
        count+=1; verts+=len(mesh.verts); faces+=len(mesh.faces); seen.add(aid)
    missing=TARGETS-seen
    if missing: raise SystemExit("Vegetation V2 missed: "+", ".join(sorted(missing)))
    print(f"Clean tropical vegetation V2: {count} meshes / {len(seen)} families / {verts} vertices / {faces} faces")
    return 0


if __name__=="__main__": raise SystemExit(main())
