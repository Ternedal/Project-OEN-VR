# Source production control — PROJECT ØEN

**Ejer:** ChatGPT  
**Unity integration:** Claude  
**Dato:** 2026-08-13  
**Machine-readable status:** `content/source_inventory.source.json`

## Formål

Dette dokument er den aktuelle eksekveringsrækkefølge for non-Unity source-produktion. Det erstatter den oprindelige før-produktionsplan, som fortsat viste flere allerede producerede batches som `Not started`.

`source-ready` betyder ikke Unity-integreret eller release-approved.

---

# 1. Aktuel status

| Batch | Status | Næste reelle trin |
|---|---|---|
| A1 UI/readability | **Produceret + source-QA** | Claude import/readability/device QA |
| Neutral fallback | **Produceret + source-QA** | runtime fallback + M8 E2E |
| A2 core props | **10 individual masters + firepit source mesh produceret** | Claude import/representation; PO-044 manual fire-start er stadig owner-gated |
| A3 storm VFX | **Produceret source-reference** | Claude runtime VFX/performance tuning |
| A4 camp | **Source references produceret** | final world/material polish venter stabil geometry/evidence |
| B1 environment | **Source references produceret** | Claude world implementation |
| B1 resource set | **Core set produceret** | kun resterende stabile utility gaps |
| B2 event presentation | **7 masters produceret + mapped** | Claude binding til event contract |
| Materials | **3 families produceret** | Claude Unity material/shader implementation |
| Character readability | **P1/P2 hands produceret** | torso source reference er stadig åben |
| A5 utility/release source | **Expanded source set + ending crate produceret** | Unity import/binding/device QA |
| AU-1 feedback | **Generator ready + CI validated** | Claude runtime mix/binding |
| AU-2 natural Foley | **Recording plan ready + wood/cloth packs acquired; ikke approved** | human audition; record where pack fit is insufficient |
| World ambience | **4 direct originals + 2 source packs acquired; ikke listening-approved** | human listening/selection + derived masters only after approval |
| PR #6 env candidates | **28 WAV artifact audited; ikke approved** | PR re-sync + headset/listening QA |
| Radio VO | **Script/queue ready; ikke optaget** | dry source recording |
| Music | **Direction ready; ikke produceret** | composition efter timing evidence |
| Personalization | **Contract + neutral fallback ready** | konkret gaveindhold holdes uden for public repo |

---

# 2. A2 / firepit source

Producerede A2 individual masters:

- `ITM_FIRESTEEL_001`
- `ITM_TINDER_001`
- `ITM_ROPE_COIL_001`
- `PRP_PLAN_TABLE_001`
- `PRP_HEAVY_CRATE_001`
- `PRP_SHELTER_BEAM_001`
- `PRP_SHELTER_ROPE_001`
- `PRP_SHELTER_TARP_001`
- `PRP_SHELTER_FRAME_001`
- `PRP_SIGNAL_FRAME_001`

`PRP_FIREPIT_001` har en project-original low-complexity OBJ source mesh under `source_art/props/a5/`.

Firepit-meshen er en world/fire-state reference med lav stenring og centralt fuel-referenceområde. Den indeholder ingen særskilt strike-zone eller manuel tændingsmekanik.

Det ændrer **ikke** issue #8: PO-044 manual fire-start er fortsat owner-gated og uden for accepted gift scope, indtil Anders træffer en eksplicit disposition.

---

# 3. A3 — storm source

Produceret SVG coverage:

- `VFX_RAIN_001`
- `VFX_WIND_DEBRIS_001`
- `VFX_FIRE_EMBERS_001`
- `VFX_FIRE_SMOKE_001`
- `VFX_ROPE_STRAIN_001`
- `VFX_IMPACT_001`
- `VFX_WETNESS_REFERENCE_001`

Storm-phase sequencing findes desuden i `source_art/vfx/a3/STORM_PHASE_REFERENCE.md`.

Final VFX polish venter Claude/runtime/Quest 2 evidence.

---

# 4. Environment / epilogue

Camp, wreckage, storm-camp, radio og signal source references findes.

Epilog-produktkontrakten er klar i:

- `docs/45_GIFT_EXPERIENCE_AND_RELEASE_FLOW.md`
- `docs/41_PERSONALIZATION_PACKAGE_SPEC.md`
- `docs/42_HUMAN_QA_PLAYTEST_PACK.md`

`ENV_EPILOGUE_001` er canonical som **eksisterende camp efter stormen**, ikke en ny gameplayzone.

`PRP_WATERPROOF_ENDING_CRATE_001` har en project-original OBJ source mesh med separate body/lid/gasket/latches/handles og neutrale hook-slot references. Den indeholder ingen private thumbnails, navne eller gaveindhold; sealed/available/open runtime states og hook-binding er Claude-lane.

Fortsat åbent som senere C-polish, hvis det reducerer implementation ambiguity:

- dedicated post-storm mood/dressing reference

Neutral ending-content er allerede produceret.

---

# 5. B1 / B2

## B1 produced

Environment/readability:

- jungle
- ravine
- ridge
- ravine anchor
- ravine guide markers

Resource/world source:

- wood bundle
- fiber bundle
- herb bundle
- food parcel
- general supplies
- supply crate

## B2 produced + mapped

- animal threat cues
- roof leak
- tool-break presentation
- dry fuel cache
- extra herbs
- distant smoke
- radio fragment presentation

No larger creature-system commitment is implied by the presentation source.

---

# 6. Audio production

## Natural Foley

Use `content/audio/foley_session_reconciliation.source.json`.

Three source sessions remain the recording fallback:

1. heavy/crate
2. rope/tarp
3. shelter/timber

The direct extension acquisition now adds audition material for wood/cloth before recording everything from scratch.

## Canonical acquired originals

- `AMB_WIND_WORLD`
- `AMB_RAIN_ALT`
- `SFX_FIRE_ALT`

Receipt: `content/audio/acquisition_receipt.source.json`.

## Extension acquisition — now actually acquired

- `AMB_OCEAN_ALT` — 4.0 s CC0 FLAC building block
- `SFX_WOOD_PACK_ALT` — CC0 archive with 27 WAVs
- `SFX_CLOTH_PACK_ALT` — Kenney CC0 archive with cloth/creak members

Receipt:

`content/audio/acquisition_extension_receipt.source.json`

Technical member shortlist:

`content/audio/acquisition_extension_member_shortlist.source.json`

Shortlisted internal members include five wood creaks and nine cloth/creak files. Their hashes, codec/sample-rate and duration are pinned.

**Acquired is not approved.**

- ocean still needs creative/loop-fit listening and a derived 48 kHz master if selected
- wood floor/door identity may be wrong for shelter timber
- Kenney cloth/creaks may read too small/game-like for tarp
- archive acquisition does not promote every member to project cue status
- lossy OGG members should not be repeatedly transcoded

The acquisition workflow is reproducible and now probes technical metadata with ffprobe. Raw originals/archives remain outside Git history.

## PR #6 audition pack

Independent audit records:

- 28 WAV candidates
- 28 provenance rows
- 0 missing files
- 0 output-hash mismatches
- status remains `candidate-headset-listen`

PR #6 must re-sync current `main` and regenerate/re-pin physical evidence before merge consideration.

---

# 7. Genuine remaining source-side work

### Can still progress without M0b/M-Pre

1. human audition/selection of acquired natural audio sources
2. real Foley recording only where acquired packs do not meet material/space quality
3. dedicated epilogue mood/dressing reference only if it reduces implementation ambiguity
4. torso source reference as later avatar polish
5. keep machine-readable source inventory synchronized with actual files

### Human-gated

- M-Pre
- OQ-008/OQ-009/OQ-010
- creative/listening approval of natural audio

### Device/Unity-gated

- M0b cross-device
- final world dimensions
- runtime VFX/materials
- spatial mix
- Quest 2 performance/readability

### Owner-gated

- issue #8 manual fire-start scope

---

# 8. Acceptance rule

Do not mark a source batch complete because filenames merely exist.

Source-side completion means:

- required IDs are explicit
- source master/reference actually exists
- provenance is recorded
- scope/gate caveats are explicit
- Claude can consume the handoff without inventing product semantics

Runtime/device/release approval remains a separate lane.
