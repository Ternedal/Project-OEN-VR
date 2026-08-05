# Architecture and product decision log

| ADR | Status | Beslutning | Begrundelse | Konsekvens |
|---|---|---|---|---|
| ADR-001 | Accepted | Original IP under PROJECT ØEN | Undgår uautoriseret direkte digitalisering | Navne, regler, art og tekst skal være originale |
| ADR-002 | Accepted | Præcis to spillere i MVP | Stærk asymmetrisk kooperation og håndterbart scope | Ingen solo/3+ players nu |
| ADR-003 | Accepted | Quest 2 er baseline | Reelt målheadset og performanceanker | Alt skal profileres fysisk dér |
| ADR-004 | Superseded by ADR-019 | Quest 1 er best-effort legacy-test | Brugeren vil teste på Q1, men device er legacy | Bortfaldet: gavemodtager ejer ikke Quest 1 |
| ADR-005 | Accepted | Quest 3 har gameplayparitet og enhancements | Fremtidssikring uden feature split | Grafikprofile, ikke separat design |
| ADR-006 | Superseded by ADR-020 | Unity 2022.3 LTS candidate | Quest 1-lane og fortsatte 3-year LTS patches | Bortfaldet: Q1-bindingen var eneste begrundelse |
| ADR-007 | Accepted | OpenXR + XR Interaction Toolkit 3.x via Unity OpenXR Plugin | Mindre Meta-lock-in; Oculus XR Plugin er deprecated | Quest-specific features begrænses; se ADR-020 |
| ADR-008 | Proposed | Photon Fusion 2.1 Shared Mode | Egnet til to-player VR uden dedicated server | Authority discipline og custom coop solver; 2.1 kræver Realtime 5 |
| ADR-009 | Accepted | Ingen moderne Meta Platform SDK i core | Undgå Meta-lock-in; oprindelig Q1 v51-begrundelse bortfaldet med ADR-019 | Join codes/Photon frem for Meta identity |
| ADR-010 | Accepted | Data-driven scenario/events | Hurtigere iteration og test | Validators og stable IDs kræves |
| ADR-011 | Accepted | Små additive zoner, ikke open world | Scope og Quest memory/performance | Transitions/fades mellem zoner |
| ADR-012 | Accepted | Kinematic/staged coop physics | Rå network physics er for risikabelt | Mindre emergent, mere robust |
| ADR-013 | Accepted | Checkpoint pr. dag/før storm | Reconnect og retry uden continuous physics save | Kun logisk persistent state |
| ADR-014 | Accepted | Touch controllers baseline | Virker på alle målheadset | Hand tracking udskydes |
| ADR-015 | Accepted | Ingen direkte sabotage i MVP | Fælles gaveoplevelse og reduceret designrisiko | Konkurrence via efterspilsstatistik |
| ADR-016 | Proposed | Camp + én action-zone resident | Quest 2 memory discipline | Parallelle scener udskydes |
| ADR-017 | Accepted | Personalization er data/assets | Privat indhold må ikke forurene core | Neutral fallback obligatorisk |
| ADR-018 | Proposed | Vulkan first | Moderne Quest performance; GLES3-fallback var Q1-drevet og bortfalder med ADR-019 | Fysisk Quest 2-test bestemmer |
| ADR-019 | Accepted | Quest 1 udgår som runtime-target | Gavemodtager ejer ikke Quest 1; lanen har ingen aftager | Ingen Q1-build, -profil eller -testlane; supersedes ADR-004 |
| ADR-020 | Accepted | Unity 6 LTS 6000.3.x + Unity OpenXR Plugin + XRI 3.x | Oculus XR Plugin deprecated; 2022.3 LTS ude af standardsupport; Q1-binding bortfaldet | Betinget af M0-verifikationsgate; supersedes ADR-006 |
| ADR-021 | Accepted | M-Pre greybox-gate før M0 | Kernehypotesen bevises i dag først i M3, efter ~200 t platform/netværk | Ny milepæl 10-20 t med hårdt gate-kriterium |
| ADR-022 | Accepted | Release 1 = afslutning af M5 | 500-810 t uden ekstern deadline har høj risiko for aldrig at blive færdig | 1 dag + 3-fase storm er afsendbar gave; M6-M9 bliver stretch |

## Detaljer for ADR-019 til ADR-022

Besluttet 2026-08-05 i beslutningspakke DP-001 (`docs/32_DECISION_PACKAGE_DP-001.md`) på grundlag af Claude-review 1.0 og ejerbesvarelse af Q-001 og Q-007.

### ADR-019 - Quest 1 udgår som runtime-target

- **Problem:** Q1-lanen var den dominerende tekniske risiko (CR-001) og bandt stacken til en provider-lane, der er ældre end XRI 3.x (CR-008).
- **Alternativer:** (a) behold fuld Q1-support, (b) reducér til kompatibilitetsdemo, (c) drop helt.
- **Valgt løsning:** (c). Q1 fjernes fra targets, buildprofiler, testmatrix og labels.
- **Evidens:** Ejeren bekræftede 2026-08-05, at gavemodtageren ikke ejer en Quest 1. Lanen har dermed ingen aftager.
- **Konsekvenser:** To-manifest-forken (`modern`/`legacy-q1`) udgår. Buildprofiler 3 → 2. OQ-001..003 bortfalder. Reviewet estimerede 15-25 % merarbejde på berørte områder ved at beholde lanen. Projektet kan ikke længere beskrives som kørende på al Quest-hardware, hvilket noteres på v2.0-linjen.
- **Rollback/exit:** Lav reversibilitet. Genindførsel vil sandsynligvis kræve engine-downgrade. Behandles som endelig.

### ADR-020 - Unity 6 LTS som engine-baseline

- **Problem:** 2022.3 LTS blev valgt for at bevare Q1-lanen. Med ADR-019 er begrundelsen væk, og sporet er ude af standardsupport.
- **Alternativer:** (a) bliv på 2022.3 LTS, (b) Unity 6000.0.x LTS, (c) Unity 6000.3.x LTS, (d) mainline 6000.4.
- **Valgt løsning:** (c) Unity 6000.3.x LTS + Unity OpenXR Plugin + XRI 3.x + URP/Vulkan + Photon Fusion 2.1.
- **Evidens (verificeret 2026-08-05, se `docs/22_SOURCE_REGISTER.md`):** Unity 2022.3 LTS har to års standardsupport fra 2023-05-30. Oculus XR Plugin er deprecated og planlagt til fjernelse; Meta anbefaler Unity OpenXR Plugin, som kræver Unity 6+. Fusion 2.1 understøtter 6.0.x og 6.3.x.
- **Konsekvenser:** Kilderegister skal udskiftes. Perf-budgetter i `docs/08` bevares, men er nu konservative. Fremtidigt render-arbejde skal være Render Graph-kompatibelt.
- **Rollback/exit:** Betinget beslutning. Fejler M0-gaten, falder valget til 6000.0.x LTS. Kun ved dobbelt fejl overvejes 2022.3.45 som accepteret teknisk gæld.

### ADR-021 - M-Pre greybox-gate før M0

- **Problem:** Kernehypotesen (markørallokering skaber diskussion, ikke administration; R-003/OQ-006) bevises først i M3, efter ~200 t platform- og netværksarbejde.
- **Alternativer:** (a) behold i M3, (b) parallelt med M0, (c) hård gate før M0.
- **Valgt løsning:** (c). Ny milepæl M-Pre, 10-20 t, fladskærm eller papir. Ingen VR, intet netværk.
- **Evidens:** Ingen. Dette er netop den manglende evidens, gaten skal producere.
- **Konsekvenser:** PO-039 nedskaleres til genverifikation i VR. OQ-006 og OQ-007 lukkes efter M-Pre. Kræver to eksterne testere, hvilket eskalerer CR-007.
- **Rollback/exit:** Rødt gate udløser redesign af kerneloopet før alt andet arbejde. Potentiel besparelse ved rødt: hele M0-M2, ca. 250 t.

### ADR-022 - Release 1 = afslutning af M5

- **Problem:** Den fokuserede gavevej er 500-810 t (~8-13 mdr. ved 15 t/uge). R-005 vurderer, at gaven aldrig bliver færdig, som mest sandsynlige dødsårsag.
- **Alternativer:** (a) fuld Stormnatten som eneste mål, (b) scope-ladder uden fast release, (c) eksplicit afsendbar delmængde.
- **Valgt løsning:** (c). M5 afsluttes som Release 1: 1 spilbar dag + storm reduceret til 3 faser (vind → regn/ild → signal).
- **Evidens:** Ejeren bekræftede 2026-08-05, at der ingen ekstern deadline er, hvilket øger driftrisikoen frem for at reducere den.
- **Konsekvenser:** Storm-fase 3 og 4 bliver stretch. M6-M9 bliver stretch oven på en allerede afsendbar gave. Ny risiko R-011 registreres.
- **Rollback/exit:** Hvis M-Pre eller M0-M2 fejler, bortfalder Release 1-målet sammen med resten af roadmappet.

## Beslutningsproces

Nye ADR'er skal indeholde:

- problem,
- alternativer,
- valgt løsning,
- evidens,
- konsekvenser,
- rollback/exit-plan.

Claude-review ændrer ikke en Accepted ADR automatisk. Kommentar behandles først i response matrix.
