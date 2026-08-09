# Runbook — Fusion 2-laget ind i Unity-projektet

**Forudsætning: M0a er besvaret.** Editorversion og pakkematrix er ikke låst før det, og `ADR-006` gør editorvalget afhængigt af netop det svar. Gør du dette først, risikerer du at bygge oven på en stak, der skal skiftes ud.

Regn med 3-5 timer, hvoraf det meste er første gangs opsætning.

## 1. Mappestruktur

`docs/16` foreskriver strukturen. Læg filerne sådan:

```
Assets/ProjectOen/Scripts/
  Core/            <- HELE src/ProjectOen.Core/ kopieres hertil, uændret
    ProjectOen.Core.asmdef
  Interaction/     <- src/unity/ProjectOen.Interaction/
  Networking/      <- src/unity/ProjectOen.Networking/
```

Core kopieres **uden ændringer**. Filerne er `netstandard2.1` uden `UnityEngine`-referencer netop for at kunne flyttes 1:1. Ændrer du dem her, mister du testdækningen — 82 tests kører kun mod `src/`.

Opret `ProjectOen.Core.asmdef`:

```json
{
  "name": "ProjectOen.Core",
  "rootNamespace": "ProjectOen.Core",
  "references": [],
  "noEngineReferences": true
}
```

`noEngineReferences: true` er ikke kosmetik. Det er compilerens håndhævelse af `docs/06` §11 — Core kan ikke komme til at referere Unity, uanset hvad nogen skriver senere.

## 2. Fusion 2 SDK

1. Opret konto på dashboard.photonengine.com, opret en **Fusion**-app, kopiér App ID.
2. Hent Fusion 2 SDK som `.unitypackage` fra Photons dokumentation og importér.
3. Fusion Hub → indsæt App ID.
4. Project Settings → Editor → Asset Serialization → **Force Text** (Fusion kræver det).

**Omkostning: 0 kr.** Fusions gratis plan giver 100 CCU til både udvikling og kommerciel brug for én app. To spillere er langt under.

## 3. Verificér API'et FØR du bygger videre

Alle filer i `src/unity/` bærer en `UNVERIFIED-IN-SANDBOX`-header med de konkrete API-antagelser. Gennemgå dem mod den installerede SDK-version, før du bruger tid på at wire scener.

Det mest sandsynlige afvigelsespunkt er `NetworkArray<T>` med `[Capacity(2)]` i `NetworkedCoopObject`. Afviger signaturen, erstattes de to arrays af fire separate `[Networked]`-properties — trivielt, men gør det først, så compile-fejlene ikke stabler sig.

Meld hvilken der fejler. Hver af dem har et alternativ.

## 4. Scene-opsætning

1. `NetworkRunner`-prefab med `SessionCoordinator`.
2. `NetworkPlayerRig`-prefab: hoved + to hænder, tildelt i inspektoren. `_localHead`/`_localLeftHand`/`_localRightHand` peger på XR Origin's egne transforms.
3. `HandshakeExchange` på en `NetworkObject`, der spawnes ved sessionsstart. Kald `Configure()` med buildets `BuildIdentity` **før** spawn.
4. Den tunge kasse: `NetworkObject` + `NetworkedCoopObject`. Sæt `_gripSpan` til kassens faktiske gribeafstand.

## 5. Hvad der skal verificeres, og i hvilken rækkefølge

Stop ved første røde. Går du videre, ved du ikke længere hvilken ændring der knækkede hvad.

| # | Test | Accept |
|---|---|---|
| 1 | To editor-instanser joiner samme kode | Begge ser hinandens hoved og hænder |
| 2 | Join med forkert kode | Afvises tydeligt, ingen session |
| 3 | Handshake med forskellig `PlatformProfile` | **Accepteres** — grafikprofil må afvige på Q2↔Q3-lanen |
| 4 | Handshake med forskelligt content hash | Afvises før spawn (COMPAT-002) |
| 5 | Begge griber kassen | Den følger midtpunktet på begge klienter |
| 6 | Én slipper | Kassen bliver markant tungere at flytte |
| 7 | Træk hænderne fra hinanden | Kvaliteten falder gradvist, ikke i ét spring |
| 8 | Én klient lukkes under greb | Den anden pauser, ingen kasse i ingenmandsland |
| 9 | 10× løft cross-device (PO-025) | Identisk slutposition, 10/10 |

Test 5-7 er de samme regler, `CoopSolverTests` allerede har bevist i C#. Afviger de på device, er det bindingen der er gal — ikke solveren. Det er hele grunden til at skille dem ad.

## 6. Måling der ikke må glemmes (CR-009)

`docs/07` §10 foreslår 90 sekunders reconnect-vindue. **Det tal er et gæt.** Quest går i standby få sekunder efter aftagning, så den hyppigste virkelige afbrydelse — "jeg tog headsettet af for at åbne døren" — kan overskride vinduet og ramme den dyre sti.

Mål det:

1. Start session, tag headsettet af, start et stopur.
2. Notér hvornår Fusion melder disconnect på den anden klient.
3. Tag headsettet på igen, notér om reconnect lykkes.
4. Gentag på både Quest 2 og Quest 3 — de kan opføre sig forskelligt.

Sæt vinduet efter tallene og opdatér `docs/07` §10. Det er CR-009's `NEEDS_EVIDENCE`.

## 7. Når det virker

Opdatér `config/COMPATIBILITY_MATRIX.md` med de faktiske resultater, sæt ADR-008 til `Accepted` via response matrix, og tag en release med zip som asset.

## 8. On-device resultater (M0b inkrement 1-3 · 9. august 2026)

Bevist på Quest (serial 1WMHH818L30444, `com.projectoen.app`, IL2CPP/ARM64, Unity 6000.4.10f1, Fusion 2.0.12):

- **Feasibility:** `NetworkRunner.StartGame` (Shared) forbinder til Photon — `[Fusion] adding player [Player:1]`. App Id sat i `PhotonAppSettings`.
- **Inkrement 1 (kasse):** `Runner.Spawn` af `NetworkedCoopObject` med state authority; `CoopSolver` kører stabilt (`quality=1.00`).
- **Inkrement 2 (rig):** `Runner.Spawn` af `NetworkPlayerRig` med input authority; `BindLocalRig` binder de lokale kilder. Ingen NullRef.
- **Inkrement 3b (greb→kasse):** simuleret `SubmitHandTarget(gripping=true)` → fase `Released`→`HeldByOne` → `CoopSolver` flytter `boxPos.X` langs et sinus-mål, `quality` holder 1.00. Hele den netværkede interaktion (spawn m. authority → greb → solver → replikering) er de-risket på hardware.

### Kritisk config: AssembliesToWeave
`Assets/Photon/Fusion/Resources/NetworkProjectConfig.fusion` → `AssembliesToWeave` SKAL indeholde `ProjectOen.Networking` og `ProjectOen.Interaction`, ellers fejler spawn med *"Type … has not been weaved"*. Efter ændring: tving en recompile (rør en kildefil) — weaveren kører kun ved recompile. Projekt-lokal config (App Id/TickRate) dokumenteres som post-import-trin; commit den ikke.

### Head-tracking: brug InputDevices, ikke en ubundet TrackedPoseDriver (VERIFICERET on-device)
Inkrement 3 loggede `head=(0.00,0.00,0.00)` — også da headsettet blev bevæget. Årsag: en programmatisk `AddComponent<TrackedPoseDriver>()` får INGEN input-action-bindinger og skriver derfor nul-pose til kameraet (den overskriver endda den satte `localPosition`). M0a beviste tracking på præcis dette rig via den robuste, binding-frie vej: `UnityEngine.XR.InputDevices.GetDevicesAtXRNode(XRNode.Head/LeftHand/RightHand)` + `TryGetFeatureValue(CommonUsages.devicePosition/deviceRotation)`. **Konklusion:** driv `NetworkPlayerRig._localHead/_localLeftHand/_localRightHand` fra `InputDevices` (ikke fra en ubundet TrackedPoseDriver). Replikerings-halvdelen (`[Networked]` pose + interpolation) er allerede compile- og spawn-sund; det, der manglede, var en levende pose-kilde.

**Bekræftet 2026-08-09 (inkrement 4):** med `InputDevices`-kilden logger samme scene ikke-nul, bevægelig
hovedpose (`head=(-0.01, 1.18, -0.05)` → `(0.08, 1.19, -0.09)`, Y ≈ 1,14-1,20 m over gulv-origin), mens
greb→solver-kæden fortsat holder `quality` 1,00. Mønsteret ligger i `Assets/Scripts/M0bHeadRig.cs`:
tre transforms drevet af `GetDevicesAtXRNode` + `TryGetFeatureValue`, bundet ind i `NetworkPlayerRig`
via `BindLocalRig` i `Runner.Spawn(..., onBeforeSpawned)`.

## 9. Status: hvad der mangler on-device (to headset)

Alt **per-klient** er de-risket på hardware. Følgende kræver to Quests samtidig og er **ikke** verificeret:

| # | Venter på | Accept |
|---|---|---|
| 1 | Head/hands replikeret mellem to klienter | Begge ser hinandens hoved og hænder bevæge sig |
| 2 | Handshake-gaten afviser version-mismatch | Afvist før spawn (COMPAT-002) |
| 3 | Kassen delt mellem to spillere | Identisk position på begge klienter; `HeldByTwo` ved to greb |
| 4 | 10× løftetest (PO-025) | Identisk slutposition, 10/10 |
| 5 | 72 Hz i minimal netværksscene | Stabil, ingen vedvarende drops |
| 6 | Reconnect-vinduet (CR-009) | Måles, jf. §6 |

Resultaterne føres ind i `config/COMPATIBILITY_MATRIX.md`.
