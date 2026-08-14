# Audio cue manifest — PROJECT ØEN

**Ejer af audio direction/source:** ChatGPT  
**Unity-integration/mix:** Claude  
**Dato:** 2026-08-13

## Formål

Dette dokument gør lydsiden produktionsklar uden at blande source audio og Unity-implementation sammen.

ChatGPT leverer/definerer:

- cue-ID
- betydning
- dramaturgisk funktion
- source master/fallback
- loop/one-shot-intention
- prioritet
- variation
- accessibility-paritet

Claude ejer:

- `AudioSource`/Mixer
- spatialization
- attenuation curves
- runtime compression/import
- voice stealing
- ducking
- device-mix/performance

## Source master-regel

Anbefalet source-master før Unity-import:

- WAV, 48 kHz
- 24-bit hvis source produceres i høj kvalitet; 16-bit accepteres for simple SFX
- mono for lokale 3D one-shots, medmindre cueet kræver stereo
- stereo for ikke-spatial musik/ambience beds hvor det giver mening
- loop masters skal have dokumenteret seamless loop point
- ingen final loudness-normalisering må erstatte Unity/device-mix

Runtime codec/compression bestemmes af Claude.

## Canonical machine-ID rule

Machine runtime binding IDs come from `content/audio/audio_cues.source.json`. Rows in this human manifest that are absent from the machine registry remain **source/design specs only** and must not be bound under invented runtime IDs. `content/audio/audio_cue_alias_reconciliation.source.json` records retired aliases.

---

# Prioritet

- **A:** release 1 / M5
- **B:** full Stormnatten / M6
- **C:** polish / M7+
- **P:** private personalization / M8

---

# Ambience — zones

| ID | Zone | Type | Pri. | Funktion | Variation/fallback | Status |
|---|---|---|---:|---|---|---|
| `SFX_AMB_BEACH_CAMP_001` | Strand/camp | loop | A | Base island ambience | surf + light wind; neutral fallback | Spec klar |
| `SFX_AMB_CAMP_NIGHT_001` | Camp/night | loop | B | Nat, sårbarhed | insects/surf/light creaks | Spec klar |
| `SFX_AMB_JUNGLE_001` | Jungle | loop | B | Exploration identity | foliage/insects/birds | Spec klar |
| `SFX_AMB_RAVINE_001` | Ravine | loop | B | Height/depth tension | wind/stone/echo | Spec klar |
| `SFX_AMB_RIDGE_001` | Ridge | loop | B | Exposure + ship route | stronger open wind | Spec klar |
| `SFX_AMB_POST_STORM_001` | Epilogue | loop | A | Release/tension drop | reduced wind, surf, sparse birds | Spec klar |

---

# Weather layers

| ID | Cue | Type | Pri. | State | Accessibility pair | Status |
|---|---|---|---:|---|---|---|
| `SFX_WIND_L0_001` | Light wind | loop layer | A | calm | cloth/foliage visual motion | Spec klar |
| `SFX_WIND_L1_001` | Building wind | loop layer | A | warning | stronger VFX + forecast cues | Spec klar |
| `SFX_WIND_L2_001` | Storm wind | loop layer | A | storm 1 | debris/VFX intensity | Spec klar |
| `SFX_WIND_L3_001` | Peak wind | loop layer | A | collapse risk | camera-safe world VFX + structure cues | Spec klar |
| `SFX_RAIN_LIGHT_001` | Light rain | loop layer | B | night/weather | visible droplets/wetness | Spec klar |
| `SFX_RAIN_L2_001` | Heavy rain | loop layer | A | storm 2 | rain VFX + wetness | Spec klar |
| `SFX_THUNDER_DISTANT_001` | Distant thunder | one-shot set | B | warning | sky flash optional; never sole information | Spec klar |
| `SFX_THUNDER_NEAR_001` | Near thunder | one-shot set | C | drama | flash + environmental response | Spec klar |

---

# Fire state

Fire audio is gameplay information. Every state must have a readable visual state as well.

| ID | State | Type | Pri. | Meaning | Status |
|---|---|---|---:|---|---|
| `SFX_FIRE_DEAD_001` | dead | sparse one-shot/bed | A | No useful flame | Spec klar |
| `SFX_FIRE_EMBERS_001` | embers | loop | A | Recoverable fire | Spec klar |
| `SFX_FIRE_SMALL_001` | small | loop | A | Weak but active | Spec klar |
| `SFX_FIRE_STRONG_001` | strong | loop | A | Stable camp/fire | Spec klar |
| `SFX_FIRE_WET_HISS_001` | wet impact | one-shot variants | A | Rain/water harming fire | Spec klar |
| `SFX_FIRE_FUEL_ADD_001` | fuel add | one-shot variants | A | Successful action feedback | Spec klar |
| `SFX_FIRE_IGNITION_001` | ignition | one-shot | A | Fire-start success | Spec klar |

---

# Shelter / structure feedback

| ID | Cue | Type | Pri. | Gameplay meaning | Status |
|---|---|---|---:|---|---|
| `SFX_SHELTER_CREAK_LOW_001` | light creak | loop/oneshots | A | Stable but loaded | Spec klar |
| `SFX_SHELTER_CREAK_HIGH_001` | stressed creak | loop/oneshots | A | Structure under threat | Spec klar |
| `SFX_SHELTER_ROPE_FLAP_001` | loose tarp/rope | loop/oneshots | A | Repair needed | Spec klar |
| `SFX_SHELTER_TEAR_001` | tarp tear | one-shot | A | Damage event | Spec klar |
| `SFX_BEAM_SHIFT_001` | beam shift | one-shot | A | Stability loss | Spec klar |
| `SFX_SHELTER_SNAP_SUCCESS_001` | repair/snap confirm | one-shot | A | Successful placement | Spec klar |
| `SFX_SHELTER_COLLAPSE_PARTIAL_001` | partial collapse | staged one-shot | A | Storm phase 4 | Spec klar |

---

# Rope / coop interaction feedback

| ID | Cue | Type | Pri. | Function | Status |
|---|---|---|---:|---|---|
| `SFX_ROPE_TENSION_LOW_001` | low tension | loop reactive | A | safe/loose | Spec klar |
| `SFX_ROPE_TENSION_GOOD_001` | good tension | loop reactive | A | target zone | Spec klar |
| `SFX_ROPE_TENSION_HIGH_001` | strained fibers | loop reactive | A | near failure | Spec klar |
| `SFX_ROPE_TIE_001` | knot/tie confirm | one-shot variants | A | successful bind | Spec klar |
| `SFX_GRAB_HEAVY_001` | heavy grip | one-shot | A | shared object engaged | Spec klar |
| `SFX_HEAVY_MOVE_001` | crate/beam movement | loop reactive | A | physical weight | Spec klar |
| `SFX_HEAVY_PLACE_001` | heavy placement | one-shot | A | placement confirm | Spec klar |

---

# Planning / effort system

| ID | Cue | Type | Pri. | Meaning | Status |
|---|---|---|---:|---|---|
| `SFX_MARKER_PICKUP_001` | effort marker pickup | one-shot | A | token interaction | Spec klar |
| `SFX_MARKER_PLACE_001` | marker placed | one-shot | A | tentative allocation | Spec klar |
| `SFX_MARKER_MOVE_001` | marker moved | one-shot | A | changed mind | Spec klar |
| `SFX_PLAN_READY_001` | plan ready | one-shot | A | all markers allocated | Spec klar |
| `SFX_PLAN_LOCK_001` | plan locked | one-shot | A | decision committed | Spec klar |
| `SFX_PLAN_CONFLICT_001` | invalid/race feedback | one-shot | A | plan could not lock | Spec klar |

No cue may pressure players into confirming faster. Planning audio should feel tactile, not timer-like.

---

# Tool / item feedback

| ID | Cue | Type | Pri. | Status |
|---|---|---|---:|---|
| `SFX_FIRESTEEL_STRIKE_001` | strike variants | one-shot set | A | Spec klar |
| `SFX_TOOL_WOOD_HIT_001` | wood impact | one-shot set | B | Spec klar |
| `SFX_TOOL_ROCK_HIT_001` | rock impact | one-shot set | C | Spec klar |
| `SFX_CLOTH_HANDLE_001` | tarp/cloth handling | one-shot set | A | Spec klar |
| `SFX_CRATE_OPEN_001` | crate open | one-shot | A | Spec klar |
| `SFX_RADIO_SWITCH_001` | radio control | one-shot | A | Spec klar |
| `SFX_ITEM_RETURN_001` | critical item reset/return | one-shot | B | Spec klar |

---

# Animal/threat cues

MVP has no combat focus. Threat is primarily communicated through presence, reaction and consequence.

| ID | Cue | Type | Pri. | Meaning | Status |
|---|---|---|---:|---|---|
| `SFX_ANIMAL_DISTANT_001` | distant rustle/call | one-shot set | B | anticipation | Spec klar |
| `SFX_ANIMAL_CAMP_APPROACH_001` | approach/rustle | staged set | B | scent consequence | Spec klar |
| `SFX_ANIMAL_RETREAT_001` | retreat | one-shot | B | successfully deterred | Spec klar |
| `SFX_FOOD_DISTURBED_001` | food/container disturbance | one-shot | B | camp consequence | Spec klar |

Animal identity should remain abstract enough that audio does not promise a complex AI creature system.

---

# Radio / narrative cues

| ID | Cue | Type | Pri. | Content status | Notes |
|---|---|---|---:|---|---|
| `SFX_RADIO_STATIC_LOW_001` | weak static | loop | A | Spec klar | intro/radio dead-ish state |
| `SFX_RADIO_SIGNAL_FOUND_001` | signal acquisition | one-shot | A | Spec klar | visual meter pair |
| `VO_RADIO_NIGHT1_001` | first fragment | voice | B | Copy catalog needed | reveals ship in two days |
| `VO_RADIO_DAY3_001` | route confirmation | voice | B | Copy catalog needed | confirms final window |
| `VO_RADIO_NEUTRAL_END_001` | neutral rescue ending | voice | A | Copy catalog needed | fallback finale |
| `VO_RADIO_PERSONAL_END_001` | personal message hook | voice/private | P | Private package | never in repo |

---

# Onboarding / interaction assistance

Important information should prefer world/visual feedback over narrator chatter.

| ID | Cue | Pri. | Function | Status |
|---|---:|---|---|---|
| `SFX_HINT_SOFT_001` | B | gentle hint available | Spec klar |
| `SFX_INTERACTION_AVAILABLE_001` | B | readable affordance | Spec klar |
| `SFX_CONFIRM_001` | A | generic confirmed action | Spec klar |
| `SFX_WARNING_001` | A | generic warning paired with shape | Spec klar |
| `SFX_ERROR_SOFT_001` | A | invalid action, non-punitive | Spec klar |

---

# Music system — source layers

Minimal and adaptive. Music must not become a constant score that masks communication.

| ID | Layer | Pri. | Trigger intention | Status |
|---|---|---:|---|---|
| `MUS_CAMP_BASE_001` | warm camp texture | C | safe planning/rest | Spec klar |
| `MUS_WARNING_PULSE_001` | low pulse | B | approaching storm | Spec klar |
| `MUS_STORM_BASE_001` | storm base | A | storm starts | Spec klar |
| `MUS_STORM_PRESSURE_001` | pressure layer | A | camp state worsens | Spec klar |
| `MUS_SIGNAL_FINAL_001` | final tension | A | signal window | Spec klar |
| `MUS_RESCUE_RELEASE_001` | resolution layer | A | signal succeeds | Spec klar |
| `MUS_LOSS_RELEASE_001` | quiet loss resolution | B | loss/retry | Spec klar |

Rules:

- no musical stinger may obscure player speech during planning
- failure music must not shame the players
- successful signal opens the music rather than blasting a victory fanfare instantly

---

# UI / non-diegetic state audio

| ID | Cue | Pri. | Status |
|---|---|---:|---|
| `UIA_JOIN_CODE_ENTER_001` | code character input | A | Spec klar |
| `UIA_JOIN_SUCCESS_001` | peer joined | A | Spec klar |
| `UIA_READY_001` | player ready | A | Spec klar |
| `UIA_RECONNECT_START_001` | connection lost/recovery starts | A | Spec klar |
| `UIA_RECONNECT_SUCCESS_001` | recovery complete | A | Spec klar |
| `UIA_CHECKPOINT_001` | checkpoint saved | B | Spec klar |
| `UIA_PAUSE_001` | shared pause accepted | B | Spec klar |

---

# Finale audio sequence contract

## Strong/pressed win

1. storm layer decays
2. signal fire/audio rises
3. distant acknowledgement cue or radio response
4. rescue music opens
5. optional ending crate/radio interaction
6. neutral or private final message
7. music resolves without locking player movement for long

## Loss

1. immediate danger audio resolves
2. score reduces rather than dramatizing punishment
3. clear diegetic explanation cue where possible
4. retry prompt is UI/copy, not voice-only

---

# Accessibility rule

Every gameplay-critical audio cue must have at least one non-audio equivalent:

- visual state
- shape/icon
- animation
- haptic cue where appropriate
- text/subtitle for voice

Examples:

- high rope tension → sound + visible guide/state
- weak fire → sound + ember/flame state
- shelter near failure → creak + movement/damage cue
- radio message → voice + subtitle

---

# Source production checklist

A source cue is ready for Claude when:

1. cue ID is final
2. function/state is explicit
3. source file has no clipped peaks or accidental silence
4. loop is clean where applicable
5. variation count is documented
6. intended mono/stereo source is clear
7. private/provenance status is known
8. corresponding visual/text fallback is identified
9. filename matches cue ID
10. Unity runtime behavior is not baked into undocumented editing tricks

---

# Production order

When production is authorized:

1. **A core feedback:** fire, rope, heavy object, marker, plan, shelter, radio, reconnect.
2. **A storm:** wind/rain layers, structure stress, collapse, signal, minimal music.
3. **B scenario:** zones, animal threat, radio narrative, ravine.
4. **C polish:** richer ambience, extra tool impacts, avatar/environment detail.
5. **P private:** final personal message — outside repository.