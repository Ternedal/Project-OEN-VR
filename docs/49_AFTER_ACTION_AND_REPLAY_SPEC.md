# After-action & replay spec — PROJECT ØEN

**Product owner:** ChatGPT  
**Unity implementation:** Claude  
**Dato:** 2026-08-13

## Formål

Efterspillet skal gøre to ting:

1. forklare de vigtigste årsag/konsekvens-forbindelser
2. give spillerne lyst til at tale om og evt. prøve scenariet igen

Det må ikke blive en stat-screen, der reducerer en fælles historie til point.

---

# 1. Entry condition

After-action åbner efter:

- win epilogue/personalization beat, eller
- loss-cause beat

Det må ikke afbryde den umiddelbare emotionelle reaktion på signal/rescue.

---

# 2. Information order

## 1. Outcome

- Strong win
- Pressed win
- Loss

## 2. Causal highlights

Vis 2-4 vigtigste årsagskæder.

## 3. Team story

Kort opsummering af hvad der karakteriserede runnet.

## 4. Optional individual titles

Kun hvis OQ-010 evidens støtter det.

## 5. Next action

- retry storm
- replay scenario
- exit

---

# 3. Causal highlight selection

Prioritér facts med høj player relevance:

1. valg der ændrede stormen
2. delayed consequences spilleren oplevede fysisk
3. preparation der konkret hjalp
4. unresolved issue der konkret kostede noget

Undgå:

- every minor resource delta
- hidden RNG rolls
- technical state names/tags

## Example

**Dyrene fandt lejren**  
I lod maden stå usikret på dag 1.

**Taget holdt vindfasen**  
I forstærkede det før stormen.

---

# 4. Blame rule

After-action taler om **I / jeres valg**.

Do not display:

- “Player 1 caused loss”
- “Player 2 wasted resources”
- negative leaderboards by default

Even if telemetry can attribute an action technically, player-facing report should preserve the cooperative framing unless Anders later explicitly chooses otherwise.

---

# 5. Strong win presentation

Tone:

- earned confidence
- camp survived
- signal succeeded

Suggested short summary:

> I gjorde øen til et sted, der kunne holde længe nok.

Do not imply “perfect play” if some costs occurred.

---

# 6. Pressed win presentation

Tone:

- messy success
- sacrifice/consequence visible

Suggested summary:

> Det holdt kun lige — men signalet blev set.

The report should highlight the cost without framing it as lesser entertainment.

---

# 7. Loss presentation

Tone:

- explanatory, not punitive

Suggested summary pattern:

> I kom gennem stormen, men signalvinduet lukkede før signalet var klart.

Then show 1-3 most important contributing chains.

The player should leave loss screen knowing **what they might try differently**.

---

# 8. Team story tags

These are narrative summaries, not competitive scores.

Possible internal tags:

- `TEAM_PREPARED`
- `TEAM_IMPROVISED`
- `TEAM_RISKY`
- `TEAM_RECOVERED`
- `TEAM_PROTECTED_CAMP`
- `TEAM_SIGNAL_FOCUSED`

Presentation uses human copy, not raw tags.

Examples:

- “I var godt forberedt.”
- “I improviserede jer gennem problemerne.”
- “I satsede hårdt på signalet.”

Only one or two need display.

---

# 9. Individual titles — gated by OQ-010

Potential titles exist in `docs/40`, but are **off by default** until tested.

If enabled:

- titles are non-hierarchical
- no numeric score required
- both players receive something meaningful
- titles may be playful
- neither title should assign blame

If OQ-010 is red, omit this layer entirely without breaking layout.

---

# 10. Replay prompt

Replay CTA should connect to learning:

> **Spil igen**  
> Prøv en anden plan og se, hvad stormen gør ved den.

Do not reveal exact hidden outcomes/events before replay.

---

# 11. Retry storm

On loss, allow pre-storm retry where current save/checkpoint contract supports it.

Retry screen may show:

- known camp condition summary
- what checkpoint is used

It should not let players edit past choices retroactively.

---

# 12. Content for personalization build

Personal message appears **before** after-action details, unless later testing shows it is emotionally disruptive.

After-action must remain usable if personalization is neutral/missing.

No private content is repeated into logs/report data unless explicitly authored as visible copy.

---

# 13. Accessibility

- text readable in normal/large modes
- causal cards not color-only
- no required audio
- report can be advanced at player pace
- no time limit

---

# 14. Human acceptance

At M6 ask players before showing detailed report:

- Why did the hardest storm complication happen?
- What helped most?

Then show report and ask:

- Did this match what you thought happened?
- Did anything surprise you unfairly?
- Does this make you want to try a different plan?

If report teaches a completely different causal story than players experienced, either telegraphing or report logic is wrong.

---

# 15. Unity handoff data requirements

Claude's presentation layer needs, conceptually:

- outcome class
- ordered causal facts from authoritative journal/report system
- human-readable localization keys/arguments
- optional team-story tags
- optional individual titles gated by product flag
- retry/replay availability

Exact view/UI architecture is Claude's choice.

---

# 16. Acceptance criteria

After-action is product-ready when:

- it explains 2-4 meaningful causes
- it does not expose internal tag names/formulas
- it avoids player blame
- loss gives a useful retry hypothesis
- replay CTA is clear
- it works with no individual titles
- it works with neutral personalization
- human testers recognize the causal story as fair
