# Risiko-, scope- og budgetplan

## Toprisici

| ID | Risiko | Sandsynlighed | Effekt | Tidligt signal | Mitigation |
|---|---|---:|---:|---|---|
| ~~R-001~~ | Quest 1 kræver inkompatibel package lane | - | - | **Indtruffet 2026-08-08:** tom OpenXR-build crashede på Q1 | **Lukket.** Exit-kriteriet udløst; lanen droppet (`DROP_Q1_RUNTIME`) |
| R-002 | Shared VR physics desync | Høj | Høj | Jitter/ownership loops i kassetest | Kinematic coop solver; replicate intents/results, ikke rå forces |
| R-003 | Planlægning føles som administration | Mellem | Høj | Testere vælger uden diskussion | Reducér handlinger; tydelig prognose; skarpere tradeoffs |
| R-004 | For meget content før core er sjov | Høj | Høj | Art/assets produceres før M3 | Stop/go gates; greybox first |
| R-005 | Solo dev scope eksploderer | Høj | Høj | Flere parallelle systemer åbnes | WIP limit 1 epic; scope ladder |
| R-006 | Storm bryder Quest 2-performance | Mellem | Høj | GPU > budget tidligt | Storm prototype før fuldt art pass |
| R-007 | Reconnect/save state corruption | Mellem | Høj | Bugs ved standby | Snapshot architecture og failure injection fra M2 |
| R-008 | Fysiske handlinger bliver trætte | Mellem | Mellem | Arm fatigue efter 20 min | 5-20 sek actions, assisted repetition |
| R-009 | IP ligner brætspillet for meget | Mellem | Høj offentlig release | Samme navn/tekster/regler sniger sig ind | Original terminology, mechanics and art; legal review før public |
| R-010 | Personligt indhold bliver kitschet | Mellem | Mellem | Finale føles løsrevet | Kort, fortjent epilog; neutral fallback |
| R-011 | Purchased assets clash visually | Mellem | Mellem | Uens art direction | Style pass and material unification |
| R-012 | AI-assistance skaber inkonsistent kode | Høj | Mellem | Duplikerede abstractions og scripts | Architecture rules, small PRs, tests and review |
| R-013 | Momentum-drift: gaven bliver aldrig afsendt | Høj | Høj | Milepæle skrider uden at noget er spilbart; ingen dato nævnes | Release 1 defineret som afslutning af M5 (ADR-023); M-Pre-gate før M1 (ADR-022) |

## Scopekontrol

Ny feature kræver:

1. Spillerproblem den løser.
2. Hvilket eksisterende element den erstatter eller forsinker.
3. Acceptance criteria.
4. Quest 2-performancepåvirkning.
5. Network/save-impact.
6. Estimat og risiko.

Ingen “det er nemt at tilføje” uden prototype eller code diff.

## Kontantbudget

Vejledende gaveversion:

| Post | Interval DKK |
|---|---:|
| Photon Fusion (100 CCU gratis, dækker udvikling og kommerciel brug for én app) | 0 |
| Unity-licens (kun hvis Personal ikke kan bruges) | 0-1.500 |
| Art-/environment-assets | 1.000-5.000 |
| Audio/music/SFX | 500-3.000 |
| Plugins/tools | 0-2.500 |
| Store/developer/diverse | 0-1.000 |
| Buffer | 1.000-3.000 |
| **Total** | **2.500-16.000** |

Den reelle omkostning er udviklingstid. Køb først assets, når greyboxen har bevist, at behovet består.

## Tidsbudget

- M0: stop/go **ved afslutningen af M0**, ikke efter et timeloft. Med den reviderede M0 falder det omkring 150-175 timer. Quest 1-beslutningen faldt allerede i M0a (`DROP_Q1_RUNTIME`); resten af M0's stop/go handler om netværkslanen.
- M0-M2: hårdt loft på **250 timer** som bagstopper, også hvis alle planlagte opgaver ikke er afsluttet.
- M3-M5: stop/go senest efter yderligere **350 timer**.
- Hvis en spilbar vertical slice ikke er overbevisende efter cirka **600 timer samlet**, skal scope, netværksmodel eller produktgrundlag revurderes før mere content.
- P0-backloggen (`Gaveversion = In`, 44 items) summerer til **631 timer** efter at PO-004 og PO-007 blev droppet med `DROP_Q1_RUNTIME`. Den er det konservative kritiske loft - ikke et krav om at bruge alle timer før en gate må godkendes.
- Den fulde aktive backlog (108 items) summerer til **1.451 timer** og repræsenterer maksimal hardening/polish. De 3 droppede Q1-items (28 t) er ikke medregnet.
- P1-scope blev valgt 2026-08-08: **gaveversion = 1.012 t** (P0 631 + P1 381, i alt 77 items) efter at M-Pre (PO-110, 15 t) kom til med ADR-022. Udskudt til efter v1.0: **439 t** (31 items = 312 t P1 + 127 t P2).

## Quest 1 exit-kriterium - UDLØST 2026-08-08

Kriteriet blev udløst af M0a: Unitys OpenXR-provider crasher (SIGABRT) på Q1's frosne v50-runtime, så en
Q1-lane ville kræve en separat Oculus-provider-fork af hele interaktionslaget. Ejeren accepterede
nedgraderingen samme dag.

Resultat: Quest 1 er ikke længere legacy-test eller kompatibilitetsdemo i hovedprojektet - kun en eventuel
frossen sideload-demo uden for lanen. Genoptagelse kræver ny ADR.

## Juridisk/IP

- Arbejdstitlen og alle assets skal være originale.
- Ingen kopieret regeltekst, kort, scenarier, illustrationer eller ikonografi.
- “Inspireret af” er ikke automatisk juridisk sikkerhed.
- Offentlig udgivelse kræver konkret IP/trademark/privacy review.

## Privatliv

- Personlige billeder/lyd i private encrypted storage/release artifact, ikke public repo.
- Ingen voice recording.
- Minimal anonym teknisk logging.
- Sletning/udskiftning af personalization profile skal være enkel.
