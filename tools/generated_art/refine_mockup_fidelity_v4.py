#!/usr/bin/env python3
"""Fourth visual fidelity pass for Project ØEN production art.

Driven by direct comparison between the generated OBJ review sheet and the approved
Project ØEN gameplay mockups / complete asset atlas. This pass targets the remaining
visible gap to stylized realism rather than broad coverage:

* PR-001 tarp: shared-vertex cloth grid, stronger asymmetric storm sag, reinforced
  corners, readable field patches and wet pooling without the procedural checker read;
* PR-005 radio: rebuilt as a rugged rescue/field receiver with clean rubber bumpers,
  recessed speaker, coherent controls, battery door, carrying grip and antenna while
  retaining enough bounded interaction geometry for Quest hand readability;
* CS-009 campfire: smaller irregular stone ring, crossed charred logs, ember bed and
  multiple curved flame ribbons instead of a monolithic low-poly flame crystal;
* EN-007 palm: denser layered crown, curved frond midribs, hanging leaflets, trunk scars
  and storm asymmetry while remaining Quest-conscious.

Canonical paths/GUIDs and the shared material vocabulary are preserved.
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
    write_obj,
)
from refine_mockup_fidelity_v2 import add_ribbon
from refine_mockup_fidelity_v3 import build as build_v3

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROD = ROOT / "Assets" / "ProjectOEN" / "ProductionArt"
MANIFEST = PROD / "Docs" / "production_art_manifest.json"
TARGETS = {"PR-001", "PR-005", "CS-009", "EN-007"}


def add_shared_quad(mesh: Mesh, ia: int, ib: int, ic: int, id_: int, mat: str) -> None:
    mesh.tri(ia, ib, ic, mat)
    mesh.tri(ia, ic, id_, mat)


def build_tarp(variant: str) -> Mesh:
    if variant == "folded":
        return build_v3("PR-001", variant)

    m = Mesh()
    wet = variant == "wet"
    damaged = variant == "damaged"
    nx, nz = 20, 15
    # Unequal corner heights/positions create the improvised hand-rigged silhouette
    # visible in the approved camp/storm mockups.
    c00 = (-1.10, .82, -.77)
    c10 = ( 1.04, .74, -.69)
    c11 = ( 1.00, .71,  .80)
    c01 = (-1.07, .86,  .73)

    def bilerp(u, v):
        return tuple(
            c00[k]*(1-u)*(1-v) + c10[k]*u*(1-v) + c11[k]*u*v + c01[k]*(1-u)*v
            for k in range(3)
        )

    grid: list[list[int]] = []
    positions: list[list[tuple[float,float,float]]] = []
    for iz in range(nz + 1):
        v = iz / nz
        row_ids=[]; row_pos=[]
        for ix in range(nx + 1):
            u = ix / nx
            x,y,z = bilerp(u,v)
            interior = math.sin(math.pi*u) * math.sin(math.pi*v)
            # Wet cloth carries deeper centre mass and a slight downwind skew.
            sag = (.185 if wet else .125) * interior
            wind = (.028 if wet else .018) * math.sin(v*math.pi) * u
            wrinkle = (
                .016*math.sin(u*math.pi*5.3 + v*1.9)
                + .009*math.sin(v*math.pi*4.2 - u*2.1)
                + .006*math.sin((u+v)*math.pi*3.0)
            ) * interior
            p=(x + wind, y - sag + wrinkle, z + .009*math.sin(u*math.pi*4.0)*interior)
            row_pos.append(p)
            row_ids.append(m.v(p,(u,v)))
        grid.append(row_ids); positions.append(row_pos)

    for iz in range(nz):
        for ix in range(nx):
            u=(ix+.5)/nx; v=(iz+.5)/nz
            # Torn centre is deliberately irregular rather than a clean rectangle.
            if damaged and ((.45<u<.67 and .30<v<.56) or (.58<u<.72 and .46<v<.66)):
                continue
            a,b,c,d=grid[iz][ix],grid[iz][ix+1],grid[iz+1][ix+1],grid[iz+1][ix]
            add_shared_quad(m,a,b,c,d,"Tarp")
            # reverse winding for two-sided cloth without duplicating the shared grid
            add_shared_quad(m,d,c,b,a,"Tarp")

    corners=[positions[0][0],positions[0][-1],positions[-1][-1],positions[-1][0]]
    anchors=[(-1.38,.03,-1.01),(1.34,.03,-.94),(1.31,.03,1.04),(-1.37,.03,.98)]
    for i,(p,a) in enumerate(zip(corners,anchors)):
        add_cylinder_between(m,p,a,.0085,"Rope",7)
        add_stick(m,(a[0],.01,a[2]),(a[0]+(.025 if i%2 else -.020),.24,a[2]+(.010 if i<2 else -.012)),.018,"Wood",1200+i,7,2)
        # proper grommet + wrapped corner reinforcement
        add_torus(m,p,.037,.008,"Metal",14,5,"y")
        add_torus(m,(p[0],p[1]-.006,p[2]),.052,.007,"Rope",14,4,"y")

    # Reinforced hem reads as a practical survival tarp rather than a flat sheet.
    for p,q in zip(corners,corners[1:]+corners[:1]):
        add_cylinder_between(m,p,q,.010,"Rope",7)

    if variant in ("placed","wet"):
        # Two non-identical field repairs, one cloth and one darker worn strip.
        add_box(m,(-.40,.652,.17),(.34,.014,.20),"Cloth",yaw=-8,roll=1)
        add_box(m,(.31,.625,-.21),(.22,.012,.10),"Char",yaw=19,roll=-2)
        add_cylinder_between(m,(-.55,.661,.07),(-.24,.657,.08),.004,"Rope",5)
    if wet:
        # Subtle pooling uses the existing water material; keep it broad and shallow.
        m.quad((-.22,.596,-.10),(.20,.590,-.06),(.16,.587,.18),(-.18,.594,.15),"Water")
    if damaged:
        # Hanging tear flaps provide a storm-damaged silhouette.
        add_ribbon(m,[(.04,.64,-.07),(.22,.56,-.04),(.29,.34,.01)],[.30,.22,.07],"Cloth")
        add_ribbon(m,[(.23,.57,.05),(.36,.47,.11),(.33,.26,.16)],[.22,.15,.05],"Cloth")
        add_cylinder_between(m,(.25,.56,.10),(.72,.09,.74),.007,"Rope",6)
    return m


def add_handle_grip(m: Mesh) -> None:
    # Rubber/rope-wrapped centre grip built from short cylinders instead of floating torus loops.
    y=.925; z=.015
    for i in range(9):
        x=-.14+i*.035
        add_cylinder_between(m,(x,y-.018,z),(x,y+.018,z),.030,"Rope",9)


def build_radio(variant: str) -> Mesh:
    m=Mesh(); active=variant=="active"; broken=variant=="broken"; repaired=variant=="repaired"
    # Main shell: slightly taller/narrower than V3, closer to the approved field-radio reference.
    add_box(m,(0,.405,0),(.78,.57,.30),"Char")
    add_box(m,(0,.405,-.164),(.724,.505,.028),"Metal")
    add_box(m,(0,.405,-.184),(.690,.470,.016),"Char")

    # Four compact rubber corner bumpers — readable, but not giant protruding fins.
    for x in (-.365,.365):
        for y in (.175,.635):
            add_box(m,(x,y,-.015),(.070,.095,.335),"Rope")
            add_box(m,(x,y,-.190),(.086,.105,.024),"Char")

    # Recessed speaker + protective ring + curved-ish grille approximation.
    sx,sy=-.205,.395
    add_cylinder_between(m,(sx,sy,-.173),(sx,sy,-.226),.158,"Char",24)
    add_torus(m,(sx,sy,-.226),.164,.012,"Metal",24,6,"z")
    for i in range(-6,7):
        x=sx+i*.022
        chord=math.sqrt(max(0,.142**2-(x-sx)**2))*1.85
        add_box(m,(x,sy,-.240),(.007,chord,.012),"Metal")

    # Green/amber frequency window and chunky controls like the atlas reference.
    add_box(m,(.195,.555,-.205),(.255,.080,.018),"Cloth")
    add_box(m,(.255,.555,-.219),(.088,.044,.012),"Fire" if active else "Char")
    # coarse display tick rail
    for i in range(6):
        x=.090+i*.036
        h=.044 if i in (0,3,5) else .030
        add_box(m,(x,.555,-.230),(.008,h,.010),"Metal")

    # Two tactile knobs + one guarded press button.
    for x,r in ((.190,.063),(.322,.050)):
        add_cylinder_between(m,(x,.335,-.190),(x,.335,-.260),r,"Metal",18)
        add_torus(m,(x,.335,-.258),r*.82,.008,"Rope",14,4,"z")
        add_box(m,(x,.335,-.272),(.010,r*1.30,.010),"Char",roll=18 if x<.25 else -23)
    add_cylinder_between(m,(.270,.235,-.195),(.270,.235,-.252),.028,"Metal",12)
    add_torus(m,(.270,.235,-.250),.045,.007,"Rope",12,4,"z")

    # Carry handle: two uprights, rigid top rail and wrapped centre grip.
    add_cylinder_between(m,(-.285,.690,.015),(-.285,.925,.015),.023,"Metal",10)
    add_cylinder_between(m,( .285,.690,.015),( .285,.925,.015),.023,"Metal",10)
    add_cylinder_between(m,(-.285,.925,.015),( .285,.925,.015),.025,"Metal",10)
    add_handle_grip(m)

    # Telescopic antenna with small collar rather than a floating spike.
    add_cylinder_between(m,(-.300,.665,.045),(-.292,.845,.045),.018,"Metal",9)
    add_torus(m,(-.292,.845,.045),.028,.006,"Rope",12,4,"y")
    if broken:
        add_cylinder_between(m,(-.292,.845,.045),(-.420,1.080,.090),.010,"Metal",8)
        add_box(m,(.05,.640,-.229),(.24,.018,.012),"Cloth",yaw=12,roll=0)
    else:
        add_cylinder_between(m,(-.292,.845,.045),(-.255,1.365,.045),.010,"Metal",8)

    # Battery/service panel and fasteners on the lower front establish plausible construction.
    add_box(m,(.065,.210,-.202),(.260,.115,.014),"Metal")
    for x in (-.045,.175):
        for y in (.175,.245): add_cylinder_between(m,(x,y,-.204),(x,y,-.232),.013,"Metal",9)

    # Side strap lugs + compact carrying strap preserve high interaction geometry delta
    # without reintroducing the old visual wedges.
    for side in (-1,1):
        x=side*.405
        add_torus(m,(x,.48,.02),.055,.010,"Metal",14,5,"x")
        add_cylinder_between(m,(x,.48,-.02),(x,.31,.10),.012,"Rope",7)
        add_cylinder_between(m,(x,.31,.10),(x,.14,.02),.012,"Rope",7)

    if repaired:
        add_box(m,(-.03,.175,-.222),(.36,.024,.014),"Cloth",yaw=-4,roll=0)
        add_box(m,(.060,.150,-.223),(.024,.17,.014),"Cloth",yaw=0,roll=7)
    if active:
        # Tiny status lamp, not a giant emissive slab.
        add_cylinder_between(m,(.330,.555,-.203),(.330,.555,-.244),.017,"Fire",10)
    return m


def smooth_flame(m: Mesh, center, height, width, yaw, phase):
    x,y,z=center; a=math.radians(yaw); side=(-math.sin(a),0,math.cos(a)); forward=(math.cos(a),0,math.sin(a))
    pts=[]; ids_left=[]; ids_right=[]
    for i in range(9):
        t=i/8
        bend=math.sin(t*math.pi*1.45+phase)*width*.18*(1-t*.35)
        px=x+side[0]*bend+forward[0]*.018*t
        pz=z+side[2]*bend+forward[2]*.018*t
        py=y+height*t
        w=(width*(1-t)**.78+.008)/2
        l=(px+side[0]*w,py,pz+side[2]*w); r=(px-side[0]*w,py,pz-side[2]*w)
        ids_left.append(m.v(l,(0,t))); ids_right.append(m.v(r,(1,t)))
    for i in range(8):
        add_shared_quad(m,ids_left[i],ids_right[i],ids_right[i+1],ids_left[i+1],"Fire")
        add_shared_quad(m,ids_right[i],ids_left[i],ids_left[i+1],ids_right[i+1],"Fire")


def build_campfire() -> Mesh:
    m=Mesh(); rnd=random.Random(1409)
    # Irregular but deliberately low profile ring, closer to the gameplay reference.
    for i in range(15):
        a=2*math.pi*i/15+rnd.uniform(-.035,.035); r=.315+rnd.uniform(-.015,.012)
        add_irregular_rock(m,(math.cos(a)*r,.038,math.sin(a)*r),(.075+rnd.uniform(-.008,.008),.043+rnd.uniform(-.005,.006),.070+rnd.uniform(-.008,.008)),1420+i,"Stone",4,9)
    # Crossed logs with different heights/angles and ember glow underneath.
    logs=[((-.27,.105,-.16),(.27,.145,.16),1450),((-.27,.138,.16),(.27,.105,-.16),1451),((-.23,.172,-.03),(.23,.183,.04),1452),((-.18,.090,.06),(.18,.120,-.08),1453)]
    for a,b,s in logs: add_stick(m,a,b,.040,"Char",s,10,4)
    for i in range(12):
        a=2*math.pi*i/12; rr=.135+.015*(i%2)
        add_irregular_rock(m,(math.cos(a)*rr,.060,math.sin(a)*rr),(.041,.014,.036),1470+i,"Fire" if i%3==0 else "Char",3,7)
    smooth_flame(m,(0,.142,0),.46,.21,0,.2)
    smooth_flame(m,(.052,.148,-.020),.37,.16,55,1.1)
    smooth_flame(m,(-.058,.149,.026),.31,.14,121,2.0)
    smooth_flame(m,(.012,.155,.058),.26,.11,27,2.8)
    smooth_flame(m,(-.018,.154,-.052),.23,.095,92,3.5)
    return m


def add_palm_frond(m: Mesh, crown, yaw, length, lift, droop, seed):
    rnd=random.Random(seed); a=math.radians(yaw); dx,dz=math.cos(a),math.sin(a); x,y,z=crown
    centre=[]
    for i in range(8):
        t=i/7
        sideways=math.sin(t*math.pi*1.3+seed*.19)*.035*(1-t)
        px=x+dx*length*t-dz*sideways
        pz=z+dz*length*t+dx*sideways
        py=y+math.sin(t*math.pi)*lift-droop*(t**1.65)
        centre.append((px,py,pz))
    # woody midrib follows the actual frond curve
    for p,q in zip(centre,centre[1:]): add_cylinder_between(m,p,q,.0075,"Wood",6)
    # broad central leaf strip with shared vertices
    left=[]; right=[]
    perp=(-dz,0,dx)
    for i,p in enumerate(centre):
        t=i/7; half=(.155*(1-t)**.48+.010)
        left.append(m.v((p[0]+perp[0]*half,p[1],p[2]+perp[2]*half),(0,t)))
        right.append(m.v((p[0]-perp[0]*half,p[1],p[2]-perp[2]*half),(1,t)))
    for i in range(7):
        add_shared_quad(m,left[i],right[i],right[i+1],left[i+1],"Leaf")
        add_shared_quad(m,right[i],left[i],left[i+1],right[i+1],"Leaf")
    # side leaflets create the layered tropical crown seen in the atlas.
    for j,t in enumerate((.18,.28,.38,.48,.58,.68,.77,.85,.92)):
        idx=min(6,max(1,int(t*7))); b=centre[idx]; span=(.32-.15*t)
        for sign in (-1,1):
            tip=(b[0]+perp[0]*span*sign,b[1]-.035-rnd.uniform(0,.035),b[2]+perp[2]*span*sign)
            add_ribbon(m,[b,tip],[.065,.012],"Leaf")


def build_palm(variant: str) -> Mesh:
    m=Mesh(); young=variant=="young"; broken=variant=="broken"
    h=2.8 if young else (3.05 if broken else 4.0)
    trunk=[(0,.02,0),(.075,h*.30,.012),(-.055,h*.64,.065),(.105,h,.018)]
    radii=[.145 if not young else .112,.132 if not young else .098,.112 if not young else .083,.085 if not young else .065]
    for i in range(3): add_cylinder_between(m,trunk[i],trunk[i+1],radii[i],"Wood",12,radii[i+1])
    scars=7 if young else 11
    for i in range(scars):
        t=(i+1)/(scars+1); x=.035*math.sin(t*math.pi*1.5); z=.018+.035*math.sin(t*math.pi)
        add_torus(m,(x,h*t,z),radii[min(2,int(t*3))]*1.02,.007,"Char",16,4,"y")
    crown=trunk[-1]
    n=12 if young else (11 if broken else 18)
    for i in range(n):
        yaw=i*360/n+(i%4-1.5)*5
        length=(.92 if young else 1.42)*(1+.08*math.sin(i*1.73))
        lift=.20+.06*(i%4); droop=.23+.055*(i%3)
        if broken and i in (2,6,9): length*=.60
        add_palm_frond(m,crown,yaw,length,lift,droop,1510+i)
    # upright spear leaves add vertical volume to the crown
    for yaw in (20,140,260):
        a=math.radians(yaw); x,y,z=crown
        add_ribbon(m,[(x,y,z),(x+math.cos(a)*.20,y+.40,z+math.sin(a)*.20),(x+math.cos(a)*.38,y+.56,z+math.sin(a)*.38)],[.18,.12,.018],"Leaf")
    if not young:
        for i,yaw in enumerate((15,105,195,285)):
            a=math.radians(yaw)
            add_irregular_rock(m,(crown[0]+math.cos(a)*.115,crown[1]-.105,crown[2]+math.sin(a)*.115),(.058,.067,.058),1560+i,"Wood",3,8)
    if broken:
        add_stick(m,(.07,h*.68,.03),(.56,h*.90,.18),.036,"Wood",1580,8,3)
    return m


def build(asset_id: str, variant: str) -> Mesh:
    if asset_id == "PR-001": return build_tarp(variant)
    if asset_id == "PR-005": return build_radio(variant)
    if asset_id == "CS-009": return build_campfire()
    if asset_id == "EN-007": return build_palm(variant)
    raise KeyError(asset_id)


def main() -> int:
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8")); count=verts=faces=0; seen=set()
    for e in manifest:
        aid=str(e.get("asset_id","")); variant=str(e.get("variant","default"))
        if aid not in TARGETS or e.get("kind")!="mesh": continue
        mesh=build(aid,variant); write_obj(mesh,ROOT/e["path"])
        count+=1; verts+=len(mesh.verts); faces+=len(mesh.faces); seen.add((aid,variant))
    fam={a for a,_ in seen}
    if fam != TARGETS:
        raise SystemExit(f"Mockup fidelity v4 missing families: {sorted(TARGETS-fam)}")
    print(f"Mockup fidelity v4: {count} meshes / {len(fam)} families / {verts} vertices / {faces} faces")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
