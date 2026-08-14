# ChatGPT-workstream — PROJECT ØEN

**Ejer:** ChatGPT  
**Projektejer:** Anders  
**Opdateret:** 2026-08-14  
**Scope:** Alt uden for Unity jf. `AI_COLLABORATION_AGREEMENT.md`

## Arbejdsregel

ChatGPT ejer produkt/content/source/QA uden for Unity. Claude ejer Unity/runtime/editor/XR/Fusion/C#/build/device-runtime.

M0b + M-Pre blokerer **M1 runtime-implementation**. De blokerer ikke non-Unity sourceproduktion, content contracts, provenance, review-tooling eller handoff-forberedelse.

Human/device/listening evidence må aldrig opfindes eller erstattes af synthetic CI.

---

# Aktuelle gates

## M0b — issue #3

Per-client Quest-feasibility er dokumenteret. Der mangler fortsat rigtig cross-device evidence for bl.a.:

- remote head/hands
- compatibility mismatch rejection
- shared two-player state
- 10× Q2↔Q3 uden permanent desync
- 72 Hz minimal network scene
- standby/reconnect measurement
- compatibility matrix med faktiske resultater

Dette er Claude/device-lane. Ingen synthetic/self-test lukker gaten.

## M-Pre — issue #7

Tre faktiske menneskesessioner med mindst to testerpar mangler fortsat.

Repoet har nu både facilitator/evaluator og tamper-evident evidence-bundle tooling:

- `prototype/m-pre/facilitator_runner.html`
- `prototype/m-pre/print_pack.html`
- `tools/evaluate_mpre.py`
- `content/mpre/evidence_bundle_contract.source.json`
- `tools/package_mpre_evidence.py`
- `tools/validate_mpre_evidence_bundle.py`

Bundle-tooling må kun validere og hashbinde leveret menneskeevidens. Det opfinder ikke sessionsdata, accepterer ikke gaten og lukker ikke issue #7.

## Content scope — issue #8

Onboarding og Day 3 er canonical:

- `content/onboarding/stormnatten.onboarding.source.json`
- `content/phases/stormnatten.day3_planning.source.json`
- `content/contracts/issue8.reconciliation.source.json`

Proposal-filer under `content/proposals/` er historiske/non-canonical.

**Fire-start er stadig owner-gated:** `implementationAllowed=false`; ingen accepted-gift timer ændres uden Anders' eksplicitte scope-disposition.

---

# Verificeret non-Unity source på main

## Art/source

- A1 UI/source kit
- A2 core props: 10 individuelle masters
- A3 storm/VFX inkl. rope-strain
- A4 camp/wreck/radio/signal references
- B1 environment/resources + supply crate + `ITM_KNIFE_001`
- B2 event presentation for alle 10 events
- A5 source meshes/items/release UI inkl. ember carrier og repair mallet
- material families
- P1/P2 hand references + `CHR_TORSO_BASE_001`
- neutral fallback package
- C1 `ENV_EPILOGUE_001` reuse-first ending reference

Source-ready er **ikke** Unity-integrated eller release-approved.

## Content/UX contracts

Canonical/machine-readable contracts omfatter bl.a.:

- dansk localization
- Stormnatten actions/events/event presentation
- planning/status UI og release UI
- after-action presentation
- material families
- neutral personalization
- canonical onboarding + Day 3 planning
- issue #8 reconciliation
- storm-finale source contract
- audio acquisition/listening contracts
- radio VO session intake
- adaptive-music candidate audit/reproducibility
- M-Pre evidence-bundle contract

`content/source_inventory.source.json` er den autoritative machine-readable oversigt over nuværende non-Unity source-status.

---

# Audio — faktisk status

## Acquired environment / Foley sources

Audio er ikke længere kun en acquisition-plan.

Repoet har provenance/receipts for:

- base originals: wind, rain og fire
- extension acquisition: ocean + wood/cloth packs
- syv field-backlog originals

Relevante source-of-truth-filer omfatter:

- `content/audio/acquisition_receipt.source.json`
- `content/audio/acquisition_extension_receipt.source.json`
- `content/audio/acquisition_field_backlog_receipt.source.json`
- `content/audio/acquisition_technical_qa.source.json`
- `content/audio/listening_review_targets.source.json`

Wood/cloth members er teknisk shortlisted. Field-review kan hashbindes via `tools/normalize_audio_field_review.py`.

**Acquired/technical-QA betyder ikke human listening-approved, source-approved, derived-master-approved eller release-approved.**

## Radio VO

9 cues × 3 takes er specificeret. Repoet har nu en fail-closed 27-take recording intake:

- `content/audio/radio_vo_recording_queue.source.json`
- `content/audio/radio_vo_session_contract.source.json`
- `tools/prepare_radio_vo_session.py`
- `tools/validate_radio_vo_session.py`

Faktisk recording, dansk pronunciation/delivery review og human listening approval mangler.

## Adaptive music

14 originale procedurale music candidates er auditeret og audition-ready:

- `content/audio/music_candidate_audit.source.json`
- fem candidate-families er mappet til eksisterende canonical music cues
- `MUS_Warning_LowPulse` er eksplicit unmapped og må ikke bindes uden særskilt produktbeslutning

Den originale generator er nu bevaret på `main`:

- `tools/generate_authored_adaptive_music.py`
- `content/audio/music_candidate_reproducibility.source.json`
- `tools/validate_music_candidate_reproducibility.py`

Pinned CI har reproduceret **14/14 eksakte SHA-256-identiske WAVs** med CPython 3.12.13 + NumPy 2.3.5 på Ubuntu 24.04. Kandidaterne er dermed ikke afhængige af den tidsbegrænsede PR #6 artifact.

Dette er stadig **ikke** human audition/source approval eller runtime/headset acceptance.

---

# Claude draft PRs

PR #5 og #6 forbliver draft/fysisk-QA-blokerede.

De må ikke merges alene på repo/CI-evidens. Autoritativ fysisk QA skal være bundet til en re-synced branch/payload og rigtig Unity/Quest evidence.

ChatGPT må gerne genbruge eller auditere non-Unity source-materiale fra disse branches, når provenance og identity kan verificeres uden at trække runtime-laget med ind.

---

# CI / quality

Aktive guards omfatter bl.a.:

- Core tests
- Validate handoff
- Validate non-Unity sources
- Validate source inventory + backing
- source closeout / audio manifest alignment
- AU-1 regeneration/validation
- audio acquisition/listening/field-review validators
- radio VO session tooling
- music candidate audition tooling
- music exact-byte reproducibility
- M-Pre facilitator/evaluator/evidence-bundle tooling

Grøn CI beviser repository-/contract-integritet. Den erstatter ikke menneskelig listening/playtest eller Quest-device evidence.

---

# Next real work

Den brede automatable source-backlog er ikke længere den primære flaskehals. Prioritér nu:

1. **M-Pre:** tre reelle human sessions → evaluator → hashbundet evidence bundle → eksplicit gate-acceptance.
2. **M0b:** ingest rigtig two-headset/Quest evidence fra Claude/Anders.
3. **Issue #8:** Anders disponerer fire-start scope; timer/backlog ændres kun hvis scope ændres.
4. **Audio:** human audition/selection af acquired ambience/Foley sources; promover kun eksplicit godkendte sources.
5. **Music:** human audition af de 14 hashbundne candidates; eksplicit source promotion af valgte kandidater.
6. **Radio VO:** faktisk recording af 27 takes → technical intake → pronunciation/delivery/listening review.
7. **Claude #5/#6:** re-sync før autoritativ physical QA; ingen gammel evidence må genbruges uden korrekt source stamp/pin.
8. Producer yderligere art/content/source kun når et konkret manglende master/contract reducerer implementation ambiguity; undgå art for art's sake.
9. M1 handoff assembly først når både M0b + M-Pre er grønne.

---

# Arbejdsregel ved “kør videre”

1. check current `main`, issues, åbne PRs og CI
2. tag højeste ublokerede non-Unity-opgave
3. editér ikke Unity/runtime code
4. lever konkrete source/contracts/tooling eller repo-hygiejne — ikke pseudo-progress
5. QA og bevar provenance/hash identity
6. opfind aldrig human/device/listening evidence
7. promover aldrig acquired/candidate audio uden den krævede human gate
8. hvis kun human/device/owner gates står tilbage, gør tooling/handoff klar men lad gaten stå åben
