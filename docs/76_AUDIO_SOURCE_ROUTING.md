# Audio source routing — PROJECT ØEN

**Owner:** ChatGPT  
**Runtime owner:** Claude  
**Machine source:** `content/audio/audio_source_routing.source.json`

## Why this exists

`content/audio/audio_cues.source.json` currently has 35 cues with `productionStatus=needs_source`.

That single status used to hide several very different realities:

- some cues already have a complete physical-recording lane;
- some have exact acquired source candidates awaiting human listening;
- some are derived cues that should not get an independent raw recording;
- some genuinely need a new acquisition/recording plan;
- firesteel is blocked by the owner decision in issue #8.

The routing contract gives every one of the 35 cues exactly one current production/evidence route without pretending any source is approved.

## Current routing shape

| Route | Cues | Meaning |
|---|---:|---|
| Physical Foley session ready | 17 | Current 17-cue / 73-take heavy/rope/shelter/event recording lane |
| Acquired candidate pool | 13 | Exact acquired sources exist; human listening/source approval still required |
| Derived after approved sources | 1 | Partial shelter collapse should be authored from approved shelter/timber sources with documented derivation |
| Physical recording extension pending | 0 | All currently scoped safe event/small-prop Foley is now in the recording queue |
| Source acquisition or recording pending | 2 | Dedicated ignition and wet-fire-hiss source still missing |
| Licensed source acquisition pending | 1 | Ambiguous distant animal-threat source still missing |
| Owner-gated | 1 | Firesteel stays blocked by issue #8 |

Total: **35 needs-source cues, 0 source approvals implied.**

## Four physical-recording extensions now routed

These were former gaps and are now part of the 73-take physical session:

- `SFX_FIRE_FUEL_ADD_001`
- `SFX_ANIMAL_CAMP_APPROACH_001`
- `SFX_ANIMAL_RETREAT_001`
- `SFX_FOOD_DISTURBED_001`

`SFX_FIRE_FUEL_ADD_001` is a storm fire-maintenance cue. It is **not** the owner-gated manual firesteel interaction, so it can receive a safe small-prop recording plan without changing issue #8 scope.

The animal approach/retreat cues should remain ambiguous rustle/ground movement where possible. The project does not need to canonize a hero creature voice merely to fill those slots.

Their route remains `recording-tooling-ready-not-recorded`: adding them to the
queue does not claim that any takes or human approvals exist.

## The three acquisition-oriented gaps

### `SFX_FIRE_IGNITION_001`

Needs a natural ignition/transient source independent of manual firesteel. Acquisition or safe controlled source production is allowed; no risky recording requirement is created.

### `SFX_FIRE_WET_HISS_001`

Prefer provenance-clean licensed/natural wet-fire hiss material or a safely produced equivalent. The routing contract explicitly does not require risky live-fire capture.

### `SFX_ANIMAL_DISTANT_001`

Tier-L licensed acquisition is appropriate. Desired semantic identity is an ambiguous medium-animal distant presence, not an obvious dog/wolf/monkey signature unless product design later canonizes one.

## Existing acquired candidate families

The 13 acquired-pool routes include:

- fire embers/small/strong from `SFX_FIRE_ALT` candidate material;
- wind L0/L1 from `AMB_WIND_WORLD` candidate material;
- wind L2/L3 from the Fisterra source candidate;
- light/heavy rain from `AMB_RAIN_ALT` candidate material;
- beach, jungle, ravine and camp-night ambience from the current acquired field/extension pool.

These mappings are **candidate routes**, not approvals. Human listening may reject a candidate and reopen acquisition.

## Derived shelter collapse

`SFX_SHELTER_COLLAPSE_PARTIAL_001` is routed as a derivative after approved shelter/timber source families rather than requiring a separate arbitrary stock collapse file.

Current dependencies:

- `SFX_SHELTER_CREAK_HIGH_001`
- `SFX_BEAM_SHIFT_001`

Any composite/edit must use the existing derived-master recipe + technical + repeated-human-listening gate.

## Fire-start boundary

Only `SFX_FIRESTEEL_STRIKE_001` is `owner-gated` in the current source-routing matrix.

It remains bound to:

`content/contracts/issue8.reconciliation.source.json`

Do not broaden that owner gate to normal fire maintenance cues, and do not narrow it by silently recording/implementing firesteel interaction audio before Anders decides issue #8.

## Validation

Run:

```bash
python tools/validate_audio_source_routing.py
```

The validator checks:

- exactly 35 current `needs_source` cues;
- exactly one route per cue;
- physical-Foley routes exactly equal the current 17-cue recording queue;
- acquired candidate targets exist in committed acquisition receipts;
- extension/pending/licensed/derived/owner route sets do not drift;
- firesteel is the only current owner-gated audio source cue;
- no route or summary claims source approval.

This routing matrix is the preferred starting point for future source acquisition/recording work. Do not use a broad code search for `needs_source` and then invent a second production lane for a cue that is already routed.
