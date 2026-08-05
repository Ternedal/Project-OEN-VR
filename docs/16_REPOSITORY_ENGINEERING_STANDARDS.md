# Repository- og engineeringstandarder

## Foreslået struktur

```text
Assets/ProjectOen/
  Art/
  Audio/
  Content/
    Scenarios/
    Events/
    Items/
    Recipes/
    Localization/
  Prefabs/
  Scenes/
    Boot/
    Lobby/
    Shared/
    Stormnatten/
  Scripts/
    Core/
    Gameplay/
    Interaction/
    Networking/
    Persistence/
    Platform/
    UI/
    Editor/
  Tests/
    EditMode/
    PlayMode/
Packages/
ProjectSettings/
BuildScripts/
Docs/
PrivateContent/   # gitignored
```

## Assembly definitions

Én asmdef per arkitekturmodul. Dependencies følger retningen:

`Core <- Gameplay <- Presentation/Interaction`

Networking implementerer interfaces defineret i gameplay/core, ikke omvendt.

## C# standard

- Nullable reference annotations hvor realistisk.
- Ingen `FindObjectOfType` i runtime core paths.
- Ingen public mutable fields uden klar Unity-serialisering.
- `Try...`/Result patterns ved forventede fejl.
- Cancellation/lifetime håndteres ved async scene loading.
- Ingen string-baserede IDs i spredt kode; brug typed IDs/wrappers eller central constants.
- Logs gennem fælles logger med category og build stripping.

## Unity-regler

- Prefabs har klar owner og dokumenteret network behavior.
- ScriptableObjects er definitionsdata, ikke mutable runtime state.
- Runtime state ligger i services/components/save snapshots.
- Scene references valideres i editor tool.
- Coroutines må ikke være skjult state machine for kritisk gameplay; brug explicit phase/sequence state.

## Testkrav for PR

PR med gameplayændring skal mindst indeholde:

- test eller begrundelse,
- acceptance criteria,
- network/save impact,
- device profile impact,
- screenshot/log ved fysisk test hvis relevant.

## Commits

Conventional-ish:

- `feat:`
- `fix:`
- `refactor:`
- `test:`
- `docs:`
- `build:`
- `perf:`

Commit skal være én forståelig ændring. AI-genererede kæmpecommits undgås.

## Pull request gate

- Scope matcher issue.
- Ingen nye warnings.
- Tests grønne.
- Package lock ikke ændret utilsigtet.
- Ingen private assets/secrets.
- Architecture dependency direction bevaret.
- Fysisk device-test noteret, hvis interaktion/render/network ændres.

## Git LFS

Bruges til:

- `.fbx`, `.blend`, store textures, audio, video.

Private personlige assets må ikke blot beskyttes af LFS; de skal ligge i gitignored/private storage.

## Issue labels

- `epic`, `story`, `bug`, `tech-debt`, `spike`, `content`, `qa`.
- `platform:q1`, `platform:q2`, `platform:q3`.
- `area:network`, `area:interaction`, `area:gameplay`, `area:save`, `area:art`, `area:audio`.
- `priority:p0` ... `priority:p3`.
- `status:blocked`, `needs-device-test`, `needs-review`.

## AI-assistance policy

- AI må generere et lille, reviewbart change-set.
- Hvert script skal have en defineret plads i arkitekturen.
- Ingen “manager” eller singleton tilføjes uden begrundelse.
- Ingen package opgradering som sideeffekt.
- AI-output testes i Editor og på device før næste system bygges ovenpå.
