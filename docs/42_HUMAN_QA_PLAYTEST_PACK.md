# Human QA & playtest pack — PROJECT ØEN

**Ejer:** ChatGPT  
**Device/build execution:** Anders + Claude  
**Dato:** 2026-08-13

## Formål

`docs/13_TEST_QA_ACCEPTANCE.md` beskriver gates. Dette dokument beskriver **hvordan mennesketestene faktisk gennemføres**, så resultater kan sammenlignes på tværs af builds og milepæle.

M-Pre har sin egen protokol i `prototype/m-pre/` og gentages ikke her.

---

# 1. Fælles testregler

## Testeren skal ikke undervises i løsningen

Facilitator må:

- hjælpe med headset/fit
- hjælpe ved teknisk fejl
- gentage ordret instruktion, hvis UI/voice allerede har vist den
- stoppe testen af sikkerhedsårsager

Facilitator må ikke:

- forklare den “rigtige” strategi
- fortælle hvem der bør gøre hvad
- pege på skjulte affordances
- redde designet med verbal tutorial

Hvis facilitatorhjælp var nødvendig, logges det som et fund.

## Minimum metadata pr. session

- build/version
- device P1/P2
- seated/standing
- dominant hand
- tidligere VR-erfaring: lav/mellem/høj
- har testerne spillet denne build før?
- same-room/remote
- session start/slut
- crashes/restarts

No private names are required; use tester IDs.

---

# 2. Standard observation sheet

Registrér tidsstemplet observationer med disse tags:

| Tag | Betydning |
|---|---|
| `CONFUSION` | ved ikke hvad næste mål/interaktion er |
| `AFFORDANCE` | kan ikke se hvordan objekt bruges |
| `REACH` | fysisk svært/umuligt at nå |
| `COMFORT` | kvalme, øjentræthed, arm/skulderbelastning |
| `WAIT` | ufrivillig passivitet |
| `COOP` | reel koordinering/kommunikation |
| `UI` | UI skaber misforståelse |
| `AUDIO` | lyd hjælper/forvirrer |
| `NETWORK` | synlig desync/latency/failure |
| `DELIGHT` | spontan positiv reaktion/latter/overraskelse |
| `FRUSTRATION` | irritation uden tilsigtet dramatisk spænding |
| `RECOVERY` | spilleren kommer selv videre efter fejl |

Format:

```text
12:43  P2  AFFORDANCE  leder efter hvor rebet skal fastgøres
13:02  BOTH COOP        diskuterer hvem der holder bjælken
13:18  P1  RECOVERY     opdager selv snap-zonen efter feedback
```

---

# 3. Standard post-session spørgsmål

Spørg i denne rækkefølge og undgå ledende opfølgning først:

1. Hvad prøvede I at opnå?
2. Hvad var jeres vigtigste valg?
3. Var der et tidspunkt, hvor I var uenige om hvad I skulle gøre?
4. Hvornår var I mest afhængige af hinanden?
5. Var der et tidspunkt, hvor en af jer bare ventede?
6. Hvad var mest uklart?
7. Hvad føltes mest tilfredsstillende?
8. Hvad ville I gøre anderledes næste gang?
9. Var noget fysisk ubehageligt eller trættende?
10. Har I lyst til at prøve igen? Hvorfor/hvorfor ikke?

Derefter må facilitator spørge specifikt til observerede hændelser.

---

# 4. Comfort score

Ved 15/30/45 min hvor relevant:

0 = intet  
1 = mildt  
2 = moderat  
3 = kraftigt

| Dimension | 15m | 30m | 45m |
|---|---:|---:|---:|
| Kvalme | | | |
| Øjentræthed | | | |
| Svimmelhed | | | |
| Arm/skuldertræthed | | | |
| Reach-frustration | | | |
| Mental overload | | | |

**Stop testen** ved kraftigt ubehag eller hvis tester ønsker det.

---

# 5. M1 — interaction foundation human gate

## Formål

Bevis at de basale VR-interaktioner er komfortable og forståelige, ikke om scenariet er sjovt endnu.

## Testere

Minimum 2 personer; gerne mindst én med lav/mellem VR-erfaring.

## Opgaver

Uden verbal hjælp skal hver tester kunne:

1. kalibrere seated/standing
2. teleportere
3. bruge snap turn
4. gribe/aflevere en let genstand
5. returnere/reset en mistet genstand
6. gribe tungt objekt med partner
7. flytte og placere objektet sammen
8. bruge magnetisk snap-preview
9. ændre dominant hånd/comfort-indstilling

## Gentagelser

Kerneinteraktionerne gentages 10 gange, hvor `docs/12` kræver det.

## Registrér

- misgrabs
- accidental releases
- antal reset
- reach-problemer
- seated/standing mismatch
- tid hvor partner venter
- comfort issues

## Grøn M1-human side

- ingen kritisk interaktion kræver udviklerforklaring
- alle kritiske objekter kan nås uden knælen
- ingen systematisk forskel der gør seated spilleren sekundær
- ingen moderat+ discomfort hos flertal

Teknisk M1-gate verificeres fortsat af Claude/device-tests.

---

# 6. M3 — one-day cooperation gate

## Formål

Bevis at én dag kan forstås og at planning→action→consequence skaber et reelt valg.

## Setup

Brug én-dags build/greybox. Ingen Stormnatten-finale nødvendig.

## Facilitator observerer

- tid til målforståelse
- første meningsfulde fælles beslutning
- om fire effort markers diskuteres
- om action cards forstås
- om begge roller er aktive
- om dusk/night-resultatet kan kobles til planens valg

## Post-test ekstra spørgsmål

- Hvad gav I bevidst afkald på?
- Hvad troede I ville ske på grund af det?
- Var der et “rigtigt svar”, eller føltes valget reelt?

## Grøn M3-human side

- testerpar gennemfører dagen uden dev-forklaring
- kan beskrive mindst ét tradeoff
- kan forklare hvad en effort marker gjorde
- ingen sekvens har >20 sek. ufrivillig passivitet

M-Pre reducerer risikoen før M1; M3 beviser mekanikken igen i VR.

---

# 7. M4 — delayed consequence test

## Formål

Bevis at en forsinket konsekvens opleves som forståelig årsag/virkning og ikke random straf.

## Minimum test chain

`open food → SCENT_HIGH → animal/camp consequence`

## Testvarianter

- Run A: spillerne sikrer maden
- Run B: spillerne gør det ikke

## Spørg bagefter

- Hvorfor skete hændelsen i nat?
- Kunne I have gjort noget tidligere?
- Føltes konsekvensen fair?

## Grøn

Tester kan forklare mindst én årsagskæde uden at få den fortalt af facilitator.

---

# 8. M5 — storm vertical slice / Release 1 human gate

## Formål

Bevis at stormen er dramatisk samarbejde og ikke bare fem mekaniske chores.

## Før test

Start fra et defineret pre-storm checkpoint med kendt camp state. Brug mindst to forskellige state-profiler:

### Profile A — godt forberedt

- shelter relativt stærkt
- ild okay
- begrænset skade

### Profile B — presset

- shelter svagt
- fire low / consequence tag
- mindst én relevant tidligere konsekvens

Tallene er test fixtures, ikke endelig balance.

## Observer

- om roller fordeles spontant
- om en spiller bliver “instruktør” mens den anden bare udfører
- passive perioder
- om stormens branches kan mærkes
- om spillere forstår, hvad tidligere valg ændrede
- om finale/signalet føles som payoff

## Post-test

- Hvad gjorde stormen sværere i dette run?
- Hvad kunne I have forberedt tidligere?
- Hvornår følte I jer mest pressede?
- Føltes I som et hold?

## Grøn human-side

- begge kan nævne mindst ét tidligere valg der ændrede stormen
- begge havde aktive roller i hver releasekritisk stormfase
- ingen sekvens føles som >20 sek. passiv ventetid
- signalet forstås som fælles slutmål

Teknisk Release 1 kræver desuden Quest 2 performance/soak fra Claude.

---

# 9. M6 — full Stormnatten test

## Formål

Bevis hele 35-45 min oplevelsen.

## Testere

Minimum 2 eksterne par før release; ikke kun udvikleren/gavemodtageren.

## Målinger

- total tid
- intro/tutorial tid
- dag 1/2/3 tid
- storm tid
- after-action tid
- developer interventions
- begge aktive %
- passive periods >12s og >20s
- comfort 15/30/45
- antal misunderstood UI states
- antal retry/reset
- post-session causal understanding

## Grøn

- median 35-45 min
- mål forstået inden for 4 min
- begge aktive ≥70 % action-tid
- ingen udviklerforklaring nødvendig
- begge kan forklare mindst to årsag/konsekvens-forbindelser
- begge kan nævne mindst ét valg de ville ændre ved replay

---

# 10. M8 — personalization/fallback test

## To builds/content states

### A. Neutral

Ingen private assets til stede.

Test:

- hele finale-flowet virker
- ingen placeholder paths/labels
- ingen “missing private asset” synlig som dev-fejl
- neutral message føles som rigtig afslutning

### B. Personal

Privat package er til stede.

Test:

- hooks binder korrekt
- content vises/afspilles kun i epilogen
- ingen private data i logs
- private content ændrer ikke outcome
- samlet personlig sekvens ≤90 sek.

Gavemodtageren bør ikke bruges til almindelig pre-release personalization-QA, hvis overraskelsen skal bevares. Brug neutral eller dummy private content til teknisk test.

---

# 11. M9 — release candidate human test

## Persona

En person, der **ikke skrev installationsguiden**, skal kunne:

1. installere/opdatere build efter den tiltænkte releasevej
2. starte appen
3. etablere sessionen
4. gennemføre scenario uden dev tools
5. finde comfort settings
6. håndtere mindst én kontrolleret reconnect-situation
7. afslutte/replay/exit uden hjælp

## RC observation

Log alle steder, hvor facilitator føler trang til at forklare noget — selv hvis der ikke faktisk hjælpes.

## Grøn

- clean install på begge målheadsets
- session gennemføres uden dev tools
- ingen P0/P1 human-observed issue
- known P2/P3 dokumenteret

---

# 12. Session result template

```markdown
# Playtest result

Build:
Milestone:
Date:
Tester pair:
Devices:
Seated/standing:
VR experience:
Same-room/remote:

## Outcome
- Completed: yes/no
- Developer interventions:
- Crashes/restarts:
- Total time:

## Metrics
- Goal understood at:
- Both-active %:
- Passive >12s:
- Passive >20s:
- UI misunderstandings:
- Resets:

## Comfort
15m:
30m:
45m:

## Top observations
1.
2.
3.

## Player quotes/paraphrases
- 

## Post-session answers
- Important choice:
- Cooperation moment:
- Cause/effect understood:
- Would change next run:
- Replay interest:

## Gate
GREEN / RED / NEEDS_FIX

## Required follow-up
- 
```

---

# 13. Privacy

Human QA notes use tester IDs by default.

Do not commit:

- private names unnecessarily
- health information beyond generic comfort ratings
- private voice recordings
- personal ending content

Audio/video recording of playtests requires explicit participant agreement and should be stored outside repo.

---

# 14. Definition of done

Dette playtest pack er en **facilitator-standard**. Milepælen er ikke grøn, fordi formularen findes; den er grøn, når de krævede mennesker har kørt testen, rå observationer findes, og gatekriterierne er opfyldt.
