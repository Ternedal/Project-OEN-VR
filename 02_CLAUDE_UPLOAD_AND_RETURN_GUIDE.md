# Upload- og returguide

## Sådan gives projektet til Claude

Den foretrukne vej er at give Claude adgang til dette private repository og bede den starte med `01_PROMPT_FOR_CLAUDE.md`.

Alternativt:

1. Upload hele `PROJECT_OEN_CLAUDE_HANDOFF_v2.0.zip`.
2. Indsæt teksten fra `01_PROMPT_FOR_CLAUDE.md` som første besked.
3. Bed Claude bekræfte, at den har læst `00_READ_ME_FIRST.md`.
4. Lad Claude gennemføre reviewet før nogen kodegenerering.

## Det Claude skal returnere

- Hele reviewet i ét Markdown-dokument.
- Stabile ID'er: `CR-001`, `CR-002` osv.
- Ingen implementering eller omskrivning af source-of-truth i første svar.
- Kilder til platformpåstande.
- En afsluttende maskinlæsbar JSON-blok som specificeret i prompten.

Gem svaret som `review/CLAUDE_RAW_REVIEW.md` og send enten filen eller hele teksten tilbage. Derefter behandles hvert punkt i `review/RESPONSE_MATRIX.md` og den detaljerede backlog.
