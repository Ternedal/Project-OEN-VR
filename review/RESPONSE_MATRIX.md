# Response matrix til Claude-kommentarer

Reviewet ligger i [`CLAUDE_RAW_REVIEW.md`](CLAUDE_RAW_REVIEW.md) (review version 1.0, 2026-08-06).

**Status 2026-08-06:** Dispositionerne nedenfor er *foreslåede* og udført på branchen `review/response-v1`. De er ikke merget til `main`.
Ejeren kan acceptere ved at merge, ændre ved at rette på branchen, eller afvise ved at droppe den relevante commit — der er én commit pr. fundgruppe.

To punkter kan **ikke** lukkes uden ejerens input: CR-002 (kræver fysisk Q1-test) og CR-005 (kræver P1-udvælgelse).

| Comment ID | Severity | Summary | Disposition | Rationale | Required evidence | Affected docs | ADR/change ID | Status |
|---|---|---|---|---|---|---|---|---|
| CR-001 | BLOCKER | M0's gate kræver netværksbevis, men alle Photon-items ligger i M2 | ACCEPT | M0's gate kunne ikke bevises af M0's opgaver. Seks items flyttet fra M2; stop/go flyttet fra timeloft til M0-afslutning. | Nej — dokumentændring | `docs/12`, `docs/17`, `docs/14`, `docs/06`, `docs/30` | M0-REV-01 | **Implementeret** — afventer godkendelse |
| CR-002 | BLOCKER | Q1-lanen er et andet XR-backend, ikke en pakkeversion; Oculus-provider er deprecated | ACCEPT_WITH_MODIFICATION | Fundet accepteres. Løsningen er ikke at droppe Q1 nu, men at gøre lanen afhængig af ét fysisk eksperiment (ADR-019). Kræver hardware. | Ja — fysisk test af OpenXR på Quest 1 | `docs/06`, `docs/08`, `docs/14`, `docs/18`, `docs/30` | ADR-019 | **Delvist** — dokumenteret, afventer test |
| CR-003 | HIGH | Unity 2022.3 LTS er uden for support på Personal/Pro | ACCEPT | Begrundelsen for 2022.3 var faktuelt forkert på Personal/Pro. Editorvalget er nu M0-afhængigt med Unity 6 LTS som foretrukken kandidat. | Nej — Q-005 besvares | `docs/01`, `docs/06`, `docs/22`, `docs/18` | ADR-006 rev. | **Implementeret** — bekræft licenstier (Q-005) |
| CR-004 | HIGH | Quest 2 er EOL dec. 2027, inden for projektets egen tidshorisont | ACCEPT | Ren formuleringsrettelse. Quest 2 bevares som performancegulv; EOL-datoerne er nu skrevet ind, og Quest 3S er antaget baseline efter v1.0. | Nej — formulering | `docs/01`, `docs/08`, `docs/12`, `docs/18` | ADR-003 rev. | **Implementeret** |
| CR-005 | HIGH | Roadmap-intervaller er ikke udledt af backloggen; ingen scope-markering | ACCEPT_WITH_MODIFICATION | Kolonnen `Gaveversion` er tilføjet og P0 forudfyldt som `In` (afledt af docs/12's egen P0-definition). P1-udvælgelsen kan kun foretages af ejeren — 56 items står `TBD`. | Nej — scope-valg | `docs/12`, `docs/14`, `docs/17`, `docs/01` | SCOPE-01 | **Delvist** — afventer P1-valg (Q-004) |
| CR-006 | HIGH | Skemaer mangler felter fra `docs/10` og er lukkede; CI giver falsk tryghed | ACCEPT | Skemaerne manglede felter docs/10 kræver og var samtidig lukkede. Rettet, checksum defineret, og valideringen håndhæver nu kontrakten i CI. | Nej — skemaændring | `docs/10`, `schemas/`, `tools/` | DATA-01 | **Implementeret** |
| CR-007 | HIGH | "Begge aktive" har to grænseværdier og ingen målemetode | ACCEPT | 12 sek. som designregel, 20 sek. som testgrænse — skrevet eksplicit i alle fire dokumenter. UX-002 omskrevet til automatisk måling fra event-journalen. | Nej — vælg værdi + instrumentér | `docs/02`, `docs/04`, `docs/05`, `docs/13` | QA-01 | **Implementeret** |
| CR-008 | MEDIUM | Ingen lokaliseringsopgave, men build fejler ved manglende key | ACCEPT_WITH_MODIFICATION | ADR-021 (dansk som eneste sprog) foreslået og PO-104 tilføjet. Beslutningen kræver ejerens svar på Q-007. | Nej — Q-007 besvares | `docs/09`, `docs/10`, `docs/17`, `docs/19` | ADR-021 | **Delvist** — afventer Q-007 |
| CR-009 | MEDIUM | 90 sek. reconnect-vindue er ikke afstemt med Quest standby | NEEDS_EVIDENCE | 90 sek. er et gæt. Målingen er lagt ind i M2 som eksplicit opgave; vinduet sættes efter data. | Ja — måling på Q2/Q3 i M2 | `docs/07`, `docs/13` | M2-MEAS-01 | Open — knyttet til M2 |
| CR-010 | MEDIUM | Ingen backlog-item for selve reviewbehandlingen | ACCEPT | PO-000 tilføjet som M0/P0, 12 t. | Nej — backlog-tilføjelse | `docs/17`, `docs/24` | PO-000 | **Implementeret** |

## Konflikter

| Conflict ID | Kilde A | Kilde B | Anbefalet autoritet | Disposition | Status |
|---|---|---|---|---|---|
| CONFLICT-001 | `docs/12` M0-gate | `docs/17` milepælstildeling | `docs/12` | ACCEPT — docs/12 er autoritativ | **Lukket** |
| CONFLICT-002 | `docs/04` §8 (12 sek.) | `docs/02`, `docs/05` (20 sek.) | `docs/04` som designregel | ACCEPT — 12 s designregel, 20 s testgrænse | **Lukket** |
| CONFLICT-003 | `docs/10` feltbeskrivelser | `schemas/*.json` | `docs/10` | ACCEPT — skemaerne rettet efter docs/10 | **Lukket** |
| CONFLICT-004 | `docs/01`, ADR-006 (3-årig LTS) | Unitys LTS-politik (2 år) | Unity | ACCEPT — Unitys politik er autoritativ | **Lukket** |
| CONFLICT-005 | `docs/01` (620 t) | `docs/14` + beregnet (622 t) | Beregnet sum | ACCEPT — 622 er beregnet; nu 634 efter PO-000 | **Lukket** |
| CONFLICT-006 | `docs/07` §11 (revision) | `schemas/savegame.schema.json` | `docs/07` | ACCEPT — revision gjort påkrævet | **Lukket** |

## Behandlingsregler

- Blockers behandles først.
- En kommentar kan ikke markeres Closed uden dokumentændring, ADR eller dokumenteret afvisning.
- `NEEDS_EVIDENCE` skal knyttes til en spike/testcase.
- Claude's formulering kopieres ikke automatisk ind i spec; intentionen vurderes først.
- Efter behandling bumpes package version og changelog.
