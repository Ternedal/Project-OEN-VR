# Gift experience & release flow — PROJECT ØEN

**Ejer:** ChatGPT  
**Unity/build implementation:** Claude  
**Dato:** 2026-08-13

## Formål

PROJECT ØEN er ikke bare et spilbuild; gaveversionen skal føles som en sammenhængende oplevelse fra installation til epilog.

Dette dokument beskriver produktflowet uden at foreskrive Unity-implementation.

---

# 1. Designmål

Gaveoplevelsen skal:

- starte uden teknisk ceremoniel følelse
- få to spillere sammen hurtigt
- ikke spoile den personlige finale
- kunne fungere helt neutralt
- tåle disconnect/retry uden at ødelægge stemningen
- slutte med plads til reaktion/samtale, ikke en abrupt menu

---

# 2. Før spillet — distribution

Den tekniske releasekanal vælges/implementeres af Claude, men produktkravet er:

Anders skal kunne give begge spillere en enkel instruktion med højst disse informationer:

1. installér/åbn appen
2. sørg for internet og controllerne
3. start appen på begge headset
4. én opretter session, én indtaster join-koden

Ingen udviklerværktøjer bør være nødvendige for slutbrugerne.

## Gave-/spoilerregel

Installations- og lobbytekst må ikke afsløre:

- den personlige slutbesked
- konkrete memento-referencer
- stormens branches
- “rigtige” strategier

---

# 3. First launch

## Step 1 — minimal title

Vis:

**STRANDET SAMMEN**

Short subtitle optional:

> Et samarbejdseventyr for to.

No long lore text.

## Step 2 — comfort/setup

Player chooses:

- seated/standing
- dominant hand
- default comfort options, with safe defaults preselected

Setup must feel like preparing to play, not a settings wizard.

## Step 3 — session

Options:

- Opret privat session
- Deltag med kode

Once connected, show partner presence/ready state.

---

# 4. Lobby tone

Lobby is not a social hub. It is a short staging area.

Must communicate:

- partner connected
- both compatible
- both ready

Should not require:

- accounts beyond platform necessities
- character customization
- loadout selection
- long settings sequence

Target: connected pair should reach scenario start quickly after comfort setup.

---

# 5. Scenario start

Avoid title-card exposition.

Preferred experience:

1. brief fade/arrival
2. beach/wreck ambience
3. player sees partner
4. first physical problem is visible
5. first instruction appears only if necessary

The heavy crate is the opening statement: “You need each other.”

---

# 6. Surprise management

The personalization overlay must stay invisible until the intended epilogue.

Before finale:

- no filenames/private labels
- no UI saying “personal message”
- no preview thumbnail in settings
- no debug hooks visible in release build

Neutral build should look identical during gameplay.

---

# 7. Failure during play

Technical failure must be handled with language that protects the shared experience.

## Disconnect

- pause safely
- explain that the partner connection was lost
- attempt recovery
- checkpoint option if recovery fails

Avoid wording like “client/server error” in player UI.

## Crash/restart

On safe resume:

- offer latest valid checkpoint
- preserve causal state
- do not force replay from beginning unless no valid checkpoint exists

---

# 8. Gameplay ending — success

## Beat 1 — Signal acknowledged

World gives immediate confirmation:

- fire/signal response
- audio/radio acknowledgement
- storm pressure drops

## Beat 2 — Shared breath

Give players a short uncontrolled-by-menu moment to look at:

- each other
- camp damage
- sunrise/weather shift

Do not instantly interrupt with score panels.

## Beat 3 — Epilogue unlock

Radio/ending crate becomes available.

Neutral or private personalization package supplies the content.

## Beat 4 — Personal/neutral message

The message plays only after a deliberate interaction.

Player can move/look naturally; avoid hard camera lock.

## Beat 5 — After-action

Show the most important causal story:

- what they prepared well
- what returned as a consequence
- why the storm played out the way it did

Individual titles only if OQ-010 evidence supports them.

---

# 9. Gameplay ending — loss

Loss flow:

1. danger resolves enough to read the state
2. concise cause summary
3. no blame assignment to one player
4. retry options

Recommended options:

- Prøv stormen igen
- Fortsæt fra tidligere checkpoint (if valid)
- Afslut

Do not make the pair replay all three days just to see the finale again.

---

# 10. Replay

Replay should preserve the question:

> “What would we do differently?”

A replay may vary:

- weather profile
- event selection
- opportunity order

But replay screen should not expose hidden formulas.

After-action report can highlight one or two different strategic opportunities without recommending an “optimal build”.

---

# 11. Same-room vs remote

Product question remains open for primary optimization, but base release flow must work in both where networking supports it.

## Same-room

Potential problem:

- hearing partner both physically and through in-game voice if voice is later added

Gift scope should avoid requiring remote voice if same-room is viable.

## Remote

Requires:

- clear partner presence
- connection state
- later voice solution if platform/social setup does not provide it

No decision here silently adds Photon Voice to release scope; voice remains scoped separately.

---

# 12. Neutral build requirement

A neutral release candidate must be treated as a first-class product, not a broken gift build with placeholders.

Neutral build has:

- neutral names
- neutral ending crate/photo
- neutral rescue radio
- no missing-hook errors
- same gameplay
- complete after-action

This is also the safest build for external QA.

---

# 13. Private gift build/content package

Before private release:

- source package passes `docs/41_PERSONALIZATION_PACKAGE_SPEC.md`
- no private data in repo/logs
- neutral fallback still present
- gift content only becomes visible in epilogue
- rollback state is known

---

# 14. Player-facing release note

For gift release, release notes should be short and nontechnical.

Example structure:

```text
STRANDET SAMMEN

Et samarbejdseventyr for to Meta Quest-headsets.

Før I starter:
- Sørg for internetforbindelse.
- Hav begge controllere klar.
- Start spillet på begge headset.
- Én opretter en privat session og deler join-koden.

Hvis forbindelsen ryger undervejs, forsøger spillet at finde jer igen eller fortsætte fra et sikkert punkt.
```

Technical version/build info can live under diagnostics/settings.

---

# 15. Gift release acceptance criteria

From user perspective:

- both players can get from app launch to connected lobby without developer help
- comfort setup is understandable
- first scenario objective appears through play, not a manual
- private finale remains a surprise
- neutral fallback is complete
- disconnect/retry does not require technical knowledge
- success ending leaves room for reaction
- replay choice is clear

Technical clean-install/build/signing acceptance remains with Claude + `docs/13`/`docs/15`.

---

# 16. Open owner decisions — intentionally not blocked

Later Anders decisions:

- final tone: adventurous / humorous / romantic
- same-room vs remote-first optimization
- explicit character identity vs neutral survivors
- launch language beyond Danish

The flow above supports all options without forcing an early choice.
