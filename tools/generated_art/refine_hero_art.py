#!/usr/bin/env python3
"""Refine Project ØEN hero world assets after the broad production generator.

The broad generator guarantees complete coverage of the canonical asset master.
This pass deliberately spends more geometry on the six world-space hero families
that dominate Stormnatten and the existing gameplay mockups:

- tarp / presenning
- supply crate / shared carry box
- portable radio
- shelter states
- campfire states
- handmade signal beacon states

The output remains deterministic, OBJ/MTL based, Quest-2-conscious, and keeps the
same canonical file paths + Unity GUIDs produced by generate_production_art.py.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROD = ROOT / "Assets" / "ProductionArt"
MANIFEST = PROD / "Docs" / "production_art_manifest.json"

HERO_IDS = {
    "PR-001", "PR-004", "PR-005", "PR-020",
    "CS-001", "CS-002", "CS-003", "CS-004", "CS-005",
    "CS-006", "CS-007", "CS-008", "CS-009", "CS-010",
    "CS-011", "CS-012", "CS-013", "CS-014", "CS-015",
}

@dataclass
class Mesh:
    verts: list[tuple[float, float, float]] = field(default_factory=list)
    uvs: list[tuple[float, float]] = field(default_factory=list)
    faces: list[tuple[int, int, int, str]] = field(default_factory=list)

    def v(self, p, uv=(0.0, 0.0)) -> int:
        self.verts.append(tuple(float(x) for x in p))
        self.uvs.append(tuple(float(x) for x in uv))
        return len(self.verts)

    def tri(self, a: int, b: int, c: int, mat: str) -> None:
        self.faces.append((a, b, c, mat))

    def quad(self, a, b, c, d, mat: str) -> None:
        ia = self.v(a, (0, 0)); ib = self.v(b, (1, 0)); ic = self.v(c, (1, 1)); id_ = self.v(d, (0, 1))
        self.tri(ia, ib, ic, mat); self.tri(ia, ic, id_, mat)

def rot(p, euler=(0, 0, 0)):
    x, y, z = p
    rx, ry, rz = [math.radians(a) for a in euler]
    y, z = y * math.cos(rx) - z * math.sin(rx), y * math.sin(rx) + z * math.cos(rx)
    x, z = x * math.cos(ry) + z * math.sin(ry), -x * math.sin(ry) + z * math.cos(ry)
    x, y = x * math.cos(rz) - y * math.sin(rz), x * math.sin(rz) + y * math.cos(rz)
    return x, y, z

def tp(p, center, euler=(0, 0, 0)):
    q = rot(p, euler)
    return q[0] + center[0], q[1] + center[1], q[2] + center[2]

def add_box(m: Mesh, center, size, mat="Wood", euler=(0, 0, 0)):
    sx, sy, sz = [v / 2 for v in size]
    ps = [(-sx,-sy,-sz),(sx,-sy,-sz),(sx,sy,-sz),(-sx,sy,-sz),
          (-sx,-sy,sz),(sx,-sy,sz),(sx,sy,sz),(-sx,sy,sz)]
    p = [tp(x, center, euler) for x in ps]
    for a,b,c,d in [(0,1,2,3),(5,4,7,6),(4,0,3,7),(1,5,6,2),(3,2,6,7),(4,5,1,0)]:
        m.quad(p[a],p[b],p[c],p[d],mat)

def add_cylinder(m: Mesh, center, radius, height, mat="Wood", segments=10, euler=(0,0,0)):
    h = height / 2
    top, bot = [], []
    for i in range(segments):
        a = 2 * math.pi * i / segments
        bot.append(tp((math.cos(a)*radius,-h,math.sin(a)*radius), center, euler))
        top.append(tp((math.cos(a)*radius,h,math.sin(a)*radius), center, euler))
    for i in range(segments):
        j=(i+1)%segments
        m.quad(bot[i],bot[j],top[j],top[i],mat)
    cb, ct = tp((0,-h,0),center,euler), tp((0,h,0),center,euler)
    for i in range(segments):
        j=(i+1)%segments
        a=m.v(cb,(.5,.5)); b=m.v(bot[j],(0,0)); c=m.v(bot[i],(1,0)); m.tri(a,b,c,mat)
        a=m.v(ct,(.5,.5)); b=m.v(top[i],(0,1)); c=m.v(top[j],(1,1)); m.tri(a,b,c,mat)

def add_torus(m: Mesh, center, major, minor, mat="Rope", seg_major=18, seg_minor=6, euler=(0,0,0)):
    grid=[]
    for i in range(seg_major):
        a=2*math.pi*i/seg_major; row=[]
        for j in range(seg_minor):
            b=2*math.pi*j/seg_minor
            p=((major+minor*math.cos(b))*math.cos(a),minor*math.sin(b),(major+minor*math.cos(b))*math.sin(a))
            row.append(tp(p,center,euler))
        grid.append(row)
    for i in range(seg_major):
        ni=(i+1)%seg_major
        for j in range(seg_minor):
            nj=(j+1)%seg_minor
            m.quad(grid[i][j],grid[ni][j],grid[ni][nj],grid[i][nj],mat)

def add_tarp(m: Mesh, center, width, depth, mat="Tarp", sag=.12, grid=8, damaged=False, wet=False, euler=(0,0,0)):
    pts=[]
    for z in range(grid+1):
        row=[]
        for x in range(grid+1):
            u=x/grid; v=z/grid
            px=(u-.5)*width; pz=(v-.5)*depth
            edge=(1-(2*u-1)**2)*(1-(2*v-1)**2)
            ripple=math.sin(u*math.pi*4+v*1.8)*0.018 + math.sin(v*math.pi*3)*0.012
            py=-(sag*(1.35 if wet else 1.0))*edge + ripple
            if damaged and .42<u<.58 and .35<v<.68:
                py -= .05 * math.sin((u-.42)/.16*math.pi)
            row.append(tp((px,py,pz),center,euler))
        pts.append(row)
    for z in range(grid):
        for x in range(grid):
            if damaged and 3 <= x <= 4 and 3 <= z <= 4:
                continue
            m.quad(pts[z][x],pts[z][x+1],pts[z+1][x+1],pts[z+1][x],mat)
    add_box(m,tp((0,.008,-depth/2),center,euler),(width,.026,.035),"Cloth",euler)
    add_box(m,tp((0,.008, depth/2),center,euler),(width,.026,.035),"Cloth",euler)
    add_box(m,tp((-width/2,.008,0),center,euler),(.035,.026,depth),"Cloth",euler)
    add_box(m,tp(( width/2,.008,0),center,euler),(.035,.026,depth),"Cloth",euler)

def add_rope_between(m: Mesh, a, b, radius=.018, mat="Rope", segments=7):
    ax,ay,az=a; bx,by,bz=b
    dx,dy,dz=bx-ax,by-ay,bz-az
    length=math.sqrt(dx*dx+dy*dy+dz*dz)
    if length < 1e-6: return
    yaw=math.degrees(math.atan2(dx,dz))
    pitch=math.degrees(math.acos(max(-1,min(1,dy/length))))
    center=((ax+bx)/2,(ay+by)/2,(az+bz)/2)
    add_cylinder(m,center,radius,length,mat,segments,(pitch,0,-yaw))

def add_flame_cross(m: Mesh, center, height=.55, width=.26):
    x,y,z=center
    for angle in (0,45,90,135):
        a=math.radians(angle); dx=math.cos(a)*width/2; dz=math.sin(a)*width/2
        m.quad((x-dx,y,z-dz),(x+dx,y,z+dz),(x+dx,y+height,z+dz),(x-dx,y+height,z-dz),"Fire")

def refine_tarp(variant: str) -> Mesh:
    m=Mesh()
    if variant=="folded":
        for i in range(4):
            add_box(m,(0,.055+i*.055,0),(.95,.045,.46),"Tarp",(0,(-1)**i*5,(-1)**i*2))
        add_torus(m,(0,.17,0),.22,.018,"Rope",16,5,(90,0,0))
    else:
        add_tarp(m,(0,.74,0),1.95,1.45,"Tarp",.16,9,variant=="damaged",variant=="wet",(0,0,0))
        for x in (-.94,.94):
            for z in (-.69,.69):
                add_torus(m,(x,.75,z),.045,.010,"Metal",12,4,(90,0,0))
                add_rope_between(m,(x,.74,z),(x*1.22,.18,z*1.18),.014)
        if variant=="damaged":
            add_box(m,(.08,.746,.02),(.34,.02,.08),"Cloth",(0,22,0))
    return m

def refine_crate(variant: str, heavy=False) -> Mesh:
    m=Mesh(); sx,sy,sz=((1.35,.82,.96) if heavy else (1.05,.68,.78))
    add_box(m,(0,sy*.48,0),(sx,sy*.92,sz),"Wood")
    for y in (.12,sy-.10):
        add_box(m,(0,y,-sz/2-.025),(sx+.05,.08,.055),"Wood")
        add_box(m,(0,y, sz/2+.025),(sx+.05,.08,.055),"Wood")
    for x in (-sx/2+.08,sx/2-.08):
        add_box(m,(x,sy*.48,-sz/2-.03),(.09,sy*.82,.06),"Metal")
        add_box(m,(x,sy*.48, sz/2+.03),(.09,sy*.82,.06),"Metal")
    add_box(m,(0,sy*.48,-sz/2-.065),(sx*.9,.055,.045),"Wood",(0,0,33))
    add_box(m,(0,sy*.48,-sz/2-.07),(sx*.9,.055,.045),"Wood",(0,0,-33))
    for x in (-sx/2-.02,sx/2+.02):
        add_torus(m,(x,sy*.48,0),.15,.018,"Rope",14,5,(0,90,0))
    if variant=="open":
        add_box(m,(0,sy+.19,.18),(sx*.98,.10,sz*.93),"Wood",(-28,0,0))
        add_box(m,(0,sy*.80,0),(sx*.76,.05,sz*.62),"Char")
    elif variant=="broken":
        add_box(m,(.17,sy+.10,-.10),(sx*.72,.07,.10),"Wood",(8,22,18))
        add_box(m,(-.30,sy+.04,.14),(sx*.50,.06,.08),"Wood",(-12,-35,-25))
    else:
        add_box(m,(0,sy+.025,0),(sx*.98,.10,sz*.93),"Wood")
    if heavy:
        for z in (-sz/2+.10,sz/2-.10):
            add_box(m,(0,.10,z),(sx*1.03,.08,.09),"Metal")
    return m

def refine_radio(variant: str) -> Mesh:
    m=Mesh()
    broken=variant=="broken"; repaired=variant=="repaired"; active=variant=="active"
    add_box(m,(0,.36,0),(.92,.58,.38),"Metal")
    add_box(m,(0,.38,-.205),(.70,.31,.035),"Char")
    for x in (-.43,.43):
        for y in (.11,.61):
            add_box(m,(x,y,0),(.09,.11,.42),"Rope")
    add_cylinder(m,(-.28,.78,0),.025,.38,"Metal",8,(0,0,-90))
    add_cylinder(m,( .28,.78,0),.025,.38,"Metal",8,(0,0,-90))
    add_cylinder(m,(0,.96,0),.025,.56,"Metal",8,(0,0,90))
    for i in range(7):
        add_box(m,(-.18+i*.06,.34,-.226),(.022,.22,.018),"Metal")
    add_box(m,(.18,.55,-.227),(.29,.07,.018),"Cloth")
    add_cylinder(m,(.32,.31,-.235),.062,.045,"Metal",10,(90,0,0))
    add_cylinder(m,(.20,.31,-.235),.047,.045,"Metal",10,(90,0,0))
    add_cylinder(m,(-.35,.97,.02),.018,.82,"Metal",8,(0,0,28 if broken else 7))
    add_cylinder(m,(-.35,1.35,.02),.012,.42,"Metal",8,(0,0,42 if broken else 4))
    if active or repaired:
        add_box(m,(.18,.55,-.248),(.025,.045,.012),"Fire")
    if broken:
        add_box(m,(.05,.67,-.235),(.32,.025,.018),"Metal",(0,0,15))
        add_box(m,(.12,.15,-.24),(.22,.018,.015),"Rope",(0,0,-22))
    if repaired:
        add_box(m,(-.02,.12,-.235),(.42,.035,.02),"Cloth")
    return m

def shelter_stage(stage: int) -> Mesh:
    m=Mesh()
    for z in (-.72,.72):
        for x,ang in ((-.72,-27),(.72,27)):
            add_cylinder(m,(x*.55,.78,z),.055,1.72,"Wood",9,(0,0,ang))
    add_cylinder(m,(0,1.56,0),.055,1.62,"Wood",9,(0,0,90))
    if stage>=2:
        for z in (-.72,.72):
            add_cylinder(m,(0,.22,z),.045,1.55,"Wood",8,(0,0,90))
        for x in (-.66,.66):
            add_cylinder(m,(x,.38,0),.042,1.45,"Wood",8,(90,0,0))
        for p in [(-.52,.78,-.72),(.52,.78,-.72),(-.52,.78,.72),(.52,.78,.72)]:
            add_torus(m,p,.09,.014,"Rope",12,4,(90,0,0))
    if stage>=3:
        add_tarp(m,(-.44,1.30,0),.88,1.48,"Tarp",.08,7,stage==4,stage==4,(0,0,-27))
        add_tarp(m,( .44,1.30,0),.88,1.48,"Tarp",.08,7,stage==4,stage==4,(0,0, 27))
        for a,b in [((-.78,1.18,-.70),(-1.08,.10,-.90)),((.78,1.18,-.70),(1.08,.10,-.90)),
                    ((-.78,1.18,.70),(-1.08,.10,.90)),((.78,1.18,.70),(1.08,.10,.90))]:
            add_rope_between(m,a,b,.013)
    if stage==4:
        add_cylinder(m,(.26,.77,.20),.05,1.15,"Wood",8,(0,0,55))
        add_box(m,(-.12,1.38,-.02),(.30,.025,.12),"Cloth",(0,18,0))
    if stage==5:
        add_cylinder(m,(-.58,.62,-.70),.035,1.18,"Wood",8,(0,0,-45))
        add_cylinder(m,( .58,.62,-.70),.035,1.18,"Wood",8,(0,0,45))
        add_box(m,(-.18,1.37,.18),(.32,.028,.18),"Cloth",(0,20,0))
        add_box(m,( .25,1.34,-.25),(.28,.028,.15),"Cloth",(0,-18,0))
    return m

def campfire_stage(stage: int) -> Mesh:
    m=Mesh()
    for i in range(12):
        a=2*math.pi*i/12
        add_box(m,(math.cos(a)*.43,.11,math.sin(a)*.43),(.22,.16,.20),"Stone",(0,math.degrees(a),0))
    for ang,y in [(-42,.20),(42,.22),(0,.25)]:
        add_cylinder(m,(0,y,0),.07,.86,"Wood",9,(0,0,90+ang))
    if stage>=2:
        for i in range(5):
            a=2*math.pi*i/5
            add_box(m,(math.cos(a)*.18,.18,math.sin(a)*.18),(.20,.035,.12),"Char",(0,math.degrees(a),0))
    if stage in (3,4):
        add_flame_cross(m,(0,.25,0),.48 if stage==3 else .78,.24 if stage==3 else .34)
        if stage==4:
            add_flame_cross(m,(.12,.28,-.08),.52,.18)
    if stage==5:
        add_tarp(m,(0,.245,0),.50,.42,"Water",.015,3,False,True)
    return m

def beacon_stage(stage: int) -> Mesh:
    m=Mesh()
    for x,z,ax,az in [(-.55,-.35,-14,-8),(.55,-.35,14,-8),(-.55,.35,-14,8),(.55,.35,14,8)]:
        add_cylinder(m,(x,.82,z),.055,1.75,"Wood",9,(az,0,ax))
    if stage>=2:
        for y in (.42,.78,1.12):
            add_cylinder(m,(0,y,-.36),.035,1.10,"Wood",8,(0,0,90))
            add_cylinder(m,(0,y,.36),.035,1.10,"Wood",8,(0,0,90))
        for p in [(-.50,.45,-.35),(.50,.45,-.35),(-.50,.45,.35),(.50,.45,.35)]:
            add_torus(m,p,.08,.014,"Rope",12,4,(90,0,0))
    if stage>=3:
        add_box(m,(0,1.55,0),(1.02,.12,.80),"Wood")
        for x in (-.40,-.20,0,.20,.40):
            add_box(m,(x,1.64,0),(.10,.06,.72),"Wood")
        add_tarp(m,(.52,1.92,0),.72,.46,"Cloth",.04,4,stage==5,stage==5,(0,0,90))
        add_cylinder(m,(.18,1.92,0),.030,.82,"Wood",8)
        add_cylinder(m,(0,1.78,0),.26,.13,"Metal",12)
        add_box(m,(0,1.85,0),(.42,.07,.42),"Char")
    if stage==4:
        add_flame_cross(m,(0,1.88,0),.88,.38)
        add_flame_cross(m,(.10,1.90,-.05),.62,.22)
    if stage==5:
        add_cylinder(m,(.22,.92,.08),.055,1.35,"Wood",8,(0,0,55))
        add_box(m,(-.18,1.53,.08),(.52,.08,.18),"Wood",(0,24,12))
    return m

def build(asset_id: str, variant: str) -> Mesh:
    if asset_id=="PR-001": return refine_tarp(variant)
    if asset_id=="PR-004": return refine_crate(variant,False)
    if asset_id=="PR-020": return refine_crate(variant,True)
    if asset_id=="PR-005": return refine_radio(variant)
    n=int(asset_id.split("-")[1])
    if 1 <= n <= 5: return shelter_stage(n)
    if 6 <= n <= 10: return campfire_stage(n-5)
    if 11 <= n <= 15: return beacon_stage(n-10)
    raise KeyError(asset_id)

def write_obj(mesh: Mesh, path: Path) -> None:
    mtl_rel="../../Materials/project_oen.mtl"
    lines=[f"mtllib {mtl_rel}",f"o {path.stem}"]
    for v in mesh.verts: lines.append("v %.6f %.6f %.6f" % v)
    for uv in mesh.uvs: lines.append("vt %.6f %.6f" % uv)
    last=None
    for a,b,c,mat in mesh.faces:
        if mat!=last:
            lines.append("usemtl "+mat); last=mat
        lines.append(f"f {a}/{a} {b}/{b} {c}/{c}")
    path.write_text("\n".join(lines)+"\n",encoding="utf-8")

def main() -> int:
    if not MANIFEST.exists():
        raise SystemExit(f"Missing production manifest: {MANIFEST}")
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    refined=0; verts=0; tris=0
    for entry in manifest:
        aid=str(entry.get("asset_id",""))
        if aid not in HERO_IDS or entry.get("kind")!="mesh":
            continue
        path=ROOT/entry["path"]
        mesh=build(aid,str(entry.get("variant","default")))
        write_obj(mesh,path)
        refined+=1; verts+=len(mesh.verts); tris+=len(mesh.faces)
    print(f"Refined {refined} hero meshes: {verts} vertices / {tris} triangles")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
