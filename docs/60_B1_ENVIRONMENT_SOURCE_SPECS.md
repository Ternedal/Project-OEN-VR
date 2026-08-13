# B1 environment source specifications — PROJECT ØEN

**Owner:** ChatGPT  
**Runtime/world implementation:** Claude  
**Date:** 2026-08-13  
**Scope:** Jungle, ravine and ridge source/readability contracts before Unity scene production

## Purpose

B1 defines what the three exploration environments must communicate to players before any final world geometry, dressing, lighting or Unity navigation is locked.

The package is intentionally about:

- navigation readability
- landmark hierarchy
- interaction-safe space
- information asymmetry
- route recovery / fail-forward
- state and weather communication

It is **not** final level design geometry. Claude remains free to implement the cheapest robust Quest 2-compatible world that satisfies these product constraints.

---

# 1. Global environment rules

## 1.1 Never make navigation itself the puzzle

The game may ask players to choose priorities, read risk and communicate. It should not ask them to spend minutes being lost in visually repetitive foliage.

Required:

- every zone has one dominant route silhouette
- optional detours are short and visibly reconnect
- major decision points have a recognizable return landmark
- route changes are reinforced by shape/value/audio, not color alone

## 1.2 Comfort beats spectacle

No environment requires:

- real-world walking across a large physical area
- leaning over a virtual edge
- jumping
- sustained overhead reach
- forced camera pitch/roll
- fast artificial lateral motion

## 1.3 Environment communicates state

Players should be able to answer from the world, not only UI:

- where did we come from?
- what is the next meaningful destination?
- is this place becoming more dangerous?
- which object/landmark matters here?
- how do we safely return?

## 1.4 Quest 2 source discipline

Source art should favor:

- strong large shapes
- repeatable foliage/material families
- small reusable decal/texture sets
- landmarks with silhouette differences
- restrained transparency/overdraw assumptions

No source brief requires expensive runtime fog volumes, dense alpha foliage or unique 4K materials.

---

# 2. `ENV_JUNGLE_001`

## Player function

A short exploration corridor that can contain resource opportunities and route decisions without becoming a maze.

## Spatial contract

- clear camp/return anchor at entry
- one primary route with 2–3 readable bends
- at most one meaningful optional short detour at a time
- visible or strongly implied reconnect from detour
- ridge exit reads before the final approach

## Landmark hierarchy

1. camp/return anchor
2. resource pocket
3. decision fork
4. ridge exit marker

## Resource pockets

Resource pockets should be readable from the route before entering them.

Examples:

- fiber cluster with a distinct vertical silhouette
- herb patch framed by a rock/log boundary
- fallen branches/wood near a route widening

Do not scatter pickup-scale objects uniformly through foliage.

## Visual language

- broad leaf masses and trunks define enclosure
- route remains a simpler value/shape band
- detours use a different edge rhythm rather than a different color only
- avoid identical tree tunnels for long stretches

## Audio relationship

`SFX_AMB_JUNGLE_001` may reinforce depth and direction, but the route must remain readable with audio disabled.

## Acceptance

A player shown the zone for 5–10 seconds should be able to point to:

- the route forward
- the approximate return direction
- the next landmark or opportunity

---

# 3. `ENV_RAVINE_001`

## Player function

A bounded two-person rescue/traversal space where one player is exposed in fiction and the second player actively manages safety/information.

Product interaction contract: `design/interactions/RAVINE_RESCUE.md`.

## Required spaces

- belayer platform
- obvious rope anchor
- 2–4 bounded traversal progression points
- recovery/objective ledge
- safe pause/resolve point
- visible fail-forward/return route

## Information asymmetry

### Traverser reads

- local hold/step target
- next immediate safe position
- objective ledge

### Belayer reads

- rope tension state
- guide marker order/route sequence
- partner progress

The environment should create complementary views rather than hiding arbitrary information.

## Edge/height treatment

The ravine can feel deep without requiring the player to physically approach a dangerous real-world boundary.

Required:

- critical controls/holds within calibrated reach
- no mandatory lean over edge
- no jump-scare fall
- ordinary mistake resolves to safe consequence state
- recovery route is visually different from the main traversal path

## Key source IDs

- `PRP_RAVINE_ANCHOR_001`
- `PRP_RAVINE_GUIDE_MARKERS_001`
- `TEX_TENSION_GUIDE_001`
- `ITM_ROPE_COIL_001`

## Acceptance

A greybox/reference review must clearly identify both meaningful player stations and the fail-forward path without reading implementation notes.

---

# 4. `ENV_RIDGE_001`

## Player function

A short scouting/reward zone that gives useful foresight about weather, routes and signal opportunity.

The ridge should reward exploration with **information**, not exposition.

## Spatial contract

- clear arrival marker from jungle
- safe overlook/platform
- obvious return route
- horizon/weather direction
- signal opportunity direction

## Information delivered

The ridge may communicate:

- storm front direction/intensity
- stronger wind exposure
- possible signal line toward sea/horizon
- route/weather context that helps later planning

It must not tell players exactly which planning action is objectively correct.

## Comfort

- overlook does not require standing at a sheer virtual edge
- important reads are available from a safe central position
- no required binocular/long overhead pose
- wind is communicated through world/audio/VFX without camera motion

## Relationship to A3 storm sources

B1 ridge establishes directional language that A3 later intensifies:

- sky/horizon value shift
- directional wind/debris
- storm-front cue
- signal-direction contrast

## Acceptance

After visiting the ridge, players should be able to describe at least one useful piece of information gained and still know how to return.

---

# 5. Cross-zone continuity

The journey should read as:

`CAMP → JUNGLE → (RAVINE branch/opportunity) → RIDGE → return/planning`

This is conceptual flow, not a mandated single Unity navmesh route.

Continuity rules:

- camp materials/markers may echo at first jungle entry
- jungle enclosure opens noticeably near ravine/ridge
- ravine uses colder/rockier shape language than jungle
- ridge opens horizon/value scale after enclosed jungle
- return direction remains recognizable across all three

---

# 6. State progression

## Calm/day

- readable surfaces and route edges
- low environmental motion
- resource landmarks visible

## Pre-storm

- wind direction increasingly coherent
- ridge weather information becomes more meaningful
- loose foliage/debris starts moving

## Storm/full pressure

These exploration zones are not expected to become new complex storm gameplay spaces unless explicitly scoped later.

If visible/visited during storm:

- reduce detail before reducing route readability
- preserve landmarks
- reuse A3 storm language

---

# 7. Source package

`source_art/environment/b1/` contains:

- `B1_JUNGLE_READABILITY_001.svg`
- `B1_RAVINE_READABILITY_001.svg`
- `B1_RIDGE_READABILITY_001.svg`
- `PROVENANCE.md`

These are reference masters, not Unity textures or final level maps.

---

# 8. Claude handoff acceptance

Before B1 is treated as implementation-ready:

- zone purpose is preserved
- navigation does not become a maze
- ravine has two materially active player roles
- ridge provides foresight without solving planning
- comfort rules remain intact
- return/recovery routes stay obvious
- Quest 2 performance may simplify decoration but not landmark hierarchy

No exact meter distances, polygon budgets or runtime systems are locked by this document unless separately accepted through Unity/device evidence.
