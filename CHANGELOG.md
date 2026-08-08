# Changelog

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
