#!/usr/bin/env python3
"""Third visual-fidelity correction pass driven by the second actual OBJ review.

This pass targets the remaining obvious mockup misses rather than increasing global
poly counts: the tarp gets real tension/sag, the radio loses its accidental spike-like
corner guards, the mature palm gets a broad layered crown, the strong campfire gets a
smaller natural ring and smoother flame tongues, and the wreck gets storm-torn cloth,
deck beams and rope clutter while preserving its new readable hull silhouette.
"""
from __future__ import annotations

import json
import math
import random
from pathlib import Path

from refine_mockup_fidelity import (
    Mesh,
    add_box,
    add_cylinder_between,
    add_irregular_rock,
    add_stick,
    add_torus,
    build as build_v1,
    write_obj,
)
from refine_mockup_fidelity_v2 import build_shipwreck, add_ribbon
from refine_interaction_readability import add_radio_interaction_detail

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PROD=ROOT/"Assets"/"ProductionArt"
MANIFEST=PROD/"Docs"/"production_art_manifest.json"
TARGETS={"PR-001","PR-005","CS-009","EN-001","EN-007"}


def bilerp(a,b,c,d,u,v):
    # corners a=00, b=10, c=11, d=01
    return tuple(
        a[k]*(1-u)*(1-v)+b[k]*u*(1-v)+c[k]*u*v+d[k]*(1-u)*v
        for k in range(3)
    )


def tarp_surface(m:Mesh,corners,wet=False,damaged=False,seed=1):
    nx,nz=16,13; pts=[]; rnd=random.Random(seed)
    a,b,c,d=corners
    for iz in range(nz+1):
        v=iz/nz; row=[]
        for ix in range(nx+1):
            u=ix/nx; p=list(bilerp(a,b,c,d,u,v))
            center=math.sin(math.pi*u)*math.sin(math.pi*v)
            sag=(.18 if wet else .115)*center
            wrinkle=(.012*math.sin(u*math.pi*7+v*2.1+seed)+.007*math.sin(v*math.pi*5-u*1.4))*center
            p[1]+=-sag+wrinkle
            p[0]+=.010*math.sin(v*math.pi*4+seed*.3)*center
            p[2]+=.008*math.sin(u*math.pi*5+seed*.7)*center
            row.append(tuple(p))
        pts.append(row)
    for iz in range(nz):
        for ix in range(nx):
            u=(ix+.5)/nx; v=(iz+.5)/nz
            if damaged and .48<u<.69 and .31<v<.56: continue
            uv=((ix/nx,iz/nz),((ix+1)/nx,iz/nz),((ix+1)/nx,(iz+1)/nz),(ix/nx,(iz+1)/nz))
            m.quad(pts[iz][ix],pts[iz][ix+1],pts[iz+1][ix+1],pts[iz+1][ix],"Tarp",uv)
            m.quad(pts[iz+1][ix],pts[iz+1][ix+1],pts[iz][ix+1],pts[iz][ix],"Tarp",uv)
    # Rope-reinforced hem and metal grommets.
    for p,q in ((a,b),(b,c),(c,d),(d,a)): add_cylinder_between(m,p,q,.010,"Rope",6)
    for p in corners: add_torus(m,p,.032,.007,"Metal",12,4,"y")
    if damaged:
        # A long loose flap hangs from the torn centre instead of a perfect rectangular hole.
        flap=[(.04,.66,-.08),(.28,.62,-.04),(.30,.35,-.01),(.11,.42,-.03)]
        m.quad(flap[0],flap[1],flap[2],flap[3],"Cloth")
        m.quad(flap[3],flap[2],flap[1],flap[0],"Cloth")
    return pts


def build_tarp(variant:str)->Mesh:
    if variant=="folded":
        m=build_v1("PR-001",variant)
        add_box(m,(.16,.18,-.17),(.30,.018,.11),"Cloth",yaw=13,roll=-3)
        return m
    m=Mesh(); wet=variant=="wet"; damaged=variant=="damaged"
    corners=[(-1.02,.79,-.74),(1.06,.74,-.67),(1.00,.72,.78),(-1.08,.83,.72)]
    tarp_surface(m,corners,wet,damaged,920)
    anchors=[(-1.32,.03,-.98),(1.34,.03,-.93),(1.30,.03,1.00),(-1.35,.03,.96)]
    for i,(p,a) in enumerate(zip(corners,anchors)):
        add_cylinder_between(m,p,a,.008,"Rope",6)
        add_stick(m,(a[0],.01,a[2]),(a[0]+(.018 if i%2 else -.022),.23,a[2]),.017,"Wood",930+i,6,2)
    # Large field repair/patch gives the cloth history and scale seen in the mockups.
    if variant in ("placed","wet"):
        add_box(m,(-.38,.665,.18),(.34,.012,.20),"Cloth",yaw=-7,roll=1)
        add_cylinder_between(m,(-.54,.676,.09),(-.22,.675,.09),.004,"Rope",5)
    if wet:
        # Small pooled wet highlights use the existing Water material rather than a new shader family.
        m.quad((-.20,.617,-.07),(.18,.605,-.04),(.15,.601,.18),(-.18,.612,.15),"Water")
    return m


def build_radio(variant:str)->Mesh:
    m=Mesh(); active=variant=="active"; broken=variant=="broken"; repaired=variant=="repaired"
    # Clean rugged rescue-radio silhouette: body, rubber bumpers, front plate.
    add_box(m,(0,.40,0),(.82,.56,.32),"Char")
    add_box(m,(0,.40,-.173),(.76,.49,.026),"Metal")
    add_box(m,(0,.40,-.190),(.71,.44,.018),"Char")
    for x in (-.385,.385):
        add_box(m,(x,.40,-.01),(.055,.50,.35),"Rope")
        add_box(m,(x,.17,-.04),(.080,.080,.38),"Char")
        add_box(m,(x,.63,-.04),(.080,.080,.38),"Char")

    # Speaker with a readable grille, display, tuning dial and volume knob.
    speaker=(-.20,.39,-.214)
    add_cylinder_between(m,(speaker[0],speaker[1],-.197),(speaker[0],speaker[1],-.235),.155,"Char",20)
    add_torus(m,speaker,.158,.011,"Metal",22,5,"z")
    for i in range(-5,6):
        x=speaker[0]+i*.025; hh=math.sqrt(max(0,.137**2-(x-speaker[0])**2))*1.78
        add_box(m,(x,speaker[1],-.242),(.008,hh,.010),"Metal")
    add_box(m,(.205,.555,-.215),(.255,.082,.016),"Cloth")
    add_box(m,(.275,.555,-.227),(.070,.045,.010),"Fire" if active else "Char")
    for x,r in ((.19,.060),(.325,.047)):
        add_cylinder_between(m,(x,.33,-.196),(x,.33,-.250),r,"Metal",16)
        add_box(m,(x,.33,-.257),(.012,r*1.45,.010),"Char",roll=18 if x<.25 else -23)

    # Proper squared carrying handle and telescopic antenna.
    add_cylinder_between(m,(-.29,.69,.02),(-.29,.91,.02),.022,"Metal",8)
    add_cylinder_between(m,(.29,.69,.02),(.29,.91,.02),.022,"Metal",8)
    add_cylinder_between(m,(-.29,.91,.02),(.29,.91,.02),.024,"Metal",8)
    add_torus(m,(0,.91,.02),.12,.009,"Rope",16,4,"z")
    if broken:
        add_cylinder_between(m,(-.30,.67,.04),(-.30,1.05,.04),.013,"Metal",8)
        add_cylinder_between(m,(-.30,1.05,.04),(-.44,1.18,.08),.010,"Metal",7)
    else:
        add_cylinder_between(m,(-.30,.67,.04),(-.27,1.38,.04),.011,"Metal",8)
    # Small screws/fasteners break the blank front without adding noise.
    for x in (-.34,.34):
        for y in (.22,.60): add_cylinder_between(m,(x,y,-.204),(x,y,-.236),.014,"Metal",8)
    if repaired:
        add_box(m,(-.02,.18,-.229),(.40,.025,.014),"Cloth",yaw=-4,roll=0)
        add_box(m,(.06,.15,-.230),(.025,.18,.014),"Cloth",yaw=0,roll=7)
    if broken:
        add_box(m,(.05,.64,-.230),(.27,.018,.012),"Cloth",yaw=13,roll=0)
    # Reapply the established chunky controls/grip cues so visual polish never regresses VR interaction.
    add_radio_interaction_detail(m,variant)
    return m


def smooth_flame(m:Mesh,center,height,width,yaw,phase):
    a=math.radians(yaw); side=(-math.sin(a),0,math.cos(a)); forward=(math.cos(a),0,math.sin(a)); x,y,z=center
    pts=[]; widths=[]
    for i in range(7):
        t=i/6; bend=math.sin(t*math.pi*1.35+phase)*width*.18*(1-t*.45)
        p=(x+side[0]*bend+forward[0]*.025*t,y+height*t,z+side[2]*bend+forward[2]*.025*t)
        pts.append(p); widths.append(width*(1-t)**.72+.010)
    add_ribbon(m,pts,widths,"Fire")


def build_campfire()->Mesh:
    m=Mesh(); rnd=random.Random(940)
    for i in range(14):
        a=2*math.pi*i/14+rnd.uniform(-.04,.04); r=.325+rnd.uniform(-.012,.014)
        add_irregular_rock(m,(math.cos(a)*r,.040,math.sin(a)*r),(.082+rnd.uniform(-.008,.008),.046+rnd.uniform(-.006,.008),.076+rnd.uniform(-.008,.008)),950+i,"Stone",4,9)
    for a,b,s in [
        ((-.27,.10,-.15),(.27,.14,.15),970),((-.27,.13,.15),(.27,.10,-.15),971),
        ((-.23,.17,-.02),(.23,.18,.03),972),((-.17,.09,.06),(.18,.12,-.07),973),
    ]: add_stick(m,a,b,.042,"Char",s,9,3)
    for i in range(10):
        a=2*math.pi*i/10; add_irregular_rock(m,(math.cos(a)*.145,.065,math.sin(a)*.145),(.045,.016,.040),980+i,"Fire" if i%3==0 else "Char",3,7)
    # Five overlapping curved tongues; each is broad at the base and softly tapered.
    smooth_flame(m,(0,.145,0),.49,.22,0,.2)
    smooth_flame(m,(.055,.150,-.025),.39,.17,58,1.0)
    smooth_flame(m,(-.060,.150,.030),.34,.15,122,2.1)
    smooth_flame(m,(.015,.160,.060),.28,.12,28,2.8)
    smooth_flame(m,(-.015,.158,-.055),.25,.105,88,3.4)
    return m


def palm_frond(m:Mesh,crown,yaw,length,pitch,droop,seed):
    a=math.radians(yaw); dx,dz=math.cos(a),math.sin(a); x,y,z=crown; rnd=random.Random(seed)
    pts=[]; widths=[]
    for i in range(7):
        t=i/6; lift=math.sin(t*math.pi)*pitch; fall=droop*(t**1.7)
        side_wobble=math.sin(t*math.pi*1.3+seed*.31)*.045*(1-t)
        px=x+dx*length*t-dz*side_wobble; pz=z+dz*length*t+dx*side_wobble
        pts.append((px,y+lift-fall,pz)); widths.append(.30*(1-t)**.52+.025)
    add_ribbon(m,pts,widths,"Leaf")
    # Flexible midrib and alternating side leaflets broaden the crown in headset view.
    for p,q in zip(pts,pts[1:]): add_cylinder_between(m,p,q,.008,"Wood",5)
    for j,t in enumerate((.20,.32,.44,.56,.68,.79,.88)):
        idx=min(5,max(1,int(t*6))); base=pts[idx]; perp=(-dz,0,dx); half=(.34-.16*t)
        for sign in (-1,1):
            tip=(base[0]+perp[0]*half*sign,base[1]-.04-rnd.uniform(0,.045),base[2]+perp[2]*half*sign)
            add_ribbon(m,[base,tip],[.075,.012],"Leaf")


def build_palm(variant:str)->Mesh:
    m=Mesh(); young=variant=="young"; broken=variant=="broken"; h=2.85 if young else (3.10 if broken else 4.05)
    pts=[(0,.02,0),(.07,h*.31,.01),(-.05,h*.66,.07),(.11,h,.02)]
    radii=[.15 if not young else .115,.137 if not young else .10,.115 if not young else .085,.088 if not young else .066]
    for i in range(3): add_cylinder_between(m,pts[i],pts[i+1],radii[i],"Wood",10,radii[i+1])
    scars=7 if young else 10
    for i in range(scars):
        t=(i+1)/(scars+1); x=.04*math.sin(t*math.pi*1.6); z=.02+.04*math.sin(t*math.pi)
        add_torus(m,(x,h*t,z),radii[min(2,int(t*3))]*1.03,.008,"Char",14,4,"y")
    crown=pts[-1]; n=11 if young else (10 if broken else 17)
    for i in range(n):
        yaw=i*360/n+(i%3-1)*6; length=(.95 if young else 1.45)*(1+.09*math.sin(i*1.9)); pitch=.20+.08*(i%4); droop=.22+.07*(i%3)
        if broken and i in (2,6): length*=.58
        palm_frond(m,crown,yaw,length,pitch,droop,1000+i)
    # Upright spear leaves prevent the crown from reading as a flat umbrella.
    for yaw in (35,155,275):
        a=math.radians(yaw); x,y,z=crown
        pts2=[(x,y,z),(x+math.cos(a)*.22,y+.42,z+math.sin(a)*.22),(x+math.cos(a)*.40,y+.58,z+math.sin(a)*.40)]
        add_ribbon(m,pts2,[.20,.14,.025],"Leaf")
    if not young:
        for i,yaw in enumerate((15,100,190,285)):
            a=math.radians(yaw); add_irregular_rock(m,(crown[0]+math.cos(a)*.12,crown[1]-.11,crown[2]+math.sin(a)*.12),(.060,.070,.060),1060+i,"Wood",3,8)
    return m


def polish_wreck(variant:str)->Mesh:
    m=build_shipwreck(variant); scale=.82 if variant=="medium" else 1.0
    # Broken deck beams across the open hull communicate scale and keep the top edge from looking like a faceted shell.
    for i,(x,w) in enumerate(((-1.22,.72),(-.55,.96),(.15,1.02),(.82,.82))):
        add_stick(m,(x*scale,.62*scale,-w*scale),(x*scale,.65*scale,w*scale),.030*scale,"Wood",1100+i,8,3)
    # Torn sail/cloth caught between the broken mast and gunwale; deliberately irregular, not a clean rectangle.
    cloth=[(-.05*scale,1.52*scale,.07),(.62*scale,1.10*scale,.32*scale),(.52*scale,.71*scale,.44*scale),(.02*scale,.92*scale,.12)]
    m.quad(cloth[0],cloth[1],cloth[2],cloth[3],"Cloth"); m.quad(cloth[3],cloth[2],cloth[1],cloth[0],"Cloth")
    add_cylinder_between(m,cloth[0],cloth[1],.007,"Rope",5)
    add_cylinder_between(m,cloth[2],(.88*scale,.12,.67*scale),.008,"Rope",6)
    add_torus(m,(-.78*scale,.34*scale,-.54*scale),.18*scale,.010,"Rope",16,5,"z")
    # Dark wet/muddy contact patches visually seat the wreck in a storm beach scene.
    add_box(m,(.95*scale,.055,-.20*scale),(.72*scale,.020,.24*scale),"Mud",yaw=11,roll=0)
    return m


def build(aid,variant):
    if aid=="PR-001": return build_tarp(variant)
    if aid=="PR-005": return build_radio(variant)
    if aid=="CS-009": return build_campfire()
    if aid=="EN-001": return polish_wreck(variant)
    if aid=="EN-007": return build_palm(variant)
    raise KeyError(aid)


def main():
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8")); count=verts=faces=0; seen=set()
    for e in manifest:
        aid=str(e.get("asset_id","")); variant=str(e.get("variant","default"))
        if aid not in TARGETS or e.get("kind")!="mesh": continue
        mesh=build(aid,variant); write_obj(mesh,ROOT/e["path"])
        count+=1; verts+=len(mesh.verts); faces+=len(mesh.faces); seen.add((aid,variant))
    fam={a for a,_ in seen}
    if fam!=TARGETS: raise SystemExit(f"Mockup fidelity v3 missing families: {sorted(TARGETS-fam)}")
    print(f"Mockup fidelity v3: {count} meshes / {len(fam)} families / {verts} vertices / {faces} faces"); return 0

if __name__=="__main__": raise SystemExit(main())
