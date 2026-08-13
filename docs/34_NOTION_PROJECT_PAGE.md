# Notion-side: Projekt Øen VR — aktuel kildetekst

> **Opdateret 2026-08-13.** Notion-projektsiden blev oprettet 2026-08-08. Denne fil er nu kildetekst til fremtidig ajourføring — ikke en instruktion om at oprette siden igen.

Repoet er source of truth. Ved konflikt gælder `00_READ_ME_FIRST.md`, `repo_status.md` og de relevante source-of-truth-dokumenter før denne Notion-tekst.

---

## Felter

| Felt | Værdi |
|---|---|
| **Projekt** | `Projekt Øen VR / Strandet Sammen` |
| **Status** | `Udvikling` |
| **Prioritet** | `P2 Normal` |
| **Type** | `VR` |
| **Tech stack** | `Unity 6 LTS`, `OpenXR`, `Photon Fusion`, `Claude`, `ChatGPT` |
| **Version** | `Baseline v2.1 · Core 146 tests grønne · M0a lukket · M0b i gang` |
| **Repo** | `https://github.com/Ternedal/Project-OEN-VR` |

### Næste handling

```text
To parallelle gates:

1. Claude/Unity-sporet lukker M0b cross-device:
   head/hands-replikering, handshake mismatch, delt coop-kasse, 10x Q2↔Q3-løft,
   72 Hz-måling og standby/reconnect-evidens.

2. ChatGPT/produkt-sporet har gjort M-Pre klar under prototype/m-pre/.
   M-Pre skal køres som 3 menneskelige testsessioner med mindst 2 forskellige par.

M1 starter først, når både M0b og M-Pre er grønne.
```

---

# Kort beskrivelse

**PROJECT ØEN — STRANDET SAMMEN** er et originalt, to-spiller kooperativt VR-overlevelsesspil til Meta Quest.

Spillerne har for få ressourcer og for lidt tid. De fordeler fire indsatsmarkører, udfører korte fysiske samarbejdsopgaver og oplever senere konsekvenserne af deres prioriteringer. Første scenario er **Stormnatten**.

Produktretning:

- Quest 2 = performance- og kvalitetsgulv.
- Quest 3/3S = enhanced parity med samme gameplay.
- Quest 1 = udgået runtime/testlane (`DROP_Q1_RUNTIME`).
- MVP/gaveversion = præcis to spillere.
- Release 1 = M5 storm vertical slice (ADR-023).

---

# Aktuel status

## Produkt og plan

- Kritisk Claude-review er gennemført og behandlet.
- Alle 10 oprindelige reviewfund er lukket.
- Baseline er v2.1.
- P1-scope er valgt.
- Gaveversionens aktive scope er **1.012 timer** over 77 items.
- M-Pre er accepteret som særskilt produktgate via ADR-022.
- ChatGPT/Claude-arbejdsdelingen er dokumenteret i `AI_COLLABORATION_AGREEMENT.md`.

## Core

`src/ProjectOen.Core` er ren C# uden UnityEngine-afhængighed og har **146 grønne tests**, som køres i CI.

Det dokumenterede Core-fundament omfatter blandt andet:

- typed IDs
- scenario contract/loader
- command/event-model og fasemaskine
- save/checksum/atomic write/snapshot
- delayed consequences
- udfaldsmodel
- coop-solver
- compatibility handshake
- join codes
- participation measurement
- after-action causal report

## M0a — afsluttet 2026-08-08

Hardwaretesten af OpenXR-lanen er gennemført.

- Quest 2: immersiv OpenXR, Vulkan, head tracking, ca. 72 Hz i smoketest.
- Quest 1: deterministisk crash under OpenXR-init.

Beslutning: **`DROP_Q1_RUNTIME`**.

Quest 1 er højst en frossen sideload-demo og må ikke påvirke hovedprojektets arkitektur eller gates.

## M0b — per-klient bevist, cross-device mangler

Dokumenteret on-device:

- Unity `6000.4.10f1`
- OpenXR
- Photon Fusion `2.0.12`
- Photon Shared-session forbinder
- NetworkPlayerRig spawner med authority
- levende head pose via `InputDevices`
- coop solver/greb→kasse-kæde kører på device

Resterende gate kræver to headset:

1. remote head/hands replication
2. handshake mismatch-afvisning
3. delt coop-object i to-spiller-state
4. 10× Q2↔Q3-løft uden permanent desync
5. 72 Hz i minimal netværksscene
6. standby/reconnect-måling
7. opdateret compatibility matrix med faktiske resultater

Dette er Claude/Unity-sporet.

## M-Pre — klar til mennesketest

M-Pre tester projektets vigtigste designhypotese før M1:

> Skaber fordelingen af fire indsatsmarkører reel diskussion og prioritering mellem to spillere — eller bare administration?

Ready-to-run-materialet ligger i `prototype/m-pre/` og indeholder:

- runbook
- facilitator-script
- task cards
- session sheet
- result template

Gaten kræver mindst tre sessions med mindst to forskellige par. Gavemodtageren må ikke bruges som tester.

Dette er ChatGPT/produkt-sporet sammen med Anders.

---

# Åbne designspørgsmål

Tre ikke-blokerende spørgsmål har nu konkrete protokoller under `prototype/design-tests/`:

- **OQ-008:** hvor meget randomness føles fair?
- **OQ-009:** skal spillerroller vælges eller rotere automatisk?
- **OQ-010:** hjælper individuel efterspils-feedback oplevelsen eller skaber den uønsket konkurrence?

De må ikke lukkes på AI-vurdering alene; de afventer menneskedata.

---

# Estimat

| Model | Sum |
|---|---:|
| Aktiv backlog | 1.451 t |
| Gaveversion — 77 items | **1.012 t** |
| Udskudt til efter v1.0 | 439 t |
| Droppet med `DROP_Q1_RUNTIME` | 28 t |

Ved ca. 15 timer/uge svarer 1.012 timer groft til 15-16 måneders arbejde. Det er et backlog-estimat, ikke et kalenderløfte.

---

# Roadmap — gate-baseret

1. **M0** — platform + netværksfeasibility
2. **M-Pre** — kernehypotese uden VR
3. **M1** — interaction foundation
4. **M2** — multiplayer hardening
5. **M3** — one-day prototype
6. **M4** — delayed consequences
7. **M5** — storm vertical slice / **Release 1**
8. **M6** — fuld Stormnatten
9. **M7** — art/audio pass
10. **M8** — personalisering/gaveleverance
11. **M9** — release candidate/QA

M1 må først begynde efter grøn **M0b + M-Pre**.

---

# Arbejdsdeling

## Claude

- Unity
- C#/runtime/editor-kode
- XR/OpenXR/Fusion
- scenes/prefabs
- Unity asset/audio integration
- builds
- profiling/performance
- Unity-side QA

## ChatGPT

- produkt og gameplay-design
- specs og roadmap
- source-assets og art direction
- audio-design/source-materiale
- playtestprotokoller
- ekstern arkitektur
- produkt-QA
- handoff til Claude

Anders har sidste ord.

---

# Risici lige nu

- **M0b cross-device er endnu ikke bevist.** Per-client success er ikke det samme som stabil to-player networking.
- **M-Pre er endnu ikke kørt.** Kerneloopets samarbejdspræmis er derfor stadig en hypotese.
- **Scope er stort.** 1.012 t kræver disciplineret scope ladder og gate-baseret udvikling.
- **Content/art før bevis** er fortsat en høj risiko; dyr masseproduktion skal vente til de relevante gates.

---

# Næste statusopdatering

Opdatér denne fil/Notion, når mindst ét af følgende sker:

- M0b bliver `GO` eller `REDESIGN`
- M-Pre bliver `GRØNT` eller `RØDT`
- gave-scope ændres
- en ny milestone åbnes/lukkes
- en større produktbeslutning accepteres i decision log
