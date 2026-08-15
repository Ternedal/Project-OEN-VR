# M0b — bootstrap af det rigtige Projekt Øen Unity-projekt

M0a er afgjort (Quest 2 kører OpenXR; Quest 1 = DROP_Q1_RUNTIME). M0b bygger selve
produktprojektet: Unity-projekt, låste pakker, Core-laget i Unity, production art og Photon-netværk.

Bootstrappen er delt i to faser, fordi **Photon Fusion 2 ikke ligger i Unity-registret** —
den kræver din konto. Fase 1 er Photon-uafhængig og kan køres nu.

---

## Fase 1 — projekt + pakker + Core + XR + production art

Én kommando:

```powershell
cd C:\Users\admin\Desktop\Project-OEN-VR\prototype\m0b-bootstrap
.\Bootstrap-M0b.ps1 -UnityPath "C:\Program Files\Unity\Hub\Editor\6000.4.10f1\Editor\Unity.exe"
```

Den opretter `ProjektOenApp` ved siden af repoet, skriver pakke-manifestet, kopierer
**hele Core-laget** ind som `Assets/ProjectOen/Core` med asmdef og konfigurerer OpenXR +
Meta Quest + Oculus Touch via `M0bConfigure.cs`.

Production-art-passet installerer `Assets/ProductionArt`, bygger OBJ-filer til
Unity-prefabs med de raffinerede materialer, genererer `StormnattenArtShowcase.unity`,
tilføjer den begrænsede lokale stormregn og kører Unity-side Quest 2-budgetaudit.

**Vigtigt:** showcase-scenen er kun visual review. Den føjes ikke til Android build settings.
`CoopGame.unity` forbliver den minimale 72 Hz/netværksgate.

---

## Autoritativ on-machine art-verifikation

Når Fase 1 allerede er kørt, bruges den source-stemplede wrapper:

```powershell
cd C:\Users\admin\Desktop\Project-OEN-VR\prototype\m0b-bootstrap
.\Verify-ProductionArt.ps1 `
  -UnityPath "C:\Program Files\Unity\Hub\Editor\6000.4.10f1\Editor\Unity.exe" `
  -OpenEditor
```

`Verify-ProductionArt.ps1` gør først rapportens kilde entydig:

- kræver `git`;
- kræver en navngivet branch, ikke detached HEAD;
- læser den aktuelle 40-tegns commit-SHA;
- kræver clean worktree for production art, `src/unity/ProjectOen.Art` og review/verify-scripts;
- kører derefter `Review-ProductionArt.ps1 -OneShot`;
- source-stempler kun en Unity-rapport med `PASS` og `failed = 0`;
- skriver `sourceBranch`, `sourceSha`, `sourceWorktreeClean`, UTC-stempel og stamp-tool i JSON;
- læser JSON tilbage og verificerer branch/SHA/clean-flag før den accepteres.

Dermed kan en senere grøn rapport bindes til præcis den committed art-kilde, der blev kopieret
ind i Unity. Lokale verification-logs og den source-stemplede repo-rapport er `.gitignore`'et.

### One-shot Unity-kæden

`Review-ProductionArt.ps1 -OneShot` synkroniserer art + runtime/editor-scripts og starter
**én** Unity batchmode-proces. `ProductionArtBatchVerification.RunAll` kører 23 ordnede trin:

1. world prefabs;
2. state appearance + audit;
3. material calibration + audit;
4. state catalogs;
5. state-transition scene + reel `SetState`-audit;
6. hero-readability scene + audit;
7. decals;
8. VFX + VFX-scene/audit;
9. diegetic UI + UI-scene/audit;
10. Stormnatten showcase;
11. camp + signal-finale stormatmosfære;
12. storm motion FX + wind response;
13. imported Stormnatten Quest-2 audit;
14. slutkontrol af at alle seks review-scener findes og er ude af enabled build settings.

Unity kan kun nå `RunAll`, hvis de synkroniserede C#-filer er importeret og kompileret i den
installerede Unity-version. Efter hvert trin køres en synkron `AssetDatabase.Refresh`.

Rapporter:

- Unity-projekt: `ProjektOenApp\ProjectOEN-ArtVerification.json`;
- source-stemplet repo-handoff: `prototype\m0b-bootstrap\review-art-verification.json`;
- samlet Unity-log: `prototype\m0b-bootstrap\review-art-one-shot.log`.

Hvis Unity returnerer non-zero, rapporten mangler eller ikke siger `PASS`, stopper flowet.
Editor åbnes først efter en grøn, source-stemplet rapport.

---

## Debug fallback — én Unity-proces pr. trin

Hvis et konkret builder/audit-trin skal isoleres, bruges den etablerede debug fallback:

```powershell
cd C:\Users\admin\Desktop\Project-OEN-VR\prototype\m0b-bootstrap
.\Review-ProductionArt.ps1 `
  -UnityPath "C:\Program Files\Unity\Hub\Editor\6000.4.10f1\Editor\Unity.exe" `
  -OpenEditor
```

Fallbacken starter Unity separat for hvert build/audit-trin og skriver individuelle
`review-art-*.log` filer. Den er langsommere, men god til fejlisolering.

Begge review-modes rører **ikke** `Packages/`, XR-konfiguration, Photon/Fusion,
`CoopGame.unity` eller M0b APK-buildet.

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