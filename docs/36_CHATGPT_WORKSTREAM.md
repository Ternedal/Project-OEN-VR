# ChatGPT-workstream — PROJECT ØEN

**Ejer:** ChatGPT  
**Projektejer:** Anders  
**Opdateret:** 2026-08-13  
**Scope:** Alt uden for Unity jf. `AI_COLLABORATION_AGREEMENT.md`

## Arbejdsregel

M0b + M-Pre blokerer **M1-implementation**, ikke det parallelle non-Unity-produktionsspor.

Human/device evidence blokerer kun de valg, balanceparametre og acceptance gates, som faktisk kræver evidensen. ChatGPT fortsætter derfor med source-art, audio-source, content authoring, UX/copy, QA, provenance, narrative og handoff-forberedelse uden at ændre Unity-runtime.

## Autoritativ produktionsstatus

Den machine-readable status ligger i:

`content/source_inventory.source.json`

Den fil er fremover første reference for spørgsmålet: **hvad er faktisk produceret, hvad er kun spec/source-ready, og hvad mangler?**

`source_art/PROVENANCE_INDEX.md` er autoritativ for source-art provenance.

---

# Aktuelle gates

## M0b — Claude / Unity

Tracker: GitHub issue #3. Cross-device/device evidence mangler fortsat.

## M-Pre — ChatGPT / produkt

Tracker: GitHub issue #7. Testpakken er ready-to-run; der mangler tre menneskelige sessioner med mindst to forskellige par.

## Content contract

Tracker: GitHub issue #8.

- intro → eksplicit onboarding-sequence foreslået
- Day 3 → eksplicit planning phase foreslået
- minimal fire-start → source/spec klar, men gave-scope kræver Anders' disposition

Proposal-data under `content/proposals/` er fortsat `proposal-not-canonical`.

---

# Leveret foundation

Produkt/design/QA-pakken dækker bl.a.:

- non-Unity gap audit
- source asset/audio manifests
- dansk UX/copy/localization
- personalization/privacy/fallback
- human QA M1-M9
- IP/provenance
- Stormnatten content coverage og 10-event catalog
- visual style/UI IA
- gift/release-flow
- after-action/replay
- telemetry/metrics
- backlog ownership overlay
- narrative continuity
- content-contract proposals
- source production batch plan

Interaction handoffs findes for:

- planning table
- shelter reinforcement
- fire start
- ravine rescue
- storm finale

---

# Faktisk source-artproduktion

## Produceret

- **A1 UI/source kit** — gameplay/status/action symbols, effort markers, cards og interaction feedback
- **Neutral fallback** — fictional chart, compass, route card og signal tag
- **A2 core-prop references** — separate prop briefs + concept/reference SVGs
- **A3 storm VFX source** — rain, debris, embers, smoke, impact, wetness og storm-phase refs
- **A4 camp source-reference** — camp layout/state progression
- **B1 environment source-reference** — jungle/ravine/ridge readability
- **B1 world-items** — wood, fiber, herbs, food og general supplies
- **B1 ravine props** — anchor + guide markers
- **B2 event presentation** — source presentation for all ten authored events + machine-readable mapping

## Ny A5-bølge — delvist produceret

### Unity-venlige external source meshes

`source_art/props/a5/`:

- `PRP_WIND_SHIELD_001.obj`
- `PRP_DRY_FUEL_CACHE_001.obj`
- `PRP_SIGNAL_FUEL_001.obj`

De er meter/Y-up source meshes uden Unity-materialer, colliders, LOD eller runtimeopsætning. Unity-import og runtime-ejerskab forbliver Claude.

### Source items

`source_art/items/a5/`:

- `ITM_CLOTH_001.svg`
- `ITM_MAP_FRAGMENT_001.svg`

### Release UI

`source_art/ui/a5/`:

- `UI_RECONNECT_PANEL_001.svg`
- `UI_JOIN_CODE_PANEL_001.svg`

Nogle yderligere source-art write-kald er blevet sikkerhedsblokeret af connectoren. De blokeringer omgås ikke; arbejdet fortsætter på andre ublokerede leverancer.

---

# Audio/source-status

## AU-1

Deterministisk generator til korte syntetiske UI/system-cues findes under `source_audio/au1/` og har CI-verifikation.

## Foley

`content/audio/foley_recording_queue.source.json` er nu recording-ready med:

- cue-ID
- variantantal
- filnavnemønster
- mållængde
- recording intent
- 48 kHz / 24-bit sourcekrav
- QA-regler

## Ambience

`content/audio/ambience_acquisition_queue.source.json` definerer acquisition/production-kø for:

- wind L0-L3
- light/heavy rain
- beach/camp
- jungle
- ravine
- camp night

Naturalistisk Foley/ambience er **ikke** fejlagtigt markeret som produceret WAV endnu.

## VO og musik

- neutral radio-VO: script/source-ready, recording mangler
- musik: direction/cue-sheet ready, composition/source mangler

---

# Machine-readable content

Aktuelle source contracts omfatter:

- dansk localization
- Stormnatten actions
- placeholder cost mirror
- ten-event authoring
- event→presentation mapping
- neutral personalization profile
- onboarding/Day 3 proposals
- Foley recording queue
- ambience acquisition queue
- samlet source inventory

---

# CI / kvalitet

Aktive non-Unity guards omfatter bl.a.:

- non-Unity source validation
- action placeholder-cost mirror
- AU-1 source audio regeneration/validation
- event presentation validation

Action-cost-valideringen fangede tidligere en forkert antagelse i ChatGPT-source og er efter rettelse grøn. Dette er den ønskede model: source contracts skal kunne afsløre vores egne fejl før Claude integrerer dem.

---

# Repo hygiene

`.gitignore` ignorerer eksplicit `src/**/bin/` og `src/**/obj/`, men tracked `bin/` buildoutputs findes fortsat i repositoryet.

Det er bekræftet repo-gæld. En atomisk bulk-cleanup via connectorens tree-operation blev sikkerhedsblokeret, så den er **ikke** forsøgt omgået. Ingen filer er slettet på et usikkert grundlag.

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

Prioritet i denne rækkefølge, medmindre repo/evidence ændrer den:

1. resterende A-priority world/source items og release-UI, hvor connectoren tillader sikre writes
2. audio natural-source production: Foley → ambience → radio VO → minimal music
3. source inventory/provenance reconciliation efter hver reel produktionsbatch
4. yderligere machine-readable contracts hvor de reducerer Unity-gætteri
5. richer camp/environment art først når geometry/device evidence gør rework-risiko acceptabel
6. private personalization source uden for public repo senere
7. M1 implementation handoff når både M0b + M-Pre er grønne

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
