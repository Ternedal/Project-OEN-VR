# Repository status

- Handoff baseline: v2.0
- Review state: **Claude review v1.0 modtaget 2026-08-06** — verdict `PROCEED_WITH_BLOCKERS` (2 BLOCKER, 5 HIGH, 3 MEDIUM, 6 konflikter)
- Response state: **foreslået ændringspakke ligger på branchen `review/response-v1`** — ikke merget
- Implementation state: Not started — gaten i `docs/24` er ikke passeret
- Next gate: **M0a — starter og tracker Unitys OpenXR-provider fysisk på Quest 1?** Alt andet i M0 venter på det svar
- Quest policy: Q2 performancegulv (EOL dec. 2027), Q3/3S enhanced parity. **Q1-lanen afgøres af M0a**, jf. ADR-019

## Hvad ejeren skal gøre

1. Gennemgå branchen `review/response-v1` — én commit pr. fundgruppe, så enkelte kan droppes.
2. Svar på Q-001 (droppes Q1 hvis OpenXR fejler?), Q-004 (hvilke P1-items er med i gaveversionen?) og Q-005 (Unity-licenstier).
3. Merge til `main`, hvorefter `docs/24`-gaten er passeret på alt undtagen CR-002 og CR-005.
4. Kør M0a på hardware.

## Filer

- Review: [`review/CLAUDE_RAW_REVIEW.md`](review/CLAUDE_RAW_REVIEW.md)
- Dispositioner: [`review/RESPONSE_MATRIX.md`](review/RESPONSE_MATRIX.md)
- M0-issuetekst: [`docs/30_M0_ISSUE_BODY.md`](docs/30_M0_ISSUE_BODY.md) (revideret efter CR-001/CR-002)
