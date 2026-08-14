#!/usr/bin/env python3
"""Generate the first production source meshes for the A2 camp props.

The meshes are deliberately low-poly, metre-scaled and split into named parts so
Unity can assign colliders, interaction states and runtime materials downstream.
"""

from __future__ import annotations

import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "source_art" / "props" / "a2" / "production"


class Obj:
    def __init__(self, name: str, out: Path | None = None, mtl: str | None = None):
        self.name = name
        self.out = out or OUT
        self.mtl = mtl or MTL
        self.v = []
        self.vt = []
        self.faces = []
        self.current = "MAT_WOOD"

    def material(self, name: str):
        self.current = name

    def box(self, name, center, size):
        cx, cy, cz = center
        sx, sy, sz = (n / 2 for n in size)
        pts = [
            (cx-sx,cy-sy,cz-sz),(cx+sx,cy-sy,cz-sz),(cx+sx,cy+sy,cz-sz),(cx-sx,cy+sy,cz-sz),
            (cx-sx,cy-sy,cz+sz),(cx+sx,cy-sy,cz+sz),(cx+sx,cy+sy,cz+sz),(cx-sx,cy+sy,cz+sz),
        ]
        quads = [(0,3,2,1),(4,5,6,7),(0,1,5,4),(3,7,6,2),(0,4,7,3),(1,2,6,5)]
        self._part(name, pts, quads)

    def beam(self, name, start, end, width):
        ax, ay, az = start; bx, by, bz = end
        dx, dy, dz = bx-ax, by-ay, bz-az
        length = math.sqrt(dx*dx + dy*dy + dz*dz)
        z = (dx/length, dy/length, dz/length)
        seed = (0,1,0) if abs(z[1]) < .9 else (1,0,0)
        xx = seed[1]*z[2]-seed[2]*z[1]; xy = seed[2]*z[0]-seed[0]*z[2]; xz = seed[0]*z[1]-seed[1]*z[0]
        mag = math.sqrt(xx*xx+xy*xy+xz*xz); x = (xx/mag,xy/mag,xz/mag)
        y = (z[1]*x[2]-z[2]*x[1], z[2]*x[0]-z[0]*x[2], z[0]*x[1]-z[1]*x[0])
        c = ((ax+bx)/2,(ay+by)/2,(az+bz)/2); hw=width/2; hl=length/2
        pts=[]
        for zz in (-hl,hl):
            for yy in (-hw,hw):
                for xxv in (-hw,hw):
                    pts.append((c[0]+x[0]*xxv+y[0]*yy+z[0]*zz,c[1]+x[1]*xxv+y[1]*yy+z[1]*zz,c[2]+x[2]*xxv+y[2]*yy+z[2]*zz))
        quads=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
        self._part(name, pts, quads)

    def cylinder(self, name, center, radius, height, sides=10):
        cx,cy,cz=center; pts=[]
        for y in (cy-height/2,cy+height/2):
            for i in range(sides):
                a=2*math.pi*i/sides; pts.append((cx+radius*math.cos(a),y,cz+radius*math.sin(a)))
        quads=[]
        for i in range(sides): quads.append((i,(i+1)%sides,(i+1)%sides+sides,i+sides))
        quads += [tuple(range(sides-1,-1,-1)),tuple(range(sides,2*sides))]
        self._part(name,pts,quads)

    def torus(self, name, center, major, minor, major_steps=16, minor_steps=6):
        cx,cy,cz=center; pts=[]
        for i in range(major_steps):
            a=2*math.pi*i/major_steps
            for j in range(minor_steps):
                b=2*math.pi*j/minor_steps
                r=major+minor*math.cos(b)
                pts.append((cx+r*math.cos(a),cy+minor*math.sin(b),cz+r*math.sin(a)))
        quads=[]
        for i in range(major_steps):
            for j in range(minor_steps):
                quads.append((i*minor_steps+j,((i+1)%major_steps)*minor_steps+j,((i+1)%major_steps)*minor_steps+(j+1)%minor_steps,i*minor_steps+(j+1)%minor_steps))
        self._part(name,pts,quads)

    def cloth(self, name, width, depth, height, sag, torn=False):
        nx,nz=6,4; pts=[]
        for iz in range(nz+1):
            for ix in range(nx+1):
                x=-width/2+width*ix/nx; z=-depth/2+depth*iz/nz
                y=height-sag*math.sin(math.pi*ix/nx)*math.sin(math.pi*iz/nz)
                if torn and ix>=5 and iz>=3: y-=.28
                pts.append((x,y,z))
        quads=[]
        for iz in range(nz):
            for ix in range(nx):
                if torn and ix==5 and iz==3: continue
                a=iz*(nx+1)+ix; quads.append((a,a+1,a+nx+2,a+nx+1))
        self._part(name,pts,quads)

    def _part(self,name,pts,polys):
        base=len(self.v); self.v.extend(pts)
        for poly in polys:
            uvbase=len(self.vt); self.vt.extend([(0,0),(1,0),(1,1),(0,1)][:len(poly)] if len(poly)<=4 else [(0.5+0.5*math.cos(2*math.pi*i/len(poly)),0.5+0.5*math.sin(2*math.pi*i/len(poly))) for i in range(len(poly))])
            self.faces.append((name,self.current,[(base+i+1,uvbase+j+1) for j,i in enumerate(poly)]))

    def write(self):
        path=self.out/f"{self.name}.obj"
        lines=[f"# PROJECT OEN production source mesh: {self.name}",f"mtllib {self.name}.mtl","s off"]
        lines += [f"v {x:.6f} {y:.6f} {z:.6f}" for x,y,z in self.v]
        lines += [f"vt {u:.6f} {v:.6f}" for u,v in self.vt]
        last=(None,None)
        for part,mat,face in self.faces:
            if part!=last[0]: lines.append(f"o {part}")
            if mat!=last[1]: lines.append(f"usemtl {mat}")
            lines.append("f "+" ".join(f"{vi}/{ti}" for vi,ti in face)); last=(part,mat)
        path.write_text("\n".join(lines)+"\n",encoding="utf-8")
        (self.out/f"{self.name}.mtl").write_text(self.mtl,encoding="utf-8")
        return path


MTL="""# Quest-friendly source materials; Claude owns final Unity shader setup.
newmtl MAT_WOOD
Kd 0.55 0.36 0.20
map_Kd textures/MAT_WEATHERED_WOOD_001.png
newmtl MAT_METAL
Kd 0.16 0.17 0.16
map_Kd textures/MAT_WORN_IRON_001.png
newmtl MAT_STONE
Kd 0.25 0.25 0.23
map_Kd textures/MAT_BEACH_STONE_001.png
newmtl MAT_CANVAS
Kd 0.72 0.65 0.48
map_Kd textures/MAT_AGED_CANVAS_001.png
newmtl MAT_CHAR
Kd 0.08 0.07 0.06
map_Kd textures/MAT_WORN_IRON_001.png
"""


def heavy_crate():
    o=Obj("PRP_HEAVY_CRATE_001")
    o.box("CrateBody",(0,.32,0),(1.02,.60,.64))
    for y in (.08,.29,.51): o.box(f"FrontSlat_{y}",(0,y,-.331),(.96,.16,.035))
    for x in (-.47,.47): o.box("CornerBrace",(x,.32,0),(.07,.62,.68))
    o.box("LidClosed",(0,.655,0),(1.08,.09,.69))
    o.material("MAT_METAL")
    for z in (-.32,.32):
        o.beam("BroadCarryHandle",(-.28,.34,z),(.28,.34,z),.07)
        o.beam("HandleMount",(-.28,.26,z),(-.28,.39,z),.07); o.beam("HandleMount",(.28,.26,z),(.28,.39,z),.07)
    return o.write()


def plan_table():
    o=Obj("PRP_PLAN_TABLE_001")
    o.box("PlanningSurface",(0,.91,0),(1.20,.10,.68))
    for x in (-.52,.52):
        for z in (-.26,.26): o.beam("TableLeg",(x,0,z),(x,.87,z),.075)
    o.beam("LongBrace",(-.52,.45,0),(.52,.45,0),.06)
    o.material("MAT_CANVAS")
    for i in range(5): o.box(f"ActionCard_{i+1}",(-.42+i*.21,.972,-.10),(.16,.012,.22))
    o.material("MAT_METAL")
    for i in range(4): o.cylinder(f"EffortMarker_{i+1}",(-.30+i*.20,1.00,.20),.035,.035,8)
    return o.write()


def signal_frame():
    o=Obj("PRP_SIGNAL_FRAME_001")
    o.beam("LeftUpright",(-.55,0,0),(0,2.05,0),.105); o.beam("RightUpright",(.55,0,0),(0,2.05,0),.105)
    o.beam("RearBrace",(0,0,.45),(0,2.05,0),.105)
    o.beam("ReachableCrossbar",(-.34,1.15,0),(.34,1.15,0),.09)
    o.material("MAT_CANVAS"); o.box("SignalPanel",(0,1.53,.015),(.58,.48,.035))
    o.material("MAT_METAL")
    for x,z in ((-.55,0),(.55,0),(0,.45)): o.cylinder("GroundAnchor",(x,.08,z),.07,.16,8)
    return o.write()


def firepit():
    o=Obj("PRP_FIREPIT_001"); o.material("MAT_STONE")
    for i in range(14):
        a=2*math.pi*i/14; o.cylinder(f"RingStone_{i+1}",(.36*math.cos(a),.105,.36*math.sin(a)),.10,.21,8)
    o.material("MAT_CHAR")
    o.beam("CharredLogA",(-.28,.16,-.20),(.28,.16,.20),.10); o.beam("CharredLogB",(-.28,.17,.20),(.28,.17,-.20),.10)
    o.cylinder("EmberBed",(0,.08,0),.30,.05,14)
    return o.write()


def shelter_beam():
    o=Obj("PRP_SHELTER_BEAM_001")
    o.beam("IntactBeam",(-.80,.11,0),(.80,.11,0),.16)
    o.material("MAT_CHAR")
    o.beam("StressBand",(-.06,.11,0),(.06,.11,0),.175)
    o.material("MAT_WOOD")
    o.beam("DamagedLeft",(-.80,.45,.30),(-.05,.45,.30),.16)
    o.beam("DamagedRight",(.10,.39,.30),(.80,.45,.30),.16)
    return o.write()


def shelter_rope():
    o=Obj("PRP_SHELTER_ROPE_001"); o.material("MAT_CANVAS")
    for y,r in ((.04,.17),(.08,.16),(.12,.15),(.16,.14)): o.torus("ChunkyCoil",(0,y,0),r,.022,18,6)
    o.beam("ReadableLooseEnd",(.14,.16,0),(.34,.05,.08),.045)
    for x in (-.34,.34): o.torus("OversizeBindingLoop",(x,.16,.32),.11,.025,14,6)
    return o.write()


def shelter_tarp(state, sag, torn=False):
    o=Obj(f"PRP_SHELTER_TARP_001_{state}"); o.material("MAT_CANVAS")
    o.cloth(f"Tarp_{state}",2.60,2.10,1.72,sag,torn)
    o.material("MAT_METAL")
    for x,z in ((-1.3,-1.05),(1.3,-1.05),(-1.3,1.05),(1.3,1.05)): o.torus("ReinforcedTiePoint",(x,1.72,z),.065,.018,10,5)
    return o.write()


def shelter_frame():
    o=Obj("PRP_SHELTER_FRAME_001")
    for z in (-.95,.95):
        o.beam("AFrameLeg",(-1.05,0,z),(0,1.82,z),.13); o.beam("AFrameLeg",(1.05,0,z),(0,1.82,z),.13)
    o.beam("RidgeBeam",(0,1.82,-1.05),(0,1.82,1.05),.13)
    o.beam("SideBrace",(-.72,.58,-.95),(-.72,.58,.95),.11); o.beam("SideBrace",(.72,.58,-.95),(.72,.58,.95),.11)
    o.beam("CrossBrace",(-.70,.42,-.96),(.70,1.30,-.96),.09); o.beam("CrossBrace",(.70,.42,-.97),(-.70,1.30,-.97),.09)
    o.material("MAT_CANVAS")
    for x,z in ((-.72,-.95),(.72,-.95),(-.72,.95),(.72,.95)): o.torus("LargeRepairNode",(x,.58,z),.075,.02,10,5)
    return o.write()


def wreck():
    o=Obj("ENV_WRECKAGE_001")
    for i in range(7):
        z=-1.45+i*.48; half=1.65*(1-0.045*abs(i-3))
        o.beam(f"HullPlankL_{i}",(-half,.28,z),(-.10,.06,z),.16); o.beam(f"HullPlankR_{i}",(.10,.06,z),(half,.28,z),.16)
    for z in (-1.25,-.45,.45,1.25):
        o.beam("ReadableRib",(-1.35,.30,z),(0,1.18,z),.12); o.beam("ReadableRib",(1.35,.30,z),(0,1.18,z),.12)
    o.beam("TiltedMast",(-.20,.22,.15),(.35,3.25,.15),.16); o.beam("BrokenYard",(-.65,2.30,.15),(.75,2.55,.15),.12)
    o.material("MAT_METAL"); o.box("WornHullBand",(0,.31,-1.48),(2.55,.10,.07))
    return o.write()


def radio():
    o=Obj("PRP_RADIO_001"); o.material("MAT_METAL")
    o.box("RadioBody",(0,.31,0),(.58,.62,.24)); o.box("SpeakerRecess",(-.11,.39,-.132),(.29,.25,.025))
    for y in (.30,.36,.42,.48): o.box("SpeakerBar",(-.11,y,-.151),(.25,.018,.018))
    o.cylinder("OversizeTuningDial",(.17,.45,-.16),.065,.04,12); o.cylinder("PowerDial",(.17,.25,-.16),.045,.04,10)
    o.material("MAT_CANVAS"); o.box("StateDisplay",(-.09,.15,-.15),(.22,.075,.025))
    o.material("MAT_METAL"); o.beam("Antenna",(.21,.61,0),(.31,.98,0),.025)
    o.box("KeyedBatterySocket",(.18,.10,-.15),(.13,.08,.035))
    return o.write()


def supply_crate():
    o=Obj("PRP_SUPPLY_CRATE_001")
    o.box("CrateBody",(0,.23,0),(.68,.46,.48)); o.box("SealedLid",(0,.49,0),(.72,.08,.51))
    for x in (-.27,.27): o.box("VerticalBrace",(x,.25,-.25),(.055,.44,.035))
    o.material("MAT_METAL")
    for x in (-.36,.36):
        o.beam("BroadSideHandle",(x,.18,-.12),(x,.18,.12),.055)
        o.beam("HandleMount",(x,.12,-.12),(x,.23,-.12),.055); o.beam("HandleMount",(x,.12,.12),(x,.23,.12),.055)
    o.box("ReadableLatch",(0,.44,-.285),(.12,.12,.04))
    return o.write()


def wind_shield():
    o=Obj("PRP_WIND_SHIELD_001"); o.material("MAT_METAL")
    for i,(x,z,a) in enumerate(((-.18,.035,-.06),(-.09,.005,-.025),(0,0,0),(.09,.005,.025),(.18,.035,.06))):
        o.beam(f"CurvedShieldSlat_{i+1}",(x-.045,.03,z),(x+.045,.41,z+a),.085)
    o.beam("TopOrientationRail",(-.24,.42,.04),(.24,.42,.04),.045)
    o.material("MAT_WOOD"); o.beam("LargeHandle",(-.10,.20,.11),(.10,.20,.11),.055)
    o.beam("HandleMount",(-.10,.14,.07),(-.10,.26,.11),.055); o.beam("HandleMount",(.10,.14,.07),(.10,.26,.11),.055)
    return o.write()


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    files=[heavy_crate(),plan_table(),signal_frame(),firepit(),shelter_beam(),shelter_rope(),
           shelter_tarp("TAUT",.10),shelter_tarp("WET_SAG",.55),shelter_tarp("TORN",.22,True),
           shelter_frame(),wreck(),radio(),supply_crate(),wind_shield()]
    print("\n".join(str(p.relative_to(ROOT)) for p in files))


if __name__ == "__main__": main()
