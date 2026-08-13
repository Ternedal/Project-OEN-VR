# M-Pre — ready-to-run playtestpakke

Denne mappe gør ADR-022-gaten i `docs/35_M_PRE_GREYBOX_GATE.md` direkte kørbar.

## Formål

Test én og kun én hypotese:

> Skaber fordelingen af fire indsatsmarkører på for få opgaver reel diskussion mellem to spillere?

Testen er **ikke** en vurdering af art, VR, historie, balance eller samlet sjov.

## Du skal bruge

- 2 testere i samme rum
- 4 ens markører (mønter, klodser eller lignende)
- 1 almindelig d6
- de seks kort fra `TASK_CARDS.md`
- ét eksemplar af `SESSION_SHEET.md` pr. session
- facilitatorens manuskript fra `FACILITATOR_SCRIPT.md`

Test **ikke** med gavemodtageren.

## Testomfang

- mindst 3 sessioner
- mindst 2 forskellige par
- 30-40 minutter pr. session inkl. kort debrief

## Før hver session

1. Sæt de seks opgavekort synligt på bordet.
2. Læg fire ens markører mellem spillerne.
3. Læg d6 frem.
4. Sæt alle fire statusspor til `2` på `SESSION_SHEET.md`.
5. Start stopur eller lydoptagelse, hvis testerne accepterer det.
6. Læs kun teksten i `FACILITATOR_SCRIPT.md` — forklar ikke strategi.

## Under sessionen

For hver af de tre dage:

1. Start tidtagning, når spillerne begynder at diskutere fordelingen.
2. Notér deres første forslag hver især, hvis det er tydeligt.
3. Notér om de er uenige.
4. Notér hvert tydeligt meningsskift efter et argument.
5. Stop forhandlingstiden, når de låser dagens markører.
6. Slå d6 for hver igangsat opgave.
7. Anvend udfaldet fra kortet.
8. Opdatér de fire statusspor.

Facilitatoren må:

- gentage regler ordret
- svare på rene regelspørgsmål
- minde om at alle fire spor betyder noget

Facilitatoren må ikke:

- foreslå en fordeling
- afsløre stormens tærskler
- fortælle spillerne hvad der er “smart”
- hjælpe dem ud af en dårlig beslutning

## Efter dag 3

Læs stormteksten fra `FACILITATOR_SCRIPT.md`.

Stormen er bestået hvis:

- Ly ≥ 6
- Helbred ≥ 4
- Signal ≥ 5

Alle tre skal være opfyldt.

## Debrief

Stil spørgsmålene i manuskriptet uden at forklare hvorfor de stilles.

Det vigtigste datapunkt er ikke om spillerne siger “det var sjovt”, men om de faktisk:

- forhandlede
- var uenige mindst én dag
- ændrede mening på baggrund af argumenter
- talte om **hvad vi skal prioritere** frem for bare **hvad jeg skal gøre**

## Gate

En session regnes som grøn på kernehypotesen, når den opfylder de relevante kriterier fra `docs/35`:

- median forhandlingstid ≥ 45 sekunder pr. dag
- mindst én dag med uenighed
- ingen tydelig administrationsadfærd

Den samlede gate er grøn når mindst **2 af 3 sessioner** er grønne.

## Efter alle tre sessioner

1. Kopiér de rå sessionstal til `RESULT_TEMPLATE.md`.
2. Gem observationer — især det uventede.
3. Overfør de endelige tal til §10 i `docs/35_M_PRE_GREYBOX_GATE.md`.
4. Ved grønt: OQ-006/OQ-007 kan behandles/lukkes og projektet kan gå videre til M1.
5. Ved rødt: stop før M1 og redesign kerneloopet efter prioriteringen i `docs/35`.

## Deterministisk gate-evaluering

`tools/evaluate_mpre.py` kan bruges efter de tre menneskelige sessioner til at kontrollere gateberegningen uden fortolkning.

Lav en anonym CSV med præcis tre rækker og disse kolonner:

`session_id,pair_id,day1_seconds,day2_seconds,day3_seconds,disagreement_days,administration_observed,changed_mind_count,regret_after_storm,human_session,gift_recipient_used`

Kør:

```bash
python tools/evaluate_mpre.py path/to/results.csv
```

Regler:

- `pair_id` er anonymt; evaluator behøver ikke testernes navne.
- `human_session` skal være `true` for alle tre sessioner.
- `gift_recipient_used` skal være `false` for alle tre sessioner.
- mindst to forskellige `pair_id` skal være repræsenteret.
- evaluatoren bruger kun de tre gatekriterier fra `docs/35` til GRØN/RØD.
- meningsskift og fortrydelse rapporteres, men ændrer ikke gateberegningen.
- ugyldig eller ufuldstændig input giver ingen gatekonklusion.

En legitim RØD gate er et gyldigt testresultat og må ikke behandles som en teknisk fejl.

## Ingen snyde-grøn

AI, designerens egen vurdering eller en “simuleret spiller” kan ikke bestå denne gate. Den kræver observeret menneskelig adfærd.
