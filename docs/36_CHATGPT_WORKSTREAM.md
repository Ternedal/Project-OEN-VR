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
- P1-scope til gaveversionen er valgt: 1.012 t.
- M-Pre er accepteret som gate via ADR-022.
- Release 1 er fastlagt til M5 via ADR-023.
- Art/audio/UI-retningen findes i `docs/11_ART_AUDIO_UI_DIRECTION.md`.
- Stormnatten og kerne-gameplay er beskrevet i eksisterende design- og contentdokumenter.
- M0b er de-risket per klient; de resterende M0b-beviser kræver to headset og tilhører Claude/Anders-sporet.
- M-Pre ready-to-run-pakken er oprettet under `prototype/m-pre/`.
- De centrale statusdokumenter er ajourført til det aktuelle M0/M-Pre-flow.
- GitHub issue #3 er ajourført fra gammel Q1/2/3-scope til den aktuelle Q2/Q3-M0b-gate.
- OQ-008, OQ-009 og OQ-010 har nu konkrete testprotokoller under `prototype/design-tests/`.
- `docs/19_OPEN_QUESTIONS.md` peger nu på de konkrete protokoller uden at foregive, at spørgsmålene er besvaret.

### Det vigtigste, der mangler nu

1. **M-Pre er ikke kørt.** Kernehypotesen om fire indsatsmarkører er derfor stadig ikke bevist med mennesker.
2. **M0b er ikke lukket cross-device.** Det er Claude/Anders-sporet og kræver to headset.
3. **OQ-008, OQ-009 og OQ-010 mangler menneskedata.** Testdesignene er klare; resultater må ikke erstattes af AI-vurdering.
4. **OQ-007 kan kun delvist besvares af M-Pre.** M-Pre kan vise naturlig arbejdsdeling, men tester ikke eksplicitte asymmetriske roller; OQ-009-data skal indgå.
5. **Endelige art/audio/source-assets skal ikke masseproduceres endnu.** Projektets egne gates forbyder dyr art/content før kerne- og greyboxbeviser er grønne.
6. **Senere produktejerinput er stadig åbent:** same-room vs remote-first, finalens tone, neutral/personlig karakterisering, standardsværhedsgrad og launch-sprog.

---

# Prioriteret plan

## P0 — nu

### C-001 — Gør M-Pre kørbar — FÆRDIG

Ready-to-run-pakken ligger under `prototype/m-pre/`:

- `README.md`
- `FACILITATOR_SCRIPT.md`
- `TASK_CARDS.md`
- `SESSION_SHEET.md`
- `RESULT_TEMPLATE.md`

Materialet kan bruges direkte med fire ens markører og én d6.

### C-002 — Ryd statusdokumenter op — FÆRDIG

Opdateret:

- `docs/29_NEXT_ACTION.md`
- `repo_status.md`
- `docs/12_PRODUCTION_ROADMAP.md`
- GitHub issue #3

Kun dokumenterede Unity-resultater er skrevet ind.

### C-003 — Kør selve M-Pre-playtesten — AFVENTER MENNESKER

Selve gaten kræver mindst tre menneskelige sessioner med mindst to forskellige par og kan ikke “simuleres grøn” af en AI.

Når rådata kommer tilbage:

- udfyld §10 i `docs/35_M_PRE_GREYBOX_GATE.md`
- afgør gaten efter de eksisterende tærskler
- behandl OQ-006/OQ-007 med den faktiske evidens
- opdatér roadmap/backlog med faktisk resultat

---

## P1 — designforsøg klar, afventer mennesker

### C-010 — Randomness (OQ-008) — PROTOKOL FÆRDIG

`prototype/design-tests/OQ-008_RANDOMNESS_FAIRNESS.md`

Sammenligner 1/6 og 1/3 komplikationsrisiko med samme fremdrift/omkostning og måler fairness, agency, spænding, frustration og forståelse.

### C-011 — Rolletest (OQ-009) — PROTOKOL FÆRDIG

`prototype/design-tests/OQ-009_ROLE_ASSIGNMENT.md`

Sammenligner selvvalgte/faste roller med automatisk rotation. Midlertidige rolleeffekter er eksplicit prototype-data, ikke canon.

### C-012 — Efterspils-konkurrence (OQ-010) — PROTOKOL FÆRDIG

`prototype/design-tests/OQ-010_AFTER_ACTION_COMPETITION.md`

Sammenligner rent fælles efterspil med fælles efterspil plus ikke-hierarkiske individuelle titler. Testen måler især fællesskab, replaylyst og sammenligningspres.

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
| C-001 | M-Pre ready-to-run-pakke | **Færdig** | — |
| C-002 | Status-/roadmapoprydning | **Færdig** | — |
| C-003 | Kør M-Pre med mennesker | **Afventer** | 3 testsessioner |
| C-010 | OQ-008 randomness-testdesign | **Færdig** | Resultat afventer mennesker |
| C-011 | OQ-009 rolletestdesign | **Færdig** | Resultat afventer M-Pre/roller + mennesker |
| C-012 | OQ-010 after-action competition test | **Færdig** | Resultat afventer målbrugere |
| C-020 | M1 produkt/UX-handoff | Planlagt | Grøn M-Pre |
| C-021 | Source asset manifest | Planlagt | Grøn relevant gate |
| C-022 | Audio cue manifest | Planlagt | Grøn relevant gate |

## Nuværende stoplinje

Der er nu ingen højprioriteret ikke-Unity-designbeslutning, som bør “løses på skrift” uden menneskedata.

Det rigtige næste skridt er derfor ikke mere spekulativ contentproduktion. Det er:

- Claude afslutter M0b's cross-device-bevis i Unity-sporet.
- M-Pre køres med mennesker i produktsporet.
- OQ-008/OQ-009/OQ-010 køres, når deres testforudsætninger er til stede.

Når M-Pre er grøn, åbner C-020 og derefter de relevante source asset/audio-manifests.

## Hovedprincip

> **Bevis spillets beslutninger før vi polerer dem.**

ChatGPTs opgave er ikke at fylde repoet med flere planer. Opgaven er at lukke den næste produktmæssige usikkerhed, levere det materiale Claude har brug for, og holde Unity-arbejdet fri for uklare krav.
