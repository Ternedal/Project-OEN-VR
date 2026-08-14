#!/usr/bin/env python3
"""Generate Project ØEN production-oriented Unity art assets.

Reads tools/generated_art/asset_master.csv and materializes every master-list row as
one or more separate Unity-importable files. 2D/UI rows become transparent PNGs;
world rows become OBJ meshes using shared stylized materials. Variants/states are
exported as individual files rather than contact sheets.

Only Pillow + stdlib are required so GitHub Actions can reproduce the pack.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
import csv, hashlib, json, math, random, re, shutil, unicodedata

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1] if (HERE / 'asset_master.csv').exists() else HERE
MASTER = HERE / 'asset_master.csv'
if not MASTER.exists():
    # Local QA fallback used outside the repo.
    MASTER = Path('/mnt/data/Project_OEN_Asset_Master_List_v1.0/02_PROJECT_OEN_ASSET_MASTER_LIST.csv')
OUT = ROOT / 'Assets' / 'ProjectOEN' / 'ProductionArt'

SPRITE_CATEGORIES = {
    'Branding & identity',
    'Wrist UI & player status',
    'Planning board & phase UI',
    'Resource icons & inventory support',
    'Interaction markers & helper UI',
    'Menus & meta screens',
    'VFX support graphics',
}
WORLD_CATEGORIES = {'Props & tools', 'Construction states', 'Environment set dressing'}

P = {
    'ink': (23, 29, 29, 255),
    'ink2': (35, 45, 45, 255),
    'ivory': (231, 220, 191, 255),
    'cream': (245, 236, 209, 255),
    'teal': (47, 93, 104, 255),
    'teal2': (70, 126, 137, 255),
    'rust': (139, 76, 43, 255),
    'gold': (193, 144, 66, 255),
    'green': (77, 105, 65, 255),
    'green2': (106, 132, 78, 255),
    'blue': (62, 101, 122, 255),
    'cold': (121, 184, 204, 255),
    'red': (151, 55, 43, 255),
    'orange': (231, 111, 37, 255),
    'yellow': (248, 189, 69, 255),
    'wood': (105, 73, 45, 255),
    'wood2': (143, 100, 59, 255),
    'rope': (171, 139, 91, 255),
    'stone': (104, 111, 108, 255),
    'metal': (92, 104, 104, 255),
}


def slug(s: str) -> str:
    s = s.lower().replace('ø', 'oe').replace('å', 'aa').replace('æ', 'ae')
    s = s.replace('–', '-').replace('—', '-')
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '_', s).strip('_')[:84] or 'default'


def guid_for(path: str) -> str:
    return hashlib.md5(('ProjectOEN.ProductionArt.v2:' + path).encode()).hexdigest()


def font(size: int, bold=False):
    candidates = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf',
    ]
    for c in candidates:
        try:
            return ImageFont.truetype(c, size)
        except OSError:
            pass
    return ImageFont.load_default()


def variants_for(row: dict) -> list[str]:
    raw = (row.get('states_variants') or '').strip()
    if not raw or raw.lower() in {'default', 'available', 'warning'}:
        return [raw.lower() or 'default']
    # Construction rows already encode their state in the asset name.
    if re.match(r'^state\s+\d+\s+of\s+\d+$', raw.lower()):
        return ['default']
    vals = [v.strip() for v in raw.split(',') if v.strip()]
    if len(vals) <= 1:
        return [slug(raw)]
    return [slug(v) for v in vals]


def add_texture_noise(im: Image.Image, strength=0.12, seed='noise') -> Image.Image:
    rnd = random.Random(str(seed))
    # Pillow's effect_noise is fast and deterministic enough once offset/tint are fixed.
    n = Image.effect_noise((128,128), 36).convert('L').resize(im.size, Image.Resampling.BILINEAR)
    # Slightly break uniformity without changing transparent pixels.
    tint = Image.new('RGBA', im.size, (255, 246, 228, 0))
    # Never paint into transparent pixels: texture alpha is masked by source alpha.
    noise_alpha = n.point(lambda x: int(x * strength))
    src_alpha = im.getchannel('A')
    from PIL import ImageChops
    tint.putalpha(ImageChops.multiply(noise_alpha, src_alpha))
    out = Image.alpha_composite(im, tint)
    # Sparse scratches, also clipped to the original alpha footprint.
    scratches = Image.new('RGBA', im.size, (0,0,0,0)); sd = ImageDraw.Draw(scratches)
    for _ in range(max(8, im.width // 90)):
        x = rnd.randint(0, im.width - 1); y = rnd.randint(0, im.height - 1)
        l = rnd.randint(max(6, im.width // 80), max(12, im.width // 25))
        a = rnd.randint(18, 55)
        sd.line((x, y, min(im.width - 1, x + l), y + rnd.randint(-3, 3)), fill=(245, 231, 194, a), width=max(1, im.width // 700))
    scratches.putalpha(ImageChops.multiply(scratches.getchannel('A'), src_alpha))
    return Image.alpha_composite(out, scratches)


def shadowed(base: Image.Image, layer: Image.Image, blur=18, offset=(0, 10), opacity=130):
    alpha = layer.getchannel('A')
    sh = Image.new('RGBA', base.size, (0, 0, 0, 0))
    blurred = alpha.filter(ImageFilter.GaussianBlur(blur))
    blurred = blurred.point(lambda p: p * opacity // 255)
    black = Image.new('RGBA', base.size, (0, 0, 0, 255))
    black.putalpha(blurred)
    sh.alpha_composite(black, offset)
    base.alpha_composite(sh)
    base.alpha_composite(layer)


def emblem_base(size=512, panel=False, square=False, seed='base'):
    im = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    layer = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    pad = int(size * 0.08)
    if panel:
        r = int(size * 0.055)
        d.rounded_rectangle((pad, pad * 1.5, size - pad, size - pad * 1.5), r, fill=(23,29,29,238), outline=P['rust'], width=max(5,size//120))
        d.rounded_rectangle((pad+14, pad*1.5+14, size-pad-14, size-pad*1.5-14), r-8, outline=(193,144,66,170), width=max(2,size//400))
    else:
        box = (pad, pad, size-pad, size-pad)
        if square:
            d.rounded_rectangle(box, int(size*.10), fill=(23,29,29,245), outline=P['rust'], width=max(6,size//120))
        else:
            d.ellipse(box, fill=(23,29,29,242), outline=P['rust'], width=max(6,size//120))
            d.ellipse((pad+18,pad+18,size-pad-18,size-pad-18), outline=(193,144,66,165), width=max(2,size//380))
    layer = add_texture_noise(layer, .05, seed)
    shadowed(im, layer, blur=size//45, offset=(0,size//80), opacity=150)
    return im


def draw_cracks(d, box, seed, count=12, color=(18,22,22,120), width=2):
    rnd = random.Random(str(seed))
    x0,y0,x1,y1 = box
    for _ in range(count):
        x = rnd.randint(x0,x1); y = rnd.randint(y0,y1)
        pts=[(x,y)]
        for _ in range(rnd.randint(2,5)):
            x += rnd.randint(-28,28); y += rnd.randint(10,35)
            pts.append((x,y))
        d.line(pts, fill=color, width=width)


def motif_heart(d,cx,cy,s,variant='normal'):
    col = P['red'] if variant not in ('critical','low') else ((112,39,34,255) if variant=='critical' else (177,77,53,255))
    r=int(80*s); y=int(25*s)
    d.ellipse((cx-r,cy-r-y,cx,cy-y),fill=col); d.ellipse((cx,cy-r-y,cx+r,cy-y),fill=col)
    d.polygon([(cx-r,cy-int(28*s)),(cx+r,cy-int(28*s)),(cx,cy+int(120*s))],fill=col)
    if variant=='critical':
        d.line((cx-25*s,cy-70*s,cx+10*s,cy-10*s,cx-5*s,cy+70*s), fill=P['cream'], width=max(4,int(10*s)))


def motif_moon_eye(d,cx,cy,s,variant='normal'):
    # Fatigue: crescent + closed eye, intentionally calm rather than horror.
    r=int(115*s)
    d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=P['ivory'])
    d.ellipse((cx-int(65*s),cy-int(125*s),cx+int(135*s),cy+int(85*s)),fill=P['ink'])
    eyey=cy+int(58*s)
    d.arc((cx-int(70*s),eyey-int(38*s),cx+int(70*s),eyey+int(34*s)),10,170,fill=P['ivory'],width=max(5,int(11*s)))
    for i in (-48,-24,0,24,48):
        d.line((cx+i*s,eyey+14*s,cx+i*1.08*s,eyey+37*s), fill=P['ivory'], width=max(3,int(5*s)))
    if variant in ('tired','exhausted'):
        for i in range(3):
            x=cx+int((48+i*34)*s); y=cy-int((80-i*14)*s)
            d.polygon([(x,y-int(10*s)),(x+int(7*s),y),(x,y+int(10*s)),(x-int(7*s),y)],fill=P['cold'])


def motif_drop(d,cx,cy,s,variant='wet'):
    col=P['cold'] if variant in ('freezing','cold') else P['blue']
    pts=[(cx,cy-int(130*s)),(cx-int(85*s),cy+int(5*s)),(cx,cy+int(125*s)),(cx+int(85*s),cy+int(5*s))]
    d.polygon(pts,fill=col,outline=P['ivory'])
    d.ellipse((cx-int(85*s),cy-int(15*s),cx+int(85*s),cy+int(150*s)),fill=col,outline=P['ivory'],width=max(3,int(6*s)))
    if variant in ('freezing','cold'):
        for a in range(0,360,60):
            ang=math.radians(a); x=cx+int(math.cos(ang)*115*s); y=cy+int(math.sin(ang)*115*s)
            d.line((cx,cy,x,y),fill=P['cream'],width=max(3,int(6*s)))


def motif_cross(d,cx,cy,s,variant='minor'):
    w=int(34*s); l=int(125*s)
    d.rounded_rectangle((cx-w,cy-l,cx+w,cy+l),max(4,int(8*s)),fill=P['ivory'])
    d.rounded_rectangle((cx-l,cy-w,cx+l,cy+w),max(4,int(8*s)),fill=P['ivory'])
    if variant in ('severe','critical'):
        d.line((cx-int(100*s),cy-int(35*s),cx+int(92*s),cy+int(48*s)),fill=P['red'],width=max(8,int(17*s)))
        d.line((cx-int(78*s),cy+int(25*s),cx+int(60*s),cy-int(50*s)),fill=(111,37,31,220),width=max(4,int(9*s)))


def motif_flame(d,cx,cy,s,variant='strong'):
    scale={'out':.0,'ember':.35,'low':.62,'small_flame':.62,'strong':1.0,'strong_flame':1.0,'nearly_out':.28,'wet':.20}.get(variant, .82)
    # logs
    for off,ang in [(-20,-18),(20,18)]:
        x0=cx-int(105*s); x1=cx+int(105*s); y=cy+int(70*s+off*s)
        d.rounded_rectangle((x0,y-int(18*s),x1,y+int(18*s)),int(12*s),fill=P['wood2'],outline=P['ink'],width=max(3,int(5*s)))
    if scale <= 0:
        return
    ss=s*scale
    pts=[(cx,cy-int(145*ss)),(cx-int(60*ss),cy-int(25*ss)),(cx-int(38*ss),cy+int(70*ss)),(cx,cy+int(108*ss)),(cx+int(66*ss),cy+int(35*ss)),(cx+int(42*ss),cy-int(45*ss))]
    d.polygon(pts,fill=P['orange'])
    d.polygon([(cx,cy-int(78*ss)),(cx-int(22*ss),cy+int(15*ss)),(cx,cy+int(65*ss)),(cx+int(28*ss),cy-int(5*ss))],fill=P['yellow'])


def motif_shelter(d,cx,cy,s,variant='intact'):
    wood=P['wood2']; w=max(5,int(12*s))
    xL=cx-int(145*s); xR=cx+int(145*s); yB=cy+int(120*s); yT=cy-int(100*s)
    d.line((xL,yB,cx-int(65*s),yT),fill=wood,width=w); d.line((xR,yB,cx+int(65*s),yT),fill=wood,width=w)
    d.line((cx-int(65*s),yT,cx+int(65*s),yT),fill=wood,width=w)
    d.polygon([(cx-int(85*s),yT+int(10*s)),(cx+int(85*s),yT+int(10*s)),(xR-int(10*s),yB-int(20*s)),(xL+int(10*s),yB-int(20*s))],fill=P['teal'],outline=P['ivory'])
    if variant in ('weakened','damaged'):
        d.line((cx-int(40*s),cy-int(40*s),cx+int(35*s),cy+int(45*s)),fill=P['red'],width=max(4,int(8*s)))
    if variant=='damaged':
        d.polygon([(cx+20*s,cy-75*s),(cx+85*s,cy-70*s),(cx+55*s,cy-5*s)],fill=(0,0,0,0))


def motif_beacon(d,cx,cy,s,variant='ready'):
    w=max(5,int(12*s)); base=cy+int(125*s)
    d.line((cx-int(105*s),base,cx,cy-int(125*s)),fill=P['wood2'],width=w)
    d.line((cx+int(105*s),base,cx,cy-int(125*s)),fill=P['wood2'],width=w)
    for yy in (-40,15,70): d.line((cx-int(70*s),cy+int(yy*s),cx+int(70*s),cy+int(yy*s)),fill=P['rope'],width=max(3,int(7*s)))
    if variant in ('active','lit'):
        motif_flame(d,cx,cy-int(85*s),s*.42,'strong')
    elif variant in ('none','partial'):
        d.line((cx-int(40*s),cy+20*s,cx+int(40*s),cy+50*s),fill=P['rust'],width=max(3,int(7*s)))


def motif_radio(d,cx,cy,s,variant='good'):
    d.rounded_rectangle((cx-int(130*s),cy-int(95*s),cx+int(130*s),cy+int(110*s)),int(20*s),fill=(57,72,61,255),outline=P['rust'],width=max(4,int(9*s)))
    d.rectangle((cx-int(92*s),cy-int(55*s),cx+int(92*s),cy+int(10*s)),fill=P['ink'],outline=P['gold'],width=max(2,int(5*s)))
    d.line((cx-int(92*s),cy-int(95*s),cx-int(128*s),cy-int(185*s)),fill=P['metal'],width=max(4,int(8*s)))
    strength={'offline':0,'weak':1,'good':3}.get(variant,2)
    for i in range(3):
        x=cx+int((42+i*25)*s); y=cy+int(62*s); h=int((18+i*18)*s)
        d.rectangle((x,y-h,x+int(14*s),y),fill=P['gold'] if i<strength else (75,79,73,255))


def motif_rope(d,cx,cy,s):
    for r in (125,96,68):
        d.ellipse((cx-int(r*s),cy-int(r*.52*s),cx+int(r*s),cy+int(r*.52*s)),outline=P['rope'],width=max(5,int(14*s)))
        d.arc((cx-int(r*s),cy-int(r*.52*s),cx+int(r*s),cy+int(r*.52*s)),200,330,fill=P['teal2'],width=max(2,int(5*s)))
    d.line((cx+int(100*s),cy+int(20*s),cx+int(145*s),cy+int(115*s)),fill=P['rope'],width=max(5,int(13*s)))


def motif_logs(d,cx,cy,s,wet=False):
    for i,(off,ang) in enumerate([(-52,-7),(-16,3),(22,-4),(58,6)]):
        y=cy+int(off*s); col=(90,77,69,255) if wet else P['wood2']
        d.rounded_rectangle((cx-int(150*s),y-int(22*s),cx+int(150*s),y+int(22*s)),int(14*s),fill=col,outline=P['ink'],width=max(3,int(5*s)))
        d.ellipse((cx-int(152*s),y-int(22*s),cx-int(112*s),y+int(22*s)),fill=(162,117,68,255),outline=P['ink'])
    if wet:
        for x in (-90,0,95): d.ellipse((cx+x*s,cy-85*s,cx+(x+14)*s,cy-60*s),fill=P['cold'])


def motif_leaf(d,cx,cy,s):
    for a in (-38,-15,12,35):
        ang=math.radians(a)
        x=cx+int(math.cos(ang)*20*s); y=cy+int(math.sin(ang)*20*s)
        box=(x-int(135*s),y-int(48*s),x+int(135*s),y+int(48*s))
        d.ellipse(box,fill=P['green2'],outline=P['green'],width=max(2,int(5*s)))
        d.line((x-int(110*s),y,x+int(110*s),y),fill=P['cream'],width=max(2,int(4*s)))


def motif_stone(d,cx,cy,s):
    pts=[(cx-int(145*s),cy+int(70*s)),(cx-int(105*s),cy-int(55*s)),(cx-int(20*s),cy-int(120*s)),(cx+int(115*s),cy-int(55*s)),(cx+int(150*s),cy+int(72*s)),(cx+int(30*s),cy+int(125*s))]
    d.polygon(pts,fill=P['stone'],outline=P['ink'])


def motif_crate(d,cx,cy,s,variant='closed'):
    box=(cx-int(145*s),cy-int(105*s),cx+int(145*s),cy+int(105*s))
    d.rectangle(box,fill=P['wood2'],outline=P['ink'],width=max(5,int(9*s)))
    d.line((box[0],box[1],box[2],box[3]),fill=P['wood'],width=max(5,int(10*s)))
    d.line((box[2],box[1],box[0],box[3]),fill=P['wood'],width=max(5,int(10*s)))
    if variant=='open': d.rectangle((box[0]+20,box[1]+20,box[2]-20,cy),fill=P['ink'])
    if variant=='broken': d.line((cx-80*s,cy-80*s,cx+100*s,cy+55*s),fill=P['red'],width=max(5,int(10*s)))


def motif_hand(d,cx,cy,s,two=False):
    def one(xoff):
        d.rounded_rectangle((cx+xoff-int(58*s),cy-int(5*s),cx+xoff+int(65*s),cy+int(120*s)),int(25*s),fill=P['ivory'],outline=P['ink'],width=max(2,int(5*s)))
        for i in range(4):
            x=cx+xoff-int(75*s)+i*int(37*s)
            d.rounded_rectangle((x,cy-int(105*s),x+int(27*s),cy+int(28*s)),int(12*s),fill=P['ivory'],outline=P['ink'],width=max(2,int(4*s)))
    one(-70*s if two else 0)
    if two: one(70*s)


def motif_marker(d,cx,cy,s,variant='primary'):
    col=P['gold'] if variant not in ('warning','danger') else P['red']
    d.ellipse((cx-int(80*s),cy-int(110*s),cx+int(80*s),cy+int(50*s)),fill=col,outline=P['cream'],width=max(3,int(6*s)))
    d.polygon([(cx-int(62*s),cy+int(20*s)),(cx+int(62*s),cy+int(20*s)),(cx,cy+int(145*s))],fill=col)
    d.ellipse((cx-int(26*s),cy-int(55*s),cx+int(26*s),cy-int(3*s)),fill=P['ink'])


def panel_sprite(row, variant, size=(1024,512)):
    w,h=size; im=Image.new('RGBA',(w,h),(0,0,0,0)); layer=Image.new('RGBA',(w,h),(0,0,0,0)); d=ImageDraw.Draw(layer)
    pad=int(min(w,h)*.065); r=int(min(w,h)*.055)
    d.rounded_rectangle((pad,pad,w-pad,h-pad),r,fill=(25,31,30,246),outline=P['rust'],width=max(5,w//180))
    d.rounded_rectangle((pad+12,pad+12,w-pad-12,h-pad-12),max(8,r-8),outline=(193,144,66,180),width=2)
    for x in (w*.25,w*.5,w*.75): d.line((x,pad+25,x,h-pad-25),fill=(231,220,191,30),width=1)
    title=row['asset_name'].replace('–','-'); f=font(max(22,int(h*.065)),bold=True); d.text((pad+28,pad+22),title,fill=P['cream'],font=f)
    sub=variant.replace('_',' ').upper(); d.text((pad+30,pad+70),sub,fill=P['gold'],font=font(max(13,int(h*.034)),bold=True))
    lname=row['asset_name'].lower(); top=int(h*.34); bottom=int(h*.82)
    if 'time slots' in lname:
        gap=int(w*.035); slotw=int((w-2*(pad+45)-3*gap)/4); x0=pad+45
        for i in range(4):
            x=x0+i*(slotw+gap); d.rounded_rectangle((x,top,x+slotw,bottom),18,fill=(53,65,62,255),outline=P['gold'],width=3)
            d.text((x+slotw*.42,top+(bottom-top)*.32),str(i+1),font=font(max(26,int(h*.09)),True),fill=P['cream'])
    elif any(k in lname for k in ('planning board','camp summary','objective','weather card','consequence')):
        gap=int(w*.025); cardw=int((w-2*(pad+35)-3*gap)/4); x0=pad+35
        for i in range(4):
            x=x0+i*(cardw+gap); d.rounded_rectangle((x,top,x+cardw,bottom),18,fill=(54,65,61,245),outline=P['teal2'],width=3)
            rr=int(cardw*.25); cx=x+cardw//2; cy=top+int((bottom-top)*.38); d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),outline=P['gold'],width=5)
    else:
        for i in range(4):
            y=top+i*int((bottom-top)/4); d.rounded_rectangle((pad+90,y,w-pad-90,y+int(h*.08)),12,fill=(52,64,61,245),outline=P['teal2'],width=2)
    shadowed(im,layer,blur=10,offset=(0,6),opacity=130)
    return im


def icon_sprite(row, variant, size=1024):
    name=row['asset_name'].lower(); aid=row['asset_id']; cat=row['category']
    panel=('frame' in name or 'board' in name or 'screen' in name or 'panel' in name or 'track' in name or 'card' in name)
    if panel: return panel_sprite(row,variant)
    im=emblem_base(size, panel=False, square=('app icon' in name), seed=aid+variant)
    layer=Image.new('RGBA',im.size,(0,0,0,0)); d=ImageDraw.Draw(layer); cx=cy=size//2; s=size/512.0
    v=variant.lower()
    if aid=='BR-001' or 'primary logo' in name or 'secondary logo' in name or 'loading screen title' in name:
        # Island crescent mark + wordmark; transparent export.
        r=210*s
        d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=P['ivory'])
        d.ellipse((cx-80*s,cy-220*s,cx+260*s,cy+130*s),fill=P['ink'])
        if 'wordmark' in name or 'title' in name or aid=='BR-001':
            text='ØEN'; f=font(int(145*s),True); bb=d.textbbox((0,0),text,font=f); d.text((cx-(bb[2]-bb[0])/2,cy+160*s),text,fill=P['cream'],font=f)
    elif 'app icon' in name:
        motif_beacon(d,cx,cy,s*.75,'active')
    elif 'stamp' in name:
        d.ellipse((cx-170*s,cy-170*s,cx+170*s,cy+170*s),outline=P['ivory'],width=int(18*s)); motif_beacon(d,cx,cy,s*.55,'ready')
    elif 'typography ornament' in name:
        for y in (-90,0,90):
            d.line((cx-260*s,cy+y*s,cx+260*s,cy+y*s),fill=P['ivory'],width=max(3,int(7*s)))
            d.polygon([(cx,cy+(y-20)*s),(cx+20*s,cy+y*s),(cx,cy+(y+20)*s),(cx-20*s,cy+y*s)],fill=P['gold'])
    elif 'chapter' in name or 'day badge' in name:
        txt={'day_1':'DAY 1','day_2':'DAY 2','day_3':'DAY 3','stormnatten':'STORM'}.get(v,v.upper())
        f=font(int(92*s),True); bb=d.textbbox((0,0),txt,font=f); d.text((cx-(bb[2]-bb[0])/2,cy-45*s),txt,fill=P['cream'],font=f)
        motif_flame(d,cx,cy+130*s,s*.35,'low')
    elif 'health' in name: motif_heart(d,cx,cy,s,v)
    elif 'fatigue' in name: motif_moon_eye(d,cx,cy,s,v)
    elif 'cold' in name or 'wetness' in name: motif_drop(d,cx,cy,s,v)
    elif 'injury' in name: motif_cross(d,cx,cy,s,v)
    elif 'status ring' in name:
        frac={'full':1.0,'half':.5,'low':.25}.get(v,.75)
        d.arc((cx-180*s,cy-180*s,cx+180*s,cy+180*s),-90,-90+int(360*frac),fill=P['gold'],width=int(28*s))
    elif 'player 1' in name or 'player 2' in name:
        num='1' if '1' in name else '2'; f=font(int(210*s),True); bb=d.textbbox((0,0),num,font=f); d.text((cx-(bb[2]-bb[0])/2,cy-(bb[3]-bb[1])/2-30*s),num,fill=P['cream'],font=f)
    elif 'alert' in name or 'danger' in name:
        d.polygon([(cx,cy-165*s),(cx-170*s,cy+145*s),(cx+170*s,cy+145*s)],fill=P['rust'],outline=P['cream']); d.rectangle((cx-13*s,cy-55*s,cx+13*s,cy+65*s),fill=P['cream']); d.ellipse((cx-15*s,cy+88*s,cx+15*s,cy+118*s),fill=P['cream'])
    elif 'held indicator' in name or 'two-hand carry' in name: motif_hand(d,cx,cy,s*.75,two=('two-hand' in name or 'shared' in v))
    elif 'radio signal' in name or 'radio part' in name: motif_radio(d,cx,cy,s*.75,v)
    elif 'shelter integrity' in name or 'shelter needs' in name: motif_shelter(d,cx,cy,s*.72,v)
    elif 'fire strength' in name or 'fire needs' in name: motif_flame(d,cx,cy,s*.72,v)
    elif 'signal progress' in name: motif_beacon(d,cx,cy,s*.70,v)
    elif 'action token' in name:
        if 'gather' in name: motif_leaf(d,cx-30*s,cy-20*s,s*.55); motif_logs(d,cx+50*s,cy+70*s,s*.36)
        elif 'build' in name: motif_shelter(d,cx,cy,s*.65,'intact')
        elif 'scout' in name: motif_marker(d,cx,cy,s*.75,'primary')
        elif 'repair' in name: motif_cross(d,cx,cy,s*.65,'minor'); d.line((cx-110*s,cy+110*s,cx+105*s,cy-105*s),fill=P['gold'],width=int(18*s))
    elif 'risk marker' in name: motif_marker(d,cx,cy,s*.75,'danger' if v=='high' else 'warning' if v=='medium' else 'primary')
    elif 'resource requirement' in name:
        # Render each named variant if caller gives one; otherwise generic pips.
        if v=='wood': motif_logs(d,cx,cy,s*.55)
        elif v=='rope': motif_rope(d,cx,cy,s*.55)
        elif v=='fuel': motif_flame(d,cx,cy,s*.55,'low')
        elif v=='food': motif_leaf(d,cx,cy,s*.55)
        else: motif_radio(d,cx,cy,s*.52,'good')
    elif 'wood resource' in name or 'wet wood' in name: motif_logs(d,cx,cy,s*.60,wet=('wet' in name))
    elif 'rope resource' in name: motif_rope(d,cx,cy,s*.58)
    elif any(k in name for k in ('fiber','vines','leaves','fronds','herb')): motif_leaf(d,cx,cy,s*.60)
    elif 'stone resource' in name: motif_stone(d,cx,cy,s*.58)
    elif 'fuel' in name or 'tinder' in name: motif_flame(d,cx,cy,s*.60,'low')
    elif 'food ration' in name:
        motif_leaf(d,cx,cy-45*s,s*.45); d.rounded_rectangle((cx-115*s,cy+45*s,cx+115*s,cy+115*s),20,fill=P['rope'],outline=P['ink'])
    elif name == 'water icon': motif_drop(d,cx,cy,s*.72,v)
    elif 'parts' in name or 'metal scrap' in name or 'signal material' in name:
        for i in (-70,0,70): d.rounded_rectangle((cx+(i-24)*s,cy-110*s,cx+(i+24)*s,cy+110*s),10,fill=P['metal'],outline=P['cream'],width=max(2,int(4*s)))
    elif 'cloth' in name or 'rag' in name:
        d.polygon([(cx-150*s,cy-100*s),(cx+120*s,cy-130*s),(cx+160*s,cy+95*s),(cx-100*s,cy+130*s)],fill=P['teal'],outline=P['cream'])
    elif 'torch fuel' in name:
        d.rounded_rectangle((cx-62*s,cy-130*s,cx+62*s,cy+135*s),22,fill=P['metal'],outline=P['cream'],width=max(3,int(7*s))); motif_flame(d,cx,cy-150*s,s*.27,'strong')
    elif 'crate icon' in name: motif_crate(d,cx,cy,s*.60,v)
    elif 'carried weight' in name:
        d.ellipse((cx-70*s,cy-150*s,cx+70*s,cy-20*s),outline=P['cream'],width=int(18*s)); d.rounded_rectangle((cx-125*s,cy-25*s,cx+125*s,cy+160*s),30,fill=P['metal'])
    elif 'durability' in name:
        count={'full':5,'medium':3,'low':1}.get(v,4)
        for i in range(5): d.rounded_rectangle((cx+(-170+i*82)*s,cy-35*s,cx+(-110+i*82)*s,cy+35*s),12,fill=P['green2'] if i<count else (72,77,74,255))
    elif 'quantity counter' in name:
        d.rounded_rectangle((cx-150*s,cy-105*s,cx+150*s,cy+105*s),26,outline=P['gold'],width=int(12*s)); d.text((cx-35*s,cy-70*s),'12',font=font(int(100*s),True),fill=P['cream'])
    elif 'grab prompt' in name: motif_hand(d,cx,cy,s*.72)
    elif any(k in name for k in ('marker','ping','highlight','snap zone','anchor')): motif_marker(d,cx,cy,s*.72,'danger' if 'danger' in name else v)
    elif 'subtitle speaker' in name:
        d.polygon([(cx-125*s,cy-70*s),(cx-35*s,cy-70*s),(cx+50*s,cy-145*s),(cx+50*s,cy+145*s),(cx-35*s,cy+70*s),(cx-125*s,cy+70*s)],fill=P['ivory']); d.arc((cx-20*s,cy-125*s,cx+210*s,cy+125*s),-60,60,fill=P['gold'],width=int(13*s))
    elif 'pause' in name or 'reconnect' in name:
        if 'paused' in v: d.rectangle((cx-85*s,cy-145*s,cx-25*s,cy+145*s),fill=P['cream']); d.rectangle((cx+25*s,cy-145*s,cx+85*s,cy+145*s),fill=P['cream'])
        else:
            d.arc((cx-155*s,cy-155*s,cx+155*s,cy+155*s),25,325,fill=P['gold'],width=int(22*s)); d.polygon([(cx+135*s,cy-120*s),(cx+175*s,cy-35*s),(cx+88*s,cy-50*s)],fill=P['gold'])
    elif 'smoke' in name:
        for i in range(6):
            rr=int((70+i*8)*s); x=cx+int((-30+i*12)*s); y=cy+int((130-i*58)*s); d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=(165,169,165,max(35,135-i*14)))
    elif 'ember' in name or 'ash' in name:
        rnd=random.Random(aid+variant)
        for _ in range(45):
            x=rnd.randint(int(cx-180*s),int(cx+180*s)); y=rnd.randint(int(cy-180*s),int(cy+180*s)); rr=rnd.randint(3,12); col=P['orange'] if 'ember' in name else (180,183,177,170); d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=col)
    elif 'rain splash' in name:
        for a in range(0,360,35):
            ang=math.radians(a); d.line((cx,cy,cx+math.cos(ang)*170*s,cy+math.sin(ang)*80*s),fill=P['cold'],width=int(7*s)); motif_drop(d,cx,cy-80*s,s*.35,'wet')
    elif 'wet sheen' in name:
        d.ellipse((cx-190*s,cy-120*s,cx+190*s,cy+120*s),fill=(129,184,198,70)); d.arc((cx-180*s,cy-100*s,cx+150*s,cy+95*s),195,330,fill=P['cream'],width=int(16*s))
    elif 'lightning' in name:
        d.polygon([(cx+20*s,cy-170*s),(cx-85*s,cy+10*s),(cx-15*s,cy+10*s),(cx-70*s,cy+180*s),(cx+115*s,cy-40*s),(cx+30*s,cy-40*s)],fill=P['cream'])
    elif 'glow halo' in name or 'pulse ring' in name:
        for r,a in [(190,50),(150,80),(110,120)]: d.ellipse((cx-r*s,cy-r*s,cx+r*s,cy+r*s),outline=(248,189,69,a),width=int(22*s))
    else:
        # A usable, non-placeholder generic physical symbol: compass/island mark.
        d.polygon([(cx,cy-175*s),(cx+45*s,cy-45*s),(cx+175*s,cy),(cx+45*s,cy+45*s),(cx,cy+175*s),(cx-45*s,cy+45*s),(cx-175*s,cy),(cx-45*s,cy-45*s)],fill=P['ivory'])
        d.ellipse((cx-35*s,cy-35*s,cx+35*s,cy+35*s),fill=P['teal'])
    # Composite every recognized motif, not only the generic fallback.
    shadowed(im,layer,blur=max(10,size//60),offset=(0,size//70),opacity=135)
    return im


def texture(name: str, size=512):
    rnd=random.Random('tex:'+name)
    base_colors={
        'Wood': (119,83,50), 'Rope': (171,140,92), 'Tarp': (48,88,105), 'Metal': (91,103,103),
        'Stone': (101,106,103), 'Leaf': (73,105,62), 'Cloth': (96,84,68), 'Mud': (76,67,48),
        'Fire': (226,102,30), 'Char': (44,39,34), 'Water': (65,117,137)
    }
    rgb=base_colors[name]; im=Image.new('RGB',(size,size),rgb); d=ImageDraw.Draw(im)
    noise=Image.effect_noise((size,size),28).convert('L')
    tint=Image.merge('RGB',(noise,noise,noise))
    im=Image.blend(im,tint,0.10); d=ImageDraw.Draw(im)
    if name=='Wood':
        for y in range(18,size,34): d.line((0,y,size,y+rnd.randint(-5,5)),fill=(79,54,34),width=3)
        for _ in range(20):
            x=rnd.randint(0,size); y=rnd.randint(0,size); r=rnd.randint(5,16); d.ellipse((x-r,y-r,x+r,y+r),outline=(76,52,34),width=2)
    elif name=='Rope':
        for x in range(-size,size*2,24): d.line((x,0,x-size,size),fill=(116,88,58),width=8)
        for x in range(-size,size*2,24): d.line((x+7,0,x-size+7,size),fill=(205,174,121),width=3)
    elif name=='Tarp':
        for x in range(0,size,32): d.line((x,0,x,size),fill=(63,109,124),width=1)
        for y in range(0,size,32): d.line((0,y,size,y),fill=(38,72,87),width=1)
    elif name=='Metal':
        for _ in range(28):
            x=rnd.randint(0,size); y=rnd.randint(0,size); l=rnd.randint(20,90); d.line((x,y,min(size,x+l),y+rnd.randint(-3,3)),fill=(132,128,111),width=2)
    elif name=='Stone':
        for _ in range(16):
            x=rnd.randint(0,size); y=rnd.randint(0,size); d.line((x,y,x+rnd.randint(-70,70),y+rnd.randint(20,90)),fill=(69,73,72),width=2)
    elif name=='Leaf':
        for y in range(0,size,50): d.line((0,y,size,y+20),fill=(103,135,73),width=3)
    elif name=='Cloth':
        for x in range(0,size,14): d.line((x,0,x,size),fill=(123,106,80),width=1)
        for y in range(0,size,14): d.line((0,y,size,y),fill=(72,62,51),width=1)
    elif name=='Mud':
        for _ in range(40):
            x=rnd.randint(0,size); y=rnd.randint(0,size); r=rnd.randint(3,18); d.ellipse((x-r,y-r,x+r,y+r),fill=(86,77,56))
    return im


# ---------- OBJ mesh helpers ----------
@dataclass
class Mesh:
    verts: list
    uvs: list
    faces: list

    def __init__(self): self.verts=[]; self.uvs=[]; self.faces=[]
    def v(self,p,uv=(0,0)):
        self.verts.append(p); self.uvs.append(uv); return len(self.verts)
    def tri(self,a,b,c,mat): self.faces.append((a,b,c,mat))
    def quad(self,p0,p1,p2,p3,mat):
        a=self.v(p0,(0,0)); b=self.v(p1,(1,0)); c=self.v(p2,(1,1)); d=self.v(p3,(0,1)); self.tri(a,b,c,mat); self.tri(a,c,d,mat)


def rot(p, euler=(0,0,0)):
    x,y,z=p; rx,ry,rz=[math.radians(a) for a in euler]
    # X
    y,z=y*math.cos(rx)-z*math.sin(rx), y*math.sin(rx)+z*math.cos(rx)
    x,z=x*math.cos(ry)+z*math.sin(ry), -x*math.sin(ry)+z*math.cos(ry)
    x,y=x*math.cos(rz)-y*math.sin(rz), x*math.sin(rz)+y*math.cos(rz)
    return x,y,z


def tp(p,center,euler=(0,0,0)):
    q=rot(p,euler); return q[0]+center[0],q[1]+center[1],q[2]+center[2]


def add_box(m,center,size,mat='Wood',euler=(0,0,0)):
    sx,sy,sz=[v/2 for v in size]
    corners=[(-sx,-sy,-sz),(sx,-sy,-sz),(sx,sy,-sz),(-sx,sy,-sz),(-sx,-sy,sz),(sx,-sy,sz),(sx,sy,sz),(-sx,sy,sz)]
    c=[tp(p,center,euler) for p in corners]
    for a,b,cx,d in [(0,1,2,3),(5,4,7,6),(4,0,3,7),(1,5,6,2),(3,2,6,7),(4,5,1,0)]: m.quad(c[a],c[b],c[cx],c[d],mat)


def add_cylinder(m,center,radius,height,mat='Wood',segments=10,euler=(0,0,0)):
    h=height/2
    top=[]; bot=[]
    for i in range(segments):
        a=2*math.pi*i/segments
        bot.append(tp((math.cos(a)*radius,-h,math.sin(a)*radius),center,euler))
        top.append(tp((math.cos(a)*radius,h,math.sin(a)*radius),center,euler))
    for i in range(segments):
        j=(i+1)%segments; m.quad(bot[i],bot[j],top[j],top[i],mat)
    cb=tp((0,-h,0),center,euler); ct=tp((0,h,0),center,euler)
    for i in range(segments):
        j=(i+1)%segments
        a=m.v(cb,(.5,.5)); b=m.v(bot[j],(0,0)); c=m.v(bot[i],(1,0)); m.tri(a,b,c,mat)
        a=m.v(ct,(.5,.5)); b=m.v(top[i],(0,1)); c=m.v(top[j],(1,1)); m.tri(a,b,c,mat)


def add_torus(m,center,major,minor,mat='Rope',seg_major=18,seg_minor=6,euler=(90,0,0)):
    grid=[]
    for i in range(seg_major):
        a=2*math.pi*i/seg_major; row=[]
        for j in range(seg_minor):
            b=2*math.pi*j/seg_minor
            p=((major+minor*math.cos(b))*math.cos(a), minor*math.sin(b), (major+minor*math.cos(b))*math.sin(a))
            row.append(tp(p,center,euler))
        grid.append(row)
    for i in range(seg_major):
        ni=(i+1)%seg_major
        for j in range(seg_minor):
            nj=(j+1)%seg_minor; m.quad(grid[i][j],grid[ni][j],grid[ni][nj],grid[i][nj],mat)


def add_tarp_mesh(m,center,width,height,mat='Tarp',sag=.12,euler=(0,0,0),grid=4):
    pts=[]
    for y in range(grid+1):
        row=[]
        for x in range(grid+1):
            u=x/grid; v=y/grid
            px=(u-.5)*width; pz=(v-.5)*height
            py=-sag*(1-(2*u-1)**2)*(1-(2*v-1)**2)
            row.append(tp((px,py,pz),center,euler))
        pts.append(row)
    for y in range(grid):
        for x in range(grid): m.quad(pts[y][x],pts[y][x+1],pts[y+1][x+1],pts[y+1][x],mat)


def add_leaf_mesh(m,center,length=.9,width=.24,mat='Leaf',euler=(0,0,0)):
    # diamond leaf, double sided
    ps=[(-length/2,0,0),(0,0,width/2),(length/2,0,0),(0,0,-width/2)]
    ps=[tp(p,center,euler) for p in ps]; m.quad(*ps,mat); m.quad(ps[3],ps[2],ps[1],ps[0],mat)


def add_flame_quad(m,center,size=.55,euler=(0,0,0)):
    w=size*.45; h=size
    m.quad(tp((-w/2,0,0),center,euler),tp((w/2,0,0),center,euler),tp((w/2,h,0),center,euler),tp((-w/2,h,0),center,euler),'Fire')
    m.quad(tp((0,0,-w/2),center,euler),tp((0,0,w/2),center,euler),tp((0,h,w/2),center,euler),tp((0,h,-w/2),center,euler),'Fire')


def world_mesh(row,variant):
    aid=row['asset_id']; name=row['asset_name'].lower(); v=variant; m=Mesh(); rnd=random.Random(aid+v)
    scale={'small':.72,'medium':1.0,'large':1.32,'young':.72,'mature':1.0,'dense':1.3}.get(v,1.0)
    # Props
    if aid=='PR-001' or 'tarp / presenning' in name:
        if v=='folded': add_box(m,(0,.12,0),(.9,.12,.48),'Tarp',(0,12,3))
        else: add_tarp_mesh(m,(0,.55,0),1.8,1.35,'Tarp',.18 if v!='wet' else .28,(0,0,0),5)
    elif aid=='PR-002' or name=='rope coil':
        for off in (-.05,.06): add_torus(m,(0,.12+off,0),.43,.045,'Rope',20,6,(0,0,0))
    elif aid=='PR-003' or 'wood poles bundle' in name:
        for i in range(7): add_cylinder(m,((i%3-.8)*.15,.16+(i//3)*.11,0),.055,1.45,'Wood',8,(0,0,90+rnd.uniform(-4,4)))
        for x in (-.34,.34): add_torus(m,(x,.18,0),.17,.025,'Rope',14,5,(90,0,0))
    elif aid in ('PR-004','PR-020') or 'crate' in name or 'heavy box' in name:
        sx,sy,sz=(1.25,.75,.9) if aid=='PR-020' else (1.0,.65,.72); add_box(m,(0,sy/2,0),(sx,sy,sz),'Wood')
        for z in (-sz/2+.04,sz/2-.04): add_box(m,(0,sy*.62,z),(sx*.95,.08,.07),'Metal')
        if v=='broken': add_box(m,(0,sy+.05,0),(sx*.8,.07,.1),'Wood',(0,25,16))
    elif aid=='PR-005' or 'portable radio' in name:
        add_box(m,(0,.32,0),(.92,.55,.35),'Metal'); add_box(m,(0,.37,-.19),(.55,.18,.03),'Char')
        add_cylinder(m,(-.34,.78,0),.025,.85,'Metal',8,(0,0,12)); add_cylinder(m,(.31,.53,-.2),.07,.05,'Gold' if False else 'Metal',8,(90,0,0))
    elif aid=='PR-006' or 'first-aid' in name:
        add_box(m,(0,.18,0),(.72,.34,.52),'Cloth'); add_box(m,(0,.36,-.27),(.12,.13,.03),'Ivory' if False else 'Metal')
    elif aid=='PR-007' or 'canteen' in name:
        add_cylinder(m,(0,.34,0),.28,.62,'Metal',12); add_cylinder(m,(0,.69,0),.11,.16,'Metal',10)
    elif aid=='PR-008' or 'lantern' in name:
        add_cylinder(m,(0,.18,0),.26,.12,'Metal',10); add_cylinder(m,(0,.48,0),.18,.52,'Glass' if False else 'Water',10); add_cylinder(m,(0,.79,0),.23,.10,'Metal',10)
        add_torus(m,(0,.66,0),.34,.025,'Metal',16,5,(0,0,0))
    elif aid=='PR-009' or name=='torch':
        add_cylinder(m,(0,.55,0),.045,1.1,'Wood',8); add_cylinder(m,(0,1.12,0),.11,.25,'Cloth',9); 
        if v in ('lit','dying'): add_flame_quad(m,(0,1.24,0),.42 if v=='lit' else .26)
    elif aid=='PR-010' or 'stone pile' in name:
        for i in range({'small':5,'medium':9,'large':14}.get(v,9)):
            x=rnd.uniform(-.5,.5)*scale; z=rnd.uniform(-.4,.4)*scale; r=rnd.uniform(.12,.26)*scale; add_box(m,(x,r*.55,z),(r*1.7,r,r*1.4),'Stone',(rnd.uniform(-20,20),rnd.uniform(0,180),rnd.uniform(-20,20)))
    elif aid=='PR-011' or 'palm leaf pile' in name:
        for i in range(10 if v!='small' else 6): add_leaf_mesh(m,(rnd.uniform(-.35,.35),.03+i*.008,rnd.uniform(-.25,.25)),.9,.22,'Leaf',(rnd.uniform(-15,15),rnd.uniform(0,180),rnd.uniform(-8,8)))
    elif aid=='PR-012' or 'scrap metal' in name:
        for i in range(7): add_box(m,(rnd.uniform(-.35,.35),.1+i*.035,rnd.uniform(-.25,.25)),(rnd.uniform(.35,.75),.06,.08),'Metal',(0,rnd.uniform(0,180),rnd.uniform(-12,12)))
    elif aid=='PR-013' or 'cloth bundle' in name:
        add_box(m,(0,.18,0),(.72,.34,.45),'Cloth',(0,9,4)); add_torus(m,(0,.20,0),.27,.025,'Rope',16,5,(90,0,0))
    elif aid=='PR-014' or 'signal flag' in name:
        add_tarp_mesh(m,(.35,.85,0),.85,.62,'Cloth',.08,(0,0,90),4); add_cylinder(m,(0,.75,0),.035,1.5,'Wood',8)
    elif aid=='PR-015' or 'cook pot' in name:
        add_cylinder(m,(0,.22,0),.34,.42,'Metal',14); add_torus(m,(0,.48,0),.36,.025,'Metal',16,5,(0,0,0))
    elif aid=='PR-016' or 'water collector' in name:
        for x in (-.55,.55): add_cylinder(m,(x,.55,0),.035,1.1,'Wood',8)
        add_tarp_mesh(m,(0,1.0,0),1.25,.95,'Tarp',.18,(0,0,0),4); add_cylinder(m,(0,.22,0),.35,.42,'Metal',12)
    elif aid=='PR-017' or 'hammer' in name or 'mallet' in name:
        add_cylinder(m,(0,.45,0),.045,.9,'Wood',8); add_box(m,(0,.93,0),(.48,.22,.22),'Metal')
    elif aid=='PR-018' or 'knife' in name:
        add_box(m,(0,.2,0),(.13,.42,.10),'Wood'); add_box(m,(0,.63,0),(.08,.55,.025),'Metal',(0,0,-8))
    elif aid=='PR-019' or 'anchor point peg' in name:
        add_cylinder(m,(0,.48,0),.055,.95,'Metal',8); add_torus(m,(0,.92,0),.16,.035,'Metal',14,5,(90,0,0))
    # Construction states
    elif aid.startswith('CS-00') and 'shelter' in name:
        stage=int(aid.split('-')[1])
        # 3 A-frame poles + crossbar
        for x in (-.72,.72): add_cylinder(m,(x*.55,.72,0),.055,1.55,'Wood',8,(0,0,28 if x<0 else -28))
        add_cylinder(m,(0,1.42,0),.05,1.55,'Wood',8,(0,0,90))
        if stage>=2: add_cylinder(m,(0,.18,.55),.05,1.65,'Wood',8,(0,0,90)); add_cylinder(m,(0,.18,-.55),.05,1.65,'Wood',8,(0,0,90))
        if stage>=3: add_tarp_mesh(m,(0,1.02,0),1.65,1.55,'Tarp',.13,(0,0,0),4)
        if stage==4: add_box(m,(.25,.72,0),(.08,.9,.08),'Wood',(0,0,35))
        if stage>=5:
            for z in (-.58,.58): add_torus(m,(0,.58,z),.35,.018,'Rope',14,4,(90,0,0))
    elif aid.startswith('CS-0') and 'campfire' in name:
        stage=int(aid.split('-')[1])-5
        for i in range(8):
            a=2*math.pi*i/8; add_box(m,(math.cos(a)*.42,.11,math.sin(a)*.42),(.24,.16,.22),'Stone',(0,math.degrees(a),0))
        for ang in (-38,38): add_cylinder(m,(0,.21,0),.07,.82,'Wood',8,(0,0,90+ang))
        if stage>=2: add_box(m,(0,.24,0),(.38,.05,.32),'Char')
        if stage in (3,4): add_flame_quad(m,(0,.24,0),.65 if stage==4 else .42)
        if stage==5: add_tarp_mesh(m,(0,.23,0),.32,.25,'Water',.02,(0,0,0),2)
    elif aid.startswith('CS-01') and 'signal beacon' in name:
        stage=int(aid.split('-')[1])-10
        for x in (-.48,.48): add_cylinder(m,(x,.72,0),.055,1.55,'Wood',8,(0,0,20 if x<0 else -20))
        if stage>=2:
            for y in (.45,.78,1.08): add_cylinder(m,(0,y,0),.035,.98,'Rope',8,(0,0,90))
        if stage>=3:
            add_box(m,(0,1.40,0),(.55,.18,.55),'Wood')
            for i in range(5): add_cylinder(m,((i-2)*.09,1.55,0),.025,.45,'Wood',7,(0,0,90))
        if stage==4: add_flame_quad(m,(0,1.52,0),.75)
        if stage==5: add_cylinder(m,(.1,.82,0),.055,1.15,'Wood',8,(0,0,55))
    elif aid=='CS-016' or 'radio repair station' in name:
        add_box(m,(0,.38,0),(1.2,.12,.72),'Wood'); add_box(m,(-.25,.58,0),(.55,.34,.28),'Metal')
        for i in range(6): add_box(m,(.25+rnd.uniform(-.25,.35),.52+rnd.uniform(0,.08),rnd.uniform(-.25,.25)),(.12,.04,.06),'Metal',(0,rnd.uniform(0,180),0))
    # Environment
    elif aid=='EN-001' or 'shipwreck hull' in name:
        for i in range(7):
            z=(i-3)*.16; add_box(m,(0,.35,z),(2.2-i*.08,.18,.13),'Wood',(0,rnd.uniform(-9,9),rnd.uniform(-5,5)))
        for x in (-.9,.9): add_cylinder(m,(x,.45,0),.06,1.35,'Wood',8,(0,0,90))
    elif aid=='EN-002' or 'broken plank pile' in name or 'driftwood' in name:
        for i in range({'small':5,'medium':9,'large':14}.get(v,9)):
            add_box(m,(rnd.uniform(-.55,.55),.06+i*.025,rnd.uniform(-.38,.38)),(rnd.uniform(.65,1.45)*scale,.08,rnd.uniform(.08,.14)),'Wood',(rnd.uniform(-8,8),rnd.uniform(0,180),rnd.uniform(-12,12)))
    elif aid=='EN-003' or 'barrel' in name:
        add_cylinder(m,(0,.48,0),.36,.96,'Wood',12); 
        for y in (.15,.48,.81): add_torus(m,(0,y,0),.365,.018,'Metal',16,5,(0,0,0))
        if v=='broken': add_box(m,(.15,.82,0),(.45,.12,.12),'Wood',(0,20,25))
    elif aid=='EN-004' or 'rope debris' in name:
        for i in range(3 if v=='small' else 5): add_torus(m,(rnd.uniform(-.35,.35),.04+i*.02,rnd.uniform(-.25,.25)),rnd.uniform(.18,.38),.025,'Rope',16,5,(0,rnd.uniform(0,180),0))
    elif aid=='EN-005' or 'stone cluster' in name:
        for i in range({'small':5,'medium':9,'large':14}.get(v,9)):
            x=rnd.uniform(-.7,.7)*scale; z=rnd.uniform(-.5,.5)*scale; r=rnd.uniform(.15,.35)*scale; add_box(m,(x,r*.5,z),(r*1.7,r,r*1.5),'Stone',(rnd.uniform(-20,20),rnd.uniform(0,180),rnd.uniform(-20,20)))
    elif aid=='EN-007' or 'palm tree' in name:
        h=2.5*scale; add_cylinder(m,(0,h/2,0),.11*scale,h,'Wood',9,(0,0,-6 if v!='broken' else -28))
        if v!='broken':
            for a in range(0,360,45): add_leaf_mesh(m,(0,h,0),1.35*scale,.26*scale,'Leaf',(rnd.uniform(-12,12),a,rnd.uniform(-18,4)))
    elif aid in ('EN-008','EN-009','EN-010','EN-013') or any(k in name for k in ('frond','bush','vine','grass')):
        count={'small':5,'medium':9,'dense':15,'short':7,'hanging':10}.get(v,10)
        for i in range(count): add_leaf_mesh(m,(rnd.uniform(-.55,.55)*scale,rnd.uniform(.03,.42)*scale,rnd.uniform(-.4,.4)*scale),rnd.uniform(.55,.95)*scale,rnd.uniform(.12,.24)*scale,'Leaf',(rnd.uniform(-35,35),rnd.uniform(0,360),rnd.uniform(-20,20)))
    elif aid=='EN-011' or 'mud' in name or 'puddle' in name:
        add_tarp_mesh(m,(0,.008,0),1.5*scale,1.05*scale,'Mud',0,(0,0,0),3)
    elif aid in ('EN-012','EN-014') or 'rock wall' in name or 'cave wall' in name:
        for y in range(3):
            for x in range(4):
                add_box(m,((x-1.5)*.55*scale,.28+y*.48*scale,rnd.uniform(-.12,.12)),(.65*scale,.55*scale,.42*scale),'Stone',(rnd.uniform(-8,8),rnd.uniform(-12,12),rnd.uniform(-8,8)))
    elif aid=='EN-015' or 'cave floor debris' in name:
        for i in range(12):
            if i%2: add_box(m,(rnd.uniform(-.7,.7),.06,rnd.uniform(-.5,.5)),(rnd.uniform(.15,.35),rnd.uniform(.08,.15),rnd.uniform(.12,.28)),'Stone',(rnd.uniform(0,30),rnd.uniform(0,180),0))
            else: add_cylinder(m,(rnd.uniform(-.7,.7),.08,rnd.uniform(-.5,.5)),.035,rnd.uniform(.4,.8),'Wood',7,(0,rnd.uniform(0,180),90))
    elif aid in ('EN-016','EN-017','EN-018','EN-019','EN-020','EN-021','EN-022','EN-023','EN-024'):
        # Camp clusters assembled from the same coherent kit.
        if 'mat' in name or 'groundsheet' in name: add_tarp_mesh(m,(0,.02,0),1.35,.8,'Cloth',.03,(0,0,0),3)
        elif 'cooking' in name: add_cylinder(m,(0,.25,0),.28,.42,'Metal',12); add_cylinder(m,(-.42,.18,0),.05,.8,'Wood',7,(0,0,90)); add_cylinder(m,(.42,.18,0),.05,.8,'Wood',7,(0,0,90))
        elif 'storage' in name: add_box(m,(-.28,.25,0),(.72,.5,.58),'Wood'); add_box(m,(.35,.18,.1),(.42,.36,.38),'Cloth')
        elif 'signal hill' in name: 
            for i in range(5): add_cylinder(m,((i-2)*.12,.14,0),.04,.8,'Wood',7,(0,0,90)); add_torus(m,(0,.20,.2),.24,.022,'Rope',14,5,(90,0,0))
        elif 'rain catcher' in name:
            for x in (-.45,.45): add_cylinder(m,(x,.55,0),.035,1.1,'Wood',7); add_tarp_mesh(m,(0,1.0,0),1.0,.72,'Tarp',.15,(0,0,0),3)
        elif 'torch stand' in name: add_cylinder(m,(0,.55,0),.05,1.1,'Wood',7); add_flame_quad(m,(0,1.08,0),.35 if v=='lit' else .01)
        elif 'path marker' in name: add_cylinder(m,(0,.55,0),.04,1.1,'Wood',7); add_tarp_mesh(m,(.18,.9,0),.35,.24,'Cloth',.02,(0,0,90),2)
        elif 'storm damage' in name:
            for i in range(8): add_box(m,(rnd.uniform(-.65,.65),.06+i*.025,rnd.uniform(-.4,.4)),(rnd.uniform(.35,1.0),.07,.09),'Wood',(rnd.uniform(-10,10),rnd.uniform(0,180),rnd.uniform(-15,15)))
            add_tarp_mesh(m,(.15,.07,-.1),.8,.55,'Tarp',.08,(0,0,18),3)
        elif 'boundary rope' in name:
            for x in (-.65,.65): add_cylinder(m,(x,.38,0),.035,.76,'Wood',7); add_cylinder(m,(0,.55,0),.028,1.3,'Rope',7,(0,0,90))
    elif aid=='EN-025' or 'shoreline foam' in name:
        add_tarp_mesh(m,(0,.006,0),1.7,1.0,'Water',.0,(0,0,0),4)
    else:
        add_box(m,(0,.25,0),(1.0,.5,.7),'Wood')
    return m


def write_obj(mesh: Mesh, path: Path, mtl_rel='../../Materials/project_oen.mtl'):
    path.parent.mkdir(parents=True,exist_ok=True)
    lines=[f'mtllib {mtl_rel}', f'o {path.stem}']
    for v in mesh.verts: lines.append('v %.6f %.6f %.6f'%v)
    for uv in mesh.uvs: lines.append('vt %.6f %.6f'%uv)
    last=None
    for a,b,c,mat in mesh.faces:
        if mat!=last: lines.append('usemtl '+mat); last=mat
        lines.append(f'f {a}/{a} {b}/{b} {c}/{c}')
    path.write_text('\n'.join(lines)+'\n',encoding='utf-8')


def unity_meta(path: Path, kind: str, max_size=1024):
    rel=str(path.relative_to(ROOT)).replace('\\','/') if path.is_absolute() else str(path)
    g=guid_for(rel)
    if kind=='texture':
        return f'''fileFormatVersion: 2\nguid: {g}\nTextureImporter:\n  internalIDToNameTable: []\n  externalObjects: {{}}\n  serializedVersion: 13\n  mipmaps:\n    mipMapMode: 0\n    enableMipMap: 1\n  isReadable: 0\n  streamingMipmaps: 0\n  textureSettings:\n    serializedVersion: 2\n    filterMode: 1\n    aniso: 1\n    mipBias: 0\n    wrapU: 0\n    wrapV: 0\n    wrapW: 0\n  nPOTScale: 0\n  alphaIsTransparency: 1\n  textureType: 0\n  spriteMode: 0\n  alphaSource: 1\n  platformSettings:\n  - serializedVersion: 3\n    buildTarget: DefaultTexturePlatform\n    maxTextureSize: {max_size}\n    resizeAlgorithm: 0\n    textureFormat: -1\n    textureCompression: 1\n    compressionQuality: 70\n    crunchedCompression: 0\n    allowsAlphaSplitting: 0\n    overridden: 0\n  userData: Project OEN production art generated texture\n  assetBundleName: \n  assetBundleVariant: \n'''
    if kind=='sprite':
        return f'''fileFormatVersion: 2\nguid: {g}\nTextureImporter:\n  internalIDToNameTable: []\n  externalObjects: {{}}\n  serializedVersion: 13\n  mipmaps:\n    mipMapMode: 0\n    enableMipMap: 0\n  isReadable: 0\n  streamingMipmaps: 0\n  textureSettings:\n    serializedVersion: 2\n    filterMode: 1\n    aniso: 1\n    mipBias: 0\n    wrapU: 1\n    wrapV: 1\n    wrapW: 1\n  nPOTScale: 0\n  alphaIsTransparency: 1\n  textureType: 8\n  spriteMode: 1\n  spritePixelsToUnits: 100\n  alphaSource: 1\n  platformSettings:\n  - serializedVersion: 3\n    buildTarget: DefaultTexturePlatform\n    maxTextureSize: {max_size}\n    resizeAlgorithm: 0\n    textureFormat: -1\n    textureCompression: 1\n    compressionQuality: 80\n    crunchedCompression: 0\n    allowsAlphaSplitting: 0\n    overridden: 0\n  spriteSheet:\n    serializedVersion: 2\n    sprites: []\n    outline: []\n    physicsShape: []\n    bones: []\n    spriteID: 5e97eb03825dee720800000000000000\n    internalID: 0\n  spritePackingTag: ProjectOEN_ProductionArt\n  userData: Project OEN production art generated sprite\n  assetBundleName: \n  assetBundleVariant: \n'''
    if kind=='model':
        return f'''fileFormatVersion: 2\nguid: {g}\nModelImporter:\n  serializedVersion: 22200\n  internalIDToNameTable: []\n  externalObjects: {{}}\n  materials:\n    materialImportMode: 1\n    materialName: 0\n    materialSearch: 1\n  meshes:\n    lODScreenPercentages: []\n    globalScale: 1\n    meshCompression: 1\n    addColliders: 0\n    useFileUnits: 1\n    optimizeMeshPolygons: 1\n    optimizeMeshVertices: 1\n    weldVertices: 1\n    preserveHierarchy: 0\n  tangentSpace:\n    normalSmoothAngle: 60\n    normalImportMode: 0\n    tangentImportMode: 3\n  userData: Project OEN production art generated model\n  assetBundleName: \n  assetBundleVariant: \n'''
    return f'fileFormatVersion: 2\nguid: {g}\n'


def write_meta(path,kind,max_size=1024):
    Path(str(path)+'.meta').write_text(unity_meta(path,kind,max_size),encoding='utf-8')


def write_mtl(mat_dir: Path):
    mat_dir.mkdir(parents=True,exist_ok=True); texdir=mat_dir/'Textures'; texdir.mkdir(exist_ok=True)
    names=['Wood','Rope','Tarp','Metal','Stone','Leaf','Cloth','Mud','Fire','Char','Water']
    for name in names:
        p=texdir/(slug(name)+'_albedo.png'); texture(name if name not in ('Char',) else 'Metal').save(p,compress_level=6); write_meta(p,'texture',512)
    lines=[]
    kd={'Wood':(.47,.32,.19),'Rope':(.67,.54,.35),'Tarp':(.18,.34,.40),'Metal':(.36,.40,.40),'Stone':(.40,.42,.41),'Leaf':(.29,.41,.24),'Cloth':(.38,.32,.26),'Mud':(.29,.25,.18),'Fire':(1,.34,.04),'Char':(.12,.11,.10),'Water':(.25,.46,.54)}
    for name in names:
        lines += [f'newmtl {name}', 'Ka 0.080 0.080 0.080', 'Kd %.3f %.3f %.3f'%kd[name], 'Ks 0.050 0.050 0.050', 'Ns 12.0', f'map_Kd Textures/{slug(name)}_albedo.png', '']
    p=mat_dir/'project_oen.mtl'; p.write_text('\n'.join(lines),encoding='utf-8'); write_meta(p,'generic')


def main():
    if OUT.exists(): shutil.rmtree(OUT)
    (OUT/'Sprites').mkdir(parents=True,exist_ok=True); (OUT/'Meshes').mkdir(parents=True,exist_ok=True); (OUT/'Docs').mkdir(parents=True,exist_ok=True)
    write_mtl(OUT/'Materials')
    rows=list(csv.DictReader(MASTER.open(encoding='utf-8-sig')))
    manifest=[]; sprite_count=mesh_count=0
    for row in rows:
        variants=variants_for(row)
        cat=row['category']; aid=row['asset_id']; base=slug(row['asset_name']); cat_slug=slug(cat)
        for var in variants:
            suffix='' if var in ('default','available','warning') else '__'+slug(var)
            if cat in SPRITE_CATEGORIES:
                p=OUT/'Sprites'/cat_slug/f'{aid.lower()}_{base}{suffix}.png'; p.parent.mkdir(parents=True,exist_ok=True)
                im=icon_sprite(row,var)
                im.save(p,compress_level=6)
                write_meta(p,'sprite',2048 if max(im.size)>1024 else 1024)
                manifest.append({'asset_id':aid,'name':row['asset_name'],'category':cat,'variant':var,'kind':'sprite','path':str(p.relative_to(ROOT)).replace('\\','/'),'dimensions':list(im.size)})
                sprite_count+=1
            elif cat in WORLD_CATEGORIES:
                # Decal-oriented environment rows become both a plane mesh and shared material.
                p=OUT/'Meshes'/cat_slug/f'{aid.lower()}_{base}{suffix}.obj'
                m=world_mesh(row,var); write_obj(m,p); write_meta(p,'model')
                manifest.append({'asset_id':aid,'name':row['asset_name'],'category':cat,'variant':var,'kind':'mesh','path':str(p.relative_to(ROOT)).replace('\\','/'),'vertices':len(m.verts),'triangles':len(m.faces)})
                mesh_count+=1
    (OUT/'Docs'/'production_art_manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    (OUT/'Docs'/'README.md').write_text(f'''# Project ØEN Production Art\n\nGenerated from the canonical 148-row asset master. Every listed state/variant is exported as an individual Unity-importable file.\n\n- Separate sprites: **{sprite_count}**\n- Separate world meshes: **{mesh_count}**\n- Shared stylized Quest-friendly materials/textures: **11**\n- Source: `tools/generated_art/asset_master.csv`\n\nThe generated art deliberately uses coherent handmade wood/rope/tarp/metal/stone materials, diegetic-first UI, warm camp accents and cool storm accents. No Hunger/Thirst HUD assets are generated.\n''',encoding='utf-8')
    print(f'Generated {sprite_count} sprites and {mesh_count} meshes from {len(rows)} master rows')

if __name__=='__main__': main()
