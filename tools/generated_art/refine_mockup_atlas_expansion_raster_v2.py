#!/usr/bin/env python3
"""Derive atlas-expansion raster V2 from the approved Project ØEN reference panels.

The first expansion pass proved structural coverage but still looked too flat. The
approved atlas itself is the visual source of truth, so this pass takes curated source
panel crops committed under art_payloads/mockup_reference and separates / enlarges
those real reference forms into the existing expansion PNG paths.

No canonical IDs or Unity GUIDs change. Generated backgrounds preserve the cinematic
atlas scenes; maps/documents preserve the aged-paper look; wildlife and food are keyed
from the atlas' charcoal presentation background into transparent Unity billboards;
weather elements retain the exact atmosphere language of the reference sheet.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageStat

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PROD=ROOT/"Assets"/"ProjectOEN"/"ProductionArt"
REF=ROOT/"art_payloads"/"mockup_reference"
MANIFEST=PROD/"Docs"/"mockup_atlas_expansion_manifest.json"
REPORT=PROD/"Docs"/"mockup_atlas_raster_v2.json"

SOURCES={
 "keyart":"keyart.jpg",
 "maps":"maps_planning.jpg",
 "wildlife":"wildlife.jpg",
 "food":"food_cooking.jpg",
 "weather":"weather_atmosphere.jpg",
 "documents":"documents_notes.jpg",
}

# Hand-curated cells from the approved 1536x1024 atlas category panels. Coordinates
# are intentionally stored in source-panel pixels so the extraction stays deterministic.
KEYART={
 "island":(4,18,221,82),
 "sunset_jungle":(222,7,428,82),
 "storm_island":(428,8,720,82),
 "beach":(4,83,240,178),
 "night_camp":(241,83,380,178),
 "signal_tower":(381,83,548,178),
 "wreck_sunset":(549,83,720,178),
}
WILDLIFE={
 "gull":(47,18,113,70),
 "parrot":(139,17,184,80),
 "crab":(99,59,153,111),
 "boar":(4,87,85,151),
 "goat":(86,94,167,151),
 "fish":(42,54,107,91),
 "reptile":(72,132,124,163),  # sea-turtle / island-reptile family in the atlas
}
FOOD={
 "coconut":(167,15,229,70),
 "fish":(45,55,157,101),
 "fruit":(125,93,204,144),
 "meat":(95,15,165,58),
 "meal":(105,143,232,230),
}
WEATHER={
 "sun":(42,16,107,77),
 "cloud":(98,18,186,73),
 "storm_cloud":(100,5,215,81),
 "splash":(36,84,108,139),
 "mist":(111,87,179,139),
 "moon":(176,83,226,140),
 "sunset":(195,48,276,92),
 "night":(224,92,276,145),
}
DOCS={
 "map_page":(5,20,65,87),
 "field_photo":(66,22,125,84),
 "letter":(126,19,185,90),
 "note":(5,88,85,157),
 "sketch":(86,89,136,158),
 "photo":(136,90,190,143),
 "signal":(188,91,245,158),
}
MAPS={
 "main":(3,17,173,178),
 "secondary":(174,16,233,74),
 "legend":(173,74,234,113),
 "sketch":(173,112,236,178),
 "notes":(234,16,279,132),
 "compass":(235,132,280,179),
}


def font(size:int,bold=False):
    for p in (("/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf"),
              ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")):
        try:return ImageFont.truetype(p,size)
        except OSError:pass
    return ImageFont.load_default()


def load_sources():
    result={}
    for key,name in SOURCES.items():
        path=REF/name
        if not path.exists(): raise SystemExit(f"Missing approved mockup reference panel: {path.relative_to(ROOT)}")
        with Image.open(path) as src: result[key]=src.convert("RGB")
    return result


def crop(src:Image.Image,box,pad=0):
    x0,y0,x1,y1=box
    return src.crop((max(0,x0-pad),max(0,y0-pad),min(src.width,x1+pad),min(src.height,y1+pad)))


def cover_resize(im:Image.Image,size,focus_y=.5):
    tw,th=size; scale=max(tw/im.width,th/im.height); nw=max(1,int(im.width*scale)); nh=max(1,int(im.height*scale))
    big=im.resize((nw,nh),Image.Resampling.LANCZOS)
    x=max(0,(nw-tw)//2); y=max(0,min(nh-th,int((nh-th)*focus_y)))
    return big.crop((x,y,x+tw,y+th))


def contain_resize(im:Image.Image,size,margin=.08,bg=(0,0,0,0)):
    tw,th=size; mw=int(tw*(1-2*margin)); mh=int(th*(1-2*margin)); scale=min(mw/im.width,mh/im.height)
    nw=max(1,int(im.width*scale)); nh=max(1,int(im.height*scale)); item=im.resize((nw,nh),Image.Resampling.LANCZOS)
    out=Image.new("RGBA",size,bg); out.alpha_composite(item,((tw-nw)//2,(th-nh)//2)); return out


def polish(im:Image.Image,contrast=1.07,color=1.08,sharp=1.25):
    rgb=im.convert("RGB")
    rgb=ImageEnhance.Contrast(rgb).enhance(contrast); rgb=ImageEnhance.Color(rgb).enhance(color)
    rgb=rgb.filter(ImageFilter.UnsharpMask(radius=1.8,percent=int(100*sharp),threshold=3))
    return rgb.convert("RGBA")


def sample_border_bg(im:Image.Image):
    rgb=im.convert("RGB"); w,h=rgb.size; pixels=[]
    strip=max(2,min(w,h)//18)
    for y in range(h):
        for x in range(w):
            if x<strip or x>=w-strip or y<strip or y>=h-strip: pixels.append(rgb.getpixel((x,y)))
    if not pixels:return (47,50,49)
    # median-ish robust mean using channel medians from sorted lists
    cols=list(zip(*pixels)); return tuple(sorted(c)[len(c)//2] for c in cols)


def key_dark_background(im:Image.Image,soft=34,hard=72,shadow_floor=8):
    """Convert the atlas' charcoal presentation field to alpha while keeping subjects."""
    rgb=im.convert("RGB"); w,h=rgb.size; bg=sample_border_bg(rgb); alpha=Image.new("L",(w,h),0); ap=alpha.load(); px=rgb.load()
    for y in range(h):
        for x in range(w):
            r,g,b=px[x,y]; dist=math.sqrt((r-bg[0])**2+(g-bg[1])**2+(b-bg[2])**2)
            chroma=max(r,g,b)-min(r,g,b); lum=(r+g+b)/3
            # coloured / bright subjects separate easily; dark brown/black wildlife gets
            # extra weight from local luma/chroma difference so legs are not erased.
            score=dist+chroma*.42+max(0,lum-(sum(bg)/3))*.25
            a=int(max(0,min(255,(score-soft)/(hard-soft)*255))) if hard>soft else 255
            if score>hard:a=255
            elif score<soft:a=0
            ap[x,y]=a
    alpha=alpha.filter(ImageFilter.GaussianBlur(.65)).point(lambda p:0 if p<shadow_floor else min(255,int(p*1.08)))
    out=rgb.convert("RGBA"); out.putalpha(alpha)
    # Trim empty gutter before scaling; keep a little soft shadow/edge context.
    bbox=alpha.getbbox()
    if bbox:
        pad=max(2,min(w,h)//18); x0,y0,x1,y1=bbox; out=out.crop((max(0,x0-pad),max(0,y0-pad),min(w,x1+pad),min(h,y1+pad)))
    return out


def state_marker(im:Image.Image,variant:str,color=(235,145,47,220)):
    """Small restrained state mark for variants sharing one approved source motif."""
    if variant in ("default","clean","clear","whole","raw","calm","sun","moonlit","off"):return im
    out=im.copy(); d=ImageDraw.Draw(out,"RGBA"); w,h=out.size; r=max(7,min(w,h)//45); cx=w-int(w*.07); cy=int(h*.08)
    d.ellipse((cx-r*2,cy-r*2,cx+r*2,cy+r*2),fill=(12,20,21,155),outline=color,width=max(2,r//3))
    v=variant.lower()
    if any(k in v for k in ("storm","annotated","marked","lightning")): d.line((cx-r,cy-r,cx+r,cy+r),fill=color,width=max(3,r//2)); d.line((cx+r,cy-r,cx-r,cy+r),fill=color,width=max(3,r//2))
    elif any(k in v for k in ("cooked","firelit","golden","sunset","active")): d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=color)
    else: d.line((cx-r,cy,cx-.15*r,cy+r,cx+r,cy-r),fill=color,width=max(3,r//2))
    return out


def source_to_billboard(src,box,size=(768,768),variant="default",pad=2):
    item=crop(src,box,pad); item=key_dark_background(item)
    item=polish(item,1.06,1.08,1.15)
    return state_marker(contain_resize(item,size,.10),variant)


def keyart_image(src,which,size,variant):
    scene=crop(src,KEYART[which],0); scene=cover_resize(scene,size,.50); out=polish(scene,1.08,1.11,1.16)
    # Gentle edge vignette restores the cinematic panel feel lost during enlargement.
    w,h=size; mask=Image.new("L",size,0); md=ImageDraw.Draw(mask); md.ellipse((-w*.12,-h*.38,w*1.12,h*1.38),fill=255); mask=mask.filter(ImageFilter.GaussianBlur(max(18,int(h*.06))))
    dark=Image.new("RGBA",size,(7,15,16,255)); dark.putalpha(ImageChops.invert(mask).point(lambda p:int(p*.44))); out=Image.alpha_composite(out,dark)
    return state_marker(out,variant,(238,155,48,210))


def aged_paper_from_ref(src,box,size,variant,title=None):
    page=crop(src,box,1); page=cover_resize(page,size,.5); page=polish(page,1.04,.92,1.20)
    # Preserve real atlas paper/photo texture, then add only a tiny semantic title/state cue.
    d=ImageDraw.Draw(page,"RGBA")
    if title:
        fs=max(16,int(size[1]*.028)); d.rounded_rectangle((22,22,min(size[0]-22,22+fs*len(title)*.57),22+fs+16),radius=7,fill=(39,29,21,145)); d.text((30,27),title.upper(),font=font(fs,True),fill=(236,221,185,235))
    return state_marker(page,variant,(177,74,49,220))


def map_from_ref(src,size,variant):
    base=crop(src,MAPS["main"],0); base=cover_resize(base,size,.50); out=polish(base,1.05,1.05,1.20)
    d=ImageDraw.Draw(out,"RGBA"); w,h=size
    if variant in ("marked","storm_route"):
        pts=[(w*.28,h*.70),(w*.38,h*.58),(w*.48,h*.53),(w*.57,h*.40),(w*.69,h*.30)]
        col=(185,69,48,230) if variant=="storm_route" else (231,145,46,230); d.line(pts,fill=col,width=max(7,w//90),joint="curve")
        for x,y in pts[::2]:r=max(6,w//115);d.ellipse((x-r,y-r,x+r,y+r),fill=col)
    return state_marker(out,variant,(188,67,47,220))


def weather_sprite(src,which,size,variant):
    item=crop(src,WEATHER[which],2)
    if which in {"sunset","night"}:
        return state_marker(polish(cover_resize(item,size,.5),1.08,1.12,1.20),variant)
    item=key_dark_background(item,soft=26,hard=61)
    item=polish(item,1.08,1.05,1.18)
    return state_marker(contain_resize(item,size,.10),variant,(73,182,224,220))


def rebuild(entry,srcs):
    aid=str(entry["asset_id"]); variant=str(entry.get("variant","default")); dims=tuple(entry.get("dimensions",[768,768]))
    if aid=="AX-BG-001":
        which={"clear":"island","golden_hour":"sunset_jungle","storm":"storm_island"}[variant]; return keyart_image(srcs["keyart"],which,dims,variant)
    if aid=="AX-BG-002":
        which={"moonlit":"night_camp","firelit":"night_camp","lightning":"storm_island"}[variant]; out=keyart_image(srcs["keyart"],which,dims,variant)
        if variant=="firelit": out=ImageEnhance.Color(out).enhance(1.14)
        return out
    if aid=="AX-BG-003":
        which={"calm":"beach","sunset":"wreck_sunset","storm":"storm_island"}[variant]; return keyart_image(srcs["keyart"],which,dims,variant)
    if aid=="AX-MAP-001": return map_from_ref(srcs["maps"],dims,variant)
    if aid=="AX-DOC-001":
        box={"camp":DOCS["note"],"storm_annotated":DOCS["letter"],"signal":DOCS["signal"]}[variant]; return aged_paper_from_ref(srcs["documents"],box,dims,variant,"field notes")
    if aid=="AX-DOC-002":
        box=DOCS["sketch"] if variant=="annotated" else DOCS["map_page"]; return aged_paper_from_ref(srcs["documents"],box,dims,variant,"radio repair")
    if aid=="AX-DOC-003":
        box=DOCS["signal"] if variant=="storm_annotated" else DOCS["sketch"]; return aged_paper_from_ref(srcs["documents"],box,dims,variant,"signal plan")
    if aid.startswith("AX-WLD-"):
        key={"AX-WLD-001":"gull","AX-WLD-002":"parrot","AX-WLD-003":"crab","AX-WLD-004":"boar","AX-WLD-005":"goat","AX-WLD-006":"fish","AX-WLD-007":"reptile"}[aid]
        return source_to_billboard(srcs["wildlife"],WILDLIFE[key],dims,variant,2)
    if aid.startswith("AX-FOOD-"):
        key={"AX-FOOD-001":"coconut","AX-FOOD-002":"fish","AX-FOOD-003":"fruit","AX-FOOD-004":"meat","AX-FOOD-005":"meal"}[aid]
        out=source_to_billboard(srcs["food"],FOOD[key],dims,variant,2)
        # State variants share the exact approved food source but receive restrained
        # tint/state treatment rather than invented replacement art.
        if variant=="cooked": out=ImageEnhance.Color(out).enhance(.92)
        return out
    if aid=="AX-SKY-001":
        key="storm_cloud" if variant=="storm" else "cloud"; return weather_sprite(srcs["weather"],key,dims,variant)
    if aid=="AX-SKY-002": return weather_sprite(srcs["weather"],"sun" if variant=="sun" else "moon",dims,variant)
    if aid=="AX-SKY-003": return weather_sprite(srcs["weather"],"splash",dims,variant)
    return None


def main()->int:
    srcs=load_sources(); data=json.loads(MANIFEST.read_text(encoding="utf-8")); entries=data.get("entries",[]); report=[]; count=0
    for e in entries:
        if e.get("kind")!="sprite":continue
        out=rebuild(e,srcs)
        if out is None:continue
        path=ROOT/e["path"]; path.parent.mkdir(parents=True,exist_ok=True); out.convert("RGBA").save(path,compress_level=6); count+=1
        alpha=out.getchannel("A"); report.append({"asset_id":e["asset_id"],"variant":e["variant"],"path":e["path"],"alpha":list(alpha.getextrema()),"sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
    if count!=40: raise SystemExit(f"Expected to rebuild all 40 expansion sprites from approved atlas panels, rebuilt {count}")
    REPORT.write_text(json.dumps({"version":2,"source":"approved Project OEN atlas category panels","sprite_count":count,"entries":report},indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(f"Atlas expansion raster V2: rebuilt {count} sprites from approved reference source panels")
    return 0


if __name__=="__main__": raise SystemExit(main())
