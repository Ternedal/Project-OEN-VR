# Localization source

`da.source.json` er ChatGPT-ejet source-copy for dansk.

## Status

- Ikke en Unity-runtime-kontrakt endnu.
- Keys og source-copy kommer fra `docs/40_UX_COPY_AND_LOCALIZATION_CATALOG.md`.
- Claude må bruge filen som input til den Unity-side localization-løsning, når den implementeres.
- Private personalization-tekst må ikke lægges her; den ligger som `textOverrides` i privat profile.

## Regler

- Nye spillerrettede strings får key før de hardcodes.
- Voice lines har subtitle-equivalent.
- Runtime fallback og build-validation implementeres senere.
- `PO-104` kan fortsat være deferred som fuld localization/subtitle-pass; denne mappe reducerer authoring-risikoen nu.
