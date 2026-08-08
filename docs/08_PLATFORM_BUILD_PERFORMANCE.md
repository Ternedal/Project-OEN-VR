# Platform-, build- og performance-specifikation

## 1. Platformpolitik

### Quest 2 - baseline og performancegulv

Quest 2 udgik af salg ultimo 2024. Meta leverer feature-opdateringer til december 2026 og kritiske bug-/sikkerhedsopdateringer til december 2027. Den er derfor et gyldigt og bevidst konservativt performancegulv for gaveversionen — men den er ikke fremtidens målenhed. Quest 3S er antaget baseline for alt efter v1.0.

Quest 2 bestemmer:

- scene complexity,
- interaktionsmængde,
- gameplayparitet,
- minimum framerate,
- memory discipline,
- QA-gates.

### Quest 1 - legacy-test

Quest 1 skal kunne:

- starte en signeret sideload-build,
- tracke Touch-controllere,
- forbinde via Photon,
- gennemføre Stormnatten,
- bruge samme network protocol, scenario data og save schema.

Quest 1 må bruge:

- lavere render scale,
- enklere skygger,
- færre partikler,
- færre audio voices,
- lavere texture mips,
- mere aggressiv scene unloading,
- reducerede post effects.

Quest 1 er ikke offentlig supportgaranti og må ikke kræve moderne Meta Platform SDK.

### Quest 3/3S - enhanced

Quest 3 må forbedre:

- render scale,
- shadows,
- texture mip bias,
- vegetation density,
- particles,
- material quality,
- optional 90 Hz mode efter 72 Hz er stabilt.

Ingen Quest 3-only gameplaymekanik i gaveversionen.

## 2. SDK-realitet for Quest 1

- Meta oplyser, at apps med Platform SDK v51+ ikke kan starte på Quest 1.
- Unitys Oculus XR Plugin v4+ fjernede Quest 1 som target; Unity dokumenterer v3.3.0 som sidste kompatible Oculus-provider.
- Cross-device multiplayer via Meta Platform services kan begrænses af SDK-version. Metas vejledning er eksplicit: en app på Quest 1 med v50 kan ikke spille multiplayer med en app på Quest 2 med v51. Projektet bruger derfor Photon og undgår Platform SDK i kerneflowet. Den beslutning (ADR-009) er korrekt og bekræftet.
- Unitys manual angiver understøttet udvikling for Quest 2, 3, 3S og Quest Pro. Quest 1 står ikke på listen, og Oculus-provider v4+ har fjernet Quest 1 som target device.
- **Metas egen Unity-dokumentation angiver Oculus XR Plugin som deprecated og planlagt til fjernelse**, med Unity OpenXR Plugin som anbefalet erstatning. En Quest 1-lane bygget på Oculus-provider v3.x er derfor en lane på en pakke, der er på vej ud — ikke bare en ældre version.

Dette skal fysisk valideres. Dokumentationen alene er ikke bevis for, at en bestemt moderne OpenXR-pakke fungerer på alle tre headset.

## 3. Buildprofiler

### `Q1_LEGACY` — ARKIVERET 2026-08-08 (`DROP_Q1_RUNTIME`)

> **Ikke en aktiv buildprofil.** M0a viste, at Unitys OpenXR-provider crasher på Quest 1's v50-runtime (native SIGABRT i `libopenxr_loader.so`, jf. `prototype/m0a-openxr-smoke/RESULTAT.md`). Q1 bevares udelukkende som en **frossen sideload-only demo-plan** — der bygges ingen Quest 1-lane i hovedprojektet. Aktive profiler er `Q2_BASE` og `Q3_ENHANCED`.

Historisk profiludkast (arkiveret):

- Target: Quest 1. 72 Hz. Conservative render scale. No dynamic shadows. Low particles/vegetation/audio. Sideload-only.

### `Q2_BASE`

- Target: Quest 2.
- 72 Hz hard gate.
- URP mobile profile.
- Baked lighting + meget begrænsede realtime lights.
- Standard assets.
- Alpha/private release channel.

### `Q3_ENHANCED`

- Target: Quest 3/3S.
- 72 Hz default; 90 Hz optional quality mode.
- Højere render scale og LOD bias.
- Bedre shadows/particles, men identisk logic/network.

## 4. Package lock strategy

Efter M0 committes:

- `ProjectVersion.txt`.
- `Packages/manifest.json`.
- `Packages/packages-lock.json`.
- `config/COMPATIBILITY_MATRIX.md` med fysisk testresultat.

Pakkeopgraderinger efter M1 kræver separat branch og fuld device smoke test. Ingen automatiske “latest package”-opgraderinger.

## 5. Quest 2 performancebudget

Officiel minimumsrate for interaktive Meta Quest-apps er 72 FPS, svarende til ca. 13,9 ms framebudget.

Interne startbudgetter:

| Område | Quest 2 budget |
|---|---:|
| CPU main thread | < 8 ms typisk, < 11 ms worst-case |
| GPU | < 11 ms typisk |
| Draw calls | mål <100, hard warning >130 |
| Triangles/frame | mål <500k, warning >750k |
| Realtime lights | 0-1 med shadows |
| Visible skinned meshes | minimér; simple avatarer |
| Particle systems | <10 aktive, device-profiled |
| Audio voices | mål <24 samtidige |

Budgetter er startpunkter; OVR Metrics/Meta tools og Unity Profiler på device er autoritative.

## 6. Assetbudget

- Miljøteksturer typisk 512-1024; hero objects op til 2048 på modern profile.
- ASTC compression.
- Quest 1/2 bruger aggressive mipmaps.
- Maks. 2-3 materials pr. almindeligt prefab.
- Static batching/mesh combining hvor det giver mening.
- Vegetation som cards/low-poly clusters, ikke tusind separate GameObjects.
- LODs og occlusion/zone culling.
- Personlige billeder nedskaleres til fast maxdimension og valideres ved build.

## 7. Lighting

- Baked global lighting.
- Light probes ved bevægelige objekter.
- Én styliseret directional light uden realtime shadow på Q1, valgfri shadow på Q2/3 efter profiling.
- Stormeffekt skabes primært med skybox, fog, audio, material animation og lokale overlays.

## 8. Memory og loading

- Camp + én action-zone resident.
- Unload unused assets ved sikre faseovergange, ikke midt i kritisk interaktion.
- Audio streaming for længere spor.
- Pooling for particles og event props.
- Ingen store runtime-generated textures.
- Memory watermark logges per fase.

## 9. Render/API spike

M0 sammenligner:

- Vulkan + OpenXR.
- GLES3 fallback kun hvis Q1 viser blocker.
- Single-pass instanced/multiview hvor understøttet.
- Foveated rendering kun via stabil, fælles API; aldrig som eneste vej til 72 Hz.

## 10. Build- og distributionsmatrix

| Kanal | Q1 | Q2 | Q3 |
|---|---|---|---|
| Lokal development APK | Ja | Ja | Ja |
| Meta Alpha channel | Ikke primær plan | Ja | Ja |
| Signeret gavebuild | Sideload APK | Alpha/private | Alpha/private |
| Production store | Nej | Senere | Senere |

## 11. Performance gates

### M0

Tom netværksscene holder 72 Hz på alle enheder.

### M2

Fælles kasseinteraktion holder 72 Hz og har acceptabel jitter.

### M4

Én komplet dagcyklus holder 72 Hz på Quest 2 og afsluttes uden memory growth.

### M5

Stormen køres 20 minutters soak på Quest 2. Quest 1 gennemfører reduceret storm. Quest 3 regression og enhancement testes separat.

### Release

- Ingen vedvarende dropped-frame perioder i kerneflow.
- Thermal throttling må ikke bryde 72 Hz på Quest 2 under én fuld mission.
- Peak memory og loading dokumenteret per buildprofil.
