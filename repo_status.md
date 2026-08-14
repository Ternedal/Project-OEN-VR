# Repository status

**Opdateret:** 2026-08-15
**Baseline:** v2.1

## Platform og scope

- Quest 2 = performance-/kvalitetsgulv.
- Quest 3/3S = enhanced parity.
- Quest 1 = droppet runtime/testlane (`DROP_Q1_RUNTIME`).
- Accepted gave-scope = **1.012 t**; **439 t deferred**, så længe fire-start ikke promoveres.
- Claude ejer Unity/runtime/editor/XR/Fusion/C#/build/device.
- ChatGPT ejer non-Unity produkt/content/source/provenance/QA/tooling.

## Autoritative statusflader

- source/content state: `content/source_inventory.source.json`
- workflow/tooling state: `content/non_unity_capability_matrix.source.json`
- gap closeout: `docs/37_NON_UNITY_GAP_AUDIT.md`
- ChatGPT execution rules: `docs/36_CHATGPT_WORKSTREAM.md`

`tooling-ready`, `source-ready`, `candidate-ready` og `technical-intake-passed` er ikke human-approved, Unity-integrated, Quest-approved eller release-approved.

---

# Reelle projektgates

## M0b — issue #3

Rigtig Quest 2/Quest 3 cross-device evidence mangler fortsat: remote head/hands, mismatch rejection, shared state, 10× Q2↔Q3 coop-object, 72 Hz, standby/reconnect og faktisk compatibility matrix.

**Ingen synthetic/self-test må lukke denne gate.**

## M-Pre — issue #7

Evaluator og evidence-bundle tooling er klar, men **der er fortsat ingen påståede menneskesessioner**. Gate kræver 3 reelle sessioner og mindst 2 testerpar.

## Fire-start — issue #8

Onboarding og Day 3 er canonical. Fire-start forbliver owner-gated:

- `implementationAllowed=false`
- ikke accepted gift scope
- **1.012 accepted timer / 439 deferred timer** uændret

Anders skal eksplicit disponere scope før timer eller implementation ændres.

---

# Non-Unity foundation

N-002–N-010 foundation er leveret og valideret: source-asset/audio-manifests, dansk UX/localization, personalization/fallback, human QA, provenance, content coverage, interaction briefs og gift/release flow.

Producer kun nyt source/content, når et konkret dokumenteret gap reduceres.

## Grafik/source-produktion

Repoet indeholder nu konkrete importklare non-Unity masters, ikke kun briefs:

- **45 OBJ** source meshes med matchende materialehandoff, herunder Camp, B1, A5, avatar og C1-epilog;
- **22 PNG** texture/VFX sources;
- A2-, B1-, A4-, A5-, avatar- og C1-pakker har eksplicitte produktionsvalidatorer;
- de sidste reference-only priority interactables (`ITM_FIRESTEEL_001`, `ITM_TINDER_001`, `ITM_ROPE_COIL_001`, `ITM_CLOTH_001`, `ITM_MAP_FRAGMENT_001`, `ITM_RADIO_BATTERY_001`) har nu UV-mapped OBJ/MTL source geometry;
- de fem A5-props og utility knife/repair mallet/ember carrier er erstattet eller opgraderet til UV/materiale/semantic-part handoff;
- `ENV_EPILOGUE_001` har en reuse-first production overlay, ikke kun et mood board.

Dette lukker den automatiserbare source-art-produktion. Unity-import, shader/prefab/collider/rig/VFX-binding og Quest-visuel acceptance er fortsat runtime/device gates.

---

# Audio — faktisk pipeline-status

## Acquired ambience/Foley sources

Repoet har 3 main originals, 15 extension sources/members og 9 field originals. De udgør en reproducibel **27-source** audition lane.

- final field receipt: `content/audio/acquisition_field_backlog_final_receipt.source.json`
- audition builder: `tools/build_audio_source_audition_pack.py`
- typed approval: `content/audio/source_approval_contract.source.json`
- derived-master gate: `content/audio/derived_master_contract.source.json`

Kun `SFX_AMB_Beach_PalmCanopy` mangler stadig field acquisition. En exact-fit CC0 source er kendt, men originalfilen kræver authenticated download; preview audio bruges ikke som source master.

Der er ingen faktisk human source approval eller derived-master approval påstået.

## Physical Foley — 17 cues / 73 takes

De releasekritiske heavy-crate, rope/tarp og shelter-timber cues har nu en separat fysisk recording lane.

Recording/intake:

- `content/audio/foley_session_contract.source.json`
- `docs/74_FOLEY_RECORDING_INTAKE.md`
- `tools/prepare_foley_session.py`
- `tools/validate_foley_session.py`

Shape er **17 canonical cues / 73 distinct physical raw take slots**. Technical intake kræver 48 kHz / 24-bit mono PCM, no full-scale samples, current session/provenance bindings og unikke raw bytes.

Human review/promotion:

- `content/audio/foley_human_review_contract.source.json`
- `content/audio/foley_source_materialization_contract.source.json`
- `docs/75_FOLEY_HUMAN_REVIEW_AND_SOURCE_APPROVAL.md`
- `tools/prepare_foley_human_review.py`
- `tools/normalize_foley_human_review.py`
- `tools/materialize_foley_source_approved.py`

Alle 73 take hashes bindes til 17 cue-family reviews. De 8 canonical listening checks suppleres med `UNDER_WEATHER_READABILITY`. MATERIAL_MATCH og VARIATION_VALUE skal være >=3. Komplet negativ/rerecord evidence er gyldig, men kan ikke source-promote.

**Faktisk status:** 0 fysiske Foley recordings og 0 human Foley approvals er påstået. Tooling er klar; human recording/listening mangler.

Fire-start-specifik Foley, herunder firesteel, forbliver uden for denne lane mens issue #8 er owner-gated.

## Radio VO

Canonical shape: **9 cues × 3 takes = 27**.

Tooling dækker recording-board, technical intake, human pronunciation/delivery/semantic/rights review og byte-identisk selected-dry materialization:

- `content/audio/radio_vo_human_review_contract.source.json`
- `content/audio/radio_vo_selected_dry_contract.source.json`

Faktisk authorized recording og human selection mangler.

## Adaptive music

**14 deterministic** candidates er auditeret og exact-byte reproducible. Fem canonical families kan human-selectes; `MUS_Warning_LowPulse` forbliver unmapped.

- `content/audio/music_family_selection_contract.source.json`
- `content/audio/music_selected_source_contract.source.json`

Human audition/selection mangler.

---

# Integreret produktionsbaseline

De tre resync-/produktionsspor er nu landet på `main`:

- PR #56 — non-Unity product/content/source/provenance/tooling — merge `4b22cfeadd581140b2ee4e518d704a20a2106e27`;
- PR #49 — authored first-playable audio/runtime/editor foundation — merge `13828bf569649d3a792233a1bb3ff56edbfcd45a`;
- PR #48 — generated production art/runtime/editor integration — merge `2842f5f47005110d72cc8afc9905e85f947d52ae`.

Den endelige merge-head bestod `Core tests #1829`, `Validate handoff #1906` og alle generation/validation-trin i `Generate Project OEN runtime art #283`. Den pinned first-playable-audioartifact fra den grønne `Audio Validation #182` er desuden uafhængigt verificeret til 173 clips / 47 events mod committed ZIP- og manifest-SHA.

Dette er repository-/CI-integration, ikke fysisk acceptance. Unity 6000.4.10f1 import/compile i den faktiske projektkopi, saved-scene visuel/skala-review, in-headset audio review og Quest 2/3 device/cross-device evidence er fortsat åbne Claude/Anders-gates. Repo/CI-evidence alene må ikke bruges som Quest acceptance.

---

# CI / kvalitet

Aktive guards omfatter bl.a. Core, handoff, source inventory, non-Unity capability/gap/status, field acquisition, 27-source audition/approval, derived masters, **Foley 17/73 recording intake + human review/source promotion**, radio VO, music, M-Pre evidence tooling og de konkrete source-mesh/VFX/audio-master packs.

Grøn CI beviser contract/repository-integritet; ikke menneskelig listening/playtest eller fysisk Quest evidence.

---

# Prioritet nu

1. **M-Pre:** 3 reelle human sessions → evaluator → evidence bundle → gate-resultat.
2. **M0b:** rigtig Quest 2/Quest 3 evidence.
3. **Issue #8:** Anders disponerer fire-start.
4. **Physical Foley:** optag 73 distinct performances → technical intake → human 17-cue review → evt. copy-only source approval.
5. **Ambience/Foley acquisition:** human audition af 27-source pack; find exact PalmCanopy original under current policy.
6. **Radio VO:** faktisk authorized 27-take recording → review/selection.
7. **Music:** human audition af 14 candidates → 5 canonical selections.
8. **Post-merge Unity/Quest QA:** importér den integrerede `main`-head i Unity 6000.4.10f1, kør saved-scene/visuel/audio-review og indsamle faktisk Quest-evidence.
9. M1 handoff først efter grøn M0b + M-Pre.

Hvis en autonom opgave ikke reducerer et dokumenteret gap, skal den ikke oprettes for aktivitetens skyld.
