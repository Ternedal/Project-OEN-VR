#!/usr/bin/env python3
"""Fifth Project ØEN mockup-fidelity pass.

Directly addresses the largest remaining mismatches found by comparing the actual OBJ
review sheet against the approved gameplay mockups and complete asset atlas:

* PR-005 repaired: retain the bright radio-state cue required by VR/readability QA.
* CS-001..005: replace the incorrect A-frame/tent language with the canonical
  rectangular post-and-beam survival shelter shown in the atlas: platform foundation,
  upright frame, blue tarp roof, storm damage and a visibly reinforced repair state.
* CS-011..014: replace the squat/tripod signal shape with a tall, narrow, cross-braced
  timber lattice tower, top platform, signal flag and active fire basket.
* EN-001: rebuild wreckage as an open, ribbed, storm-broken wooden hull with separate
  plank courses, dark weathering, interior deck fragments, rails, mast and debris.
* EN-017: rebuild the cooking corner around a believable lashed tripod, hanging pot,
  compact ember bed and variant-specific camp clutter.

CS-015 is intentionally NOT touched: the dedicated signal-finale refinement owns that
state and has exact geometry/provenance QA. All assets keep canonical paths/GUIDs and
use only the existing Project ØEN shared material vocabulary.
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
from refine_mockup_fidelity_v4 import build as build_v4, add_shared_quad

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROD = ROOT / "Assets" / "ProjectOEN" / "ProductionArt"
MANIFEST = PROD / "Docs" / "production_art_manifest.json"
TARGETS = {
    "PR-005",
    "CS-001", "CS-002", "CS-003", "CS-004", "CS-005",
    "CS-011", "CS-012", "CS-013", "CS-014",
    "EN-001", "EN-017",
}


def add_lashing(m: Mesh, p, radius=.052, axis="z") -> None:
    add_torus(m,p,radius,.008,"Rope",12,4,axis)
    add_torus(m,(p[0]+.006,p[1]-.004,p[2]+.004),radius*.92,.006,"Rope",12,4,axis)


def add_shared_cloth_panel(
    m: Mesh,
    corners,
    material="Tarp",
    nx=12,
    nz=10,
    sag=.045,
    damaged=False,
    seed=1,
):
    c00,c10,c11,c01=corners
    grid=[]; pos=[]
    for iz in range(nz+1):
        v=iz/nz; ids=[]; row=[]
        for ix in range(nx+1):
            u=ix/nx
            p=[
                c00[k]*(1-u)*(1-v)+c10[k]*u*(1-v)+c11[k]*u*v+c01[k]*(1-u)*v
                for k in range(3)
            ]
            interior=math.sin(math.pi*u)*math.sin(math.pi*v)
            p[1]-=sag*interior
            p[0]+=.010*math.sin(v*math.pi*3.2+seed)*interior
            p[2]+=.009*math.sin(u*math.pi*4.1+seed*.7)*interior
            q=tuple(p); row.append(q); ids.append(m.v(q,(u,v)))
        grid.append(ids); pos.append(row)
    for iz in range(nz):
        for ix in range(nx):
            u=(ix+.5)/nx; v=(iz+.5)/nz
            # One ragged storm tear, never a clean punched rectangle.
            if damaged and ((.54<u<.73 and .25<v<.53) or (.62<u<.79 and .46<v<.67)):
                continue
            a,b,c,d=grid[iz][ix],grid[iz][ix+1],grid[iz+1][ix+1],grid[iz+1][ix]
            add_shared_quad(m,a,b,c,d,material)
            add_shared_quad(m,d,c,b,a,material)
    corners_out=[pos[0][0],pos[0][-1],pos[-1][-1],pos[-1][0]]
    for p,q in zip(corners_out,corners_out[1:]+corners_out[:1]):
        add_cylinder_between(m,p,q,.008,"Rope",6)
    return corners_out


# ---------------------------------------------------------------------------
# Radio state compatibility fix
# ---------------------------------------------------------------------------

def build_radio(variant: str) -> Mesh:
    m=build_v4("PR-005",variant)
    if variant == "repaired":
        # V4 deliberately cleaned up the old oversized glow geometry, but the repaired
        # state still needs a bounded bright status cue. A small amber service lamp is
        # both visually plausible and preserves the established interaction contract.
        add_cylinder_between(m,(.330,.555,-.203),(.330,.555,-.244),.017,"Fire",10)
    return m


# ---------------------------------------------------------------------------
# Canonical rectangular survival shelter
# ---------------------------------------------------------------------------
SHELTER_W=1.82
SHELTER_D=1.42
ZF=-SHELTER_D/2
ZB=SHELTER_D/2
XL=-SHELTER_W/2
XR=SHELTER_W/2


def add_foundation(m: Mesh, damaged=False) -> None:
    # Raised slatted platform gives the shelter a physical, boardgame-clear footprint.
    for i in range(12):
        x=XL+.09+i*(SHELTER_W-.18)/11
        yaw=(-1.6 if i%3==0 else (1.0 if i%4==0 else 0))
        add_box(m,(x,.085,0),(.105,.070,SHELTER_D-.12),"Wood",yaw=yaw)
    # Four dark ground runners plus irregular stone footings.
    for z in (ZF+.05,ZB-.05):
        add_stick(m,(XL-.03,.055,z),(XR+.03,.055,z),.040,"Char",1700+int((z+1)*10),8,4)
    for i,(x,z) in enumerate(((XL,ZF),(XR,ZF),(XL,ZB),(XR,ZB))):
        add_irregular_rock(m,(x,.035,z),(.16,.085,.14),1710+i,"Stone",4,9)
    if damaged:
        add_box(m,(.31,.155,-.09),(.55,.045,.10),"Char",yaw=19,roll=7)


def add_frame(m: Mesh, stage: int) -> None:
    # Four upright posts. In the damaged state the front-right post is visibly snapped.
    corners=[(XL,ZF),(XR,ZF),(XL,ZB),(XR,ZB)]
    tops={
        (XL,ZF):(XL-.02,1.52,ZF),
        (XR,ZF):(XR+.02,1.46,ZF),
        (XL,ZB):(XL-.02,1.47,ZB),
        (XR,ZB):(XR+.02,1.40,ZB),
    }
    for i,(x,z) in enumerate(corners):
        top=tops[(x,z)]
        if stage==4 and x==XR and z==ZF:
            add_stick(m,(x,.12,z),(x-.06,.74,z+.02),.050,"Wood",1730+i,9,4)
            add_stick(m,(x+.05,.69,z+.04),(x-.22,1.31,z+.08),.043,"Wood",1750+i,8,3)
        else:
            add_stick(m,(x,.12,z),top,.050,"Wood",1730+i,9,4)
        add_lashing(m,(x,.30,z),.050,"z")

    # Top rails create the rectangular/post-and-beam language from the asset atlas.
    for a,b,s in [
        ((XL,1.51,ZF),(XR,1.45,ZF),1760),
        ((XL,1.46,ZB),(XR,1.39,ZB),1761),
        ((XL,1.50,ZF),(XL,1.45,ZB),1762),
        ((XR,1.44,ZF),(XR,1.38,ZB),1763),
    ]:
        add_stick(m,a,b,.041,"Wood",s,8,3)

    # Side X-braces: fewer/larger pieces than the old procedural cage.
    if stage>=2:
        braces=[
            ((XL,.28,ZF),(XL,1.31,ZB),1770),((XL,.28,ZB),(XL,1.30,ZF),1771),
            ((XR,.28,ZF),(XR,1.23,ZB),1772),((XR,.28,ZB),(XR,1.26,ZF),1773),
        ]
        for idx,(a,b,s) in enumerate(braces):
            if stage==4 and idx==2:
                add_stick(m,a,(XR-.04,.78,.04),.027,"Wood",s,7,3)
            else:
                add_stick(m,a,b,.027,"Wood",s,7,3)

    # Strong visible lashings at the four roof joints.
    for p in ((XL,1.48,ZF),(XR,1.42,ZF),(XL,1.43,ZB),(XR,1.37,ZB)):
        add_lashing(m,p,.058,"z")


def add_shelter_roof(m: Mesh, stage: int) -> None:
    damaged=stage==4
    # One shallow single-slope tarp roof, not an A-frame tent.
    corners=[
        (XL-.13,1.59,ZF-.13),
        (XR+.13,1.52,ZF-.13),
        (XR+.13,1.36 if damaged else 1.43,ZB+.13),
        (XL-.13,1.48,ZB+.13),
    ]
    roof=add_shared_cloth_panel(m,corners,"Tarp",15,11,.055 if damaged else .040,damaged,1790+stage)
    # Short guys at the outer tarp corners keep the shelter visually hand-rigged.
    anchors=[(XL-.30,.04,ZF-.28),(XR+.30,.04,ZF-.28),(XR+.28,.04,ZB+.27),(XL-.28,.04,ZB+.27)]
    for i,(p,a) in enumerate(zip(roof,anchors)):
        add_cylinder_between(m,p,a,.007,"Rope",6)
        add_stick(m,(a[0],.01,a[2]),(a[0]+(.018 if i%2 else -.018),.20,a[2]),.015,"Wood",1810+i,6,2)

    # Back windbreak makes the usable shelter look lived-in while preserving openness.
    back=[(XL+.10,.24,ZB-.03),(XR-.10,.24,ZB-.03),(XR-.11,1.24,ZB-.03),(XL+.09,1.30,ZB-.03)]
    add_shared_cloth_panel(m,back,"Cloth",8,6,.018,False,1820+stage)

    if damaged:
        add_ribbon(m,[(.18,1.34,.10),(.34,1.08,.15),(.29,.76,.20)],[.36,.25,.08],"Cloth")
        add_cylinder_between(m,(.45,1.30,ZB+.12),(.72,.16,ZB+.33),.007,"Rope",6)
    elif stage==5:
        # Two large visible repairs + diagonal frame reinforcement.
        add_box(m,(-.28,1.475,-.12),(.42,.015,.23),"Cloth",yaw=8,roll=-2)
        add_box(m,(.36,1.423,.24),(.29,.014,.17),"Char",yaw=-13,roll=2)
        add_stick(m,(XR-.02,.20,ZF+.02),(XL+.12,1.34,ZF+.03),.032,"Wood",1840,8,3)
        add_stick(m,(XL+.02,.18,ZB-.02),(XR-.14,1.24,ZB-.03),.030,"Wood",1841,8,3)
        add_lashing(m,(.08,1.22,ZF+.03),.047,"z")
        add_lashing(m,(-.06,1.18,ZB-.03),.047,"z")


def build_shelter(stage: int) -> Mesh:
    m=Mesh()
    add_foundation(m,stage==4)
    if stage>=2:
        add_frame(m,stage)
    if stage>=3:
        add_shelter_roof(m,stage)
    # Stage 1 stays a clearly readable foundation; extra rope/wood gives VR-scale detail.
    if stage==1:
        add_torus(m,(-.55,.17,-.42),.16,.012,"Rope",18,5,"y")
        add_stick(m,(-.70,.16,.43),(.57,.18,.38),.035,"Wood",1850,8,4)
    return m


# ---------------------------------------------------------------------------
# Tall timber signal tower progression
# ---------------------------------------------------------------------------

def tower_corner(level_y: float, sign_x: int, sign_z: int, top_y=2.34):
    # Tower tapers from a wide square base to a narrow top platform.
    t=max(0.0,min(1.0,level_y/top_y))
    half=.57*(1-t)+.22*t
    return (sign_x*half,level_y,sign_z*half)


def add_square_ring(m: Mesh, y: float, seed: int, radius=.030) -> None:
    pts=[tower_corner(y,-1,-1),tower_corner(y,1,-1),tower_corner(y,1,1),tower_corner(y,-1,1)]
    for i in range(4): add_stick(m,pts[i],pts[(i+1)%4],radius,"Wood",seed+i,7,3)


def add_tower_braces(m: Mesh, y0: float, y1: float, seed: int) -> None:
    # One X on every face of the tower at each bay.
    pairs=[
        (tower_corner(y0,-1,-1),tower_corner(y1,1,-1)),
        (tower_corner(y0,1,-1),tower_corner(y1,-1,-1)),
        (tower_corner(y0,1,1),tower_corner(y1,-1,1)),
        (tower_corner(y0,-1,1),tower_corner(y1,1,1)),
        (tower_corner(y0,-1,-1),tower_corner(y1,-1,1)),
        (tower_corner(y0,-1,1),tower_corner(y1,-1,-1)),
        (tower_corner(y0,1,-1),tower_corner(y1,1,1)),
        (tower_corner(y0,1,1),tower_corner(y1,1,-1)),
    ]
    for i,(a,b) in enumerate(pairs): add_stick(m,a,b,.020,"Wood",seed+i,7,3)


def add_signal_flame(m: Mesh, center, height, width, yaw, phase):
    x,y,z=center; a=math.radians(yaw); side=(-math.sin(a),0,math.cos(a)); forward=(math.cos(a),0,math.sin(a))
    pts=[]
    for i in range(7):
        t=i/6
        bend=math.sin(t*math.pi*1.35+phase)*width*.18*(1-t*.35)
        pts.append((x+side[0]*bend+forward[0]*.018*t,y+height*t,z+side[2]*bend+forward[2]*.018*t))
    add_ribbon(m,pts,[width*(1-t/6)**.75+.012 for t in range(7)],"Fire")


def build_beacon(stage: int) -> Mesh:
    m=Mesh(); top_y=2.34
    # Base is visible in every stage.
    base=[tower_corner(.06,-1,-1),tower_corner(.06,1,-1),tower_corner(.06,1,1),tower_corner(.06,-1,1)]
    for i,p in enumerate(base):
        add_irregular_rock(m,(p[0],.035,p[2]),(.15,.08,.14),1900+i,"Stone",4,8)
        add_lashing(m,(p[0],.12,p[2]),.047,"z")
    add_square_ring(m,.12,1910,.035)

    height={1:.58,2:1.36,3:top_y,4:top_y}[stage]
    # Four structural legs made from bounded segments so the lattice remains legible.
    levels=[.12]
    for y in (.58,1.10,1.62,2.08,top_y):
        if y<=height+.001: levels.append(y)
    if levels[-1] < height-.001: levels.append(height)
    for sx,sz in ((-1,-1),(1,-1),(1,1),(-1,1)):
        for idx,(y0,y1) in enumerate(zip(levels,levels[1:])):
            add_stick(m,tower_corner(y0,sx,sz),tower_corner(y1,sx,sz),.036,"Wood",1920+idx+sx*7+sz*13,8,3)
    for idx,y in enumerate(levels[1:]):
        add_square_ring(m,y,1950+idx*10,.026)
        add_tower_braces(m,levels[idx],y,1990+idx*20)

    # Strong rope wraps at the principal levels.
    for y in levels[1:]:
        for sx,sz in ((-1,-1),(1,-1),(1,1),(-1,1)):
            add_lashing(m,tower_corner(y,sx,sz),.038,"z")

    if stage>=3:
        # Slatted top platform + central metal fire basket.
        for i,x in enumerate((-.28,-.14,0,.14,.28)):
            add_stick(m,(x,2.30,-.31),(x,2.30,.31),.030,"Wood",2100+i,7,2)
        add_cylinder_between(m,(0,2.32,0),(0,2.46,0),.215,"Metal",16,.185)
        add_torus(m,(0,2.46,0),.198,.012,"Metal",18,5,"y")
        # Tall signal pole and green accent flag (Leaf is the existing green shared material).
        add_stick(m,(.26,2.23,.02),(.27,3.02,.02),.022,"Wood",2120,7,3)
        flag=[(.29,2.93,.02),(.88,2.83,.02),(.82,2.40,.02),(.29,2.51,.02)]
        m.quad(flag[0],flag[1],flag[2],flag[3],"Leaf")
        m.quad(flag[3],flag[2],flag[1],flag[0],"Leaf")
        add_cylinder_between(m,flag[0],flag[1],.006,"Rope",5)
        # Guys keep the tall silhouette credible.
        for i,(p,a) in enumerate([
            ((-.20,2.25,-.20),(-.98,.03,-.90)),
            ((.20,2.25,-.20),(.98,.03,-.90)),
            ((0,2.25,.22),(0,.03,1.08)),
        ]):
            add_cylinder_between(m,p,a,.007,"Rope",6)
            add_stick(m,(a[0],.01,a[2]),(a[0]+.015,.20,a[2]),.015,"Wood",2140+i,6,2)

    if stage==4:
        add_signal_flame(m,(0,2.44,0),.72,.27,0,.2)
        add_signal_flame(m,(.05,2.45,-.02),.52,.20,64,1.1)
        add_signal_flame(m,(-.06,2.45,.03),.43,.17,126,2.0)
        # Ember bed inside the basket makes the active state glow at a distance.
        for i in range(7):
            a=2*math.pi*i/7
            add_irregular_rock(m,(math.cos(a)*.11,2.43,math.sin(a)*.11),(.035,.014,.030),2160+i,"Fire",3,7)
    return m


# ---------------------------------------------------------------------------
# Open, ribbed shipwreck hull
# ---------------------------------------------------------------------------

def hull_width(xn: float) -> float:
    # xn -1..1, full amidships and sharply tapered at bow/stern.
    return .18 + .86*(max(0.0,1.0-abs(xn)**1.65)**.55)


def build_wreck(variant: str) -> Mesh:
    m=Mesh(); scale=.82 if variant=="medium" else 1.0
    stations=11
    xs=[(-2.15+4.10*i/(stations-1))*scale for i in range(stations)]
    xnorm=[-1+2*i/(stations-1) for i in range(stations)]
    widths=[hull_width(n)*scale for n in xnorm]
    courses=[(.12,.18),(.26,.33),(.41,.48),(.57,.62),(.72,.73)]  # y, width multiplier-ish handled below

    # Separate plank courses with small gaps make this read as a wrecked boat, not a brown solid.
    for side in (-1,1):
        for ci,(y0,y1) in enumerate(courses):
            mat="Char" if ci in (1,4) else "Wood"
            for i in range(stations-1):
                n0=xnorm[i]; n1=xnorm[i+1]
                # storm-created missing upper sections
                if ci>=3 and (i+ci+(0 if side>0 else 1))%5==0:
                    continue
                w0=widths[i]*(.36+.72*(y0/.72))
                w1=widths[i+1]*(.36+.72*(y0/.72))
                wt0=widths[i]*(.36+.72*(y1/.72))
                wt1=widths[i+1]*(.36+.72*(y1/.72))
                a=(xs[i],y0*scale,side*w0); b=(xs[i+1],y0*scale,side*w1)
                c=(xs[i+1],y1*scale,side*wt1); d=(xs[i],y1*scale,side*wt0)
                m.quad(a,b,c,d,mat)
                m.quad(d,c,b,a,mat)

    # Prominent ribs continue above the surviving hull skin.
    for i in range(1,stations-1):
        x=xs[i]; w=widths[i]
        bottom=(x,.08,0)
        for side in (-1,1):
            p1=(x,.28*scale,side*w*.58)
            p2=(x,.62*scale,side*w*.95)
            p3=(x,(.83+.07*(i%2))*scale,side*w*1.03)
            add_cylinder_between(m,bottom,p1,.026*scale,"Wood",8)
            add_cylinder_between(m,p1,p2,.024*scale,"Wood",8)
            add_cylinder_between(m,p2,p3,.022*scale,"Char" if i%3==0 else "Wood",8)

    # Keel, deck beams and broken gunwales establish an open interior.
    add_stick(m,(xs[0]+.08,.075,0),(xs[-1]-.08,.08,0),.050*scale,"Char",2200,9,5)
    for i in range(2,stations-2,2):
        x=xs[i]; w=widths[i]*.82
        add_stick(m,(x,.57*scale,-w),(x,.60*scale,w),.030*scale,"Wood",2210+i,8,3)
    for side in (-1,1):
        add_stick(m,(xs[1],.73*scale,side*widths[1]*.90),(xs[-2],.70*scale,side*widths[-2]*.90),.032*scale,"Char",2230+(1 if side>0 else 0),8,5)

    # Broken stern cabin/deckhouse fragment: dark panels, missing wall and leaning rail.
    add_box(m,(-1.15*scale,.80*scale,.18*scale),(.68*scale,.50*scale,.055*scale),"Char",yaw=-3,roll=4)
    add_box(m,(-1.40*scale,.72*scale,-.25*scale),(.46*scale,.38*scale,.050*scale),"Wood",yaw=11,roll=-7)
    add_stick(m,(-1.38*scale,.98*scale,-.44*scale),(-.74*scale,.92*scale,-.41*scale),.024*scale,"Metal",2240,7,3)
    add_stick(m,(-1.37*scale,.98*scale,.43*scale),(-.90*scale,.88*scale,.48*scale),.022*scale,"Metal",2241,7,3)

    # Broken mast + torn rope and sail remnant.
    add_stick(m,(-.35*scale,.16,0),(.22*scale,1.65*scale,.10*scale),.045*scale,"Wood",2250,8,4)
    add_cylinder_between(m,(.08*scale,1.32*scale,.07*scale),(.70*scale,.72*scale,.58*scale),.008,"Rope",6)
    add_ribbon(m,[(.06*scale,1.31*scale,.07*scale),(.46*scale,1.08*scale,.29*scale),(.56*scale,.76*scale,.43*scale)],[.34*scale,.25*scale,.08*scale],"Cloth")
    add_torus(m,(-.62*scale,.32*scale,-.50*scale),.17*scale,.010,"Rope",16,5,"z")
    add_torus(m,(.42*scale,.48*scale,.54*scale),.105*scale,.008,"Metal",14,4,"z")

    # Scattered detached boards visually merge the wreck into the storm beach.
    debris=[
        ((1.70,.065,-.82),(.72,.045,.09),-31,6),
        ((1.30,.055,.92),(.61,.040,.08),28,-5),
        ((-1.72,.060,.82),(.66,.042,.085),39,7),
        ((.82,.050,-1.00),(.52,.038,.075),-14,-4),
    ]
    for i,(c,s,yaw,roll) in enumerate(debris):
        add_box(m,(c[0]*scale,c[1],c[2]*scale),(s[0]*scale,s[1],s[2]*scale),"Wood" if i%2 else "Char",yaw=yaw,roll=roll)
    return m


# ---------------------------------------------------------------------------
# Cooking corner
# ---------------------------------------------------------------------------

def add_pot(m: Mesh) -> None:
    # Tapered metal body + rim + side handle; hangs at useful VR hand height.
    add_cylinder_between(m,(0,.42,0),(0,.69,0),.205,"Metal",18,.185)
    add_torus(m,(0,.69,0),.205,.010,"Metal",18,5,"y")
    add_torus(m,(0,.58,0),.275,.009,"Metal",18,4,"z")
    add_box(m,(0,.71,0),(.12,.045,.12),"Char",yaw=8)


def build_cooking(variant: str) -> Mesh:
    m=Mesh(); apex=(0,1.34,0)
    feet=[(-.57,.025,-.37),(.57,.025,-.37),(0,.025,.60)]
    for i,p in enumerate(feet):
        add_stick(m,p,apex,.037,"Wood",2300+i,9,4)
    # Lashed tripod apex and pot hanger.
    add_lashing(m,(0,1.28,0),.075,"y")
    add_lashing(m,(.015,1.33,.01),.062,"z")
    add_cylinder_between(m,(0,1.25,0),(0,.74,0),.008,"Rope",7)
    add_pot(m)

    # Tiny stone/ember fire directly under pot; much smaller than the standalone campfire.
    for i in range(8):
        a=2*math.pi*i/8; r=.24
        add_irregular_rock(m,(math.cos(a)*r,.035,math.sin(a)*r),(.070,.040,.062),2320+i,"Stone",3,7)
    for i,(a,b) in enumerate([
        ((-.18,.085,-.10),(.18,.105,.10)),
        ((-.17,.100,.11),(.17,.080,-.11)),
        ((-.12,.120,0),(.13,.125,.02)),
    ]): add_stick(m,a,b,.026,"Char",2340+i,7,2)
    for i in range(5):
        a=2*math.pi*i/5
        add_irregular_rock(m,(math.cos(a)*.10,.070,math.sin(a)*.10),(.032,.013,.028),2350+i,"Fire",3,6)

    # A horizontal utility rail supports utensils / drying cloth.
    add_stick(m,(-.44,.92,-.24),(.44,.92,-.24),.018,"Wood",2360,7,3)
    add_cylinder_between(m,(-.28,.92,-.24),(-.28,.55,-.25),.006,"Rope",5)
    add_cylinder_between(m,(.25,.92,-.24),(.25,.62,-.25),.006,"Rope",5)

    if variant=="crate":
        add_box(m,(.54,.16,.34),(.47,.30,.38),"Wood",yaw=-11)
        add_box(m,(.54,.32,.34),(.50,.035,.40),"Char",yaw=-11)
        add_torus(m,(.54,.35,.15),.075,.008,"Rope",12,4,"z")
    elif variant=="utensils":
        for i,(x,mat) in enumerate(((-.30,"Metal"),(-.19,"Wood"),(.20,"Metal"),(.31,"Wood"))):
            add_stick(m,(x,.55,-.25),(x+.04,.28,-.27),.008 if mat=="Metal" else .010,mat,2380+i,6,2)
        add_box(m,(.46,.085,.31),(.30,.040,.22),"Cloth",yaw=18,roll=-2)
    else:  # pot-focused review state
        add_box(m,(-.47,.055,.31),(.30,.026,.17),"Cloth",yaw=-16,roll=1)
        add_torus(m,(.42,.055,.25),.14,.010,"Rope",16,5,"y")
    return m


# ---------------------------------------------------------------------------
# Dispatch / write
# ---------------------------------------------------------------------------

def build(asset_id: str, variant: str) -> Mesh:
    if asset_id=="PR-005": return build_radio(variant)
    if asset_id.startswith("CS-"):
        n=int(asset_id.split("-")[1])
        if 1<=n<=5: return build_shelter(n)
        if 11<=n<=14: return build_beacon(n-10)
    if asset_id=="EN-001": return build_wreck(variant)
    if asset_id=="EN-017": return build_cooking(variant)
    raise KeyError(asset_id)


def main() -> int:
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8")); count=verts=faces=0; seen=set()
    for e in manifest:
        aid=str(e.get("asset_id","")); variant=str(e.get("variant","default"))
        if aid not in TARGETS or e.get("kind")!="mesh": continue
        mesh=build(aid,variant); write_obj(mesh,ROOT/e["path"])
        count+=1; verts+=len(mesh.verts); faces+=len(mesh.faces); seen.add((aid,variant))
    families={a for a,_ in seen}
    if families != TARGETS:
        raise SystemExit(f"Mockup fidelity v5 coverage mismatch: missing={sorted(TARGETS-families)} extra={sorted(families-TARGETS)}")
    print(f"Mockup fidelity v5: {count} meshes / {len(families)} families / {verts} vertices / {faces} faces")
    print("Replaced A-frame shelter language, rebuilt tall lattice signal tower, open wreck hull and cooking tripod; restored repaired-radio bright cue")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
