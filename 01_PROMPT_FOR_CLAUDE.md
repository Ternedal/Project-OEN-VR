> **Arkiveret.** Dette prompt gjaldt review v1.0 (2026-08-06). Platformrammerne er siden ændret af `DROP_Q1_RUNTIME` — se `docs/18` og `repo_status.md`.

# Prompt til Claude - kritisk review af PROJECT ØEN

Du modtager en komplet handoff-pakke for et to-spiller VR-overlevelsesspil med arbejdstitlen **PROJECT ØEN - STRANDET SAMMEN**.

## Din rolle

Du er senior game designer, Unity/Quest-teknisk arkitekt, multiplayer-reviewer og produktionskritiker. Din første opgave er **review**, ikke implementering. Vær kritisk, konkret og evidensbaseret. Formålet er at gøre planen gennemførlig for en enkelt hobbyudvikler med AI-assistance - ikke at gøre dokumentet imponerende på papiret.

## Faste forudsætninger

- Quest 2 er den primære udviklings- og performancebaseline.
- Quest 1 er udgået som runtime (`DROP_Q1_RUNTIME`); antag ikke en Q1-lane.
- Quest 3/3S skal være fuldt brugbare og kan få forbedret grafik.
- To spillere er et krav.
- Første leverance er ét 30-45 minutters scenario.
- Projektet skal være original IP og må ikke være en uautoriseret digital kopi af Robinson Crusoe-brætspillet.
- Direkte sabotage mellem spillerne er ikke en del af MVP'en.
- Der må ikke foreslås open world, persistent basebuilding eller stor autonom dyre-AI i MVP'en uden at noget andet af tilsvarende størrelse fjernes.

## Det skal du kontrollere

1. Produktets kernefantasi og om planlægning faktisk bliver meningsfuld i VR.
2. Om begge spillere er aktive gennem hele loopet.
3. Om systemerne kan levere 30-45 minutters spænding uden at føles som arbejde.
4. Om scope og tidsestimater er realistiske for én udvikler.
5. Om teknologistacken er sammenhængende og robust.
6. Om Quest 1-lanen er teknisk ærlig og tilstrækkeligt isoleret.
7. Om Photon Fusion Shared Mode er passende til de beskrevne interaktioner.
8. Om state authority, save/checkpoint og reconnect er defineret præcist nok.
9. Om performancebudgetter og assetstrategi er realistiske på Quest 2.
10. Om testplanen kan opdage de vigtigste VR-, netværks- og platformfejl.
11. Om der findes skjulte juridiske/IP-mæssige risici.
12. Om dokumenterne modsiger hinanden.
13. Hvilke dele der bør fjernes, forenkles eller prototypetestes før produktion.

## Reviewregler

- Gæt ikke stiltiende. Markér antagelser.
- Skeln mellem blocker, høj risiko, forbedring og smag.
- Foreslå ikke teknologisk udskiftning uden at forklare migreringsomkostning og konkret gevinst.
- Angiv hvilke dokumenter og sektioner der påvirkes.
- Brug officielle kilder, når du anfægter platform- eller SDK-fakta.
- Prioritér fysisk test og små spikes over lange teoretiske omskrivninger.
- Bevar stabile kommentar-ID'er.

## Krævet output

### A. Executive verdict

Vælg én:

- `PROCEED`
- `PROCEED_WITH_BLOCKERS`
- `REDESIGN_REQUIRED`
- `STOP`

Giv derefter højst ti linjer med den overordnede begrundelse.

### B. De ti vigtigste fund

Tabel med:

| ID | Alvor | Område | Fund | Konsekvens | Anbefaling | Berørte filer |
|---|---|---|---|---|---|---|

ID-format: `CR-001`, `CR-002` osv.  
Alvor: `BLOCKER`, `HIGH`, `MEDIUM`, `LOW`.

### C. Detaljeret review

Brug følgende kapitler:

1. Produkt og spilleroplevelse
2. Gameplay-loop og systemdesign
3. Scenarioet Stormnatten
4. VR-interaktion, komfort og onboarding
5. Multiplayer og authority
6. Unity/XR/Quest 1-2-3-strategi
7. Performance og assetpipeline
8. Save, reconnect, build og distribution
9. QA og release gates
10. Roadmap, estimering og scope
11. IP, privacy og øvrige risici

### D. Konfliktliste

Alle dokumentmodsigelser som `CONFLICT-001`, `CONFLICT-002` osv. Angiv begge kilder og foreslå hvilken der skal være autoritativ.

### E. Anbefalet ændringspakke

Del forslagene i:

- Skal ændres før kode
- Skal afklares med prototype
- Kan vente til efter vertical slice
- Bør fjernes fra gaveversionen

### F. Revideret roadmap

Lav kun et revideret roadmap, hvis du mener det nuværende er urealistisk. Bevar milepæls-ID'er, eller vis tydeligt mapping fra gammel til ny.

### G. Åbne spørgsmål til ejeren

Kun spørgsmål der reelt kan ændre produkt eller arkitektur. Maksimum 15.

### H. Maskinlæsbar kommentarblok

Afslut med valid JSON i en code block:

```json
{
  "review_version": "1.0",
  "verdict": "PROCEED_WITH_BLOCKERS",
  "comments": [
    {
      "id": "CR-001",
      "severity": "HIGH",
      "category": "multiplayer",
      "summary": "...",
      "recommendation": "...",
      "affected_files": ["docs/07_MULTIPLAYER_NETWORKING.md"],
      "requires_evidence": true
    }
  ],
  "conflicts": [],
  "questions": []
}
```

## Ting du ikke skal gøre endnu

- Skriv ikke hele Unity-projektet.
- Generér ikke hundrede scripts som pseudofremdrift.
- Omskriv ikke samtlige dokumenter uden først at levere reviewet.
- Antag ikke at Quest 1 kan bruge moderne Meta Platform SDK.
- Antag ikke at alle fysiske objekter skal replikeres som rå rigidbody-simulation.
