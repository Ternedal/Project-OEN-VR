#!/usr/bin/env python3
"""Final mockup-fidelity pass for Project ØEN Stormnatten hero world art.

This pass runs *after* the broad/refinement/story passes and intentionally replaces
the most visually dominant hero meshes with more organic, asymmetric, weathered,
VR-readable geometry matching the approved Stormnatten mockup direction:
hand-built survival objects, storm-loaded cloth, worn rescue equipment, wet coastal
materials and an imperfect "made here, with what we found" silhouette.

The pass is deterministic and Quest-2-conscious. It preserves canonical paths and
Unity GUIDs because only OBJ contents are replaced.
"""
from __future__ import annotations
import json, math, random
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROD = ROOT / "Assets" / "ProjectOEN" / "ProductionArt"
MANIFEST = PROD / "Docs" / "production_art_manifest.json"

TARGET_IDS = {
    "PR-001", "PR-005",
    "CS-001","CS-002","CS-003","CS-004","CS-005",
    "CS-006","CS-007","CS-008","CS-009","CS-010",
    "CS-011","CS-012","CS-013","CS-014","CS-015",
}

@dataclass
class Mesh:
    verts: list[tuple[float,float,float]] = field(default_factory=list)
    uvs: list[tuple[float,float]] = field(default_factory=list)
    faces: list[tuple[int,int,int,str]] = field(default_factory=list)
    def v(self,p,uv=(0.0,0.0)):
        self.verts.append(tuple(float(x) for x in p)); self.uvs.append(tuple(float(x) for x in uv)); return len(self.verts)
    def tri(self,a,b,c,mat): self.faces.append((a,b,c,mat))
    def quad(self,a,b,c,d,mat,uvs=((0,0),(1,0),(1,1),(0,1))):
        ids=[self.v(p,uv) for p,uv in zip((a,b,c,d),uvs)]
        self.tri(ids[0],ids[1],ids[2],mat); self.tri(ids[0],ids[2],ids[3],mat)

def add_box(m, center, size, mat="Wood", yaw=0.0, roll=0.0):
    cx,cy,cz=center; sx,sy,sz=(s/2 for s in size)
    cr,sr=math.cos(math.radians(roll)),math.sin(math.radians(roll)); cyw,syw=math.cos(math.radians(yaw)),math.sin(math.radians(yaw))
    raw=[(-sx,-sy,-sz),(sx,-sy,-sz),(sx,sy,-sz),(-sx,sy,-sz),(-sx,-sy,sz),(sx,-sy,sz),(sx,sy,sz),(-sx,sy,sz)]
    pts=[]
    for x,y,z in raw:
        x,y=x*cr-y*sr,x*sr+y*cr; x,z=x*cyw+z*syw,-x*syw+z*cyw; pts.append((x+cx,y+cy,z+cz))
    for a,b,c,d in ((0,1,2,3),(5,4,7,6),(4,0,3,7),(1,5,6,2),(3,2,6,7),(4,5,1,0)): m.quad(pts[a],pts[b],pts[c],pts[d],mat)

def _basis(a,b):
    ax,ay,az=a; bx,by,bz=b; dx,dy,dz=bx-ax,by-ay,bz-az; ln=math.sqrt(dx*dx+dy*dy+dz*dz)
    if ln < 1e-7: return None
    w=(dx/ln,dy/ln,dz/ln); helper=(0,1,0) if abs(w[1]) < .88 else (1,0,0)
    ux=helper[1]*w[2]-helper[2]*w[1]; uy=helper[2]*w[0]-helper[0]*w[2]; uz=helper[0]*w[1]-helper[1]*w[0]; ul=math.sqrt(ux*ux+uy*uy+uz*uz)
    u=(ux/ul,uy/ul,uz/ul); v=(w[1]*u[2]-w[2]*u[1],w[2]*u[0]-w[0]*u[2],w[0]*u[1]-w[1]*u[0]); return w,u,v,ln

def add_cylinder_between(m,a,b,radius,mat="Wood",segments=9,radius2=None):
    basis=_basis(a,b)
    if not basis:return
    w,u,v,ln=basis; radius2=radius if radius2 is None else radius2; rings=[]
    for p,r in ((a,radius),(b,radius2)):
        ring=[]
        for i in range(segments):
            q=2*math.pi*i/segments
            ring.append((p[0]+r*(u[0]*math.cos(q)+v[0]*math.sin(q)),p[1]+r*(u[1]*math.cos(q)+v[1]*math.sin(q)),p[2]+r*(u[2]*math.cos(q)+v[2]*math.sin(q))))
        rings.append(ring)
    for i in range(segments):
        j=(i+1)%segments; m.quad(rings[0][i],rings[0][j],rings[1][j],rings[1][i],mat)
    for ring,flip,c in ((rings[0],True,a),(rings[1],False,b)):
        ci=m.v(c,(.5,.5))
        for i in range(segments):
            j=(i+1)%segments; ii=m.v(ring[i],(0,0)); jj=m.v(ring[j],(1,0)); m.tri(ci,jj,ii,mat) if flip else m.tri(ci,ii,jj,mat)

def add_stick(m,a,b,radius=.045,mat="Wood",seed=1,segments=8,bends=3):
    rnd=random.Random(seed); pts=[a]
    for i in range(1,bends):
        t=i/bends; p=[a[k]*(1-t)+b[k]*t for k in range(3)]; p[0]+=rnd.uniform(-.025,.025); p[1]+=rnd.uniform(-.018,.018); p[2]+=rnd.uniform(-.025,.025); pts.append(tuple(p))
    pts.append(b)
    for i in range(len(pts)-1):
        add_cylinder_between(m,pts[i],pts[i+1],radius*(1+rnd.uniform(-.12,.12)),mat,segments,radius*(1+rnd.uniform(-.16,.10)))

def add_torus(m,center,major,minor,mat="Rope",seg_major=18,seg_minor=6,axis="y"):
    cx,cy,cz=center; grid=[]
    for i in range(seg_major):
        a=2*math.pi*i/seg_major; row=[]
        for j in range(seg_minor):
            b=2*math.pi*j/seg_minor; x=(major+minor*math.cos(b))*math.cos(a); y=minor*math.sin(b); z=(major+minor*math.cos(b))*math.sin(a)
            if axis=="z": y,z=z,y
            elif axis=="x": x,y=y,x
            row.append((cx+x,cy+y,cz+z))
        grid.append(row)
    for i in range(seg_major):
        ni=(i+1)%seg_major
        for j in range(seg_minor):
            nj=(j+1)%seg_minor; m.quad(grid[i][j],grid[ni][j],grid[ni][nj],grid[i][nj],mat)

def add_irregular_rock(m,center,scale,seed,mat="Stone",rings=4,segments=9):
    rnd=random.Random(seed); cx,cy,cz=center; pts=[]
    for r in range(rings+1):
        phi=math.pi*r/rings; row=[]
        for s in range(segments):
            th=2*math.pi*s/segments; jitter=1+rnd.uniform(-.14,.14)
            row.append((cx+math.sin(phi)*math.cos(th)*scale[0]*jitter,cy+math.cos(phi)*scale[1]*(1+rnd.uniform(-.08,.08)),cz+math.sin(phi)*math.sin(th)*scale[2]*jitter))
        pts.append(row)
    for r in range(rings):
        for s in range(segments):
            ns=(s+1)%segments; m.quad(pts[r][s],pts[r][ns],pts[r+1][ns],pts[r+1][s],mat)

def _cloth_point(cx,cy,cz,px,pz,sag,u,v,wet,seed,roof_pitch=0.0):
    edge=(1-(2*u-1)**2)*(1-(2*v-1)**2); ripple=(math.sin(u*math.pi*5.1+v*1.7+seed*.13)*.024+math.sin(v*math.pi*3.6-u*.8)*.015+math.sin((u+v)*math.pi*2.1)*.010); tension=math.sin(u*math.pi)*math.sin(v*math.pi)
    y=cy-sag*edge*(1.28 if wet else 1.0)+ripple*tension+roof_pitch*px
    return (cx+px+.018*math.sin(v*math.pi*2.0+seed)*tension,y,cz+pz+.012*math.sin(u*math.pi*3.0+seed*.7)*tension)

def add_cloth_panel(m,center,width,depth,mat="Tarp",sag=.16,nx=14,nz=11,wet=False,damaged=False,seed=1,roof_pitch=0.0):
    cx,cy,cz=center; pts=[]
    for iz in range(nz+1):
        v=iz/nz; row=[]
        for ix in range(nx+1):
            u=ix/nx; px=(u-.5)*width; pz=(v-.5)*depth
            if ix in (0,nx) and iz not in (0,nz): px+=math.sin(v*math.pi*5+seed)*.012
            if iz in (0,nz) and ix not in (0,nx): pz+=math.sin(u*math.pi*4+seed*.5)*.012
            row.append(_cloth_point(cx,cy,cz,px,pz,sag,u,v,wet,seed,roof_pitch))
        pts.append(row)
    for iz in range(nz):
        for ix in range(nx):
            u=(ix+.5)/nx; v=(iz+.5)/nz
            if damaged and (.48<u<.67 and .36<v<.60): continue
            m.quad(pts[iz][ix],pts[iz][ix+1],pts[iz+1][ix+1],pts[iz+1][ix],mat,((ix/nx,iz/nz),((ix+1)/nx,iz/nz),((ix+1)/nx,(iz+1)/nz),(ix/nx,(iz+1)/nz)))
    corners=[pts[0][0],pts[0][-1],pts[-1][-1],pts[-1][0]]
    for i in range(4): add_cylinder_between(m,corners[i],corners[(i+1)%4],.014,"Cloth",6)
    for p in corners: add_torus(m,(p[0],p[1]+.006,p[2]),.034,.008,"Metal",12,4,"y")
    if damaged:
        hole=[pts[int(nz*.36)][int(nx*.48)],pts[int(nz*.36)][int(nx*.67)],pts[int(nz*.60)][int(nx*.67)],pts[int(nz*.60)][int(nx*.48)]]
        for i in range(4): add_cylinder_between(m,hole[i],hole[(i+1)%4],.009,"Cloth",5)
    return corners

def add_lashing(m,center,axis="y",major=.075):
    add_torus(m,center,major,.010,"Rope",12,4,axis); add_torus(m,(center[0]+.008,center[1]+.006,center[2]-.006),major*1.04,.008,"Rope",12,4,axis)

def build_tarp(variant):
    m=Mesh()
    if variant=="folded":
        for i in range(5): add_box(m,((-.02 if i%2 else .02),.035+i*.038,0),(.92,.032,.42),"Tarp",yaw=(-3+i*1.7),roll=(2 if i%2 else -2))
        add_torus(m,(0,.13,0),.20,.015,"Rope",16,5,"z"); add_torus(m,(.26,.13,0),.17,.012,"Rope",14,5,"z"); return m
    wet=variant in ("wet","damaged"); damaged=variant=="damaged"
    corners=add_cloth_panel(m,(0,.76,0),2.05,1.52,"Tarp",.19,16,12,wet,damaged,11)
    anchors=[(-1.34,.08,-1.02),(1.28,.09,-.96),(1.37,.07,1.03),(-1.29,.08,.98)]
    for i,(p,a) in enumerate(zip(corners,anchors)):
        add_cylinder_between(m,p,a,.0105,"Rope",6); add_stick(m,(a[0],.02,a[2]),(a[0]+(-.02 if i%2 else .03),.23,a[2]+.015),.018,"Wood",80+i,6,2)
    if damaged: add_box(m,(.25,.715,.05),(.38,.018,.17),"Cloth",yaw=13,roll=-2)
    return m

def build_radio(variant):
    m=Mesh(); broken=variant=="broken"; repaired=variant=="repaired"; active=variant=="active"
    add_box(m,(0,.39,0),(.88,.58,.38),"Char"); add_box(m,(0,.40,-.018),(.82,.53,.39),"Metal"); add_box(m,(0,.40,-.216),(.76,.45,.026),"Char")
    for x in (-.405,.405):
        for y in (.16,.64): add_box(m,(x,y,-.01),(.075,.115,.42),"Rope",roll=(4 if x*y>0 else -4))
    speaker=(-.19,.39,-.242); add_cylinder_between(m,(speaker[0],speaker[1],-.223),(speaker[0],speaker[1],-.258),.165,"Char",20); add_torus(m,speaker,.165,.012,"Metal",22,5,"z")
    for i in range(-5,6):
        x=speaker[0]+i*.026; h=math.sqrt(max(0,.145**2-(x-speaker[0])**2))*1.75; add_box(m,(x,speaker[1],-.266),(.009,h,.012),"Metal")
    add_box(m,(.205,.54,-.248),(.27,.085,.018),"Cloth"); add_box(m,(.292,.54,-.259),(.055,.046,.012),"Fire" if (active or repaired) else "Metal")
    for x,r in ((.21,.062),(.335,.050)):
        add_cylinder_between(m,(x,.33,-.225),(x,.33,-.285),r,"Metal",14); add_box(m,(x,.33,-.289),(.014,r*1.4,.010),"Char",roll=15 if x<.3 else -24)
    add_cylinder_between(m,(-.29,.74,0),(-.29,.88,0),.024,"Metal",8); add_cylinder_between(m,(.29,.74,0),(.29,.88,0),.024,"Metal",8); add_cylinder_between(m,(-.29,.88,0),(.29,.88,0),.027,"Metal",8)
    knee=(-.34,1.05,.02); tip=(-.28 if broken else -.25,1.48,.03); add_cylinder_between(m,(-.34,.72,.02),knee,.018,"Metal",8); add_cylinder_between(m,knee,tip,.011,"Metal",7)
    if broken:
        add_box(m,(.05,.63,-.274),(.31,.015,.012),"Metal",roll=17); add_cylinder_between(m,(.13,.17,-.25),(.29,.03,-.31),.008,"Rope",5)
    if repaired:
        add_box(m,(-.05,.16,-.277),(.44,.032,.014),"Cloth",roll=-4); add_box(m,(.06,.13,-.279),(.032,.19,.014),"Cloth",roll=8)
    return m

def _frame(m,stage):
    posts=[((-.73,.04,-.70),(-.18,1.58,-.67),101),((.76,.04,-.70),(.15,1.55,-.69),102),((-.69,.04,.72),(-.14,1.60,.69),103),((.72,.04,.70),(.16,1.57,.71),104)]
    for a,b,s in posts:add_stick(m,a,b,.050,"Wood",s,8,4)
    add_stick(m,(-.20,1.58,-.70),(.18,1.58,.72),.048,"Wood",111,8,4)
    if stage>=2:
        for a,b,s in [((-.70,.25,-.70),(.72,.29,-.70),121),((-.66,.24,.70),(.68,.30,.70),122),((-.68,.28,-.68),(-.64,.31,.68),123),((.70,.31,-.68),(.66,.27,.68),124)]: add_stick(m,a,b,.035,"Wood",s,7,3)
        for p in [(-.48,.77,-.69),(.48,.79,-.69),(-.46,.80,.70),(.47,.78,.70)]: add_lashing(m,p,"z",.058)

def build_shelter(stage):
    m=Mesh(); _frame(m,stage)
    if stage>=3:
        add_cloth_panel(m,(-.40,1.23,0),.94,1.50,"Tarp",.075,10,11,stage>=4,stage==4,201,roof_pitch=.52); add_cloth_panel(m,(.40,1.23,0),.94,1.50,"Tarp",.075,10,11,stage>=4,stage==4,202,roof_pitch=-.52)
        for p,a in [((-.78,1.12,-.70),(-1.12,.08,-.96)),((.79,1.10,-.69),(1.13,.08,-.94)),((-.78,1.13,.70),(-1.10,.08,.97)),((.78,1.12,.70),(1.11,.08,.96))]: add_cylinder_between(m,p,a,.009,"Rope",6)
    if stage==4:
        add_stick(m,(.16,.08,.18),(.71,.94,.36),.042,"Wood",240,7,3); add_box(m,(-.13,1.39,-.03),(.34,.020,.14),"Cloth",yaw=17,roll=-4)
    if stage==5:
        add_stick(m,(-.64,.20,-.68),(.44,1.20,-.67),.034,"Wood",251,7,3); add_stick(m,(.64,.18,-.67),(-.43,1.17,-.68),.033,"Wood",252,7,3); add_box(m,(-.20,1.40,.18),(.35,.022,.20),"Cloth",yaw=18,roll=2); add_box(m,(.26,1.35,-.23),(.30,.022,.17),"Cloth",yaw=-14,roll=-3)
    return m

def add_flame_ribbon(m,center,height,width,yaw,mat="Fire"):
    x,y,z=center; a=math.radians(yaw); dx=math.cos(a)*width/2; dz=math.sin(a)*width/2; b1=(x-dx,y,z-dz); b2=(x+dx,y,z+dz); mid=(x+math.sin(a)*width*.12,y+height*.55,z-math.cos(a)*width*.12); tip=(x-math.sin(a)*width*.10,y+height,z+math.cos(a)*width*.10)
    i1=m.v(b1); i2=m.v(b2); im=m.v(mid); it=m.v(tip); m.tri(i1,i2,im,mat); m.tri(i1,im,it,mat); m.tri(i2,it,im,mat)

def build_campfire(stage):
    m=Mesh(); rnd=random.Random(360+stage)
    for i in range(13):
        a=2*math.pi*i/13+rnd.uniform(-.045,.045); r=.43+rnd.uniform(-.035,.025); add_irregular_rock(m,(math.cos(a)*r,.09,math.sin(a)*r),(.15+rnd.uniform(-.02,.02),.10+rnd.uniform(-.015,.02),.13+rnd.uniform(-.02,.02)),400+i)
    for a,b,s in [((-.38,.17,-.22),(.40,.25,.22),501),((-.39,.21,.25),(.37,.18,-.28),502),((-.30,.29,.03),(.33,.31,-.01),503)]:
        add_stick(m,a,b,.060,"Char" if stage>=2 else "Wood",s,9,3)
        for p in (a,b): add_irregular_rock(m,p,(.065,.065,.065),s+700,"Wood",3,8)
    if stage>=2:
        for i in range(8):
            a=2*math.pi*i/8; add_irregular_rock(m,(math.cos(a)*.19,.12,math.sin(a)*.19),(.07,.028,.055),600+i,"Char",3,7)
    if stage in (3,4):
        h=.56 if stage==3 else .82
        for yaw,off,scale in [(0,(0,0,0),1),(62,(.10,.02,-.05),.78),(118,(-.09,0,.06),.70),(28,(.03,.05,.09),.55)]: add_flame_ribbon(m,(off[0],.23+off[1],off[2]),h*scale,.28*scale,yaw)
        for i in range(5): add_box(m,((i-2)*.07,.17,(i%2-.5)*.08),(.055,.018,.11),"Fire",yaw=i*23,roll=3)
    if stage==5:
        add_cloth_panel(m,(0,.225,0),.54,.46,"Water",.018,4,4,True,False,705)
        for i in range(4): add_box(m,((i-1.5)*.11,.16,.05*(-1)**i),(.08,.015,.06),"Char",yaw=17*i)
    return m

def build_beacon(stage):
    m=Mesh(); legs=[((-.56,.03,-.37),(-.33,1.67,-.23),801),((.58,.03,-.36),(.31,1.61,-.22),802),((-.52,.03,.39),(-.30,1.63,.24),803),((.56,.03,.37),(.34,1.66,.25),804)]
    for a,b,s in legs:add_stick(m,a,b,.050,"Wood",s,8,4)
    if stage>=2:
        for a,b,s in [((-.49,.48,-.33),(.48,1.08,-.28),811),((.49,.48,-.32),(-.45,1.03,-.29),812),((-.46,.48,.34),(.47,1.07,.31),813),((.48,.48,.33),(-.44,1.04,.31),814)]: add_stick(m,a,b,.030,"Wood",s,7,3)
        for p in [(-.43,.51,-.31),(.43,.52,-.30),(-.42,.52,.32),(.43,.51,.31)]: add_lashing(m,p,"z",.052)
    if stage>=3:
        for i,x in enumerate((-.39,-.20,0,.21,.40)): add_stick(m,(x,1.50,-.36),(x+(i%2)*.015,1.53,.36),.045,"Wood",830+i,7,2)
        add_stick(m,(-.47,1.47,-.38),(.49,1.48,-.38),.040,"Wood",840,7,3); add_stick(m,(-.45,1.49,.39),(.47,1.50,.38),.040,"Wood",841,7,3)
        add_cylinder_between(m,(0,1.54,0),(0,1.63,0),.25,"Metal",14,.21); add_box(m,(0,1.66,0),(.34,.035,.34),"Char",yaw=7)
        add_stick(m,(.39,1.58,.04),(.44,2.32,.03),.026,"Wood",850,7,3); add_cloth_panel(m,(.66,2.05,.03),.46,.52,"Cloth",.065,6,6,stage==5,stage==5,851)
    if stage==4:
        for yaw,off in [(0,(0,0,0)),(55,(.08,.01,-.04)),(115,(-.07,.02,.04))]: add_flame_ribbon(m,(off[0],1.65+off[1],off[2]),.84,.30,yaw)
    if stage==5:
        add_stick(m,(.18,.08,.10),(.52,1.18,.24),.048,"Wood",870,7,3); add_box(m,(-.17,1.49,.08),(.48,.07,.16),"Wood",yaw=26,roll=9)
    return m

def build(asset_id,variant):
    if asset_id=="PR-001":return build_tarp(variant)
    if asset_id=="PR-005":return build_radio(variant)
    n=int(asset_id.split("-")[1])
    if 1<=n<=5:return build_shelter(n)
    if 6<=n<=10:return build_campfire(n-5)
    if 11<=n<=15:return build_beacon(n-10)
    raise KeyError(asset_id)

def write_obj(mesh,path):
    path.parent.mkdir(parents=True,exist_ok=True); lines=["mtllib ../../Materials/project_oen.mtl",f"o {path.stem}"]
    for v in mesh.verts:lines.append("v %.6f %.6f %.6f"%v)
    for uv in mesh.uvs:lines.append("vt %.6f %.6f"%uv)
    last=None
    for a,b,c,mat in mesh.faces:
        if mat!=last:lines.append("usemtl "+mat);last=mat
        lines.append(f"f {a}/{a} {b}/{b} {c}/{c}")
    path.write_text("\n".join(lines)+"\n",encoding="utf-8")

def main():
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8")); count=verts=tris=0
    for e in manifest:
        aid=str(e.get("asset_id",""))
        if aid not in TARGET_IDS or e.get("kind")!="mesh":continue
        mesh=build(aid,str(e.get("variant","default"))); write_obj(mesh,ROOT/e["path"]); count+=1;verts+=len(mesh.verts);tris+=len(mesh.faces)
    print(f"Mockup-fidelity pass: {count} hero meshes, {verts} vertices, {tris} triangles"); return 0

if __name__=="__main__": raise SystemExit(main())
