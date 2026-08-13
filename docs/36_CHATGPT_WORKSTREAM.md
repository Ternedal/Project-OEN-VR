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

# Leveret non-Unity foundation

Produkt/design/QA-laget omfatter bl.a.:

- source asset/audio manifests
- dansk UX/copy/localization
- personalization/privacy + neutral fallback
- human QA M1-M9
- IP/provenance
- Stormnatten content coverage + 10-event catalog
- visual style/UI IA
- gift/release-flow
- telemetry/metrics
- backlog ownership overlay
- narrative continuity
- content-contract proposals
- interaction handoffs for planning, shelter, fire, ravine og stormfinale

---

# Source-art på main

## A1

Gameplay-readable UI/source kit: action/status-symboler, effort markers, action-card base og interaction feedback.

## Neutral fallback

Fictional chart, compass, route card og signal tag. Neutral source er komplet bortset fra faktisk radiooptagelse.

## A2

Core prop briefs/concepts + individuelle masters:

- `ITM_FIRESTEEL_001.svg` — reference only; issue #8 er stadig gate
- `ITM_TINDER_001.svg`
- `ITM_ROPE_COIL_001.svg`

## A3

Storm source/reference for rain, debris, embers, smoke, impact, wetness og phase intensity.

## A4

Camp layout/state + wreck, ground/readability, radio og signal progression references.

## B1

- jungle/ravine/ridge references
- ravine anchor/guide markers
- wood/fiber/herbs/food/general supplies
- `PRP_SUPPLY_CRATE_001.svg` — visuelt QA'et og rettet før merge

## B2

Event presentation source + machine-readable mapping for alle 10 events.

## A5

- OBJ source: wind shield, dry-fuel cache, signal fuel
- source items: cloth, map fragment, radio battery
- release UI: join, reconnect, first-launch setup, pause, connected/ready, subtitle band

## Base material references — produceret

`source_art/materials/base/`:

- `MAT_WOOD_ROPE_CLOTH_REFERENCE_001.svg`
- `MAT_ROCK_SAND_REFERENCE_001.svg`
- `MAT_FOLIAGE_UTILITY_REFERENCE_001.svg`
- `PROVENANCE.md`

Machine-readable kontrakt: `content/materials/material_families.source.json`.

Dækker alle syv manifestfamilier på source-reference niveau: wood, rope, cloth, rock, sand, foliage og utility metal. Claude ejer Unity material/shader implementation og device QA.

---

# Audio/source-status

- **AU-1:** deterministisk generator til 12 korte UI/system cues; CI-valideret.
- **Foley:** recording queue klar; faktiske naturalistiske masters mangler.
- **Ambience:** acquisition queue klar; faktiske masters mangler.
- **Radio VO:** 9 cues × 3 takes specificeret; faktisk recording mangler.
- **Musik:** direction/cue-sheet klar; composition/source mangler.

Naturalistisk lyd markeres aldrig som produceret før reel source + provenance findes.

---

# Machine-readable content

Source contracts omfatter nu:

- dansk localization
- Stormnatten actions + placeholder-cost mirror
- 10-event authoring
- event→presentation mapping
- neutral personalization
- onboarding/Day 3 proposals
- Foley/ambience/radio recording queues
- after-action presentation
- material families
- samlet source inventory

After-action-contracten binder Core's authoritative causal data til outcome, causal highlights, team story, retry/replay og accessibility. Individuelle titler er `off` indtil OQ-010 støtter dem.

---

# CI / kvalitet

Aktive guards:

- Core tests
- Validate handoff
- Validate non-Unity sources
- Validate source inventory
- action placeholder-cost mirror
- AU-1 regeneration/validation
- event presentation validation

`Validate source inventory` er nu **implementeret og grøn**. Den kontrollerer package/content paths, dublet-ID'er, `producedIds`-coverage og A2 `individualMasterIds`.

Source-art får visuel/layout QA, når relevant. Supply-crate overflow blev fx fundet og rettet før merge.

---

# Repo hygiene

PR #12 fjernede 89 tracked genererede `src/**/bin/` build/test-filer. `.gitignore` dækkede allerede mapperne, og Core tests var grønne efter cleanup. Gælden er lukket.

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

1. fortsæt stabile B1/world source assets uden at duplikere eksisterende source
2. bind producerede release-UI source surfaces til copy/localization som machine-readable handoff
3. actual audio source production/acquisition: Foley → ambience → radio VO; ingen fake WAV-status
4. yderligere machine-readable presentation/content contracts, kun hvor de reducerer Unity-gætteri
5. richer environment/polish først når geometry/device evidence reducerer rework-risiko
6. private personalization source uden for public repo senere
7. M1 implementation handoff når både M0b + M-Pre er grønne

## Kendte ikke-leverede artifacts

- ember-carrier source blev genereret som blob, men commit blev filtreret; tælles **ikke** som produceret
- repair-mallet source blev genereret som blob, men er ikke committed; tælles **ikke** som produceret

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
