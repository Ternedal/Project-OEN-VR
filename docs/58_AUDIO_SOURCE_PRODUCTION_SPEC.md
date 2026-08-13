# Audio source production specification — PROJECT ØEN

**Audio/content owner:** ChatGPT  
**Unity integration/mix:** Claude  
**Dato:** 2026-08-13

## Formål

`docs/39_AUDIO_CUE_MANIFEST.md` definerer cue-ID'er og adfærd. Dette dokument beskriver, hvordan de **naturlige** source-cues bør produceres og QA'es uden at lade proceduralt genererede UI-toner stå i stedet for reel world audio.

---

# 1. Source strategy tiers

## Tier S — synthetic/project-generated

Egnet til:

- UI confirm/warning/error
- planning token feedback
- reconnect motifs

Current source: `source_audio/au1/`.

## Tier R — recorded / Foley

Foretrukket til:

- rope/fiber
- wood impacts/creaks
- crate handling
- cloth/tarp
- firesteel
- small prop handling

## Tier L — licensed library / high-quality generative source

Kan bruges til:

- wind beds
- rain beds
- beach/jungle/ravine ambience
- distant animal cues

Must have provenance/license record.

## Tier V — voice recording / voice generation

- radio narrative
- neutral rescue message
- private finale message

Source strategy must preserve subtitle/copy parity and privacy.

## Tier M — composed music

Music source/composition is separate from ambience and follows `docs/60_MUSIC_DIRECTION_AND_CUE_SHEET.md`.

---

# 2. Master format

Preferred source master:

- WAV
- 48 kHz
- 24-bit where source supports it
- 16-bit acceptable for simple synthesized one-shots
- mono for localized Foley/3D cues
- stereo for ambience/music unless a deliberate spatial source strategy says otherwise

Keep uncompressed master before Unity import/compression.

---

# 3. AU-2 — physical interaction Foley

## Heavy crate

Cue targets:

- `SFX_GRAB_HEAVY_001`
- `SFX_HEAVY_MOVE_001`
- `SFX_HEAVY_PLACE_001`
- `SFX_CRATE_OPEN_001`

Source approach:

- wood box/cabinet/chest with real mass
- layered low wood thump + subtle metal hardware
- avoid cinematic sub-bass that makes every move sound like a shipping container

Variations:

- grab: 3
- move/strain: 4–6 short variants or loop strategy
- place: 4
- lid/open: 3

## Rope/fiber

Cue targets:

- `SFX_ROPE_TENSION_LOW_001`
- `SFX_ROPE_TENSION_GOOD_001`
- `SFX_ROPE_TENSION_HIGH_001`
- `SFX_ROPE_TIE_001`

Source approach:

- coarse natural rope under actual hand tension
- separate scrape/tighten/strain textures
- high tension should feel urgent without sounding like metal cable

## Shelter wood/cloth

- `SFX_SHELTER_CREAK_LOW_001`
- `SFX_SHELTER_CREAK_HIGH_001`
- `SFX_SHELTER_ROPE_FLAP_001`
- `SFX_BEAM_SHIFT_001`
- `SFX_SHELTER_SNAP_SUCCESS_001`

Source approach:

- dry timber flex/door/furniture creak sources can be layered if provenance allows
- tarp = heavy cloth/plasticized fabric, not paper flap
- snap success should be tactile/short, not UI-only

---

# 4. AU-3 — fire

Cue targets:

- `SFX_FIRE_DEAD_001`
- `SFX_FIRE_EMBERS_001`
- `SFX_FIRE_SMALL_001`
- `SFX_FIRE_STRONG_001`
- `SFX_FIRE_FUEL_ADD_001`
- `SFX_FIRE_WET_HISS_001`
- `SFX_FIRE_IGNITION_001`
- `SFX_FIRESTEEL_STRIKE_001`

## Required state separation

### Dead

Nearly silent; ash/material movement only if interacted with.

### Embers

Soft crackle, sparse, intimate.

### Small

Continuous light flame/crackle.

### Strong

Fuller low/mid body, still not bonfire roar.

### Wet

Hiss/sputter layer must communicate danger under rain.

## Loop QA

For ember/small/strong:

- no obvious periodic “signature crack” at loop point
- crossfade/source edit if needed
- loop should tolerate long camp exposure

---

# 5. AU-4 — weather ambience

## Wind L0–L3

Need four perceptually distinct levels that feel like the same weather system.

- L0: calm/light air
- L1: forecastable pressure, occasional gust
- L2: sustained storm wind
- L3: peak/gust pressure

Avoid simply multiplying volume. Variation can include:

- gust density
- frequency balance
- vegetation/structure response

## Rain

At least:

- light rain
- heavy storm rain

Rain bed should not contain recognizable urban roofs/cars/gutters unless intentionally masked; island context matters.

## Zone ambience

- beach/camp
- jungle
- ravine/ridge
- calm night

Each zone should have enough identity to help orientation without becoming a nature-documentary soundscape.

---

# 6. Animal threat

Project does not need a hero creature/monster voice.

Cues:

- distant presence
- approach/rustle
- food disturbance
- retreat

Source intent:

- ambiguous medium animal
- no obvious dog/wolf/monkey signature unless the world design later canonizes that animal
- sound can keep the threat partly off-screen and reduce art/AI scope

---

# 7. Radio source

Radio static/signal cues:

- subtle low static bed
- “signal found” transition
- no constant harsh white noise under dialogue

Voice master stays intelligible and clean; radio treatment is a derived/mix layer, not baked destructively into the only source master.

---

# 8. QA per natural cue

Before source handoff:

- [ ] clean beginning/end or documented loop
- [ ] no accidental speech/background music
- [ ] no clipping
- [ ] no obvious copyrighted melody/content in background
- [ ] cue ID/filename match
- [ ] correct mono/stereo intent
- [ ] provenance/license recorded
- [ ] variations named consistently
- [ ] source master preserved

## Listening QA contexts

Review at:

- headphones
- small speaker / Quest-like playback where possible
- under simulated storm bed

A cue that works solo but disappears under storm is not finished.

---

# 9. Player speech priority

All storm/world source production must leave room for partner communication.

Avoid sources dominated by dense midrange that cannot be ducked cleanly.

Product mix priority:

1. partner speech / critical VO
2. interaction feedback
3. critical state cues
4. ambience/weather
5. music

Actual ducking/mixer logic belongs to Claude.

---

# 10. Production order

1. AU-1 synthetic feedback — generator ready
2. rope/shelter/crate Foley
3. fire state family
4. wind/rain core beds
5. zone ambience
6. radio voice/static
7. animal/event sweeteners
8. music polish/extra variation

This order maximizes usefulness for interaction/storm implementation before decorative polish.

---

# 11. What can be complete before Unity

ChatGPT-side can complete:

- source masters
- cue/variation filenames
- provenance
- loop/source QA
- subtitle/copy alignment

Claude-side remains:

- import compression
- 3D spatialization
- attenuation
- AudioMixer routing
- adaptive state binding
- ducking
- on-device loudness/masking QA
