#!/usr/bin/env python3
"""Generate Project ØEN runtime/preview PNG sprites from the asset master list.

Output is deterministic and intentionally compact for Git. These are implementation
sprites / visual placeholders. High-resolution source renders can replace individual
files later without changing paths or GUIDs.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import csv, hashlib, math, random, re, unicodedata

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MASTER = HERE / 'asset_master.csv'
OUT = ROOT / 'Assets' / 'ProjectOEN' / 'GeneratedArtRuntime256'
DOCS = ROOT / 'Assets' / 'ProjectOEN' / 'GeneratedArtRuntime256Docs'
SIZE = 256
random.seed(260812)

P = {
    'ivory': (232,220,190,255), 'rust': (142,78,43,255), 'dark': (22,29,29,255),
    'gold': (196,145,64,255), 'green': (79,105,63,255), 'blue': (65,105,122,255),
    'red': (156,59,45,255), 'wood': (106,73,44,255), 'rope': (168,136,88,255),
    'grey': (104,108,103,255), 'white': (240,236,220,255)
}

def slug(s: str) -> str:
    s=s.lower().replace('ø','oe').replace('å','aa').replace('æ','ae')
    s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode()
    return re.sub(r'[^a-z0-9]+','_',s).strip('_')[:72]

def guid_for(s: str) -> str:
    return hashlib.md5(s.encode()).hexdigest()

def canvas(panel=False):
    im=Image.new('RGBA',(SIZE,SIZE),(0,0,0,0)); d=ImageDraw.Draw(im)
    if panel:
        d.rounded_rectangle((12,22,244,234),9,fill=(22,29,29,238),outline=P['rust'],width=4)
        d.rounded_rectangle((20,30,236,226),7,outline=(196,145,64,170),width=1)
    else:
        d.ellipse((23,23,233,233),fill=(22,29,29,230),outline=P['rust'],width=6)
        d.ellipse((33,33,223,223),outline=(196,145,64,175),width=2)
    return im,d

def flame(d,cx,cy,s=1.0):
    pts=[(cx,cy-int(62*s)),(cx-int(28*s),cy-int(16*s)),(cx-int(19*s),cy+int(24*s)),
         (cx,cy+int(46*s)),(cx+int(28*s),cy+int(17*s)),(cx+int(20*s),cy-int(17*s))]
    d.polygon(pts,fill=(235,111,28,255))
    d.polygon([(cx,cy-int(31*s)),(cx-int(10*s),cy),(cx,cy+int(25*s)),(cx+int(12*s),cy-int(2*s))],fill=(255,201,77,255))

def logs(d,cx,cy,s=1.0):
    for off in (-14,10):
        d.rounded_rectangle((cx-int(51*s),cy+int(off*s)-9,cx+int(51*s),cy+int(off*s)+9),7,fill=P['wood'],outline=(58,42,30,255),width=2)

def heart(d,cx,cy):
    d.ellipse((cx-58,cy-46,cx,cy+12),fill=P['red']); d.ellipse((cx,cy-46,cx+58,cy+12),fill=P['red'])
    d.polygon([(cx-58,cy-16),(cx+58,cy-16),(cx,cy+72)],fill=P['red'])

def drop(d,cx,cy,color=(65,136,176,255)):
    d.polygon([(cx,cy-70),(cx-42,cy+4),(cx,cy+68),(cx+42,cy+4)],fill=color)
    d.ellipse((cx-42,cy-7,cx+42,cy+76),fill=color)

def bolt(d,cx,cy):
    d.polygon([(cx+6,cy-70),(cx-33,cy),(cx-6,cy),(cx-22,cy+68),(cx+39,cy-10),(cx+8,cy-10)],fill=(213,159,44,255))

def cross(d,cx,cy):
    d.rectangle((cx-14,cy-65,cx+14,cy+65),fill=P['ivory']); d.rectangle((cx-65,cy-14,cx+65,cy+14),fill=P['ivory'])

def rope(d,cx,cy):
    for r in (61,48,35): d.ellipse((cx-r,cy-int(r*.55),cx+r,cy+int(r*.55)),outline=P['rope'],width=7)
    d.line((cx+48,cy+8,cx+76,cy+57),fill=P['rope'],width=7)

def leaf(d,cx,cy):
    d.ellipse((cx-62,cy-29,cx+62,cy+29),fill=(78,123,64,255),outline=(45,78,42,255),width=2)
    d.line((cx-52,cy+18,cx+52,cy-18),fill=(218,211,170,180),width=2)

def stone(d,cx,cy):
    d.polygon([(cx-62,cy+29),(cx-43,cy-32),(cx-5,cy-56),(cx+50,cy-28),(cx+63,cy+34),(cx+12,cy+56)],fill=P['grey'],outline=(62,67,65,255))

def crate(d,cx,cy):
    d.rectangle((cx-61,cy-49,cx+61,cy+49),fill=(111,74,42,255),outline=(58,42,30,255),width=4)
    d.line((cx-61,cy-49,cx+61,cy+49),fill=(59,42,28,255),width=5); d.line((cx+61,cy-49,cx-61,cy+49),fill=(59,42,28,255),width=5)

def tarp(d,cx,cy):
    pts=[(cx-71,cy-42),(cx+65,cy-55),(cx+75,cy+54),(cx-59,cy+64)]
    d.polygon(pts,fill=(47,86,106,255),outline=(24,45,55,255))
    for x,y in pts: d.ellipse((x-4,y-4,x+4,y+4),fill=P['gold'])

def radio(d,cx,cy):
    d.rounded_rectangle((cx-61,cy-50,cx+61,cy+57),9,fill=(62,75,55,255),outline=(31,35,30,255),width=4)
    d.rectangle((cx-43,cy-28,cx+43,cy+5),fill=(18,28,24,255),outline=P['gold'],width=2)
    d.line((cx-46,cy-50,cx-65,cy-95),fill=(50,50,48,255),width=5)
    for i in range(4): d.line((cx-39,cy+24+i*8,cx+39,cy+24+i*8),fill=(25,27,24,255),width=3)

def shelter(d,cx,cy,stage=3):
    xL,xR,yB,yT=cx-72,cx+72,cy+55,cy-63
    d.line((xL,yB,xL+14,yT),fill=P['wood'],width=8); d.line((xR,yB,xR-14,yT),fill=P['wood'],width=8); d.line((xL+14,yT,xR-14,yT),fill=P['wood'],width=8)
    if stage>=2: d.line((xL,yB,xR,yB),fill=P['wood'],width=8)
    if stage>=3: tarp(d,cx,cy-5)
    if stage==4: d.line((cx-28,cy-34,cx+31,cy+23),fill=(28,30,30,255),width=6)
    if stage>=5:
        for yy in (-11,10,31): d.line((xL+8,cy+yy,xR-6,cy+yy),fill=P['rope'],width=3)

def beacon(d,cx,cy,stage=3):
    base=cy+66
    d.line((cx-55,base,cx,cy-77),fill=P['wood'],width=8); d.line((cx+55,base,cx,cy-77),fill=P['wood'],width=8)
    if stage>=2:
        for yy in (30,0,-30): d.line((cx-36,cy+yy,cx+36,cy+yy),fill=P['rope'],width=4)
    if stage>=3: d.ellipse((cx-31,cy-94,cx+31,cy-44),fill=(69,62,55,255),outline=P['rust'],width=4)
    if stage>=4: flame(d,cx,cy-66,.55)
    if stage==5: d.line((cx-35,cy-4,cx+35,cy+36),fill=(56,40,32,255),width=7)

def palm(d,cx,cy):
    d.line((cx,cy+70,cx+10,cy-27),fill=(102,72,45,255),width=11)
    for a in (-2.8,-2.3,-1.8,-1.3,-.8,-.3):
        d.line((cx+10,cy-27,cx+10+math.cos(a)*75,cy-27+math.sin(a)*47),fill=(61,111,57,255),width=6)

def render(row):
    name=(row['asset_name']+' '+row['notes']).lower(); cat=row['category'].lower(); states=row['states_variants'].lower()
    panel=any(k in cat for k in ('menus','planning board')) or any(k in name for k in ('panel','screen','board'))
    im,d=canvas(panel); cx=cy=128
    if 'health' in name or 'heart' in name: heart(d,cx,cy)
    elif 'fatigue' in name or 'energy' in name: bolt(d,cx,cy)
    elif 'cold' in name or 'wet' in name: drop(d,cx-18,cy+8); d.line((cx+23,cy-40,cx+23,cy+40),fill=P['ivory'],width=4); d.line((cx-15,cy,cx+61,cy),fill=P['ivory'],width=4)
    elif 'injury' in name or 'first-aid' in name or 'medical' in name: cross(d,cx,cy)
    elif 'shelter' in name: shelter(d,cx,cy,4 if 'damaged' in name else 5 if 'reinforced' in name or 'repaired' in name else 3)
    elif 'campfire' in name or 'fire strength' in name or ('fire' in name and 'signal' not in name): logs(d,cx,cy+35); flame(d,cx,cy-8,.8 if 'strong' in name else .58)
    elif 'signal beacon' in name or 'signal progress' in name or 'beacon' in name: beacon(d,cx,cy,4 if 'active' in name or 'lit' in name else 5 if 'damaged' in name else 3)
    elif 'radio' in name: radio(d,cx,cy)
    elif 'rope' in name: rope(d,cx,cy)
    elif 'wood' in name or 'plank' in name or 'driftwood' in name: logs(d,cx,cy)
    elif any(k in name for k in ('leaf','frond','herb','bush','vine')): leaf(d,cx,cy)
    elif any(k in name for k in ('stone','rock','cliff','cave')): stone(d,cx,cy)
    elif any(k in name for k in ('tarp','cloth','rag','flag')): tarp(d,cx,cy)
    elif any(k in name for k in ('crate','box','container','storage')): crate(d,cx,cy)
    elif 'water' in name or 'droplet' in name: drop(d,cx,cy)
    elif 'fuel' in name or 'tinder' in name: logs(d,cx,cy+27); flame(d,cx,cy-10,.5)
    elif any(k in name for k in ('food','ration','cooking','pot')):
        d.ellipse((70,107,186,163),fill=(72,61,49,255),outline=P['rust'],width=4); d.arc((66,73,190,139),180,360,fill=P['ivory'],width=3)
    elif any(k in name for k in ('metal','scrap','parts')):
        for off in (-36,0,36): d.rectangle((cx-52+off,cy-47,cx-28+off,cy+48),fill=(113,113,105,255),outline=(60,62,60,255),width=2)
    elif 'weight' in name:
        d.ellipse((95,65,161,126),outline=P['ivory'],width=7); d.rounded_rectangle((66,121,190,196),16,fill=P['grey'])
    elif 'durability' in name or 'quantity' in name:
        for i in range(5): d.rounded_rectangle((57+i*29,111,77+i*29,145),4,fill=P['green'] if i<4 else (65,68,66,255))
    elif any(k in name for k in ('grab','hand','carry','gesture')):
        d.rounded_rectangle((99,116,160,180),16,fill=P['ivory']);
        for i in range(4): d.rounded_rectangle((91+i*20,69,105+i*20,124),6,fill=P['ivory'])
    elif any(k in name for k in ('marker','objective','ping','anchor','snap zone')):
        d.ellipse((84,74,172,162),fill=P['gold']); d.polygon([(91,143),(165,143),(128,213)],fill=P['gold']); d.ellipse((111,101,145,135),fill=P['dark'])
    elif 'weather' in name or 'rain' in name:
        d.ellipse((64,90,157,145),fill=(95,110,117,255)); d.ellipse((112,72,188,145),fill=(95,110,117,255));
        for xx in (91,128,165): d.line((xx,153,xx-10,185),fill=(65,136,176,255),width=4)
    elif any(k in name for k in ('palm','vegetation','grass')): palm(d,cx,cy)
    elif any(k in name for k in ('mud','puddle','shoreline')): d.ellipse((48,100,208,172),fill=(78,70,52,190),outline=(121,112,85,220),width=3)
    elif 'smoke' in name:
        for i in range(5):
            r=25+i*4; x=cx+random.randint(-23,23); y=cy+44-i*26; d.ellipse((x-r,y-r,x+r,y+r),fill=(150,155,153,max(45,150-i*20)))
    elif any(k in name for k in ('ember','ash','glow','lightning')):
        for _ in range(20):
            x=random.randint(69,187); y=random.randint(69,187); r=random.randint(2,5); d.ellipse((x-r,y-r,x+r,y+r),fill=(236,125,31,random.randint(110,255)))
    elif any(k in name for k in ('main menu','lobby','pause','settings','scenario','summary','credits')):
        for i in range(4): d.rounded_rectangle((59,73+i*31,197,93+i*31),4,fill=(52,63,61,245),outline=P['gold'],width=1)
    elif 'planning' in name or 'action token' in name or 'board' in name:
        d.rectangle((43,56,213,199),fill=(100,70,43,255),outline=(52,38,28,255),width=4)
        for i in range(4): d.ellipse((62+i*38,151,84+i*38,173),fill=P['gold'])
        d.line((59,86,197,86),fill=P['ivory'],width=3); d.line((59,113,171,113),fill=P['ivory'],width=3)
    elif any(k in name for k in ('logo','wordmark','badge','stamp','title','typography')):
        d.polygon([(49,171),(93,96),(128,133),(161,78),(208,171)],fill=P['ivory']); d.arc((40,45,216,198),190,350,fill=P['gold'],width=4)
    else: crate(d,cx,cy); d.ellipse((111,111,145,145),fill=P['gold'])
    # light grain
    for _ in range(180):
        x=random.randrange(SIZE); y=random.randrange(SIZE); d.point((x,y),fill=(255,245,220,random.randrange(5,22)))
    return im

def write_meta(path: Path):
    rel='Assets/'+str(path.relative_to(ROOT/'Assets')).replace('\\','/')
    guid=guid_for(rel)
    meta=f'''fileFormatVersion: 2\nguid: {guid}\nTextureImporter:\n  internalIDToNameTable: []\n  externalObjects: {{}}\n  serializedVersion: 13\n  mipmaps:\n    mipMapMode: 0\n    enableMipMap: 0\n  isReadable: 0\n  streamingMipmaps: 0\n  textureSettings:\n    serializedVersion: 2\n    filterMode: 1\n    aniso: 1\n    mipBias: 0\n    wrapU: 1\n    wrapV: 1\n    wrapW: 1\n  nPOTScale: 0\n  alphaIsTransparency: 1\n  textureType: 8\n  spriteMode: 1\n  spritePixelsToUnits: 100\n  alphaSource: 1\n  platformSettings:\n  - serializedVersion: 3\n    buildTarget: DefaultTexturePlatform\n    maxTextureSize: 256\n    resizeAlgorithm: 0\n    textureFormat: -1\n    textureCompression: 1\n    compressionQuality: 50\n    crunchedCompression: 0\n    allowsAlphaSplitting: 0\n    overridden: 0\n  spriteSheet:\n    serializedVersion: 2\n    sprites: []\n    outline: []\n    physicsShape: []\n    bones: []\n    spriteID: 5e97eb03825dee720800000000000000\n    internalID: 0\n  spritePackingTag: ProjectOEN_Runtime256\n  userData: Generated from Project OEN asset master list\n  assetBundleName: \n  assetBundleVariant: \n'''
    Path(str(path)+'.meta').write_text(meta,encoding='utf-8')
    return guid

def main():
    OUT.mkdir(parents=True,exist_ok=True); DOCS.mkdir(parents=True,exist_ok=True)
    rows=list(csv.DictReader(MASTER.open(encoding='utf-8')))
    manifest=[]
    for row in rows:
        folder=OUT/slug(row['category']); folder.mkdir(parents=True,exist_ok=True)
        path=folder/f"{row['asset_id'].lower().replace('-','_')}_{slug(row['asset_name'])}.png"
        im=render(row); im.save(path,optimize=True); guid=write_meta(path)
        manifest.append({**row,'unity_path':str(path.relative_to(ROOT)).replace('\\','/'),'guid':guid,'width':SIZE,'height':SIZE,'alpha':True,'origin':'generated_runtime_sprite'})
    import json
    (DOCS/'ASSET_MANIFEST.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    with (DOCS/'ASSET_MANIFEST.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(manifest[0].keys())); w.writeheader(); w.writerows(manifest)
    (DOCS/'README.md').write_text(f'''# Project ØEN Generated Art Runtime256\n\nGenerated **{len(rows)} separate transparent PNG sprites** from the canonical asset master list.\n\nThese are implementation/preview sprites, not a replacement for 3D world prefabs. File paths and GUIDs are stable so individual assets can be upgraded later without changing references.\n''',encoding='utf-8')
    print(f'Generated {len(rows)} Project OEN sprites in {OUT}')

if __name__=='__main__': main()
