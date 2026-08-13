# ChatGPT-workstream — PROJECT ØEN

**Ejer:** ChatGPT  
**Projektejer:** Anders  
**Dato:** 2026-08-13  
**Scope:** Alt uden for Unity jf. `AI_COLLABORATION_AGREEMENT.md`

## Formål

Denne fil er det løbende overblik over de ikke-Unity-opgaver, der mangler på PROJECT ØEN, og den rækkefølge ChatGPT arbejder dem i.

Den må ikke bruges til at overstyre produkt- eller tekniske beslutninger i `00_READ_ME_FIRST.md`. Unity-implementering, C#, XR, Fusion, builds og Unity-side QA tilhører Claude.

---

## Aktuel situation

### Verificeret / allerede på plads

- Kritisk Claude-review er behandlet; alle 10 reviewfund er lukket.
- Baseline er v2.1.
- Quest 1-runtime er droppet (`DROP_Q1_RUNTIME`).
- Quest 2 er performancegulv; Quest 3/3S er enhanced parity.
- P1-scope til gaveversionen er valgt.
- M-Pre er accepteret som gate via ADR-022.
- Release 1 er fastlagt til M5 via ADR-023.
- Art/audio/UI-retningen findes i `docs/11_ART_AUDIO_UI_DIRECTION.md`.
- Stormnatten og kerne-gameplay er beskrevet i eksisterende design- og contentdokumenter.
- M0b er de-risket per klient; de resterende M0b-beviser kræver to headset og tilhører Claude/Anders-sporet.

### Det vigtigste, der mangler nu

1. **M-Pre er ikke kørt.** Kernehypotesen om fire indsatsmarkører er derfor stadig ikke bevist med mennesker.
2. **M-Pre-materialet er ikke pakket som en konkret testpakke.** `docs/35` beskriver testen, men facilitatoren skal stadig omsætte den til kort, ark og standardiseret instruktion.
3. **Statusdokumenter er delvist forældede.** `docs/29_NEXT_ACTION.md` peger stadig på det gamle Claude-reviewflow, og `repo_status.md` indeholder en ældre “ukompileret Fusion-binding”-linje, der ikke længere matcher de dokumenterede M0b-resultater.
4. **Roadmappets estimatafsnit er delvist gammelt.** P1-scope er valgt til 1.012 timer i gaveversionen, mens et ældre afsnit stadig beskriver P1 som `TBD`.
5. **OQ-008, OQ-009 og OQ-010 mangler testdesign/resultat.** De blokerer ikke M0-M2, men skal behandles systematisk senere.
6. **Endelige art/audio/source-assets skal ikke masseproduceres endnu.** Projektets egne gates forbyder dyr art/content før kerne- og greyboxbeviser er grønne.
7. **Senere produktejerinput er stadig åbent:** same-room vs remote-first, finalens tone, neutral/personlig karakterisering, standardsværhedsgrad og launch-sprog.

---

# Prioriteret plan

## P0 — nu

### C-001 — Gør M-Pre kørbar

**Mål:** Anders skal kunne gennemføre testen uden at designe forsøget på ny.

Leverancer under `prototype/m-pre/`:

- `README.md` — komplet runbook
- `FACILITATOR_SCRIPT.md` — standardiseret intro og regler
- `TASK_CARDS.md` — seks print-/kopiklar opgavekort
- `SESSION_SHEET.md` — status, dagslog og målinger
- `RESULT_TEMPLATE.md` — rå resultatopsamling og gateberegning

**Færdig når:** materialet kan bruges direkte sammen med fire ens markører og én d6.

### C-002 — Ryd statusdokumenter op

Opdatér:

- `docs/29_NEXT_ACTION.md`
- `repo_status.md`
- den forældede estimat/statussektion i `docs/12_PRODUCTION_ROADMAP.md`

Ingen Unity-status må opfindes; kun dokumenterede resultater må skrives ind.

### C-003 — Afvent selve M-Pre-playtesten

Selve gaten kræver mindst tre menneskelige sessioner med mindst to forskellige par og kan derfor ikke “simuleres grøn” af en AI.

Når rådata kommer tilbage:

- udfyld §10 i `docs/35_M_PRE_GREYBOX_GATE.md`
- afgør gaten efter de eksisterende tærskler
- luk eller behold OQ-006/OQ-007
- opdatér roadmap/backlog med faktisk resultat

---

## P1 — mens M-Pre afventer testere

### C-010 — Design test for randomness (OQ-008)

Lav en lille A/B-test, der måler om randomness opleves som fair uden at balancere Stormnatten endeligt.

Krav:

- samme beslutning under mindst to udfaldsmodeller
- registrér oplevet agency, fairness og forståelse
- ingen permanente contenttal før M3/M4-gates

### C-011 — Rolletest (OQ-009)

Forbered to testvarianter:

- spillerne vælger roller
- roller fordeles/skifter automatisk

Mål om valget skaber strategi eller bare præference/administration.

### C-012 — Efterspils-konkurrence (OQ-010)

Design neutral testvariant med og uden individuel score/ambition. Ingen beslutning træffes, før målbrugerne kan testes uden at afsløre gaveoplevelsen.

---

## P2 — efter grøn M-Pre

### C-020 — M1 produkt-/UX-handoff til Claude

ChatGPT specificerer:

- ønsket player experience for locomotion, grab, snap og tohåndsobjekter
- comfort-krav
- seated/standing-adfærd
- feedback- og haptics-intention
- acceptance criteria set fra spillerens perspektiv

Claude vælger og implementerer Unity-løsningen.

### C-021 — Source asset manifest

Opret den autoritative liste over nødvendige source-assets med:

- ID og navn
- kategori
- gameplayfunktion
- visuel retning
- ønsket format/opløsning
- LOD-/variantbehov på designniveau
- milepæl
- status
- Unity-handoff-felt

**Vigtigt:** manifest først; dyr masseproduktion af art sker først, når den relevante gate tillader det.

### C-022 — Audio cue manifest

Opret systematisk katalog for ambience, feedback, storm, shelter/fire, UI og finale med prioritet og fallback. Unity-implementeringen tilhører Claude.

---

## P3 — senere produktbeslutninger

Følgende træffes ved den milepæl, hvor de faktisk får betydning:

- same-room eller remote-first som primær oplevelse
- personlig finales tone
- neutrale vs personligt baserede karakterer
- standardsværhedsgrad
- dansk-only vs dansk+engelsk launch

De må ikke blokere M0-M2.

---

# Arbejdsregel ved nye opgaver

Når Anders beder ChatGPT “køre videre” på Øen:

1. læs `repo_status.md`
2. læs denne fil
3. kontroller seneste commits/status før ændringer
4. tag højeste ublokerede ChatGPT-opgave
5. ændr ikke Unity-filer
6. lav konkrete leverancer frem for ren planlægning
7. opdatér denne workstream, når en opgave skifter status

---

# Aktuel kø

| ID | Opgave | Status | Blokering |
|---|---|---|---|
| C-001 | M-Pre ready-to-run-pakke | **I gang** | Ingen |
| C-002 | Status-/roadmapoprydning | **I gang** | Ingen |
| C-003 | Kør M-Pre med mennesker | Afventer | 3 testsessioner |
| C-010 | OQ-008 randomness-testdesign | Næste | Ingen |
| C-011 | OQ-009 rolletestdesign | Planlagt | M-Pre-data hjælper |
| C-012 | OQ-010 after-action competition test | Planlagt | Målbrugere senere |
| C-020 | M1 produkt/UX-handoff | Planlagt | Grøn M-Pre |
| C-021 | Source asset manifest | Planlagt | Grøn relevant gate |
| C-022 | Audio cue manifest | Planlagt | Grøn relevant gate |

## Hovedprincip

> **Bevis spillets beslutninger før vi polerer dem.**

ChatGPTs opgave er ikke at fylde repoet med flere planer. Opgaven er at lukke den næste produktmæssige usikkerhed, levere det materiale Claude har brug for, og holde Unity-arbejdet fri for uklare krav.
