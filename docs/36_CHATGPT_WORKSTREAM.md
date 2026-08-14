# ChatGPT-workstream — PROJECT ØEN

**Ejer:** ChatGPT  
**Projektejer:** Anders  
**Opdateret:** 2026-08-14  
**Scope:** Alt uden for Unity jf. `AI_COLLABORATION_AGREEMENT.md`

## Arbejdsregel

ChatGPT ejer produkt/content/source/provenance/QA/tooling uden for Unity. Claude ejer Unity/runtime/editor/XR/Fusion/C#/build/device.

Human/device/listening evidence må aldrig opfindes eller erstattes af synthetic CI.

Autoritative statusflader:

- `content/source_inventory.source.json`
- `content/non_unity_capability_matrix.source.json`
- `docs/37_NON_UNITY_GAP_AUDIT.md`
- `repo_status.md`

`source-ready`, `tooling-ready`, `candidate-ready` og `technical-intake-passed` er ikke human-approved, Unity-integrated, Quest-approved eller release-approved.

---

# Aktuelle gates

## M0b — issue #3

Quest 2/Quest 3 cross-device evidence mangler. **Ingen synthetic/self-test lukker gaten.**

## M-Pre — issue #7

**Tre faktiske menneskesessioner** med mindst to testerpar mangler. Evaluator/evidence-bundle tooling er klar, men skaber ikke evidence.

## Fire-start — issue #8

Fire-start forbliver `implementationAllowed=false`, uden for accepted gift scope og med **1.012 accepted timer / 439 deferred timer** uændret. Anders ejer dispositionen.

---

# Automatable non-Unity foundation

N-002–N-010 er leveret og CI-beskyttet. Producer kun ny non-Unity source/tooling, når et konkret gap reduceres.

---

# Audio — workflow-state

## Acquired source lane

3 main + 15 extension + 9 field = reproducibel **27-source** audition boundary.

- `content/audio/source_approval_contract.source.json`
- `content/audio/derived_master_contract.source.json`

Kun `SFX_AMB_Beach_PalmCanopy` mangler field acquisition. Human audition/source approval mangler for de eksisterende candidates.

## Physical Foley — recording gate

Heavy crate, rope/tarp og shelter timber er samlet i en fysisk lane:

- `content/audio/foley_session_contract.source.json`
- `docs/74_FOLEY_RECORDING_INTAKE.md`
- `tools/prepare_foley_session.py`
- `tools/validate_foley_session.py`

Shape: **17 cues / 73 distinct physical take slots**. Technical intake kræver current session/provenance bindings, 48 kHz / 24-bit mono PCM, no full-scale samples og ingen duplicate raw bytes.

Faktisk recording findes ikke endnu.

## Physical Foley — human review/promotion gate

Efter en reel 53/53 technical pass:

- `content/audio/foley_human_review_contract.source.json`
- `content/audio/foley_source_materialization_contract.source.json`
- `docs/75_FOLEY_HUMAN_REVIEW_AND_SOURCE_APPROVAL.md`
- `tools/prepare_foley_human_review.py`
- `tools/normalize_foley_human_review.py`
- `tools/materialize_foley_source_approved.py`

Alle take SHA’er revalideres. Human reviewer vurderer alle 73 takes og alle 17 cue-familier med de 8 canonical listening checks + `UNDER_WEATHER_READABILITY`.

Krav til positiv promotion omfatter bl.a. MATERIAL_MATCH >=3, VARIATION_VALUE >=3, weather readability pass, reviewer/timestamp, rights og 53/53 keep + 13/13 accept-current-set.

Komplet `needs-rerecord` evidence er legitimt og normaliseres, men `readyForSourceMaterialization=false`.

Faktisk human Foley review/source approval findes ikke endnu. Fire-start-specifik Foley er fortsat owner-gated via issue #8.

## Radio VO

Canonical shape: **9 cues × 3 takes = 27**. Tooling dækker intake + human review + selected-dry materialization:

- `content/audio/radio_vo_human_review_contract.source.json`
- `content/audio/radio_vo_selected_dry_contract.source.json`

Authorized recording og human selection mangler.

## Music

**14 deterministic** candidates; 5 canonical mappings; Warning-familien unmapped.

- `content/audio/music_family_selection_contract.source.json`
- `content/audio/music_selected_source_contract.source.json`

Human audition/selection mangler.

---

# Claude drafts

PR #5/#6 må ikke merges på synthetic/repo-evidence alene. Re-sync og rigtig Unity/Quest evidence kræves.

---

# Next real work

1. M-Pre: 3 human sessions.
2. M0b: fysisk Q2/Q3 cross-device evidence.
3. Issue #8: Anders fire-start disposition.
4. Physical Foley: 73 recordings → technical intake → 17-cue human review → evt. source promotion.
5. 27-source ambience/Foley human audition + PalmCanopy acquisition.
6. Radio VO: 27 actual takes → review/selection.
7. Music: 14-candidate audition → 5 canonical selections.
8. Claude #5/#6 physical QA.
9. M1 handoff først når M0b + M-Pre er grønne.

---

# Arbejdsregel ved “kør videre”

1. check current `main`, issues, åbne PRs og CI
2. læs `content/non_unity_capability_matrix.source.json`
3. tag højeste ublokerede non-Unity-opgave som reducerer et dokumenteret gap
4. editér ikke Unity/runtime code
5. QA og bevar provenance/hash identity
6. opfind aldrig human/device/listening evidence
7. promover aldrig audio uden den krævede human gate
8. vælg aldrig fire-start scope på Anders' vegne
9. hvis kun human/device/owner gates står tilbage, stop pseudo-progress og hold handoff/tooling klar
