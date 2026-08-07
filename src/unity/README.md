# `src/unity/` — kildefiler der IKKE er kompileret

**Alt i denne mappe er ukompileret og utestet.** Der findes ingen Unity Editor og intet Fusion 2 SDK i det miljø, filerne er skrevet i. Hver fil bærer en `UNVERIFIED-IN-SANDBOX`-header, der siger præcis hvad der er antaget om API'et.

Det er ikke en formalitet. Forskellen på denne mappe og `src/ProjectOen.Core/` er forskellen på "det burde virke" og "det er kørt og bestod".

## Hvorfor det alligevel er skrevet

Fordi bindingen er tynd. Al logik, der kan verificeres, ligger allerede i Core og er testet:

| Logik | Ligger i | Status |
|---|---|---|
| Coop-solverens matematik | `Core/Interaction/CoopSolver.cs` | 7 tests grønne |
| Compatibility handshake | `Core/Networking/CompatibilityHandshake.cs` | 7 tests grønne |
| Join code-alfabet og normalisering | `Core/Networking/JoinCode.cs` | 8 tests grønne |
| Fasemaskine og idempotens | `Core/Scenario/ScenarioDirector.cs` | 9 tests grønne |

Filerne her kalder den kode. De indeholder ikke deres egen kopi af den. Det er hele pointen med `docs/06` §11: *"Gameplay må ikke referere direkte til Photon-klasser."* Retningen holder også den anden vej — Fusion-laget ejer ingen regler.

## Rækkefølge

Rør ikke disse filer, før M0a er besvaret. Editorversion og pakkematrix er ikke låst endnu, og `ADR-006` gør editorvalget afhængigt af netop det svar.

Når M0a er grøn: følg `RUNBOOK_FUSION.md`.

## Filer

| Fil | Ansvar |
|---|---|
| `ProjectOen.Interaction/UnityConversions.cs` | Det eneste sted `Vec3` bliver til `Vector3`. Ét konverteringspunkt, ikke tredive |
| `ProjectOen.Networking/SessionCoordinator.cs` | Fusion-session, join code, coordinator uden live handover (ADR-020) |
| `ProjectOen.Networking/HandshakeExchange.cs` | Udveksler `BuildIdentity` og afviser før spawn |
| `ProjectOen.Networking/NetworkPlayerRig.cs` | Hoved og hænder, lokal pose-authority |
| `ProjectOen.Networking/NetworkedCoopObject.cs` | Fusion-binding omkring `CoopSolver` |
| `*/*.asmdef` | Assembly definitions med afhængighedsretningen fra `docs/16` |
