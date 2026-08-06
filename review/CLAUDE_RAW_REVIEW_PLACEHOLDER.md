# Claude raw review — placeholder

**Reviewet er leveret.** Se [`CLAUDE_RAW_REVIEW.md`](CLAUDE_RAW_REVIEW.md) (review version 1.0, 2026-08-06, verdict `PROCEED_WITH_BLOCKERS`).

Denne fil bevares, fordi `tools/validate_handoff.py` har den på listen over påkrævede filer. Den indeholder ikke længere selve reviewet.

Krav til fremtidige reviews:

- Bevar kommentar-ID'er `CR-001`, `CR-002` osv. på tværs af review-runder.
- Bevar konflikt-ID'er `CONFLICT-001`, `CONFLICT-002` osv.
- Indarbejd ikke anbefalingerne direkte i source of truth, før de er behandlet i [`RESPONSE_MATRIX.md`](RESPONSE_MATRIX.md).
- Afslut med den maskinlæsbare JSON-blok fra `01_PROMPT_FOR_CLAUDE.md`.
