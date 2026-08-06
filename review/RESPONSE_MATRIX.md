# Response matrix til Claude-kommentarer

Reviewet ligger i [`CLAUDE_RAW_REVIEW.md`](CLAUDE_RAW_REVIEW.md) (review version 1.0, 2026-08-06).

Kolonnerne **Disposition**, **Rationale**, **ADR/change ID** og **Status** udfyldes af ejeren. De øvrige er udfyldt fra reviewet.

| Comment ID | Severity | Summary | Disposition | Rationale | Required evidence | Affected docs | ADR/change ID | Status |
|---|---|---|---|---|---|---|---|---|
| CR-001 | BLOCKER | M0's gate kræver netværksbevis, men alle Photon-items ligger i M2 | | | Nej — dokumentændring | `docs/12`, `docs/17`, `docs/14`, `docs/06`, `docs/30` | | Open |
| CR-002 | BLOCKER | Q1-lanen er et andet XR-backend, ikke en pakkeversion; Oculus-provider er deprecated | | | Ja — fysisk test af OpenXR på Quest 1 | `docs/06`, `docs/08`, `docs/14`, `docs/18`, `docs/30` | | Open |
| CR-003 | HIGH | Unity 2022.3 LTS er uden for support på Personal/Pro | | | Nej — Q-005 besvares | `docs/01`, `docs/06`, `docs/22`, `docs/18` | | Open |
| CR-004 | HIGH | Quest 2 er EOL dec. 2027, inden for projektets egen tidshorisont | | | Nej — formulering | `docs/01`, `docs/08`, `docs/12`, `docs/18` | | Open |
| CR-005 | HIGH | Roadmap-intervaller er ikke udledt af backloggen; ingen scope-markering | | | Nej — scope-valg | `docs/12`, `docs/14`, `docs/17`, `docs/01` | | Open |
| CR-006 | HIGH | Skemaer mangler felter fra `docs/10` og er lukkede; CI giver falsk tryghed | | | Nej — skemaændring | `docs/10`, `schemas/`, `tools/` | | Open |
| CR-007 | HIGH | "Begge aktive" har to grænseværdier og ingen målemetode | | | Nej — vælg værdi + instrumentér | `docs/02`, `docs/04`, `docs/05`, `docs/13` | | Open |
| CR-008 | MEDIUM | Ingen lokaliseringsopgave, men build fejler ved manglende key | | | Nej — Q-007 besvares | `docs/09`, `docs/10`, `docs/17`, `docs/19` | | Open |
| CR-009 | MEDIUM | 90 sek. reconnect-vindue er ikke afstemt med Quest standby | | | Ja — måling på Q2/Q3 i M2 | `docs/07`, `docs/13` | | Open |
| CR-010 | MEDIUM | Ingen backlog-item for selve reviewbehandlingen | | | Nej — backlog-tilføjelse | `docs/17`, `docs/24` | | Open |

## Konflikter

| Conflict ID | Kilde A | Kilde B | Anbefalet autoritet | Disposition | Status |
|---|---|---|---|---|---|
| CONFLICT-001 | `docs/12` M0-gate | `docs/17` milepælstildeling | `docs/12` | | Open |
| CONFLICT-002 | `docs/04` §8 (12 sek.) | `docs/02`, `docs/05` (20 sek.) | `docs/04` som designregel | | Open |
| CONFLICT-003 | `docs/10` feltbeskrivelser | `schemas/*.json` | `docs/10` | | Open |
| CONFLICT-004 | `docs/01`, ADR-006 (3-årig LTS) | Unitys LTS-politik (2 år) | Unity | | Open |
| CONFLICT-005 | `docs/01` (620 t) | `docs/14` + beregnet (622 t) | Beregnet sum | | Open |
| CONFLICT-006 | `docs/07` §11 (revision) | `schemas/savegame.schema.json` | `docs/07` | | Open |

## Behandlingsregler

- Blockers behandles først.
- En kommentar kan ikke markeres Closed uden dokumentændring, ADR eller dokumenteret afvisning.
- `NEEDS_EVIDENCE` skal knyttes til en spike/testcase.
- Claude's formulering kopieres ikke automatisk ind i spec; intentionen vurderes først.
- Efter behandling bumpes package version og changelog.
