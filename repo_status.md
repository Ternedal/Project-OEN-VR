# Repository status

**Opdateret:** 2026-08-14  
**Baseline:** v2.1

## Platform og scope

- Quest 2 = performance-/kvalitetsgulv.
- Quest 3/3S = enhanced parity.
- Quest 1 = droppet runtime/testlane (`DROP_Q1_RUNTIME`); kun historisk/frossen sideload-demo.
- Accepted gave-scope = **1.012 t**; **439 t deferred**, så længe fire-start ikke promoveres.
- Claude ejer Unity/runtime/editor/XR/Fusion/C#/build/device.
- ChatGPT ejer non-Unity produkt/content/source/provenance/QA/tooling.

## Autoritative statusflader

- source/content state: `content/source_inventory.source.json`
- non-Unity workflow/tooling state: `content/non_unity_capability_matrix.source.json`
- reconciled non-Unity gap closeout: `docs/37_NON_UNITY_GAP_AUDIT.md`
- source asset IDs/handoff: `docs/38_SOURCE_ASSET_MANIFEST.md`
- source-art provenance: `source_art/PROVENANCE_INDEX.md`
- ChatGPT execution rules: `docs/36_CHATGPT_WORKSTREAM.md`

**Regel:** tooling-ready, source-ready, candidate-ready og technical-intake-passed er ikke det samme som human-approved, Unity-integrated, Quest-approved eller release-approved.

---

# Reelle projektgates

## M0b — issue #3 — fysisk Quest 2/3 evidence

Per-client feasibility er dokumenteret, men rigtig cross-device evidence mangler fortsat for bl.a.:

- remote head/hands
- compatibility mismatch rejection
- shared two-player state
- 10× Q2↔Q3 coop-object løft uden permanent desync
- 72 Hz minimal network scene
- standby/reconnect
- faktisk compatibility matrix

Ingen synthetic/self-test må lukke denne gate.

## M-Pre — issue #7 — faktisk human product evidence

Ready-to-run materiale, evaluator og tamper-evident evidence-bundle tooling er klar:

- `prototype/m-pre/`
- `tools/evaluate_mpre.py`
- `content/mpre/evidence_bundle_contract.source.json`
- `tools/package_mpre_evidence.py`
- `tools/validate_mpre_evidence_bundle.py`

Der er fortsat ingen påståede menneskesessioner. Gate kræver 3 reelle sessioner og mindst 2 testerpar.

## Fire-start — issue #8 — owner decision

Onboarding og Day 3 planning er canonical. Fire-start er fortsat owner-gated:

- `implementationAllowed=false`
- ikke accepted gift scope
- 1.012 accepted timer / 439 deferred timer forbliver uændret

Anders skal eksplicit vælge remove/skip, minimal onboarding beat eller full PO-044 før scope/totals ændres.

**M1 runtime implementation åbner først efter grøn M0b + M-Pre.**

---

# Non-Unity foundation

Den oprindelige N-002–N-010 gap-kø er reconcilet og leveret. Se `docs/37_NON_UNITY_GAP_AUDIT.md` og den tilhørende CI-validator.

Foundation på `main` omfatter bl.a.:

- source asset manifest
- audio cue manifest
- dansk UX/copy/localization catalog
- personalization package spec + neutral fallback
- human QA/playtest pack
- IP/provenance workflow/register
- Stormnatten content coverage matrix
- releasekritiske interaction briefs
- gift/first-launch/replay product flow
- canonical onboarding + Day 3 planning
- after-action/event/finale presentation contracts
- expanded source-art packages og machine-readable inventory

Producer yderligere art/content/source kun når en konkret manglende master eller contract reducerer implementation ambiguity. Undgå art for art's sake.

---

# Audio — faktisk pipeline-status

Den komplette machine-readable oversigt ligger i `content/non_unity_capability_matrix.source.json`.

## Acquired ambience/Foley

Repoet har provenance/receipts og technical QA for:

- base originals: wind, rain, fire
- extension: ocean + wood/cloth packs
- field backlog: **9 acquired originals** — de tidligere 7 plus canopy-wind og rough-ocean candidates

De to nyeste field-sources er pinned i `content/audio/acquisition_field_backlog_final_receipt.source.json` til Actions run `31799582783`, artifact `9218700659` og exact source SHA-256. Rough-ocean-originalen har én full-scale integer sample og skal have eksplicit headroom/peak-inspection før en eventuel derivative.

Der findes nu en reproducibel **27-source audition pack**:

- `docs/67_AUDIO_SOURCE_AUDITION_PACK.md`
- `tools/build_audio_source_audition_pack.py`
- `tools/validate_audio_source_audition_contract.py`

Preliminary human shortlist-evidence kan hashbindes, men giver stadig ikke source approval.

**Eneste tilbageværende field-acquisition-rest:** `SFX_AMB_Beach_PalmCanopy`. En exact-fit CC0-kandidat er fundet, men originaldownload kræver login; preview audio må ikke bruges som source master. Der substitueres ikke med generisk temperate-tree wind bare for at lukke coverage.

## Typed source approval

Efter shortlist findes en separat typed human approval gate:

- `content/audio/source_approval_contract.source.json`
- `tools/prepare_audio_source_approval_review.py`
- `tools/normalize_audio_source_approval_review.py`
- `tools/materialize_source_approved_audio.py`

`MATERIAL_MATCH >= 3`, reviewer identity/timestamp, provenance og source SHA håndhæves fail-closed. Source-approved materialization kopierer originalbytes uændret.

Der er **ingen faktisk human source approval påstået**.

## Derived masters

Hvis en source-approved original redigeres, findes en separat derived-master gate:

- `content/audio/derived_master_contract.source.json`
- `tools/validate_audio_derived_master_submission.py`
- `tools/prepare_audio_derived_master_review.py`
- `tools/normalize_audio_derived_master_review.py`
- `tools/materialize_derived_master_approved_audio.py`

Krav omfatter explicit edit recipe, 48 kHz / 24-bit integer PCM, no full-scale samples, ny file identity og **gentaget human listening på derived bytes**.

Der er ingen faktisk derived-master approval påstået.

## Radio VO

Canonical shape: **9 cues × 3 takes = 27 take candidates**.

Pipeline på `main`:

1. exact Danish recording board/session prep
2. technical intake
3. human pronunciation/delivery/semantic/rights review
4. one-take-per-cue selection
5. byte-identical selected dry materialization

Vigtige contracts/tools:

- `content/audio/radio_vo_session_contract.source.json`
- `content/audio/radio_vo_human_review_contract.source.json`
- `content/audio/radio_vo_selected_dry_contract.source.json`
- `tools/prepare_radio_vo_session.py`
- `tools/normalize_radio_vo_human_review.py`
- `tools/materialize_radio_vo_selected_dry.py`

Faktisk authorized recording og human selection mangler fortsat.

## Adaptive music

14 deterministic candidates er auditeret og exact-byte reproducible. Fem candidate-families er mapped til canonical music cues; `MUS_Warning_LowPulse` er eksplicit unmapped.

Pipeline:

1. human audition af 14 candidates
2. canonical family selection
3. kun `keep + alle relevante checks pass` kan vælges
4. 5/5 positive selections kræves for canonical materialization
5. selected sources kopieres byte-identisk

Contracts/tools:

- `content/audio/music_candidate_audit.source.json`
- `content/audio/music_candidate_reproducibility.source.json`
- `content/audio/music_family_selection_contract.source.json`
- `content/audio/music_selected_source_contract.source.json`
- `tools/normalize_music_candidate_review.py`
- `tools/normalize_music_family_selection.py`
- `tools/materialize_music_selected_sources.py`

Human audition/selection mangler fortsat.

---

# Unity / Claude drafts

PR #5 og #6 forbliver draft/fysisk-QA-blokerede og må ikke merges alene på repo/CI-evidens.

Autoritativ physical QA kræver aktuelle, source-stamped Unity/Quest-resultater. Gammel eller synthetic evidence må ikke genbruges som om den dækkede en ny payload.

---

# CI / kvalitet

Aktive guards omfatter nu bl.a.:

- Core tests
- Validate handoff
- Validate non-Unity sources
- Validate source inventory
- Validate non-Unity capability matrix
- Validate non-Unity gap closeout
- source closeout / manifest alignment
- audio acquisition/listening/field review
- **27-source audition pack builder**
- typed audio source approval
- derived-master pipeline
- radio VO session/human-review/selected-dry tooling
- music audition/family-selection/reproducibility tooling
- M-Pre evaluator/evidence-bundle tooling

Grøn CI beviser repository-/contract-integritet. Den erstatter aldrig human listening/playtest eller fysisk Quest evidence.

---

# Næste reelle arbejde

Prioritet nu:

1. **M-Pre:** 3 reelle human sessions → evaluator → evidence bundle → eksplicit gate-resultat.
2. **M0b:** rigtig Quest 2/Quest 3 cross-device evidence fra Claude/Anders.
3. **Issue #8:** Anders disponerer fire-start scope.
4. **Ambience/Foley:** human audition af 27-source pack → typed source approval → evt. documented derived master + ny human listening.
5. **Field acquisition:** find en exact, direct-download, CC0/Public-Domain palm-canopy original; det er den eneste åbne field-source acquisition.
6. **Radio VO:** faktisk authorized recording af 27 takes → human take review/selection.
7. **Music:** human audition af 14 candidates → 5 canonical family selections.
8. **Claude #5/#6:** re-sync og fysisk Unity/Quest QA før merge.
9. **Private personalization:** producer kun når det faktisk skal ind i gavebuildet; neutral fallback findes.
10. **M1 handoff:** samles først når M0b + M-Pre er grønne.

Hvis en ny autonom non-Unity-opgave ikke reducerer en dokumenteret gap, skal den ikke oprettes bare for aktivitetens skyld.
