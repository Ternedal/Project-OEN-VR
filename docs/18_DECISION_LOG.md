# Architecture and product decision log

| ADR | Status | Beslutning | Begrundelse | Konsekvens |
|---|---|---|---|---|
| ADR-001 | Accepted | Original IP under PROJECT ØEN | Undgår uautoriseret direkte digitalisering | Navne, regler, art og tekst skal være originale |
| ADR-002 | Accepted | Præcis to spillere i MVP | Stærk asymmetrisk kooperation og håndterbart scope | Ingen solo/3+ players nu |
| ADR-003 | Accepted (revideret 2026-08-06) | Quest 2 er baseline og performancegulv | Reelt målheadset i huset og konservativt performanceanker. EOL: feature-opd. til dec. 2026, kritiske til dec. 2027 | Alt profileres fysisk dér. Quest 3S er antaget baseline efter v1.0 |
| ADR-004 | Accepted | Quest 1 er best-effort legacy-test | Brugeren vil teste på Q1, men device er legacy | Særskilt build/profile og exit-kriterium |
| ADR-005 | Accepted | Quest 3 har gameplayparitet og enhancements | Fremtidssikring uden feature split | Grafikprofile, ikke separat design |
| ADR-006 | Proposed (revideret 2026-08-06) | Editorvalg afgøres af M0's OpenXR-test på Quest 1. Unity 6 LTS er foretrukken kandidat | Den oprindelige begrundelse holdt ikke: Unity giver to års LTS-support til Personal/Pro, tredje år er Enterprise/Industry-only, og 2022.3 udløb medio 2025 | Editoren låses først efter M0. Ingen contentproduktion før låsen |
| ADR-007 | Proposed | OpenXR + XR Interaction Toolkit | Mindre Meta-lock-in og fælles input/interaktion | Quest-specific features begrænses |
| ADR-008 | Proposed | Photon Fusion 2 Shared Mode | Egnet til to-player VR uden dedicated server | Authority discipline og custom coop solver |
| ADR-009 | Accepted | Ingen moderne Meta Platform SDK i core | Q1 v51+ launch-problem og cross-version-risiko | Join codes/Photon frem for Meta identity |
| ADR-010 | Accepted | Data-driven scenario/events | Hurtigere iteration og test | Validators og stable IDs kræves |
| ADR-011 | Accepted | Små additive zoner, ikke open world | Scope og Quest memory/performance | Transitions/fades mellem zoner |
| ADR-012 | Accepted | Kinematic/staged coop physics | Rå network physics er for risikabelt | Mindre emergent, mere robust |
| ADR-013 | Accepted | Checkpoint pr. dag/før storm | Reconnect og retry uden continuous physics save | Kun logisk persistent state |
| ADR-014 | Accepted | Touch controllers baseline | Virker på alle målheadset | Hand tracking udskydes |
| ADR-015 | Accepted | Ingen direkte sabotage i MVP | Fælles gaveoplevelse og reduceret designrisiko | Konkurrence via efterspilsstatistik |
| ADR-016 | Proposed | Camp + én action-zone resident | Quest 1/2 memory discipline | Parallelle scener udskydes |
| ADR-017 | Accepted | Personalization er data/assets | Privat indhold må ikke forurene core | Neutral fallback obligatorisk |
| ADR-018 | Proposed | Vulkan first, GLES3 spike fallback | Moderne Quest performance | Fysisk Q1 test bestemmer. Køres først efter ADR-019's OpenXR-test er afgjort |
| ADR-019 | Proposed | Quest 1-lanens levedygtighed afgøres af én test: starter og tracker Unitys OpenXR-provider på Q1's frosne v50-runtime? | Oculus-provider v3.x er eneste dokumenterede Q1-vej og er samtidig deprecated og planlagt fjernet. En fork af interaction-laget er ikke "pakkedivergens" | Positivt svar: Q1 er en buildprofil. Negativt svar: exit-kriteriet i `docs/14` udløses, og Q1 bliver frossen demo — ikke en lane i hovedprojektet |
| ADR-020 | Proposed | Ingen live coordinator-handover. Ved coordinator-tab: pause og checkpoint-resume | Med to spillere findes ingen tredje klient at overdrage til. Checkpoint-stien skal alligevel bygges og testes | Én kodesti i stedet for to. Fjerner en klasse af desync-fejl. PO-023 reduceres |
| ADR-021 | Proposed | Dansk er eneste sprog i gaveversionen | Undertekster og localization keys kræves alligevel af `docs/09`/`docs/10`; et andet sprog er ren scopevækst | Nøglestruktur på plads fra M3. Ingen oversættelsespas før en eventuel offentlig version |

## Beslutningsproces

Nye ADR'er skal indeholde:

- problem,
- alternativer,
- valgt løsning,
- evidens,
- konsekvenser,
- rollback/exit-plan.

Claude-review ændrer ikke en Accepted ADR automatisk. Kommentar behandles først i response matrix.
