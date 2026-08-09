# App-laget (Unity-projektets egne scripts)

Disse filer hører til `ProjektOenApp` (Unity 6000.4.10f1) og er versionsstyret her, fordi Unity-projektet
selv ligger uden for repoet. `src/unity/ProjectOen.Networking/` og `ProjectOen.Interaction/` er
*bindingen* (Fusion-typer); dette er *applikationen*, der wirer bindingen sammen med XR og scenen.

| Fil | Placering i Unity-projektet | Rolle |
|---|---|---|
| `M0bHeadRig.cs` | `Assets/Scripts/` | Driver tre transforms fra de levende XR-devices |
| `CoopGame.cs` | `Assets/Scripts/` | To-spiller co-op-scenen: session, rig-spawn, handshake, greb |
| `CoopGameSetup.cs` | `Assets/Editor/` | Headless scene-opbygning + APK-build |

## Hvorfor `InputDevices` og ikke `TrackedPoseDriver`

`M0bHeadRig` læser `XRNode.Head/LeftHand/RightHand` via `InputDevices.GetDevicesAtXRNode` +
`TryGetFeatureValue(CommonUsages.devicePosition/deviceRotation)`. Det er den binding-frie vej, M0a
beviste på præcis dette rig. En programmatisk `AddComponent<TrackedPoseDriver>()` får ingen
input-action-bindinger og skriver nul-pose — det kostede en fejlsøgningsrunde i M0b inkrement 3.
Se `src/unity/RUNBOOK_FUSION.md` §8.

## Handshake-gaten (docs/07 §5)

`CoopGame` spawner `Handshake.prefab` (NetworkObject + `HandshakeExchange`) **før** rig og kasse, kalder
`Configure(BuildIdentity)` i `onBeforeSpawned`, og venter op til 2 s på en peers annoncering.

`_enforceHandshakeGate` er **false** som default: resultatet logges, men blokerer ikke spawn. Det er
bevidst — en fejl i gaten må ikke kunne spærre co-op-testen. Sæt den til `true` for at teste den rigtige
afvisning (COMPAT-002), og byg den anden klient med et andet `_contentHash`.

Bygget identitet sættes i inspektoren på `CoopGame`: `_gameVersion`, `_protocolVersion`, `_contentHash`,
`_saveSchemaVersion`, `_platformProfile`.

## Verifikationsstatus

- **Compile + build:** verificeret headless (IL2CPP/ARM64).
- **Per-klient runtime:** verificeret on-device (session, spawn m. authority, head-tracking, greb → solver).
- **Handshake-afvisning mellem to klienter:** **ikke verificeret** — kræver to headset. Se
  `src/unity/RUNBOOK_FUSION.md` §9.
