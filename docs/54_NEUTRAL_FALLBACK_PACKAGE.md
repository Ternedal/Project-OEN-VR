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

Recommended internal profile:

```json
{
  "profileId": "NEUTRAL_DEFAULT",
  "version": 1,
  "fallbackProfileId": "NEUTRAL_DEFAULT",
  "displayNames": ["Spiller 1", "Spiller 2"],
  "textOverrides": {},
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

Suggested neutral contents:

1. weathered maritime chart/card
2. simple compass or rescue marker
3. generic crew/rescue note

No real-world brand/logo required.

---

# 4. Neutral source assets

| Hook | Neutral asset ID | Product intent |
|---|---|---|
| `ENDING_CRATE_PHOTO` | `NEU_ENDING_CHART_001` | stylized chart/rescue-route card |
| `CAMP_MEMENTO_1` | `NEU_MEMENTO_COMPASS_001` | generic compass token/prop |
| `CAMP_MEMENTO_2` | `NEU_MEMENTO_ROUTE_CARD_001` | generic route/weather card |
| `CAMP_MEMENTO_3` | `NEU_MEMENTO_SIGNAL_TAG_001` | generic rescued/signal marker |
| `RADIO_FINAL_MESSAGE` | neutral VO keys | radio rescue acknowledgement |

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

Add/use canonical conceptual key:

`ending.neutral.message`

Suggested Danish source:

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

Neutral source assets follow `docs/43_IP_AND_ASSET_PROVENANCE.md`.

Preferred neutral sources:

- project-original/generated and documented
- no real shipping company logo
- no third-party map scan
- no copyrighted photo used merely because it looks nautical

---

# 11. Production status

## Spec-ready now

- hook mapping
- radio copy
- visual direction
- QA behavior

## Source production still needed

- `NEU_ENDING_CHART_001`
- `NEU_MEMENTO_COMPASS_001`
- `NEU_MEMENTO_ROUTE_CARD_001`
- `NEU_MEMENTO_SIGNAL_TAG_001`
- neutral radio VO recording/source, unless synthetic/other voice strategy selected later

Actual runtime binding remains Claude work.

---

# 12. Acceptance criteria

Neutral fallback is product-complete when:

- zero private files produces a complete finale
- all private hooks have intentional fallback
- no dev/placeholder language appears
- neutral content matches the visual/narrative world
- no private cached content survives incorrectly
- external testers can use neutral build without knowing a personalized variant exists
