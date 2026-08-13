# Music direction & cue sheet — PROJECT ØEN

**Music/product owner:** ChatGPT  
**Runtime adaptive implementation/mix:** Claude  
**Dato:** 2026-08-13

## 1. Musikalsk tese

Musikken skal støtte samarbejde og dramatik uden at dominere samtalen mellem spillerne.

Retning:

- sparsom
- organisk/tekstural
- eventyr og udsathed frem for horror
- varme ved campen
- mere rytmisk/presset under storm
- tydelig release ved signal/rescue

Undgå:

- konstant underscore
- heroisk blockbuster-score
- horror drones der ændrer tonegenre
- stærke melodier der konkurrerer med radio/partner speech
- “victory fanfare” der føles som arkade-score

---

# 2. Instrument-/texture-retning

Mulige source families:

- low wooden/percussive pulses
- muted plucked strings
- soft bowed/air textures
- sparse hand percussion
- warm sustained pad/organic resonance
- low storm pulse built from non-musical/tonal hybrid

No instrument family is mandatory; the important contract is density, warmth and speech space.

---

# 3. Cue architecture

## `MUS_CAMP_BASE_001`

State:

- calm camp/planning

Product intent:

- very sparse
- can disappear completely for long periods
- reinforces safety/partnership, not sentimentality

Source target:

- 60–90 sec seamless/near-seamless bed or layered stems

## `MUS_PLANNING_TENSION_001`

State:

- optional subtle planning layer after Day 1

Intent:

- slight urgency without timer pressure
- never imply there is one “correct” answer

Could be omitted entirely if playtest shows planning works better with only ambience.

## `MUS_NIGHT_REFLECTION_001`

State:

- very short post-consequence / radio breathing space

Intent:

- 10–25 sec bridge, not a full cutscene cue

## `MUS_STORM_BASE_001`

State:

- storm phase 1–2

Intent:

- low pulse + texture
- provides forward movement
- leaves broad midrange room for speech

## `MUS_STORM_PRESSURE_001`

State:

- phase 3–4 additive layer

Intent:

- raises density/rhythm rather than simply volume
- can drop under critical voice/system cue

## `MUS_SIGNAL_FINAL_001`

State:

- phase 5 / signal attempt

Intent:

- strongest directed cue
- still supports player speech
- cadence should remain unresolved until signal acknowledgement

## `MUS_RESCUE_RELEASE_001`

State:

- signal acknowledged / storm begins to break

Intent:

- emotional release
- warm but restrained
- gives players room to look at each other/camp

## `MUS_EPILOGUE_NEUTRAL_001`

State:

- neutral/private epilogue bed

Intent:

- optional, extremely sparse
- private voice/message always primary

---

# 4. Adaptive philosophy

Prefer a small number of reusable layers over many fixed tracks.

Conceptual layers:

- calm/base
- pulse
- pressure texture
- release texture

Claude may implement using stems, snapshots, crossfades or another Unity-appropriate method.

Product contract:

- no audible hard cuts during normal phase transition
- music can intentionally fall away for radio/consequence readability
- storm intensity can rise without covering partner communication

---

# 5. Speech-space requirement

Partner speech is the highest-priority “soundtrack”.

Music source should avoid constant dense energy around the main speech intelligibility band.

This is a source-composition consideration, not only a mixer problem.

---

# 6. Silence as design

Silence/ambience-only is valid and often preferred:

- early exploration
- after a serious consequence
- before radio fragment
- immediately after storm peak

Do not fill every quiet moment because the project has a music system.

---

# 7. Outcome variants

## Strong win

Rescue release can arrive slightly cleaner/warmer.

## Pressed win

Same rescue truth, but allow more residual storm/roughness under release.

## Loss

Avoid sad piano / punishment trope.

Use:

- reduced/held unresolved texture
- causal report/retry clarity

Loss should motivate another plan, not shame the players.

---

# 8. Personalization rule

Private final voice/message may be emotionally significant.

Music under it:

- very low density
- no lyric/voice texture
- no strong melodic cadence over speech
- easy to duck/fade

Neutral and personal endings share the same musical structure.

---

# 9. Source deliverables

When composition begins, source pack should include:

```text
source_audio/music/
  MUS_CAMP_BASE_001.*
  MUS_STORM_BASE_001.*
  MUS_STORM_PRESSURE_001.*
  MUS_SIGNAL_FINAL_001.*
  MUS_RESCUE_RELEASE_001.*
  optional...
  PROVENANCE.md
```

Preferred master:

- 48 kHz WAV
- 24-bit
- stereo unless stems/source strategy suggests otherwise
- clean loop points where looping is intended
- stems preserved if adaptive implementation benefits from them

---

# 10. Music QA

Ask during human test:

- did music ever make partner speech harder to hear?
- did storm music increase pressure without making tasks confusing?
- did signal/rescue feel like a payoff?
- did any cue make the experience feel like a different genre?

Technical mix/ducking measurements remain Claude-owned.

---

# 11. Production status

## Ready

- cue IDs
- dramaturgical roles
- source/mix constraints
- speech-space rule

## Not produced

- actual composition/source masters

Do not mark music complete until source audio exists and has provenance/listening QA.
