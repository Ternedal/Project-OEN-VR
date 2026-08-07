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
