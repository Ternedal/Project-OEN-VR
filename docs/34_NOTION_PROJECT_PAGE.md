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
| **Version** | `2.1 (review behandlet) · Core 98 tests grønne` |
| **Repo** | `https://github.com/Ternedal/Project-OEN-VR` |
| **Projekt ID** | *rør ikke — auto_increment* |
| **Handoff ZIP** | *tom — ingen zip leveret endnu* |

### Næste handling

```
M0a på hardware — ét spørgsmål: starter og tracker Unitys OpenXR-provider fysisk på Quest 1?
Alt andet i M0 venter på svaret. Runbook, drop-in kildefiler og resultatskema ligger klar i
prototype/m0a-openxr-smoke/ på branchen agent/m0-platform-feasibility. Kør på Quest 2 FØRST,
så en fejl kan isoleres til opsætning vs. Quest 1, derefter Quest 1. Meld GO / REDESIGN /
DROP_Q1_RUNTIME i RESULTAT.md. Udestår desuden: Q-004 — hvilke af de 56 P1-items
(Gaveversion = TBD) er med i gaveversionen; indtil da findes der ikke et forsvarligt samlet
estimat. Og M0-issuet skal oprettes manuelt fra docs/30 (tokenet mangler issues-scope).
```

---

## Sideindhold

# Kort beskrivelse

To-spiller kooperativt VR-overlevelsesspil til Meta Quest. Original IP, tænkt som en personlig gaveoplevelse: to spillere fordeler fire indsatsmarkører ved daggry, udfører opgaverne fysisk i VR, og opdager under en afsluttende storm om prioriteringerne holdt. Første scenario er **Stormnatten** — tre døgn, 30-45 minutter.

Quest 2 er performancegulv, Quest 3/3S enhanced parity. Quest 1-lanen er under afgørelse.

# Aktuel status

**Baseline v2.1.** Design-, arkitektur- og produktionsgrundlaget er komplet (33 dokumenter, JSON-skemaer, backlog med 110 items).

Kritisk review gennemført 2026-08-06: verdict `PROCEED_WITH_BLOCKERS`, 2 BLOCKER, 5 HIGH, 3 MEDIUM, 6 dokumentkonflikter. Ændringspakken er merget til `main`. 8 af 10 fund er lukket — de sidste to kan kun lukkes af Anders.

**Der findes endnu intet Unity-projekt.** Til gengæld findes hele det lag, der kan verificeres uden headset: `src/ProjectOen.Core` er ren C# (netstandard2.1, ingen UnityEngine-referencer) med **98 tests grønne**, som nu også kører i CI på hvert push.

Alt netværks- og Unity-specifikt ligger i `src/unity/` som **ukompilerede** kildefiler med `UNVERIFIED-IN-SANDBOX`-header og konkrete API-antagelser pr. fil.

# Reviewets to blockers

- **CR-001 (lukket):** M0's gate krævede netværksbevis, men alle Photon-opgaver lå i M2. Seks items flyttet til M0, der nu er 176 t / 19 items. Stop/go flyttet fra et 250-timers loft til M0's afslutning.
- **CR-002 (åben — kræver hardware):** Quest 1-lanen blev beskrevet som en pakkeversionsforskel. Den er reelt et andet XR-backend: Q1 kræver Oculus-provider v3.x, som Meta har markeret deprecated og planlagt fjernet, mens Q2/Q3 kører OpenXR. Afgøres af ét fysisk eksperiment (ADR-019).

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
| Backlog i alt (110 items) | 1.473 t |
| `Gaveversion = In` (45 P0-items) | 634 t |
| `Gaveversion = TBD` (56 P1-items) | 712 t |
| `Gaveversion = Defer` (9 P2-items) | 127 t |

Der findes ikke et forsvarligt gaveestimat, før P1-udvælgelsen er foretaget. Ingen deadline er registreret nogen steder; med 15 t/uge fra august 2026 lander gaveversionen tidligst medio 2027.

# Roadmap

## Nu — M0a (blokeret på hardware)

OpenXR-smoketest på Quest 1. Runbook, drop-in kildefiler og resultatskema ligger i `prototype/m0a-openxr-smoke/`. Accept: appen starter immersivt og hovedtracking virker — eller `DROP_Q1_RUNTIME` meldes med logcat-evidens.

## Leveret parallelt (uden hardware)

Core-laget: typed IDs, kanonisk JSON, save-checksum, atomisk skrivning, scenario-kontrakt, fasemaskine med idempotens, delayed events, udfaldsformel, coop-solver, compatibility handshake, join code, deltagelsesmåling, efterspilsrapport, fuld save round-trip og data-drevet win/lose. 98 tests, CI-kørt.

## Næste — M0b

Unity-projekt oprettes, editor og pakker låses, Photon-session, handshake, head/hands-replication, CoopObjectController, 10× cross-device løftetest. Accept: Q1↔Q2 og Q2↔Q3 uden permanent desync, 72 Hz i minimal scene.

## Senere — M1 til M9

Interaktionsfundament, multiplayer-hardening, én-dags greybox, konsekvenskæder, storm vertical slice, fuldt Stormnatten-content, art pass, personalisering, release candidate.

## Ikke nu

Open world, procedural ø, permanent base, håndtracking, mixed reality, offentlig matchmaking, mere end to spillere.

# Risici

- **Quest 1-lanen kan kræve en fork af interaktionslaget** frem for en pakkeprofil. Mitigation: afgøres af ét eksperiment før alt andet; exit-planen er skrevet på forhånd, så et nej er en beslutning og ikke et nederlag.
- **P1-scope er ikke valgt.** 712 timer står som `TBD`. Uden udvælgelsen kan hverken tid eller færdiggørelse estimeres.
- **Content før core er sjov** (R-004, sandsynlighed høj). Videre gameplay-mekanik ud over det byggede ville være spekulativt før M0 og M3.
- **Fusion-koden er ukompileret.** Alt i `src/unity/` er påstand indtil den kører på Windows.

# Næste handling

Kør M0a efter `prototype/m0a-openxr-smoke/RUNBOOK.md` og meld resultatet. Vælg derefter P1-scope.
