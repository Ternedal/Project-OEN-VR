# Narrative continuity pass — STORMNATTEN

**Ejer:** ChatGPT  
**Dato:** 2026-08-13  
**Status:** Narrative contract v0.1

## Formål

Stormnatten skal frigive information i en rækkefølge, der skaber bedre beslutninger uden at fortælle spillerne den optimale strategi.

Dette dokument kontrollerer kontinuiteten på tværs af:

- intro
- radio
- environmental storytelling
- action cards
- events
- storm
- epilogue

---

# 1. What players know over time

## Intro — immediate truth

Players know:

- they are stranded
- they are together
- the camp/wreck is their immediate anchor
- basic survival requires cooperation

Players do **not** know yet:

- exact rescue timing
- full storm severity
- exact consequence chains
- optimal Day 1 strategy

This preserves discovery and prevents tutorial exposition from solving planning.

---

# 2. Day 1 — build a camp before knowing the full problem

## Information available

- immediate needs: fire/shelter/food/supplies/exploration
- island shows general exposure/weather risk
- radio is weak/incomplete

## Intended player question

> “Hvad skal vi gøre for at klare natten og forstå vores situation?”

## Narrative rule

Day 1 should not explicitly say:

> “Build shelter because a major storm comes on Day 3.”

That would make planning feel like task compliance rather than judgment.

Players may infer weather risk from the island, but not know the full future.

---

# 3. Night 1 — first strategic reveal

Radio fragment provides the first rescue horizon:

- a shipping route returns in about two days
- no guaranteed rescue

This changes the scenario from generic survival to **survive + prepare to be seen**.

## Continuity requirement

The radio line must follow a meaningful first-day consequence/state beat; it should not interrupt action.

Suggested sequence:

1. dusk/night camp state resolves
2. immediate consequences shown
3. brief calm
4. radio fragment cuts through static

## Player takeaway

> “Vi har et vindue om cirka to døgn. Vi skal både overleve og gøre os synlige.”

---

# 4. Day 2 — storm foreshadowing becomes explicit

Environmental signs:

- falling pressure / changed wind
- birds leaving
- stronger weather layer

Players now receive a clear but incomplete forecast:

> a significant storm/front is approaching

## Intended player question

> “Hvor meget tør vi bruge på signalet, når lejren også skal overleve stormen?”

This is the day where signal vs shelter vs health should become a visible strategic tension.

---

# 5. Day 2 exploration information

## Ridge

May clarify:

- sea route direction
- likely signal location/visibility
- weather exposure

Should not reveal exact win threshold.

## Distant smoke

`EVT_DISTANT_SMOKE_001` is a world teaser.

It must not create a false current objective such as “find survivors” if no such branch exists.

Canonical interpretation:

> The island/world may contain more than the players can reach in this scenario.

---

# 6. Night 2 — choices return

This night should be the first strong proof that decisions persist.

Examples:

- unsecured food → animal consequence
- weak shelter → leak/wet/cold
- good prep → calm/extra opportunity

## Narrative rule

Consequences must be presented as **world reactions**, not narrator explanations.

Bad:

> “Because you failed to secure food on Day 1, animals attack now.”

Good:

- rustling
- disturbed food
- players react
- after-action later confirms the causality

## Player takeaway

Ideally, before the report they already suspect:

> “Det her er nok fordi vi lod maden stå.”

---

# 7. Day 3 — certainty rises, information narrows

Radio now confirms:

- route/passage at dawn
- visibility will be poor
- visual signal is required

Unlike Day 1/2, Day 3 can be explicit because the drama now comes from scarcity, not uncertainty about the objective.

## Intended player question

> “Hvad skal vi sikre nu, når vi ved præcis hvornår chancen kommer?”

This is why a distinct Day 3 planning beat matters.

---

# 8. What Day 3 must NOT do

Do not show a checklist like:

- shelter 60 required
- signal 70 required
- fire 30 required

unless later evidence proves qualitative state is insufficient.

Players should make a judgment based on readable camp state, known injuries and action-card tradeoffs.

---

# 9. Storm — no new lore

The storm is payoff, not exposition.

During storm:

- no long radio explanation
- no new mystery branch
- no tutorial monologue

Information is immediate:

- what is failing
- what needs two people
- what previous state changed the pressure

Narrative should be carried by world state, not speech.

---

# 10. Phase 3 consequence continuity

Storm phase 3 should select from **earned/known consequence families** where possible.

The player may not know exactly what will happen, but the event should feel narratively connected to something already seen:

- injury
- food threat
- weak shelter

Randomness can vary which problem peaks, not invent an unrelated disaster from nowhere.

---

# 11. Signal payoff

The signal sequence resolves both narrative lines:

- survival: camp/fire endured enough
- rescue: players became visible within the window

Immediate acknowledgement should answer:

> “Did anyone see us?”

before personal epilogue content begins.

---

# 12. Personalization placement

Personalization comes **after** the canonical rescue acknowledgement.

Reason:

- the game story must resolve neutrally first
- private message becomes an added emotional payoff, not a replacement for game logic

Order:

1. signal works
2. rescue acknowledgement
3. storm settles
4. players get a quiet beat
5. ending crate/radio hook becomes available
6. neutral/private message
7. after-action

---

# 13. Loss continuity

Loss reasons must match what players were told was important.

Valid narrative causes:

- signal window missed
- both incapacitated
- explicit fire/signal collapse under established rules

Avoid surprise fail states based on hidden lore/state.

After loss, report should answer:

> “What earlier choices mattered?”

without claiming there was one guaranteed correct strategy.

---

# 14. Radio voice principles

Radio sounds functional, fragmentary and believable.

Avoid:

- omniscient narrator tone
- direct tutorial instructions
- emotional commentary on player decisions

Radio is an imperfect external signal, not a game-master voice.

---

# 15. Character voice / player identity

Gift scope does not require voiced player characters.

Benefits:

- avoids conflicting with real players speaking to each other
- reduces localization/recording scope
- keeps personalization flexible

World/radio voice can carry necessary narrative beats.

---

# 16. Narrative continuity issues found

## NC-001 — Firesteel importance

Intro crate contains firesteel and bible expects first fire. If fire-start is removed from gift scope, firesteel becomes a misleading Chekhov's gun.

Tracked in issue #8.

## NC-002 — Day 3 phase gap

Narrative explicitly builds toward one last deliberate plan, but scenario data currently jumps to storm.

Tracked in issue #8.

## NC-003 — Smoke teaser expectation

Distant smoke must stay clearly non-actionable in current scenario, or players may believe they missed content.

Mitigation: observational wording, no objective marker.

## NC-004 — Radio timing

Night 1 radio must occur after the night/camp result, otherwise it can drown the first consequence-learning beat.

## NC-005 — Personal message ordering

Canonical rescue acknowledgement must happen before private message. Otherwise neutral and personalized endings do not share the same resolved game story.

---

# 17. Information release table

| Beat | New knowledge | Kept uncertain |
|---|---|---|
| Intro | stranded, cooperate, camp matters | rescue timing, storm |
| Day 1 | survival opportunities | future priority |
| Night 1 | ship route in ~2 days | exact weather/severity |
| Day 2 | storm/front approaching | exact consequence mix |
| Night 2 | choices have delayed effects | final storm selection |
| Day 3 | passage at dawn, visual signal needed | exact threshold/branch |
| Storm | immediate failures/tasks | no new strategic lore |
| Signal | rescue acknowledgement | — |
| Epilogue | personal/neutral payoff | — |
| After-action | explicit causal explanation | hidden formulas remain hidden |

---

# 18. Narrative QA

At M6, without after-action report first, ask players:

1. Hvornår forstod I, at et skib kunne passere?
2. Hvornår blev stormen en konkret trussel?
3. Hvad troede I var vigtigst på dag 3?
4. Var der noget spillet fortalte jer for tidligt?
5. Var der en historie/ledetråd, I forventede at kunne følge, men ikke kunne?

A narrative beat fails if it:

- spoils the strategy before a decision
- creates a promised branch that does not exist
- hides the objective so completely that players cannot plan
- contradicts the world state or after-action report

---

# 19. Definition of done

Narrative continuity is release-ready when:

- information release follows this progression
- radio/copy/event content matches it
- no false objective branch is implied
- Day 3 planning and intro contracts are reconciled
- personalized ending remains optional overlay
- human testers can explain the rescue objective and at least two causal chains without exposition rescue
