# Scenario-bibel: STORMNATTEN

## Scenario-ID

`SCN_STORMNATTEN_001`

## Logline

Tre dage efter et skibbrud opdager to overlevende et kommende skibsspor. De skal holde sig i live, bygge et signal og beskytte deres skrøbelige lejr gennem en voldsom storm, før redningsvinduet lukker.

## Varighed

- Intro/tutorial: 5-7 min.
- Dag 1: 8-10 min.
- Dag 2: 10-12 min.
- Dag 3 forberedelse: 5-7 min.
- Storm/finale: 7-9 min.
- Efterspil: 2-3 min.

Måltotal: 32-48 min.; content skal trimmes, hvis medianen overstiger 45 min.

## Dramaturgisk struktur

### Beat 0 - Vraget

- Spillerne vågner på stranden få meter fra hinanden.
- Første mål: frigør en fastklemt kasse ved at løfte sammen.
- Kassen indeholder ildstål, klud, kortfragment og radio uden strøm.
- Tutorial lærer: bevægelse, greb, fælles løft og ping.

### Beat 1 - Første ild

- Den ene holder materiale tørt og beskytter mod vind.
- Den anden tænder med ildstål.
- Fejl reducerer tinder-kvalitet, men nulstiller ikke.
- Lejrbålet bliver planlægnings- og savepunkt.

### Beat 2 - Dag 1-planen

Tilgængelige handlinger:

- Saml træ.
- Find mad.
- Byg læside.
- Udforsk klippestien.
- Sikr forsyninger.

Kun to kooperative handlinger eller fire risikable solohandlinger kan prioriteres.

### Dag 1 events

- `EVT_OPEN_FOOD_001`: Mad efterladt utilstrækkeligt sikret.
- `EVT_SPLINTER_001`: Mindre håndskade ved dårlig tool quality.
- `EVT_DISTANT_SMOKE_001`: Udforskning afslører mulig menneskelig aktivitet; teaser, ikke gameplaygren i MVP.

### Nat 1

- Mild regn.
- Shelter quality og fire strength demonstreres.
- Ingen hård fail state.
- Radioen udsender svagt fragment: et skib forventes om to døgn.

### Dag 2 - Varslet

Morgeninformation:

- Kraftigt fald i lufttryk.
- Fugle forlader området.
- Spillerne får tydelig, men ikke fuldstændig stormprognose.

Nye handlinger:

- Forstærk tag.
- Find fiber.
- Find urter.
- Byg signalstativ.
- Udforsk højderyg.
- Behandl skade.

### Dag 2 centerpiece

`SEQ_RAVINE_RESCUE_001`

- Spejderen krydser en kort kløft eller skråning.
- Opfinderen styrer rebspænding og viser sikre greb via farvede markeringer.
- En fejl skaber skade/udmattelse, men sekvensen fortsætter.
- Roller kan byttes afhængigt af spillerens valg.

### Nat 2 branches

**A. Dyretrussel** hvis `SCENT_HIGH`:

- Lyde uden for lejren.
- Én holder ild og laver støj; én sikrer mad.
- Forkert reaktion kan beskadige shelter eller stjæle food.

**B. Taglækage** hvis `SHELTER_WEAK`:

- Kort fysisk reparation under regn.
- Wet/cold modifier næste morgen, hvis den mislykkes.

**C. Rolig nat** hvis forberedelserne var gode:

- Spillerne får ekstra tid til signal eller behandling.
- Belønning er konkret og ikke bare score.

### Dag 3 - Sidste vindue

- Radioen får strøm nok til at bekræfte skibets rute.
- 4-6 minutters sidste planlægning.
- Spillerne skal vælge mellem signal, lejr, medicin og mad.
- Et “perfekt” run er muligt, men kræver gode tidligere valg; standardrun indebærer mindst én komplikation.

## Stormfinale

### Fase 1 - Vind

- Hold tag/bjælke stabilt.
- Fastgør to løse reb.
- Komplikationer aktiveres fra `SHELTER_WEAK` og tool quality.

### Fase 2 - Regn og ild

- Beskyt gløder med fysisk skærm.
- Hent tørt brændsel fra en kort, sikker rute.
- `FIRE_LOW` reducerer tilgængelig tid.

### Fase 3 - Skade eller dyretrussel

- Event-slot vælges fra tidligere tags.
- Spillerne må fordele roller hurtigt.
- Ingen fuld combat. Afværgning, stabilisering og reparation.

### Fase 4 - Kollaps

- En central konstruktion svigter delvist.
- Begge skal løfte/stabilisere og snap-reparere.
- Dette genbruger den tekniske prototype med den tunge kasse i dramatisk kontekst.

### Fase 5 - Signal

- Ved daggry bæres gløder/ildkilde til signalstativet.
- Én beskytter flammen; én rydder/aktiverer signalet.
- Quality påvirker antændelsestid, ikke om spillerne får lov til at prøve.

## Win states

### Stærk sejr

- Begge står oprejst.
- Signal tændes inden for vinduet.
- Lejren overlever.

### Presset sejr

- Signal tændes, men én spiller er stærkt skadet eller lejren kollapser bagefter.

### Nederlag

- Ilden tabes permanent og signal kan ikke tændes.
- Begge incapacitated.
- Signalvinduet overskrides efter flere fail-forward-forsøg.

## Personlig finale

Efter skibet har set signalet:

- Vejret falder til ro.
- En vandtæt kasse eller radio åbnes.
- Personlig lyd/besked afspilles.
- 3-5 genstande kan referere til fælles oplevelser.
- Sekvensen må maksimalt vare 90 sekunder og må kunne erstattes af neutral ending.

## Content inventory for MVP

### Scener

- Boot/Lobby.
- Strand/lejr persistent.
- Junglesti.
- Kløft/højderyg.
- Stormvariant af lejren.
- Efterspilsområde eller lejrbåls-epilog.

### Interaktive systemobjekter

- 8 ressourceprefabs.
- 4 værktøjer.
- 3 konstruktionsstages for shelter.
- Signalstativ i 3 stages.
- Lejrbål i 4 states.
- 4 planlægningsmarkører.
- 1 radio.
- 1 tung kasse.
- 1 reb-/stabiliseringssystem.

### Events

Minimum 10 event definitions:

1. Åben mad.
2. Dyr ved lejren.
3. Splint/småskade.
4. Ubehandlet sår.
5. Taglækage.
6. Knækket værktøj.
7. Tørt brændsel fundet.
8. Ekstra urter.
9. Røg på afstand.
10. Radiofragment.

## Tutorialtekstprincip

- Maks. én kort sætning ad gangen.
- Vis hånd/objekt-fremhævning før tekst.
- Gentag kun efter 8-10 sekunders manglende fremdrift.
- Ingen voice line må blokere interaktion.

## Acceptkriterier for scenariet

- Ekstern testgruppe forstår målet inden for 4 minutter.
- Mindst ét tidligere valg ændrer hver stormfase.
- Median gennemspilning 35-45 minutter.
- Spillere oplever ingen sekvens med >20 sekunders ufrivillig passivitet (testgrænse; designreglen er 12 sek., jf. `docs/04` §8).
- Begge kan nævne mindst ét valg, de ville ændre i næste run.
