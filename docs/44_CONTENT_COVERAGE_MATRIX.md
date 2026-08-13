# Content coverage matrix — STORMNATTEN

**Ejer:** ChatGPT  
**Unity-handoff:** Claude  
**Dato:** 2026-08-13  
**Scenario:** `SCN_STORMNATTEN_001`

## Formål

Dette dokument forbinder produkt-/content-siden med Unity-siden.

For hvert releasekritisk beat viser matrixen:

**beat → player experience → interaction → state/event → source assets → audio → UI/copy → human test → Claude-handoff**

Hvis en række ikke har alle nødvendige kolonner dækket, er beatet ikke produktionsklart.

---

# Statuskoder

- `READY-SPEC`: ChatGPT-specifikation findes; source production kan mangle.
- `NEEDS-SOURCE`: konkret source asset/audio/copy mangler.
- `NEEDS-EVIDENCE`: menneske-/gate-resultat mangler.
- `UNITY`: implementering/verification tilhører Claude.
- `DEFER`: ikke releasekritisk nu.

---

# 1. Intro — Vraget

| Felt | Dækning |
|---|---|
| Beat | Spillerne vågner, finder hinanden og frigør tung kasse |
| Player experience | “Vi er strandet sammen, og allerede første problem kræver begge.” |
| Interaction | look/point → teleport → grab → shared heavy lift → place/open crate |
| Logical IDs | `PRP_HEAVY_CRATE_001`; intro-flow ikke fuldt repræsenteret som action i scenario JSON endnu |
| State/event | tutorial progression; no hard fail |
| Source assets | vrag, heavy crate, cloth, firesteel, map fragment, radio |
| Audio | beach ambience, heavy grab/move/place, crate open, radio static |
| Copy | `hint.look_partner`, `hint.teleport`, `hint.heavy_need_two`, `hint.heavy_coordinate`, `hint.open_crate` |
| Accessibility | grab/placement feedback må være visuel + audio/haptic; no color-only |
| Human test | M1 interaction + M6 onboarding; mål forstået <4 min |
| Claude handoff | build interaction chain, critical-object reset, runtime feedback |
| Status | `READY-SPEC` / source assets `NEEDS-SOURCE` / Unity `UNITY` |

**Gap:** Intro/tutorial er dramaturgisk specificeret, men scenario JSON har tom `INTRO.actions`. Det kan være korrekt, hvis introen drives særskilt; kontrakten skal gøres eksplicit før M3/M6 for at undgå skjult specialkode.

---

# 2. Første ild

| Felt | Dækning |
|---|---|
| Beat | Ilden etableres og bliver campens fælles statuspunkt |
| Player experience | Koordination uden tidsstress; første tydelige rollefordeling |
| Interaction | én skærmer tinder/flamme, én bruger firesteel, derefter fuel |
| Backlog | `PO-044` fire-start interaction (deferred i nuværende scope) |
| State | `fireStrength`; fail-forward til embers/weak fire |
| Assets | `PRP_FIREPIT_001`, `ITM_FIRESTEEL_001`, `ITM_TINDER_001`, `PRP_WIND_SHIELD_001`, wood/fuel |
| Audio | firesteel strikes, ignition, ember/small/strong states, fuel add |
| Copy | `hint.fire.*` |
| Human test | M1/M3/M6; ingen spiller passiv >20s |
| Claude handoff | interaction implementation + state visualization/audio binding |
| Status | design `READY-SPEC`; Unity/content scope `DEFER/UNITY` |

**Gap:** Fire-start er central i scenario-biblen men backloggens implementation er deferred. Hvis introen skal lære den i gaveversionen, scope skal senere reconcile med P1-selection.

---

# 3. Dag 1 planning

| Felt | Dækning |
|---|---|
| Beat | Første reelle prioritering med fire effort markers |
| Player experience | “Vi kan ikke nå alt; hvad er vigtigst?” |
| Interaction | fysisk marker pickup/place/move/lock |
| Logical actions | gather wood, find food, build shelter, explore cliff, secure supplies |
| State | plan revision + marker allocation |
| Assets | plan table, effort markers, action cards/icons |
| Audio | marker pickup/place/move, plan ready/lock/conflict |
| Copy | planning keys + action names/descriptions |
| Human test | **M-Pre issue #7** før M1; M3 VR revalidation |
| Claude handoff | Unity planning table/replication only after M-Pre + M0b green |
| Status | spec `READY-SPEC`; core hypothesis `NEEDS-EVIDENCE` |

**Critical gate:** M-Pre decides whether the planning mechanic survives as-is.

---

# 4. Dag 1 actions

## Gather wood

| Felt | Dækning |
|---|---|
| Player roles | carry / clear path |
| Assets | wood bundle, path obstacles, camp storage |
| Audio | wood handling/heavy movement |
| Copy | `action.gather_wood.*` |
| State | resource/camp effect; numeric values are placeholders until M3 |
| Test | M3 action readability + both active |
| Status | content shape `READY-SPEC`; detailed interaction brief missing |

## Find food

| Felt | Dækning |
|---|---|
| Player roles | forage / spot |
| Assets | food parcel/gathering props |
| Audio | jungle/forage feedback |
| Copy | `action.find_food.*` |
| State | food security + potential `SCENT_HIGH` path |
| Test | M3/M4 causality |
| Status | needs detailed interaction brief |

## Build shelter

| Felt | Dækning |
|---|---|
| Player roles | place beam / tie rope |
| Assets | shelter frame/tarp/beam/rope |
| Audio | rope tension, tie, beam move, snap success |
| Copy | `action.build_shelter.*`, interaction fallback copy |
| State | shelter integrity |
| Backlog | `PO-042` releasecritical greybox |
| Test | M3/M5 |
| Status | source manifest ready; detailed interaction brief **needed** |

## Explore cliff

| Felt | Dækning |
|---|---|
| Player roles | climb / belay |
| Assets | cliff/ravine reference, rope, guide marks |
| Audio | exposed wind/rope tension |
| State | information/signal progress |
| Risk | must not become required risky climbing/comfort problem |
| Status | likely redesign/alignment needed with no-forced-climbing comfort rules |

## Secure supplies

| Felt | Dækning |
|---|---|
| Player roles | stow / seal |
| Assets | supply crate, food parcel, straps/seals |
| Audio | crate/cloth/closure |
| State | food security / avoid scent consequence |
| Event | feeds open-food chain |
| Status | interaction brief needed |

---

# 5. Nat 1 — forecast reveal

| Felt | Dækning |
|---|---|
| Beat | Mild rain; camp states become meaningful; radio reveals ship route |
| Assets | camp night state, radio, shelter wet state |
| Audio | camp night, light rain, radio static, `VO_RADIO_NIGHT1_*` |
| Copy | radio Night 1 source lines + subtitles |
| State | camp inspection + ship-in-two-days narrative flag |
| Test | player can restate the new objective |
| Status | copy/audio spec `READY-SPEC`; source voice `NEEDS-SOURCE` |

---

# 6. Dag 2 forecast + planning

| Felt | Dækning |
|---|---|
| Beat | Weather warns that previous generic survival priorities are now storm prep |
| World cues | pressure/wind/birds |
| Actions | reinforce roof, find fiber, find herbs, build signal, explore ridge, treat injury |
| Assets | action cards/icons + roof/signal/medical/explore assets |
| Audio | wind L1, ambient bird change, radio/world cues |
| Copy | `weather.day2.*`, action names/descriptions |
| State | plan + camp/player status |
| Test | M6: player understands why priorities changed without exposition dump |
| Status | `READY-SPEC`; detailed interaction briefs partly missing |

---

# 7. Ravine rescue (`SEQ_RAVINE_RESCUE_001`)

| Felt | Dækning |
|---|---|
| Beat | High-cooperation centerpiece |
| Player roles | traversal/physical actor + rope tension/navigation support; roles can swap |
| Assets | ravine, rope, anchor, guide markers |
| Audio | ravine wind + rope tension states + movement cues |
| Copy | minimal; fallback: hold steady/tension feedback |
| State | fatigue/injury possible; fail-forward |
| Backlog | `PO-056` P1 In |
| Human test | both roles must materially influence outcome; no “one plays, one watches” |
| Comfort | no mandatory real-world floor contact or unsafe physical reaching |
| Status | **interaction brief needed** before Claude implements |

---

# 8. Nat 2 — delayed consequence branches

## Animal threat

| Felt | Dækning |
|---|---|
| Trigger | `SCENT_HIGH` / unsecured food |
| Player roles | one maintains fire/noise; one secures food |
| Assets | camp/food/fire; animal may stay off-screen/abstract |
| Audio | animal distant/approach/retreat, food disturbed |
| Copy | `event.animal.approach`, food warning |
| Test | M4: players can link event to earlier food decision |
| Status | chain concept `READY-SPEC`; full event definition set incomplete |

## Roof leak

| Trigger | `SHELTER_WEAK` |
| Player roles | hold/repair under rain |
| Assets | tarp tear/wet state, rope/repair nodes |
| Audio | rain L2, tarp/rope, shelter creaks |
| Copy | `event.roof_leak.warning` |
| State | wet/cold if unresolved |
| Status | needs event/presentation definition |

## Calm night

| Trigger | good preparation |
| Reward | extra signal/treatment opportunity, not score-only |
| Assets/audio | calm camp night variant |
| Test | should feel like earned relief, not missing content |
| Status | needs precise reward contract after M3 balance evidence |

---

# 9. Dag 3 — last window

| Felt | Dækning |
|---|---|
| Beat | Radio confirms route; final plan under uncertainty |
| Player experience | “We cannot fix everything; what must survive the storm?” |
| Audio | `VO_RADIO_DAY3_*`, wind L1/L2 |
| Copy | `weather.day3.window`, day3 radio lines |
| Assets | radio + planning table + all relevant action cards |
| State | final pre-storm camp/player snapshot |
| Test | players can state final tradeoff |
| Status | content skeleton ready; exact action availability/tuning needs M3/M4 evidence |

**Gap:** `examples/stormnatten.scenario.json` currently jumps from `DAY2_PLANNING` to `DAY3_STORM`; the scenario-bible explicitly contains Day 3 preparation. Data model/content must later be reconciled before M6.

---

# 10. Storm phase 1 — Wind

| Felt | Dækning |
|---|---|
| Objective | hold roof/beam + secure two ropes |
| Branch inputs | shelter state/tool quality/tags |
| Assets | shelter beam/tarp/rope, repair nodes |
| Audio | wind L2/L3, creak high, rope tension, beam shift |
| Copy | `storm.phase1.*` |
| VFX | wind debris, wetness prelude |
| Human test | both active; previous shelter prep visibly matters |
| Status | source specs ready; interaction brief needed |

---

# 11. Storm phase 2 — Rain & fire

| Felt | Dækning |
|---|---|
| Objective | shield embers + fetch dry fuel |
| Branch inputs | `FIRE_LOW`, camp state |
| Assets | fire pit, wind shield, ember carrier/dry fuel cache |
| Audio | rain L2, wet hiss, ember/small fire, storm music |
| Copy | `storm.phase2.*` |
| VFX | rain, embers, smoke, wetness |
| Test | split roles remain meaningful; no long solo fetch while partner waits |
| Status | interaction brief needed |

---

# 12. Storm phase 3 — Consequence slot

| Felt | Dækning |
|---|---|
| Objective | resolve one earned complication |
| Inputs | injury / animal / unresolved camp tags |
| Design rule | earned consequences preferred over arbitrary random punishment |
| Audio/assets | selected from relevant branch manifests |
| Copy | `storm.phase3.*` + event copy |
| Test | players can explain why this complication appeared |
| Evidence | OQ-008 informs randomness intensity |
| Status | `NEEDS-EVIDENCE` for final random/event selection weights |

---

# 13. Storm phase 4 — Partial collapse

| Felt | Dækning |
|---|---|
| Objective | lift/stabilize + snap repair |
| Reuse | heavy-box technical pattern in dramatic context |
| Assets | beam/structure/repair nodes |
| Audio | partial collapse, heavy movement, snap success |
| VFX | impact/dust/debris |
| Copy | `storm.phase4.*` |
| Technical test | isolated PERF-002 + network shared-object proof |
| Human test | both active; dramatic, not fiddly |
| Status | interaction brief needed; Unity proof owned by Claude |

---

# 14. Storm phase 5 — Signal

| Felt | Dækning |
|---|---|
| Objective | move/protect fire source + activate signal |
| Player roles | flame protector + signal clearer/activator |
| Assets | ember carrier, signal frame/fuel, final fire state |
| Audio | storm final layer → ignition → rescue release |
| Copy | `storm.phase5.*` |
| State | signal progress / win-rule |
| Test | signal reads as shared payoff; quality affects time, not permission to try |
| Status | interaction brief needed |

---

# 15. Win/loss/retry

| Felt | Dækning |
|---|---|
| Outcomes | strong win / pressed win / loss |
| Copy | `outcome.*` |
| Audio | rescue/loss resolution |
| State | causal report + retry from pre-storm/day3 checkpoint |
| Test | players understand why they won/lost; retry is clear |
| Status | logical rules exist; presentation contract ready; Unity implementation `UNITY` |

---

# 16. Epilogue / personalization

| Felt | Dækning |
|---|---|
| Beat | weather settles, rescue acknowledged, ending crate/radio opens |
| Neutral | canonical neutral rescue message |
| Private hooks | photo, final audio, 1-3 mementos |
| Spec | `docs/41_PERSONALIZATION_PACKAGE_SPEC.md` |
| Audio | neutral/private final radio + release music |
| Copy | neutral ending + after-action |
| Test | neutral build works with zero private content; personal sequence ≤90s |
| Status | package spec ready; private production later |

---

# 17. After-action report

| Felt | Dækning |
|---|---|
| Purpose | make delayed causality legible + seed replay conversation |
| Data | event journal / causal report system |
| Copy | sentence patterns in `docs/40` |
| Individual titles | prototype only until OQ-010 |
| Test | players can explain at least two cause/effect links by M6 |
| Status | product/copy ready; presentation implementation `UNITY`; OQ-010 `NEEDS-EVIDENCE` |

---

# 18. Coverage gaps discovered by this matrix

## Critical / resolve before relevant implementation

1. **Intro contract:** scenario JSON has no intro actions while bible has several critical interactions. Decide whether intro is explicit scenario data or a documented separate sequence.
2. **Day 3 data gap:** bible has Day 3 preparation; current scenario phase list does not show a separate Day 3 planning phase.
3. **Fire-start scope mismatch:** bible/onboarding treat fire-start as core learning, but `PO-044` is deferred.
4. **Explore cliff comfort ambiguity:** role `climb` must not imply required physical climbing/unsafe roomscale behavior.
5. **Calm-night reward:** needs a precise content contract after balance evidence.
6. **Storm phase 3 selection:** final randomness/event weighting must wait OQ-008/human evidence.
7. **Interaction briefs:** shelter, ravine, fire, signal, storm phases need dedicated handoff specs.

## Noncritical but needed for full scenario

- final event-definition inventory (10 minimum)
- complete source assets
- complete source audio
- production localization file
- final neutral/personal epilogue presentation
- after-action UI layout

---

# 19. Handoff rule to Claude

Claude should never receive just “implement Storm phase 2”. The handoff must include:

- relevant row from this matrix
- interaction brief
- asset IDs
- audio cue IDs
- localization keys
- state/event inputs
- player-experience acceptance criteria
- known evidence/gate status

Claude remains free to choose Unity architecture inside the agreed technical baseline.

---

# 20. Coverage definition of done

A releasecritical beat is content-ready when:

- player purpose is explicit
- both player roles are meaningful
- logical state/events are defined
- source asset IDs exist
- audio cue IDs exist
- required copy keys exist
- accessibility fallback exists
- human test/gate exists
- no unresolved product decision is silently delegated to Unity implementation
