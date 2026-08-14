#!/usr/bin/env python3
"""Final broadleaf vegetation pass for Project ØEN Stormnatten.

Dense scene review showed that environment coverage was finally sufficient, but some
vegetation still read as thin procedural twigs. This pass keeps the Quest-conscious
canonical assets while shifting the silhouette toward the approved mockups: broad,
layered tropical leaves, wind-loaded palm fronds, leafy vines and less exposed stem.

Targets only EN-007..EN-010 and preserves all canonical paths / Unity GUIDs.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

from refine_mockup_fidelity import Mesh, add_cylinder_between, write_obj
from refine_mockup_fidelity_v2 import add_ribbon
from refine_mockup_fidelity_v6 import build_palm
from refine_world_density import base_mesh, enhance as density_enhance

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROD = ROOT / "Assets" / "ProjectOEN" / "ProductionArt"
MANIFEST = PROD / "Docs" / "production_art_manifest.json"
TARGETS = {"EN-007", "EN-008", "EN-009", "EN-010"}


def broad_leaf(mesh: Mesh, root, yaw: float, length: float, width: float,
               lift: float = .10, droop: float = .12, curl: float = .05) -> None:
    """One broad, curved tropical blade made from a filled ribbon."""
    x, y, z = root
    a = math.radians(yaw)
    dx, dz = math.cos(a), math.sin(a)
    sx, sz = -dz, dx
    points=[]
    for i in range(7):
        t=i/6
        side=math.sin(t*math.pi)*curl
        points.append((
            x + dx*length*t + sx*side,
            y + math.sin(t*math.pi)*lift - droop*(t**1.55),
            z + dz*length*t + sz*side,
        ))
    widths=[.07*width,.72*width,width,.96*width,.72*width,.40*width,.018]
    add_ribbon(mesh, points, widths, "Leaf")
    # only one subtle midrib; avoids the previous stick-heavy read
    for p,q in zip(points[1:5],points[2:6]):
        add_cylinder_between(mesh,p,q,.0045,"Wood",5)


def enrich_palm(mesh: Mesh, variant: str) -> None:
    young=variant=="young"; broken=variant=="broken"
    h=2.80 if young else (3.05 if broken else 4.00)
    crown=(.105,h,.018)
    n=7 if young else (7 if broken else 10)
    # Broad under-canopy leaves fill the holes between the detailed v6 fronds.
    for i in range(n):
        yaw=i*360/n+17
        length=(.76 if young else 1.08)*(1+.08*math.sin(i*1.7))
        if broken and i in (1,5): length*=.62
        broad_leaf(mesh,crown,yaw,length,.28 if young else .34,
                   lift=.18,droop=.24+.04*(i%3),curl=.055)


def enrich_ground_fronds(mesh: Mesh, variant: str) -> None:
    n=7 if variant=="small" else 12
    for i in range(n):
        a=i*2.399963
        r=.08+.060*math.sqrt(i+1)
        root=(math.cos(a)*r,.025,math.sin(a)*r)
        broad_leaf(mesh,root,-70+i*37,.42+.06*(i%4),.20+.02*(i%2),
                   lift=.05,droop=.13,curl=.04*((i%3)-1))


def enrich_bush(mesh: Mesh, variant: str) -> None:
    scale={"small":.78,"medium":1.0,"dense":1.18}.get(variant,1.0)
    n=13 if variant=="small" else (20 if variant=="medium" else 31)
    # Layer broad leaves over the branch skeleton so the silhouette reads as foliage first.
    for i in range(n):
        a=i*2.399963
        ring=.10+.12*((i%5)/4)
        level=i%4
        root=(math.cos(a)*ring,.14+.115*level,math.sin(a)*ring)
        broad_leaf(mesh,root,math.degrees(a)+(14 if i%2 else -11),
                   (.34+.055*(i%3))*scale,(.22+.025*(i%2))*scale,
                   lift=.08+.02*(i%3),droop=.08+.025*(i%4),curl=.04*((i%3)-1))
    # A crown layer closes the conspicuous twiggy centre.
    for i in range(7 if variant!="dense" else 10):
        yaw=i*(360/(7 if variant!="dense" else 10))+22
        broad_leaf(mesh,(0,.48*scale,0),yaw,.36*scale,.23*scale,
                   lift=.13,droop=.07,curl=.035)


def enrich_vines(mesh: Mesh, variant: str) -> None:
    n={"short":5,"hanging":8,"dense":12}.get(variant,8)
    # Larger alternating leaves make the hanging mass visible without multiplying stems.
    for i in range(n):
        x=(i-(n-1)/2)*.09
        top=.44 if variant=="short" else .78+.055*(i%4)
        for j,t in enumerate((.20,.42,.64,.82)):
            root=(x+.045*math.sin(i+t*5),top*(1-t),.035*math.cos(i*.8+t*4))
            yaw=35+i*29+j*83
            broad_leaf(mesh,root,yaw,.20+.025*((i+j)%3),.115,
                       lift=.03,droop=.08,curl=.025*((i+j)%3-1))


def build(aid: str, variant: str) -> Mesh:
    if aid=="EN-007":
        mesh=build_palm(variant)
        enrich_palm(mesh,variant)
        return mesh
    mesh=base_mesh(aid,variant)
    density_enhance(aid,mesh,variant)
    if aid=="EN-008": enrich_ground_fronds(mesh,variant)
    elif aid=="EN-009": enrich_bush(mesh,variant)
    elif aid=="EN-010": enrich_vines(mesh,variant)
    return mesh


def main()->int:
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    count=verts=faces=0; seen=set()
    for e in manifest:
        aid=str(e.get("asset_id","")); variant=str(e.get("variant","default"))
        if aid not in TARGETS or e.get("kind")!="mesh": continue
        mesh=build(aid,variant)
        write_obj(mesh,ROOT/e["path"])
        count+=1; verts+=len(mesh.verts); faces+=len(mesh.faces); seen.add(aid)
    missing=TARGETS-seen
    if missing: raise SystemExit("Vegetation fidelity pass missed: "+", ".join(sorted(missing)))
    print(f"Broadleaf vegetation fidelity: {count} meshes / {len(seen)} families / {verts} vertices / {faces} faces")
    return 0


if __name__=="__main__": raise SystemExit(main())
