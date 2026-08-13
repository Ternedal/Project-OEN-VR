# Neutral fallback package — PROJECT ØEN

**Ejer:** ChatGPT  
**Dato:** 2026-08-13  
**Formål:** Gøre neutral build til et komplet produkt, ikke en personalization-build med manglende filer

## 1. Grundregel

Neutral fallback er canonical baseline.

Private personalization må erstatte enkelte hooks, men hvis hele private pakken mangler, skal spilleren aldrig se:

- placeholder paths
- “TODO”
- tomme frames
- dev errors
- generiske missing-asset ikoner
- uafsluttet finale

---

# 2. Neutral profile contract

Machine-readable source profile findes i:

`content/personalization/neutral_profile.source.json`

Conceptual content:

```json
{
  "profileId": "NEUTRAL_DEFAULT",
  "version": 1,
  "fallbackProfileId": "NEUTRAL_DEFAULT",
  "displayNames": ["Spiller 1", "Spiller 2"],
  "textOverrides": {
    "ending.neutral.message": "I holdt længe nok. Signalet blev set."
  },
  "imageAssets": [],
  "audioAssets": [],
  "finalMessageKey": "ending.neutral.message",
  "propHooks": []
}
```

The exact runtime profile representation belongs to Claude; product semantics are fixed here.

---

# 3. Neutral ending content

## Radio

Use source lines:

- `vo.radio.ending.neutral.01` — “Signal observeret.”
- `vo.radio.ending.neutral.02` — “Bliv ved kysten. Vi har jeres position.”
- `vo.radio.ending.neutral.03` — “Hold ud lidt endnu.”

These lines resolve the game before any private overlay.

## Ending crate

Neutral crate contains a small set of coherent island/rescue objects rather than empty slots.

Produced source assets:

1. `NEU_ENDING_CHART_001` — fictional island/rescue route card
2. `NEU_MEMENTO_COMPASS_001` — generic compass memento
3. `NEU_MEMENTO_ROUTE_CARD_001` — fictional route/weather card
4. `NEU_MEMENTO_SIGNAL_TAG_001` — generic signal/rescue tag

Source masters: `source_art/neutral/`.

No real-world brand/logo/map is required.

---

# 4. Neutral source assets

| Hook | Neutral asset ID | Product intent | Source status |
|---|---|---|---|
| `ENDING_CRATE_PHOTO` | `NEU_ENDING_CHART_001` | stylized chart/rescue-route card | **SVG produced** |
| `CAMP_MEMENTO_1` | `NEU_MEMENTO_COMPASS_001` | generic compass token/prop | **SVG produced** |
| `CAMP_MEMENTO_2` | `NEU_MEMENTO_ROUTE_CARD_001` | generic route/weather card | **SVG produced** |
| `CAMP_MEMENTO_3` | `NEU_MEMENTO_SIGNAL_TAG_001` | generic rescued/signal marker | **SVG produced** |
| `RADIO_FINAL_MESSAGE` | neutral VO keys | radio rescue acknowledgement | source copy ready; recording/source audio pending |

These IDs are source-side identifiers. Claude decides actual Unity asset references.

---

# 5. Neutral visual direction

Neutral content must feel intentional and part of the island art style:

- weathered utility paper/card
- hand-marked maritime symbols
- warm post-storm light
- no modern corporate branding
- no text requiring tiny reading distance

The neutral ending should feel like a genuine small epilogue even if the player never knows personalization exists.

---

# 6. Neutral final message key

Canonical conceptual key:

`ending.neutral.message`

Danish source:

> I holdt længe nok. Signalet blev set.

This is optional on-screen epilogue text; the radio lines remain the primary canonical rescue confirmation.

---

# 7. Neutral after-action

After neutral epilogue:

- same outcome headings
- same causal report
- same retry/replay options

No private-content absence should change the after-action structure.

---

# 8. Missing/invalid private content behavior

If a private hook fails:

1. log only hook ID + neutral error classification
2. bind neutral fallback
3. continue without modal error unless the failure prevents a complete experience

Player-facing error is only needed if the private package was explicitly expected and the tester/developer needs to know.

Normal gift release should prefer graceful fallback.

---

# 9. Neutral QA matrix

| Test | Expected |
|---|---|
| no private folder | complete neutral game |
| missing photo only | neutral chart/card appears |
| corrupt photo | neutral chart/card appears |
| missing final audio | neutral radio lines play/show subtitles |
| missing memento | neutral memento occupies intended slot or slot is intentionally composed away |
| invalid text override | canonical Danish copy used |
| private package removed after previous run | no stale private thumbnail/cache visible |

---

# 10. Provenance

Neutral source assets are class `OWN` and documented in:

`source_art/neutral/PROVENANCE.md`

They were rendered/reviewed as a coherent set after production.

---

# 11. Production status

## Done on ChatGPT source-side

- hook mapping
- radio copy
- visual direction
- QA behavior
- neutral profile source
- four neutral SVG source assets
- provenance record

## Still needed

- neutral radio VO recording/source, unless a later voice strategy changes this
- Claude runtime binding/fallback
- M8 E2E neutral build test

---

# 12. Acceptance criteria

Neutral fallback is product-complete when:

- zero private files produces a complete finale
- all private hooks have intentional fallback
- no dev/placeholder language appears
- neutral content matches the visual/narrative world
- no private cached content survives incorrectly
- external testers can use neutral build without knowing a personalized variant exists
