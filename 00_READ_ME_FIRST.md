# PROJECT ØEN - Claude-handoff v2.0

**Dato:** 2026-08-05  
**Status:** Design- og planlægningsbaseline til kritisk review  
**Arbejdstitel:** PROJECT ØEN - STRANDET SAMMEN  
**Format:** To-spiller kooperativt VR-overlevelsesspil  
**Primær platform:** Meta Quest 2  
**Legacy-test:** Meta Quest 1  
**Forbedret platform:** Meta Quest 3 / Quest 3S

## Formål

Denne pakke skal give Claude tilstrækkelig produkt-, design- og teknisk kontekst til at lave et seriøst review af projektet uden at gætte sig til de centrale krav. Claude skal **ikke implementere spillet endnu**. Første opgave er at finde svagheder, modsigelser, urealistiske antagelser, manglende beslutninger og unødvendig kompleksitet.

## Hårde krav

1. Spillet udvikles og profileres primært til Quest 2.
2. En reduceret legacy-build skal kunne testes fysisk på Quest 1.
3. Spillet skal være fuldt brugbart på Quest 3 og Quest 3S og må gerne få visuelle forbedringer dér.
4. Der er præcis to spillere i MVP/gaveversionen.
5. Begge spillere skal være aktive; ingen må fungere som passiv tilskuer i længere sekvenser.
6. Første leverance er et 30-45 minutters, gennemspilleligt scenario - ikke et open-world survival-spil.
7. Projektet er original IP. Det må være inspireret af scenariebaserede survival-brætspil, men må ikke kopiere navn, tekst, illustrationer eller præcise regler fra *Robinson Crusoe: Adventures on the Cursed Island*.
8. Quest 1-kompatibilitet er en **best-effort legacy-testlane**, ikke en begrundelse for at ødelægge Quest 2/3-produktet.

## Source of truth

Ved konflikter gælder denne rækkefølge:

1. `00_READ_ME_FIRST.md` - faste rammer og dokumenthierarki.
2. `docs/01_EXECUTIVE_HANDOFF.md` - gældende produktbeslutninger.
3. `docs/06_TECHNICAL_ARCHITECTURE.md` og `docs/08_PLATFORM_BUILD_PERFORMANCE.md` - tekniske beslutninger.
4. `docs/03_CURRENT_MASTER_SPEC_v1.1.md` - eksisterende samlede baseline.
5. Backlog, eksempler og skemaer - implementeringsdetaljer.

Hvis Claude finder en reel konflikt, skal den markeres som `CONFLICT-xxx` i reviewet frem for at blive løst stiltiende.

## Anbefalet læserækkefølge for Claude

1. `01_PROMPT_FOR_CLAUDE.md`
2. `docs/01_EXECUTIVE_HANDOFF.md`
3. `docs/03_CURRENT_MASTER_SPEC_v1.1.md`
4. `docs/04_GAME_DESIGN_DEEP_DIVE.md`
5. `docs/05_STORMNATTEN_CONTENT_BIBLE.md`
6. `docs/06_TECHNICAL_ARCHITECTURE.md`
7. `docs/07_MULTIPLAYER_NETWORKING.md`
8. `docs/08_PLATFORM_BUILD_PERFORMANCE.md`
9. `docs/12_PRODUCTION_ROADMAP.md`
10. `docs/13_TEST_QA_ACCEPTANCE.md`
11. `docs/14_RISK_SCOPE_BUDGET.md`
12. `review/CLAUDE_REVIEW_TEMPLATE.md`

## Centrale leverancer i pakken

- Komplet GDD og gameplay-specifikation.
- Teknisk arkitektur og netværksmodel.
- Quest 1/2/3-build- og performanceplan.
- Detaljeret scenario-bibel for **Stormnatten**.
- Roadmap, milepæle, stop/go-kriterier og produktionsestimater.
- QA-plan, acceptkriterier og enhedsmatrix.
- Data- og JSON-skemaer med konkrete eksempler.
- Repo-, kode- og CI-standarder.
- Backlog-workbook med epics, stories, tests, risici og reviewlog.
- Prompt og skabelon til Claude-review.

## Hvad der endnu ikke findes

- Ingen Unity-kode eller færdige assets.
- Ingen fysisk kompatibilitetstest er gennemført endnu.
- Ingen licensaftale til Robinson Crusoe-IP; projektet planlægges derfor som original IP.
- Ingen endelig pinning af Unity- og XR-pakkeversioner før platformspiket er bestået på Quest 1, Quest 2 og Quest 3.

## Reviewflow efter Claude

Claude afleverer kommentarer med stabile ID'er (`CR-001`, `CR-002` ...). De behandles i `review/RESPONSE_MATRIX.md` med én af følgende dispositioner:

- **ACCEPT** - indarbejdes direkte.
- **ACCEPT_WITH_MODIFICATION** - problemet accepteres, men løsningen ændres.
- **REJECT** - afvises med konkret begrundelse.
- **DEFER** - relevant, men uden for nuværende milepæl.
- **NEEDS_EVIDENCE** - kræver prototype, måling eller officiel dokumentation.

Ingen større beslutning ændres uden opdatering af `docs/18_DECISION_LOG.md`.
