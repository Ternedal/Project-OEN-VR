# ChatGPT-workstream — PROJECT ØEN

**Ejer:** ChatGPT  
**Projektejer:** Anders  
**Opdateret:** 2026-08-13  
**Scope:** Alt uden for Unity jf. `AI_COLLABORATION_AGREEMENT.md`

## Arbejdsregel

M0b + M-Pre blokerer **M1-implementation**, ikke det parallelle non-Unity-produktionsspor. Human/device evidence blokerer kun de valg, balanceparametre og acceptance gates, som faktisk kræver evidensen.

Machine-readable produktionsstatus: `content/source_inventory.source.json`.

---

# Aktuelle gates

- **M0b / issue #3 — Claude/Unity:** cross-device/device evidence mangler.
- **M-Pre / issue #7 — produkt:** ready-to-run; tre menneskelige sessioner med mindst to forskellige par mangler.
- **Content contract / issue #8:** onboarding + Day 3 proposals findes; minimal fire-start source/reference findes, men scope er ikke canonical uden Anders' disposition.

Proposal-data under `content/proposals/` forbliver `proposal-not-canonical`.

---

# Verificeret source-art på main

- **A1 UI:** action/status-symboler, player identity, effort markers, action card, wrist frame og interaction-feedback masters.
- **A2 core props:** briefs/concepts + `ITM_FIRESTEEL_001`, `ITM_TINDER_001`, `ITM_ROPE_COIL_001`. Firesteel er reference-only indtil issue #8 er afgjort.
- **A3 storm/VFX:** rain, debris, embers, smoke, impact, wetness, storm phases samt `VFX_ROPE_STRAIN_001`.
- **A4 camp:** camp layout/state, wreck, ground/readability, radio og signal progression.
- **B1:** jungle/ravine/ridge references, ravine anchor/guide markers, resource items og `PRP_SUPPLY_CRATE_001`.
- **B2:** presentation source + mapping for alle 10 events.
- **A5:** wind shield, dry-fuel cache, signal fuel; cloth, map fragment, radio battery; release UI for join/reconnect/setup/pause/ready/subtitles.
- **Materialfamilier:** wood/rope/cloth, rock/sand og foliage/utility source references + machine-readable contract.
- **Character handwear:** `CHR_HAND_P1_001` + `CHR_HAND_P2_001`; torso er stadig åben C-polish.
- **Neutral fallback:** fictional chart, compass, route card og signal tag.

Source-ready er ikke det samme som Unity-integrated eller release-approved. Claude ejer runtime import/implementation/device QA.

---

# Machine-readable content / UX

Aktuelle contracts omfatter:

- dansk localization
- Stormnatten actions
- 10-event authoring + event presentation
- neutral personalization
- onboarding/Day 3 proposals
- after-action presentation
- material families
- release UI surface→copy mapping
- planning/status UI→action/localization/source mapping
- audio recording/acquisition queues
- audio acquisition candidates + listening QA
- samlet source inventory

`content/ui/planning_status_ui.source.json` binder planning card/effort markers/wrist status direkte til eksisterende action- og localization-data; Unity skal ikke oprette en parallel action/copy mapping.

---

# Audio/source-status

## AU-1

Deterministisk generator til 12 korte UI/system cues; CI-valideret.

## Naturalistisk source

- Foley recording queue findes.
- Ambience acquisition queue findes.
- `content/audio/acquisition_candidates.source.json` indeholder licensverificerede CC0-kandidater for bl.a. wind, rain, fire, rope, wood og cloth.
- `tools/acquire_audio_sources.py` downloader direct-download candidates, bevarer originals, beregner SHA-256, prøver `ffprobe` og skriver acquisition-manifest under den allerede ignorerede `PrivateContent/AudioSourceIncoming/`.
- `content/audio/listening_qa.source.json` kræver listening/technical QA før en acquired original kan blive source-approved eller derived-master-approved.

**Vigtigt:** WAV/FLAC-originalerne er ikke acquired i denne ChatGPT-runtime, fordi binary download til arbejdscontaineren er blokeret. De må derfor ikke markeres som producerede masters.

## Radio / musik

- Radio VO: 9 cues × 3 takes specificeret; faktisk recording mangler.
- Musik: direction/cue-sheet klar; composition/source mangler.

---

# CI / kvalitet

Aktive guards omfatter:

- Core tests
- Validate handoff
- Validate non-Unity sources
- Validate source inventory
- action placeholder-cost mirror
- AU-1 regeneration/validation
- event presentation validation

Seneste planning/status inventory-commit `36a38dd` er grøn på Core, handoff, non-Unity og source-inventory.

Forsøg på at udvide `validate_source_inventory.py` med dybere planning/status cross-file checks blev filtreret og tælles **ikke** som leveret. Den eksisterende pipeline er fortsat grøn.

---

# Repo hygiene

PR #12 fjernede 89 tracked genererede `src/**/bin/` build/test-filer. Gælden er lukket.

---

# Evidens der stadig ikke må opfindes

- M-Pre / issue #7
- OQ-008 fairness/randomness
- OQ-009 role assignment
- OQ-010 after-action competition
- M3/M4 numeric balance/tuning
- M3-M9 human gates
- M0b/device gates

---

# Næste aktive ChatGPT-bølge

1. fortsæt stabile B1/world source assets, men kun hvor et manglende source master reducerer reel Unity-gætteri
2. actual audio acquisition + listening QA på en internetforbundet workstation; ingen fake WAV-status
3. derefter derived audio masters/Foley/ambience, når source originals faktisk er acquired og godkendt
4. radio VO recording efter samme provenance/listening pipeline
5. yderligere machine-readable contracts kun hvor de erstatter manuel mapping — ikke for dokumentationens egen skyld
6. richer environment/polish og torso først når geometry/device evidence reducerer rework-risiko
7. private personalization source uden for public repo senere
8. M1 implementation handoff når både M0b + M-Pre er grønne

## Kendte ikke-leverede artifacts

- ember-carrier source blev genereret som blob, men commit blev filtreret; tælles **ikke** som produceret
- repair-mallet source blev genereret som blob, men er ikke committed; tælles **ikke** som produceret
- fuld gameplay interaction-feedback JSON-binding blev filtreret; planning/status-delen blev i stedet leveret som separat contract

Der omgås ikke sikkerhedsfiltre, og ucommittede artifacts tælles aldrig som produktion.

---

# Arbejdsregel ved “kør videre”

1. kontrollér seneste repo/issues/CI
2. brug `content/source_inventory.source.json` som produktionsstatus
3. tag højeste ublokerede non-Unity-opgave
4. ændr ikke Unity-filer
5. producer konkrete artifacts/source frem for kun planer
6. QA egne leverancer og registrér provenance
7. opfind aldrig human/device-evidens

> **Gates bestemmer hvad der må låses. De betyder ikke, at ChatGPTs produktionsspor skal stå stille.**
