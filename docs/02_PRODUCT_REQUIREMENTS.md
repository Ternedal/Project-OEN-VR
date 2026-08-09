# Product Requirements Document

## Problem

Mange kooperative VR-spil er enten actiontunge, korte minispil eller symmetriske oplevelser, hvor begge spillere gør det samme. PROJECT ØEN skal give to spillere følelsen af at være afhængige af hinandens prioriteringer, hænder og kommunikation i en samlet dramatisk mission.

## Primære brugere

- To voksne spillere med basal VR-erfaring.
- Kan spille sammen i samme bolig eller over internet.
- Har to Meta Quest-headsets.
- Vil have samarbejde, beslutninger, fysisk interaktion og gensidig drilleri - men ikke et forholdstest-spil.

## Job to be done

> Når vi spiller sammen, vil vi have en fælles udfordring, hvor vores valg og samarbejde skaber en historie, så oplevelsen føles personlig og værd at tale om bagefter.

## Funktionelle krav

### Session og lobby

- Privat session med 5-6 tegns join code.
- Vis headset/build/version og kompatibilitetsstatus.
- Kalibrering af gulvhøjde, siddende/stående og dominant hånd.
- Begge skal markere Ready.
- Ved inkompatibel content hash må sessionen ikke starte.

### Spilflow

- Intro uden lang tekstforklaring.
- Daggry -> planlægning -> handlinger -> skumring -> nat.
- Tre dage i Stormnatten.
- Checkpoint ved begyndelsen af hver dag samt før stormfinalen.
- Fælles resource inventory og individuel health/fatigue/injury state.
- Data-driven event queue med forsinkede konsekvenser.
- Fælles win/lose og efterspilsrapport.

### Multiplayer

- Hoved og hænder synkroniseres.
- Interaktioner giver øjeblikkelig lokal feedback.
- Vigtige resultater valideres af en autoritativ gameplay director.
- Fysiske samarbejdsobjekter må bruge stabiliseret, begrænset fysik frem for rå netværksrigidbody.
- Disconnect håndteres med pause/checkpoint eller kontrolleret reconnect.

### Personligt indhold

- Navne, billeder, lyd og slutbesked ligger i en separat `PersonalizationProfile`.
- Ingen personlige assets i offentligt repo.
- Standardprofil bruges, hvis assets mangler eller fejler validering.

## Ikke-funktionelle krav

- 72 Hz stabil målperformance på Quest 2.
- Ingen vedvarende fysisk aktivitet, der kræver knælen, løb eller gulvkontakt.
- Undertekster på al vigtig tale.
- Venstre-/højrehåndsvalg.
- Teleport som standard; snap turn som standard; smooth locomotion valgfri.
- Maksimalt to klik fra pausemenu til komfortindstillinger.
- Autosave skal være atomisk og versionsmærket.
- Ingen voice recording eller upload af personlige assets.

## Produktmålinger under test

- Tutorial completion uden verbal udviklerhjælp.
- Tid til første meningsfulde fælles beslutning.
- Andel af handlinger hvor begge er aktive.
- Antal situationer med mere end 20 sekunders passiv ventetid (testgrænse; designreglen er 12 sek., jf. `docs/04` §8). Måles fra event-journalen.
- Antal misforståelser der skyldes UI frem for samarbejdsudfordring.
- Komfortscore efter 15, 30 og 45 minutter.
- Framerate og thermal headroom under stormen.
- Reconnect-success og checkpoint-integritet.

## Releasekrav

Se `docs/13_TEST_QA_ACCEPTANCE.md` for målelige gates. Et flot build er ikke releaseklart, hvis det ikke består fysisk test på Quest 2 og regressionstest på Quest 3.
