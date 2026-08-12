# M0b — bootstrap af det rigtige Projekt Øen Unity-projekt

M0a er afgjort (Quest 2 kører OpenXR; Quest 1 = DROP_Q1_RUNTIME). M0b bygger selve
produktprojektet: Unity-projekt, låste pakker, Core-laget i Unity, production art og Photon-netværk.

Bootstrappen er delt i to faser, fordi **Photon Fusion 2 ikke ligger i Unity-registret** —
den kræver din konto. Fase 1 er Photon-uafhængig og kan køres nu.

---

## Fase 1 — projekt + pakker + Core + XR + production art

Én kommando (samme mønster som M0a, bygget på det der virkede):

```powershell
cd C:\Users\admin\Desktop\Project-OEN-VR\prototype\m0b-bootstrap
.\Bootstrap-M0b.ps1 -UnityPath "C:\Program Files\Unity\Hub\Editor\6000.4.10f1\Editor\Unity.exe"
```

Den opretter `ProjektOenApp` ved siden af repoet, skriver pakke-manifestet (ASCII, ingen
BOM), kopierer **hele Core-laget** ind som `Assets/ProjectOen/Core` med en asmdef og
konfigurerer OpenXR + Meta Quest + Oculus Touch via `M0bConfigure.cs`.

Production-art-passet installerer desuden `Assets/ProjectOEN/ProductionArt`, bygger de
genererede OBJ-filer til Unity-prefabs med de raffinerede materialer, genererer den separate
`StormnattenArtShowcase.unity`, tilføjer den begrænsede lokale stormregn og kører den
Unity-side Quest 2-budgetaudit.

**Vigtigt:** showcase-scenen er kun visual review. Den føjes ikke til Android build settings.
`CoopGame.unity` forbliver den minimale 72 Hz/netværksgate.

**Accept efter Fase 1:** Unity åbner projektet uden compile-fejl, `[M0B-SETUP]`-loggen viser
`Configure: færdig`, `ProjectOen.Core` kompilerer som Unity-assembly, production-art-prefabs
kan bygges, og `[ProjectOEN.Art.Budget] PASS` står i `production-art-budget.log`.

Den sidste linje betyder kun, at den importerede showcase holder sig under repoets hårde
scene-budgetter. Den erstatter ikke profiling i Quest 2-headsettet.

---

## Hurtig art-iteration — uden at køre hele M0b igen

Når Fase 1 allerede er kørt én gang, bruges denne til resten af art-arbejdet:

```powershell
cd C:\Users\admin\Desktop\Project-OEN-VR\prototype\m0b-bootstrap
.\Review-ProductionArt.ps1 `
  -UnityPath "C:\Program Files\Unity\Hub\Editor\6000.4.10f1\Editor\Unity.exe" `
  -OpenEditor
```

`Review-ProductionArt.ps1` gør kun dette:

1. synkroniserer den aktuelle `ProductionArt`-pakke og art-editor-scripts til `ProjektOenApp`;
2. genbygger production-art-prefabs;
3. genbygger `StormnattenArtShowcase.unity`;
4. tilføjer den lokale stormregn;
5. kører Quest 2-budgetauditen;
6. åbner Unity direkte på showcase-scenen, når `-OpenEditor` er angivet.

Den rører **ikke** `Packages/`, XR-konfiguration, Photon/Fusion, `CoopGame.unity` eller M0b APK-buildet.
Hvis budgetauditen fejler, åbnes editor-reviewet ikke som en falsk grøn levering.

Budgetauditen bruger følgende hårde scenegrænser:

- triangles: >750k = fail (mål ≤500k);
- renderer-material-slots som konservativ draw-call-proxy: >130 = fail (mål ≤100);
- realtime shadow-casters: >1 = fail;
- aktive particle systems: >10 = fail.

---

## Photon-trin (kun dig)

1. Opret konto på **dashboard.photonengine.com**.
2. Ny app → type **Fusion** → navn "Projekt Oen" → **Create**. Kopiér **App ID**.
3. Hent **Photon Fusion 2 SDK** og importér `.unitypackage` i `ProjektOenApp`.
4. Fusion Hub → indsæt **App ID** under Fusion.
5. Kør Fase 2.

Konto og Photons vilkår skal være dine; de kan ikke automatiseres her.

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

De fire Fusion-filer bærer eksplicitte API-antagelser i deres header (`NetworkBehaviour`,
`[Networked]`, `StartGameArgs`, `NetworkArray`, RPC-attributter). Den installerede SDK er
sandheden; en compile-fejl her skal rettes mod den faktiske Fusion 2-version, ikke gættes væk.

**Accept efter Fase 2 (M0b-gaten):** privat session mellem to klienter, compatibility handshake
afviser mismatch før spawn, head/hands replikeres, `CoopObjectController` holder den tunge kasse
identisk på begge klienter (10× løftetest Q2↔Q3), og den minimale scene holder 72 Hz.

---

## Hvorfor visual review og M0b-gate er adskilt

M0b skal bevise XR/netværk/performance med mindst mulig støj. Stormnatten-showcasen skal bevise,
at production-art-pakken hænger visuelt sammen. Hvis de to scener blandes, bliver et performance-
problem umuligt at skelne fra et art-problem, og art-polish kan utilsigtet flytte platformsgaten.
Derfor har de to flows forskellige scener, scripts og acceptkriterier.
