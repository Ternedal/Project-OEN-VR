# Repository status

**Opdateret:** 2026-08-13

## Baseline

- Baseline: **v2.1**.
- Alle 10 oprindelige reviewfund er lukket.
- Quest 2 = performance-/kvalitetsgulv.
- Quest 3/3S = enhanced parity.
- Quest 1 = droppet runtime/testlane (`DROP_Q1_RUNTIME`).
- Gaveversion = **1.012 t**; 439 t deferred efter v1.0.
- M5 = Release 1.
- Arbejdsdeling: `AI_COLLABORATION_AGREEMENT.md` — Claude = Unity, ChatGPT = alt andet.

---

# Aktuelle gates

## M0b — Claude / Unity

Tracker: GitHub issue #3.

Per-client feasibility er dokumenteret. Cross-device evidence mangler fortsat:

1. remote head/hands replication
2. handshake mismatch rejection
3. shared box korrekt two-player state
4. 10× Q2↔Q3 lift uden permanent desync
5. 72 Hz minimal network scene
6. standby/reconnect measurement
7. compatibility matrix completion

## M-Pre — ChatGPT / produkt

Tracker: GitHub issue #7.

Ready-to-run package findes i `prototype/m-pre/`; menneskedata mangler.

## Content contract

Tracker: GitHub issue #8.

- intro → explicit onboarding sequence foreslået
- Day 3 → explicit planning phase foreslået
- minimal fire-start → source/spec/reference findes, men gave-scope kræver Anders' disposition

Proposal-data under `content/proposals/` er `proposal-not-canonical`.

**M1 åbner først efter grøn M0b + M-Pre.** Det stopper ikke non-Unity-sourceproduktionen.

---

# Core / Unity

`src/ProjectOen.Core` har senest dokumenteret **146 passed, 0 failed** i Core-dokumentationen, og aktuelle Core Actions-runs er fortsat grønne efter de seneste non-Unity/repo-hygiene ændringer.

Unity/Fusion-laget ejes af Claude. Den gamle status “Fusion ukompileret” er historisk; M0b cross-device er den reelle åbne tekniske gate.

---

# ChatGPT / non-Unity

## Autoritativ status

- levende arbejdskø: `docs/36_CHATGPT_WORKSTREAM.md`
- machine-readable produktionsstatus: `content/source_inventory.source.json`
- asset-ID/funktionsmanifest: `docs/38_SOURCE_ASSET_MANIFEST.md`
- source-art provenance: `source_art/PROVENANCE_INDEX.md`

`docs/38` er reconcilet med de faktisk producerede sourcefiler og skelner nu mellem **source master**, **source reference**, **spec** og **Unity/release-status**.

## Leveret produkt/design/QA foundation

Der findes nu bl.a.:

- non-Unity gap audit
- source asset/audio manifests
- dansk UX/copy/localization
- personalization/privacy + komplet neutral fallback-source
- human QA M1-M9
- IP/provenance
- Stormnatten content coverage + 10-event authoring
- visual style bible + UI information architecture
- gift/release flow
- telemetry/metrics
- backlog ownership overlay
- narrative continuity
- content-contract proposals
- interaction handoffs for planning, shelter, fire, ravine og stormfinale

## Machine-readable content

`content/` indeholder bl.a.:

- dansk localization
- Stormnatten actions + placeholder-cost mirror
- 10-event authoring
- event→presentation mapping
- neutral personalization profile
- onboarding/Day 3 proposals
- Foley recording queue
- ambience acquisition queue
- radio VO recording queue
- after-action presentation contract
- samlet source inventory

After-action-kontrakten bruger Core's authoritative causal data og holder individuelle titler slået fra, indtil OQ-010 giver evidens.

---

# Source-art på main

Producerede sourcepakker omfatter nu:

- **A1:** gameplay/status/action UI, effort markers, cards og feedback cues
- **Neutral:** fictional chart, compass, route card og signal tag
- **A2:** core prop briefs/concepts + individuelle masters for firesteel-reference, tinder og rope coil
- **A3:** storm VFX/source references
- **A4:** camp layout/state + wreck, ground, radio og signal progression refs
- **B1 environment:** jungle/ravine/ridge + ravine anchor/guide markers
- **B1 resources:** wood/fiber/herbs/food/general supplies
- **B1 utility:** supply crate source master
- **B2:** event presentation source + mapping for alle 10 events
- **A5 meshes:** wind shield, dry-fuel cache og signal-fuel OBJ source
- **A5 items:** cloth, map fragment og radio battery
- **A5 release UI:** join, reconnect, setup, pause, ready-state og subtitle band

Source-ready betyder ikke Unity-integreret eller release-approved; Claude ejer runtime-import, prefabs, colliders, materials, performance og device QA.

---

# Audio/source-status

- AU-1: deterministisk generator til 12 korte UI/system cues; CI-valideret.
- Foley: recording queue klar; faktiske naturalistiske masters mangler.
- Ambience: acquisition/recording queue klar; faktiske masters mangler.
- Radio VO: 9 cues × 3 takes er specificeret; faktisk recording mangler.
- Musik: direction/cue-sheet klar; composition/source mangler.

Ingen naturalistisk lyd markeres som produceret, før reel source + provenance findes.

---

# CI / kvalitet

Aktive guards omfatter:

- Core tests
- Validate handoff
- Validate non-Unity sources
- action placeholder-cost mirror
- AU-1 source regeneration/validation
- event-presentation validation
- **Validate source inventory**

Den nye inventory-validator kontrollerer package/content paths, dublet-ID'er, `producedIds`-coverage og A2 `individualMasterIds`. Første workflow-run er grøn.

Source-art får desuden visuel QA, når layout/readability kræver det; supply-crate source blev fx rettet for tekst-overflow før merge.

---

# Repo hygiene

Tidligere tracked `src/ProjectOen.Core/bin/` og `src/ProjectOen.Core.Tests/bin/` er fjernet via PR #12.

- 89 genererede build/test-filer fjernet
- `.gitignore` dækkede allerede `src/**/bin/`
- Core tests var grønne efter cleanup
- begge paths er verificeret væk fra `main`

Denne gæld er lukket.

---

# Fortsat åbent på ChatGPT-siden

Der er fortsat væsentligt non-Unity-arbejde:

1. stabile B1/world/source assets hvor det reducerer Unity-gætteri
2. source material/texture families og øvrig produktionsreference
3. reel Foley/ambience/radio-VO sourceproduktion og provenance
4. musikproduktion, når timing/evidence gør cue-længder meningsfulde
5. yderligere machine-readable presentation/content contracts hvor nødvendigt
6. richer environment/polish efter geometry/device evidence
7. private personalization source uden for public repo senere
8. human design/playtest evidence
9. M1 handoff assembly når M0b + M-Pre er grønne

Genererede men ikke committede artifacts tælles aldrig som produceret.

---

# Parallelle handlinger

- Claude fortsætter issue #3.
- M-Pre human sessions lukker issue #7, når de køres.
- Fire-start-scope i issue #8 kræver Anders' beslutning, før det må tælle ind i gaveversionen.
- ChatGPT fortsætter resten af den ublokerede non-Unity-kø parallelt.
