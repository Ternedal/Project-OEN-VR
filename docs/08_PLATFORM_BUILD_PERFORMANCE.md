# Platform-, build- og performance-specifikation

## 1. Platformpolitik

### Quest 2 - baseline

Quest 2 bestemmer:

- scene complexity,
- interaktionsmængde,
- gameplayparitet,
- minimum framerate,
- memory discipline,
- QA-gates.

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

## 2. Provider- og SDK-realitet

- Unitys Oculus XR Plugin er deprecated og planlagt til fjernelse. Unity OpenXR Plugin er den anbefalede provider fremadrettet og kræver Unity 6 eller nyere.
- Unity 2022.3 LTS er ude af sit toårige standardsupportvindue (udløbet maj 2025).
- Projektet bruger Photon og undgår Meta Platform SDK i kerneflowet, jf. ADR-009.

Dette skal fysisk valideres. Dokumentation alene er ikke bevis for, at kombinationen kører stabilt på device. Se `docs/22_SOURCE_REGISTER.md` for kilder og verifikationsdato.

## 3. Buildprofiler

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

Budgetterne blev sat med Quest 1 som gulv. Efter ADR-019 er gulvet Quest 2, og tallene er derfor bevidst konservative. De justeres ikke på skrivebordet - kun på baggrund af device-profilering. Q-008 (præcis headset-model hos gavemodtageren) skal besvares, før budgettet låses.

## 6. Assetbudget

- Miljøteksturer typisk 512-1024; hero objects op til 2048 på modern profile.
- ASTC compression.
- Quest 2 bruger aggressive mipmaps.
- Maks. 2-3 materials pr. almindeligt prefab.
- Static batching/mesh combining hvor det giver mening.
- Vegetation som cards/low-poly clusters, ikke tusind separate GameObjects.
- LODs og occlusion/zone culling.
- Personlige billeder nedskaleres til fast maxdimension og valideres ved build.

## 7. Lighting

- Baked global lighting.
- Light probes ved bevægelige objekter.
- Én styliseret directional light; valgfri realtime shadow på Q2/3 efter profiling.
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
- GLES3-fallback er udgået med ADR-019; Vulkan er eneste lane.
- Single-pass instanced/multiview hvor understøttet.
- Foveated rendering kun via stabil, fælles API; aldrig som eneste vej til 72 Hz.

## 10. Build- og distributionsmatrix

| Kanal | Q2 | Q3 |
|---|---|---|
| Lokal development APK | Ja | Ja |
| Meta Alpha channel | Ja | Ja |
| Signeret gavebuild | Alpha/private | Alpha/private |
| Production store | Senere | Senere |

## 11. Performance gates

### M0

Engine-baseline-gaten i `docs/06` §3 er bestået, og tom netværksscene holder 72 Hz på Quest 2 og Quest 3.

### M2

Fælles kasseinteraktion holder 72 Hz og har acceptabel jitter.

### M4

Én komplet dagcyklus holder 72 Hz på Quest 2 og afsluttes uden memory growth.

### M5

Stormen køres 20 minutters soak på Quest 2. Quest 3 regression og enhancement testes separat.

### Release

- Ingen vedvarende dropped-frame perioder i kerneflow.
- Thermal throttling må ikke bryde 72 Hz på Quest 2 under én fuld mission.
- Peak memory og loading dokumenteret per buildprofil.
