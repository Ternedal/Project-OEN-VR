# OQ-010 — skal gavebuilden have efterspils-konkurrence?

**Åbent spørgsmål:** `docs/19_OPEN_QUESTIONS.md` OQ-010  
**Designreference:** `docs/04_GAME_DESIGN_DEEP_DIVE.md` §11  
**Ejer:** ChatGPT  
**Status:** Testprotokol klar; resultat afventer målbrugertest

## Hvad testen skal afgøre

PROJECT ØEN er kooperativt mod spillet. Det åbne spørgsmål er, om en let individuel efterspils-score gør oplevelsen mere hyggelig og replayable — eller om den underminerer følelsen af fælles sejr/nederlag.

Testen handler **kun om efterspillet**. Der må ikke indføres skjulte mål eller incitamenter, som påvirker missionen undervejs.

---

## Hypotese

En let, humoristisk efterspilsprofil kan øge lysten til replay uden at skabe sabotage, hvis den:

- først vises efter fælles resultat
- ikke rangerer spillerne med én samlet vinder/taber-score
- beskriver forskellige bidrag frem for “bedst/dårligst”
- ikke belønner handlinger, der skader fælles mål

---

## Varianter

Brug samme afsluttede mini-run eller et neutralt, fiktivt resultatark. Spillerne skal se præcis samme missiondata i begge varianter.

### Variant A — kun fælles efterspil

Vis:

- fælles resultat: reddet / ikke reddet
- 2-3 centrale årsag/konsekvens-linjer
- samlet ressource-/lejrstatus
- forslag om retry/replay

Ingen individuel statistik.

### Variant B — fælles efterspil + individuelle titler

Vis alt fra A og derefter 2-3 individuelle, ikke-hierarkiske titler baseret på bidrag.

Test-eksempler, **ikke canon**:

- “Lejrbyggeren” — størst bidrag til ly/reparation
- “Stifinderen” — mest udforskning
- “Ildvogteren” — flest succesfulde bål-/signalbidrag
- “Risikovillige” — flest højrisikohandlinger
- “Ressourcevogteren” — mindst spild

Undgå:

- samlet pointsum
- “vinder” / “taber”
- titler for sabotage, passivitet eller bevidst spild
- en score der vises før den fælles slutning

---

## Testere

Denne test bør køres på målbrugere eller personer, der ligner målgruppen.

Hvis gaveoplevelsens personlige twist stadig skal være hemmeligt, bruges neutral tekst og neutrale navne. Gavemodtageren må ikke se privat/finalt content under testen.

Mindst 4 par er ønskeligt.

Halvdelen ser A→B, halvdelen B→A.

---

## Procedure

1. Giv parret et kort neutralt efterspilsscenarie.
2. Vis første variant.
3. Lad dem læse den uden forklaring.
4. Registrér spontane reaktioner.
5. Stil skala-spørgsmålene.
6. Vis anden variant.
7. Gentag.
8. Stil sammenligningsspørgsmålene.

Testen skal kunne gennemføres på 10-15 minutter.

---

## Målinger

Efter hver variant vurderer begge 1-5:

| Mål | Spørgsmål | Grøn for B |
|---|---|---:|
| Fællesskab | “Føles resultatet som noget I opnåede sammen?” | median ≥ 4 |
| Replaylyst | “Giver efterspillet lyst til at prøve igen?” | B ≥ A eller median ≥ 4 |
| Sammenligningspres | “Føles det som om én af jer vandt over den anden?” | median ≤ 2 |
| Relevans | “Fortæller efterspillet noget meningsfuldt om jeres forskellige bidrag?” | median ≥ 4 |
| Humør | “Passer tonen til et hyggeligt coop-eventyr?” | median ≥ 4 |

Observer også:

- joker spillerne med titlerne på en positiv måde?
- begynder de at forklare eller forsvare deres individuelle præstation?
- opstår der “jeg vandt”-sprog?
- taler de om at prøve andre bidrag næste gang?

---

## Debrief

1. Hvilken version ville I helst have efter en rigtig mission?
2. Gjorde de individuelle titler oplevelsen mere personlig eller mere konkurrencepræget?
3. Ville titlerne få jer til at spille anderledes næste gang?
4. Er der en risiko for, at man jagter sin egen titel frem for fælles mål?
5. Vil I hellere have **to forskellige anerkendelser** eller én samlet “bedst”-score?
6. Er der en type titel, der ville føles dømmende eller irriterende?

---

## Beslutningsregel

### Behold individuelle efterspilstitler hvis

- fællesskab median ≥ 4
- sammenligningspres median ≤ 2
- replaylyst er mindst lige så høj som A
- ingen tydeligt beskriver lyst til at sabotere/optimere mod fælles mål for at få titel

### Brug kun fælles efterspil hvis

- B reducerer fællesskab
- skaber “vinder/taber”-sprog
- eller får spillere til at fokusere mere på individuel score end årsag/konsekvens

### Hvis B er næsten grøn

Prøv en mildere B2:

- én titel pr. spiller
- ingen numeriske sammenligninger
- titler beskriver stil, ikke rang

---

## Rådata

| Par | Rækkefølge | A fællesskab | A replay | B fællesskab | B replay | B pres | B relevans | B humør | Foretrækker |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | A→B | | | | | | | | |
| 2 | B→A | | | | | | | | |
| 3 | A→B | | | | | | | | |
| 4 | B→A | | | | | | | | |

## Resultat

**Valgt model:** `FÆLLES / FÆLLES+TITLER / B2 / INGEN`  
**Dato:**  
**Begrundelse:**  

## Efter test

- Opdatér OQ-010 i `docs/19_OPEN_QUESTIONS.md`.
- Hvis individuelle ambitioner senere tilføjes, må de stadig ikke belønne sabotage; §11's designregel står fast, medmindre den ændres gennem beslutningsloggen.
