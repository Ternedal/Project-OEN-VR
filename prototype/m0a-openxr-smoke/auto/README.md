# M0a automatiseret — to kommandoer

Manuel vej: `../RUNBOOK.md`. Brug den, hvis scripterne fejler — den er langsommere, men jeg ved hvad hvert trin gør.

**Ingen af filerne her er kørt.** Der er ingen Unity, intet Android SDK og ingen Quest i det miljø, de er skrevet i. De er skrevet til at fejle højlydt og på det rigtige trin, ikke til at fejle pænt.

## Kommandoerne

```powershell
cd prototype\m0a-openxr-smoke\auto

.\Build-M0a.ps1 -UnityPath "C:\Program Files\Unity\Hub\Editor\<version>\Editor\Unity.exe"
# opretter projekt, skriver pakkeliste, kopierer kildefiler, konfigurerer XR, bygger APK
# første kørsel: 5-15 min mens pakker importeres

.\Run-M0a.ps1 -Apk ..\..\..\..\OenM0aSmoke\Build\OenM0aSmoke.apk
# installerer, starter appen, optager logcat i 40 sek, aflæser og skriver et resultatdokument
```

Mellem de to: tag headsettet på, start appen fra **Ukendte kilder**, gå et skridt til siden, drej hovedet, bevæg hænderne.

## Hvad scripterne gør for dig

| Manuelt trin | Automatiseret |
|---|---|
| Opret projekt, vælg template | `-createProject` |
| Installér pakker via Package Manager | `manifest.json` skrives direkte |
| IL2CPP, ARM64, minSdk, Linear, Vulkan→GLES3 | `M0aBuild.ConfigurePlayer()` |
| XR Plug-in Management → OpenXR → features | `M0aBuild.ConfigureXR()` |
| Byg scene, tilføj XR Origin og HUD | `M0aBuild.CreateScene()` |
| File → Build | `BuildPipeline.BuildPlayer` |
| Læs HUD, fortolk, udfyld skema | `Run-M0a.ps1` parser logcat og skriver resultatet |

## Bevidste valg

**XR Interaction Toolkit er ikke med.** M0a skal svare på ét spørgsmål, og hver ekstra pakke er en variabel mere i fejlsøgningen. Kameraets pose drives af Input Systems `TrackedPoseDriver`, og HUD'en læser controllere via `UnityEngine.XR.InputDevices` — begge virker uden XRI. XRI kommer i M1.

**Oculus XR Plugin er ikke med.** Den er deprecated, og hele pointen med M0a er at afgøre, om Quest 1 kan undvære den. Er den installeret, tester du noget andet, end du tror.

**XR-features slås til ved navnematch, ikke ved typereference.** API'et har flyttet sig mellem Unity-versioner. Et navnematch der fejler giver en tydelig besked; en hård typereference ville give en compile-fejl og stoppe hele scriptet.

## Manifestet

`Build-M0a.ps1` skriver ikke et custom `AndroidManifest.xml`. Meta Quest Support-featuren i OpenXR-pakken tilføjer selv VR-kategori og headtracking-feature.

Starter appen som et **fladt panel** i Quest-hjemmet i stedet for immersivt, er featuren ikke slået til. Så patch manifestet i hånden efter `../files/ANDROIDMANIFEST_PATCH.md` — og meld det, for så virkede den automatiske XR-opsætning ikke.

## Når noget fejler

Send **de første fejllinjer**, ikke den sidste. De hænger typisk sammen, og den sidste er ofte bare følgefejlen.

- Build-fejl: `Build-M0a.ps1` printer `[M0A-SETUP]`-linjerne og de første 15 `error CS`. Fuld log i `m0a-build.log`.
- Ingen enhed: er headsettet tændt, tilsluttet, og har du godkendt USB-debugging **inde i headsettet**?
- Pakkeversioner: versionsnumrene i scriptet er bedste gæt. Klager Unity, så fjern versionsstrengen fra `manifest.json` og lad Package Manager vælge.
