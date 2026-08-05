# Executive handoff

## Produkt i én sætning

Et to-spiller VR-overlevelsesspil, hvor spillerne ved daggry fordeler deres begrænsede tid og derefter fysisk gennemfører opgaverne på en fjendtlig ø, som husker deres valg og returnerer konsekvenserne under en afsluttende storm.

## Produktmål

Den første version skal være en personlig, poleret gaveoplevelse, som to personer kan gennemføre på én aften. Den skal føles som et rigtigt spil og ikke som et virtuelt fotoalbum eller et brætspilsbord i VR.

## Spillerløfte

> Vi lægger en plan sammen, udfører den med hænderne og opdager senere, om vores prioriteringer reddede os eller gjorde stormen værre.

## MVP/gaveversion

- Ét scenario: **Stormnatten**.
- Tre fiktive døgn.
- 30-45 minutters samlet spilletid.
- To spillere, hver med eget headset og egen installation.
- Fælles planlægning, ressourcevalg, fysisk crafting/byggeri og forsinkede konsekvenser.
- Fælles sejr eller nederlag.
- Individuelle efterspils-titler og statistik, men ingen direkte sabotage.
- Personligt indhold indlæses som data/assets og har neutral fallback.

## Ikke-mål

- Open world.
- Proceduralt genereret ø.
- Permanent base eller lang progression.
- Realistisk sult-/tørstsimulator.
- Stor våben- eller kampsimulation.
- Håndtracking som krav.
- Mixed reality/passthrough.
- Offentlig matchmaking.
- Mere end to spillere.
- Officiel Robinson Crusoe-licens i første fase.

## Platformbeslutning

| Platform | Rolle | Krav |
|---|---|---|
| Quest 2 | Autoritativ baseline | Alle gameplay-, performance- og komfortbeslutninger valideres her. Stabil 72 Hz er releasekrav. |
| Quest 3 / 3S | Forbedret målplatform | Samme gameplay og netværk. Højere opløsning, skarpere teksturer og flere visuelle effekter må aktiveres. |
| Quest Pro | Sekundær kompatibilitet | Følger som udgangspunkt Quest 2-profilen; ikke særskilt optimeringsmål. |

## Teknisk anbefaling

- Unity 6 LTS 6000.3.x som baseline med Unity OpenXR Plugin og XRI 3.x (ADR-020). Betinget af engine-baseline-gaten i M0.
- OpenXR og XR Interaction Toolkit som kerne.
- Ingen afhængighed af moderne Meta Platform SDK i det delte gameplaylag.
- URP, Vulkan først; OpenGLES3 holdes kun som fallback under platformspiket.
- Photon Fusion 2 Shared Mode til to-spiller-sessioner.
- Data-driven scenarios, events, items og recipes via ScriptableObjects med JSON-validerbare eksportformater.
- Én kodebase, men tre buildprofiler og betingede pakker/features.

## Den vigtigste tekniske usikkerhed

Det er endnu ikke fysisk bevist, at den valgte kombination af Unity-, OpenXR- og netværkspakker kan producere kompatible builds til Quest 2 og Quest 3 uden at låse projektet til forældede SDK'er. Derfor er platformspiket **M0** og må bestås før contentproduktion.

## Den vigtigste designusikkerhed

Planlægningsfasen kan blive administrativ frem for dramatisk. Den første playtest skal bevise, at fire indsatsmarkører skaber reel diskussion og mærkbare konsekvenser uden at kræve lange forklaringer.

## Produktionsstrategi

1. Bevis platform og netværk.
2. Bevis fysisk samarbejde med én tung kasse.
3. Bevis én komplet dagcyklus.
4. Bevis konsekvenskæde og stormfinale.
5. Saml vertical slice.
6. Først derefter: art pass, personligt indhold og gavepolish.

## Estimat

Der bruges tre estimatniveauer, så det detaljerede backlogark ikke forveksles med den korteste vej til en gaveversion:

| Niveau | Omfang | Estimat |
|---|---|---:|
| Kritisk P0-sti | Platform, multiplayer, kerneflow, storm og release-blockers | ca. 620 timer |
| Poleret gaveversion | P0 plus udvalgte P1-opgaver, købte assets og stram scopekontrol | 500-810 timer |
| Fuld engineering-backlog | Alle 108 planlagte P0/P1/P2-opgaver, maksimal hardening og polish | ca. 1.447 timer før usikkerhedsbuffer |
| Release 1 (M-Pre + M0-M5) | Afsendbar gave: 1 dag + storm i tre faser (ADR-022) | ca. 340-470 timer, lav konfidens |

Roadmappets faseintervaller beskriver den fokuserede gavevej. Backlog-workbookens timesum er bevidst konservativ og inkluderer værktøj, automatisering, gentagne device-tests, hardening og flere opgaver, som kan skæres eller købes som assets. Ved 15 timer om ugen svarer den fokuserede gaveversion groft til 8-13 måneders arbejde; den fulde backlog svarer snarere til 18-27 måneder. Det er planlægningsrammer, ikke løfter.

**Release 1 (ADR-022) er det primære gavemål** og estimeres til ca. 340-470 timer, svarende til 5,5-7,5 måneder ved 15 t/uge. Estimatet er afledt og har lav konfidens; M3-M4 er ikke dækket af selvstændige tal og skal genberegnes mod backlog-workbooken.

## Definition af succes

Gaveversionen er først færdig, når:

- To ikke-udviklere kan installere, forbinde og gennemføre uden hjælp.
- Quest 2 holder performancekrav gennem stormen.
- Quest 3 gennemfører regressionstest uden gameplayafvigelser.
- En midlertidig netværksfejl eller standby fører til kontrolleret genoptagelse eller tydelig tilbagevenden til checkpoint.
- Den personlige finale virker men kan fjernes uden at ødelægge spillet.
- Ingen kendte P0/P1-fejl eksisterer.
