#!/usr/bin/env python3
"""Atlas-aligned diegetic UI / sprite fidelity pass for Project ØEN.

The broad sprite generator and first refinement pass guarantee complete canonical
coverage, but visual review showed that many assets still read as generic templates.
This pass rebuilds every non-VFX production sprite around the approved mockup language:

- rugged dark wrist-device screens with cyan/green instrument light;
- distinct colour-coded circular status icons;
- physical wood/brass planning boards, cards, pins and tokens;
- recognisable resource silhouettes rather than abstract placeholders;
- cyan/orange holographic world interaction markers;
- distressed island/palm ØEN branding and rugged menu/meta panels.

Every state remains an individual transparent Unity sprite at its existing canonical
path and dimensions. VFX textures remain owned by refine_vfx_art.py.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PROD=ROOT/"Assets"/"ProductionArt"
MANIFEST=PROD/"Docs"/"production_art_manifest.json"
REPORT=PROD/"Docs"/"mockup_ui_v2.json"

INK=(13,20,21,255); INK2=(22,31,31,255); STEEL=(43,54,54,255)
TEAL=(39,111,126,255); CYAN=(24,184,230,255); CYAN2=(93,224,255,255)
GREEN=(116,190,70,255); ORANGE=(244,158,39,255); RED=(203,64,55,255)
IVORY=(236,224,190,255); BRASS=(181,132,61,255); WOOD=(101,70,42,255)
WOOD_DARK=(54,38,27,255); PAPER=(198,181,143,255); GREY=(129,139,134,255)
VFX_CATEGORY="VFX support graphics"


def font(size:int,bold=False):
    candidates=(
        "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    )
    for p in candidates:
        try:return ImageFont.truetype(p,size)
        except OSError:pass
    return ImageFont.load_default()


def rng(seed:str): return random.Random(int(hashlib.sha256(seed.encode()).hexdigest()[:16],16))

def norm_variant(v:str): return v.lower().replace("-","_").replace(" ","_")

def accent_for(variant:str, aid:str=""):
    v=norm_variant(variant)
    if any(k in v for k in ("critical","danger","failed","damaged","storm","severe","low")): return RED
    if any(k in v for k in ("wet","freezing","rain","reconnecting","weak","preview","hover")): return CYAN
    if any(k in v for k in ("active","selected","ready","valid","good","success","highlighted","full","placed")): return GREEN if aid.startswith("UI-") else ORANGE
    return ORANGE


def line_scaled(d,points,fill,width,scale=1.0): d.line(points,fill=fill,width=max(1,int(width*scale)),joint="curve")

def glow_layer(size,draw_fn,color=CYAN,blur=24):
    mask=Image.new("L",size,0); md=ImageDraw.Draw(mask); draw_fn(md,255)
    glow=mask.filter(ImageFilter.GaussianBlur(blur))
    layer=Image.new("RGBA",size,color); layer.putalpha(glow.point(lambda p:int(p*.58)))
    core=Image.new("RGBA",size,color); core.putalpha(mask)
    return Image.alpha_composite(layer,core)


def add_grain(im:Image.Image,seed:str,amount=18,alpha=22):
    r=rng(seed); w,h=im.size; noise=Image.new("RGBA",im.size,(0,0,0,0)); px=noise.load()
    # sparse deterministic speckle is cheaper than touching every pixel in CI
    for _ in range(max(1200,w*h//950)):
        x=r.randrange(w); y=r.randrange(h); v=r.randint(-amount,amount)
        c=255 if v>0 else 0; px[x,y]=(c,c,c,r.randint(3,alpha))
    return Image.alpha_composite(im,noise)


def scratches(im,seed,bbox,color=(220,205,170,38),count=18):
    r=rng(seed); d=ImageDraw.Draw(im,"RGBA"); x0,y0,x1,y1=bbox
    for _ in range(count):
        x=r.randint(x0,x1); y=r.randint(y0,y1); ln=r.randint(12,max(14,(x1-x0)//7))
        d.line((x,y,min(x1,x+ln),y+r.randint(-4,4)),fill=color,width=r.randint(1,2))


def rugged_panel(size,label:str,variant:str,wood=False,screen=True):
    w,h=size; im=Image.new("RGBA",size,(0,0,0,0)); d=ImageDraw.Draw(im)
    x0,y0,x1,y1=int(w*.07),int(h*.10),int(w*.93),int(h*.90)
    outer=WOOD_DARK if wood else (29,35,34,255); edge=BRASS if wood else (80,97,94,255)
    d.rounded_rectangle((x0,y0,x1,y1),radius=max(18,int(min(w,h)*.055)),fill=outer,outline=edge,width=max(3,int(min(w,h)*.008)))
    if wood:
        for i in range(11):
            yy=y0+int((i+1)*(y1-y0)/12); d.line((x0+18,yy,x1-18,yy+int(6*math.sin(i))),fill=(126,88,51,90),width=3)
    else:
        d.rounded_rectangle((x0+18,y0+18,x1-18,y1-18),radius=max(14,int(min(w,h)*.04)),fill=INK2,outline=TEAL,width=max(2,int(min(w,h)*.004)))
    if screen and not wood:
        sx0,sy0,sx1,sy1=x0+int((x1-x0)*.10),y0+int((y1-y0)*.22),x1-int((x1-x0)*.10),y1-int((y1-y0)*.12)
        d.rounded_rectangle((sx0,sy0,sx1,sy1),radius=12,fill=(8,27,31,255),outline=(48,139,154,255),width=3)
        for yy in range(sy0+18,sy1,34): d.line((sx0+12,yy,sx1-12,yy),fill=(25,82,91,75),width=1)
    screw=max(4,int(min(w,h)*.012))
    for x,y in ((x0+28,y0+28),(x1-28,y0+28),(x0+28,y1-28),(x1-28,y1-28)):
        d.ellipse((x-screw,y-screw,x+screw,y+screw),fill=(158,132,82,255),outline=INK,width=2); d.line((x-screw//2,y,x+screw//2,y),fill=INK,width=2)
    if label:
        txt=label.upper()[:28]; d.text((x0+36,y0+30),txt,font=font(max(13,int(h*.044)),True),fill=IVORY)
    scratches(im,label+variant,(x0+15,y0+15,x1-15,y1-15),count=16)
    return add_grain(im,"panel:"+label+variant,alpha=14)


def circle_badge(size,accent=CYAN,fill=INK2):
    w,h=size; im=Image.new("RGBA",size,(0,0,0,0)); d=ImageDraw.Draw(im); cx,cy=w//2,h//2; r=int(min(w,h)*.34)
    # outer glow
    def ring(md,a): md.ellipse((cx-r,cy-r,cx+r,cy+r),outline=a,width=max(8,int(r*.065)))
    im=Image.alpha_composite(im,glow_layer(size,ring,accent,max(10,int(r*.10))))
    d=ImageDraw.Draw(im); d.ellipse((cx-r+9,cy-r+9,cx+r-9,cy+r-9),fill=fill,outline=(132,145,139,255),width=max(2,int(r*.018)))
    return im,(cx,cy,r)


def draw_heart(d,cx,cy,s,col):
    r=s*.25; d.ellipse((cx-s*.44,cy-s*.28,cx-s*.04,cy+s*.12),fill=col); d.ellipse((cx+s*.04,cy-s*.28,cx+s*.44,cy+s*.12),fill=col)
    d.polygon(((cx-s*.43,cy-.02*s),(cx+s*.43,cy-.02*s),(cx,cy+s*.52)),fill=col)

def draw_drop(d,cx,cy,s,col): d.polygon(((cx,cy-s*.48),(cx-s*.32,cy+.10*s),(cx,cy+s*.48),(cx+s*.32,cy+.10*s)),fill=col)
def draw_flame(d,cx,cy,s,col): d.polygon(((cx,cy-s*.52),(cx+s*.32,cy-s*.05),(cx+s*.24,cy+s*.40),(cx,cy+s*.53),(cx-s*.30,cy+s*.32),(cx-s*.24,cy-.04*s),(cx-.05*s,cy-s*.25)),fill=col)
def draw_cross(d,cx,cy,s,col):
    t=s*.18; d.rectangle((cx-t,cy-s*.45,cx+t,cy+s*.45),fill=col); d.rectangle((cx-s*.45,cy-t,cx+s*.45,cy+t),fill=col)
def draw_lightning(d,cx,cy,s,col): d.polygon(((cx+.08*s,cy-s*.50),(cx-.30*s,cy+.05*s),(cx-.02*s,cy+.05*s),(cx-.16*s,cy+s*.50),(cx+.34*s,cy-.10*s),(cx+.08*s,cy-.10*s)),fill=col)
def draw_shelter(d,cx,cy,s,col):
    line_scaled(d,((cx-s*.48,cy+s*.30),(cx,cy-s*.36),(cx+s*.48,cy+s*.30)),col,s*.08); line_scaled(d,((cx-s*.32,cy+s*.29),(cx-s*.32,cy+s*.02),(cx+s*.32,cy+s*.02),(cx+s*.32,cy+s*.29)),col,s*.055)
def draw_radio(d,cx,cy,s,col):
    d.rounded_rectangle((cx-s*.40,cy-s*.28,cx+s*.40,cy+s*.35),radius=int(s*.08),outline=col,width=max(3,int(s*.06))); d.ellipse((cx-s*.28,cy-s*.14,cx-s*.02,cy+s*.12),outline=col,width=max(2,int(s*.04))); d.rectangle((cx+s*.08,cy-s*.16,cx+s*.28,cy-s*.05),fill=col); line_scaled(d,((cx+s*.28,cy-s*.30),(cx+s*.35,cy-s*.58)),col,s*.045)
def draw_tower(d,cx,cy,s,col):
    line_scaled(d,((cx-s*.32,cy+s*.43),(cx-s*.12,cy-s*.35),(cx+s*.10,cy-s*.35),(cx+s*.32,cy+s*.43)),col,s*.055)
    for y in (-.18,.02,.22,.40): line_scaled(d,((cx-s*(.14+.35*(y+.18)),cy+s*y),(cx+s*(.12+.33*(y+.18)),cy+s*y)),col,s*.035)
def draw_rope(d,cx,cy,s,col):
    for k in (1.0,.70,.42): d.ellipse((cx-s*.42*k,cy-s*.30*k,cx+s*.42*k,cy+s*.30*k),outline=col,width=max(2,int(s*.045)))
def draw_leaf(d,cx,cy,s,col):
    d.ellipse((cx-s*.42,cy-s*.20,cx+s*.36,cy+s*.22),fill=col); line_scaled(d,((cx-s*.36,cy+s*.18),(cx+s*.42,cy-s*.26)),INK,s*.035)
def draw_stone(d,cx,cy,s,col): d.polygon(((cx-s*.42,cy+s*.30),(cx-s*.34,cy-s*.18),(cx-.06*s,cy-s*.42),(cx+s*.32,cy-s*.22),(cx+s*.44,cy+s*.24),(cx+s*.08,cy+s*.40)),fill=col)
def draw_wood(d,cx,cy,s,col):
    for off in (-.18,0,.18):
        d.rounded_rectangle((cx-s*.40,cy+s*off-s*.065,cx+s*.40,cy+s*off+s*.065),radius=int(s*.045),fill=col,outline=INK,width=max(1,int(s*.018)))
def draw_hammer(d,cx,cy,s,col):
    line_scaled(d,((cx-s*.18,cy+s*.38),(cx+s*.14,cy-s*.12)),col,s*.10); d.rounded_rectangle((cx-s*.06,cy-s*.34,cx+s*.38,cy-s*.12),radius=int(s*.05),fill=col)
def draw_compass(d,cx,cy,s,col):
    d.ellipse((cx-s*.40,cy-s*.40,cx+s*.40,cy+s*.40),outline=col,width=max(3,int(s*.055))); d.polygon(((cx,cy-s*.34),(cx+s*.11,cy),(cx,cy+s*.34),(cx-s*.11,cy)),fill=col)
def draw_wrench(d,cx,cy,s,col):
    line_scaled(d,((cx-s*.28,cy+s*.34),(cx+s*.23,cy-s*.25)),col,s*.11); d.arc((cx+s*.02,cy-s*.45,cx+s*.42,cy-.05*s),35,255,fill=col,width=max(4,int(s*.09)))
def draw_hand(d,cx,cy,s,col):
    d.rounded_rectangle((cx-s*.24,cy-.05*s,cx+s*.25,cy+s*.37),radius=int(s*.12),fill=col)
    for i,x in enumerate((-.22,-.07,.08,.23)): d.rounded_rectangle((cx+s*x-s*.055,cy-s*(.46-.04*(i%2)),cx+s*x+s*.055,cy+s*.05),radius=int(s*.05),fill=col)
def draw_flag(d,cx,cy,s,col):
    line_scaled(d,((cx-s*.28,cy+s*.44),(cx-s*.28,cy-s*.46)),col,s*.055); d.polygon(((cx-s*.25,cy-s*.40),(cx+s*.36,cy-s*.28),(cx+s*.15,cy+.02*s),(cx-s*.25,cy-.08*s)),fill=col)


def status_icon(aid,variant,size):
    color={"UI-002":RED,"UI-003":ORANGE,"UI-004":CYAN,"UI-005":RED,"UI-011":GREEN,"UI-012":GREEN,"UI-013":ORANGE,"UI-014":GREEN}.get(aid,accent_for(variant,aid))
    v=norm_variant(variant)
    if any(k in v for k in ("critical","damaged","severe","offline","out")): color=RED
    if any(k in v for k in ("wet","freezing","weak")): color=CYAN
    im,(cx,cy,r)=circle_badge(size,color); d=ImageDraw.Draw(im); s=r*.96
    if aid=="UI-002": draw_heart(d,cx,cy,s,color)
    elif aid=="UI-003": draw_lightning(d,cx,cy,s,color)
    elif aid=="UI-004": draw_drop(d,cx,cy,s,color); # small snow cross
    elif aid=="UI-005": draw_cross(d,cx,cy,s,color)
    elif aid=="UI-011": draw_radio(d,cx,cy,s,color)
    elif aid=="UI-012": draw_shelter(d,cx,cy,s,color)
    elif aid=="UI-013": draw_flame(d,cx,cy,s,color)
    elif aid=="UI-014": draw_tower(d,cx,cy,s,color)
    return im


def wrist_ui(aid,name,variant,size):
    w,h=size
    if aid in {"UI-002","UI-003","UI-004","UI-005","UI-011","UI-012","UI-013","UI-014"}: return status_icon(aid,variant,size)
    if aid=="UI-006":
        col=accent_for(variant,aid); im,(cx,cy,r)=circle_badge(size,col); d=ImageDraw.Draw(im)
        start=-90; span={"full":350,"half":180,"low":80}.get(norm_variant(variant),260)
        d.arc((cx-r*.62,cy-r*.62,cx+r*.62,cy+r*.62),start,start+span,fill=col,width=max(8,int(r*.13))); return im
    if aid in {"UI-007","UI-008"}:
        col=CYAN if aid=="UI-007" else ORANGE; im,(cx,cy,r)=circle_badge(size,col); d=ImageDraw.Draw(im); t="1" if aid=="UI-007" else "2"
        f=font(int(r*.95),True); bb=d.textbbox((0,0),t,font=f); d.text((cx-(bb[2]-bb[0])/2,cy-(bb[3]-bb[1])/2-8),t,font=f,fill=IVORY); return im
    if aid=="UI-009":
        col=RED if "danger" in norm_variant(variant) else ORANGE; im,(cx,cy,r)=circle_badge(size,col); d=ImageDraw.Draw(im); d.polygon(((cx,cy-r*.58),(cx+r*.53,cy+r*.43),(cx-r*.53,cy+r*.43)),outline=col,fill=(0,0,0,0)); d.text((cx-12,cy-10),"!",font=font(44,True),fill=col); return im
    if aid=="UI-010":
        col=accent_for(variant,aid); im,(cx,cy,r)=circle_badge(size,col); d=ImageDraw.Draw(im); draw_hand(d,cx-r*.12,cy,r*.70,col); d.rounded_rectangle((cx+r*.12,cy-r*.18,cx+r*.55,cy+r*.28),radius=12,outline=col,width=7); return im
    # UI-001: actual rugged watch/instrument face rather than generic panel placeholder.
    im=Image.new("RGBA",size,(0,0,0,0)); d=ImageDraw.Draw(im); col=GREEN if "active" in norm_variant(variant) else CYAN
    cx,cy=w//2,h//2; bw,bh=int(w*.62),int(h*.72)
    # strap / body
    d.rounded_rectangle((cx-bw*.18,cy-bh*.61,cx+bw*.18,cy+bh*.61),radius=28,fill=(40,48,45,255),outline=(87,101,94,255),width=4)
    d.rounded_rectangle((cx-bw*.52,cy-bh*.40,cx+bw*.52,cy+bh*.40),radius=52,fill=(25,30,29,255),outline=(115,106,72,255),width=6)
    d.rounded_rectangle((cx-bw*.42,cy-bh*.31,cx+bw*.42,cy+bh*.31),radius=34,fill=(5,25,29,255),outline=TEAL,width=6)
    # digital instrument content
    d.text((cx-bw*.30,cy-bh*.22),"DAY 4",font=font(max(18,int(h*.045)),True),fill=(105,168,173,255)); d.text((cx-bw*.05,cy-bh*.06),"12:34",font=font(max(28,int(h*.085)),True),fill=col)
    for i,(lab,c) in enumerate((("+",RED),("~",CYAN),("^",ORANGE),("SOS",GREEN))):
        x=cx-bw*.29+i*bw*.19; y=cy+bh*.16; d.ellipse((x-22,y-22,x+22,y+22),outline=c,width=4); f=font(16,True); bb=d.textbbox((0,0),lab,font=f); d.text((x-(bb[2]-bb[0])/2,y-(bb[3]-bb[1])/2-2),lab,font=f,fill=c)
    for x,y in ((cx-bw*.45,cy-bh*.32),(cx+bw*.45,cy-bh*.32),(cx-bw*.45,cy+bh*.32),(cx+bw*.45,cy+bh*.32)): d.ellipse((x-8,y-8,x+8,y+8),fill=BRASS)
    return add_grain(im,"watch:"+variant,alpha=12)


def island_mark(d,cx,cy,s,col=IVORY,accent=GREEN):
    d.polygon(((cx-s*.48,cy+s*.20),(cx-s*.18,cy-s*.24),(cx-.02*s,cy-.05*s),(cx+s*.15,cy-s*.34),(cx+s*.48,cy+s*.20)),fill=col)
    d.arc((cx-s*.54,cy+s*.08,cx+s*.55,cy+s*.48),10,170,fill=accent,width=max(3,int(s*.04)))
    # two palms
    for off,scale in ((-.26,.55),(-.08,.42)):
        x=cx+s*off; base=cy+s*.16; top=cy-s*.18*scale
        line_scaled(d,((x,base),(x+s*.035,top)),col,s*.032)
        for ang in (-155,-115,-70,-25,20):
            a=math.radians(ang); line_scaled(d,((x+s*.035,top),(x+s*.035+math.cos(a)*s*.20*scale,top+math.sin(a)*s*.15*scale)),col,s*.023)


def branding(aid,name,variant,size):
    w,h=size; im=Image.new("RGBA",size,(0,0,0,0)); d=ImageDraw.Draw(im); v=norm_variant(variant); storm="storm" in v
    if aid in {"BR-005","BR-006"}:
        panel=rugged_panel(size,"",variant,wood=False,screen=False); d=ImageDraw.Draw(panel); x0,y0,x1,y1=int(w*.08),int(h*.10),int(w*.92),int(h*.90)
        island_mark(d,w*.29,h*.48,min(w,h)*.48,IVORY,CYAN if storm else GREEN)
        f=font(max(28,int(h*.16)),True); d.text((w*.48,h*.31),"ØEN",font=f,fill=IVORY); d.text((w*.48,h*.54),"SURVIVE TOGETHER",font=font(max(12,int(h*.045)),True),fill=ORANGE if storm else GREEN)
        return panel
    if aid=="BR-007":
        col=IVORY; pad=int(min(w,h)*.14); d.line((pad,h//2,w-pad,h//2),fill=col,width=4); d.line((pad,h//2-16,pad,h//2+16),fill=BRASS,width=5); d.line((w-pad,h//2-16,w-pad,h//2+16),fill=BRASS,width=5); return im
    if aid=="BR-008":
        im,(cx,cy,r)=circle_badge(size,RED if storm else BRASS); d=ImageDraw.Draw(im); txt="STORM" if storm else variant.upper().replace("_"," "); f=font(max(24,int(r*.38)),True); bb=d.textbbox((0,0),txt,font=f); d.text((cx-(bb[2]-bb[0])/2,cy-(bb[3]-bb[1])/2),txt,font=f,fill=IVORY); draw_flame(d,cx,cy+r*.52,r*.25,ORANGE); return im
    if aid=="BR-004":
        im,(cx,cy,r)=circle_badge(size,BRASS,(37,30,24,255)); d=ImageDraw.Draw(im); island_mark(d,cx,cy-r*.08,r*.88,IVORY,GREEN); d.arc((cx-r*.78,cy-r*.78,cx+r*.78,cy+r*.78),15,345,fill=IVORY,width=3); return im
    if aid=="BR-003":
        im,(cx,cy,r)=circle_badge(size,GREEN,(20,27,25,255)); d=ImageDraw.Draw(im); island_mark(d,cx,cy,r*.92,IVORY,GREEN); return im
    # BR-001/002 strong island/palm wordmark
    island_mark(d,w*.50,h*.36,min(w,h)*.68,IVORY,GREEN)
    f=font(max(42,int(h*.22)),True); txt="ØEN"; bb=d.textbbox((0,0),txt,font=f); d.text((w/2-(bb[2]-bb[0])/2,h*.55),txt,font=f,fill=IVORY,stroke_width=2,stroke_fill=(75,75,65,180))
    if aid=="BR-001":
        sub="SURVIVE TOGETHER"; fs=font(max(13,int(h*.055)),True); bb=d.textbbox((0,0),sub,font=fs); d.text((w/2-(bb[2]-bb[0])/2,h*.78),sub,font=fs,fill=GREEN)
    return im


def board_panel(size,name,variant,cards=4):
    im=rugged_panel(size,name,variant,wood=True,screen=False); d=ImageDraw.Draw(im); w,h=size; x0,y0,x1,y1=int(w*.12),int(h*.28),int(w*.88),int(h*.78)
    gap=max(8,int(w*.018)); cw=(x1-x0-gap*(cards-1))/cards
    for i in range(cards):
        xx=x0+i*(cw+gap); col=(77,94,87,255) if i%2==0 else (88,83,66,255)
        d.rounded_rectangle((xx,y0,xx+cw,y1),radius=12,fill=col,outline=(182,159,105,255),width=3)
        d.ellipse((xx+cw*.43,y0+18,xx+cw*.57,y0+18+cw*.14),fill=BRASS,outline=INK,width=2)
        for j in range(3): d.line((xx+cw*.16,y0+cw*.38+j*22,xx+cw*.82,y0+cw*.38+j*22),fill=(207,196,160,120),width=2)
    return im


def planning(aid,name,variant,size):
    v=norm_variant(variant)
    if aid in {"PL-001","PL-002","PL-008","PL-009","PL-010","PL-012"}:
        cards=4 if aid not in {"PL-009","PL-010"} else 3
        im=board_panel(size,name,variant,cards); d=ImageDraw.Draw(im); w,h=size
        if aid=="PL-002":
            # time-slot sun marks
            for i in range(4):
                x=w*(.21+.19*i); y=h*.55; d.ellipse((x-26,y-26,x+26,y+26),outline=ORANGE,width=5); d.line((x,y-38,x,y-30),fill=IVORY,width=3)
        if aid=="PL-009":
            symbols=(CYAN,CYAN,RED); xs=(.28,.50,.72)
            for x,c in zip(xs,symbols): d.ellipse((w*x-24,h*.49-24,w*x+24,h*.49+24),fill=c)
        if aid=="PL-010": draw_flag(d,w*.50,h*.54,min(w,h)*.28,ORANGE)
        return im
    if aid=="PL-011":
        im=Image.new("RGBA",size,(0,0,0,0)); d=ImageDraw.Draw(im); w,h=size
        for i,(fn,c) in enumerate(((draw_wood,WOOD),(draw_rope,BRASS),(draw_flame,ORANGE),(draw_leaf,GREEN),(draw_radio,CYAN))):
            x=w*(.14+.18*i); y=h*.50; d.ellipse((x-70,y-70,x+70,y+70),fill=INK2,outline=c,width=5); fn(d,x,y,95,c)
        return im
    # tokens PL-003..007
    col=accent_for(variant,aid); im,(cx,cy,r)=circle_badge(size,col,(55,43,31,255)); d=ImageDraw.Draw(im); s=r*.92
    if aid=="PL-003": draw_leaf(d,cx,cy,s,GREEN)
    elif aid=="PL-004": draw_hammer(d,cx,cy,s,IVORY)
    elif aid=="PL-005": draw_compass(d,cx,cy,s,CYAN)
    elif aid=="PL-006": draw_wrench(d,cx,cy,s,IVORY)
    else:
        risk={"low":GREEN,"medium":ORANGE,"high":RED}.get(v,col); d.polygon(((cx,cy-r*.55),(cx+r*.52,cy+r*.42),(cx-r*.52,cy+r*.42)),outline=risk,fill=(0,0,0,0)); d.ellipse((cx-8,cy+r*.10,cx+8,cy+r*.27),fill=risk)
    return im


def resource_icon(aid,name,variant,size):
    im,(cx,cy,r)=circle_badge(size,BRASS,(27,32,29,255)); d=ImageDraw.Draw(im); s=r*.95
    fn=None; col=IVORY
    mapping={
        "RS-001":(draw_wood,WOOD),"RS-002":(draw_wood,WOOD),"RS-003":(draw_rope,BRASS),"RS-004":(draw_leaf,GREEN),"RS-005":(draw_leaf,GREEN),
        "RS-006":(draw_stone,GREY),"RS-007":(draw_flame,ORANGE),"RS-010":(draw_radio,CYAN),"RS-011":(None,(66,117,128,255)),
        "RS-013":(draw_leaf,GREEN),"RS-015":(draw_flag,ORANGE),"RS-018":(draw_drop,CYAN),
    }
    if aid in mapping: fn,col=mapping[aid]
    if fn: fn(d,cx,cy,s,col)
    elif aid=="RS-008":
        d.rounded_rectangle((cx-s*.30,cy-s*.38,cx+s*.30,cy+s*.38),radius=int(s*.06),fill=(151,128,83,255),outline=IVORY,width=3); d.line((cx-s*.30,cy-s*.10,cx+s*.30,cy-s*.10),fill=INK,width=3)
    elif aid=="RS-009":
        draw_drop(d,cx,cy,s*.90,CYAN); d.arc((cx-s*.40,cy-s*.40,cx+s*.40,cy+s*.40),20,160,fill=IVORY,width=4)
    elif aid=="RS-011":
        d.polygon(((cx-s*.38,cy-s*.28),(cx+s*.31,cy-s*.36),(cx+s*.40,cy+s*.30),(cx-s*.28,cy+s*.39)),fill=col,outline=IVORY)
        d.line((cx-s*.18,cy-s*.30,cx+s*.02,cy+s*.36),fill=(207,212,195,170),width=3)
    elif aid=="RS-012":
        for i,(ox,oy) in enumerate(((-.20,-.12),(.10,.02),(-.03,.22))): d.polygon(((cx+s*(ox-.22),cy+s*(oy-.13)),(cx+s*(ox+.22),cy+s*(oy-.18)),(cx+s*(ox+.16),cy+s*(oy+.16)),(cx+s*(ox-.18),cy+s*(oy+.20))),fill=(100,112,111,255),outline=ORANGE,width=2)
    elif aid=="RS-014":
        d.rounded_rectangle((cx-s*.18,cy-s*.36,cx+s*.18,cy+s*.38),radius=int(s*.06),fill=(91,80,54,255),outline=IVORY,width=4); draw_flame(d,cx,cy,s*.34,ORANGE)
    elif aid=="RS-016":
        d.rectangle((cx-s*.38,cy-s*.28,cx+s*.38,cy+s*.30),fill=WOOD,outline=IVORY,width=3); d.line((cx-s*.38,cy,cx+s*.38,cy),fill=INK,width=4); d.rectangle((cx-s*.06,cy-s*.08,cx+s*.06,cy+s*.08),fill=BRASS)
    elif aid=="RS-017":
        d.polygon(((cx-s*.34,cy+s*.34),(cx-s*.24,cy-s*.20),(cx+s*.24,cy-s*.20),(cx+s*.34,cy+s*.34)),outline=IVORY,fill=(50,57,52,255)); d.ellipse((cx-s*.14,cy-s*.38,cx+s*.14,cy-s*.10),outline=IVORY,width=4)
    elif aid=="RS-019":
        for i in range(3): d.rounded_rectangle((cx-s*.34,cy-s*.30+i*s*.26,cx+s*.34,cy-s*.16+i*s*.26),radius=8,fill=GREEN if i<2 else ORANGE)
    elif aid=="RS-020":
        d.rounded_rectangle((cx-s*.38,cy-s*.28,cx+s*.38,cy+s*.28),radius=18,fill=(7,27,30,255),outline=CYAN,width=5); d.text((cx-s*.18,cy-s*.20),"12",font=font(int(s*.46),True),fill=IVORY)
    # semantic wet-state overlay
    if aid=="RS-002": draw_drop(d,cx+s*.28,cy-s*.25,s*.28,CYAN)
    return im


def world_marker(aid,name,variant,size):
    w,h=size; col=ORANGE if any(k in norm_variant(variant) for k in ("valid","active","warning","high")) or aid in {"WK-009","WK-010","WK-011"} else CYAN
    im=Image.new("RGBA",size,(0,0,0,0)); cx,cy=w//2,h//2; rr=int(min(w,h)*.31)
    def ring(md,a): md.ellipse((cx-rr,cy-rr*.40,cx+rr,cy+rr*.40),outline=a,width=max(6,int(rr*.055)))
    im=Image.alpha_composite(im,glow_layer(size,ring,col,max(18,int(rr*.10)))); d=ImageDraw.Draw(im); s=rr*.95
    if aid=="WK-001": draw_hand(d,cx,cy-s*.05,s,col)
    elif aid=="WK-002": draw_hand(d,cx-s*.24,cy,s*.72,col); draw_hand(d,cx+s*.24,cy,s*.72,col)
    elif aid=="WK-003":
        d.polygon(((cx,cy-s*.58),(cx+s*.42,cy-s*.22),(cx+s*.42,cy+s*.33),(cx,cy+s*.58),(cx-s*.42,cy+s*.33),(cx-s*.42,cy-s*.22)),outline=col,fill=(0,0,0,0)); d.line((cx,cy-s*.58,cx,cy+s*.58),fill=col,width=5)
    elif aid=="WK-004": draw_rope(d,cx,cy,s,col)
    elif aid=="WK-005": d.polygon(((cx,cy-s*.60),(cx+s*.44,cy),(cx,cy+s*.60),(cx-s*.44,cy)),fill=col)
    elif aid=="WK-006":
        for r in (.18,.34,.50): d.ellipse((cx-s*r,cy-s*r,cx+s*r,cy+s*r),outline=col,width=4); d.ellipse((cx-12,cy-12,cx+12,cy+12),fill=IVORY)
    elif aid in {"WK-007","WK-015"}: d.arc((cx-s*.42,cy-s*.42,cx+s*.42,cy+s*.42),30,330,fill=col,width=max(6,int(s*.08))); d.polygon(((cx+s*.38,cy-s*.28),(cx+s*.58,cy-s*.26),(cx+s*.44,cy-s*.08)),fill=col)
    elif aid=="WK-008":
        for r in (.18,.36,.54): d.ellipse((cx-s*r,cy-s*r,cx+s*r,cy+s*r),outline=col,width=4); d.line((cx-s*.66,cy,cx+s*.66,cy),fill=col,width=3); d.line((cx,cy-s*.66,cx,cy+s*.66),fill=col,width=3)
    elif aid=="WK-009": d.polygon(((cx,cy-s*.58),(cx+s*.54,cy+s*.43),(cx-s*.54,cy+s*.43)),outline=RED,fill=(0,0,0,0)); d.text((cx-12,cy-10),"!",font=font(44,True),fill=RED)
    elif aid=="WK-010": draw_flame(d,cx,cy,s,ORANGE)
    elif aid=="WK-011": draw_shelter(d,cx,cy,s,ORANGE); draw_wrench(d,cx+s*.20,cy+s*.12,s*.42,IVORY)
    elif aid=="WK-012": draw_radio(d,cx,cy,s,CYAN); d.polygon(((cx+s*.30,cy-s*.10),(cx+s*.62,cy),(cx+s*.30,cy+s*.10)),fill=col)
    elif aid=="WK-013":
        d.rectangle((cx-s*.45,cy-s*.30,cx+s*.45,cy+s*.30),outline=col,width=6); d.line((cx-s*.30,cy-s*.12,cx+s*.30,cy-s*.12),fill=col,width=4); d.line((cx-s*.30,cy+s*.08,cx+s*.10,cy+s*.08),fill=col,width=4)
    elif aid=="WK-014":
        d.rounded_rectangle((cx-s*.45,cy-s*.28,cx+s*.42,cy+s*.24),radius=22,outline=col,width=6); d.polygon(((cx-s*.22,cy+s*.22),(cx-s*.36,cy+s*.48),(cx+.02*s,cy+s*.22)),fill=col)
    return im


def menu_panel(aid,name,variant,size):
    im=rugged_panel(size,name,variant,wood=False,screen=True); d=ImageDraw.Draw(im); w,h=size; v=norm_variant(variant); x0,y0,x1,y1=int(w*.20),int(h*.37),int(w*.80),int(h*.74)
    col=RED if "failed" in v or "failure" in v else (GREEN if "success" in v or "connected" in v else ORANGE)
    if aid=="MN-001":
        island_mark(d,w*.50,h*.48,min(w,h)*.30,IVORY,GREEN); d.text((w*.41,h*.64),"ØEN",font=font(max(30,int(h*.12)),True),fill=IVORY)
    elif aid=="MN-002":
        for i in range(2): d.rounded_rectangle((x0,y0+i*70,x1,y0+50+i*70),radius=12,fill=(31,61,65,255),outline=CYAN,width=3); d.ellipse((x0+20,y0+14+i*70,x0+42,y0+36+i*70),fill=GREEN if i==0 else ORANGE)
    elif aid in {"MN-003","MN-006"}:
        for i in range(4):
            y=y0+i*62; d.text((x0,y),("COMFORT","TURN","VIGNETTE","SUBTITLES")[i] if aid=="MN-003" else ("SUBTITLES","SIZE","BACKGROUND","SPEAKER")[i],font=font(15,True),fill=IVORY); d.rounded_rectangle((x1-160,y,x1,y+28),radius=12,outline=CYAN,width=3); d.ellipse((x1-50,y+4,x1-28,y+26),fill=GREEN)
    elif aid=="MN-004":
        for i,t in enumerate(("RESUME","SETTINGS","QUIT")): d.rounded_rectangle((x0,y0+i*62,x1,y0+44+i*62),radius=10,outline=BRASS,width=3); d.text((x0+26,y0+9+i*62),t,font=font(20,True),fill=IVORY)
    elif aid=="MN-005":
        d.arc((w*.37,h*.41,w*.63,h*.67),-80,220,fill=col,width=9); d.text((w*.37,h*.69),"LINK",font=font(22,True),fill=col)
    elif aid=="MN-007":
        d.rounded_rectangle((x0,y0,x1,y1),radius=18,fill=(57,48,36,255),outline=BRASS,width=4); d.text((x0+28,y0+28),"STORMNATTEN",font=font(24,True),fill=IVORY); draw_lightning(d,x1-90,y0+70,70,CYAN)
    elif aid=="MN-008":
        d.text((x0,y0),"RUN SUMMARY",font=font(22,True),fill=IVORY); bars=(.82,.64,.48,.76)
        for i,b in enumerate(bars): y=y0+55+i*45; d.rectangle((x0,y,x1,y+18),outline=STEEL,width=2); d.rectangle((x0+3,y+3,x0+3+(x1-x0-6)*b,y+15),fill=col)
    elif aid=="MN-009":
        im2,(cx,cy,r)=circle_badge(size,BRASS,(34,31,24,255)); d=ImageDraw.Draw(im2); island_mark(d,cx,cy-r*.08,r*.80,IVORY,GREEN); return im2
    else:
        island_mark(d,w*.36,h*.51,min(w,h)*.26,IVORY,GREEN); d.text((w*.52,h*.45),"TAK",font=font(max(26,int(h*.11)),True),fill=IVORY)
    return im


def generic_panel(category,aid,name,variant,size):
    if category=="Branding & identity": return branding(aid,name,variant,size)
    if category=="Wrist UI & player status": return wrist_ui(aid,name,variant,size)
    if category=="Planning board & phase UI": return planning(aid,name,variant,size)
    if category=="Resource icons & inventory support": return resource_icon(aid,name,variant,size)
    if category=="Interaction markers & helper UI": return world_marker(aid,name,variant,size)
    if category=="Menus & meta screens": return menu_panel(aid,name,variant,size)
    return rugged_panel(size,name,variant)


def main()->int:
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8")); report=[]; counts={}
    for e in manifest:
        if e.get("kind")!="sprite" or e.get("category")==VFX_CATEGORY: continue
        rel=str(e["path"]); path=ROOT/rel; category=str(e.get("category","")); aid=str(e.get("asset_id","")); variant=str(e.get("variant","default")); name=str(e.get("name",aid))
        with Image.open(path) as src: size=src.size
        im=generic_panel(category,aid,name,variant,size)
        if im.size!=size: im=im.resize(size,Image.Resampling.LANCZOS)
        # Deterministic tiny state notch prevents semantically distinct variants from collapsing.
        d=ImageDraw.Draw(im); code=hashlib.sha256((aid+":"+variant).encode()).digest()[0]; y=int(size[1]*.88); x=int(size[0]*.18)
        for bit in range(8):
            if code&(1<<bit): d.rounded_rectangle((x+bit*13,y,x+bit*13+6,y+12),radius=2,fill=accent_for(variant,aid))
        im.save(path,compress_level=6)
        counts[category]=counts.get(category,0)+1
        report.append({"asset_id":aid,"variant":variant,"category":category,"path":rel,"size":list(size),"sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
    REPORT.write_text(json.dumps({"version":2,"count":len(report),"category_counts":counts,"entries":report},indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(f"Mockup UI V2: rebuilt {len(report)} non-VFX sprites across {len(counts)} categories")
    return 0


if __name__=="__main__": raise SystemExit(main())
