#!/usr/bin/env python3
"""Generate the Project ØEN mockup-atlas expansion pack.

The original 148-ID canonical master is intentionally kept stable because Unity-side
contracts already depend on it. Visual audit against the approved asset atlas showed
that the atlas itself contains additional families not represented in that master.
This generator materialises those *missing reference families* as separate Unity-ready
assets without renaming or replacing existing canonical files.

Expansion coverage:
- key-art / environment backgrounds;
- island maps and physical documents;
- wildlife billboard sprites;
- food/cooking set-dressing sprites;
- additional survival tools and crafting furniture;
- radio/communication accessories;
- sky/weather billboard support.

The output lives inside the existing ProductionArt tree and has deterministic Unity
.meta GUIDs. 3D assets reuse the production material set and remain Quest-conscious.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from guid_identity import stable_production_art_guid_path

from refine_mockup_fidelity import (
    Mesh, add_box, add_cylinder_between, add_stick, add_torus,
    add_irregular_rock, write_obj,
)

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PROD=ROOT/"Assets"/"ProductionArt"
SPR=PROD/"Sprites"/"atlas_expansion"
MESH=PROD/"Meshes"/"atlas_expansion"
DOCS=PROD/"Docs"
MANIFEST=DOCS/"mockup_atlas_expansion_manifest.json"

IVORY=(235,225,194,255); INK=(18,24,23,255); INK2=(31,39,36,255)
GREEN=(54,88,48,255); GREEN2=(76,117,61,255); PALM=(93,126,68,255)
CYAN=(42,155,186,255); BLUE=(62,111,137,255); SKY=(109,165,185,255)
ORANGE=(237,132,38,255); RED=(175,58,43,255); GOLD=(196,151,67,255)
WOOD=(112,76,45,255); PAPER=(205,188,148,255); STONE=(92,98,94,255)
METAL=(103,112,109,255); WATER=(42,116,145,255); SAND=(154,132,91,255)


def slug(s): return ''.join(ch.lower() if ch.isalnum() else '_' for ch in s).strip('_').replace('__','_')
def guid(path:Path): return hashlib.md5(("ProjectOEN.AtlasExpansion.v1:"+stable_production_art_guid_path(path, ROOT)).encode()).hexdigest()

def font(size,bold=False):
    for p in (("/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf"),
              ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")):
        try:return ImageFont.truetype(p,size)
        except OSError: pass
    return ImageFont.load_default()

def png_meta(path:Path,w:int,h:int):
    return f'''fileFormatVersion: 2\nguid: {guid(path)}\nTextureImporter:\n  internalIDToNameTable: []\n  externalObjects: {{}}\n  serializedVersion: 13\n  mipmaps:\n    mipMapMode: 0\n    enableMipMap: 1\n  isReadable: 0\n  streamingMipmaps: 0\n  textureSettings:\n    serializedVersion: 2\n    filterMode: 1\n    aniso: 1\n    mipBias: 0\n    wrapU: 1\n    wrapV: 1\n    wrapW: 1\n  nPOTScale: 0\n  alphaIsTransparency: 1\n  textureType: 8\n  spriteMode: 1\n  spritePixelsToUnits: 100\n  alphaSource: 1\n  platformSettings:\n  - serializedVersion: 3\n    buildTarget: DefaultTexturePlatform\n    maxTextureSize: {max(w,h)}\n    textureFormat: -1\n    textureCompression: 1\n    compressionQuality: 72\n    crunchedCompression: 0\n    overridden: 0\n  userData: Project OEN mockup atlas expansion\n  assetBundleName: \n  assetBundleVariant: \n'''

def obj_meta(path:Path):
    return f'''fileFormatVersion: 2\nguid: {guid(path)}\nModelImporter:\n  serializedVersion: 22200\n  internalIDToNameTable: []\n  externalObjects: {{}}\n  materials:\n    materialImportMode: 1\n    materialName: 0\n    materialSearch: 1\n  animations:\n    legacyGenerateAnimations: 4\n    bakeSimulation: 0\n    resampleCurves: 1\n    optimizeGameObjects: 0\n  meshes:\n    lODScreenPercentages: []\n    globalScale: 1\n    meshCompression: 0\n    addColliders: 0\n    useFileScale: 1\n  tangentSpace:\n    normalSmoothAngle: 60\n    normalImportMode: 0\n    tangentImportMode: 3\n  userData: Project OEN mockup atlas expansion\n  assetBundleName: \n  assetBundleVariant: \n'''

def save_sprite(im:Image.Image,path:Path):
    path.parent.mkdir(parents=True,exist_ok=True); im.convert("RGBA").save(path,compress_level=6); Path(str(path)+".meta").write_text(png_meta(path,*im.size),encoding="utf-8")

def save_mesh(mesh:Mesh,path:Path):
    path.parent.mkdir(parents=True,exist_ok=True); write_obj(mesh,path); Path(str(path)+".meta").write_text(obj_meta(path),encoding="utf-8")

def grain(im,seed,amount=14):
    r=random.Random(seed); d=ImageDraw.Draw(im,"RGBA"); w,h=im.size
    for _ in range(max(800,w*h//2200)):
        x=r.randrange(w); y=r.randrange(h); a=r.randint(3,amount); c=255 if r.random()>.52 else 0; d.point((x,y),fill=(c,c,c,a))
    return im

def gradient(size,top,bottom):
    w,h=size; im=Image.new("RGBA",size); d=ImageDraw.Draw(im)
    for y in range(h):
        t=y/max(1,h-1); c=tuple(int(top[i]*(1-t)+bottom[i]*t) for i in range(4)); d.line((0,y,w,y),fill=c)
    return im

def palm_silhouette(d,x,y,s,col=(22,48,34,255)):
    d.line((x,y,x+s*.05,y-s*.66),fill=(80,57,36,255),width=max(3,int(s*.055)))
    crown=(x+s*.05,y-s*.66)
    for a in (-160,-130,-100,-72,-42,-12,18):
        q=math.radians(a); ex=crown[0]+math.cos(q)*s*.42; ey=crown[1]+math.sin(q)*s*.27
        d.line((crown[0],crown[1],ex,ey),fill=col,width=max(3,int(s*.035)))
        for t in (.35,.58,.78):
            bx=crown[0]+(ex-crown[0])*t; by=crown[1]+(ey-crown[1])*t
            d.ellipse((bx-s*.06,by-s*.025,bx+s*.06,by+s*.025),fill=col)

def island_shape(d,cx,cy,s,fill=GREEN):
    pts=[]
    for i in range(28):
        a=2*math.pi*i/28; rad=s*(.78+.14*math.sin(i*2.17)+.08*math.sin(i*5.3)); pts.append((cx+math.cos(a)*rad,cy+math.sin(a)*rad*.72))
    d.polygon(pts,fill=fill)
    for i in range(8):
        a=2*math.pi*i/8+.3; r=s*(.18+.045*(i%3)); x=cx+math.cos(a)*s*.45; y=cy+math.sin(a)*s*.30; d.ellipse((x-r,y-r*.65,x+r,y+r*.65),fill=GREEN2)
    d.polygon(((cx-s*.22,cy+s*.20),(cx,cy-s*.45),(cx+s*.25,cy+s*.22)),fill=STONE)

def backdrop(variant,size=(1536,768)):
    storm="storm" in variant or "lightning" in variant; sunset="golden" in variant or "sunset" in variant; night="moon" in variant or "firelit" in variant
    if storm: top=(14,29,38,255); bottom=(54,67,69,255)
    elif night: top=(7,20,38,255); bottom=(27,54,60,255)
    elif sunset: top=(77,66,97,255); bottom=(235,148,73,255)
    else: top=(61,139,190,255); bottom=(185,211,197,255)
    im=gradient(size,top,bottom); d=ImageDraw.Draw(im,"RGBA"); w,h=size; horizon=int(h*.63)
    # clouds
    r=random.Random("bg:"+variant)
    if storm or night:
        for _ in range(20 if storm else 10):
            x=r.randint(-80,w); y=r.randint(30,int(h*.42)); rx=r.randint(90,230); ry=r.randint(30,85); d.ellipse((x-rx,y-ry,x+rx,y+ry),fill=(25,39,48,r.randint(60,130)))
    # sea and coast
    d.rectangle((0,horizon,w,h),fill=(27,105,129,255) if not storm else (28,67,78,255))
    for i in range(12):
        yy=horizon+15+i*16; d.line((0,yy,w,yy+r.randint(-4,4)),fill=(170,225,218,75),width=2)
    # island
    base=[(w*.26,horizon+20),(w*.40,h*.39),(w*.50,h*.28),(w*.58,h*.36),(w*.72,horizon+15)]
    d.polygon(base,fill=(33,65,42,255)); d.polygon(((w*.36,horizon),(w*.50,h*.25),(w*.61,horizon)),fill=(65,78,68,255))
    for i in range(17): palm_silhouette(d,w*(.30+i*.023),horizon+22,70+r.randint(-12,18),(37,72,39,255))
    # beach foreground
    d.polygon(((0,h*.76),(w*.42,h*.67),(w*.62,h*.78),(w,h*.71),(w,h),(0,h)),fill=(145,125,86,255) if not night else (59,62,50,255))
    palm_silhouette(d,w*.12,h*.92,180,(24,55,34,255)); palm_silhouette(d,w*.90,h*.90,145,(25,57,35,255))
    if sunset:
        d.ellipse((w*.78-48,h*.22-48,w*.78+48,h*.22+48),fill=(255,205,99,220))
    if night:
        d.ellipse((w*.76-38,h*.17-38,w*.76+38,h*.17+38),fill=(221,230,222,220))
    if "lightning" in variant:
        pts=[(w*.64,h*.05),(w*.60,h*.24),(w*.65,h*.25),(w*.56,h*.48),(w*.61,h*.29),(w*.56,h*.28)]; d.line(pts,fill=(230,246,255,255),width=7)
    return grain(im,"bggrain:"+variant,10)

def map_sprite(variant,size=(1024,1024)):
    im=Image.new("RGBA",size,(0,0,0,0)); d=ImageDraw.Draw(im); pad=78
    d.rounded_rectangle((pad,pad,size[0]-pad,size[1]-pad),radius=24,fill=(193,170,126,255),outline=(112,75,42,255),width=8)
    # aged edge + grid
    for i in range(10):
        x=pad+30+i*(size[0]-2*pad-60)/9; d.line((x,pad+30,x,size[1]-pad-30),fill=(97,105,81,42),width=2)
        y=pad+30+i*(size[1]-2*pad-60)/9; d.line((pad+30,y,size[0]-pad-30,y),fill=(97,105,81,42),width=2)
    island_shape(d,size[0]//2,size[1]//2,300,(55,102,61,255))
    # shoreline
    d.ellipse((160,210,864,810),outline=(44,100,122,150),width=9)
    if variant!="clean":
        rr=random.Random("map:"+variant); pts=[]
        for i in range(7): pts.append((310+i*70,620-rr.randint(0,250)))
        d.line(pts,fill=RED if "storm" in variant else ORANGE,width=10,joint="curve")
        for x,y in pts[::2]: d.ellipse((x-12,y-12,x+12,y+12),fill=RED if "storm" in variant else ORANGE)
    d.text((110,105),"ØEN — FIELD MAP",font=font(40,True),fill=(65,47,31,255)); d.text((735,900),"N ↑",font=font(34,True),fill=(55,48,38,255))
    return grain(im,"mapgrain:"+variant,18)

def document_sprite(kind,variant,size=(768,1024)):
    im=Image.new("RGBA",size,(0,0,0,0)); d=ImageDraw.Draw(im); p=54
    d.polygon(((p+10,p),(size[0]-p-10,p+8),(size[0]-p,p+size[1]*.80),(size[0]-p-20,size[1]-p),(p,size[1]-p-12)),fill=PAPER,outline=(118,84,48,255))
    title={"journal":"SURVIVAL NOTES","radio":"RADIO FIELD REPAIR","signal":"SIGNAL PLAN"}[kind]
    d.text((p+45,p+50),title,font=font(38,True),fill=(71,49,31,255))
    for i in range(11):
        y=p+145+i*58; d.line((p+45,y,size[0]-p-45,y),fill=(95,82,59,110),width=2)
    if kind=="radio":
        d.rounded_rectangle((150,270,610,600),radius=18,outline=(61,65,58,255),width=7); d.ellipse((205,360,370,525),outline=(61,65,58,255),width=8); d.rectangle((410,345,555,395),outline=(61,65,58,255),width=6); d.line((485,270,550,170),fill=(61,65,58,255),width=6)
    elif kind=="signal":
        d.line((210,650,360,250,520,650),fill=(74,55,36,255),width=10); d.line((245,550,490,550),fill=(74,55,36,255),width=7); d.polygon(((365,250),(570,320),(550,440),(365,390)),outline=RED,fill=(0,0,0,0))
    else:
        island_shape(d,370,440,150,(72,104,62,255)); d.text((145,735),"FIRE  •  SHELTER  •  SIGNAL",font=font(23,True),fill=(95,56,37,255))
    if "annotated" in variant or "storm" in variant:
        d.line((125,780,630,690),fill=RED,width=7); d.text((415,720),"CHECK!",font=font(28,True),fill=RED)
    return grain(im,kind+variant,24)

# --- transparent billboard / inventory art -------------------------------------------------

def canvas(size=(768,768)): return Image.new("RGBA",size,(0,0,0,0))
def shadow(d,cx,cy,rx,ry): d.ellipse((cx-rx,cy-ry,cx+rx,cy+ry),fill=(5,8,7,65))

def wildlife(kind,size=(768,768)):
    im=canvas(size); d=ImageDraw.Draw(im); cx,cy=size[0]//2,int(size[1]*.52); s=min(size)*.62
    shadow(d,cx,cy+s*.30,s*.34,s*.055)
    if kind=="gull":
        d.ellipse((cx-s*.26,cy-s*.05,cx+s*.20,cy+s*.16),fill=(211,215,205,255),outline=INK,width=3); d.ellipse((cx+s*.13,cy-s*.15,cx+s*.31,cy+s*.04),fill=(221,224,213,255)); d.polygon(((cx+s*.29,cy-.04*s),(cx+s*.43,cy),(cx+s*.29,cy+.05*s)),fill=ORANGE)
        d.polygon(((cx-s*.12,cy),(cx-s*.50,cy-s*.26),(cx-s*.24,cy+s*.06)),fill=(167,176,171,255)); d.line((cx-.02*s,cy+s*.14,cx-.06*s,cy+s*.31),fill=(142,104,58,255),width=6); d.line((cx+.10*s,cy+s*.14,cx+.14*s,cy+s*.31),fill=(142,104,58,255),width=6)
    elif kind=="parrot":
        d.ellipse((cx-s*.22,cy-s*.30,cx+s*.18,cy+s*.24),fill=(41,137,77,255),outline=INK,width=4); d.ellipse((cx-s*.11,cy-s*.38,cx+s*.20,cy-s*.09),fill=(209,59,47,255)); d.polygon(((cx+s*.18,cy-s*.26),(cx+s*.37,cy-s*.20),(cx+s*.18,cy-s*.12)),fill=(218,183,81,255)); d.polygon(((cx-s*.16,cy+.10*s),(cx-s*.36,cy+s*.48),(cx+.01*s,cy+s*.20)),fill=(46,86,150,255))
    elif kind=="crab":
        d.ellipse((cx-s*.20,cy-s*.10,cx+s*.20,cy+s*.18),fill=(186,69,44,255),outline=INK,width=4)
        for sign in (-1,1):
            for i in range(3): d.line((cx+sign*s*.14,cy+s*(.02+i*.045),cx+sign*s*(.34+i*.035),cy+s*(.18+i*.08)),fill=(174,67,43,255),width=8)
            d.ellipse((cx+sign*s*.32-s*.07,cy-s*.13,cx+sign*s*.32+s*.07,cy+.01*s),outline=(189,73,45,255),width=9)
    elif kind=="boar":
        d.ellipse((cx-s*.34,cy-s*.14,cx+s*.26,cy+s*.20),fill=(78,61,45,255),outline=INK,width=4); d.ellipse((cx+s*.15,cy-s*.10,cx+s*.38,cy+s*.12),fill=(82,64,48,255)); d.polygon(((cx+s*.23,cy-s*.10),(cx+s*.21,cy-s*.28),(cx+s*.09,cy-s*.11)),fill=(74,58,43,255))
        for x in (-.22,.10): d.line((cx+s*x,cy+s*.14,cx+s*(x-.03),cy+s*.34),fill=(57,48,39,255),width=10)
        d.arc((cx+s*.30,cy, cx+s*.46,cy+s*.18),80,250,fill=IVORY,width=5)
    elif kind=="goat":
        d.ellipse((cx-s*.30,cy-s*.12,cx+s*.25,cy+s*.20),fill=(156,142,113,255),outline=INK,width=4); d.ellipse((cx+s*.15,cy-s*.28,cx+s*.36,cy+.02*s),fill=(170,155,122,255)); d.arc((cx+s*.16,cy-s*.42,cx+s*.34,cy-s*.16),170,330,fill=(93,75,52,255),width=7); d.arc((cx+s*.28,cy-s*.42,cx+s*.46,cy-s*.16),210,20,fill=(93,75,52,255),width=7)
        for x in (-.20,.05): d.line((cx+s*x,cy+s*.14,cx+s*(x-.03),cy+s*.38),fill=(104,90,69,255),width=8)
    elif kind=="fish":
        d.ellipse((cx-s*.34,cy-s*.12,cx+s*.26,cy+s*.16),fill=(91,135,147,255),outline=INK,width=4); d.polygon(((cx-s*.30,cy),(cx-s*.52,cy-s*.21),(cx-s*.52,cy+s*.21)),fill=(77,112,122,255)); d.polygon(((cx-.02*s,cy-s*.10),(cx+s*.10,cy-s*.29),(cx+s*.15,cy-s*.08)),fill=(79,119,130,255)); d.ellipse((cx+s*.18,cy-.04*s,cx+s*.23,cy+.01*s),fill=INK)
    else: # lizard
        d.ellipse((cx-s*.25,cy-s*.07,cx+s*.22,cy+s*.08),fill=(79,118,63,255),outline=INK,width=3); d.ellipse((cx+s*.17,cy-s*.07,cx+s*.35,cy+s*.06),fill=(87,126,69,255)); d.line((cx-s*.24,cy,cx-s*.52,cy+s*.12),fill=(73,104,57,255),width=10)
        for sign in (-1,1):
            for x in (-.10,.10): d.line((cx+s*x,cy, cx+s*(x+.11*sign),cy+s*.18*sign),fill=(70,101,55,255),width=6)
    return im.filter(ImageFilter.GaussianBlur(.25))

def food(kind,variant,size=(768,768)):
    im=canvas(size); d=ImageDraw.Draw(im); cx,cy=size[0]//2,size[1]//2; s=min(size)*.60; shadow(d,cx,cy+s*.30,s*.33,s*.055)
    cooked="cooked" in variant
    if kind=="coconut":
        if variant=="whole": d.ellipse((cx-s*.25,cy-s*.25,cx+s*.25,cy+s*.25),fill=(116,74,39,255),outline=INK,width=5)
        else:
            for off in (-.18,.18): d.ellipse((cx+s*off-s*.20,cy-s*.18,cx+s*off+s*.20,cy+s*.20),fill=(109,72,41,255),outline=INK,width=4); d.ellipse((cx-s*.34,cy-s*.10,cx+s*.02,cy+s*.13),fill=(241,233,208,255))
    elif kind=="fish":
        base=(157,95,54,255) if cooked else (80,132,146,255); d.ellipse((cx-s*.34,cy-s*.12,cx+s*.23,cy+s*.15),fill=base,outline=INK,width=4); d.polygon(((cx-s*.30,cy),(cx-s*.52,cy-s*.20),(cx-s*.52,cy+s*.20)),fill=base); d.ellipse((cx+s*.16,cy-.04*s,cx+s*.21,cy+.01*s),fill=INK)
        if cooked:
            for i in range(4): d.line((cx-s*.12+i*s*.08,cy-s*.10,cx-s*.08+i*s*.08,cy+s*.12),fill=(78,47,29,180),width=5)
    elif kind=="fruit":
        d.ellipse((cx-s*.23,cy-s*.16,cx+s*.05,cy+s*.17),fill=(221,150,47,255),outline=INK,width=4); d.ellipse((cx+s*.02,cy-s*.10,cx+s*.28,cy+s*.18),fill=(184,76,43,255),outline=INK,width=4); d.polygon(((cx-.12*s,cy-s*.18),(cx-.02*s,cy-s*.42),(cx+.05*s,cy-s*.18)),fill=GREEN)
    elif kind=="meat":
        base=(142,64,54,255) if not cooked else (125,76,42,255); d.polygon(((cx-s*.35,cy-s*.05),(cx-s*.14,cy-s*.28),(cx+s*.31,cy-s*.16),(cx+s*.37,cy+s*.16),(cx+.04*s,cy+s*.28),(cx-s*.31,cy+s*.15)),fill=base,outline=INK); d.ellipse((cx+s*.05,cy-s*.06,cx+s*.18,cy+s*.08),fill=(231,197,164,255))
    else:
        d.ellipse((cx-s*.34,cy-s*.07,cx+s*.34,cy+s*.24),fill=(70,65,52,255),outline=METAL,width=7); d.ellipse((cx-s*.28,cy-s*.12,cx+s*.28,cy+s*.15),fill=(146,78,42,255));
        for i in range(8):
            a=2*math.pi*i/8; d.ellipse((cx+math.cos(a)*s*.17-16,cy+math.sin(a)*s*.08-12,cx+math.cos(a)*s*.17+16,cy+math.sin(a)*s*.08+12),fill=(212,135,49,255))
    return im

def sky_support(kind,variant,size=(1024,512)):
    im=Image.new("RGBA",size,(0,0,0,0)); d=ImageDraw.Draw(im); w,h=size
    if kind=="cloud":
        r=random.Random(kind+variant); col=(48,62,68,210) if "storm" in variant else (191,205,202,185)
        for _ in range(18 if "storm" in variant else 12):
            x=r.randint(int(w*.18),int(w*.82)); y=r.randint(int(h*.24),int(h*.70)); rx=r.randint(60,160); ry=r.randint(28,75); d.ellipse((x-rx,y-ry,x+rx,y+ry),fill=col)
        im=im.filter(ImageFilter.GaussianBlur(10 if "storm" in variant else 16))
    elif kind=="disc":
        cx,cy=w//2,h//2; rr=int(h*.24); col=(255,208,92,240) if variant=="sun" else (225,231,218,235); d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),fill=col)
        glow=Image.new("RGBA",size,(0,0,0,0)); gd=ImageDraw.Draw(glow); gd.ellipse((cx-rr*2,cy-rr*2,cx+rr*2,cy+rr*2),fill=(col[0],col[1],col[2],80)); im=Image.alpha_composite(glow.filter(ImageFilter.GaussianBlur(34)),im)
    else:
        for i in range(7):
            y=int(h*(.30+i*.065)); d.arc((w*.05,y,w*.95,y+55),180,350,fill=(165,215,225,90 if variant=="calm" else 145),width=5 if variant=="calm" else 8)
    return im

# --- mesh helpers --------------------------------------------------------------------------
def blade_mesh(kind,variant):
    m=Mesh(); worn=variant=="worn"
    if kind=="axe":
        add_cylinder_between(m,(0,.02,0),(0,1.00,0),.045,"Wood",10,.037); add_box(m,(.11,.90,0),(.34,.20,.075),"Metal",yaw=0,roll=-8); add_box(m,(.25,.90,0),(.10,.28,.025),"Metal",roll=-8)
    elif kind=="machete":
        add_cylinder_between(m,(0,.02,0),(0,.32,0),.045,"Wood",9,.040); add_box(m,(.02,.68,0),(.075,.78,.035),"Metal",roll=-6); add_box(m,(.07,1.02,0),(.18,.12,.025),"Metal",roll=-12)
    elif kind=="saw":
        add_box(m,(-.28,.10,0),(.26,.16,.06),"Wood",yaw=0,roll=0); add_box(m,(.15,.12,0),(.72,.10,.025),"Metal",yaw=0,roll=-2)
        for i in range(12): add_box(m,(-.16+i*.055,.055,0),(.024,.050,.026),"Metal",roll=35)
    elif kind=="shovel":
        add_cylinder_between(m,(0,.25,0),(0,1.20,0),.035,"Wood",9,.030); add_box(m,(0,.12,0),(.32,.28,.045),"Metal",roll=0); add_torus(m,(0,1.29,0),.11,.025,"Wood",14,5,"z")
    elif kind=="binoculars":
        for x in (-.09,.09): add_cylinder_between(m,(x,.02,0),(x,.34,0),.075,"Char",14,.065); add_box(m,(0,.18,0),(.13,.10,.10),"Metal"); add_torus(m,(0,.35,.02),.12,.008,"Rope",14,4,"z")
    else: # compass
        add_cylinder_between(m,(0,.02,0),(0,.07,0),.19,"Metal",18,.19); add_torus(m,(0,.075,0),.18,.012,"Metal",18,5,"y"); add_box(m,(0,.09,0),(.025,.014,.27),"Cloth",yaw=35)
    if worn:
        add_box(m,(.02,.18,-.04),(.11,.025,.07),"Cloth",yaw=14,roll=-5)
    return m

def workbench(variant):
    m=Mesh();
    # broad plank top + four uneven legs + shelf
    for i,z in enumerate((-.36,-.12,.12,.36)): add_box(m,(0,.84,z),(1.48,.075,.19),"Wood",yaw=(i%2)*1.2,roll=(i-1.5)*.6)
    for i,(x,z) in enumerate(((-.58,-.30),(.58,-.30),(-.58,.30),(.58,.30))): add_stick(m,(x,.02,z),(x+(.03 if i%2 else -.02),.82,z+.01),.055,"Wood",1300+i,8,3)
    add_box(m,(0,.37,0),(1.16,.055,.54),"Wood");
    # vice, hammer, rope and tool clutter
    add_box(m,(.45,.94,-.18),(.20,.18,.16),"Metal"); add_cylinder_between(m,(.55,.95,-.18),(.74,.95,-.18),.018,"Metal",7)
    add_torus(m,(-.40,.93,.10),.14,.012,"Rope",16,5,"y")
    add_cylinder_between(m,(-.15,.91,-.05),(.16,.91,.12),.020,"Wood",7); add_box(m,(.18,.91,.13),(.20,.08,.07),"Metal",yaw=31)
    if variant=="storm": add_box(m,(-.22,.985,-.18),(.46,.018,.24),"Cloth",yaw=8,roll=-3)
    return m

def tool_board(variant):
    m=Mesh(); add_box(m,(0,.72,0),(.94,1.25,.06),"Wood")
    for i,x in enumerate((-.30,-.10,.12,.31)):
        add_cylinder_between(m,(x,.38,-.05),(x,.92,-.05),.016,"Metal" if i%2 else "Wood",7); add_torus(m,(x,.96,-.05),.035,.007,"Metal",10,4,"z")
    if variant=="used": add_box(m,(.22,.58,-.075),(.26,.018,.12),"Cloth",yaw=-8,roll=0)
    return m

def comm_mesh(kind,variant):
    m=Mesh()
    if kind=="handheld_radio":
        add_box(m,(0,.30,0),(.32,.54,.16),"Char"); add_box(m,(0,.31,-.09),(.27,.40,.025),"Metal"); add_box(m,(0,.40,-.108),(.21,.10,.012),"Cloth"); add_torus(m,(-.06,.24,-.112),.065,.008,"Metal",14,4,"z")
        add_cylinder_between(m,(.10,.54,0),(.13,1.02,0),.012,"Metal",7); add_cylinder_between(m,(-.10,.58,-.02),(-.10,.66,-.02),.035,"Metal",10)
        if variant=="active": add_box(m,(.07,.41,-.118),(.05,.035,.008),"Fire")
    elif kind=="antenna_kit":
        if variant=="folded":
            for i in range(3): add_cylinder_between(m,(-.06+i*.06,.02,0),(-.06+i*.06,.74,0),.012,"Metal",7)
            add_torus(m,(.12,.22,0),.10,.009,"Rope",14,4,"z")
        else:
            add_cylinder_between(m,(0,.02,0),(0,1.70,0),.014,"Metal",8,.009); add_stick(m,(-.42,.02,0),(0,1.15,0),.020,"Wood",1401,7,3); add_stick(m,(.42,.02,0),(0,1.15,0),.020,"Wood",1402,7,3)
            add_cylinder_between(m,(0,1.30,0),(.45,1.30,0),.009,"Metal",6); add_cylinder_between(m,(0,1.46,0),(-.38,1.46,0),.008,"Metal",6)
    elif kind=="signal_lamp":
        add_cylinder_between(m,(0,.02,0),(0,.38,0),.15,"Metal",16,.14); add_torus(m,(0,.42,0),.15,.012,"Metal",16,5,"y"); add_cylinder_between(m,(0,.18,0),(0,.33,0),.085,"Cloth",14)
        if variant=="lit": add_cylinder_between(m,(0,.19,0),(0,.34,0),.07,"Fire",14)
        add_torus(m,(0,.55,0),.18,.012,"Metal",16,5,"z")
    else:
        for i,r in enumerate((.28,.22,.16)): add_torus(m,(0,.04+i*.035,0),r,.018,"Rope",20,5,"y")
        if variant=="loose": add_cylinder_between(m,(.20,.06,.08),(.76,.02,-.32),.010,"Rope",6)
    return m

SPRITE_SPECS=[
    ("AX-BG-001","Key art & backgrounds","Island daylight backdrop",["clear","golden_hour","storm"]),
    ("AX-BG-002","Key art & backgrounds","Camp night backdrop",["moonlit","firelit","lightning"]),
    ("AX-BG-003","Key art & backgrounds","Shoreline panorama",["calm","sunset","storm"]),
    ("AX-MAP-001","Maps & documents","Island overview map",["clean","marked","storm_route"]),
    ("AX-DOC-001","Maps & documents","Survival journal page",["camp","storm_annotated","signal"]),
    ("AX-DOC-002","Maps & documents","Radio repair sheet",["clean","annotated"]),
    ("AX-DOC-003","Maps & documents","Signal construction note",["clean","storm_annotated"]),
    ("AX-WLD-001","Animals & wildlife","Seabird / gull",["default"]),
    ("AX-WLD-002","Animals & wildlife","Tropical parrot",["default"]),
    ("AX-WLD-003","Animals & wildlife","Beach crab",["default"]),
    ("AX-WLD-004","Animals & wildlife","Wild boar",["default"]),
    ("AX-WLD-005","Animals & wildlife","Feral goat",["default"]),
    ("AX-WLD-006","Animals & wildlife","Reef fish",["default"]),
    ("AX-WLD-007","Animals & wildlife","Island lizard",["default"]),
    ("AX-FOOD-001","Food & cooking","Coconut",["whole","split"]),
    ("AX-FOOD-002","Food & cooking","Fish meal",["raw","cooked"]),
    ("AX-FOOD-003","Food & cooking","Island fruit",["mixed"]),
    ("AX-FOOD-004","Food & cooking","Meat ration",["raw","cooked"]),
    ("AX-FOOD-005","Food & cooking","Camp meal bowl",["cooked"]),
    ("AX-SKY-001","Weather & atmosphere","Cloud bank",["calm","storm"]),
    ("AX-SKY-002","Weather & atmosphere","Sun / moon disc",["sun","moon"]),
    ("AX-SKY-003","Weather & atmosphere","Shoreline spray band",["calm","storm"]),
]
MESH_SPECS=[
    ("AX-TOOL-001","Tools & crafting","Survival axe",["clean","worn"]),
    ("AX-TOOL-002","Tools & crafting","Machete",["clean","worn"]),
    ("AX-TOOL-003","Tools & crafting","Hand saw",["clean","worn"]),
    ("AX-TOOL-004","Tools & crafting","Shovel",["clean","worn"]),
    ("AX-TOOL-005","Tools & crafting","Binoculars",["clean","worn"]),
    ("AX-TOOL-006","Tools & crafting","Compass",["clean","worn"]),
    ("AX-CRAFT-001","Tools & crafting","Crafting workbench",["clean","storm"]),
    ("AX-CRAFT-002","Tools & crafting","Workbench tool board",["stocked","used"]),
    ("AX-COM-001","Radio & communication","Handheld radio",["off","active"]),
    ("AX-COM-002","Radio & communication","Antenna mast kit",["folded","deployed"]),
    ("AX-COM-003","Radio & communication","Signal lamp",["off","lit"]),
    ("AX-COM-004","Radio & communication","Cable coil",["coiled","loose"]),
]


def render_sprite(aid,name,variant):
    if aid.startswith("AX-BG-"):
        # map semantic variant onto the same painterly island renderer
        return backdrop(variant,(1536,768))
    if aid.startswith("AX-MAP-"): return map_sprite(variant)
    if aid.startswith("AX-DOC-001"): return document_sprite("journal",variant)
    if aid.startswith("AX-DOC-002"): return document_sprite("radio",variant)
    if aid.startswith("AX-DOC-003"): return document_sprite("signal",variant)
    if aid.startswith("AX-WLD-"):
        kinds={"AX-WLD-001":"gull","AX-WLD-002":"parrot","AX-WLD-003":"crab","AX-WLD-004":"boar","AX-WLD-005":"goat","AX-WLD-006":"fish","AX-WLD-007":"lizard"}; return wildlife(kinds[aid])
    if aid.startswith("AX-FOOD-"):
        kinds={"AX-FOOD-001":"coconut","AX-FOOD-002":"fish","AX-FOOD-003":"fruit","AX-FOOD-004":"meat","AX-FOOD-005":"meal"}; return food(kinds[aid],variant)
    if aid=="AX-SKY-001": return sky_support("cloud",variant)
    if aid=="AX-SKY-002": return sky_support("disc",variant)
    return sky_support("spray",variant)

def render_mesh(aid,variant):
    if aid.startswith("AX-TOOL-"):
        kinds={"AX-TOOL-001":"axe","AX-TOOL-002":"machete","AX-TOOL-003":"saw","AX-TOOL-004":"shovel","AX-TOOL-005":"binoculars","AX-TOOL-006":"compass"}; return blade_mesh(kinds[aid],variant)
    if aid=="AX-CRAFT-001": return workbench(variant)
    if aid=="AX-CRAFT-002": return tool_board(variant)
    kinds={"AX-COM-001":"handheld_radio","AX-COM-002":"antenna_kit","AX-COM-003":"signal_lamp","AX-COM-004":"cable"}; return comm_mesh(kinds[aid],variant)


def main():
    entries=[]
    for aid,category,name,variants in SPRITE_SPECS:
        for variant in variants:
            ext="png"; folder=slug(category); filename=f"{aid.lower()}_{slug(name)}__{slug(variant)}.{ext}"; path=SPR/folder/filename
            im=render_sprite(aid,name,variant); save_sprite(im,path)
            entries.append({"asset_id":aid,"category":category,"name":name,"variant":variant,"kind":"sprite","path":str(path.relative_to(ROOT)).replace('\\','/'),"dimensions":list(im.size)})
    for aid,category,name,variants in MESH_SPECS:
        for variant in variants:
            folder=slug(category); filename=f"{aid.lower()}_{slug(name)}__{slug(variant)}.obj"; path=MESH/folder/filename
            mesh=render_mesh(aid,variant); save_mesh(mesh,path)
            entries.append({"asset_id":aid,"category":category,"name":name,"variant":variant,"kind":"mesh","path":str(path.relative_to(ROOT)).replace('\\','/'),"vertices":len(mesh.verts),"faces":len(mesh.faces)})
    DOCS.mkdir(parents=True,exist_ok=True); MANIFEST.write_text(json.dumps({"version":1,"reference":"approved Project OEN mockup asset atlas","entry_count":len(entries),"asset_id_count":len({e['asset_id'] for e in entries}),"entries":entries},indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(f"Mockup atlas expansion: {len(entries)} files / {len({e['asset_id'] for e in entries})} asset families")
    return 0

if __name__=="__main__": raise SystemExit(main())
