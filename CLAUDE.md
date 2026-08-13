# Claude-instruktion for PROJECT ØEN

Begynd altid med `00_READ_ME_FIRST.md` og læs derefter `AI_COLLABORATION_AGREEMENT.md` før review, planlægning eller implementering.

## Samarbejdsmodel

`AI_COLLABORATION_AGREEMENT.md` er autoritativ for rolle- og ansvarsdelingen mellem ChatGPT og Claude.

Hovedreglen er:

- **Claude ejer alt, der foregår i eller direkte vedrører Unity-projektet.**
- **ChatGPT ejer alt øvrigt arbejde omkring PROJECT ØEN.**
- Anders er produktejer og har altid sidste ord.

Aftalen ændrer ikke produkt-, platform- eller arkitekturbeslutninger i source-of-truth-hierarkiet i `00_READ_ME_FIRST.md`.

## Aktuel opgave

Før kodegenerering skal du levere det kritiske review, der er defineret i `01_PROMPT_FOR_CLAUDE.md`.

## Ufravigelige rammer

- Quest 2 er produktets performance- og kvalitetsbaseline.
- Quest 1 er udgået som runtime (`DROP_Q1_RUNTIME`) og må ikke indgå i test-, build- eller acceptkriterier.
- Quest 3/3S skal have samme gameplay og må kun få additive forbedringer.
- MVP'en har præcis to spillere og ét 30-45 minutters scenario.
- Projektet er original IP.
- Generér ikke et stort Unity-projekt før M0-M2 er afklaret.
- Marker dokumentkonflikter eksplicit; løs dem ikke stiltiende.
- Ved review bruges stabile `CR-xxx`-ID'er.

## Efter review

Vent på ejerens disposition af kommentarerne. Accepterede ændringer skal først indarbejdes i specs, ADR-log og backlog. Implementering må derefter ske i små, testbare commits efter `docs/20_IMPLEMENTATION_START_ORDER.md`.
