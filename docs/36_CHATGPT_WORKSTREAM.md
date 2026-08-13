# ChatGPT-workstream — PROJECT ØEN

**Ejer:** ChatGPT  
**Projektejer:** Anders  
**Opdateret:** 2026-08-13  
**Scope:** Alt uden for Unity jf. `AI_COLLABORATION_AGREEMENT.md`

## Formål

Denne fil er det løbende overblik over de ikke-Unity-opgaver, ChatGPT ejer, og den rækkefølge de udføres i.

Den overstyrer ikke source-of-truth-hierarkiet i `00_READ_ME_FIRST.md`. Unity/runtime/editor, XR/Fusion, builds, profiling og Unity-side QA tilhører Claude.

## Korrigeret arbejdsregel

Den tidligere version af denne workstream gjorde M-Pre til en for bred stoplinje. Det var forkert.

M-Pre skal blokere:

- M1 gameplay-production
- endelig validering af effort-marker-kernen
- designvalg der eksplicit kræver menneskedata
- balance/tuning som kun kan bevises i spil

M-Pre skal **ikke** blokere:

- source asset manifests
- audio cue design
- UX/copy/localization source
- human-QA pakker
- content coverage
- interaction briefs
- personalization contracts
- IP/provenance
- visual style
- information architecture
- event authoring
- after-action/replay design
- product telemetry
- gift/release product flow

Grundreglen er nu:

> **Forbered, specificér og gør produktionen eksekverbar nu. Vent kun med de beslutninger og den dyre produktion, som faktisk kræver gate-evidens.**

---

# Aktuel situation

## Gates

### Claude / Unity

**M0b** er ikke lukket cross-device. Tracker: GitHub issue #3.

### ChatGPT / produkt

**M-Pre** er klar, men ikke kørt med mennesker. Tracker: GitHub issue #7.

### Content contract

Tre konkrete content-konflikter er sporet i GitHub issue #8:

- intro contract
- Day 3 planning i data
- fire-start scope

Disse skal løses konsistent før den relevante M3/M6 implementation.

---

# Afsluttede non-Unity leverancer

## Foundation / proces

| ID | Leverance | Status |
|---|---|---|
| C-001 | M-Pre ready-to-run package | **Færdig** |
| C-002 | Status-/roadmapoprydning | **Færdig** |
| C-004 | Root/master/handoff guidance cleanup | **Færdig** |
| C-010 | OQ-008 randomness test protocol | **Færdig** |
| C-011 | OQ-009 role test protocol | **Færdig** |
| C-012 | OQ-010 after-action competition protocol | **Færdig** |

## Produktionsberedskab

| ID | Leverance | Fil | Status |
|---|---|---|---|
| N-001 | Comprehensive non-Unity gap audit | `docs/37_NON_UNITY_GAP_AUDIT.md` | **Færdig** |
| N-002 | Source asset manifest | `docs/38_SOURCE_ASSET_MANIFEST.md` | **Færdig v0.1** |
| N-003 | Audio cue manifest | `docs/39_AUDIO_CUE_MANIFEST.md` | **Færdig v0.1** |
| N-004 | UX/copy/localization catalog | `docs/40_UX_COPY_AND_LOCALIZATION_CATALOG.md` | **Færdig v0.1** |
| N-004b | Machine-readable Danish source copy | `content/localization/da.source.json` | **Færdig v0.1** |
| N-005 | Personalization package/privacy spec | `docs/41_PERSONALIZATION_PACKAGE_SPEC.md` | **Færdig v0.1** |
| N-006 | Human QA/playtest pack M1-M9 | `docs/42_HUMAN_QA_PLAYTEST_PACK.md` | **Færdig v0.1** |
| N-007 | IP/asset provenance workflow | `docs/43_IP_AND_ASSET_PROVENANCE.md` | **Færdig v0.1** |
| N-008 | Stormnatten content coverage matrix | `docs/44_CONTENT_COVERAGE_MATRIX.md` | **Færdig v0.1** |
| N-009 | Releasecritical interaction briefs | `design/interactions/` | **Færdig første pakke** |
| N-010 | Gift/release product flow | `docs/45_GIFT_EXPERIENCE_AND_RELEASE_FLOW.md` | **Færdig v0.1** |
| N-011 | Ten-event authoring catalog | `docs/46_STORMNATTEN_EVENT_CATALOG.md` | **Færdig v0.1** |
| N-012 | Visual style bible | `docs/47_VISUAL_STYLE_BIBLE.md` | **Færdig v0.1** |
| N-013 | UI/information architecture | `docs/48_UI_INFORMATION_ARCHITECTURE.md` | **Færdig v0.1** |
| N-014 | After-action/replay product spec | `docs/49_AFTER_ACTION_AND_REPLAY_SPEC.md` | **Færdig v0.1** |
| N-015 | Product telemetry & metrics | `docs/50_PRODUCT_TELEMETRY_AND_METRICS.md` | **Færdig v0.1** |

---

# Evidensarbejde der stadig afventer mennesker

## M-Pre / C-003

Krav:

- mindst 3 sessions
- mindst 2 forskellige par
- ikke gavemodtageren
- rå målinger efter `docs/35_M_PRE_GREYBOX_GATE.md`

Når data findes:

1. afgør `GRØNT` / `RØDT`
2. behandl OQ-006/OQ-007
3. opdatér backlog/status
4. åbner M1 kun hvis M0b også er grøn

## Design tests

- OQ-008 fairness/randomness
- OQ-009 role assignment
- OQ-010 after-action competition

Protokoller er klare; resultater må ikke opfindes.

---

# Aktive ChatGPT-opgaver — næste bølge

## N-016 — Backlog ownership/status overlay

Problem: `docs/17_BACKLOG_AND_MILESTONES.md` har historiske `Not Started`-statusser på arbejde der helt eller delvist er udført, og blander Claude-, ChatGPT- og human-work.

Leverance:

- map hver relevant backlogtype til `Claude`, `ChatGPT`, `Shared`, `Human evidence`
- markér dokumenteret pre-work/foundation uden at omskrive Excel-trackeren falsk
- gør det synligt hvor ChatGPT kan fortsætte uafhængigt

## N-017 — Content contract resolution support

GitHub issue #8.

ChatGPT skal forberede konkrete, scope-bevidste løsningsforslag for:

- intro flow contract
- Day 3 planning representation
- fire-start gift scope

Hvis en løsning ændrer 1.012 t-scope eller accepted beslutning, skal Anders godkende den.

## N-018 — Machine-readable content expansion

Uden at låse balance kan vi udvide:

- localization/source content
- event presentation contracts
- neutral fallback content
- authoring templates

Final event probabilities/numeric tuning venter på evidence.

## N-019 — Source production batching

Brug asset/audio manifests til at forberede konkrete batches:

1. A1 gameplay-readable source
2. A2 camp/storm source
3. A3 feedback/VFX source
4. B full-scenario source
5. P private personalization

## N-020 — Actual source asset/audio production

Kan begynde selektivt for gameplay-readable source assets, når outputtet ikke risikerer dyr rework.

Full environment polish/final audio pass venter på relevante greybox gates.

## N-021 — Narrative continuity pass

Sammenhold:

- scenario bible
- radio copy
- event catalog
- Day 1/2/3 information release
- epilogue

Mål: ingen lore/goal contradictions og ingen exposition der løser planlægningsproblemet for spillerne.

## N-022 — Neutral fallback asset/copy package

Personalization spec har kontrakten; der mangler stadig konkrete neutral source placeholders/assets og deres provenance.

## N-023 — Content authoring templates

Standard templates for:

- event
- interaction
- action card
- audio cue
- source asset handoff

så senere content ikke driver fra kontrakten.

---

# M1 product/UX handoff

`C-020` åbner som **implementeringshandoff** efter grøn M0b + M-Pre.

En stor del af materialet er allerede forberedt:

- visual style
- UI IA
- copy
- interaction briefs
- human QA
- metrics

Når gaten åbner, samles dette til en kompakt M1-pakke til Claude i stedet for at designe det fra nul.

---

# Arbejdsregel ved “kør videre”

1. læs `repo_status.md`
2. læs denne fil
3. kontroller seneste commits/issues/gates
4. tag højeste ublokerede ChatGPT-opgave
5. ændr ikke Unity-filer
6. lever konkrete source/product artifacts
7. vent kun når næste beslutning faktisk kræver human/device evidence
8. opdatér workstream/status ved reelle statusskift

## Nuværende situation

Der er **fortsat væsentligt non-Unity-arbejde**.

M-Pre og M0b blokerer M1-production, men de blokerer ikke ChatGPTs produktionsberedskab.

> **Bevis beslutninger der kræver evidens. Forbered resten så langt frem som det kan gøres uden at skabe rework.**
