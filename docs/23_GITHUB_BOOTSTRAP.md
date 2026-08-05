# GitHub-bootstrap

## Repository

- **Navn:** `Ternedal/Project-OEN-VR`
- **Visibility:** Private
- **Default branch:** `main`
- **Beskrivelse:** `Two-player scenario-based VR survival game for Meta Quest 2, with Quest 1 legacy testing and Quest 3 enhancements.`

## Første fase

Repositoryet indeholder først design-, review- og engineeringgrundlaget. Unity-projektet oprettes først efter Claude-reviewet og M0-beslutningen om editor- og package-matrix.

## Anbefalede brancher

- `main` - godkendt source of truth.
- `agent/m0-platform-feasibility` - første tekniske spike.
- efterfølgende korte `agent/<opgave>`-brancher.

## Første issue

**Titel:** `M0: Bevis fælles Quest 1/2/3 platformlane`

**Definition of done:**

1. Minimal build starter på Quest 1, Quest 2 og Quest 3.
2. Q1-Q2 og Q2-Q3 kan forbinde i en privat session.
3. Begge spillere kan løfte og snap'e det samme coop-objekt.
4. Package-, graphics API- og manifestmatrix er dokumenteret med faktiske testresultater.
5. Der er truffet en eksplicit `GO`, `REDESIGN` eller `DROP_Q1_RUNTIME`-beslutning.

## Repository settings

- Branch protection på `main` efter første arbejdende CI.
- Kræv pull request og grøn `Validate handoff`.
- Slå secret scanning til, hvis tilgængeligt.
- Commit aldrig keystore, signing credentials eller private personaliseringsassets.
- Brug Git LFS først, når reelle Unity-binaries/kunstassets tilføjes.
