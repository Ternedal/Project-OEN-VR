# Repository status

- Handoff baseline: **v2.1** (review v1.0 behandlet og merget 2026-08-07)
- Review state: Lukket for 8 af 10 fund. **Åbne:** CR-002 (kræver fysisk Q1-test), CR-005 (kræver P1-udvælgelse)
- Implementation state: Not started på `main`. Arbejdet ligger på `agent/m0-platform-feasibility`
- **Næste gate: M0a — starter og tracker Unitys OpenXR-provider fysisk på Quest 1?** Alt andet i M0 venter på det svar
- Quest policy: Q2 performancegulv (EOL dec. 2027), Q3/3S enhanced parity. Q1-lanen afgøres af M0a, jf. ADR-019

## På `agent/m0-platform-feasibility`

- `prototype/m0a-openxr-smoke/` — runbook, resultatskema og drop-in kildefiler til hardwaretesten.
- `src/` — Core-fundament i ren C# (typed IDs, kanonisk JSON, save-checksum, atomisk skrivning, scenario-kontrakt). 22 tests grønne, kørt uden Unity.

Merges til `main`, når M0a er besvaret og editorversionen dermed er afgjort.

## Hvad ejeren skal gøre

1. **Kør M0a** efter `prototype/m0a-openxr-smoke/RUNBOOK.md` på agent-branchen. Ét spørgsmål: starter og tracker den på Quest 1?
2. Udfyld `RESULTAT.md` og meld `GO`, `REDESIGN` eller `DROP_Q1_RUNTIME`.
3. Vælg P1-scope (Q-004): hvilke af de 56 `Gaveversion = TBD`-items er med i gaveversionen?
4. Opret M0-issuet fra `docs/30_M0_ISSUE_BODY.md` (token mangler `issues`-scope).

## Filer

- Eksekveringsplan: [`docs/32_OPUS_EXECUTION_PLAN.md`](docs/32_OPUS_EXECUTION_PLAN.md)
- Review: [`review/CLAUDE_RAW_REVIEW.md`](review/CLAUDE_RAW_REVIEW.md)
- Dispositioner: [`review/RESPONSE_MATRIX.md`](review/RESPONSE_MATRIX.md)
- M0-issuetekst: [`docs/30_M0_ISSUE_BODY.md`](docs/30_M0_ISSUE_BODY.md)
