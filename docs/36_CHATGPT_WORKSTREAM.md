# ChatGPT-workstream — PROJECT ØEN

**Ejer:** ChatGPT  
**Projektejer:** Anders  
**Opdateret:** 2026-08-13  
**Scope:** Alt uden for Unity jf. `AI_COLLABORATION_AGREEMENT.md`

## Arbejdsregel

M0b + M-Pre blokerer **M1-implementation**, men ikke ChatGPTs non-Unity-produktionsspor.

Human/device evidence blokerer kun de beslutninger, balancevalg og acceptance gates, som faktisk kræver den evidens.

ChatGPT fortsætter derfor med:

- content/source authoring
- art/audio source production
- UX/copy/localization
- QA og metrics
- personalization/fallback
- provenance
- interaction/product handoffs
- narrative og release flow

uden at ændre Unity-runtime eller foregive, at human/device gates er grønne.

---

# Aktuelle gates

## Claude / Unity — M0b

Tracker: GitHub issue #3.

Cross-device evidence mangler fortsat.

## ChatGPT / produkt — M-Pre

Tracker: GitHub issue #7.

Ready-to-run; afventer tre menneskelige sessioner med mindst to forskellige par.

## Content contract

Tracker: GitHub issue #8.

Løsningspakke findes i `docs/52_CONTENT_CONTRACT_RESOLUTION_PROPOSAL.md` samt `content/proposals/`.

- intro → anbefalet eksplicit onboarding-sequence
- Day 3 → anbefalet eksplicit planning phase
- minimal fire-start → source/spec klar, men scopevalg afventer Anders

---

# Leveret på ChatGPT-siden

## Produkt/design/QA foundation

- `docs/37_NON_UNITY_GAP_AUDIT.md`
- `docs/38_SOURCE_ASSET_MANIFEST.md`
- `docs/39_AUDIO_CUE_MANIFEST.md`
- `docs/40_UX_COPY_AND_LOCALIZATION_CATALOG.md`
- `docs/41_PERSONALIZATION_PACKAGE_SPEC.md`
- `docs/42_HUMAN_QA_PLAYTEST_PACK.md`
- `docs/43_IP_AND_ASSET_PROVENANCE.md`
- `docs/44_CONTENT_COVERAGE_MATRIX.md`
- `docs/45_GIFT_EXPERIENCE_AND_RELEASE_FLOW.md`
- `docs/46_STORMNATTEN_EVENT_CATALOG.md`
- `docs/47_VISUAL_STYLE_BIBLE.md`
- `docs/48_UI_INFORMATION_ARCHITECTURE.md`
- `docs/49_AFTER_ACTION_AND_REPLAY_SPEC.md`
- `docs/50_PRODUCT_TELEMETRY_AND_METRICS.md`
- `docs/51_BACKLOG_OWNERSHIP_AND_STATUS_OVERLAY.md`
- `docs/52_CONTENT_CONTRACT_RESOLUTION_PROPOSAL.md`
- `docs/53_NARRATIVE_CONTINUITY_PASS.md`
- `docs/54_NEUTRAL_FALLBACK_PACKAGE.md`
- `docs/55_SOURCE_PRODUCTION_BATCH_PLAN.md`
- `docs/56_A2_CORE_PROP_SOURCE_SPECS.md`

## Interaction handoffs

`design/interactions/`:

- planning table
- shelter reinforcement
- fire start
- ravine rescue
- storm finale

Hvert brief beskriver player experience, begge roller, fail-forward, source assets/audio/copy, comfort og acceptance — ikke Unity-arkitektur.

## Machine-readable source content

`content/`:

- dansk localization source
- Stormnatten action-card source
- 10-event authoring source
- neutral personalization profile
- onboarding-sequence proposal
- Day 3 planning proposal

Proposal-filer er markeret `proposal-not-canonical` og må ikke forveksles med accepterede beslutninger.

## Content authoring templates

`templates/content/`:

- event
- interaction brief
- action card
- source asset handoff
- audio cue handoff

---

# Faktisk source-artproduktion

## A1 gameplay-readable UI/source kit — produceret

`source_art/ui/a1/` indeholder separate SVG source masters for bl.a.:

- Player A/B identity
- shelter/fire/food/signal/medical/explore icons
- health/fatigue/injury/wet-cold status
- warning/success/partial shapes
- effort markers P1/P2
- action-card base
- wrist-status frame
- snap/grip/tension/repair feedback

Pakken har egen `PROVENANCE.md` og er class `OWN`.

Første visuelle QA fandt to problemer og de blev rettet:

- fatigue-ikonets første version læste for meget som en pose/weight
- signal-ikonet havde for lille edge margin

SVG source masters er bevaret; Unity-import/raster/atlas tilhører Claude.

## Neutral fallback source-art — produceret

`source_art/neutral/`:

- fictional rescue/chart card
- compass memento
- route card
- signal tag

Alle er project-originale, uden real-world brands/maps, med provenance.

Neutral machine-readable profile findes også under `content/personalization/`.

---

# Non-Unity CI

Ny validator:

`tools/validate_non_unity_sources.py`

Ny workflow:

`.github/workflows/non-unity-source-validation.yml`

Den kontrollerer bl.a.:

- JSON parse/source metadata
- localization references
- action icon references
- event audio/copy references
- SVG XML/viewBox
- provenance på source-art packs
- proposal isolation
- oplagte private-content fejl

**Første CI-run: success.**

---

# Evidens der stadig ikke må opfindes

- M-Pre / issue #7
- OQ-008 fairness/randomness
- OQ-009 role assignment
- OQ-010 after-action competition
- M3/M4 balance/tuning
- M3-M9 human gates
- M0b/device gates

---

# Næste aktive ChatGPT-bølge

## N-026 — A2 prop source handoff packages

Brug `docs/56_A2_CORE_PROP_SOURCE_SPECS.md` til at gøre hver core prop klar som separat source-handoff:

- heavy crate
- firepit
- firesteel
- tinder
- wind shield
- shelter beam
- rope/coil
- tarp
- planning table
- signal frame

## N-027 — A3 storm source references

Source-side reference packs for:

- rain
- wind debris
- ember/smoke
- wetness
- collapse/impact
- storm phase intensity

Runtime VFX remains Claude.

## N-028 — Audio production source plan → files

Start med AU-1:

- planning feedback
- rope tension
- shelter stress
- fire-state feedback
- reconnect/system feedback

Actual final Unity mix waits Claude/device evidence.

## N-029 — Complete neutral source package

Remaining non-Unity item:

- neutral radio VO source/strategy

Runtime binding remains Claude.

## N-030 — Content contract follow-up

Issue #8:

- canonicalize intro/Day3 only after data-contract review
- fire-start scope remains Anders decision

## N-031 — Source provenance register expansion

Register actual produced A1/neutral source packs in central provenance summary, while per-pack records remain authoritative.

## N-032 — Continue machine-readable authoring

Add authoring source where it reduces later Unity guesswork, without locking numeric balance.

---

# M1 handoff

Når **M0b + M-Pre begge er grønne**, samles det allerede producerede materiale til en kompakt M1 implementation handoff til Claude.

Det betyder, at M1 ikke starter med designarbejde fra nul.

---

# Arbejdsregel ved “kør videre”

1. kontrollér seneste repo/issues/CI
2. tag højeste ublokerede non-Unity-opgave
3. ændr ikke Unity-filer
4. producer konkrete artifacts/source, ikke kun planer
5. QA egne leverancer
6. brug human/device evidence hvor det faktisk kræves
7. opdatér workstream ved reelle statusskift

> **Der er fortsat væsentligt arbejde på ChatGPT-siden. Gates bestemmer hvad der må låses — ikke om arbejdet må fortsætte.**
