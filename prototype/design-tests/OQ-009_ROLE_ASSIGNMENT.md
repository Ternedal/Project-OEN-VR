# OQ-009 — skal roller vælges eller skifte automatisk?

**Åbent spørgsmål:** `docs/19_OPEN_QUESTIONS.md` OQ-009  
**Relateret:** OQ-007 (rolleasymmetri)  
**Ejer:** ChatGPT  
**Status:** Testprotokol klar; køres først når M-Pre har givet rolleobservationer

## Hvad testen skal afgøre

Sammenlign to måder at håndtere de to spillerroller på:

- **Variant A — valgt/fikseret:** spillerne vælger rolle ved start og beholder den gennem mini-run'et.
- **Variant B — automatisk rotation:** rollerne skifter efter en kendt regel mellem dage/faser.

Spørgsmålet er ikke, hvilken rolle der er “bedst”. Testen måler om **ejerskab** eller **rotation** giver bedre samarbejde uden at skabe lock-in, forvirring eller administration.

---

## Vigtig afgrænsning

De konkrete rolleeffekter i denne test er **prototype-data, ikke canon**.

Testen må først køres, når:

1. M-Pre har vist om der naturligt opstår arbejdsdeling.
2. Der er defineret to midlertidige rolleprofiler med nogenlunde samme power budget.
3. Begge roller har aktivt bidrag og ingen kan reduceres til “hjælperen”.

Navnene `Opfinder` og `Spejder` må gerne bruges som arbejdstitler, fordi `RoleAffinity` allerede findes i designet, men testens midlertidige evner må ikke skrives ind i master-spec som en beslutning.

---

## Minimumskrav til de to prototype-roller

Hver rolle skal have:

- ét område, hvor rollen har **bedre information eller effektivitet**
- ét område, hvor den anden rolle tydeligt er stærkere
- mindst én aktivitet pr. dag, hvor begge roller bidrager samtidigt
- ingen skjult sabotage eller individuelle mål

Power budget skal være symmetrisk nok til, at testen handler om **assignment-modellen**, ikke om at én rolle er åbenlyst stærkere.

---

## Testdesign

### Testere

- mindst 4 par er ønskeligt til dette valg
- samme par prøver begge varianter
- halvdelen starter A→B, halvdelen B→A
- brug ikke gavemodtageren, hvis testen indeholder personlig/finale-content

### Mini-run

Brug en 12-15 minutters papir/fladskærmssekvens med:

- 2 planlægningsrunder
- mindst 3 beslutninger hvor rollekompetencerne er relevante
- mindst 1 situation hvor den “forkerte” rolle må støtte den anden
- samme hændelser og udfald i A og B

Randomness skal enten være fjernet eller forudbestemt. Rollen er den variable, ikke terningen.

---

## Variant A — selvvalgt/fikseret

1. Vis begge rolleprofiler.
2. Spillerne vælger selv hvem der tager hvilken.
3. Roller kan ikke byttes under mini-run'et.
4. Notér hvor lang tid valget tager og hvorfor de vælger som de gør.

### Det måles især

- ejerskab/identifikation
- om en spiller føler sig låst til “sin” type opgaver
- om rollevalget skaber en dominant/passiv arbejdsdeling

---

## Variant B — automatisk rotation

1. Startroller tildeles tilfældigt eller fast efter testplanen.
2. Roller skifter automatisk mellem de to planlægningsrunder.
3. Skiftet varsles tydeligt før næste valg.
4. Spillerne må ikke vælge at beholde rollen i denne variant.

### Det måles især

- om skiftet giver variation eller bare kognitiv friktion
- om spillerne stadig oplever ejerskab
- om begge får bedre forståelse for helheden

---

## Målinger

Efter hver variant vurderer begge spillere 1-5:

| Mål | Spørgsmål | Grøn |
|---|---|---:|
| Rolleclarity | “Vidste du hvad din rolle bidrog med?” | median ≥ 4 |
| Agency | “Føltes det som dit valg/bidrag gjorde en forskel?” | median ≥ 4 |
| Samarbejde | “Fik rollerne jer til at koordinere?” | median ≥ 4 |
| Lock-in | “Følte du dig fastlåst til bestemte opgaver?” | median ≤ 2 |
| Friktion | “Var rollemodellen besværlig at holde styr på?” | median ≤ 2 |

Observer også:

- planlægningstid
- antal gange nogen siger “det er bare din opgave”
- antal gange spillere frivilligt hjælper uden for deres primære rolle
- passivperioder >12 sekunder
- om én spiller tager >70 % af beslutningerne

---

## Debrief

Spørg efter begge varianter:

1. Hvilken model ville I vælge til et 30-45 minutters spil?
2. Hjalp faste roller jer med at føle ansvar, eller låste de jer fast?
3. Gav rotation mere variation, eller føltes det kunstigt?
4. Var der en rolle, I begge helst ville have? Hvorfor?
5. Var der situationer, hvor rollefordelingen stod i vejen for den løsning, I egentlig ønskede?
6. Ville I foretrække en hybrid: valgt rolle, men midlertidigt rollebytte ved bestemte faser?

---

## Beslutningsregel

### Vælg A — selvvalgte/faste roller hvis

- rolleclarity og agency begge er ≥4
- lock-in ≤2
- ingen tydelig dominans/passivitet opstår
- flertallet foretrækker ejerskab frem for rotation

### Vælg B — automatisk rotation hvis

- rotation ikke øger friktion over 2
- bidragene bliver mere jævne
- faste roller giver lock-in eller “det er din opgave”-adfærd

### Hybrid skal undersøges hvis

- A giver stærkt ejerskab men tydelig lock-in
- B giver god variation men lavere rolleidentitet

En hybrid må ikke vælges bare for at undgå en beslutning; den skal testes i en ny, mindre variant.

---

## OQ-007 relation

M-Pre kan vise **naturlig** arbejdsdeling. Denne test viser **påtvungen/eksplicit** rollefordeling.

OQ-007 (“for asymmetriske eller for ens?”) bør først lukkes, når begge evidenskilder er set sammen. Hvis naturlig arbejdsdeling fungerer, men eksplicitte rolleprofiler skaber lock-in, er den rigtige konklusion sandsynligvis mildere rollebonusser — ikke stærkere asymmetri.

---

## Rådata

| Par | Rækkefølge | A clarity | A agency | A coop | A lock-in | B clarity | B agency | B coop | B friktion | Foretrækker |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | A→B | | | | | | | | | |
| 2 | B→A | | | | | | | | | |
| 3 | A→B | | | | | | | | | |
| 4 | B→A | | | | | | | | | |

## Resultat

**Valgt model:** `A / B / HYBRID / INGEN`  
**Dato:**  
**Begrundelse:**  

## Efter test

- Opdatér OQ-009 i `docs/19_OPEN_QUESTIONS.md`.
- Behandl OQ-007 med både M-Pre-observationer og rolletestens data.
- Hvis rollemodellen ændres materielt, registrér beslutningen i `docs/18_DECISION_LOG.md`.
