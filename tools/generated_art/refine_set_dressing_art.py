#!/usr/bin/env python3
"""Refine remaining Project ØEN world/set-dressing assets plus CS-016.

This pass intentionally leaves EN-011 puddles and EN-025 shoreline foam as thin
holder meshes and generates their actual state-specific transparent decal textures in
`ProductionArt/Decals`. Unity's prefab builder wires those textures onto the holder
meshes, so these assets behave like cheap Quest-friendly ground decals instead of
pretending a generic Mud/Water material is enough.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from refine_hero_art import (
    Mesh, add_box, add_cylinder, add_torus, add_tarp, add_rope_between,
    add_flame_cross, write_obj,
)
from refine_environment_art import add_rock, add_leaf

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PROD=ROOT/"Assets"/"ProjectOEN"/"ProductionArt"
MANIFEST=PROD/"Docs"/"production_art_manifest.json"
DECAL_ROOT=PROD/"Decals"/"environment_set_dressing"

MESH_IDS={
    "CS-016",
    "EN-003","EN-004","EN-013","EN-014","EN-015","EN-016","EN-017",
    "EN-018","EN-019","EN-020","EN-021","EN-022","EN-023","EN-024",
    "EN-011","EN-025",
}
DECAL_IDS={"EN-011","EN-025"}


def guid_for(path:Path)->str:
    rel=str(path.relative_to(ROOT)).replace('\\','/')
    return hashlib.md5(("ProjectOEN.ProductionArt.Decal.v1:"+rel).encode()).hexdigest()


def write_decal_meta(path:Path):
    max_size=max(Image.open(path).size)
    text=f'''fileFormatVersion: 2\nguid: {guid_for(path)}\nTextureImporter:\n  internalIDToNameTable: []\n  externalObjects: {{}}\n  serializedVersion: 13\n  mipmaps:\n    mipMapMode: 0\n    enableMipMap: 1\n  isReadable: 0\n  streamingMipmaps: 0\n  textureSettings:\n    serializedVersion: 2\n    filterMode: 1\n    aniso: 1\n    mipBias: 0\n    wrapU: 1\n    wrapV: 1\n    wrapW: 1\n  nPOTScale: 0\n  alphaIsTransparency: 1\n  textureType: 0\n  spriteMode: 0\n  alphaSource: 1\n  platformSettings:\n  - serializedVersion: 3\n    buildTarget: DefaultTexturePlatform\n    maxTextureSize: {max_size}\n    resizeAlgorithm: 0\n    textureFormat: -1\n    textureCompression: 1\n    compressionQuality: 80\n    crunchedCompression: 0\n    allowsAlphaSplitting: 0\n    overridden: 0\n  userData: Project OEN production ground decal\n  assetBundleName: \n  assetBundleVariant: \n'''
    Path(str(path)+".meta").write_text(text,encoding="utf-8")


def radio_repair(variant:str)->Mesh:
    m=Mesh(); mid=variant in ("mid_repair","mid-repair"); repaired=variant=="repaired"
    # rough beach workbench: planks lashed across low supports
    for z in (-.28,.28):
        add_cylinder(m,(-.48,.23,z),.045,.52,"Wood",8)
        add_cylinder(m,( .48,.23,z),.045,.52,"Wood",8)
    for z in (-.24,0,.24):
        add_box(m,(0,.48,z),(1.18,.07,.20),"Wood",(0,0,0))
    for x in (-.45,.45): add_torus(m,(x,.46,0),.12,.013,"Rope",14,5,(90,0,0))
    # radio chassis
    add_box(m,(-.22,.70,0),(.52,.34,.31),"Metal")
    add_box(m,(-.22,.72,-.165),(.38,.17,.018),"Char")
    add_cylinder(m,(-.05,.84,-.18),.025,.10,"Metal",8,(90,0,0))
    # parts/readability differ by repair state
    part_count=7 if not repaired else 2
    for i in range(part_count):
        x=.16+(i%4)*.13; z=-.18+(i//4)*.22
        add_box(m,(x,.57,z),(.09,.025,.055),"Metal",(0,(i*37)%90,0))
    if variant=="broken":
        add_box(m,(-.18,.75,-.18),(.20,.025,.035),"Char",(0,0,18))
        add_rope_between(m,(-.30,.83,-.18),(-.08,.56,-.10),.009,"Metal",5)
    elif mid:
        add_rope_between(m,(-.09,.78,-.18),(.32,.58,-.10),.008,"Metal",5)
        add_box(m,(.30,.62,.15),(.18,.04,.10),"Cloth",(0,15,0))
    else:
        add_cylinder(m,(-.22,.93,0),.012,.54,"Metal",6,(0,0,-8))
        add_box(m,(-.22,.75,-.182),(.12,.055,.012),"Fire")
    return m


def barrel(variant:str)->Mesh:
    m=Mesh(); broken=variant=="broken"
    # stave-like body using 12 narrow boxes, stronger silhouette than cylinder-only broad pass
    for i in range(12):
        a=2*math.pi*i/12; x=math.sin(a)*.31; z=math.cos(a)*.31
        add_box(m,(x,.48,z),(.15,.88,.08),"Wood",(0,math.degrees(a),0))
    for y in (.13,.46,.79): add_torus(m,(0,y,0),.35,.018,"Metal",18,5,(90,0,0))
    add_cylinder(m,(0,.94,0),.31,.035,"Wood",14)
    if broken:
        add_box(m,(.18,.96,-.03),(.36,.07,.11),"Char",(5,26,32))
        add_box(m,(-.24,.88,.10),(.30,.065,.10),"Wood",(-8,-19,-26))
        add_torus(m,(0,.78,0),.36,.016,"Metal",18,5,(90,0,13))
    return m


def rope_debris(variant:str)->Mesh:
    m=Mesh(); coils=3 if variant=="small" else 5
    for i in range(coils):
        x=(i-(coils-1)/2)*.15; z=.09*math.sin(i*1.9)
        add_torus(m,(x,.035+i*.012,z),.20+.035*(i%2),.016,"Rope",18,5,(90,i*17,0))
    # loose tails make the debris read as discarded rope rather than perfect rings
    add_rope_between(m,(-.22,.04,-.08),(-.62,.025,.24),.014,"Rope",6)
    if variant=="medium": add_rope_between(m,(.22,.05,.04),(.72,.025,-.26),.014,"Rope",6)
    return m


def cliff_grass(variant:str)->Mesh:
    m=Mesh(); count=14 if variant=="short" else 26
    for i in range(count):
        a=i*2.399963; r=.04+.035*math.sqrt(i); x=math.cos(a)*r; z=math.sin(a)*r
        h=.24+.10*((i*5)%4) if variant=="short" else .38+.13*((i*7)%4)
        add_rope_between(m,(x,.01,z),(x+.05*math.sin(i),h,z+.04*math.cos(i)),.007,"Wood",5)
        add_leaf(m,(x,h*.30,z),h*.60,.055,20+i*37,-28,"Leaf",.03)
    return m


def cave_wall(variant:str)->Mesh:
    m=Mesh(); rows=4; cols=6
    for row in range(rows):
        for col in range(cols):
            x=(col-2.5)*.58+(row%2)*.17; y=row*.43; phase=(row*7+col)*.29
            if variant=="corner" and col>2:
                add_rock(m,(.75, y, (col-2.5)*.56),(.37,.34,.31),"Stone",8,phase)
            elif variant=="arch" and row>=2 and 1<=col<=4:
                # leave central opening; cap with an irregular stone arch
                if row==2 and col in (1,4): add_rock(m,(x,y,.02),(.40,.34,.34),"Stone",8,phase)
            else:
                add_rock(m,(x,y,.04*math.sin(col+row)),(.38,.35,.33),"Stone",8,phase)
    if variant=="arch":
        for i,a in enumerate((150,125,100,80,55,30)):
            r=math.radians(a); add_rock(m,(math.cos(r)*1.22+0.02,1.22+math.sin(r)*.55,0),(.34,.28,.34),"Stone",8,i*.47)
    return m


def cave_debris(variant:str)->Mesh:
    m=Mesh(); stones=variant=="stones"
    count=12 if stones else 9
    for i in range(count):
        a=i*2.399963; r=.12+.11*math.sqrt(i); x=math.cos(a)*r; z=math.sin(a)*r
        if stones: add_rock(m,(x,0,z),(.14+.025*(i%3),.11,.13),"Stone",7,i*.31)
        else:
            add_cylinder(m,(x,.05,z),.028,.42+.08*(i%4),"Wood",7,(0,(i*53)%180,90))
            if i%3==0: add_leaf(m,(x,.07,z),.24,.08,(i*71)%360,-25,"Leaf",.03)
    return m


def groundsheet(variant:str)->Mesh:
    m=Mesh(); wet=variant=="wet"; worn=variant=="worn"
    add_tarp(m,(0,.025,0),1.48,.88,"Tarp" if wet else "Cloth",.045,7,worn,wet)
    for x,z in ((-.68,-.38),(.68,-.38),(-.68,.38),(.68,.38)):
        add_cylinder(m,(x,.035,z),.012,.16,"Wood",6)
        add_rope_between(m,(x,.04,z),(x*.94,.04,z*.94),.007,"Rope",5)
    if worn: add_box(m,(.30,.055,-.08),(.28,.012,.04),"Char",(0,18,5))
    return m


def cooking_corner(variant:str)->Mesh:
    m=Mesh()
    # tripod base always present
    for yaw in (0,120,240):
        a=math.radians(yaw); add_cylinder(m,(math.sin(a)*.28,.48,math.cos(a)*.28),.027,1.02,"Wood",7,(0,0,15 if yaw==0 else -12))
    add_torus(m,(0,.92,0),.22,.012,"Rope",14,5,(90,0,0))
    if variant=="pot":
        add_cylinder(m,(0,.38,0),.24,.30,"Metal",12); add_torus(m,(0,.54,0),.23,.014,"Metal",16,5,(90,0,0))
    elif variant=="crate":
        add_box(m,(.45,.22,.10),(.56,.44,.48),"Wood"); add_box(m,(.45,.22,-.15),(.60,.06,.05),"Metal")
    else:  # utensils
        for i in range(4): add_cylinder(m,(-.22+i*.14,.23,-.10+i*.035),.012,.46,"Metal",6,(0,0,70+i*8))
        add_box(m,(.35,.08,.10),(.32,.08,.24),"Wood",(0,18,0))
    return m


def storage_corner(variant:str)->Mesh:
    m=Mesh()
    if variant=="crate":
        add_box(m,(0,.28,0),(.76,.56,.62),"Wood")
        for y in (.07,.49): add_box(m,(0,y,-.32),(.80,.055,.045),"Metal")
    elif variant=="sack":
        # layered cloth bundles read as a tied supply sack without expensive sculpt topology
        for i in range(5): add_box(m,(0,.08+i*.075,0),(.48-.035*i,.065,.38-.018*i),"Cloth",(0,(i%2)*8-4,0))
        add_torus(m,(0,.46,0),.09,.012,"Rope",12,4,(90,0,0))
    else: # poles
        for i in range(7): add_cylinder(m,((i-3)*.08,.10,.03*math.sin(i)),.036,1.16,"Wood",7,(0,0,78+(i-3)*3))
        add_torus(m,(0,.18,0),.12,.014,"Rope",14,5,(90,0,0))
    return m


def signal_hill(variant:str)->Mesh:
    m=Mesh()
    if variant=="logs":
        for i in range(7): add_cylinder(m,((i-3)*.10,.10,.03*(i%2)),.038,.86,"Wood",7,(0,0,90+(i-3)*4))
    elif variant=="ropes":
        for i in range(4): add_torus(m,((i-1.5)*.13,.04,.03*math.sin(i)),.19+.02*(i%2),.015,"Rope",18,5,(90,i*11,0))
    else:
        for i in range(8):
            a=i*2.399963; add_rock(m,(math.cos(a)*(.12+.07*i),0,math.sin(a)*(.12+.07*i)),(.16,.12,.15),"Stone",7,i*.33)
    return m


def rain_catcher(variant:str)->Mesh:
    m=Mesh()
    # variants are separate components as master-list items, but each remains recognizable alone
    if variant=="frame":
        for x,z,ang in ((-.45,-.30,-10),(.45,-.30,10),(-.45,.30,-10),(.45,.30,10)):
            add_cylinder(m,(x,.48,z),.034,1.02,"Wood",7,(0,0,ang))
        add_rope_between(m,(-.44,.93,-.29),(.44,.93,-.29),.012,"Rope",6)
        add_rope_between(m,(-.44,.93,.29),(.44,.93,.29),.012,"Rope",6)
    elif variant=="cloth":
        add_tarp(m,(0,.12,0),1.10,.78,"Tarp",.13,7,False,True)
        for x,z in ((-.50,-.34),(.50,-.34),(-.50,.34),(.50,.34)): add_rope_between(m,(x,.12,z),(x*.92,.02,z*.92),.010,"Rope",5)
    else: # basin
        add_cylinder(m,(0,.16,0),.31,.26,"Metal",14); add_cylinder(m,(0,.30,0),.25,.015,"Water",14)
    return m


def torch_stand(variant:str)->Mesh:
    m=Mesh(); lit=variant=="lit"
    add_cylinder(m,(0,.62,0),.047,1.24,"Wood",8)
    add_cylinder(m,(0,1.18,0),.18,.16,"Metal",12)
    add_torus(m,(0,1.29,0),.17,.012,"Metal",14,5,(90,0,0))
    for i in range(4): add_box(m,((i-1.5)*.06,1.32,0),(.045,.08,.16),"Char",(0,0,90))
    if lit: add_flame_cross(m,(0,1.36,0),.34,.15)
    return m


def path_marker(variant:str)->Mesh:
    m=Mesh(); marked=variant in ("cloth_marked","cloth-marked")
    add_cylinder(m,(0,.55,0),.035,1.10,"Wood",7)
    add_box(m,(0,1.04,0),(.26,.055,.07),"Wood",(0,0,0))
    if marked:
        p0=(.04,.91,-.01); p1=(.37,.87,-.01); p2=(.31,.62,-.01); p3=(.04,.67,-.01); m.quad(p0,p1,p2,p3,"Cloth")
        add_rope_between(m,(.04,.88,0),(.04,.65,0),.008,"Rope",5)
    return m


def storm_damage(variant:str)->Mesh:
    m=Mesh(); cloth=variant in ("loose_cloth","loose-cloth")
    if not cloth:
        for i in range(10):
            x=((i%5)-2)*.20; z=(i//5-.5)*.30; add_box(m,(x,.05+.018*i,z),(.62+.08*(i%3),.065,.09),"Wood",(0,-40+(i*37)%88,(i%3-1)*10))
        add_rope_between(m,(-.42,.12,-.14),(.52,.09,.20),.012,"Rope",6)
    else:
        add_tarp(m,(0,.06,0),1.15,.78,"Tarp",.18,8,True,True)
        add_rope_between(m,(-.56,.08,-.30),(-.82,.04,-.48),.012,"Rope",6)
        add_rope_between(m,(.50,.08,.27),(.76,.03,.46),.012,"Rope",6)
    return m


def boundary_rope(variant:str)->Mesh:
    m=Mesh(); slack=variant=="slack"
    add_cylinder(m,(-.70,.40,0),.035,.80,"Wood",7)
    add_cylinder(m,( .70,.40,0),.035,.80,"Wood",7)
    if slack:
        points=[(-.70,.64,0),(-.35,.50,.02),(0,.44,0),(.35,.50,-.02),(.70,.64,0)]
    else:
        points=[(-.70,.64,0),(-.35,.63,0),(0,.62,0),(.35,.63,0),(.70,.64,0)]
    for a,b in zip(points,points[1:]): add_rope_between(m,a,b,.014,"Rope",7)
    return m


def decal_holder(asset_id:str,variant:str)->Mesh:
    m=Mesh(); wide=1.15 if asset_id=="EN-011" else 1.55
    depth=.88 if asset_id=="EN-011" else .75
    if asset_id=="EN-011":
        scale={"small":.60,"medium":.82,"large":1.0}.get(variant,.82)
    else:
        scale=1.0 if variant=="calm" else 1.15
    # one horizontal quad with useful UVs; actual state-specific visual comes from decal texture
    w=wide*scale; d=depth*scale; y=.008
    m.quad((-w/2,y,-d/2),(w/2,y,-d/2),(w/2,y,d/2),(-w/2,y,d/2),"Mud" if asset_id=="EN-011" else "Water")
    return m


def build(aid:str,variant:str)->Mesh:
    if aid=="CS-016": return radio_repair(variant)
    return {
        "EN-003":barrel,"EN-004":rope_debris,"EN-013":cliff_grass,"EN-014":cave_wall,
        "EN-015":cave_debris,"EN-016":groundsheet,"EN-017":cooking_corner,"EN-018":storage_corner,
        "EN-019":signal_hill,"EN-020":rain_catcher,"EN-021":torch_stand,"EN-022":path_marker,
        "EN-023":storm_damage,"EN-024":boundary_rope,
        "EN-011":lambda v:decal_holder("EN-011",v),"EN-025":lambda v:decal_holder("EN-025",v),
    }[aid](variant)


def irregular_mask(size:int,seed:str,coverage=.72,elongate=1.0)->Image.Image:
    rnd=random.Random(seed); small=128
    mask=Image.new("L",(small,small),0); d=ImageDraw.Draw(mask)
    cx=cy=small/2; pts=[]; n=36
    for i in range(n):
        a=2*math.pi*i/n
        wob=.80+.17*math.sin(i*2.19+rnd.random()*1.8)+rnd.uniform(-.08,.08)
        rx=small*.43*coverage*elongate*wob; ry=small*.43*coverage/elongate*wob
        pts.append((cx+math.cos(a)*rx,cy+math.sin(a)*ry))
    d.polygon(pts,fill=238)
    mask=mask.filter(ImageFilter.GaussianBlur(2.2)).resize((size,size),Image.Resampling.LANCZOS)
    return mask


def puddle_texture(variant:str,size=1024)->Image.Image:
    im=Image.new("RGBA",(size,size),(0,0,0,0)); mask=irregular_mask(size,"puddle:"+variant,{"small":.58,"medium":.74,"large":.92}.get(variant,.74),1.18)
    # dark wet mud under a cooler reflective center; alpha remains modest for ground blending
    base=Image.new("RGBA",im.size,(55,62,55,0)); base.putalpha(mask.point(lambda a:int(a*.72)))
    im=Image.alpha_composite(im,base)
    inner=mask.filter(ImageFilter.GaussianBlur(size//28)); cool=Image.new("RGBA",im.size,(77,103,110,0)); cool.putalpha(inner.point(lambda a:int(a*.38))); im=Image.alpha_composite(im,cool)
    # subtle highlight streaks clipped by puddle mask
    hi=Image.new("RGBA",im.size,(0,0,0,0)); d=ImageDraw.Draw(hi)
    for yoff,xoff in ((-.12,-.10),(.04,.06),(.17,-.04)):
        y=int(size*(.5+yoff)); x=int(size*(.5+xoff)); d.arc((x-int(size*.22),y-int(size*.055),x+int(size*.22),y+int(size*.055)),195,340,fill=(180,207,211,82),width=max(3,size//170))
    hi.putalpha(Image.composite(hi.getchannel("A"),Image.new("L",im.size,0),mask)); return Image.alpha_composite(im,hi)


def foam_texture(variant:str,size=1024)->Image.Image:
    im=Image.new("RGBA",(size,size),(0,0,0,0)); d=ImageDraw.Draw(im); storm=variant=="storm"
    rnd=random.Random("foam:"+variant); bands=4 if storm else 2
    for band in range(bands):
        pts=[]; y0=size*(.34+band*.13)
        for i in range(25):
            x=i*size/24; y=y0+math.sin(i*.78+band)*size*(.025 if storm else .018)+rnd.uniform(-8,8)
            pts.append((x,y))
        width=max(6,size//75)*(2 if storm and band<2 else 1)
        d.line(pts,fill=(229,239,235,190 if storm else 145),width=width)
        for i in range(6 if storm else 3):
            x=rnd.randint(0,size-1); y=int(y0+rnd.uniform(-.05,.05)*size); r=rnd.randint(size//80,size//40)
            d.ellipse((x-r,y-r,x+r,y+r),outline=(240,247,242,135),width=max(2,size//260))
    return im.filter(ImageFilter.GaussianBlur(.7 if storm else .45))


def decal_filename(aid:str,name:str,variant:str)->str:
    base=name.lower().replace(" / ","_").replace(" ","_").replace("-","_")
    base=''.join(ch if ch.isalnum() or ch=='_' else '' for ch in base)
    while '__' in base: base=base.replace('__','_')
    return f"{aid.lower()}_{base}__{variant}.png"


def main()->int:
    if not MANIFEST.exists(): raise SystemExit(f"Missing production manifest: {MANIFEST}")
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8")); refined=verts=faces=0; families=set(); decals=0
    DECAL_ROOT.mkdir(parents=True,exist_ok=True)
    # remove stale generated decal png/meta only; directory is dedicated to this deterministic pass
    for p in DECAL_ROOT.glob("en-0*.png*"): p.unlink()
    for entry in manifest:
        aid=str(entry.get("asset_id","")); variant=str(entry.get("variant","default"))
        if aid not in MESH_IDS or entry.get("kind")!="mesh": continue
        mesh=build(aid,variant); write_obj(mesh,ROOT/entry["path"])
        refined+=1; verts+=len(mesh.verts); faces+=len(mesh.faces); families.add(aid)
        if aid in DECAL_IDS:
            name=str(entry.get("name","decal")); path=DECAL_ROOT/decal_filename(aid,name,variant)
            im=puddle_texture(variant) if aid=="EN-011" else foam_texture(variant)
            im.save(path,compress_level=6); write_decal_meta(path); decals+=1
    missing=MESH_IDS-families
    if missing: raise SystemExit("Set-dressing refinement missed families: "+", ".join(sorted(missing)))
    if decals!=5: raise SystemExit(f"Expected 5 decal textures, generated {decals}")
    print(f"Refined {refined} set-dressing/world meshes across {len(families)} families: {verts} vertices / {faces} faces")
    print(f"Generated {decals} state-specific transparent ground decal textures")
    return 0

if __name__=="__main__": raise SystemExit(main())
