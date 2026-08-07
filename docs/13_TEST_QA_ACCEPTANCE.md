# Test-, QA- og acceptplan

## Testlag

1. **EditMode:** pure state, event conditions, save migration, validators.
2. **PlayMode:** phase flow, interactions, local multiplayer simulation.
3. **Network integration:** to Unity instances og packet simulation.
4. **Physical device:** Quest 1/2/3.
5. **Human playtest:** usability, cooperation, comfort and fun.

## Device matrix

| Test | Q1 | Q2 | Q3 | Cross-device |
|---|---:|---:|---:|---:|
| Boot/input | Hver milestone | Hver build | Hver milestone | - |
| Full scenario | RC | Hver RC | Hver RC | Q1↔Q2, Q2↔Q3 |
| Performance | Legacy smoke | Autoritativ | Regression/enhanced | - |
| Reconnect | M2+ | M2+ | M2+ | Ja |
| Standby | M2+ | M2+ | M2+ | Ja |
| Save/resume | M3+ | M3+ | M3+ | Ja |

## Bug severity

- **P0:** data loss, crash loop, kan ikke starte/session join, sikkerhedsproblem.
- **P1:** mission kan ikke gennemføres, permanent desync, alvorlig komfortfejl, vedvarende frameratebrud.
- **P2:** omvej findes, tydelig visuel/interaktionsfejl, enkelte state mismatch der kan resync.
- **P3:** kosmetik, tekst, mindre polish.

## Release gates

### Functional

- Clean install og first-run virker.
- Lobby/join/ready virker 10/10.
- Alle kritiske paths i Stormnatten gennemføres.
- Retry/checkpoint virker.
- Personlig profile og neutral fallback virker.

### Network

- Ingen permanent state divergence efter authority transfer.
- Disconnect/reconnect testet i hver fase.
- Mismatched protocol/content afvises tydeligt.
- Duplicate commands er idempotente.

### Performance

- Quest 2 stabil 72 Hz gennem fuld mission og storm.
- 20 minutters storm soak uden memory leak/thermal collapse.
- Quest 1 reduceret build gennemfører.
- Quest 3 regression og enhancement profile dokumenteret.

### Comfort/accessibility

- Teleport/snap turn default.
- Seated/standing gennemført.
- Venstre/højrehånd.
- Undertekster.
- Ingen påkrævet gulvkontakt.
- Ingen moderat+ ubehag hos flertal af testere.

### Content

- Ingen dead-end event chains.
- Alle IDs, keys og fallback assets valideret.
- Median playtime 35-45 min.
- Begge aktive mindst 70 % af action-tid.

## Kritiske testcases

### NET-001 Same-frame grab

Begge griber samme lette object i samme frame. Én authority vinder deterministisk; den anden hånd slipper uden teleport/jitter.

### NET-002 Coop box

Begge griber den tunge kasse, bevæger og placerer den. Resultat er ens på begge clients.

### NET-003 Authority disconnect

Authority disconnecter under interaction. Spillet pauser/resumer eller går til checkpoint; object må ikke blive ubrugeligt.

### FLOW-001 Plan lock race

En spiller placerer sidste marker mens anden bekræfter. Kun én planversion låses.

### SAVE-001 Delayed event

Checkpoint gemmes efter event scheduling, før trigger. Resume udløser event præcis én gang.

### DEV-001 Standby

Quest går i standby i lobby, action og storm. Return flow er tydeligt og state er gyldig.

### UX-002 Aktiv deltagelse (automatiseret)

Andelen af action-tid med aktivt bidrag fra begge spillere udledes af event-journalen (`docs/06` §6), ikke af observation. Hver `ActionResolved` bærer aktive frames pr. spillerrolle, og en rapport pr. run udskriver:

- andel af action-tid med begge aktive (gate: ≥70 %),
- længste passive periode pr. spiller (designregel 12 sek., testgrænse 20 sek.),
- antal perioder over hver af de to grænser.

Manuel observation bruges stadig til *hvorfor*, men tallet afgør gaten.

### PERF-002 Kollapssekvens isoleret

Stormens fase 4 (delvist kollaps med tohånds-stabilisering og snap-reparation) er et gameplay-tungt, netværkssynkroniseret event oven i stormens VFX-peak. Den måles isoleret på Quest 2 **før** art pass, ikke først som del af PERF-001.

### PERF-001 Storm soak

Storm gentages/holdes aktiv 20 min. Log CPU/GPU, memory, thermal, network.

### DEV-002 Blandet siddende/stående

Én spiller siddende, én stående, på det fælles coop-objekt. Snap-zoner og gribehøjder skal fungere for begge, og kalibreringen må ikke kræve, at begge vælger samme opsætning.

### DEV-003 Afbrudt checkpoint-skrivning

Skrivning afbrydes (fuld disk eller proceskill) midt i checkpoint. Forrige checkpoint skal være intakt og indlæsbart. Den atomiske skrivestrategi er kun værd noget, hvis den er testet.

### COMPAT-002 Klokkeskævt content hash

Q1-build med ældre content hash mod Q3-build med nyere. Sessionen skal afvises tydeligt før spawn, ikke fejle undervejs.

### CONTENT-001 Missing personalization asset

Manglende/korrupt billede eller lyd bruger neutral fallback uden crash.

### COMPAT-001 Q1-Q3

Q1 legacy build joiner Q3 enhanced build med samme protocol/content hash og gennemfører fælles interaction.

## Playtest-protokol

- Observer uden at hjælpe.
- Markér alle steder med >10 sekunders stilstand.
- Registrér hvem der taler, hvem der udfører, og ventetid.
- Spørg efter missionen: mål, vigtigste valg, årsag til stormproblem, ønsket retry.
- Brug ikke kun udvikleren og kæresten som QA; mindst 2 eksterne par før release.

## Definition of Done - feature

- Acceptance criteria automatiseret eller dokumenteret.
- Demonstreret på to fysiske headset.
- Network authority/reconnect vurderet.
- Performance målt på Quest 2.
- Quest 1 smoke og Quest 3 regression hvis relevant.
- Subtitles/handedness/comfort vurderet.
- Ingen P0/P1.

## Definition of Done - release

- Alle release gates grønne.
- Known issues dokumenteret.
- Signed builds og rollback-build arkiveret.
- Sideload-guide testet af en person, der ikke skrev den.
- Backup af profile/assets og source tag oprettet.
