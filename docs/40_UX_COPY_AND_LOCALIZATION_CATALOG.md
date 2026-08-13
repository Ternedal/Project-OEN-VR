# UX copy & localization source catalog — PROJECT ØEN

**Ejer:** ChatGPT  
**Unity presentation:** Claude  
**Source language:** Dansk  
**Dato:** 2026-08-13  
**Status:** Source-copy v0.1 — kan ændres efter playtest, men keys må være stabile når de tages i brug

## Formål

Repoet har hidtil haft regler for localization og undertekster, men ikke et samlet spillerrettet tekstkatalog.

Dette dokument er source of truth for:

- UI-copy
- onboarding hints
- fejl/reconnect-tekst
- planning labels
- status labels
- radio-/narrative source lines
- after-action copy
- neutral finale/fallback

Det erstatter ikke en senere maskinlæsbar localization-fil. Det er source-copyen, som en sådan fil skal genereres fra.

## Copy-principper

1. Maks. én kort instruktion ad gangen under gameplay.
2. Verber først: “Grib”, “Hold”, “Placér”, “Vent”.
3. Ingen desktop-jargon, når en fysisk forklaring er bedre.
4. Ingen joke må skjule kritisk information.
5. Fejltekst forklarer **hvad spilleren kan gøre nu**.
6. Voice må aldrig være eneste kilde til kritisk information.
7. Undertekst skal kunne læses uden at kende speakerens placering.
8. Fælles beslutninger omtales som “I”, ikke som individuel skyld.

---

# Lobby / session

| Key | Dansk source-copy | Brug |
|---|---|---|
| `lobby.title` | **Strandet Sammen** | Lobbytitel |
| `lobby.create_session` | Opret privat session | Primær CTA |
| `lobby.join_session` | Deltag med kode | Primær CTA |
| `lobby.join_code.label` | Join-kode | Label |
| `lobby.join_code.share` | Del denne kode med din makker | Host-hint |
| `lobby.join_code.enter` | Indtast koden fra din makker | Join-hint |
| `lobby.ready` | Klar | Ready-knap |
| `lobby.not_ready` | Ikke klar | State |
| `lobby.partner_ready` | Din makker er klar | State |
| `lobby.waiting_partner` | Venter på din makker… | State |
| `lobby.start_when_ready` | Begge skal være klar | State |
| `lobby.device_info` | Enhed og version | Diagnostics label |
| `lobby.content_mismatch.title` | Versionerne passer ikke sammen | Compatibility error |
| `lobby.content_mismatch.body` | Opdatér begge headset til samme spilversion, og prøv igen. | Compatibility recovery |
| `lobby.invalid_code` | Koden kunne ikke findes. Tjek tegnene, og prøv igen. | Join error |
| `lobby.session_full` | Sessionen har allerede to spillere. | Join error |
| `lobby.connection_error` | Forbindelsen kunne ikke oprettes. Prøv igen om lidt. | Network error |

---

# Kalibrering / comfort setup

| Key | Dansk source-copy | Brug |
|---|---|---|
| `setup.title` | Gør plads til at overleve | Setup title |
| `setup.standing` | Jeg spiller stående | Option |
| `setup.seated` | Jeg spiller siddende | Option |
| `setup.dominant_left` | Venstre hånd | Option |
| `setup.dominant_right` | Højre hånd | Option |
| `setup.reset_position` | Nulstil position | Utility |
| `setup.floor_check` | Gulvet ser forkert ud | Utility |
| `setup.reach_check` | Ræk ud mod markøren foran dig | Calibration hint |
| `setup.reach_ok` | Fint — alt vigtigt placeres inden for din rækkevidde. | Confirmation |

---

# Onboarding — Vraget

Hints vises kun efter behov. Først affordance, derefter tekst.

| Key | Dansk source-copy | Trigger |
|---|---|---|
| `hint.look_partner` | Find din makker. | Første orientering |
| `hint.teleport` | Peg på jorden, og teleportér hen til kassen. | Manglende movement |
| `hint.grab_light` | Grib håndtaget. | Første grab |
| `hint.heavy_need_two` | Den er for tung alene. Grib hver jeres side. | Heavy crate, solo attempt |
| `hint.heavy_coordinate` | Løft sammen — roligt. | Begge griber |
| `hint.place_crate` | Sæt kassen i den markerede zone. | Carry phase |
| `hint.open_crate` | Åbn kassen. | Intro progress |
| `hint.take_firesteel` | Tag ildstålet. | Intro object |
| `hint.return_object` | Mistede du den? Hent den tilbage fra armbåndet. | Critical object lost |

---

# Fire-start onboarding

| Key | Dansk source-copy | Trigger |
|---|---|---|
| `hint.fire.protect_tinder` | Hold vinden væk fra det tørre materiale. | Secondary role |
| `hint.fire.strike` | Stryg ildstålet mod tinderet. | Primary role |
| `hint.fire.together` | Skærm flammen, mens din makker tænder. | Coordination |
| `hint.fire.embers` | Der er gløder — giv dem tørt brændsel. | Partial success |
| `hint.fire.success` | Ilden holder. | Success |

---

# Planning table

| Key | Dansk source-copy | Brug |
|---|---|---|
| `planning.title` | Hvad bruger I dagen på? | Planning heading |
| `planning.effort_available` | Indsats tilbage | Counter/physical label |
| `planning.cost` | Indsats | Card field |
| `planning.risk` | Risiko | Card field |
| `planning.expected_gain` | Mulig gevinst | Card field |
| `planning.commit` | Lås planen | Commit action |
| `planning.change` | Flyt markørerne, hvis I vil ændre planen | Hint |
| `planning.wait_partner` | Din makker er ikke færdig endnu | State |
| `planning.ready` | Planen kan låses | State |
| `planning.locked` | Planen er låst | Confirmation |
| `planning.invalid` | Fordel alle fire markører først | Validation |
| `planning.revision_changed` | Planen ændrede sig — kig på markørerne igen | Race/conflict recovery |

## Action-card titles

| Key | Dansk source-copy |
|---|---|
| `action.gather_wood.name` | Saml træ |
| `action.find_food.name` | Find mad |
| `action.build_shelter.name` | Byg læ |
| `action.explore_cliff.name` | Udforsk klippestien |
| `action.secure_supplies.name` | Sikr forsyninger |
| `action.reinforce_roof.name` | Forstærk taget |
| `action.find_fiber.name` | Find fiber |
| `action.find_herbs.name` | Find urter |
| `action.build_signal.name` | Byg signal |
| `action.explore_ridge.name` | Udforsk højderyggen |
| `action.treat_injury.name` | Behandl skaden |

## Short action-card descriptions

These are deliberately non-numeric until M3 tuning.

| Key | Dansk source-copy |
|---|---|
| `action.gather_wood.short` | Brændsel og byggemateriale. |
| `action.find_food.short` | Mere sikker mad til lejren. |
| `action.build_shelter.short` | Bedre beskyttelse mod nat og vejr. |
| `action.explore_cliff.short` | Information og muligheder længere inde på øen. |
| `action.secure_supplies.short` | Beskyt det, I allerede har. |
| `action.reinforce_roof.short` | Gør taget klar til hårdt vejr. |
| `action.find_fiber.short` | Reb og bindinger til byggeri. |
| `action.find_herbs.short` | Noget der kan bruges til behandling. |
| `action.build_signal.short` | Gør jer nemmere at opdage. |
| `action.explore_ridge.short` | Få overblik over havet og vejret. |
| `action.treat_injury.short` | Reducér risikoen fra en skade. |

---

# Camp status labels

| Key | Dansk source-copy |
|---|---|
| `status.camp.shelter` | Ly |
| `status.camp.fire` | Ild |
| `status.camp.food` | Mad |
| `status.camp.signal` | Signal |
| `status.camp.threat` | Fare |
| `status.player.health` | Helbred |
| `status.player.fatigue` | Træthed |
| `status.player.injury` | Skade |
| `status.player.wet` | Våd |
| `status.player.cold` | Kold |

State adjectives:

| Key | Dansk source-copy |
|---|---|
| `state.good` | God |
| `state.stable` | Stabil |
| `state.weak` | Svag |
| `state.critical` | Kritisk |
| `state.unknown` | Ukendt |

---

# Shared pause / reconnect

| Key | Dansk source-copy | Brug |
|---|---|---|
| `pause.requested` | Din makker vil holde pause | Shared request |
| `pause.countdown` | Pauser sikkert… | Transition |
| `pause.title` | Pause | State |
| `pause.resume` | Fortsæt | CTA |
| `pause.settings` | Komfortindstillinger | CTA |
| `pause.return_object` | Hent vigtig genstand tilbage | Utility |
| `reconnect.lost` | Forbindelsen til din makker blev afbrudt | Error |
| `reconnect.waiting` | Forsøger at finde hinanden igen… | Recovery |
| `reconnect.returned` | I er forbundet igen | Success |
| `reconnect.checkpoint_offer` | Forbindelsen kunne ikke gendannes. Fortsæt fra sidste sikre punkt? | Recovery choice |
| `reconnect.resume_checkpoint` | Fortsæt fra checkpoint | CTA |
| `reconnect.leave` | Afslut sessionen | CTA |

---

# Critical object / interaction feedback

| Key | Dansk source-copy |
|---|---|
| `interaction.need_partner` | I skal være to til den her. |
| `interaction.partner_grab_other_side` | Grib den anden side. |
| `interaction.hold_steady` | Hold den stabil. |
| `interaction.too_much_tension` | Rebet er ved at blive overbelastet. |
| `interaction.good_tension` | Spændingen er god. |
| `interaction.snap_ready` | Slip for at fastgøre. |
| `interaction.partial` | Det holder — men ikke perfekt. |
| `interaction.failed_forward` | Det gik skævt, men I kom videre. |
| `interaction.returned` | Genstanden er tilbage. |

Copy is fallback/help text; normal play should communicate most of this through world feedback.

---

# Day/phase cards

| Key | Dansk source-copy |
|---|---|
| `phase.day1.dawn` | Dag 1 — Få lejren til at holde natten |
| `phase.day1.night` | Nat 1 |
| `phase.day2.dawn` | Dag 2 — Vejret vender |
| `phase.day2.night` | Nat 2 |
| `phase.day3.dawn` | Dag 3 — Sidste chance |
| `phase.storm` | Stormen |
| `phase.signal` | Signalet |
| `phase.epilogue` | Efter stormen |

---

# Environmental / forecast text

| Key | Dansk source-copy | Presentation |
|---|---|---|
| `weather.day2.pressure` | Luften føles tung. Vinden er ved at vende. | Radio/journal/world cue |
| `weather.day2.birds` | Fuglene trækker væk fra øen. | Observation text/hint |
| `weather.storm.warning` | Stormen rammer før natten er omme. | Forecast |
| `weather.day3.window` | Skibet passerer i dag. Det her er jeres vindue. | Critical objective |

---

# Radio source lines — neutral canon

All voice lines get subtitles with the same text unless performance requires a shortened subtitle version.

## Night 1

| Key | Speaker | Dansk source-copy |
|---|---|---|
| `vo.radio.night1.01` | Radio | “…til alle fartøjer i området…” |
| `vo.radio.night1.02` | Radio | “…ruten langs øgruppen genoptages om cirka to døgn…” |
| `vo.radio.night1.03` | Radio | “…hold kanalen fri…” |

The fragment intentionally leaves uncertainty: they know a ship route returns; they do not receive a rescue promise.

## Day 3

| Key | Speaker | Dansk source-copy |
|---|---|---|
| `vo.radio.day3.01` | Radio | “…ruten er bekræftet. Passage ved daggry…” |
| `vo.radio.day3.02` | Radio | “…sigtbarheden bliver dårlig under fronten…” |
| `vo.radio.day3.03` | Radio | “…visuelt signal anbefales…” |

## Neutral ending

| Key | Speaker | Dansk source-copy |
|---|---|---|
| `vo.radio.ending.neutral.01` | Radio | “Signal observeret.” |
| `vo.radio.ending.neutral.02` | Radio | “Bliv ved kysten. Vi har jeres position.” |
| `vo.radio.ending.neutral.03` | Radio | “Hold ud lidt endnu.” |

Personal final-message audio uses hook `RADIO_FINAL_MESSAGE` and is never stored in this repository.

---

# Night consequence text

| Key | Dansk source-copy |
|---|---|
| `event.food_open.warning` | Noget har været ved maden. |
| `event.animal.approach` | Der er noget uden for lejren. |
| `event.roof_leak.warning` | Taget holder ikke regnen ude. |
| `event.injury.untreated` | Skaden bliver værre. |
| `event.tool.broken` | Værktøjet holder ikke til mere. |
| `event.dry_fuel.found` | I fandt brændsel, der stadig er tørt. |
| `event.herbs.extra` | I fandt mere brugbart end forventet. |
| `event.smoke.distant` | Der er røg i det fjerne. |

No event text should expose hidden numeric modifiers.

---

# Storm phase copy

| Key | Dansk source-copy | Brug |
|---|---|---|
| `storm.phase1.title` | Vinden tager til | Phase intro |
| `storm.phase1.objective` | Hold taget. Få rebene fast. | Objective |
| `storm.phase2.title` | Regnen rammer | Phase intro |
| `storm.phase2.objective` | Beskyt gløderne. Find tørt brændsel. | Objective |
| `storm.phase3.title` | Noget giver efter | Phase intro |
| `storm.phase3.objective` | Fordel rollerne hurtigt. | Objective |
| `storm.phase4.title` | Konstruktionen kollapser | Phase intro |
| `storm.phase4.objective` | Løft sammen. Stabiliser. Reparér. | Objective |
| `storm.phase5.title` | Daggry | Phase intro |
| `storm.phase5.objective` | Få ilden til signalet. | Objective |

---

# Outcome / after-action

## Result headings

| Key | Dansk source-copy |
|---|---|
| `outcome.strong_win.title` | I klarede den |
| `outcome.pressed_win.title` | I blev set |
| `outcome.loss.title` | Signalet nåede ikke frem |
| `outcome.retry` | Prøv stormen igen |
| `outcome.replay` | Spil scenariet igen |
| `outcome.leave` | Afslut |

## Causal report sentence patterns

| Key | Dansk source-copy pattern |
|---|---|
| `aar.because_choice` | `{CONSEQUENCE} — fordi I {CHOICE} på {WHEN}.` |
| `aar.prepared_for` | `{PREPARATION} gjorde {CONSEQUENCE} lettere.` |
| `aar.left_unresolved` | `{ISSUE} blev ikke løst før stormen.` |
| `aar.recovery` | I kom videre, selv om {PROBLEM}.` |

Examples:

- “Dyrene fandt lejren — fordi I lod maden stå usikret på dag 1.”
- “Det forstærkede tag gjorde vindfasen lettere.”
- “Skaden blev ikke behandlet før stormen.”

The report must explain causality without implying that a single person is to blame.

---

# Optional individual titles

These are **prototype copy only** until OQ-010 is resolved.

| Key | Dansk source-copy |
|---|---|
| `title.craft` | Lejrens håndværker |
| `title.scout` | Den nysgerrige |
| `title.rescue` | Den der holdt fast |
| `title.resourceful` | Intet gik til spilde |
| `title.risk` | Først ud i stormen |
| `title.chaos` | Kaosagenten |

Do not implement as ranking or score before OQ-010 evidence.

---

# Error / system text

| Key | Dansk source-copy |
|---|---|
| `error.generic` | Noget gik galt. Prøv igen. |
| `error.save_failed` | Checkpointet kunne ikke gemmes. Det forrige sikre punkt er bevaret. |
| `error.save_invalid` | Checkpointet kunne ikke læses. I kan fortsætte fra det forrige. |
| `error.private_asset_missing` | Personligt indhold mangler. Den neutrale afslutning bruges i stedet. |
| `error.private_asset_invalid` | Et personligt element kunne ikke indlæses. Den neutrale version bruges. |
| `error.return_to_lobby` | Sessionen kan ikke fortsætte sikkert. I sendes tilbage til lobbyen. |

---

# Accessibility / settings labels

| Key | Dansk source-copy |
|---|---|
| `settings.comfort` | Komfort |
| `settings.locomotion` | Bevægelse |
| `settings.teleport` | Teleport |
| `settings.smooth_move` | Flydende bevægelse |
| `settings.turning` | Drejning |
| `settings.snap_turn` | Snap-drejning |
| `settings.smooth_turn` | Flydende drejning |
| `settings.snap_angle` | Snap-vinkel |
| `settings.vignette` | Bevægelsesvignette |
| `settings.haptics` | Haptik |
| `settings.haptics_strength` | Haptikstyrke |
| `settings.subtitles` | Undertekster |
| `settings.subtitle_size` | Tekststørrelse |
| `settings.subtitle_background` | Tekstbaggrund |
| `settings.handedness` | Dominant hånd |

---

# Subtitle speaker labels

| Key | Dansk source-copy |
|---|---|
| `speaker.radio` | Radio |
| `speaker.partner` | Makker |
| `speaker.system` | — |

Player voice chat is not automatically subtitled in gift scope.

---

# Copy QA checklist

A key is ready when:

1. wording is understandable without developer explanation
2. gameplay-critical instruction is short enough for VR
3. key has a neutral fallback
4. voice key has subtitle copy
5. text does not expose internal implementation terms such as “authority”, “content hash” unless in diagnostics
6. error copy includes recovery action where possible
7. no critical distinction relies on color wording alone
8. placeholders have documented variables
9. private/personal text is not committed

---

# Maskinlæsbar næste leverance

Når katalogets key-set stabiliseres efter M-Pre/M1-handoff, genereres en separat localization source-file fra dette dokument.

`PO-104` kan fortsat være deferred som fuld localization/subtitle content-pass; dette dokument reducerer risikoen ved at definere **source keys og dansk baseline-copy** før den dyre implementation.
