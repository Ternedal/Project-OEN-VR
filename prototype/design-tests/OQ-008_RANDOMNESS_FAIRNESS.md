# OQ-008 — hvor meget randomness føles fair?

**Åbent spørgsmål:** `docs/19_OPEN_QUESTIONS.md` OQ-008  
**Designregel:** `docs/04_GAME_DESIGN_DEEP_DIVE.md` §9  
**Ejer:** ChatGPT  
**Status:** Testprotokol klar; resultat afventer mennesketest

## Hvad testen skal afgøre

Spillet skal have usikkerhed nok til at skabe spænding, men ikke så meget at spillernes planlægning og dygtige udførelse føles ligegyldig.

Den eksisterende designregel står fast under testen:

> Tilfældighed må ændre omkostningen eller kvaliteten, men må ikke uden forklaring slette tydelig fremdrift fra en god beslutning/udførelse.

Testen måler derfor **intensiteten af randomness**, ikke om spillet skal være rent binært success/fail.

---

## Hypotese

En komplikationsrisiko på ca. **1/3** giver mere spænding end ca. **1/6** uden at fairness og agency falder under acceptabelt niveau, når spilleren stadig får fremdrift.

Hvis 1/3 opleves urimelig, bruges 1/6 som baseline og større usikkerhed skabes gennem skjult information/tradeoffs frem for højere tilfældighed.

---

## Testdesign

### Testere

- 6-10 personer er tilstrækkeligt til et tidligt retningsvalg.
- Samme person prøver begge varianter.
- Rækkefølgen counterbalances: halvdelen A→B, halvdelen B→A.
- Testen må gerne bruges på M-Pre-testere efter deres M-Pre-session, så længe denne test præsenteres separat.

### Fælles scenarie

Giv spilleren samme korte beslutning seks gange pr. variant:

> I har valgt at reparere lyet før stormen. Arbejdet lykkes funktionelt, men vejret kan skabe en ekstra omkostning. Slå d6.

Fremdriften forsvinder aldrig. Terningen afgør kun om der kommer en komplikation.

### Variant A — lav randomness

- d6 = **1** → fremdrift + komplikation
- d6 = **2-6** → fremdrift uden komplikation
- Risiko: **16,7 %**

Eksempel på komplikation:

> Lyet bliver repareret, men I bruger én ekstra forsyning.

### Variant B — moderat randomness

- d6 = **1-2** → fremdrift + komplikation
- d6 = **3-6** → fremdrift uden komplikation
- Risiko: **33,3 %**

Samme komplikationstekst som A.

**Vigtigt:** Brug præcis samme gevinst og omkostning i begge varianter. Kun sandsynligheden må ændres.

---

## Procedure

For hver variant:

1. Fortæl komplikationsrisikoen åbent før første slag.
2. Lad testeren gennemføre seks identiske udfald.
3. Efter hvert slag: spørg kun “føles det rimeligt?” og registrér Ja/Nej uden diskussion.
4. Efter sjette slag udfylder testeren vurderingsskalaerne.
5. Gå derefter til den anden variant.
6. Efter begge: bed testeren vælge den variant, de helst ville have i et 30-45 minutters coop-spil.

Terningesekvenser bør på forhånd være balancerede, så én tester ikke tilfældigvis får seks gode udfald i én model og seks dårlige i den anden. Brug enten forudtrukne sekvenser eller samme antal komplikationer skaleret efter den nominelle risiko.

---

## Målinger

Efter hver variant vurderes 1-5:

| Mål | Spørgsmål | Grøn |
|---|---|---:|
| Fairness | “Føltes udfaldene fair?” | median ≥ 4 |
| Agency | “Føltes dit valg stadig vigtigt?” | median ≥ 4 |
| Spænding | “Skabte usikkerheden spænding?” | median ≥ 3 |
| Frustration | “Hvor frustrerende var tilfældigheden?” | median ≤ 3 |
| Forståelse | “Kunne du forudsige risikoen?” | ≥ 80 % Ja |

Derudover:

- foretrukken variant A/B
- kommentarer der forklarer hvorfor
- hvor ofte et komplikationsudfald efterfølgende blev kaldt “uretfærdigt”

---

## Beslutningsregel

### Vælg B (33,3 %) som standard baseline hvis

- fairness median ≥ 4
- agency median ≥ 4
- frustration median ≤ 3
- mindst halvdelen foretrækker B eller vurderer A som for tam

### Vælg A (16,7 %) hvis

- B fejler fairness eller agency
- eller tydeligt opleves som “spillet bestemmer for meget”

### Ingen af dem er grønne

Hvis begge fejler, er problemet sandsynligvis ikke procentsatsen alene. Undersøg:

1. om komplikationen er for hård
2. om risikoen er dårligt kommunikeret
3. om spillerens forberedelse bør reducere risikoen
4. om randomness bør flyttes fra udfald til eventvalg/timing

Hæv **ikke** bare succesprocenten uden at diagnosticere årsagen.

---

## Rådata

| Tester | Rækkefølge | A fairness | A agency | A spænding | A frustration | B fairness | B agency | B spænding | B frustration | Foretrækker |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | A→B | | | | | | | | | |
| 2 | B→A | | | | | | | | | |
| 3 | A→B | | | | | | | | | |
| 4 | B→A | | | | | | | | | |
| 5 | A→B | | | | | | | | | |
| 6 | B→A | | | | | | | | | |

## Resultat

**Valgt baseline:** `A / B / INGEN`  
**Dato:**  
**Begrundelse:**  

## Efter test

- Opdatér OQ-008 i `docs/19_OPEN_QUESTIONS.md`.
- Hvis resultatet ændrer den gældende usikkerhedsmodel, opret/ændr beslutning gennem `docs/18_DECISION_LOG.md` frem for at ændre §9 stiltiende.
- Oversæt først resultatet til konkrete Stormnatten-tal, når content-/balanceringsgaten tillader det.
