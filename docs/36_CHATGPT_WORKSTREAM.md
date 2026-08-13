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

`tools/validate_planning_status_ui.py` håndhæver nu cross-file-kæden: canonical action fields, localization keys, A1 icons, effort markers, player identity og wrist-status source paths. Den kører via den eksisterende non-Unity CI og er grøn på commit `556cb153`.

---

# M-Pre testværktøj

`tools/evaluate_mpre.py` evaluerer kun anonymt, faktisk human-session CSV-input mod den accepterede gate i `docs/35`.

`prototype/m-pre/facilitator_runner.html` er nu en offline browser-runner til de faktiske menneskesessioner:

- anonym `session_id` + `pair_id`
- tre dages forhandlingstimere
- uenighed + meningsskift
- lokale observationer/debrief
- delayed storm reveal efter dag 3
- lokal batch i browseren
- evaluator-kompatibel CSV
- separat notes-JSON
- ingen backend/netværksafhængighed

Kode-/kontrakt-QA:

- `tools/test_evaluate_mpre.py` bruger kun midlertidige syntetiske data og producerer aldrig playtest-evidens.
- `tools/test_mpre_facilitator_runner.py` kontrollerer offline-only, anonym fields, seks task cards, CSV-schema parity, lokal batch/download og at runneren ikke selv afgør projektgaten.
- M-Pre CI på commit `46331542` er **grøn med 10/10 tests**: 4 evaluator-tests + 6 runner-contract-tests.
- dækkede evaluator-cases: 2/3 grøn → GREEN; 1/3 grøn → gyldig RED; ét testerpar → invalid; non-human/gavemodtager → invalid.

M-Pre er stadig **ikke kørt**. Runner, evaluator og syntetisk kode-QA må aldrig tælles som menneskelig evidens.

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
- `tools/test_audio_acquisition_contract.py` kontrollerer kandidat-ID/filnavne, CC0-policy, HTTPS source evidence, private output-isolation, SHA-256-helper og at listening-state-kæden ikke kan springes over.
- audio acquisition-contract-testene køres nu inde fra `tools/validate_non_unity_sources.py`; non-Unity CI på commit `1af4b0ba` er grøn.

**Vigtigt:** WAV/FLAC-originalerne er stadig ikke acquired i denne ChatGPT-runtime. Både container-download og browser/web-binary retrieval er blokeret, så der markeres fortsat ingen naturalistiske masters som producerede.

## Radio / musik

- Radio VO: 9 cues × 3 takes specificeret; faktisk recording mangler.
- Musik: direction/cue-sheet klar; composition/source mangler.

---

# CI / kvalitet

Aktive guards omfatter:

- Core tests
- Validate handoff
- Validate non-Unity sources
  - generelle source contracts
  - planning/status cross-file links
  - natural audio acquisition/listening contract
- Validate source inventory
- Validate M-Pre evaluator/runner
- action placeholder-cost mirror
- AU-1 regeneration/validation
- event presentation validation

Aktuel verificeret status:

- planning/status validator: grøn via non-Unity CI på `556cb153`
- M-Pre evaluator + runner QA: grøn 10/10 på `46331542`
- natural audio acquisition contract: grøn via non-Unity CI på `1af4b0ba`

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

1. **M-Pre human sessions**: næste reelle produktgate; offline runner, evaluator og facilitatorpakke er klar.
2. **Actual audio acquisition + listening QA** på en internetforbundet workstation; ingen fake WAV-status.
3. **Derived audio masters/Foley/ambience** først når originals faktisk er acquired og godkendt.
4. **Radio VO recording** efter samme provenance/listening pipeline.
5. Fortsæt kun B1/source-art hvor en konkret manglende master reducerer Unity-gætteri; undgå grafikproduktion for grafikkens egen skyld.
6. Richer environment/polish og torso først når geometry/device evidence reducerer rework-risiko.
7. Private personalization source uden for public repo senere.
8. M1 implementation handoff når både M0b + M-Pre er grønne.

## Kendte ikke-leverede artifacts / gæld

- ember-carrier source blev genereret som blob, men commit blev filtreret; tælles **ikke** som produceret
- repair-mallet source blev genereret som blob, men er ikke committed; tælles **ikke** som produceret
- fuld gameplay interaction-feedback JSON-binding blev filtreret; planning/status-delen blev i stedet leveret som separat contract
- `docs/38_SOURCE_ASSET_MANIFEST.md` har stadig stale statuslinjer for rope-strain og player hands; inventory + denne workstream er korrekte, og manifest-rewrite blev filtreret
- den ønskede in-place robusthedsrewrite af `facilitator_runner.html` blev filtreret; den committed runner er statisk kontrakttestet og må fortsat browser-smoke-testes ved første faktiske testafvikling

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
