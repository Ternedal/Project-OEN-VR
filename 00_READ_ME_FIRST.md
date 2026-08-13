# PROJECT ØEN — STRANDET SAMMEN

**Opdateret:** 2026-08-13  
**Status:** Aktiv udvikling · M0b cross-device i gang · M-Pre klar til mennesketest  
**Format:** To-spiller kooperativt VR-overlevelsesspil  
**Primær platform:** Meta Quest 2  
**Forbedrede platforme:** Meta Quest 3 / Quest 3S  
**Udgået runtime/testlane:** Meta Quest 1 (`DROP_Q1_RUNTIME`, 2026-08-08)

---

## Formål

Dette er projektets indgangsdokument og øverste dokumenthierarki.

Projektet er **ikke længere i pre-review-fasen**. Det kritiske review er gennemført og behandlet, baseline v2.1 er på `main`, Core-laget er testet, Unity-projektet er etableret, M0a er afsluttet, og arbejdet står nu ved to gates:

1. **M0b:** cross-device platform/netværksbevis i Claude/Unity-sporet.
2. **M-Pre:** menneskelig greybox-test af kernehypotesen i ChatGPT/produkt-sporet.

M1 må først begynde, når begge gates er grønne.

---

# Hårde krav

1. Quest 2 er projektets performance- og kvalitetsgulv.
2. Quest 3/3S skal have samme gameplay og må kun få additive forbedringer.
3. Quest 1 er ikke en runtime-, build- eller testlane. Den er højst en frossen sideload-demo uden for hovedprojektet.
4. Gaveversionen/MVP'en har præcis to spillere.
5. Begge spillere skal være aktive; ingen må være passiv tilskuer gennem længere gameplaysekvenser.
6. Første fulde scenario er cirka 30-45 minutter og er ikke et open-world survival-spil.
7. Projektet er original IP og må ikke være en uautoriseret digital kopi af *Robinson Crusoe: Adventures on the Cursed Island*.
8. Produktgates må ikke erklæres grønne uden den evidens, deres protokol kræver.
9. Device-gates må ikke erklæres grønne ud fra compile eller kildekode alene.
10. Dyr art/contentproduktion skal vente til de relevante greybox-/produktgates tillader det.

---

# Source of truth

Ved konflikt gælder denne rækkefølge:

1. `00_READ_ME_FIRST.md` — faste rammer og dokumenthierarki.
2. `docs/01_EXECUTIVE_HANDOFF.md` — gældende produktbeslutninger.
3. `docs/18_DECISION_LOG.md` — accepterede beslutninger/ADR'er.
4. `docs/06_TECHNICAL_ARCHITECTURE.md` og `docs/08_PLATFORM_BUILD_PERFORMANCE.md` — tekniske beslutninger.
5. `docs/03_CURRENT_MASTER_SPEC_v1.1.md` — samlet baseline.
6. `docs/12_PRODUCTION_ROADMAP.md`, `docs/17_BACKLOG_AND_MILESTONES.md` — plan og scope.
7. Backlogdetaljer, eksempler, skemaer og runbooks — implementerings-/testdetaljer.

`repo_status.md` er den hurtige status-snapshot og skal afspejle ovenstående, men overstyrer ikke accepted ADR'er.

`AI_COLLABORATION_AGREEMENT.md` er særskilt autoritativ for **rolle-, ansvar- og handoff-grænser mellem ChatGPT og Claude**.

Reelle konflikter må ikke løses stiltiende. Dokumentér dem og opdatér de berørte source-of-truth-filer/ADR'er.

---

# Samarbejdsmodel

Fra 2026-08-13 gælder:

## Claude = Unity

Claude ejer:

- Unity-projekt og Unity-runtime/editor
- C# der indgår i Unity-runtime
- XR/OpenXR/Fusion
- scenes, prefabs og components
- Unity asset/audio integration
- builds og signing-relateret Unity-konfiguration
- profiling/performance
- Unity-side QA

## ChatGPT = alt andet

ChatGPT ejer:

- produkt- og gameplay-design
- specs og roadmap
- source-assets og art direction
- lyd-design/source-materiale
- design-/playtestprotokoller
- ekstern arkitektur
- produkt-QA
- handoff til Claude

Anders er produktejer og har altid sidste ord.

Se `AI_COLLABORATION_AGREEMENT.md` for fuld aftale.

---

# Aktuel verificeret status

## Review og baseline

- Kritisk review v1.0 er gennemført, dispositioneret og merget.
- Alle 10 reviewfund er lukket.
- Baseline er v2.1.
- `01_PROMPT_FOR_CLAUDE.md` er arkiveret reviewmateriale og er **ikke** den aktuelle Claude-opgave.

## Core

- `src/ProjectOen.Core` er ren C# uden UnityEngine-afhængighed.
- **146 tests er grønne** og køres i CI.
- Core omfatter bl.a. scenario loading/contracts, save/checksum/snapshot, command/event-state, delayed consequences, outcome model, coop solver, compatibility handshake, join codes og telemetry/after-action.

## M0a — lukket 2026-08-08

- Quest 2: OpenXR starter immersivt; Vulkan og head tracking bevist.
- Quest 1: deterministisk crash under OpenXR-init.
- Beslutning: `DROP_Q1_RUNTIME`.

## M0b — per-client bevist, cross-device mangler

Dokumenteret on-device:

- Unity `6000.4.10f1`
- OpenXR
- Photon Fusion `2.0.12`
- Shared-session forbinder
- NetworkPlayerRig spawner med authority
- head pose er non-zero via `InputDevices`
- coop solver/greb→kasse-kæde kører on-device

Resterende M0b-gate:

1. remote head/hands mellem to klienter
2. handshake mismatch-afvisning
3. delt kasse i to-spiller-state
4. 10× Q2↔Q3-løft uden permanent desync
5. 72 Hz i minimal netværksscene
6. standby/reconnect-måling
7. faktiske resultater i `config/COMPATIBILITY_MATRIX.md`

Dette er Claude/Unity-sporet.

## M-Pre — klar, men ikke kørt

M-Pre tester om fordelingen af fire indsatsmarkører skaber reel diskussion frem for administration.

Ready-to-run-pakken ligger i `prototype/m-pre/`.

Gaten kræver mindst tre menneskelige sessions med mindst to forskellige par. Resultatet må ikke simuleres eller afgøres af AI alene.

Dette er ChatGPT/produkt-sporet sammen med Anders.

---

# Læserækkefølge — Claude

1. `AI_COLLABORATION_AGREEMENT.md`
2. `repo_status.md`
3. `CLAUDE.md`
4. `docs/32_OPUS_EXECUTION_PLAN.md`
5. `config/COMPATIBILITY_MATRIX.md`
6. `src/unity/RUNBOOK_FUSION.md`
7. `docs/06_TECHNICAL_ARCHITECTURE.md`
8. `docs/07_MULTIPLAYER_NETWORKING.md`
9. `docs/08_PLATFORM_BUILD_PERFORMANCE.md`
10. `docs/13_TEST_QA_ACCEPTANCE.md`
11. `docs/35_M_PRE_GREYBOX_GATE.md` — gate der skal være grøn før M1

Reviewfilerne under `review/` og `01_PROMPT_FOR_CLAUDE.md` er historik/evidens, ikke næste arbejdsordre.

---

# Læserækkefølge — ChatGPT

1. `repo_status.md`
2. `docs/36_CHATGPT_WORKSTREAM.md`
3. `docs/01_EXECUTIVE_HANDOFF.md`
4. `docs/04_GAME_DESIGN_DEEP_DIVE.md`
5. `docs/05_STORMNATTEN_CONTENT_BIBLE.md`
6. `docs/11_ART_AUDIO_UI_DIRECTION.md`
7. `docs/12_PRODUCTION_ROADMAP.md`
8. `docs/19_OPEN_QUESTIONS.md`
9. `docs/35_M_PRE_GREYBOX_GATE.md`

ChatGPT ændrer ikke Unity-filer, medmindre Anders eksplicit ændrer arbejdsdelingen.

---

# Aktuelle næste handlinger

## Claude / Unity

Luk M0b cross-device efter GitHub issue #3 og `src/unity/RUNBOOK_FUSION.md`.

## ChatGPT / produkt

- M-Pre-materialet er færdigt.
- OQ-008/OQ-009/OQ-010 har testprotokoller.
- Afvent menneskedata til de gates, der kræver dem.
- Når M-Pre er grøn: forbered M1 player-experience/UX-handoff og derefter relevante source asset/audio manifests.

## Anders

- leverer den fysiske to-headset-testkontekst til M0b
- arrangerer M-Pre med eksterne testere
- træffer produktejerbeslutninger, når evidensen kræver et valg

---

# Ændringsdisciplin

Større beslutninger skal være sporbare:

1. registrér fund/evidens
2. opdatér decision log/ADR ved beslutningsændring
3. opdatér berørte specs/backlog
4. opdatér `repo_status.md`
5. kør relevante validatorer/tests

Hovedprincip:

> **Bevis før polish. Måling slår antagelse.**
