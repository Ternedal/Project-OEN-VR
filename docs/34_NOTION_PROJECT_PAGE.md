# Notion-side: Projekt Øen VR — klar til indsættelse

Skrivningen til Notion blev afvist to gange med **"No approval received"**. Læsning virker (jeg hentede databasens skema uden problemer), så det er skriveadgangen, der mangler godkendelse — sandsynligvis en connector-prompt, der skal accepteres i appen.

Nedenfor er alt, klar til copy/paste. Opret siden i **ProjectRig HQ → Projekter**.

---

## Felter

| Felt | Værdi |
|---|---|
| **Projekt** (titel) | `Projekt Øen VR / Strandet Sammen` |
| **Status** | `Udvikling` |
| **Prioritet** | `P2 Normal` |
| **Type** | `VR` |
| **Tech stack** | `Unity`, `Claude` |
| **Version** | `2.1 (review behandlet) · Core 146 tests grønne` |
| **Repo** | `https://github.com/Ternedal/Project-OEN-VR` |
| **Projekt ID** | *rør ikke — auto_increment* |
| **Handoff ZIP** | *tom — ingen zip leveret endnu* |

### Næste handling

```
M0b: Unity-projektet er oprettet, Fusion-sessionen kører on-device, og co-op-kassen spawner.
Naeste gate er privat session mellem to klienter med head/hands-replikation og 10x loeftetest
uden permanent desync (Q2<->Q3). M0a er afgjort: DROP_Q1_RUNTIME. P1-scope er valgt
(gaveversion = 997 t). Udestaar: M0-issuet skal oprettes manuelt fra docs/30
(tokenet mangler issues-scope).
```

---

## Sideindhold

# Kort beskrivelse

To-spiller kooperativt VR-overlevelsesspil til Meta Quest. Original IP, tænkt som en personlig gaveoplevelse: to spillere fordeler fire indsatsmarkører ved daggry, udfører opgaverne fysisk i VR, og opdager under en afsluttende storm om prioriteringerne holdt. Første scenario er **Stormnatten** — tre døgn, 30-45 minutter.

Quest 2 er performancegulv, Quest 3/3S enhanced parity. Quest 1-lanen er droppet 2026-08-08 (`DROP_Q1_RUNTIME`) — Q1 er højst en frossen sideload-demo.

# Aktuel status

**Baseline v2.1.** Design-, arkitektur- og produktionsgrundlaget er komplet (33 dokumenter, JSON-skemaer, backlog med 107 aktive items (3 droppet med `DROP_Q1_RUNTIME`)).

Kritisk review gennemført 2026-08-06: verdict `PROCEED_WITH_BLOCKERS`, 2 BLOCKER, 5 HIGH, 3 MEDIUM, 6 dokumentkonflikter. Ændringspakken er merget til `main`. Alle 10 fund er lukket (CR-002 lukket af M0a 2026-08-08, CR-005 af P1-scopevalget samme dag).

**Unity-projektet er oprettet** (`ProjektOenApp`, Unity 6000.4.10f1 + OpenXR + Fusion 2.0.12), og M0b-bindingen kompilerer og kører on-device. Derudover findes hele det lag, der kan verificeres uden headset: `src/ProjectOen.Core` er ren C# (netstandard2.1, ingen UnityEngine-referencer) med **146 tests grønne**, som kører i CI på hvert push.

Alt netværks- og Unity-specifikt ligger i `src/unity/` som **ukompilerede** kildefiler med `UNVERIFIED-IN-SANDBOX`-header og konkrete API-antagelser pr. fil.

# Reviewets to blockers

- **CR-001 (lukket):** M0's gate krævede netværksbevis, men alle Photon-opgaver lå i M2. Seks items flyttet til M0, der nu er 176 t / 19 items. Stop/go flyttet fra et 250-timers loft til M0's afslutning.
- **CR-002 (lukket 2026-08-08):** Quest 1-lanen var reelt et andet XR-backend. M0a afgjorde det på hardware: Unitys OpenXR-provider crasher (SIGABRT) på Q1's v50-runtime. Lanen er droppet — ADR-004 superseded, ADR-019 accepted.

# Verificerede platformfakta

- Unity 2022.3 LTS er uden patchsupport på Personal/Pro — Unity giver to år, tredje år er Enterprise/Industry. Editorvalget er derfor gjort M0-afhængigt med Unity 6 LTS som foretrukken kandidat.
- Quest 2: udgik af salg ultimo 2024, feature-opdateringer til dec. 2026, kritiske til dec. 2027. Bevaret som performancegulv; Quest 3S er antaget baseline efter v1.0.
- Quest 1: sidste OS-udgivelse v50 (feb. 2023), sikkerhedsopdateringer sluttede aug. 2024, butikken lukket. Sideload er ikke blokeret.
- Photon Fusion: 100 CCU gratis dækker udvikling og kommerciel brug for én app. Omkostning for to spillere: 0 kr.

# To målinger der modsagde dokumenterne

Begge fejl var usynlige ved gennemlæsning og åbenlyse ved måling. Det er argumentet for, at Core-laget er testbart uden headset. Skrevet op i `docs/33`.

- **Udfaldsformlen:** reviewet anbefalede at skære fra otte til fire led. Målingen (20 runs × 12 handlinger) viste, at fire led klumpede *marginalt værre* — 70,0 % mod 68,8 % i én kategori. Årsagen var ikke antallet af led, men at modstand blev trukket fra med fuld vægt fra en score, hvis positive led summerer til 1,0. Rettet med begrænset modstandsvægt og en gulv-regel: modstand kan højst trække udfaldet ét trin ned fra det, præstationen fortjente. Største enkelt-tier nu 47,5 %.
- **Coop-solveren:** testen der skulle bekræfte, at den tunge kasse er langsommere med én hånd end med to, fejlede. Hastighedsloftet var identisk i begge tilstande, så ud over få centimeter klippede det begge til samme skridt. Hele coop-præmissen ville kun kunne mærkes tæt på målet.

# Estimat

Det tidligere tal på 500-810 timer var top-down og kunne ikke spores til backloggen (M3 stod til 55-85 t mod 260 t i de faktiske items). Det er trukket tilbage.

| Model | Sum |
|---|---|
| Aktiv backlog (107 items) | 1.436 t |
| Gaveversion (76 items: P0 616 + P1 381) | **997 t** |
| Udskudt til efter v1.0 (31 items) | 439 t |
| Droppet med `DROP_Q1_RUNTIME` | 28 t (PO-004, PO-007, PO-098) |

Gaveestimatet er 997 t. Ved 15 t/uge lander det omkring årsskiftet 2027/28.

# Roadmap

## Afsluttet — M0a (2026-08-08)

OpenXR-smoketest kørt on-device. Quest 2 grøn (71,8 fps, Vulkan, head-tracking valid); Quest 1 native SIGABRT i `libopenxr_loader.so`. Resultat: `DROP_Q1_RUNTIME` med logcat- og tombstone-evidens i `prototype/m0a-openxr-smoke/RESULTAT.md`.

## Leveret parallelt (uden hardware)

Core-laget: typed IDs, kanonisk JSON, save-checksum, atomisk skrivning, scenario-kontrakt, fasemaskine med idempotens, delayed events, udfaldsformel, coop-solver, compatibility handshake, join code, deltagelsesmåling, efterspilsrapport, fuld save round-trip og data-drevet win/lose. 146 tests, CI-kørt.

## Næste — M0b

Unity-projekt oprettes, editor og pakker låses, Photon-session, handshake, head/hands-replication, CoopObjectController, 10× cross-device løftetest. Accept: Q2↔Q3 uden permanent desync, 72 Hz i minimal scene.

## Senere — M1 til M9

Interaktionsfundament, multiplayer-hardening, én-dags greybox, konsekvenskæder, storm vertical slice, fuldt Stormnatten-content, art pass, personalisering, release candidate.

## Ikke nu

Open world, procedural ø, permanent base, håndtracking, mixed reality, offentlig matchmaking, mere end to spillere.

# Risici

- **Scope er nu valgt, men ikke bevist.** Gaveversionen er sat til 997 t; ved 15 t/uge er det 15-16 måneder. Estimatet er kun så godt som backloggens itemvurderinger.

**Lukkede risici:** Quest 1-lanen (lukket 2026-08-08). Risikoen indtraf: Q1 kan ikke køre OpenXR. Exit-planen var skrevet på forhånd, så beslutningen kostede ét eksperiment i stedet for en fork af interaktionslaget.
- **Content før core er sjov** (R-004, sandsynlighed høj). Videre gameplay-mekanik ud over det byggede ville være spekulativt før M0 og M3.
- **Fusion-koden er ukompileret.** Alt i `src/unity/` er påstand indtil den kører på Windows.

# Næste handling

Kør M0a efter `prototype/m0a-openxr-smoke/RUNBOOK.md` og meld resultatet. Vælg derefter P1-scope.
