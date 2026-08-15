#!/usr/bin/env python3
"""Sixth visual fidelity pass: organic fire + fuller tropical palm silhouettes.

V5 aligned the major structures with the approved atlas. Direct visual review still
showed two remaining outliers: the mature palm crown was too sparse/flat and the strong
campfire read as a few rigid orange blades. This final targeted pass replaces only
EN-007 and CS-009 with denser but bounded Quest-conscious geometry.
"""
from __future__ import annotations

import json
import math
import random
from pathlib import Path

from refine_mockup_fidelity import (
    Mesh,
    add_cylinder_between,
    add_irregular_rock,
    add_stick,
    add_torus,
    write_obj,
)
from refine_mockup_fidelity_v2 import add_ribbon

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PROD=ROOT/"Assets"/"ProductionArt"
MANIFEST=PROD/"Docs"/"production_art_manifest.json"
TARGETS={"CS-009","EN-007"}


def add_teardrop_flame(m:Mesh,center,height,radius,seed,segments=12,rings=7):
    """Closed, gently bent low-poly flame volume instead of intersecting flat blades."""
    rnd=random.Random(seed); cx,cy,cz=center
    ring_ids=[]
    for ri in range(rings):
        t=ri/(rings-1)
        # broad lower body, narrowing continuously to a soft tip
        profile=(math.sin(math.pi*(t*.92+.03))**.72)*(1-t*.74)
        rr=max(.010,radius*profile)
        bend_x=math.sin(t*math.pi*1.35+seed*.17)*radius*.22*t
        bend_z=math.cos(t*math.pi*1.12+seed*.11)*radius*.13*t
        row=[]
        for si in range(segments):
            a=2*math.pi*si/segments
            wobble=1+.06*math.sin(a*3+ri*.8+seed)+.03*math.sin(a*5-seed*.3)
            p=(cx+bend_x+math.cos(a)*rr*wobble,cy+height*t,cz+bend_z+math.sin(a)*rr*wobble)
            row.append(m.v(p,(si/segments,t)))
        ring_ids.append(row)
    for ri in range(rings-1):
        for si in range(segments):
            sj=(si+1)%segments
            a,b=ring_ids[ri][si],ring_ids[ri][sj]
            c,d=ring_ids[ri+1][sj],ring_ids[ri+1][si]
            m.tri(a,b,c,"Fire"); m.tri(a,c,d,"Fire")
    # tiny closing cap; avoids an obvious flat polygon at the top
    tip=m.v((cx+math.sin(seed)*radius*.15,cy+height*1.035,cz+math.cos(seed)*radius*.08),(.5,1))
    for si in range(segments):
        sj=(si+1)%segments
        m.tri(ring_ids[-1][si],ring_ids[-1][sj],tip,"Fire")


def build_fire()->Mesh:
    m=Mesh(); rnd=random.Random(2609)
    # Lower, less regular stone ring than previous passes.
    for i in range(14):
        a=2*math.pi*i/14+rnd.uniform(-.055,.055); r=.305+rnd.uniform(-.018,.014)
        add_irregular_rock(
            m,(math.cos(a)*r,.035,math.sin(a)*r),
            (.070+rnd.uniform(-.009,.009),.040+rnd.uniform(-.006,.007),.065+rnd.uniform(-.009,.009)),
            2620+i,"Stone",4,9,
        )
    # Four crossed, visibly charred split logs.
    for a,b,s in [
        ((-.26,.100,-.15),(.26,.140,.15),2650),
        ((-.26,.135,.15),(.26,.100,-.15),2651),
        ((-.22,.165,-.025),(.22,.177,.035),2652),
        ((-.17,.088,.065),(.18,.115,-.075),2653),
    ]:
        add_stick(m,a,b,.039,"Char",s,10,4)
    # Ember bed is a broken warm core, not a second stone ring.
    for i in range(13):
        a=2*math.pi*i/13; rr=.055+.085*((i%4)/3)
        add_irregular_rock(m,(math.cos(a)*rr,.064+(i%2)*.006,math.sin(a)*rr),(.030,.012,.026),2670+i,"Fire" if i%3 else "Char",3,7)

    # Overlapping 3D flame bodies create a warm volume from every headset angle.
    add_teardrop_flame(m,(0,.135,0),.47,.145,2701,14,8)
    add_teardrop_flame(m,(.065,.142,-.025),.34,.105,2702,12,7)
    add_teardrop_flame(m,(-.060,.144,.035),.29,.090,2703,12,7)
    add_teardrop_flame(m,(.005,.148,.070),.23,.068,2704,10,6)
    return m


def add_frond(m:Mesh,crown,yaw,length,lift,droop,seed,broken=False):
    rnd=random.Random(seed); a=math.radians(yaw); dx,dz=math.cos(a),math.sin(a); x,y,z=crown
    centre=[]
    for i in range(9):
        t=i/8
        wind=math.sin(t*math.pi*1.15+seed*.21)*.050*(1-t*.25)
        centre.append((
            x+dx*length*t-dz*wind,
            y+math.sin(t*math.pi)*lift-droop*(t**1.68),
            z+dz*length*t+dx*wind,
        ))
    # Midrib only: cheap, curved structural read.
    for p,q in zip(centre,centre[1:]): add_cylinder_between(m,p,q,.0065,"Wood",5)
    # Paired leaflets, increasingly short toward the tip; broad enough to form a full crown.
    perp=(-dz,0,dx)
    for j,t in enumerate((.13,.22,.31,.40,.49,.58,.67,.76,.84,.91)):
        idx=min(7,max(1,int(round(t*8)))); b=centre[idx]
        span=(.39-.24*t)*(1+rnd.uniform(-.07,.07))
        if broken and j>7: span*=.55
        for sign in (-1,1):
            tip=(b[0]+perp[0]*span*sign,b[1]-.045-rnd.uniform(0,.045),b[2]+perp[2]*span*sign)
            add_ribbon(m,[b,tip],[.080*(1-t*.35),.011],"Leaf")
    # One continuous centre blade fills gaps between leaflet pairs.
    add_ribbon(m,centre,[.18,.20,.19,.17,.15,.12,.09,.055,.012],"Leaf")


def build_palm(variant:str)->Mesh:
    m=Mesh(); young=variant=="young"; broken=variant=="broken"
    h=2.80 if young else (3.05 if broken else 4.00)
    trunk=[(0,.02,0),(.075,h*.30,.012),(-.055,h*.64,.065),(.105,h,.018)]
    radii=[.145 if not young else .112,.132 if not young else .098,.112 if not young else .083,.085 if not young else .065]
    for i in range(3): add_cylinder_between(m,trunk[i],trunk[i+1],radii[i],"Wood",12,radii[i+1])
    scars=7 if young else 11
    for i in range(scars):
        t=(i+1)/(scars+1)
        # scar rings follow the bent trunk closely enough to read as old frond bases
        x=.035*math.sin(t*math.pi*1.5); z=.018+.035*math.sin(t*math.pi)
        add_torus(m,(x,h*t,z),radii[min(2,int(t*3))]*1.02,.007,"Char",16,4,"y")

    crown=trunk[-1]
    n=14 if young else (14 if broken else 22)
    for i in range(n):
        yaw=i*360/n+(i%5-2)*4.5
        length=(1.02 if young else 1.55)*(1+.10*math.sin(i*1.71))
        lift=.22+.075*(i%4)
        droop=.24+.075*(i%3)
        if broken and i in (2,6,10): length*=.58
        add_frond(m,crown,yaw,length,lift,droop,2800+i,broken)

    # Younger central spear leaves add height and prevent an umbrella-flat silhouette.
    for yaw in (18,108,198,288):
        a=math.radians(yaw); x,y,z=crown
        add_ribbon(m,[
            (x,y,z),
            (x+math.cos(a)*.20,y+.42,z+math.sin(a)*.20),
            (x+math.cos(a)*.39,y+.60,z+math.sin(a)*.39),
        ],[.19,.13,.015],"Leaf")

    if not young:
        for i,yaw in enumerate((15,100,190,285)):
            a=math.radians(yaw)
            add_irregular_rock(m,(crown[0]+math.cos(a)*.115,crown[1]-.105,crown[2]+math.sin(a)*.115),(.058,.067,.058),2880+i,"Wood",3,8)
    if broken:
        add_stick(m,(.07,h*.68,.03),(.55,h*.90,.18),.035,"Wood",2890,8,3)
    return m


def build(aid,variant):
    if aid=="CS-009": return build_fire()
    if aid=="EN-007": return build_palm(variant)
    raise KeyError(aid)


def main()->int:
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8")); count=verts=faces=0; seen=set()
    for e in manifest:
        aid=str(e.get("asset_id","")); variant=str(e.get("variant","default"))
        if aid not in TARGETS or e.get("kind")!="mesh": continue
        mesh=build(aid,variant); write_obj(mesh,ROOT/e["path"])
        count+=1; verts+=len(mesh.verts); faces+=len(mesh.faces); seen.add((aid,variant))
    fam={a for a,_ in seen}
    if fam!=TARGETS: raise SystemExit(f"Mockup fidelity v6 coverage mismatch: {sorted(TARGETS-fam)}")
    print(f"Mockup fidelity v6: {count} meshes / {verts} vertices / {faces} faces")
    print("Fuller layered palm crowns + low-profile fire ring with overlapping 3D flame volumes")
    return 0

if __name__=="__main__": raise SystemExit(main())
