#!/usr/bin/env python3
"""Mockup-fidelity pass for the Project ØEN environment and camp dressing.

The broad environment/set-dressing passes provide coverage. This pass spends a
small, deterministic geometry budget on the objects that dominate the approved
mockups: wreckage, palms/jungle edges, cliff/cave framing and the lived-in camp.
It deliberately adds asymmetry, lashings, wear, loose debris and storm-loaded
secondary shapes so the world reads as hand-built and weather-beaten rather than
as clean procedural primitives.

Canonical OBJ paths and Unity GUIDs are preserved.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

from refine_hero_art import (
    Mesh, add_box, add_cylinder, add_torus, add_tarp, add_rope_between, write_obj,
)
from refine_environment_art import (
    build as build_environment, add_leaf, add_frond, add_rock,
)
from refine_set_dressing_art import build as build_set_dressing

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROD = ROOT / "Assets" / "ProductionArt"
MANIFEST = PROD / "Docs" / "production_art_manifest.json"

TARGETS = {
    "EN-001", "EN-003", "EN-006", "EN-007", "EN-009", "EN-012",
    "EN-013", "EN-014", "EN-016", "EN-017", "EN-018", "EN-020",
    "EN-021", "EN-022",
}
ENV_TARGETS = {"EN-001", "EN-006", "EN-007", "EN-009", "EN-012"}


def enhance_wreck(mesh: Mesh, variant: str) -> None:
    large = variant == "large"
    # Torn sail/tarp remnants caught in two ribs: a major visual cue in the beach mockups.
    add_tarp(mesh, (-0.72, 1.08, 0.05), 1.20 if large else .95, .72,
             "Cloth", .08, 6, True, True, (0, 18, -18))
    add_rope_between(mesh, (-1.20, .95, -.30), (-.55, .16, -.70), .011, "Rope", 6)
    add_rope_between(mesh, (-.25, 1.02, .34), (.18, .12, .72), .010, "Rope", 6)
    # Detached storm-thrown planks soften the generated hull footprint.
    for i, (c, e) in enumerate((
        ((1.62, .09, -.66), (0, 26, 8)), ((1.22, .07, .78), (0, -39, -5)),
        ((-1.42, .08, -.86), (0, 52, 6)), ((-.95, .06, .90), (0, -18, -7)),
    )):
        add_box(mesh, c, (.82 + .08*(i%2), .055, .095), "Wood", e)
        if i in (0, 2): add_cylinder(mesh, (c[0]+.18, c[1]+.04, c[2]), .008, .10, "Metal", 6, (0, 0, 22))


def enhance_barrel(mesh: Mesh, variant: str) -> None:
    # Salt-worn rope and a skewed rim make even the closed barrel feel scavenged.
    add_torus(mesh, (0, .58, 0), .365, .010, "Rope", 18, 5, (90, 0, 7))
    if variant == "broken":
        for i, (x, z, ang) in enumerate(((-.43,.17,-18),(.40,-.20,27),(.24,.42,48))):
            add_box(mesh, (x, .075, z), (.48, .055, .09), "Wood", (0, ang, (i-1)*8))
        add_rope_between(mesh, (-.33,.20,.08), (-.68,.035,.35), .010, "Rope", 5)


def enhance_driftwood(mesh: Mesh, variant: str) -> None:
    # Bleached forks and a half-buried rope remnant link beach debris to the camp craft language.
    count = {"small": 2, "medium": 3, "large": 4}.get(variant, 3)
    for i in range(count):
        x = (i-(count-1)/2)*.32
        add_cylinder(mesh, (x, .18, -.22+.08*i), .022, .54+.08*i, "Wood", 7, (22, i*31, 54-8*i))
    add_rope_between(mesh, (-.42,.035,-.12), (.48,.028,.17), .009, "Rope", 5)


def enhance_palm(mesh: Mesh, variant: str) -> None:
    # Dead lower fronds, scars and a few crown fruits keep silhouettes from reading as clean stock palms.
    h = 2.4 if variant == "young" else (2.65 if variant == "broken" else 4.15)
    for i, yaw in enumerate((38, 154, 268)):
        root = (.03*math.sin(i), h*.79-.04*i, .03*math.cos(i))
        add_frond(mesh, root, yaw, .52 if variant=="young" else .67, "Leaf", .32)
    for y, yaw in ((h*.24, 17), (h*.42, 61), (h*.60, 112)):
        add_box(mesh, (0, y, 0), (.25 if variant!="young" else .18, .025, .035), "Char", (0, yaw, 7))
    if variant == "mature":
        for i, yaw in enumerate((15, 135, 255)):
            a=math.radians(yaw)
            add_rock(mesh, (math.sin(a)*.14,h-.10,math.cos(a)*.14), (.075,.085,.075), "Wood", 7, i*.8)


def enhance_bush(mesh: Mesh, variant: str) -> None:
    scale = {"small": .72, "medium": 1.0, "dense": 1.18}.get(variant, 1.0)
    # A dark understory layer + outward torn leaves gives depth from headset viewing distance.
    for i in range(8 if variant!="dense" else 13):
        a=i*2.399963
        r=.20+.035*(i%3)
        root=(math.cos(a)*r,.10+.025*(i%2),math.sin(a)*r)
        add_leaf(mesh, root, (.30+.04*(i%3))*scale, .18*scale,
                 math.degrees(a)+18*(i%2), -22-(i%4)*4, "Leaf", .07)
    for i in range(3):
        a=math.radians(40+i*108)
        add_rope_between(mesh,(0,.03,0),(math.sin(a)*.34,.40+(.08*i),math.cos(a)*.34),.010,"Wood",5)


def enhance_rock_wall(mesh: Mesh, variant: str) -> None:
    # Sparse wet creepers/root lines break the modular rock-grid read without hiding traversal edges.
    anchors=[(-1.15,1.18,.05),(-.35,1.42,.02),(.62,1.25,.04),(1.30,.82,.02)]
    if variant == "corner": anchors=[(-.38,1.35,-.90),(.05,1.15,-.30),(.50,1.18,.18)]
    for i,a in enumerate(anchors):
        b=(a[0]+.10*math.sin(i*1.7), .06, a[2]+.11*math.cos(i))
        add_rope_between(mesh,a,b,.008,"Rope",5)
        add_leaf(mesh,(a[0],a[1]*.58,a[2]),.22,.11,35+i*77,-28,"Leaf",.05)
    # A few small foot stones soften the perfectly modular base.
    for i,x in enumerate((-1.28,-.62,.17,.91,1.35)):
        add_rock(mesh,(x,0,-.14+.05*math.sin(i)),(.20,.12,.18),"Stone",7,i*.47)


def enhance_cliff_grass(mesh: Mesh, variant: str) -> None:
    # Wind-load all extra tufts in a consistent storm direction.
    n=8 if variant=="short" else 14
    for i in range(n):
        a=i*2.399963; r=.12+.055*math.sqrt(i); x=math.cos(a)*r; z=math.sin(a)*r
        h=(.25+.04*(i%4)) if variant=="short" else (.42+.06*(i%4))
        tip=(x+.13, h, z-.045)
        add_rope_between(mesh,(x,.01,z),tip,.006,"Wood",5)
        add_leaf(mesh,(x,h*.30,z),h*.68,.050,68+i*11,-32,"Leaf",.035)


def enhance_cave(mesh: Mesh, variant: str) -> None:
    # Damp ledge debris and hanging roots give the cave the warm/rough mockup framing.
    for i,x in enumerate((-1.18,-.55,.22,.88)):
        add_rock(mesh,(x,.015,-.28+.08*(i%2)),(.20,.12,.18),"Stone",7,.4+i*.51)
    for i,x in enumerate((-.82,-.18,.47)):
        add_rope_between(mesh,(x,1.62,.05),(x+.07*math.sin(i),.72-.08*i,.10),.008,"Rope",5)
        add_leaf(mesh,(x,.92-.05*i,.08),.19,.09,20+i*93,-42,"Leaf",.06)
    if variant == "arch":
        add_box(mesh,(0,1.72,.08),(.58,.040,.10),"Char",(0,4,-3))


def enhance_groundsheet(mesh: Mesh, variant: str) -> None:
    # Visible seam lines, repairs and one curled edge improve scale/readability in the camp.
    for z in (-.23, .0, .23): add_rope_between(mesh,(-.66,.040,z),(.66,.043,z+.02),.005,"Cloth",5)
    add_box(mesh,(-.52,.075,.30),(.38,.018,.12),"Cloth",(0,-8,8))
    if variant in ("worn","wet"):
        add_box(mesh,(.26,.061,-.18),(.28,.014,.18),"Char" if variant=="worn" else "Tarp",(0,17,-3))


def enhance_cooking(mesh: Mesh, variant: str) -> None:
    # Soot, kindling and lashings make each component look like part of one lived-in cooking station.
    for i in range(6):
        a=2*math.pi*i/6
        add_box(mesh,(math.cos(a)*.20,.035,math.sin(a)*.20),(.18,.025,.055),"Char",(0,math.degrees(a)+18,0))
    add_torus(mesh,(0,.88,0),.235,.008,"Rope",14,4,(90,0,7))
    if variant == "pot":
        add_torus(mesh,(0,.54,0),.30,.012,"Metal",18,5,(0,0,0))
    elif variant == "utensils":
        add_rope_between(mesh,(.28,.07,.10),(.56,.025,.28),.008,"Rope",5)


def enhance_storage(mesh: Mesh, variant: str) -> None:
    if variant == "crate":
        for x in (-.31,.31): add_box(mesh,(x,.31,-.335),(.055,.55,.035),"Metal",(0,0,0))
        add_rope_between(mesh,(-.42,.52,.20),(.45,.08,-.18),.010,"Rope",5)
    elif variant == "sack":
        add_rope_between(mesh,(-.18,.12,-.10),(.22,.10,.14),.008,"Rope",5)
        add_box(mesh,(.12,.25,-.20),(.20,.022,.12),"Cloth",(0,21,-5))
    else:
        add_torus(mesh,(0,.45,0),.13,.010,"Rope",14,4,(90,0,11))


def enhance_rain_catcher(mesh: Mesh, variant: str) -> None:
    if variant == "frame":
        for p in ((-.44,.55,-.29),(.44,.55,-.29),(-.44,.55,.29),(.44,.55,.29)):
            add_torus(mesh,p,.055,.008,"Rope",12,4,(90,0,0))
    elif variant == "cloth":
        # radial tension lines visibly pull the wet tarp toward its basin point.
        for p in ((-.50,.12,-.34),(.50,.12,-.34),(-.50,.12,.34),(.50,.12,.34)):
            add_rope_between(mesh,p,(0,.035,0),.006,"Rope",5)
    else:
        add_torus(mesh,(0,.30,0),.315,.010,"Metal",16,4,(90,0,0))


def enhance_torch(mesh: Mesh, variant: str) -> None:
    for y in (.96,1.04,1.12): add_torus(mesh,(0,y,0),.070,.008,"Rope",12,4,(90,0,y*10))
    add_box(mesh,(.035,1.18,0),(.13,.22,.09),"Char",(0,14,8))
    if variant == "lit":
        add_box(mesh,(-.025,1.30,.01),(.055,.24,.055),"Fire",(0,-12,8))


def enhance_path_marker(mesh: Mesh, variant: str) -> None:
    add_torus(mesh,(0,.63,0),.075,.009,"Rope",12,4,(90,0,5))
    if variant == "cloth_marked":
        add_box(mesh,(.13,.75,.015),(.28,.025,.16),"Cloth",(0,8,-8))
        add_rope_between(mesh,(.02,.70,0),(.26,.63,.02),.007,"Rope",5)
    # Slight ground debris anchors the stake in the world.
    for i,a in enumerate((0,2.1,4.2)):
        add_rock(mesh,(math.cos(a)*.12,0,math.sin(a)*.12),(.08,.045,.07),"Stone",6,i*.4)


def enhance(aid: str, variant: str, mesh: Mesh) -> None:
    {
        "EN-001": enhance_wreck,
        "EN-003": enhance_barrel,
        "EN-006": enhance_driftwood,
        "EN-007": enhance_palm,
        "EN-009": enhance_bush,
        "EN-012": enhance_rock_wall,
        "EN-013": enhance_cliff_grass,
        "EN-014": enhance_cave,
        "EN-016": enhance_groundsheet,
        "EN-017": enhance_cooking,
        "EN-018": enhance_storage,
        "EN-020": enhance_rain_catcher,
        "EN-021": enhance_torch,
        "EN-022": enhance_path_marker,
    }[aid](mesh, variant)


def main() -> int:
    if not MANIFEST.exists(): raise SystemExit(f"Missing production manifest: {MANIFEST}")
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    count=verts=faces=0; families=set()
    for entry in manifest:
        aid=str(entry.get("asset_id","")); variant=str(entry.get("variant","default"))
        if aid not in TARGETS or entry.get("kind")!="mesh": continue
        mesh=build_environment(aid,variant) if aid in ENV_TARGETS else build_set_dressing(aid,variant)
        enhance(aid,variant,mesh)
        write_obj(mesh,ROOT/entry["path"])
        count+=1; verts+=len(mesh.verts); faces+=len(mesh.faces); families.add(aid)
    missing=TARGETS-families
    if missing: raise SystemExit("Mockup environment pass missed: "+", ".join(sorted(missing)))
    print(f"Mockup environment pass: {count} meshes / {len(families)} families / {verts} vertices / {faces} faces")
    return 0

if __name__=="__main__": raise SystemExit(main())
