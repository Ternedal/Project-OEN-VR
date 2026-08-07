# Game design deep dive

## 1. Designhypotese

Spændingen opstår ikke af, at spilleren er dårlig til at hugge træ. Den opstår af, at to spillere har for lidt tid, utilstrækkelig information og forskellige idéer om, hvad der er vigtigst. VR-interaktionen skal gøre konsekvensen fysisk og nærværende, men må ikke drukne strategien i gentagelser.

## 2. Kerne-loop

1. **Observer:** Vejr, skader, lejrstatus og nye spor præsenteres diegetisk.
2. **Diskutér:** Spillerne taler om risiko og prioritet.
3. **Allokér:** Fire indsatsmarkører fordeles på dagens handlinger.
4. **Udfør:** Korte fysiske sekvenser med to aktive roller.
5. **Betal:** Ressourcer, udmattelse og tid opdateres.
6. **Afslør:** Immediate og delayed events behandles.
7. **Overlev natten:** Lejrens kvalitet og spillernes valg testes.
8. **Lær:** Næste dag viser, hvad der virkede og hvad der blev værre.

## 3. Handlingsøkonomi

Hver spiller har to indsatsmarkører pr. dag. En handling kan modtage:

- **0 markører:** Ikke udført.
- **1 markør:** Hurtig/risikabel udførelse. Én spiller udfører; den anden får en kort støtteopgave.
- **2 markører:** Sikker kooperativ udførelse med bedre kvalitet eller lavere event-risk.
- **3+ markører:** Kun særlige scenariehandlinger; bruges ikke i standardloopet.

Der skal altid være flere værdifulde handlinger end tilgængelige markører. Hvis et oplagt korrekt svar findes hver dag, er planlægningen mislykket.

## 4. Ressourcemodel

| Ressource | Funktion | Designregel |
|---|---|---|
| Træ | Bål, ly, reparation | Let at forstå, tungt at transportere |
| Fiber | Reb, binding, tag | Binder crafting og stormforberedelse sammen |
| Mad | Undgå udmattelse/moraleproblem | Må aldrig kræve lang jagtgrind |
| Urter | Sår og sygdom | Sjælden nok til at skabe reelt valg |
| Gløder/ild | Progression og signal | Sårbar, dramatisk, fysisk håndterbar |
| Tid/indsats | Primær knaphed | Kan ikke farmes |

Ressourcer er fælles. Der er ingen individuel loot-ejerskab i MVP'en.

## 5. Personstatus

Hver spiller har:

- `Health` 0-100.
- `Fatigue` 0-100.
- 0-3 aktive `Injury`-tags.
- `Cold/Wet` som midlertidige modifiers.
- `RoleAffinity` for Opfinder/Spejder, kun som mild bonus.

Status påvirker tempo, rystelser, lyd og risikovurdering. Det må ikke skabe så meget motorisk straf, at en skadet spiller bliver fysisk frustreret i VR.

## 6. Lejrstatus

- `ShelterIntegrity`.
- `FireStrength`.
- `FoodSecurity`.
- `SignalProgress`.
- `CampThreat`.

Lejren er den fælles karakter. Stormfinalen læser disse værdier og konverterer dem til konkrete komplikationer.

## 7. Fysisk udførelse

En interaktion består af:

1. Tydelig invitation.
2. Korrekt greb eller placering.
3. 5-20 sekunders koordineret handling.
4. Delvis succes er mulig.
5. Resultat vises fysisk og opsummeres kort.

Eksempel: tagforstærkning

- Spiller A holder en bjælke i en bred stabiliseringszone.
- Spiller B fører reb gennem tre store snap-punkter.
- Hvis A mister stabiliteten, falder kvalitet gradvist frem for at nulstille.
- To succesfulde bindinger giver funktionelt tag; tredje giver kvalitetsbonus.

## 8. Begge-spillere-aktive-regel

Hver action-sekvens dokumenterer to roller:

- **Primær:** udfører den synlige kernehandling.
- **Sekundær:** navigerer, stabiliserer, observerer, forbereder eller beskytter.

En sekundær rolle må ikke blot være “se på”. Den skal ændre sandsynlighed, kvalitet eller tid.

Maksimal passiv periode: **12 sekunder** som designregel, medmindre der foregår en dramatisk sekvens, som begge observerer.

Designreglen (12 sek.) og testgrænsen (20 sek. i `docs/05` og `docs/13`) er bevidst forskellige: designet sigter mod 12, og en playtest fejler først ved 20. Begge tal måles automatisk fra event-journalen, ikke ved observation — se `docs/13` UX-002.

## 9. Usikkerhed og retfærdighed

Udfaldsscore:

**Revideret 2026-08-07 efter måling — se [`33_OUTCOME_FORMULA_EVIDENCE.md`](33_OUTCOME_FORMULA_EVIDENCE.md).**

Oprindelig formulering (bevaret for sporbarhed):

`Preparation + ToolQuality + RoleBonus + PhysicalExecution + Cooperation - Injury - Weather - EventRisk`

Gældende model:

`base = 0,30·Preparation + 0,45·PhysicalExecution + 0,25·Cooperation`
`score = base − Penalty · 0,35`

hvor `Penalty` er skade, vejr og event risk lagt sammen af kaldstedet. Modstand er et **begrænset modifikator**, ikke et ligeværdigt led: med fuld vægt blev det det dominerende led og kollapsede 70 % af alle udfald til én kategori. Det blev målt, ikke gættet.

Dertil en **gulv-regel**: modstand kan højst trække udfaldet ét trin ned fra det, den rene præstation fortjente. En perfekt udført sekvens kan koste dyrt, men kan aldrig blive "Fejl med fremdrift". Det er §9's egen regel, nu håndhævet i kode og test.

Scoren mappes til:

- Kritisk succes.
- Succes.
- Delvis succes med omkostning.
- Fejl med fremdrift.

Ren “ingen effekt”-fejl bruges næsten aldrig. Tilfældighed må modificere omkostningen, men ikke slette en dygtigt gennemført VR-sekvens uden forklaring.

## 10. Delayed consequences

Hændelser bruger tags og deadlines:

- Åben mad -> `SCENT_HIGH`.
- `SCENT_HIGH` + nat 2 -> mulig dyretrussel.
- Dårligt tag -> `SHELTER_WEAK`.
- `SHELTER_WEAK` + storm -> ekstra reparationsnode.
- Ubehandlet sår -> `INFECTION_RISK`.
- `INFECTION_RISK` + våd/kold -> reduceret stabilitet i finalen.

Efterspilsrapporten viser årsagskæden. Spilleren skal kunne forstå: “Det skete, fordi vi valgte X tidligere.”

## 11. Konkurrence uden sabotage

MVP'en er kooperativ mod spillet. Let konkurrence kommer efter missionen gennem:

- Flest redninger.
- Bedste håndværk.
- Mest udforskning.
- Færrest spildte ressourcer.
- Største risiko.
- “Kaosagenten”.

Valgfrie personlige ambitioner kan tilføjes efter vertical slice, men må ikke belønne sabotage eller skjult ødelæggelse af fælles mål.

## 12. Difficulty og dynamisk hjælp

Tre profiler:

- **Historie:** større snap-zoner, tydeligere prognoser, mildere events.
- **Standard:** designbaseline.
- **Barsk:** færre ressourcer og mindre event-information, men ingen kunstig health-bloat.

Dynamisk hjælp kan:

- forlænge interaktionsvindue,
- fremhæve næste snap-zone,
- reducere sekundære komplikationer,
- give et ekstra hint ved lejrbålet.

Den må ikke ændre allerede afslørede regler midt i en handling.

## 13. Replayability

Gaveversionen skal kunne spilles 2-4 gange gennem:

- 2-3 vejrvarianter.
- 8-12 event chains, hvor 4-6 vælges pr. run.
- alternative action opportunities.
- efterspils-titler.
- scenario seed med kontrolleret variation.

Målet er ikke endeløs procedural replayability.

## 14. Fail states

Fælles nederlag kan komme af:

- Begge spillere incapacitated.
- Ilden og lyet kollapser i stormens sidste fase.
- Signalvinduet misses efter finalen.

Ved nederlag vises en kort årsagskæde og tilbud om retry fra før stormen eller begyndelsen af dag 3. Hele missionen behøver ikke genstartes.

## 15. Design-gates

- Planlægning skal skabe mindst ét reelt valg i første eksterne test.
- Ingen sekvens må kræve over 30 sekunders gentagen fysisk bevægelse.
- Mindst 70 % af action-tiden skal have aktivt bidrag fra begge.
- Spillere skal kunne forklare mindst to årsag/konsekvens-forbindelser efter missionen.
- Stormen skal føles forskellig afhængigt af mindst tre tidligere valg.
