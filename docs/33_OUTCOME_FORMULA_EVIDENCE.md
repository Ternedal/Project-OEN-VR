# Udfaldsformlen — måling, ikke mening

**Dato:** 2026-08-07 · **Evidens til:** OQ-008 · **Kilde:** `src/ProjectOen.Core.Tests/OutcomeDistributionTests.cs`

## Baggrund

`docs/04` §9 definerede udfaldet som otte additive led uden vægte, skala eller tærskler:

> `Preparation + ToolQuality + RoleBonus + PhysicalExecution + Cooperation - Injury - Weather - EventRisk`

Claude-reviewet (afsnit 2) indvendte, at otte additive led ville lande midt i feltet og gøre `PartialWithCost` til det eneste udfald spillerne ser — læst som *"spillet straffer os uanset hvad"* — og anbefalede at reducere til fire led.

Anbefalingen blev implementeret og derefter **målt**. 20 simulerede runs × 12 handlinger, med stigende spillerkompetence og stigende modstand hen mod stormen.

## Måling 1 — reviewets anbefaling, som den var formuleret

| Tier | 4 led | 8 led |
|---|---:|---:|
| FailForward | 4,2 % | 10,4 % |
| PartialWithCost | **70,0 %** | **68,8 %** |
| Success | 25,8 % | 20,8 % |
| CriticalSuccess | 0,0 % | 0,0 % |

**Reviewets diagnose var forkert.** Fire led klumpede *marginalt værre* end otte (70,0 % mod 68,8 %), og `CriticalSuccess` forekom aldrig i nogen af dem. Antallet af led var ikke årsagen.

Den faktiske årsag: `penalty` blev trukket fra med **fuld vægt** fra en score, hvis positive led summerer til 1,0. Modstanden var dermed det dominerende led i formlen, uanset hvor mange positive led der stod foran den.

Samtidig fejlede en anden test: en perfekt udført sekvens med høj modstand endte som `FailForward` — i direkte modstrid med `docs/04` §9's egen regel om, at tilfældighed ikke må slette en dygtigt gennemført VR-sekvens.

## Rettelsen

To ændringer, begge udledt af `docs/04` §9 frem for af smag:

1. **Modstand er et begrænset modifikator, ikke et ligeværdigt led.** `MaxPenaltyInfluence = 0.35`. Modstand kan koste, men kan ikke eje resultatet.
2. **Gulv-regel.** Modstand kan højst trække udfaldet ét trin ned fra det, den rene præstation fortjente. En perfekt sekvens kan koste dyrt — men kan aldrig blive `FailForward`.

Tærskler justeret én gang: `partial 0.35 / success 0.55 / critical 0.74`. De ligger i data, ikke i kode.

## Måling 2 — efter rettelsen

| Tier | 4 led + gulv | 8 led (uændret) |
|---|---:|---:|
| FailForward | 3,3 % | 20,4 % |
| PartialWithCost | 43,8 % | 58,8 % |
| Success | **47,5 %** | 20,8 % |
| CriticalSuccess | 5,4 % | 0,0 % |

Største enkelt-tier: **47,5 %** mod 70,0 % før. Alle fire kategorier forekommer nu. Fordelingen ligner et spil, hvor dygtighed betaler sig og uheld koster — ikke et spil, der straffer uanset hvad.

## Gates i testen

Testen fejler, hvis:

1. Én enkelt tier dækker ≥ 70 % af udfaldene — så er udfaldet støj, ikke information til spilleren.
2. En udfaldskategori aldrig forekommer.
3. En perfekt udført sekvens (1/1/1) kan blive `FailForward` ved nogen modstandsværdi.

Den oprindelige påstand om "otte led klumper mere end fire" er **trukket tilbage** og fjernet som assertion. Målingen står over formuleringen.

## Forbehold

- Simuleringen bruger en antaget kompetencemodel (0,45 → 0,75 hen over et run, gaussisk støj). Modellen er en antagelse om spillere, ikke en måling af dem.
- Tallene siger noget om **fordelingen**, ikke om hvad der føles fair. OQ-008 er derfor ikke lukket — men den er nu et spørgsmål, der kan stilles til en playtest med et konkret udgangspunkt i stedet for til et tomt felt.
- Tærsklerne skal genkalibreres, når rigtige interaktionsdata findes fra M3.

---

# Tillæg: coop-solveren — samme mønster, andet system

**Dato:** 2026-08-07 · **Kilde:** `src/ProjectOen.Core.Tests/CoopSolverTests.cs`

En test skulle bekræfte det, hele coop-mekanikken hviler på: at den tunge kasse bevæger sig langsommere med én hånd end med to. Den fejlede.

Årsagen var ikke en fejl i implementeringen af den skrevne plan — den var i planen. Solveren dæmper responsiviteten ved ét greb (faktor 0,4), men hastighedsloftet var det samme i begge tilstande. Så snart objektet er mere end få centimeter fra hånden, klipper loftet begge tilstande til nøjagtig samme skridt, og forskellen forsvinder. "Tung kasse kræver to spillere" ville kun kunne mærkes tæt på målet — altså præcis dér, hvor det er mindst dramatisk.

**Rettelse:** `SingleHandSpeedFactor = 0.4`. Hastighedsloftet sænkes nu sammen med responsiviteten.

**Hvad testen ellers dokumenterer:**

- Et hånd-target der hopper 50 meter væk (en enkelt dårlig pose-pakke) flytter objektet maksimalt 0,0278 m i det frame — hastighedsloftet ved 72 Hz. Det er mekanismen, der holder to klienters jitter ude af resultatet, jf. ADR-012.
- Et enkelt frame med sprængt gribeafstand koster under 10 % kvalitet; vedvarende dårligt greb i ~2,8 s bringer den til 0,02. `docs/04` §7's "falder gradvist frem for at nulstille" er dermed håndhævet, ikke bare beskrevet.
- Kvaliteten kan genvindes, når grebet genoprettes. Uden det ville en enkelt fejl gøre resten af sekvensen meningsløs.

## Mønsteret er værd at bemærke

To gange på én dag har en test modsagt et dokument, som var skrevet med omhu. Begge gange var fejlen usynlig ved gennemlæsning og åbenlys ved måling. Det er argumentet for, at Core-laget er rent C# og testbart uden headset: de her fejl ville ellers først være dukket op på en Quest, midt i en playtest, uden nogen der kunne pege på årsagen.

---

# Tillæg 2: stormen skar den optjente konsekvens væk

**Dato:** 2026-08-07 · **Kilde:** `src/ProjectOen.Core.Tests/StormTests.cs`

Stormen har et loft på tre samtidige komplikationer — uden det giver en dårlig gennemgang en uspillelig ophobning i et 12-16 minutters vindue. Loftet skar efter severity: værst først.

En test af, at hver komplikation bærer sin årsag, afslørede konsekvensen. I værste tilfælde valgte stormen:

```
STM_SIGNAL_MAST_005 (sev 5) <- signalProgress 80 >= 60
STM_ROOF_TEAR_002   (sev 4) <- shelterIntegrity 20 <= 40
STM_FIRE_OUT_003    (sev 3) <- fireStrength 10 <= 25
```

`STM_ANIMAL_RETURN_004` — dyret der vender tilbage, fordi maden blev efterladt åben på dag 1 — blev skåret væk. Den har severity 2.

Det er ikke tilfældigt. **Tag-drevne komplikationer sporer tilbage til en konkret spillerbeslutning, og de har systematisk lavere severity end strukturelle svigt.** Et rent severity-loft skærer derfor netop de konsekvenser væk, spillerne selv har optjent. Stormen ville vise generiske katastrofer og skjule den ene ting, hele scenariet har bygget op til.

**Rettelse:** mindst én plads reserveres til en tag-drevet komplikation, når en sådan kvalificerer sig. Samme værste tilfælde giver nu:

```
STM_SIGNAL_MAST_005 (sev 5) <- signalProgress 80 >= 60
STM_ROOF_TEAR_002   (sev 4) <- shelterIntegrity 20 <= 40
STM_ANIMAL_RETURN_004 (sev 2) <- SCENT_HIGH
```

## Sidefund: EffectApplier var asymmetrisk

Den samme testrunde viste, at `EffectApplier` håndterede `RemoveTags`, men ikke `AddTags` — tags blev tilføjet af direktoren, fordi de skulle bære proveniens. En effekt anvendt uden for direktoren, som en stormkomplikation, tabte derfor sine tags stiltiende.

Rettet: applier'en tager en `sourceId` og ejer hele effekten. Én vej ind i state, ét journaliseringspunkt.

## Fjerde gang

Det er nu fire fund fra tests mod dokumenter og kode, der så rigtige ud: udfaldsformlens klumpning, coop-solverens hastighedsloft, dobbelt-journaliseringen, klientens kontrol over sin egen straf — og nu stormens prioritering. Ingen af dem var synlige ved gennemlæsning.
