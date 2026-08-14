# Repository status

**Opdateret:** 2026-08-14

## Baseline

- Baseline: **v2.1**.
- Quest 2 = performance-/kvalitetsgulv.
- Quest 3/3S = enhanced parity.
- Quest 1 = droppet runtime/testlane (`DROP_Q1_RUNTIME`); kun historisk/frossen sideload-demo.
- Gaveversion = **1.012 t**; 439 t deferred efter v1.0, så længe owner-gated fire-start ikke promoveres.
- M5 = Release 1.
- Arbejdsdeling: `AI_COLLABORATION_AGREEMENT.md` — Claude = Unity/runtime/device; ChatGPT = non-Unity produkt/content/source/QA.

---

# Aktuelle gates

## M0b — Claude / Unity

Tracker: GitHub issue #3.

Per-client feasibility er dokumenteret. Rigtig cross-device Quest-evidens mangler fortsat, herunder remote head/hands, mismatch rejection, shared-state, 10× Q2↔Q3, 72 Hz, standby/reconnect og compatibility matrix.

Ingen synthetic/self-test må lukke denne gate.

## M-Pre — human product evidence

Tracker: GitHub issue #7.

Ready-to-run material findes i `prototype/m-pre/`. Repoet har nu også en tamper-evident evidence-bundle pipeline:

- `content/mpre/evidence_bundle_contract.source.json`
- `tools/package_mpre_evidence.py`
- `tools/validate_mpre_evidence_bundle.py`

Der er fortsat **ingen påståede menneskesessioner**. Gate kræver tre reelle sessioner og mindst to testerpar; bundle-tooling kan kun validere/hashbinde leveret menneskeevidens.

## Content contract / fire-start

Tracker: GitHub issue #8.

- onboarding er canonical i `content/onboarding/stormnatten.onboarding.source.json`
- Day 3 planning er canonical i `content/phases/stormnatten.day3_planning.source.json`
- proposal-filer under `content/proposals/` er historiske/non-canonical
- fire-start er fortsat owner-gated og må ikke promoveres uden Anders' eksplicitte scope-disposition

**M1 åbner først efter grøn M0b + M-Pre.** Det stopper ikke ublokeret non-Unity-sourcearbejde.

---

# Core / Unity

Core Actions er grønne efter de seneste non-Unity merges.

Unity/Fusion-laget ejes af Claude. Den reelle tekniske gate er M0b cross-device/device evidence — ikke historiske labels om “ukompileret Fusion”.

Draft PR #5 og #6 forbliver fysisk QA-blokerede og må ikke merges alene på synthetic/CI-evidens.

---

# ChatGPT / non-Unity

## Autoritativ status

- machine-readable produktionsstatus: `content/source_inventory.source.json`
- asset-ID/funktionsmanifest: `docs/38_SOURCE_ASSET_MANIFEST.md`
- source-art provenance: `source_art/PROVENANCE_INDEX.md`
- denne fil: kort menneskelig repo-status

`source-ready`, `candidate-ready` og `technical-intake-passed` betyder **ikke** Unity-integreret, human-approved eller release-approved.

## Produkt/design/content

Canonical non-Unity foundation omfatter bl.a.:

- dansk UX/copy/localization
- Stormnatten actions/events/presentation
- canonical onboarding og Day 3 planning
- neutral personalization fallback
- after-action presentation
- material families
- release/planning UI source
- storm-finale source contract
- source-closeout for utility knife, torso-reference og epilogue-reference
- M-Pre facilitator/evidence-bundle tooling

---

# Source-art på main

Producerede sourcepakker omfatter nu bl.a.:

- **A1:** gameplay/status/action UI
- **Neutral:** fictional chart, compass, route card og signal tag
- **A2:** core prop reference + 10 individuelle masters
- **A3:** storm VFX/source references inkl. rope-strain
- **A4:** camp layout/state + wreck, ground, radio og signal progression refs
- **B1 environment:** jungle/ravine/ridge + ravine anchor/guide markers
- **B1 resources/items:** wood/fiber/herbs/food/general supplies + `ITM_KNIFE_001`
- **B1 utility:** supply crate source
- **B2:** event presentation source + mapping for alle 10 events
- **Character:** P1/P2 hand refs + `CHR_TORSO_BASE_001`
- **C1:** `ENV_EPILOGUE_001` reuse-first ending reference
- **A5 meshes:** wind shield, dry-fuel cache, signal fuel, firepit og waterproof ending crate
- **A5 items:** cloth, map fragment, radio battery, ember carrier og repair mallet
- **A5 release UI:** join, reconnect, setup, pause, ready-state og subtitle band

Claude ejer runtime-import, prefabs, colliders, materials, IK/networking, performance og device QA.

---

# Audio/source-status

## AU-1 / authored feedback

Deterministisk generator til korte UI/system cues er source- og CI-valideret. Runtime mix/binding er Claude-lane.

## Foley / naturalistic sources

Wood/cloth extension packs er acquired og teknisk shortlisted. Naturlig Foley er **ikke** generelt human-approved eller færdigmasteret; human audition og evt. field recording mangler dér, hvor pack-fit ikke er godt nok.

## Ambience / environment

Repoet har nu faktiske originale/acquired sources med provenance og objektiv QA:

- base acquisition: wind, rain og fire
- extension acquisition: ocean + wood/cloth packs
- field-backlog receipt: syv yderligere originals

De er **ikke automatisk listening/source-approved**. `tools/normalize_audio_field_review.py` hashbinder menneskelig review-evidens uden at promovere source-status.

## Radio VO

9 cues × 3 takes er specificeret, og repoet har nu en fail-closed 27-take technical intake:

- `content/audio/radio_vo_session_contract.source.json`
- `tools/prepare_radio_vo_session.py`
- `tools/validate_radio_vo_session.py`

Faktisk menneskelig recording, dansk pronunciation/delivery review og listening approval mangler fortsat.

## Musik

14 originale procedurale adaptive-music candidates er auditeret og audition-ready:

- `content/audio/music_candidate_audit.source.json`
- fem candidate-families er mappet til eksisterende canonical music cues
- `MUS_Warning_LowPulse` er eksplicit unmapped

PR #33 har bevaret den originale generator på `main` og tilføjet exact-byte reproducibility. CI reproducerede **14/14 SHA-256-identiske WAVs** med Ubuntu 24.04 / CPython 3.12.13 / NumPy 2.3.5.

Det fjerner afhængigheden af den tidsbegrænsede PR #6 artifact, men **human audition/source promotion mangler stadig**.

---

# CI / kvalitet

Aktive non-Unity guards omfatter bl.a.:

- Core tests
- Validate handoff
- Validate non-Unity sources
- Validate source inventory
- source-inventory backing
- audio manifest alignment
- source closeout validation
- radio VO session tooling
- music candidate audition tooling
- **music exact-byte candidate reproducibility**
- M-Pre evidence-bundle tooling
- audio acquisition/listening/field-review validators

Ingen af disse CI-checks må bruges som erstatning for menneskelig listening/playtest eller Quest-device evidence.

---

# Fortsat åbent på ChatGPT/non-Unity-siden

Den brede automatable source-backlog er ikke længere den primære flaskehals. De væsentlige næste skridt er nu:

1. menneskelig audition/selection af acquired ambience/Foley sources
2. menneskelig audition af de 14 music candidates og eksplicit source promotion af valgte candidates
3. faktisk radio-VO recording + pronunciation/delivery/listening review
4. tre reelle M-Pre sessions + bundle/acceptance flow
5. status/backlog-opdatering efter rigtig human/device evidence
6. richer environment/polish kun når stabil geometry/device evidence gør det nyttigt
7. private personalization source uden for public repo, når det faktisk skal produceres
8. M1 handoff assembly når M0b + M-Pre er grønne

Genererede, private eller lokalt auditerede artifacts tælles aldrig som release-/human-approved alene.

---

# Parallelle handlinger

- Claude fortsætter issue #3 og fysisk Unity/Quest QA på #5/#6.
- M-Pre human sessions er nødvendig input til issue #7.
- Fire-start scope i issue #8 kræver Anders' beslutning.
- ChatGPT fortsætter non-Unity source/review tooling og statusreconciliation uden at fabrikere human/device evidence.
