# ChatGPT-workstream — PROJECT ØEN

**Ejer:** ChatGPT  
**Projektejer:** Anders  
**Opdateret:** 2026-08-14  
**Scope:** Alt uden for Unity jf. `AI_COLLABORATION_AGREEMENT.md`

## Arbejdsregel

ChatGPT ejer produkt/content/source/provenance/QA/tooling uden for Unity. Claude ejer Unity/runtime/editor/XR/Fusion/C#/build/device.

Human/device/listening evidence må aldrig opfindes eller erstattes af synthetic CI.

Autoritative statusflader:

- source/content state: `content/source_inventory.source.json`
- workflow/tooling state: `content/non_unity_capability_matrix.source.json`
- reconciled gap closeout: `docs/37_NON_UNITY_GAP_AUDIT.md`
- human repo summary: `repo_status.md`

`source-ready`, `tooling-ready`, `candidate-ready` og `technical-intake-passed` betyder ikke human-approved, Unity-integrated, Quest-approved eller release-approved.

---

# Aktuelle gates

## M0b — issue #3

Claude/device-lane. Rigtig Quest 2/Quest 3 cross-device evidence mangler fortsat:

- remote head/hands
- mismatch rejection
- shared two-player state
- 10× Q2↔Q3 uden permanent desync
- 72 Hz minimal network scene
- standby/reconnect
- compatibility matrix med faktiske resultater

Ingen synthetic/self-test lukker gaten.

## M-Pre — issue #7

Tre faktiske menneskesessioner med mindst to testerpar mangler.

Tooling er klar:

- `prototype/m-pre/`
- `tools/evaluate_mpre.py`
- `content/mpre/evidence_bundle_contract.source.json`
- `tools/package_mpre_evidence.py`
- `tools/validate_mpre_evidence_bundle.py`

Bundle-tooling validerer leveret human evidence; det skaber ikke sessionsdata og lukker ikke issue #7.

## Fire-start — issue #8

Onboarding og Day 3 er canonical. Fire-start forbliver:

- `implementationAllowed=false`
- uden for accepted gift scope
- 1.012 accepted timer / 439 deferred timer uændret

Anders skal vælge remove/skip, minimal onboarding beat eller full PO-044 før scope/totals ændres.

**M1 runtime implementation åbner først efter grøn M0b + M-Pre.**

---

# Automatable non-Unity foundation

Den oprindelige N-002–N-010 gap-kø er leveret og CI-beskyttet i `docs/37_NON_UNITY_GAP_AUDIT.md`.

Det omfatter bl.a.:

- source asset manifest
- audio cue manifest
- dansk UX/copy/localization catalog
- personalization package spec + neutral fallback
- human QA/playtest pack
- IP/provenance workflow/register
- content coverage matrix
- interaction briefs for planning/shelter/fire/ravine/storm finale
- gift/first-launch/replay product flow
- canonical onboarding + Day 3 planning
- after-action/event/finale contracts
- source-art inventory/provenance

Producer kun yderligere art/content/source, hvis en konkret manglende master eller contract reducerer implementation ambiguity.

---

# Audio — workflow-state

Den fulde machine-readable status ligger i `content/non_unity_capability_matrix.source.json`.

## Acquired ambience/Foley

Repoet har base, extension og **9 field originals** med provenance/technical QA samt en reproducibel **27-source audition pack**.

De to nyeste field candidates er:

- `SFX_AMB_JUNGLE_CANOPY_WIND_ALT_01` → `SFX_AMB_Jungle_CanopyWind`
- `SFX_WTH_STORM_ROUGH_OCEAN_ALT_01` → `SFX_WTH_Storm_RoughOcean`

De er exact-byte acquired og pinned i `content/audio/acquisition_field_backlog_final_receipt.source.json`, men begge kræver human semantic listening. Canopy-kilden er temperate forest og skal afvises/repurposes hvis biome-identiteten er forkert. Rough-ocean-kilden har én full-scale integer sample og kræver headroom-inspection før enhver derivative.

**Kun `SFX_AMB_Beach_PalmCanopy` mangler stadig field source acquisition.** Exact-fit CC0 research findes, men originalfilen kræver authenticated download; preview audio og generisk temperate-tree substitution er ikke acceptable.

Flow:

1. build audition pack
2. actual human shortlist
3. typed human source approval
4. exact-byte source-approved materialization
5. hvis redigeret: explicit derived-master submission + technical QA
6. repeated human listening på derived bytes
7. explicit derived-master-approved materialization

Vigtige entrypoints:

- `docs/67_AUDIO_SOURCE_AUDITION_PACK.md`
- `content/audio/source_approval_contract.source.json`
- `content/audio/derived_master_contract.source.json`
- `tools/build_audio_source_audition_pack.py`
- `tools/normalize_audio_source_approval_review.py`
- `tools/validate_audio_derived_master_submission.py`
- `tools/normalize_audio_derived_master_review.py`

Ingen faktisk human source/derived-master approval er påstået.

## Radio VO

Canonical shape: 9 cues × 3 takes = 27.

Tooling på `main` dækker:

- canonical Danish recording board/session prep
- technical intake
- human pronunciation/delivery/semantic/rights review
- one-take-per-cue selection
- byte-identical selected dry materialization

Contracts:

- `content/audio/radio_vo_session_contract.source.json`
- `content/audio/radio_vo_human_review_contract.source.json`
- `content/audio/radio_vo_selected_dry_contract.source.json`

Faktisk authorized recording og human selection mangler.

## Adaptive music

14 deterministic candidates; 5 canonical mapped families; `MUS_Warning_LowPulse` forbliver unmapped.

Tooling dækker:

- human candidate audition
- canonical-family selection
- keep+pass eligibility
- 5/5 positive selection gate
- exact-byte canonical source materialization

Contracts:

- `content/audio/music_candidate_audit.source.json`
- `content/audio/music_candidate_reproducibility.source.json`
- `content/audio/music_family_selection_contract.source.json`
- `content/audio/music_selected_source_contract.source.json`

Human audition/selection mangler.

---

# Claude draft PRs

PR #5 og #6 er fortsat draft/fysisk-QA-blokerede.

De må ikke merges på repo/CI-evidens alene. Autoritativ evidence skal være current-source-stamped og komme fra rigtig Unity/Quest execution.

---

# Next real work

Prioritér nu:

1. **M-Pre:** 3 reelle human sessions → evaluator → evidence bundle → gate-resultat.
2. **M0b:** rigtig two-headset/Quest evidence fra Claude/Anders.
3. **Issue #8:** Anders disponerer fire-start scope.
4. **Ambience/Foley:** human audition af 27-source pack → typed source approval → evt. documented derived edit + ny human listening.
5. **Field acquisition:** find direct original til `SFX_AMB_Beach_PalmCanopy` under CC0/Public-Domain-policy; det er eneste resterende field acquisition-gap.
6. **Radio VO:** faktisk authorized recording af 27 takes → human review/selection.
7. **Music:** human audition af 14 candidates → 5 canonical selections.
8. **Claude #5/#6:** re-sync + fysisk QA før merge.
9. Private personalization source produceres først når det konkret skal i gavebuildet; neutral fallback findes.
10. M1 handoff assembly først når både M0b + M-Pre er grønne.

---

# Arbejdsregel ved “kør videre”

1. check current `main`, issues, åbne PRs og CI
2. læs `content/non_unity_capability_matrix.source.json`
3. tag kun en autonom non-Unity-opgave hvis den reducerer en dokumenteret gap
4. editér ikke Unity/runtime code
5. QA og bevar provenance/hash identity
6. opfind aldrig human/device/listening evidence
7. promover aldrig acquired/candidate audio uden den krævede human gate
8. vælg aldrig fire-start scope på Anders' vegne
9. hvis kun human/device/owner gates står tilbage, stop pseudo-progress og hold handoff/tooling klar
