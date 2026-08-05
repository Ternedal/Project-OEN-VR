# Architecture and product decision log

| ADR | Status | Beslutning | Begrundelse | Konsekvens |
|---|---|---|---|---|
| ADR-001 | Accepted | Original IP under PROJECT ØEN | Undgår uautoriseret direkte digitalisering | Navne, regler, art og tekst skal være originale |
| ADR-002 | Accepted | Præcis to spillere i MVP | Stærk asymmetrisk kooperation og håndterbart scope | Ingen solo/3+ players nu |
| ADR-003 | Accepted | Quest 2 er baseline | Reelt målheadset og performanceanker | Alt skal profileres fysisk dér |
| ADR-004 | Accepted | Quest 1 er best-effort legacy-test | Brugeren vil teste på Q1, men device er legacy | Særskilt build/profile og exit-kriterium |
| ADR-005 | Accepted | Quest 3 har gameplayparitet og enhancements | Fremtidssikring uden feature split | Grafikprofile, ikke separat design |
| ADR-006 | Proposed | Unity 2022.3 LTS candidate | Quest 1-lane og fortsatte 3-year LTS patches | Skal fysisk valideres i M0 |
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
| ADR-018 | Proposed | Vulkan first, GLES3 spike fallback | Moderne Quest performance | Fysisk Q1 test bestemmer |

## Beslutningsproces

Nye ADR'er skal indeholde:

- problem,
- alternativer,
- valgt løsning,
- evidens,
- konsekvenser,
- rollback/exit-plan.

Claude-review ændrer ikke en Accepted ADR automatisk. Kommentar behandles først i response matrix.
