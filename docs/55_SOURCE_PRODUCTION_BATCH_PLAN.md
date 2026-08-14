# Source production control — PROJECT ØEN

**Ejer:** ChatGPT  
**Unity integration:** Claude  
**Dato:** 2026-08-14  
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
| A2 core props | **17 UV-mapped production meshes + references produceret** | Claude import/representation; PO-044 manual fire-start er stadig owner-gated |
| A3 storm VFX | **7 deterministic production PNG sprites + references** | Claude runtime VFX/performance tuning |
| A4 camp | **3 environment production meshes + 5 PNG sources** | Claude world/material assembly og device QA |
| B1 environment | **5 environment/interaction production meshes + 5 PNG sources** | Claude world implementation |
| B1 resource set | **6 UV-mapped production item meshes** | Claude runtime handoff/device QA |
| B2 event presentation | **7 masters produceret + mapped** | Claude binding til event contract |
| Materials | **3 families produceret** | Claude Unity material/shader implementation |
| Character readability | **P1/P2 hands + neutral torso production meshes produceret** | Claude runtime representation/device QA |
| A5 utility/release source | **5 item + 5 prop UV-mapped production meshes** | Unity import/binding/device QA |
| C1 epilogue | **Reuse-first post-storm production overlay + reference produceret** | Claude ending-state assembly/light/weather/device QA |
| AU-1 feedback | **12 production WAV masters committed + deterministically CI validated** | Claude runtime mix/binding |
| AU-2 natural Foley | **Recording plan + acquired wood/cloth source packs** | human audition; record/edit/master where pack fit is insufficient |
| World ambience | **Core + ocean extension originals acquired; ikke listening-approved** | human listening/source selection |
| PR #6 env candidates | **28 WAV artifact audited; ikke approved** | PR re-sync + headset/listening QA |
| Radio VO | **Script/queue ready; ikke optaget** | dry source recording |
| Music | **14 deterministic candidates produceret/auditeret; ikke human-selected** | human audition og 5 canonical family selections |
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

Alle ti individual masters har nu konkret OBJ/MTL-handoff, og Camp-familien har fjorten yderligere production meshes under `source_art/props/a2/production/`. `PRP_FIREPIT_001` findes også som project-original UV-mapped A5 source.

Firepit-meshen er en world/fire-state reference med lav stenring og centralt fuel-referenceområde. Den indeholder ingen særskilt strike-zone eller manuel tændingsmekanik.

Det ændrer **ikke** issue #8: PO-044 manual fire-start er fortsat owner-gated og uden for accepted gift scope, indtil Anders træffer en eksplicit disposition.

---

# 3. A3 — storm source

Produceret SVG coverage plus matchende deterministic PNG production sprites:

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

Camp, wreckage, storm-camp, radio og signal har konkrete OBJ/MTL production sources; references er bevaret som art-direction records.

Epilog-produktkontrakten er klar i:

- `docs/45_GIFT_EXPERIENCE_AND_RELEASE_FLOW.md`
- `docs/41_PERSONALIZATION_PACKAGE_SPEC.md`
- `docs/42_HUMAN_QA_PLAYTEST_PACK.md`

`ENV_EPILOGUE_001` er canonical som **eksisterende camp efter stormen**, ikke en ny gameplayzone.

`PRP_WATERPROOF_ENDING_CRATE_001` har nu en project-original OBJ source mesh med separate body/lid/gasket/latches/handles og neutrale hook-slot references. Den indeholder ingen private thumbnails, navne eller gaveindhold; sealed/available/open runtime states og hook-binding er Claude-lane.

Dedicated post-storm mood/dressing reference er bevaret som `source_art/environment/c1/ENV_EPILOGUE_001.svg`, og den konkrete reuse-first overlay findes som `ENV_EPILOGUE_001.obj/.mtl` med camp footprint, receding wetness, dawn sightline, signal causality og ending-crate socket.

Neutral ending-content er allerede produceret; final lighting/weather/material implementation remains Claude-lane.

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
- utility/fiber knife source master

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

Three source sessions:

1. heavy/crate
2. rope/tarp
3. shelter/timber

Wood/cloth extension packs are acquired and technically shortlisted. Human audition still decides whether individual members are usable; recording remains the fallback where pack fit is insufficient.

## Acquired ambience originals

Canonical originals:

- `AMB_WIND_WORLD`
- `AMB_RAIN_ALT`
- `SFX_FIRE_ALT`

Extension acquisition:

- `AMB_OCEAN_ALT`
- `SFX_WOOD_PACK_ALT`
- `SFX_CLOTH_PACK_ALT`

Receipts:

- `content/audio/acquisition_receipt.source.json`
- `content/audio/acquisition_extension_receipt.source.json`
- `content/audio/acquisition_extension_member_shortlist.source.json`

They are acquired and technically QA'ed/shortlisted, **not listening-approved**. No acquired original or archive member is promoted to source-approved solely because acquisition succeeded.

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

1. natural audio recording/listening coordination and human source selection
2. keep machine-readable source inventory synchronized with actual files

Automatable repo-side source gaps for utility tool, torso and epilogue reference are closed by this batch; this does **not** close human/audio or Unity/device gates.

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
