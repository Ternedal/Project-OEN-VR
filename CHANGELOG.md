# Changelog

## 2.7 - 2026-08-09

ADR-022 og ADR-023 accepteret af ejeren og indarbejdet.

- **M-Pre er nu en milepael** i docs/12 og docs/17 med backlog-item **PO-110** (15 t, P0, In). Gaten ligger
  foer M1: bevis kernehypotesen paa papir, foer der bygges gameplay og content oven paa den.
- **Ny fil: docs/35_M_PRE_GREYBOX_GATE.md** - koerbar protokol. Seks opgavekort, fire markoerer, tre dage
  plus storm; fem maalepunkter med taerskler; gate-kriterium og fire konkrete redesign-knapper ved roedt.
  Eksplicit: gavemodtageren maa ikke vaere tester.
- **M5 markeret som Release 1** (ADR-023) i begge dokumenter: een spilbar dag plus storm i tre faser er den
  afsendbare gave; M6-M9 er stretch.
- **Tal opdateret** efter PO-110: gaveversion 997 -> **1.012 t** (P0 631 + P1 381, 77 items), aktiv backlog
  1.436 -> **1.451 t** over 108 items. Validatorens forventede summer er rettet tilsvarende.
- PR #2 (DP-001) lukket som afloest af #4.

## 2.6 - 2026-08-09

Genindfoerer to beslutninger fra DP-001, som aldrig blev merget.

- **ADR-022 (Proposed): M-Pre greybox-gate.** Kernehypotesen - at markoerallokering skaber diskussion frem for administration - bevises i dag foerst i M3, efter hele platform- og netvaerkslaget. Ny milepael paa 10-20 t uden VR og uden netvaerk, placeret foer M1. DP-001 placerede gaten foer M0; det er overhalet, da M0a er afgjort og M0b er per-klient bevist on-device.
- **ADR-023 (Proposed): Release 1 = afslutning af M5.** Gaveversionen er 997 t uden ekstern deadline. En eksplicit afsendbar delmaengde - een spilbar dag plus storm i tre faser - giver projektet et defineret "faerdigt", laenge foer backloggen er tom.
- **R-013 registreret** i docs/14: momentum-drift, hoej/hoej, mitigeret af de to ADR'er ovenfor. DP-001 registrerede den som R-011, men det nummer er optaget af purchased-asset visual clash.

Resten af DP-001 (PR #2) er ikke taget med: den kolliderer med ADR-019/020/021 i main og foreskriver Unity 6000.3.x og Fusion 2.1, hvor projektet allerede koerer 6000.4.10f1 og Fusion 2.0.12 verificeret paa hardware.

## 2.5 - 2026-08-09

Konsistensoprydning efter `DROP_Q1_RUNTIME` plus M0b-fremdrift on-device.

- **Docs:** beslutningen var truffet 08-08, men Quest 1 stod stadig som runtime-lane, testplatform eller acceptkriterium i ~25 filer. Rettet i docs/01, 02, 06, 07, 08, 11, 12, 13, 14, 15, 17, 19, 20, 21, 23, 24, 25, 26, 27, 30, 32, 34 samt README, CLAUDE.md, 00_READ_ME_FIRST, 01_PROMPT_FOR_CLAUDE (arkiveret), repo_status, VALIDATION_REPORT, review/RESPONSE_MATRIX, diagrams og PR-/issue-skabeloner.
- **docs/08:** Q1-legacyafsnittet erstattet af en udgaaet-note; distributionsmatricen, M5-gaten, lighting- og assetbudgettet renset for Q1. GLES3-fallbacken (OQ-003) fjernet - Vulkan er eneste API.
- **docs/13:** Q1 fjernet fra release gates og Definition of Done.
- **docs/17:** R-001 lukket, E00/E12/M7 omformuleret, 16 Testplatform-celler sat til Q2/Q3, PO-083 og PO-087 reduceret (9 t frigjort).
- **docs/19:** OQ-001, OQ-002 og OQ-003 lukket med resultat.
- **docs/14:** Quest 1 exit-kriteriet markeret som UDLOEST; estimater rettet til 616 t P0 / 1.006 t gaveversion.
- **Ny fil:** `config/COMPATIBILITY_MATRIX.md` oprettet (uden Q1-kolonne), forudfyldt med M0a/M0b-resultater.
- **M0b on-device:** head-tracking loest - poser drives nu fra `UnityEngine.XR.InputDevices` i stedet for en ubundet `TrackedPoseDriver` (som skrev nul-pose). Verificeret paa Quest: head ikke-nul og bevaegelig, greb -> `CoopSolver` flytter kassen, `quality` 1,00. Se `src/unity/RUNBOOK_FUSION.md` §8.
- **Afventer on-device med to headset:** head/hands mellem klienter, handshake-gate, 10x loeftetest, 72 Hz-maaling.

## 2.4 — 2026-08-08

Bygget videre på Core (efter M0a). Første post-M0a-feature.

- `src/ProjectOen.Core/Interaction/InteractionSequence.cs`: PO-040 — den authorbare coop-opgave-model. Primær/sekundær-roller, vægtede trin, deterministisk score i [0,1] der fødes til `OutcomeResolver.Tier`. Coop-præmissen håndhæves: en opgave løst af én spiller alene loftes ved `PartialWithCost` (CoopSoloCeiling). Content-validering fanger dårligt forfattede sekvenser ved indlæsning. **15 nye tests.** Grundlaget crafting-content (PO-042 shelter, PO-044 fire) bygger videre på.

## 2.3 — 2026-08-08

M0a kørt og afgjort på hardware. Beslutning: **`DROP_Q1_RUNTIME`**.

- Hele M0a-kæden kørt headless + on-device. Fem reelle fejl fundet og rettet på vejen: `manifest.json` UTF-8 BOM → ASCII; `M0aBuild.cs` CS1503-cast; reflection-XR-opsætning omskrevet til direkte, compile-tjekkede XR Management/OpenXR-kald (oprettede aldrig `XRManagerSettings` før → NullReference); Configure og Build splittet i hver sin Unity-session ("OpenXR Settings not yet loaded"); Windows Smart App Control blokerede Unitys Bee-DLL (`0x800711C7`, slået fra af ejer).
- **Quest 2:** samme OpenXR-APK kører immersivt, head-tracking `valid=True tracked=True`, 71,8 fps, Vulkan.
- **Quest 1:** deterministisk native crash — SIGABRT i `libopenxr_loader.so` kaldt fra `libUnityOpenXR.so` under XR-opstart, før første frame (to forsøg, tombstone). Unitys OpenXR-provider kan ikke initialisere mod Q1's frosne v50-runtime.
- **Beslutning `DROP_Q1_RUNTIME`** dokumenteret i `prototype/m0a-openxr-smoke/RESULTAT.md`. Lukker den åbne halvdel af CR-002.
- Konsekvens indarbejdet i baseline: ADR-004 superseded, ADR-018 resolved, ADR-019 accepted (docs/18); `Q1_LEGACY` arkiveret (docs/08); Q1 fjernet fra device-matrix + COMPAT-001 udgået (docs/13); PO-004/PO-007/PO-098 droppet og 18 t frigjort fra P0, PO-025 reduceret til Q2↔Q3 (docs/17).
- `M0a`-automatisering committet som durable: `Build-M0a.ps1` (ASCII-manifest + Configure/Build i to sessioner) og den omskrevne `M0aBuild.cs`.

## 2.2 — 2026-08-07

Core-lag bygget og bevist, mens M0a venter på hardware.

- `src/ProjectOen.Core`: typed IDs, kanonisk JSON, save-checksum, atomisk skrivning, fuld snapshot round-trip, scenario-kontraktvalidering, fasemaskine med idempotens, delayed events med proveniens, udfaldsformel med gulv-regel, coop-solver, compatibility handshake, join code, deltagelsesmåling, efterspilsrapport, data-drevet win/lose og handlingseffekter. **110 tests grønne.**
- `.github/workflows/core-tests.yml`: testene kører nu i CI på hvert push. Indtil da beskyttede de ingenting mellem manuelle kørsler.
- `prototype/m0a-openxr-smoke/`: runbook, resultatskema og drop-in kildefiler til hardwaretesten.
- `src/unity/`: Fusion-binding som ukompilerede kildefiler med `UNVERIFIED-IN-SANDBOX`-header og API-antagelser pr. fil.
- `docs/33`: tre fejl fundet ved måling frem for gennemlæsning — udfaldsformlens klumpning, coop-solverens hastighedsloft, og events der blev journaliseret to gange.
- `docs/34`: indhold til Notion-projektsiden (connector-skrivning afvist).
- CR-007 lukket i kode: "begge aktive" måles nu fra event-journalen i stedet for at observeres.

## 2.1 — 2026-08-07

Behandling af Claude-review v1.0, merget til `main`. Alle 10 fund og 6 konflikter dispositioneret i `review/RESPONSE_MATRIX.md`. To punkter er bevidst stadig åbne: CR-002 (kræver fysisk Q1-test) og CR-005 (kræver ejerens P1-udvælgelse).

- **CR-003/CR-004/CONFLICT-004/CONFLICT-005:** faktarettelser. Unity 2022.3 LTS er uden patchsupport på Personal/Pro; editorvalget er nu M0-afhængigt (ADR-006 rev.). Quest 2 EOL-datoer skrevet ind (ADR-003 rev.). P0-sum rettet 620 → 622. Nye ADR-019/020/021. Kilderegister udvidet.
- **CR-001/CR-005:** M0 omlagt til platform- **og** netværksfeasibility (176 t, 19 items); PO-017/018/019/020/022/025 flyttet fra M2. M0a defineret som det afgørende OpenXR-eksperiment. Stop/go flyttet fra 250-timers loft til M0-afslutning. Backloggen har fået kolonnen `Gaveversion`; roadmapintervaller bundet til faktiske itemsummer. Tallet 500-810 t trukket tilbage indtil P1-udvælgelsen.
- **CR-006/CR-007/CR-009/CONFLICT-002/003/006:** datakontrakten lukket. `supportedBuildProtocol`, `actionCatalog` og `cooldown` tilføjet; `revision` gjort påkrævet; checksum defineret som SHA-256 over kanonisk JSON og beregnet i eksemplet. `validate_handoff.py` håndhæver nu begge dele — verificeret ved negativ test. Passivitetsgrænser ensrettet (12 s design / 20 s test). UX-002 gjort automatisk. Fire nye testcases: PERF-002, DEV-002, DEV-003, COMPAT-002.
- **CR-008/CR-010:** PO-000 (reviewbehandling, M0/P0) og PO-104 (lokalisering) tilføjet. Backlog: 110 items, 1.473 t.
- `docs/30` omskrevet: M0a-eksperimentet først, med dokumenteret baggrund og tre eksplicitte udfald.
- `docs/32` tilføjet: eksekveringsplan fra behandlet review til bestået M0.

## 2.0-review — 2026-08-06

- Modtaget første komplette Claude-review: `review/CLAUDE_RAW_REVIEW.md` (verdict `PROCEED_WITH_BLOCKERS`).
- 10 fund (CR-001 … CR-010: 2 BLOCKER, 5 HIGH, 3 MEDIUM) og 6 dokumentkonflikter (CONFLICT-001 … CONFLICT-006).
- `review/RESPONSE_MATRIX.md` forudfyldt med alle CR- og CONFLICT-ID'er; dispositioner afventer ejeren.
- `repo_status.md` opdateret: review state og Q1-lanens status.
- Ingen spec, ADR eller backlog er ændret — gaten i `docs/24` er ikke passeret.

## 2.0 - 2026-08-05

- Omdannet tidligere GDD v1.1 til komplet Claude-handoff.
- Tilføjet reviewprotocol, response matrix og source-of-truth.
- Udbygget gameplay-, scenario-, multiplayer-, platform-, data-, QA- og engineering specs.
- Tilføjet JSON schemas og konkrete content/save examples.
- Tilføjet diagrams, repo templates og build checklists.
- Platformstrategi fastholdt: Quest 2 baseline, Quest 1 legacy-test, Quest 3 enhanced.

## 1.1

- Quest 1/2/3 platformstrategi tilføjet til tidligere masterdokument.

## 2.0 repository bootstrap

- Tilføjet GitHub-klar README, CLAUDE.md, proprietary notice og Unity-.gitignore.
- Tilføjet issue-/PR-skabeloner, CODEOWNERS og valideringsworkflow.
- Tilføjet lokalt validerings- og manifestværktøj.
- Tilføjet master-PDF samt GitHub-bootstrapvejledning.
