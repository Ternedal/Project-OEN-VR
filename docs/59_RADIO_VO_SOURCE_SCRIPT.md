# Radio VO source script — PROJECT ØEN

**Narrative/audio owner:** ChatGPT  
**Runtime treatment:** Claude  
**Dato:** 2026-08-13  
**Language:** Danish source

## Formål

Give radio voice a complete source script, delivery direction and file plan without hardcoding a specific voice provider or Unity treatment.

Radio is functional external communication — not narrator/tutorial voice.

---

# Voice profile

Preferred delivery:

- calm professional maritime/operations voice
- gender-neutral choice acceptable
- natural Danish
- restrained urgency
- not theatrical
- no “game master” warmth or sarcasm
- short clipped phrases with believable signal gaps

Do not imitate a recognizable real broadcaster/person.

## Recording rule

Record/generate clean dry voice first.

Radio EQ/static/dropouts are derived treatment. Never keep only a heavily degraded master.

---

# Night 1

## `VO_RADIO_NIGHT1_01`

Localization key: `vo.radio.night1.01`

> …til alle fartøjer i området…

Delivery:

- begins as if middle of a longer broadcast
- neutral, low urgency

## `VO_RADIO_NIGHT1_02`

Key: `vo.radio.night1.02`

> …ruten langs øgruppen genoptages om cirka to døgn…

Delivery:

- clearest line in the fragment
- the critical information must survive radio treatment

## `VO_RADIO_NIGHT1_03`

Key: `vo.radio.night1.03`

> …hold kanalen fri…

Delivery:

- fades/fragments toward end

## Intended takeaway

Players understand:

- a route is active in roughly two days
- this is an opportunity, not guaranteed rescue

The radio does not say “build a signal now.”

---

# Day 3

## `VO_RADIO_DAY3_01`

Key: `vo.radio.day3.01`

> …ruten er bekræftet. Passage ved daggry…

Delivery:

- clear
- slightly more operational urgency

## `VO_RADIO_DAY3_02`

Key: `vo.radio.day3.02`

> …sigtbarheden bliver dårlig under fronten…

Delivery:

- important weather consequence, not dramatic acting

## `VO_RADIO_DAY3_03`

Key: `vo.radio.day3.03`

> …visuelt signal anbefales…

Delivery:

- clearest final phrase

## Intended takeaway

Players now know:

- exact passage timing
- visual signal is necessary
- weather reduces visibility

This enables deliberate Day 3 tradeoff without revealing numeric win thresholds.

---

# Neutral ending

## `VO_RADIO_END_NEUTRAL_01`

Key: `vo.radio.ending.neutral.01`

> Signal observeret.

Delivery:

- immediate confirmation
- short and unmistakable

## `VO_RADIO_END_NEUTRAL_02`

Key: `vo.radio.ending.neutral.02`

> Bliv ved kysten. Vi har jeres position.

Delivery:

- calm reassurance
- no melodrama

## `VO_RADIO_END_NEUTRAL_03`

Key: `vo.radio.ending.neutral.03`

> Hold ud lidt endnu.

Delivery:

- slight warmth is acceptable
- still professional radio tone

## Narrative ordering

Neutral rescue acknowledgement plays **before** any private gift message.

This keeps personalization as an overlay and preserves a fully resolved neutral game story.

---

# File plan

Preferred dry masters:

```text
source_audio/radio/
  VO_RADIO_NIGHT1_01.wav
  VO_RADIO_NIGHT1_02.wav
  VO_RADIO_NIGHT1_03.wav
  VO_RADIO_DAY3_01.wav
  VO_RADIO_DAY3_02.wav
  VO_RADIO_DAY3_03.wav
  VO_RADIO_END_NEUTRAL_01.wav
  VO_RADIO_END_NEUTRAL_02.wav
  VO_RADIO_END_NEUTRAL_03.wav
```

Source spec:

- 48 kHz WAV
- mono preferred for dry voice
- 24-bit where available
- clean background
- around 0.25–0.6 s silence/headroom before/after can be trimmed in derived production

---

# Radio treatment reference

Derived treatment may include:

- gentle high/low-pass band-limiting
- subtle static
- short dropout between fragments
- level fluctuation

Do not:

- destroy consonant intelligibility
- mask critical timing phrases
- make every line sound like a horror transmission

Static bed cue IDs remain separate so the mix can reduce static under important speech.

---

# Subtitle parity

Subtitle must match semantic content exactly.

Small natural spoken contractions are okay only if localization source is updated correspondingly.

Do not add unscripted critical information in recording.

---

# Voice source provenance

When a voice source is selected, record:

- human performer / service / model
- permission/license
- date/version
- whether commercial/public reuse would be allowed if project scope changes

No cloned/imitated identifiable public-person voice.

---

# QA

Before handoff:

- [ ] all 9 lines produced
- [ ] clean dry masters preserved
- [ ] Danish pronunciation reviewed
- [ ] subtitle/source parity exact
- [ ] radio-treated preview remains intelligible
- [ ] Night 1 does not reveal Day 3 strategy too early
- [ ] ending line order matches narrative continuity
- [ ] provenance recorded

Runtime spatial/treatment/mixer implementation remains Claude-owned.
