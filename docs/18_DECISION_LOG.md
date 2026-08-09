# Architecture and product decision log

| ADR | Status | Beslutning | Begrundelse | Konsekvens |
|---|---|---|---|---|
| ADR-001 | Accepted | Original IP under PROJECT ØEN | Undgår uautoriseret direkte digitalisering | Navne, regler, art og tekst skal være originale |
| ADR-002 | Accepted | Præcis to spillere i MVP | Stærk asymmetrisk kooperation og håndterbart scope | Ingen solo/3+ players nu |
| ADR-003 | Accepted (revideret 2026-08-06) | Quest 2 er baseline og performancegulv | Reelt målheadset i huset og konservativt performanceanker. EOL: feature-opd. til dec. 2026, kritiske til dec. 2027 | Alt profileres fysisk dér. Quest 3S er antaget baseline efter v1.0 |
| ADR-004 | Superseded (2026-08-08) | Quest 1 er best-effort legacy-test | M0a afgjorde det fysisk: Unitys OpenXR-provider crasher på Q1's v50-runtime | **DROP_Q1_RUNTIME.** Q1 er ikke en runtime-lane, kun frossen sideload-demo. Exit-kriteriet i `docs/14` udløst. Evidens: `prototype/m0a-openxr-smoke/RESULTAT.md` |
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
| ADR-018 | Resolved (2026-08-08) | Vulkan first, GLES3 spike fallback | Q2 bekræftet on-device på **Vulkan** (M0a: 72 fps) | GLES3-fallback-spiket (OQ-003) var betinget af Q1-lanen og bortfalder med DROP_Q1_RUNTIME. Q2/Q3 kører Vulkan |
| ADR-019 | Accepted — afgjort 2026-08-08 | Quest 1-lanens levedygtighed afgøres af én test: starter og tracker Unitys OpenXR-provider på Q1's frosne v50-runtime? | **Testet 2026-08-08:** samme OpenXR-APK kører på Quest 2 (immersivt, head-tracking valid+tracked, 72 fps, Vulkan) men crasher deterministisk på Quest 1 med native SIGABRT i `libopenxr_loader.so` under XR-opstart (to forsøg, tombstone) | **Svar: NEGATIVT → `DROP_Q1_RUNTIME`.** Exit-kriteriet i `docs/14` udløst; Q1 bliver frossen demo, ikke en lane i hovedprojektet. Evidens: `prototype/m0a-openxr-smoke/RESULTAT.md` |
| ADR-020 | Proposed | Ingen live coordinator-handover. Ved coordinator-tab: pause og checkpoint-resume | Med to spillere findes ingen tredje klient at overdrage til. Checkpoint-stien skal alligevel bygges og testes | Én kodesti i stedet for to. Fjerner en klasse af desync-fejl. PO-023 reduceres |
| ADR-021 | Proposed | Dansk er eneste sprog i gaveversionen | Undertekster og localization keys kræves alligevel af `docs/09`/`docs/10`; et andet sprog er ren scopevækst | Nøglestruktur på plads fra M3. Ingen oversættelsespas før en eventuel offentlig version |
| ADR-022 | Proposed | M-Pre: greybox-gate for kernehypotesen, før gameplay- og contentarbejdet begynder | Hypotesen — at markørallokering skaber diskussion frem for administration — bevises i dag først i M3, efter al platform-, netværks- og interaktionsarbejdet | Ny milepæl på 10-20 t uden VR og uden netværk. Rødt gate udløser redesign af kerneloopet, før M1-M3 bygges. Ny risiko R-013 registreres |
| ADR-023 | Proposed | Release 1 = afslutning af M5 | Gaveversionen er 997 t uden ekstern deadline; den mest sandsynlige dødsårsag er, at den aldrig bliver færdig | 1 spilbar dag + storm reduceret til 3 faser er en afsendbar gave. M6-M9 bliver stretch oven på noget, der allerede kan gives væk |

## Detaljer for ADR-022 og ADR-023

Begge stammer fra beslutningspakke DP-001 (2026-08-05). De blev ikke merget dengang, fordi resten af den
pakke blev overhalet af M0a's hardwareresultat. Argumenterne bag disse to er uafhængige af Quest 1-lanen og
holder stadig; de genindføres derfor mod nuværende `main` med ledige numre. Se PR-diskussionen på #2.

### ADR-022 - M-Pre greybox-gate

- **Problem:** Kernehypotesen (R-003/OQ-006: at fordeling af fire indsatsmarkører skaber diskussion frem
  for administration) er hele produktets præmis, men bevises først i M3 — efter hele platform- og
  netværkslaget. Er præmissen forkert, er alt bygget ovenpå spildt.
- **Alternativer:** (a) behold beviset i M3, (b) kør det parallelt med M0, (c) hård gate før
  gameplay- og contentarbejdet.
- **Valgt løsning:** (c). Ny milepæl **M-Pre**, 10-20 t, på papir eller fladskærm. Ingen VR, intet netværk,
  ingen art. Kun loopet: fordel markører, se udfald, tal om det.
- **Afvigelse fra DP-001:** pakken placerede gaten *før M0*. Det er overhalet — M0a er afgjort, og M0b er
  per-klient bevist on-device. Gaten flyttes derfor til **før M1**, hvor gameplay- og contentarbejdet
  begynder. Besparelsen ved rødt gate er tilsvarende mindre, men stadig hele M1-M3.
- **Evidens:** Ingen. Det er netop den manglende evidens, gaten skal producere. R-003 står som `Open` med
  effekt `Høj` og har gjort det siden baseline.
- **Konsekvenser:** PO-039 nedskaleres til genverifikation i VR. OQ-006 og OQ-007 kan lukkes efter M-Pre.
  Kræver to eksterne testere, hvilket eskalerer CR-007. Ny risiko R-013 registreres i `docs/14`.
- **Rollback/exit:** Rødt gate udløser redesign af kerneloopet, før der bygges videre. Gaten kan springes
  over ved en eksplicit ejerbeslutning, men så bæres R-003 videre uafdækket.

### ADR-023 - Release 1 = afslutning af M5

- **Problem:** Gaveversionen er opgjort til 997 t (`docs/17`). Ved 15 t/uge er det 15-16 måneder uden
  ekstern deadline. R-005 vurderer scope-eksplosion som høj sandsynlighed og høj effekt.
- **Alternativer:** (a) fuld Stormnatten som eneste mål, (b) scope-ladder uden fast release,
  (c) eksplicit afsendbar delmængde.
- **Valgt løsning:** (c). M5 afsluttes som **Release 1**: én spilbar dag plus storm reduceret til tre faser
  (vind → regn/ild → signal). Alt derefter er stretch.
- **Evidens:** Ejeren bekræftede 2026-08-05, at der ingen ekstern deadline er. Fravær af deadline øger
  driftrisikoen frem for at reducere den.
- **Konsekvenser:** Storm-fase 3 og 4 bliver stretch. M6-M9 bliver stretch oven på en allerede afsendbar
  gave. Projektet får et defineret "færdigt" længe før backloggen er tom.
- **Rollback/exit:** Fejler M-Pre eller M0-M2, bortfalder Release 1-målet sammen med resten af roadmappet.

## Beslutningsproces

Nye ADR'er skal indeholde:

- problem,
- alternativer,
- valgt løsning,
- evidens,
- konsekvenser,
- rollback/exit-plan.

Claude-review ændrer ikke en Accepted ADR automatisk. Kommentar behandles først i response matrix.
