# Forventede pakker efter trin 2

Sammenlign med `Packages/manifest.json` i spikeprojektet. Versionsnumre afhænger af din editorversion — **noter de faktiske i `RESULTAT.md`**, for det er dem, der bliver kandidater til package lock i M0b.

| Pakke | ID | Rolle |
|---|---|---|
| OpenXR Plugin | `com.unity.xr.openxr` | XR-runtime. **Testens omdrejningspunkt.** |
| XR Interaction Toolkit | `com.unity.xr.interaction.toolkit` | Leverer XR Origin (VR). Bruges for alvor i M1 |
| Input System | `com.unity.inputsystem` | Trækkes ind af XRI |
| XR Core Utilities | `com.unity.xr.core-utils` | Trækkes ind af XRI |
| Universal RP | `com.unity.render-pipelines.universal` | Følger med templaten |

**Oculus XR Plugin (`com.unity.xr.oculus`) må IKKE installeres.** Metas egen dokumentation angiver den som deprecated og planlagt fjernet. Hele pointen med M0a er at afgøre, om Quest 1 kan undvære den. Har du den i projektet, tester du noget andet, end du tror.

## Hvis Package Manager tilbyder flere versioner

Tag den, editoren markerer som anbefalet. Vi låser først versioner i M0b, og først når testen er bestået — jf. ADR-006, hvor editorvalget netop er gjort afhængigt af dette resultat.
