#!/usr/bin/env python3
"""Second mockup-fidelity pass for the visual outliers found by actual OBJ review.

The first visual review proved that structural QA was not enough. This pass replaces
only the most obvious silhouette misses seen in the generated review sheet:

- CS-003..005: readable A-frame shelter instead of a brace-heavy stick cage;
- CS-009: smaller natural fire ring with layered, curved flame tongues;
- CS-014: clean lashed signal tripod/tower with platform, basket and flag;
- EN-001: recognisable broken hull rather than an undifferentiated plank lattice;
- EN-007: bent tapered palm with a broad storm-shaped crown;
- EN-017: compact tripod cooking station instead of an oversized rope-loop silhouette.

The implementation stays deterministic, shared-material-only and Quest-conscious.
Canonical paths/GUIDs remain unchanged because only OBJ contents are replaced.
"""
from __future__ import annotations

import json
import math
import random
from pathlib import Path

from refine_mockup_fidelity import (
    Mesh,
    add_box,
    add_cloth_panel,
    add_cylinder_between,
    add_irregular_rock,
    add_stick,
    add_torus,
    write_obj,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROD = ROOT / "Assets" / "ProjectOEN" / "ProductionArt"
MANIFEST = PROD / "Docs" / "production_art_manifest.json"
TARGETS = {"CS-003", "CS-004", "CS-005", "CS-009", "CS-014", "EN-001", "EN-007", "EN-017"}


def add_ribbon(mesh: Mesh, points, widths, mat: str) -> None:
    """Create a tapered strip through 3D points without exposing a boxy silhouette."""
    left=[]; right=[]
    for i,p in enumerate(points):
        prev=points[max(0,i-1)]; nxt=points[min(len(points)-1,i+1)]
        dx=nxt[0]-prev[0]; dz=nxt[2]-prev[2]; ln=math.hypot(dx,dz) or 1.0
        px=-dz/ln; pz=dx/ln; w=widths[i]/2
        left.append((p[0]+px*w,p[1],p[2]+pz*w))
        right.append((p[0]-px*w,p[1],p[2]-pz*w))
    for i in range(len(points)-1):
        mesh.quad(left[i],right[i],right[i+1],left[i+1],mat,((0,0),(1,0),(1,1),(0,1)))
        # Back face keeps thin cloth/leaves visible from both headset sides.
        mesh.quad(right[i],left[i],left[i+1],right[i+1],mat,((0,0),(1,0),(1,1),(0,1)))


def add_flame_tongue(mesh: Mesh, center, height: float, width: float, yaw: float, bend: float = .08) -> None:
    a=math.radians(yaw); sx=math.cos(a); sz=math.sin(a)
    x,y,z=center
    pts=[
        (x,y,z),
        (x+sx*bend*.25,y+height*.28,z+sz*bend*.25),
        (x-sx*bend*.35,y+height*.58,z-sz*bend*.35),
        (x+sx*bend,y+height*.83,z+sz*bend),
        (x-sx*bend*.15,y+height,z-sz*bend*.15),
    ]
    add_ribbon(mesh,pts,[width,width*.82,width*.58,width*.32,.015],"Fire")


def build_shelter(stage: int) -> Mesh:
    m=Mesh()
    zf,zb=-.72,.72
    # Four large A-frame members; the storm state has one visibly failed front leg.
    legs=[
        ((-.82,.03,zf),(0,1.66,zf),310),
        (( .82,.03,zf),(0,1.66,zf),311),
        ((-.82,.03,zb),(0,1.66,zb),312),
        (( .82,.03,zb),(0,1.66,zb),313),
    ]
    for idx,(a,b,seed) in enumerate(legs):
        if stage==4 and idx==1:
            add_stick(m,a,(.38,.84,zf+.03),.050,"Wood",seed,8,3)
            add_stick(m,(.48,.72,zf+.05),(.10,1.50,zf-.02),.042,"Wood",seed+50,8,3)
        else:
            add_stick(m,a,b,.052,"Wood",seed,8,3)

    add_stick(m,(0,1.66,-.82),(0,1.66,.82),.050,"Wood",320,8,4)
    # Low side rails and one front/back cross tie make the structure believable without visual clutter.
    for a,b,s in [
        ((-.72,.42,zf),(.72,.42,zf),321),((-.72,.42,zb),(.72,.42,zb),322),
        ((-.72,.40,zf),(-.72,.40,zb),323),((.72,.40,zf),(.72,.40,zb),324),
    ]: add_stick(m,a,b,.033,"Wood",s,7,3)

    # Two storm-loaded tarp halves form one strong roof silhouette.
    left=add_cloth_panel(m,(-.42,1.38,0),.92,1.62,"Tarp",.055,12,12,stage==4,stage==4,330,roof_pitch=.61)
    right=add_cloth_panel(m,(.42,1.38,0),.92,1.62,"Tarp",.055,12,12,stage==4,False,331,roof_pitch=-.61)

    # Large lashings at the four A-frame joints read from VR interaction distance.
    for p in ((0,1.61,zf),(0,1.61,zb),(-.70,.43,zf),(.70,.43,zb)):
        add_torus(m,p,.060,.009,"Rope",12,4,"z")

    # Guy lines anchor the tarp to uneven stakes rather than floating in space.
    for i,(p,a) in enumerate([
        (left[0],(-1.10,.03,-.91)),(left[3],(-1.08,.03,.92)),
        (right[1],(1.10,.03,-.91)),(right[2],(1.08,.03,.92)),
    ]):
        add_cylinder_between(m,p,a,.008,"Rope",6)
        add_stick(m,(a[0],.01,a[2]),(a[0]+(.025 if i%2 else -.018),.22,a[2]+.012),.017,"Wood",340+i,6,2)

    if stage==4:
        # One torn hanging flap and failed rope tail sell storm damage without turning the frame into debris soup.
        add_ribbon(m,[(.18,1.28,-.10),(.30,1.05,-.08),(.27,.78,-.05)],[.34,.26,.10],"Cloth")
        add_cylinder_between(m,(.36,1.12,.65),(.62,.17,.84),.008,"Rope",6)
    elif stage==5:
        # Repaired state: visible patch and one diagonal reinforcement.
        add_box(m,(-.18,1.42,-.18),(.34,.018,.20),"Cloth",yaw=14,roll=-4)
        add_stick(m,(.70,.15,zf+.03),(-.18,1.39,zf+.02),.030,"Wood",360,7,3)
        add_torus(m,(.02,1.31,zf+.02),.050,.008,"Rope",12,4,"z")
    return m


def build_campfire() -> Mesh:
    m=Mesh(); rnd=random.Random(409)
    # Smaller irregular stones leave the crossed logs and flame as the focal point.
    for i in range(12):
        a=2*math.pi*i/12+rnd.uniform(-.045,.045); r=.34+rnd.uniform(-.018,.018)
        add_irregular_rock(m,(math.cos(a)*r,.055,math.sin(a)*r),(.105+rnd.uniform(-.012,.012),.065+rnd.uniform(-.008,.012),.095+rnd.uniform(-.012,.012)),410+i,"Stone",4,9)
    logs=[
        ((-.30,.12,-.16),(.30,.16,.16),430),
        ((-.30,.15,.17),(.30,.11,-.17),431),
        ((-.25,.19,-.03),(.25,.21,.02),432),
        ((-.20,.10,.02),(.20,.13,-.04),433),
    ]
    for a,b,s in logs: add_stick(m,a,b,.045,"Char",s,9,3)
    for i in range(9):
        a=2*math.pi*i/9; add_irregular_rock(m,(math.cos(a)*.15,.075,math.sin(a)*.15),(.050,.018,.043),450+i,"Fire" if i%3==0 else "Char",3,7)
    # Layered curved tongues are softer than the previous rigid triangular blades.
    add_flame_tongue(m,(0,.17,0),.52,.27,0,.10)
    add_flame_tongue(m,(.07,.18,-.03),.39,.20,62,.075)
    add_flame_tongue(m,(-.08,.18,.04),.32,.17,127,.060)
    add_flame_tongue(m,(.02,.20,.07),.25,.13,28,.050)
    return m


def build_beacon() -> Mesh:
    m=Mesh(); top_y=1.58
    feet=[]; tops=[]
    for i,a in enumerate((math.radians(90),math.radians(210),math.radians(330))):
        foot=(math.cos(a)*.58,.03,math.sin(a)*.58); top=(math.cos(a)*.17,top_y,math.sin(a)*.17)
        feet.append(foot); tops.append(top); add_stick(m,foot,top,.050,"Wood",510+i,8,4)
    # Two triangular brace rings make the tower read cleanly from any angle.
    for y,rad,seed in ((.52,.43,520),(1.02,.29,530)):
        pts=[(math.cos(a)*rad,y,math.sin(a)*rad) for a in (math.radians(90),math.radians(210),math.radians(330))]
        for i in range(3): add_stick(m,pts[i],pts[(i+1)%3],.030,"Wood",seed+i,7,3)
    for p in tops: add_torus(m,p,.055,.008,"Rope",12,4,"z")

    # Compact slatted platform and a metal fire basket at the centre.
    for i,x in enumerate((-.28,-.14,0,.14,.28)):
        add_stick(m,(x,1.43,-.30),(x,1.43,.30),.035,"Wood",550+i,7,2)
    add_cylinder_between(m,(0,1.46,0),(0,1.58,0),.225,"Metal",14,.19)
    add_torus(m,(0,1.58,0),.205,.012,"Metal",18,5,"y")
    add_flame_tongue(m,(0,1.57,0),.58,.25,0,.08)
    add_flame_tongue(m,(.05,1.58,-.02),.42,.19,68,.06)
    add_flame_tongue(m,(-.06,1.58,.03),.34,.16,132,.05)

    # Side signal pole and a broad rectangular cloth flag create the mockup's strong secondary read.
    add_stick(m,(.34,.10,.02),(.34,2.20,.02),.024,"Wood",570,7,3)
    flag=[(.36,2.03,.02),(.92,1.96,.02),(.86,1.52,.02),(.36,1.60,.02)]
    m.quad(flag[0],flag[1],flag[2],flag[3],"Cloth")
    m.quad(flag[3],flag[2],flag[1],flag[0],"Cloth")
    add_cylinder_between(m,flag[0],flag[1],.007,"Rope",5)
    for i,(p,a) in enumerate(zip(tops,[(-.96,.02,-.70),(.96,.02,-.68),(0,.02,1.02)])):
        add_cylinder_between(m,p,a,.008,"Rope",6)
        add_stick(m,(a[0],.01,a[2]),(a[0]+.02,.20,a[2]),.016,"Wood",580+i,6,2)
    return m


def build_shipwreck(variant: str) -> Mesh:
    m=Mesh(); scale=.82 if variant=="medium" else 1.0
    xs=[-2.15,-1.55,-.82,0.0,.78,1.43,1.92]
    widths=[.16,.64,.94,1.04,.93,.61,.20]
    heights=[.38,.68,.82,.86,.78,.61,.34]
    levels=[0,.22,.46,.70,1.0]
    # Two coherent broken hull sides. Slight per-band offset lets light show the plank courses.
    for side in (-1,1):
        grid=[]
        for si,(x,w,h) in enumerate(zip(xs,widths,heights)):
            row=[]
            for li,t in enumerate(levels):
                yy=(.07+h*t)*scale
                zz=side*w*(math.sin(t*math.pi/2)**.88)*scale
                zz += side*(li%2)*.008
                row.append((x*scale,yy,zz))
            grid.append(row)
        for si in range(len(xs)-1):
            for li in range(len(levels)-1):
                # A few missing upper panels produce storm damage while preserving the boat silhouette.
                if li>=3 and (si+li+(0 if side>0 else 1))%4==0: continue
                m.quad(grid[si][li],grid[si+1][li],grid[si+1][li+1],grid[si][li+1],"Wood")
                m.quad(grid[si][li+1],grid[si+1][li+1],grid[si+1][li],grid[si][li],"Wood")
        # Curved ribs visibly define the hull construction.
        for si in range(1,len(xs)-1):
            pts=grid[si]
            for a,b in zip(pts,pts[1:]): add_cylinder_between(m,a,b,.024*scale,"Wood",7)
            if si in (1,3,5):
                p=pts[-1]; ext=(p[0]+.03*(si-3),p[1]+(.38+.08*(si%2))*scale,p[2]*1.06)
                add_stick(m,p,ext,.027*scale,"Wood",610+si+(20 if side<0 else 0),7,2)
    # Keel, surviving gunwale fragments and a broken mast create an instantly readable wreck anchor.
    add_stick(m,(-2.0*scale,.08,0),(1.78*scale,.09,0),.050*scale,"Wood",650,9,5)
    for side in (-1,1): add_stick(m,(-1.55*scale,.66*scale,side*.62*scale),(1.34*scale,.59*scale,side*.59*scale),.035*scale,"Wood",651+(side>0),8,4)
    add_stick(m,(-.45*scale,.18,0),(.16*scale,1.72*scale,.08*scale),.045*scale,"Wood",660,8,4)
    add_torus(m,(-.08*scale,.82*scale,.05),.16*scale,.010*scale,"Rope",16,5,"z")
    add_torus(m,(.38*scale,.53*scale,-.42*scale),.11*scale,.008*scale,"Metal",14,4,"z")
    add_box(m,(1.58*scale,.08,-.76*scale),(.74*scale,.045,.10*scale),"Wood",yaw=-28,roll=5)
    add_box(m,(-1.45*scale,.07,.83*scale),(.66*scale,.045,.09*scale),"Wood",yaw=36,roll=-7)
    return m


def add_palm_frond(m: Mesh, crown, yaw: float, length: float, droop: float, seed: int) -> None:
    a=math.radians(yaw); dx,dz=math.cos(a),math.sin(a); x,y,z=crown
    pts=[
        (x,y,z),
        (x+dx*length*.34,y+.12,z+dz*length*.34),
        (x+dx*length*.68,y+.04,z+dz*length*.68),
        (x+dx*length,y-droop,z+dz*length),
    ]
    add_ribbon(m,pts,[.24,.29,.22,.035],"Leaf")
    add_cylinder_between(m,pts[0],pts[-1],.010,"Wood",5)
    # Narrow side leaflets build a broad but efficient tropical crown.
    rnd=random.Random(seed)
    for j,t in enumerate((.30,.48,.65,.80)):
        bx=x+dx*length*t; by=y+.09*(1-t)-droop*max(0,t-.55); bz=z+dz*length*t
        perp=(-dz,0,dx); side=.25*(1-t*.45)
        for sign in (-1,1):
            tip=(bx+perp[0]*side*sign,by-.05-rnd.uniform(0,.035),bz+perp[2]*side*sign)
            add_ribbon(m,[(bx,by,bz),tip],[.075,.015],"Leaf")


def build_palm(variant: str) -> Mesh:
    m=Mesh(); young=variant=="young"; broken=variant=="broken"
    h=2.85 if young else (3.10 if broken else 4.05)
    pts=[(0,.02,0),(.06,h*.32,.02),(-.04,h*.67,.07),(.10,h,.02)]
    radii=[.16 if not young else .12,.145 if not young else .105,.125 if not young else .09,.095 if not young else .07]
    for i in range(3): add_cylinder_between(m,pts[i],pts[i+1],radii[i],"Wood",10,radii[i+1])
    # Strong ring scars break the pole silhouette and push face count into useful visible geometry.
    for i in range(7 if young else 10):
        t=(i+1)/(8 if young else 11); x=.06*(1-t)+(-.04)*max(0,(t-.32)/.35)+.10*max(0,(t-.67)/.33)
        y=h*t; z=.02+.04*math.sin(t*math.pi)
        add_torus(m,(x,y,z),radii[min(2,int(t*3))]*1.04,.009,"Char",14,4,"y")
    crown=pts[-1]
    n=9 if young else (7 if broken else 13)
    for i in range(n):
        yaw=i*360/n+(-10 if i%2 else 7); length=(.86 if young else 1.35)*(1+.08*math.sin(i*1.7)); droop=.26+.10*(i%3)
        if broken and i in (1,4): length*=.55
        add_palm_frond(m,crown,yaw,length,droop,700+i)
    if not young:
        for i,yaw in enumerate((20,142,255,320)):
            a=math.radians(yaw); add_irregular_rock(m,(crown[0]+math.cos(a)*.13,crown[1]-.12,crown[2]+math.sin(a)*.13),(.065,.075,.065),760+i,"Wood",3,8)
    if broken:
        add_stick(m,(.07,h*.70,.03),(.62,h*.95,.20),.040,"Wood",780,8,3)
    return m


def build_cooking(variant: str) -> Mesh:
    m=Mesh(); apex=(0,1.18,0)
    feet=[(-.52,.02,-.34),(.52,.02,-.34),(0,.02,.52)]
    for i,p in enumerate(feet):
        add_stick(m,p,apex,.035,"Wood",810+i,8,4)
        add_torus(m,(p[0]*.48,.59,p[2]*.48),.045,.007,"Rope",10,4,"z")
    add_torus(m,(0,1.10,0),.070,.009,"Rope",12,4,"y")
    add_cylinder_between(m,(0,1.08,0),(0,.73,0),.008,"Rope",6)
    # Pot hangs centrally over a tiny blackened fire bed.
    add_cylinder_between(m,(0,.45,0),(0,.70,0),.22,"Metal",14,.20)
    add_torus(m,(0,.69,0),.205,.010,"Metal",16,5,"y")
    add_torus(m,(0,.66,0),.28,.009,"Metal",18,4,"z")
    for i,a in enumerate((0,math.pi/2,math.pi,3*math.pi/2)):
        add_stick(m,(math.cos(a)*.22,.09,math.sin(a)*.22),(-math.cos(a)*.18,.13,-math.sin(a)*.18),.028,"Char",830+i,7,2)
    for i,a in enumerate((0,2.1,4.2)):
        add_irregular_rock(m,(math.cos(a)*.27,.045,math.sin(a)*.27),(.08,.05,.07),840+i,"Stone",3,7)
    if variant=="crate": add_box(m,(.48,.13,.28),(.42,.25,.34),"Wood",yaw=-12,roll=0)
    if variant=="utensils":
        add_stick(m,(.34,.08,.14),(.68,.06,.34),.010,"Metal",850,6,2)
        add_stick(m,(.28,.07,.23),(.62,.05,.49),.009,"Wood",851,6,2)
    return m


def build(asset_id: str, variant: str) -> Mesh:
    if asset_id in {"CS-003","CS-004","CS-005"}: return build_shelter(int(asset_id.split("-")[1]))
    if asset_id=="CS-009": return build_campfire()
    if asset_id=="CS-014": return build_beacon()
    if asset_id=="EN-001": return build_shipwreck(variant)
    if asset_id=="EN-007": return build_palm(variant)
    if asset_id=="EN-017": return build_cooking(variant)
    raise KeyError(asset_id)


def main() -> int:
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8")); count=verts=faces=0; seen=set()
    for e in manifest:
        aid=str(e.get("asset_id","")); variant=str(e.get("variant","default"))
        if aid not in TARGETS or e.get("kind")!="mesh": continue
        mesh=build(aid,variant); write_obj(mesh,ROOT/e["path"])
        count+=1; verts+=len(mesh.verts); faces+=len(mesh.faces); seen.add((aid,variant))
    families={aid for aid,_ in seen}
    if families!=TARGETS: raise SystemExit(f"Mockup v2 coverage mismatch: missing={sorted(TARGETS-families)}")
    print(f"Mockup fidelity v2: {count} meshes / {len(families)} families / {verts} vertices / {faces} faces")
    return 0

if __name__=="__main__": raise SystemExit(main())
