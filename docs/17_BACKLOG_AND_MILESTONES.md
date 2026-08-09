# Backlog og milepæle

> Tekstbaseret source-of-truth-eksport fra `17_BACKLOG_AND_MILESTONES.xlsx`. Excel-filen er fortsat den praktiske tracker, men alle reviewkritiske opgaver er gengivet her.

**Status ved review-behandling 2026-08-06:** 110 backlog-items · 1473 estimerede timer · 45 P0-items · alle står som `Not Started`. *(Opdateret 2026-08-08 efter M0a/DROP_Q1_RUNTIME: 3 Q1-items droppet, 18 t frigjort fra P0 → P0-sum 616 t.)*

> **Ændret 2026-08-06 (CR-001, CR-005, CR-008, CR-010):** PO-017, PO-018, PO-019, PO-020, PO-022 og PO-025 er flyttet fra M2 til M0, så M0's gate kan bevises af M0's egne opgaver. Kolonnen `Gaveversion` er tilføjet: `In` = med i gaveversionen, `Out` = udenfor, `Defer` = efter v1.0. P0 er forudfyldt som `In`, fordi `docs/12` definerer P0 som releasekritisk. **P1 står som `TBD` og skal vælges af ejeren** — indtil da er 500-810 timer ikke et sporbart tal. Nye items: PO-000 (reviewbehandling) og PO-104 (lokalisering).

> **Ændret 2026-08-08 (M0a-resultat, `DROP_Q1_RUNTIME`):** Quest 1 kører ikke OpenXR-runtimen (jf. `prototype/m0a-openxr-smoke/RESULTAT.md`). Q1-specifikke items droppet: **PO-004 (8 t) og PO-007 (10 t) fjernet fra P0/gaveversion → 18 t frigjort** (P0-sum 634 → 616 t), og **PO-098 (10 t, var TBD)** droppet. PO-025 reduceret til Q2↔Q3. COMPAT-001 (Q1↔Q3) udgået.

> **P1-scope besluttet 2026-08-08 (Q-004, CR-005 lukket):** alle 55 P1-items sat til `In`/`Defer`. **Gaveversion = 1.012 t** (P0 631 + P1 381, i alt 77 items; inkl. M-Pre/PO-110 15 t fra ADR-022). Udskudt til efter v1.0: **439 t** (31 items: 312 t P1 — survival-dybde, ekstra content/art, dev/QA-luksus, undertekster — plus 127 t P2). PO-104-dubletten rettet (telemetri = PO-109). Ved 15 t/uge ≈ **15-16 måneder** → landing omkring årsskiftet 2027/28.

## Epics

| Epic | Navn | Mål | Milepæl | Kritikalitet |
| --- | --- | --- | --- | --- |
| E00 | Platform feasibility | Fælles Quest 2/3 build-, XR- og package-strategi | M0 | BLOCKER |
| E01 | XR interaction | Locomotion, grab, snap og tohåndsinteraktion | M1 | HIGH |
| E02 | Multiplayer | Lobby, replication, authority og compatibility | M2 | BLOCKER |
| E03 | Scenario flow | ScenarioDirector, faser, commands og state | M3 | HIGH |
| E04 | Planning & survival | Indsats, ressourcer, spiller- og lejrstatus | M3 | HIGH |
| E05 | Crafting & construction | Fysiske coop-opgaver og kvalitet | M3-M5 | HIGH |
| E06 | Events & consequences | Data-driven events og delayed consequences | M4 | HIGH |
| E07 | Stormnatten | Tre dage, rescue, storm og signal | M5-M6 | HIGH |
| E08 | Save & reconnect | Checkpoint, migration og resume | M2-M6 | BLOCKER |
| E09 | UX & accessibility | Onboarding, comfort, handedness og subtitles | M1-M9 | HIGH |
| E10 | Art, audio & performance | Stil, assets, VFX og device-profiler | M5-M7 | MEDIUM |
| E11 | Personalization | Privat profile og neutral fallback | M8 | MEDIUM |
| E12 | Build & release | CI, signing og Alpha-distribution | M0-M9 | HIGH |
| E13 | QA & release | Tests, device matrix og release gates | M0-M9 | BLOCKER |

## Milepæle

| ID | Navn | Output | Est. timer | Exit gate | Disposition |
| --- | --- | --- | --- | --- | --- |
| M0 | Platform feasibility | Fælles code/content lane bevist | 60-100 | Q2-Q3 box; 72 Hz minimal (Q1 udgået: DROP_Q1_RUNTIME) | Go/Redesign |
| M-Pre | Greybox-gate (ADR-022) | Kernehypotesen bevist uden VR | 10-20 | 2 af 3 sessioner viser reel forhandling (`docs/35`) | Go/Redesign |
| M1 | Interaction foundation | Komfortabel lokal VR-interaktion | 35-55 | 10x greb/snap/tohånd; seated | Go/Fix |
| M2 | Multiplayer foundation | Stabil privat session og authority | 45-70 | 10 cycles; reconnect skeleton | Go/Redesign |
| M3 | One-day prototype | Planlægning og én fuld dag | 55-85 | Ekstern test uden forklaring | Go/Cut |
| M4 | Consequences | Forsinket årsag/virkning | 40-65 | Tester forklarer chain | Go/Cut |
| M5 | Storm vertical slice — **Release 1** | Finale med branches; afsendbar gave (ADR-023) | 70-110 | 72 Hz Q2; 20 min soak | Go/Cut |
| M6 | Full Stormnatten | Tre dage og 35-45 min | 70-115 | Median tid; active ≥70% | Go/Polish |
| M7 | Art/audio pass | Sammenhængende stil | 55-90 | Q2 budget + Q3 profile | Go/Fix |
| M8 | Gift personalization | Privat profile/distribution | 30-50 | Fallback og clean install | Go/Fix |
| M9 | Release candidate | QA, comfort, gates | 40-70 | P0/P1=0; full matrix | Release/Hold |

## Testmatrix

| ID | Test | Platform | Handling | Forventet resultat | Gate |
| --- | --- | --- | --- | --- | --- |
| NET-001 | Same-frame grab | Q2/Q3 | Begge griber samme frame | Én authority; ingen jitter | M2 |
| NET-002 | Coop heavy box | Cross-device | Løft og snap | Identisk state 10/10 | M0/M2 |
| NET-003 | Authority disconnect | Cross-device | Owner disconnect under interaction | Pause/resync/checkpoint | M2 |
| FLOW-001 | Plan lock race | All | Marker og confirm samtidig | Én revision | M3 |
| SAVE-001 | Delayed event resume | All | Save efter schedule | Trigger præcis én gang | M4 |
| DEV-001 | Standby | Q2/Q3 | Sleep i tre faser | Kontrolleret resume | M6 |
| PERF-001 | Storm soak | Q2 | 20 minutter | 72 Hz target; no leak | M5 |
| ~~COMPAT-001~~ | ~~Q1-Q3 cross-play~~ UDGÅET (DROP_Q1_RUNTIME) | – | – | dækkes af COMPAT-002 (Q2↔Q3) | – |
| CONTENT-001 | Missing private asset | All | Asset mangler | Neutral fallback | M8 |
| UX-001 | No-help onboarding | Human | Nye spillere | Mål forstået <4 min | M6 |
| UX-002 | Active participation | Human | Observer action time | Begge aktive ≥70% | M6 |
| COMFORT-001 | 45-min comfort | Human/Q2 | Fuld mission | Ingen moderat+ hos flertal | M9 |

## Risici

| ID | Risiko | Sandsynlighed | Effekt | Gate | Mitigation | Status |
| --- | --- | --- | --- | --- | --- | --- |
| ~~R-001~~ | Quest 1 package lane inkompatibel | - | - | M0 | Indtruffet: Q1 kan ikke køre OpenXR. Lanen droppet (`DROP_Q1_RUNTIME`) | **Lukket 2026-08-08** |
| R-002 | Shared VR physics desync | High | High | M0/M2 | Kinematic coop solver | Open |
| R-003 | Planning føles administrativ | Medium | High | M3 | Ekstern test; skarpere tradeoffs | Open |
| R-004 | Content før core | High | High | M3 | Greybox gates | Open |
| R-005 | Solo-dev scope | High | High | All | WIP 1; scope ladder | Open |
| R-006 | Storm performance | Medium | High | M5 | Prototype før art pass | Open |
| R-007 | Reconnect/save corruption | Medium | High | M2-M6 | Snapshots og failure injection | Open |
| R-008 | Physical fatigue | Medium | Medium | M1/M9 | 5-20s actions | Open |
| R-009 | IP similarity | Medium | High | Pre-public | Original IP; legal review | Open |
| R-010 | AI code inconsistency | High | Medium | All | Small PRs; tests | Open |

## Detaljeret backlog

| ID | Epic | Type | Titel | Milepæl | Prioritet | Gaveversion | Status | Est. timer | Afhængigheder | Testplatform | Acceptance criteria |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PO-000 | E00 | Proces | Behandl Claude-review og opdatér baseline | M0 | P0 | In | Not Started | 12 | - | - | Alle BLOCKER/HIGH har disposition i response matrix; accepterede ændringer er indarbejdet i specs og ADR-log; M0-scope opdateret |
| PO-104 | E09 | Content | Localization key-tabel og underteksttekstning (dansk) | M6 | P1 | Defer | Not Started | 14 | 60 | - | Alle voice-/UI-strenge har nøgler; build fejler ved manglende key; undertekster vist i tre størrelser |
| PO-001 | E00 | Spike | Pin Unity editor candidate | M0 | P0 | In | Not Started | 6 |  | Q2/Q3 | Version og lockfiles committed |
| PO-002 | E00 | Spike | Konfigurer Android IL2CPP ARM64 og OpenXR | M0 | P0 | In | Not Started | 6 | 1 | Q2/Q3 | Tom APK starter og viser tracking |
| PO-003 | E00 | Story | Implementér BuildInfo og platformdetektion | M0 | P1 | In | Not Started | 5 | 1 | All | Build viser version, profile, device og protocol |
| PO-004 | E00 | Spike | ~~Opret Q1_LEGACY buildprofil~~ DROPPET | M0 | P0 | Out | Dropped (DROP_Q1_RUNTIME 08-08) | 8 | 2 | Q1 | Q1 kører ikke OpenXR — 8 t frigjort |
| PO-005 | E00 | Spike | Opret Q2_BASE buildprofil | M0 | P0 | In | Not Started | 5 | 2 | Q2 | Tom scene holder 72 Hz |
| PO-006 | E00 | Spike | Opret Q3_ENHANCED buildprofil | M0 | P1 | In | Not Started | 5 | 2 | Q3 | Samme gameplay flags og forbedret quality |
| PO-007 | E00 | Spike | ~~Sammenlign Vulkan/GLES3 på Quest 1~~ DROPPET | M0 | P0 | Out | Dropped (DROP_Q1_RUNTIME 08-08) | 10 | 4 | Q1 | Betinget af Q1-lanen — 10 t frigjort. Q2 bekræftet på Vulkan |
| PO-008 | E00 | Decision | Fastlås package compatibility matrix | M0 | P0 | In | Not Started | 6 | 4,5,6 | Q2/Q3 | ADR og compatibility matrix opdateret |
| PO-009 | E01 | Story | XR Origin og gulvkalibrering | M1 | P1 | In | Not Started | 8 | 2 | Q2/Q3 | Stående/siddende kan kalibreres |
| PO-110 | E00 | Proces | M-Pre greybox-gate: kernehypotesen bevist uden VR | M-Pre | P0 | In | Not Started | 15 |  | Ingen | 2 af 3 sessioner viser reel forhandling om markørerne, målt som defineret i `docs/35`; resultat og rå noter arkiveret |
| PO-010 | E01 | Story | Teleport locomotion | M1 | P1 | In | Not Started | 6 | 9 | All | Teleport er stabil og bounded |
| PO-011 | E01 | Story | Snap turn og comfort settings | M1 | P1 | In | Not Started | 6 | 9 | All | 15/30/45 grader; default 30 |
| PO-012 | E01 | Story | Grab wrapper og object reset | M1 | P1 | In | Not Started | 10 | 9 | All | Item kan gribes, overdrages og resettes |
| PO-013 | E01 | Story | Snap target med magnetisk preview | M1 | P1 | In | Not Started | 8 | 12 | All | Preview før release og tydelig feedback |
| PO-014 | E01 | Story | Lokalt tohåndsobjekt | M1 | P0 | In | Not Started | 14 | 12 | All | Tung kasse stabil med to hænder |
| PO-015 | E01 | Story | Haptics adapter og indstilling | M1 | P2 | Defer | Not Started | 5 | 12 | All | Haptics kan skaleres/deaktiveres |
| PO-016 | E01 | QA | Reach/seated playtest | M1 | P1 | In | Not Started | 8 | 10,13,14 | Q2/Q3 | Alt nås uden knælen |
| PO-017 | E02 | Spike | Photon Fusion app/config | M0 | P0 | In | Not Started | 5 | 8 | Network | To klienter kan oprette session |
| PO-018 | E02 | Story | Privat join code | M0 | P0 | In | Not Started | 10 | 17 | Network | Create/join/leave 10 af 10 |
| PO-019 | E02 | Story | Compatibility handshake | M0 | P0 | In | Not Started | 10 | 3,18 | Q2/Q3 | Protocol/content mismatch afvises |
| PO-020 | E02 | Story | Head/hands replication | M0 | P0 | In | Not Started | 14 | 17 | Q2/Q3 | Remote pose stabil og interpoleret |
| PO-021 | E02 | Story | Authority for lette objects | M2 | P0 | In | Not Started | 12 | 12,20 | Network | Same-frame grab deterministisk |
| PO-022 | E02 | Story | CoopObjectController | M0 | P0 | In | Not Started | 24 | 14,20 | Cross-device | To hand targets styrer tung kasse |
| PO-023 | E02 | Story | Scenario coordinator election | M2 | P0 | In | Not Started | 12 | 17 | Network | Coordinator kendt og kan håndteres ved loss |
| PO-024 | E02 | Tooling | Network debug panel | M2 | P1 | In | Not Started | 8 | 17 | All | Ping, region, authority og revision vises |
| PO-025 | E02 | QA | 10x Q2-Q3 box test | M0 | P0 | In | Not Started | 12 | 22 | Cross-device | Ingen permanent desync (Q1 udgået) |
| PO-026 | E02 | QA | Packet loss og latency test | M2 | P1 | Defer | Not Started | 10 | 22 | Network | Spilbart ved 120 ms |
| PO-027 | E03 | Story | ScenarioDirector state machine | M3 | P0 | In | Not Started | 16 | 24 | All | Kun director kan skifte fase |
| PO-028 | E03 | Story | Gameplay commands/domain events | M3 | P1 | In | Not Started | 12 | 27 | All | Commands valideres og events logges |
| PO-029 | E03 | Story | Dawn/Planning/Action/Dusk/Night | M3 | P0 | In | Not Started | 18 | 27 | All | Én dag kører ende-til-ende |
| PO-030 | E03 | Story | Scenario seed og deterministic selection | M3 | P1 | Defer | Not Started | 10 | 27 | All | Samme seed giver samme eventvalg |
| PO-031 | E03 | Tooling | Debug phase skip og tag injection | M3 | P1 | Defer | Not Started | 8 | 27 | All | Tester kan hoppe til fase |
| PO-032 | E03 | QA | Scenario simulation tests | M3 | P1 | Defer | Not Started | 12 | 27,28 | Automated | Transitions og ugyldige flows testes |
| PO-033 | E04 | Story | Fire effort markers | M3 | P0 | In | Not Started | 12 | 29 | Network | Begge ser placement og planversion |
| PO-034 | E04 | Story | Plan lock race protection | M3 | P0 | In | Not Started | 8 | 33 | Network | Kun én revision låses |
| PO-035 | E04 | Story | Shared resource state | M3 | P0 | In | Not Started | 10 | 28 | All | Træ/fiber/mad/urter autoritativt |
| PO-036 | E04 | Story | Player status | M3 | P1 | Defer | Not Started | 10 | 28 | All | Health/fatigue/injuries gemmes |
| PO-037 | E04 | Story | Camp status | M3 | P1 | Defer | Not Started | 10 | 28 | All | Shelter/fire/signal/threat shared |
| PO-038 | E04 | Content | Fysisk planlægningsbord | M3 | P1 | In | Not Started | 16 | 33,35 | Q2/Q3 | Fire markers og cards læsbare |
| PO-039 | E04 | QA | Ekstern one-day playtest | M3 | P0 | In | Not Started | 10 | 29,38 | Human | Reelt valg uden dev-forklaring |
| PO-040 | E05 | Story | InteractionSequence data model | M3 | P1 | In | Not Started | 12 | 28 | All | Primær/sekundær rolle og outcomes authorable |
| PO-041 | E05 | Story | Quality scoring | M3 | P1 | Defer | Not Started | 12 | 40 | All | Prep/tool/execution/cooperation beregnes |
| PO-042 | E05 | Content | Shelter greybox interaction | M3 | P0 | In | Not Started | 24 | 13,40 | Q2/Q3 | Begge aktive og partial success |
| PO-043 | E05 | Story | Tool durability/quality | M4 | P2 | Defer | Not Started | 10 | 41 | All | Tool påvirker outcome og save |
| PO-044 | E05 | Content | Fire-start interaction | M3 | P1 | Defer | Not Started | 16 | 40 | All | Vindbeskyttelse plus ildstål |
| PO-045 | E05 | Content | Signal frame interaction | M5 | P1 | Defer | Not Started | 20 | 40 | All | Tre stages; quality påvirker finale |
| PO-046 | E05 | Story | Assisted repetition | M4 | P2 | Defer | Not Started | 8 | 42 | All | Gentagelser abstraheres efter succes |
| PO-047 | E06 | Story | EventDefinition loader/validator | M4 | P0 | In | Not Started | 14 | 28 | Automated | Duplicate/missing refs stopper build |
| PO-048 | E06 | Story | Delayed event queue | M4 | P0 | In | Not Started | 16 | 46 | All | Trigger præcis én gang efter resume |
| PO-049 | E06 | Story | Gameplay tags og conditions | M4 | P1 | In | Not Started | 12 | 46 | All | Tags bruges i triggers/win rules |
| PO-050 | E06 | Content | Open food til animal chain | M4 | P0 | In | Not Started | 18 | 47,48 | All | Tidligt valg ændrer senere sekvens |
| PO-051 | E06 | Content | Injury til infection chain | M4 | P1 | Defer | Not Started | 16 | 47,48 | All | Ubehandlet sår påvirker finale |
| PO-052 | E06 | Story | Causal after-action report | M4 | P1 | In | Not Started | 14 | 47 | All | Årsagskæde forståelig |
| PO-053 | E06 | QA | Event cycle validation tests | M4 | P1 | Defer | Not Started | 10 | 46 | Automated | Dead ends/cycles rapporteres |
| PO-054 | E07 | Content | Greybox strand/camp | M3 | P1 | Defer | Not Started | 20 | 42 | Q2 | Intro, fire og planning spilbart |
| PO-055 | E07 | Content | Greybox jungle zone | M6 | P2 | Defer | Not Started | 24 | 52 | Q2 | Tydelig navigation/gathering |
| PO-056 | E07 | Content | Greybox ravine rescue | M6 | P1 | In | Not Started | 24 | 22,40 | Q2 | To aktive roller og fail-forward |
| PO-057 | E07 | Content | Dag 1 content | M6 | P1 | Defer | Not Started | 24 | 52,46 | All | Tutorial, første valg og nat |
| PO-058 | E07 | Content | Dag 2 content | M6 | P1 | In | Not Started | 28 | 54,55 | All | Varsel, rescue og branch |
| PO-059 | E07 | Content | Dag 3 forberedelse | M6 | P1 | In | Not Started | 18 | 56 | All | Sidste tradeoff før storm |
| PO-060 | E07 | Content | Storm fase 1-2 | M5 | P0 | In | Not Started | 28 | 42,49 | Q2/Q3 | Vind/tag og regn/ild branches |
| PO-061 | E07 | Content | Storm fase 3-5 | M5 | P0 | In | Not Started | 32 | 58 | Q2/Q3 | Consequence, collapse og signal |
| PO-062 | E07 | Story | Win/lose/retry flow | M5 | P0 | In | Not Started | 16 | 59 | All | Retry fra pre-storm checkpoint |
| PO-063 | E07 | Content | Tune 10 event definitions | M6 | P1 | In | Not Started | 24 | 46 | All | Fallback og test path |
| PO-064 | E07 | QA | Full scenario external playtest | M6 | P0 | In | Not Started | 16 | 55,56,59,60 | Human | 35-45 min og begge aktive ≥70% |
| PO-065 | E08 | Story | Checkpoint schema/checksum | M2 | P0 | In | Not Started | 12 | 28 | All | Versioneret schema dokumenteret |
| PO-066 | E08 | Story | Atomic local save | M3 | P0 | In | Not Started | 14 | 62 | All | Temp write, checksum og backup |
| PO-067 | E08 | Story | Snapshot apply/resync | M2 | P0 | In | Not Started | 16 | 25,62 | Network | Client modtager fuldt state snapshot |
| PO-068 | E08 | Story | Disconnect safe pause | M2 | P0 | In | Not Started | 12 | 23 | Network | Scenario pauser efter peer loss |
| PO-069 | E08 | Story | 90s reconnect flow | M4 | P0 | In | Not Started | 20 | 64,65 | Cross-device | Peer returnerer med korrekt snapshot |
| PO-070 | E08 | Story | Checkpoint resume session | M4 | P0 | In | Not Started | 18 | 63 | Network | Ny session fortsætter fra checkpoint |
| PO-071 | E08 | Story | Save migration framework | M6 | P1 | Defer | Not Started | 12 | 62 | Automated | vN til vN+1 migrator/test |
| PO-072 | E08 | QA | Standby tests i alle faser | M6 | P0 | In | Not Started | 12 | 65,66 | Q2/Q3 | Lobby/action/storm recover |
| PO-073 | E09 | Story | Handedness settings | M1 | P1 | In | Not Started | 6 | 9 | All | Dominant hånd kan ændres |
| PO-074 | E09 | Story | Subtitle system | M6 | P1 | Defer | Not Started | 12 | 28 | All | Speaker, størrelse og baggrund |
| PO-075 | E09 | Story | Comfort menu | M1 | P1 | In | Not Started | 10 | 10,11 | All | Teleport/snap/smooth/vignette |
| PO-076 | E09 | Story | Critical object return/reset | M1 | P1 | In | Not Started | 8 | 12 | All | Mistet item gendannes |
| PO-077 | E09 | Story | Onboarding hint controller | M6 | P1 | In | Not Started | 12 | 55 | All | Hint efter inactivity uden blokering |
| PO-078 | E09 | QA | Comfort playtest 15/30/45 | M9 | P0 | In | Not Started | 14 | 61,72 | Human | Ingen moderat+ ubehag hos flertal |
| PO-079 | E09 | QA | Color/shape accessibility review | M9 | P1 | In | Not Started | 8 | 72 | Human | Ingen farve-only cue |
| PO-080 | E10 | Art | Shared material palette | M7 | P2 | Defer | Not Started | 10 | 61 | All | Stilguide og master materials |
| PO-081 | E10 | Art | Camp art pass | M7 | P1 | Defer | Not Started | 30 | 52,76 | Q2 | Quest 2 budget overholdt |
| PO-082 | E10 | Art | Jungle/ravine art pass | M7 | P2 | Defer | Not Started | 36 | 53,54,76 | Q2 | Landmarks og LODs |
| PO-083 | E10 | Art | Storm VFX profiles | M5 | P1 | In | Not Started | 22 | 58 | Q2/Q3 | Q2/Q3 quality levels |
| PO-084 | E10 | Audio | Adaptive ambience/storm audio | M7 | P1 | Defer | Not Started | 24 | 58 | All | Cues kan høres og ses |
| PO-085 | E10 | Art | Simple network avatar polish | M7 | P2 | Defer | Not Started | 18 | 20 | All | Tydelig identity uden Meta Avatars |
| PO-086 | E10 | Performance | Quest 2 optimization pass | M7 | P0 | In | Not Started | 24 | 77,78,79 | Q2 | 72 Hz og budgets dokumenteret |
| PO-087 | E10 | Performance | Q3 enhancement-profil | M7 | P1 | In | Not Started | 9 | 82 | Q3 | Gameplayparitet Q2↔Q3 dokumenteret (Q1-reduktion udgået, `DROP_Q1_RUNTIME` - 9 t frigjort) |
| PO-088 | E11 | Story | PersonalizationProfile loader | M8 | P1 | In | Not Started | 12 | 46 | All | Profile og fallback kan vælges |
| PO-089 | E11 | Tooling | Private asset validation | M8 | P1 | In | Not Started | 8 | 84 | All | Size/format/missing håndteres |
| PO-090 | E11 | Content | Ending crate/radio hooks | M8 | P1 | In | Not Started | 16 | 84 | All | Hooks uden specialkode |
| PO-091 | E11 | Content | Integrér private billeder/lyd | M8 | P2 | Defer | Not Started | 10 | 85 | All | Ingen private assets i repo/log |
| PO-092 | E11 | QA | Neutral fallback end-to-end | M8 | P1 | In | Not Started | 6 | 85 | All | Build virker uden private content |
| PO-093 | E11 | QA | Personlig finale playtest | M8 | P2 | Defer | Not Started | 6 | 86 | Human | ≤90 sek og føles fortjent |
| PO-094 | E12 | Build | Content/schema CI validation | M0 | P1 | In | Not Started | 10 | 1 | Automated | CI fejler ved invalid JSON/IDs |
| PO-095 | E12 | Build | Automated build metadata | M0 | P1 | Defer | Not Started | 8 | 3 | All | Commit/profile/hash i build |
| PO-096 | E12 | Build | Signing og keystore backup | M8 | P0 | In | Not Started | 8 | 5 | All | Release key backup testet |
| PO-097 | E12 | Release | Alpha release channel flow | M8 | P1 | In | Not Started | 10 | 90 | Q2/Q3 | Q2/3 private install/update |
| PO-098 | E12 | QA | ~~Quest 1 sideload-guide~~ DROPPET | M8 | P1 | Out | Dropped (DROP_Q1_RUNTIME 08-08) | 10 | 4 | Q1 | Kun relevant hvis frossen Q1-demo genoptages |
| PO-099 | E12 | Tooling | Local log export | M6 | P1 | In | Not Started | 8 | 25 | All | Logs uden private data |
| PO-100 | E12 | Release | Build artifact/rollback archive | M9 | P0 | In | Not Started | 8 | 91,92 | All | APK, symbols, locks og notes |
| PO-101 | E13 | QA | EditMode core test suite | M0 | P1 | In | Not Started | 12 | 1 | Automated | Baseline tests grønne |
| PO-102 | E13 | QA | Two-client integration harness | M2 | P1 | Defer | Not Started | 16 | 17 | Automated | Sessiontest kan gentages |
| PO-103 | E13 | QA | Device test checklist | M0 | P1 | Defer | Not Started | 8 |  | Q2/Q3 | Q2/Q3 results registreres |
| PO-109 | E13 | QA | Performance telemetry | M3 | P1 | Defer | Not Started | 10 | 3 | Q2 | Frame timing/memory per fase |
| PO-105 | E13 | QA | Storm 20-min soak | M5 | P0 | In | Not Started | 12 | 58,97 | Q2 | No leak/thermal/permanent desync |
| PO-106 | E13 | QA | Full regression matrix | M9 | P0 | In | Not Started | 24 | 61,68,83,87 | Q2/Q3 | Alle release gates dokumenteret |
| PO-107 | E13 | QA | P0/P1 bug closure | M9 | P0 | In | Not Started | 24 | 99 | All | P0/P1 lig nul |
| PO-108 | E13 | QA | RC clean-install test | M9 | P0 | In | Not Started | 12 | 91,92,100 | Q2/Q3 | To brugere gennemfører uden dev |

## Reviewfelter

`Owner` og `Claude ref` vedligeholdes i workbooken eller i GitHub issues/PR'er. Claude-kommentarer spores i `review/RESPONSE_MATRIX.md` med stabile `CR-xxx`-ID'er.
