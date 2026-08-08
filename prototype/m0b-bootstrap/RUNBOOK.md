# M0b — bootstrap af det rigtige Projekt Øen Unity-projekt

M0a er afgjort (Quest 2 kører OpenXR; Quest 1 = DROP_Q1_RUNTIME). M0b bygger selve
produktprojektet: Unity-projekt, låste pakker, Core-laget i Unity, og Photon-netværk.

Bootstrappen er delt i to faser, fordi **Photon Fusion 2 ikke ligger i Unity-registret** —
den kræver din konto. Fase 1 er Photon-uafhængig og kan køres nu.

---

## Fase 1 — projekt + pakker + Core + XR (Photon-uafhængig)

Én kommando (samme mønster som M0a, bygget på det der virkede):

```powershell
cd C:\Users\admin\Desktop\Project-OEN-VR\prototype\m0b-bootstrap
.\Bootstrap-M0b.ps1 -UnityPath "C:\Program Files\Unity\Hub\Editor\6000.4.10f1\Editor\Unity.exe"
```

Den opretter `ProjektOenApp` ved siden af repoet, skriver pakke-manifestet (ASCII, ingen
BOM), kopierer **hele Core-laget** ind som `Assets/ProjectOen/Core` med en asmdef, og
konfigurerer OpenXR + Meta Quest + Oculus Touch via `M0bConfigure.cs` (præcis den XR-kode,
der blev verificeret on-device i M0a).

**Accept efter Fase 1:** Unity åbner projektet uden compile-fejl, `[M0B-SETUP]`-loggen viser
`Configure: færdig`, og `ProjectOen.Core` kompilerer som en Unity-assembly. Dermed er PO-001
(pin editor/pakker) og "Core i Unity" bevist.

---

## Photon-trin (kun dig — ~5 min)

1. Opret gratis konto på **dashboard.photonengine.com**.
2. Ny app → type **Fusion** → navn "Projekt Oen" → **Create**. Kopiér **App ID**.
3. Hent **Photon Fusion 2 SDK** (fra Photons side) og importér `.unitypackage` i `ProjektOenApp`.
4. Fusion Hub → indsæt **App ID** under Fusion.
5. Sig til — så kører vi Fase 2.

Jeg kan hverken oprette kontoen eller acceptere Photons vilkår for dig; det skal være din konto.

---

## Fase 2 — netværkslaget (efter Photon er importeret)

Kopiér `src/unity` ind i projektet og læg `ProjectOen.Unity.asmdef` (i `templates/`) ved
siden af:

```powershell
$app = "C:\Users\admin\Desktop\ProjektOenApp"
$repo = "C:\Users\admin\Desktop\Project-OEN-VR"
New-Item -ItemType Directory -Force -Path "$app\Assets\ProjectOen\Unity" | Out-Null
Copy-Item "$repo\src\unity\*" "$app\Assets\ProjectOen\Unity" -Recurse -Force
Copy-Item "$repo\prototype\m0b-bootstrap\templates\ProjectOen.Unity.asmdef" "$app\Assets\ProjectOen\Unity\ProjectOen.Unity.asmdef" -Force
```

`ProjectOen.Unity.asmdef` refererer `ProjectOen.Core`, `Fusion.Runtime`, `Unity.XR.Interaction.Toolkit`,
`Unity.InputSystem`, `Unity.XR.CoreUtils`. Kompilerer først når Fusion er importeret.

De fire Fusion-filer bærer eksplicitte **API-antagelser** i deres header (NetworkBehaviour,
`[Networked]`, `StartGameArgs`, `NetworkArray`, RPC-attributter). Meld den første compile-fejl —
der ligger et alternativ klar for hver antagelse. Det er selve M0b-feasibility-testen:
kompilerer Fusion-bindingen mod den installerede SDK-version?

**Accept efter Fase 2 (M0b-gaten, jf. docs/17, Q1 udgået):** privat session mellem to klienter,
compatibility handshake afviser mismatch før spawn, head/hands replikeres, `CoopObjectController`
holder den tunge kasse identisk på begge klienter (10× løftetest Q2↔Q3), 72 Hz i minimal scene.

---

## Hvorfor to faser og ikke ét script

Kopieres Fusion-filerne ind før SDK'en er importeret, kan projektet ikke kompilere, og Unitys
`-executeMethod` fejler før den når at konfigurere noget. Core-laget har derimod **ingen**
Unity- eller Fusion-referencer (det var hele pointen med at holde spillogikken ren, jf. docs/33),
så det kan kompilere og bevises i Fase 1 uden nogen ekstern afhængighed.
