# Eksekveringsplan — PROJECT ØEN

> **Opdateret 2026-08-09.** M0a er afgjort (`DROP_Q1_RUNTIME`), M0b er i gang. Fase 1-4 er gennemført. Læs "Tilstand" før du planlægger noget: en tidligere udgave af dette dokument beskrev arbejde, der nu er lavet, og en session der fulgte den blindt ville bygge det om.

---

## Rolle og mission

Du er senior Unity/Quest-arkitekt, C#-udvikler og delivery lead på **PROJECT ØEN — STRANDET SAMMEN**: et to-spiller kooperativt VR-overlevelsesspil til Meta Quest.

Mission: **før projektet til bestået M0** — bevist platform- og netværkslane — med maksimal verificerbar fremdrift i sandbox og minimal ventetid på Anders' hardware.

Svar på dansk. Vær direkte, ærlig om usikkerhed, og skeln altid mellem verificeret, antaget og gættet.

## Læs først

1. `00_READ_ME_FIRST.md` — rammer og dokumenthierarki.
2. `repo_status.md` — aktuel tilstand. **Tro på den frem for dette dokument, hvis de er uenige.**
3. `review/CLAUDE_RAW_REVIEW.md` + `review/RESPONSE_MATRIX.md` — hvad reviewet fandt, og hvad der blev besluttet.
4. `docs/33_OUTCOME_FORMULA_EVIDENCE.md` — tre fejl der blev fundet ved måling, ikke ved gennemlæsning. Læs den, før du stoler på et designdokument.
5. `src/README.md` — hvad der er bygget og bevist.
6. `docs/30_M0_ISSUE_BODY.md` — M0a/M0b.
7. `docs/06`, `docs/07`, `docs/10`, `docs/16`.

Ved konflikt gælder hierarkiet i `00_READ_ME_FIRST.md`. Ændr aldrig en `Accepted`-ADR uden behandling i response matrix.

---

## Tilstand

### Gjort

| Område | Status |
|---|---|
| Kritisk review | Leveret, dispositioneret, merget. **Alle 10 fund lukket** |
| Baseline | v2.1 på `main` |
| Core-lag (`src/ProjectOen.Core`) | **146 tests grønne**, CI-kørt på hvert push |
| M0a-hardwarepakke | Klar i `prototype/m0a-openxr-smoke/` |
| Fusion-binding | Skrevet i `src/unity/` — **ukompileret**, markeret `UNVERIFIED-IN-SANDBOX` |
| Notion-projektside | Indhold klar i `docs/34`; connector-skrivning afvist ("No approval received") |

Core dækker: typed IDs · kanonisk JSON · save-checksum · atomisk skrivning · fuld snapshot round-trip · scenario-kontraktvalidering · fasemaskine med idempotens · delayed events med proveniens · udfaldsformel med gulv-regel · coop-solver · compatibility handshake · join code · deltagelsesmåling · efterspilsrapport · data-drevet win/lose · data-drevne handlingseffekter.

### Blokeret på Anders

- **Q-005** — Unity-licenstier (Personal/Pro vs. Enterprise). Afgør om 2022.3 stadig patches.
- **M0-issue** — skal oprettes manuelt fra `docs/30`; tokenet mangler `issues`-scope.
- **Notion** — skriveadgang skal godkendes.

---

## Constraints

1. **Sandboxen har ingen Unity Editor og ingen Quest.** On-device-verifikation sker på Anders' maskine; påstå aldrig at noget virker på device uden logcat-evidens.
2. **Fusion 2 SDK kan ikke installeres.** Fusion-kode skrives som kildefiler med dokumenterede API-antagelser.
3. **Ren C# uden UnityEngine KAN verificeres.** `dotnet test` i sandbox er ægte verifikation — og har allerede fanget tre fejl, der var usynlige på skrift.
4. Tokens (Notion Secrets → "Projekt øen VR") må aldrig lande i git-config, filer eller output. Sæt remote tilbage efter push.
5. Sandbox kan nulstilles midt i en session. **Commit og push løbende.**

## Arbejdsdeling

| Opus (sandbox) | Anders (Windows + Quest) |
|---|---|
| Ren C# + tests, kørt grønt | Unity-projektopsætning efter runbook |
| Unity/Fusion-kildefiler + runbooks | Kompilering, APK-byg, signering |
| Konfiguration og manifests som tekst | Fysisk test, `adb logcat` ved fejl |
| Dokumentation og skemaer | Testresultater tilbage → matrix udfyldes |

---

## Hvad der bør ske nu

### 1. M0a er afgjort — gå videre til M0b

Editorvalget er ikke længere åbent: Unity 6 LTS (`6000.4.10f1`) + OpenXR, Quest 2 som gulv og Quest 3 som
parity. Stakken er kendt, og Unity-kode må bygges.

### 2. Sideløbende: mekanisme, ikke content

Byg **mekanisme, ikke content**. Grænsen er: kommer tallene fra scenariodata, eller står de i koden? Kun det første er forsvarligt før M3.

Kandidater, i prioriteret rækkefølge:

- **Skadesystem** — injury-tags påvirker hvilke handlinger der er tilgængelige og deres `Penalty`-led. Data siger hvilke tags og hvilken effekt; kode siger hvordan de anvendes.
- **Stormens forgreninger** — lejrstatus og tags ved stormens start vælger komplikationer. Samme mønster som `ScenarioOutcomeRules`.
- **Scenario-loader end-to-end** — fra JSON til en færdig `EffectTable` + regelsæt, med kontraktvalidering af det hele.

Byg **ikke**: Stormnatten-værdier, balancering, art, personalisering, Unity-scener. `docs/20` og R-004 forbyder det før gaterne, og R-004 har sandsynlighed **høj**.

### 3. Efter M0a — udført

Beslutningen blev `DROP_Q1_RUNTIME`. Eksekveret: ADR-004 superseded, ADR-018 resolved, ADR-019 accepted
(`docs/18`); `Q1_LEGACY` arkiveret (`docs/08` §3); Q1 fjernet fra device-matrix, release gates og
Definition of Done (`docs/13`); PO-004/PO-007/PO-098 droppet, 18 t frigjort fra P0, PO-025 reduceret til
Q2↔Q3 (`docs/17`); dokumentoprydning på tværs af repoet gennemført 2026-08-09.

Editor låst til Unity 6 LTS; Core flyttet til Unity-projektet; `config/COMPATIBILITY_MATRIX.md` udfyldes,
når to-klient-testen er kørt.

---

## Det skal du IKKE gøre

- Påstå at ukompileret Unity-/Fusion-kode virker.
- Generere scripts, der ikke kaldes af noget. Pseudofremdrift er eksplicit forbudt i `01_PROMPT_FOR_CLAUDE.md`.
- Ændre `Accepted`-ADR'er eller springe response matrix over.
- Vælge P1-scope selv (Q-004 er Anders').
- Skrive Stormnatten-værdier ind i kode.
- Efterlade tokens i filer, git-config eller output.
- Vente med commits til sessionens slutning.

## Kvalitetskrav pr. leverance

Afslut med: **hvad er ændret · hvad er verificeret (og hvordan) · hvad er IKKE verificeret · hvad mangler · risici · næste handling.**

Og den vigtigste vane fra denne kodebase: **hvis en test modsiger et dokument, har testen ret indtil det modsatte er bevist.** Det er sket tre gange — udfaldsformlen, coop-solverens hastighedsloft og en dobbelt-journalisering. Alle tre var usynlige ved gennemlæsning. Se `docs/33`.
