# Risiko-, scope- og budgetplan

## Toprisici

| ID | Risiko | Sandsynlighed | Effekt | Tidligt signal | Mitigation |
|---|---|---:|---:|---|---|
| R-001 | Engine-baseline fejler på Unity 6 | Mellem | Høj | Tom build starter ikke, eller Fusion/XRI er inkompatible | Engine-gate som allerførste M0-arbejde; fallback til 6000.0.x LTS (ADR-020). Oprindelig Q1-formulering bortfaldet med ADR-019 |
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
| R-013 | Momentum-drift uden ekstern deadline | Høj | Høj | Ingen dag hvor udskydelse er for dyr; projektet dør stille frem for at fejle synligt | Selvvalgt dato: M-Pre kørt senest 2026-10-01. Timelog pr. uge; under 5 t/uge i 4 sammenhængende uger udløser eksplicit revurdering. Release 1 (ADR-022) er eneste sted hvor "færdig" defineres |

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
| Unity/Photon under hobby-/lav CCU-grænser | 0-1.500 |
| Art-/environment-assets | 1.000-5.000 |
| Audio/music/SFX | 500-3.000 |
| Plugins/tools | 0-2.500 |
| Store/developer/diverse | 0-1.000 |
| Buffer | 1.000-3.000 |
| **Total** | **2.500-16.000** |

Den reelle omkostning er udviklingstid. Køb først assets, når greyboxen har bevist, at behovet består.

## Tidsbudget

- M0-M2: stop/go senest efter **250 timer**, også hvis alle planlagte opgaver ikke er afsluttet.
- M3-M5: stop/go senest efter yderligere **350 timer**.
- Hvis en spilbar vertical slice ikke er overbevisende efter cirka **600 timer samlet**, skal scope, netværksmodel eller produktgrundlag revurderes før mere content.
- P0-backloggen summerer til cirka **622 timer**. Den er det konservative kritiske loft - ikke et krav om at bruge alle timer før en gate må godkendes.
- Den fulde 108-opgavers backlog summerer til cirka **1.447 timer** og repræsenterer maksimal hardening/polish. Release-scope vælges eksplicit i workbooken før produktion.

## Quest 1

Udgået som runtime-target, jf. ADR-019. Gavemodtageren ejer ikke en Quest 1, og lanen havde derfor ingen aftager. Beslutningen har lav reversibilitet og behandles som endelig.

## Release 1 som scopeanker

Release 1 (afslutning af M5, ADR-022) er det primære gavemål: 1 spilbar dag + storm i tre faser. Estimeret til ca. 340-470 timer med lav konfidens. Alt efter M5 er stretch oven på en gave, der allerede kan gives.

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
