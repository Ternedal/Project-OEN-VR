# M0a — OpenXR smoke test på Quest 1

**Ét spørgsmål skal besvares: starter og tracker Unitys OpenXR-provider på Quest 1?**

Alt andet i projektet venter på svaret. Hvis ja, er Quest 1 en buildprofil, og planen holder. Hvis nej, udløses exit-kriteriet i `docs/14`, og Q1 bliver en frossen demo.

Regn med 2-4 timer inkl. installation af Android-værktøjer.

---

## 0. Før du starter

- Quest 1 med **developer mode** slået til (Meta Horizon-app → Enheder → Udviklertilstand). Kræver en verificeret udviklerorganisation på kontoen.
- USB-kabel og `adb` (følger med Unitys Android Build Support, ligger typisk i `%LOCALAPPDATA%\Unity\Hub\Editor\<version>\Editor\Data\PlaybackEngines\AndroidPlayer\SDK\platform-tools`).
- Quest 2 til sammenligning. **Byg og installér altid på Quest 2 først** — så ved du, om en fejl skyldes Quest 1 eller din opsætning.

## 1. Unity-projekt

1. Unity Hub → Installs → installér **nyeste Unity 6 LTS** (6000.0.x eller 6000.3.x) med modulet **Android Build Support** inkl. **OpenJDK** og **Android SDK & NDK Tools**.
2. Nyt projekt, template **Universal 3D**. Navn: `OenM0aSmoke`. Placér det uden for repoet — dette er en engangsspike, ikke projektkoden.
3. Notér den præcise editorversion. Den skal ind i resultatskemaet.

## 2. Pakker

Window → Package Manager → Unity Registry:

- **OpenXR Plugin** (`com.unity.xr.openxr`)
- **XR Interaction Toolkit** (`com.unity.xr.interaction.toolkit`) — trækker Input System og XR Core Utils med
- **Input System** (`com.unity.inputsystem`) — bekræft at den er der

Når Unity spørger om at aktivere det nye Input System og genstarte: **ja**.

`files/PACKAGES.md` har den forventede liste til sammenligning.

## 3. XR-indstillinger

Edit → Project Settings:

1. **XR Plug-in Management** → fanen **Android** → sæt flueben i **OpenXR**.
2. **XR Plug-in Management → OpenXR** (Android):
   - Under **Interaction Profiles**: tilføj **Oculus Touch Controller Profile**.
   - Under **OpenXR Feature Groups**: aktivér **Meta Quest Support**.
3. **Player → Other Settings**:
   - Scripting Backend: **IL2CPP**
   - Target Architectures: **ARM64** (fjern ARMv7)
   - Graphics APIs: **Vulkan** øverst. Lad **OpenGLES3** blive stående som nummer to — det er hele pointen med fallback-testen.
   - Minimum API Level: **29**
   - Color Space: **Linear**
4. **Player → Publishing Settings** → sæt flueben i **Custom Main Manifest**. Unity genererer nu `Assets/Plugins/Android/AndroidManifest.xml`.

Resten af `config/UNITY_PROJECT_SETTINGS_CHECKLIST.md` er ikke nødvendig for M0a.

## 4. Manifest

Åbn den manifestfil Unity lige har genereret og patch den efter `files/ANDROIDMANIFEST_PATCH.md`.

**Erstat ikke filen med en færdigskrevet manifest.** Activity-klassen afhænger af Unity-versionen og Application Entry Point-indstillingen, og en forkert klasse giver en app, der ikke starter. Patch den Unity selv har lavet.

## 5. Scene

1. Ny scene. Slet **Main Camera**.
2. GameObject → XR → **XR Origin (VR)**.
3. Tom GameObject i scenen, navn `SmokeTest`. Læg `files/SmokeTestHud.cs` og `files/BuildInfo.cs` i `Assets/Scripts/` og sæt `SmokeTestHud` på `SmokeTest`.
4. Gem scenen som `Assets/Scenes/Smoke.unity` og læg den i File → Build Profiles → Scene List.

`SmokeTestHud` opretter selv HUD og referencekube ved kørsel — der er ingen manuel opsætning.

## 6. Byg og installér

File → Build Profiles → Android → **Build**. Gem som `OenM0aSmoke.apk`.

```powershell
adb devices                      # bekræft at headsettet er der og godkendt
adb install -r .\OenM0aSmoke.apk
adb logcat -s Unity:V OenM0a:V   # lad den køre mens du tager headsettet på
```

Appen ligger under **Ukendte kilder** i biblioteket.

`files/build_and_install.ps1` gør trin 6 i én kommando, hvis du foretrækker det.

## 7. Aflæs resultatet

Du kigger efter tre ting:

1. **Starter den i VR?** Ikke som et fladt panel i Quest-hjemmet, men som en immersiv scene.
2. **Tracker hovedet?** Den grå referencekube skal blive stående i rummet, når du bevæger dig. Følger den med hovedet, er der ingen positionel tracking.
3. **Tracker controllerne?** To farvede kuber skal følge dine hænder.

HUD'en viser devicemodel, FPS og trackingstatus. Den samme information logges hvert sekund under tagget `OenM0a`, så `adb logcat` fanger den, selv hvis HUD'en ikke renderer.

Kør på Quest 2 først, derefter Quest 1. **Gem logcat-output fra begge.**

## 8. Meld resultatet

Udfyld `RESULTAT.md` og meld `GO`, `REDESIGN` eller `DROP_Q1_RUNTIME`.

Vær ikke skuffet over `DROP_Q1_RUNTIME`. Det er et forberedt valg med en dokumenteret exit-plan — og det sparer projektet for den dyreste valgfrie del, der findes.

## Hvis det fejler på Quest 1

Notér hvilken af disse det er, før du prøver at fikse noget:

| Symptom | Sandsynlig årsag | Prøv |
|---|---|---|
| Installerer ikke | minSdk eller ARM64 | Verificér `adb install`-fejlteksten ordret |
| Installerer, starter ikke | OpenXR-runtime på v50 mangler en påkrævet extension | `adb logcat` fra app-start; søg efter `XR_ERROR`, `openxr`, `loader` |
| Starter fladt i Quest-hjemmet | VR-kategori mangler i manifest | Gennemgå trin 4 igen |
| Starter i VR, sort skærm | Vulkan | Flyt OpenGLES3 øverst i Graphics APIs, byg igen |
| Starter, men kuben følger hovedet | Ingen positionel tracking | Det er et **rigtigt** M0a-nej — noter det |

Fejler den på Quest 2, er det din opsætning, ikke Quest 1. Ret det først.
