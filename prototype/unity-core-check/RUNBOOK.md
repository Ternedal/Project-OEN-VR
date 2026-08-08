# 15-minutters check: kompilerer Core i Unity?

Kør denne **før** M0a. Den er kort, og den fjerner risikoen fra 146 tests værd af kode, før du bruger timer på hardwaretesten.

## Hvorfor

`src/ProjectOen.Core` er bygget og testet med .NET SDK. Unity bruger sin egen compiler og læser **ikke** `.csproj` — den genererer sin egen ud fra `.asmdef`. Alt hvad der kom fra projektfilen frem for fra koden, kan derfor opføre sig anderledes.

Ét konkret eksempel var allerede fundet og rettet: nullable-annotationer (`string?`, `object?`) fik deres kontekst fra `<Nullable>enable</Nullable>` i csproj'en. Unity ville have givet CS8632 i 24 filer. Der står nu `#nullable enable` i hver fil, så de er selvstændige.

Det er præcis den slags, denne test er til for at fange resten af.

## Trin

1. Nyt tomt Unity-projekt (**samme editorversion du vil bruge til M0a**), eller genbrug M0a-spikeprojektet.
2. Opret mappen `Assets/ProjectOen/Scripts/Core/`.
3. Kopiér **hele indholdet** af `src/ProjectOen.Core/` derind — undtagen `bin/`, `obj/` og `ProjectOen.Core.csproj`.
4. Læg denne fil som `Assets/ProjectOen/Scripts/Core/ProjectOen.Core.asmdef`:

```json
{
  "name": "ProjectOen.Core",
  "rootNamespace": "ProjectOen.Core",
  "references": [],
  "noEngineReferences": true
}
```

`noEngineReferences: true` er ikke kosmetik. Det er compilerens håndhævelse af `docs/06` §11 — Core *kan* ikke komme til at referere Unity, uanset hvad nogen skriver senere.

5. Lad Unity kompilere. Åbn Console.

## Hvad der skal ske

**Nul fejl. Nul warnings.**

`AssemblyInfo.cs` indeholder `InternalsVisibleTo("ProjectOen.Core.Tests")`. Den testassembly findes ikke i Unity — det er harmløst og giver ingen fejl.

## Hvis der kommer fejl

Notér **fejlkode og fil** ordret og meld dem. Sandsynlige kandidater, hvis noget dukker op:

| Kode | Betyder | Rettelse |
|---|---|---|
| CS8632 | En fil mangler `#nullable enable` | Tilføj linjen øverst |
| CS8370 | Sprogfunktion nyere end Unitys `LangVersion` | Skriv om — Core skal holde sig til C# 9 |
| CS0518 / `IsExternalInit` | `init`-accessor på netstandard2.1 | Findes ikke i Core i dag; meld hvis den dukker op |
| CS0246 om `System.Text.Json` | Kun testkoden bruger den, ikke Core | Så er en testfil røget med — fjern den |

Meld dem samlet frem for én ad gangen. De hænger typisk sammen.
