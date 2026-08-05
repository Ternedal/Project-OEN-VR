# Risiko-, scope- og budgetplan

## Toprisici

| ID | Risiko | Sandsynlighed | Effekt | Tidligt signal | Mitigation |
|---|---|---:|---:|---|---|
| R-001 | Quest 1 kræver inkompatibel package lane | Høj | Høj | Tom build kan ikke starte eller cross-play | M0 først; isoleret legacy manifest; best-effort exit-kriterium |
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

## Quest 1 exit-kriterium

Quest 1 kan nedgraderes fra “fuld legacy-test af Stormnatten” til “kompatibilitetsdemo” hvis alle er opfyldt:

- Kræver separat gameplayfork eller mere end 15 % vedvarende ekstraarbejde.
- Kræver at Quest 2/3 forbliver på kritisk usikker/forældet stack.
- Cross-play kan ikke gøres stabilt uden platformservice-versionkonflikt.
- Ejeren accepterer ændringen efter fysisk M0-evidens.

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
