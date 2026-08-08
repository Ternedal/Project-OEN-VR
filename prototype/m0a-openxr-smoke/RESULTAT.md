# M0a — resultat

Udfyldt 2026-08-08 (kørt headless + on-device af Claude/Cowork på Anders' maskine). Dette dokument er evidensen bag CR-002, ADR-019 og hele Quest 1-beslutningen.

## Opsætning

| Felt | Værdi |
|---|---|
| Dato | 2026-08-08 |
| Unity-version | 6000.4.10f1 |
| `com.unity.xr.openxr` version | 1.14.3 |
| `com.unity.xr.interaction.toolkit` version | ikke medtaget (M0a bevidst uden XRI) |
| Graphics API brugt | Vulkan (aktiv på Quest 2, bekræftet i HUD) |
| Quest 1 OS-version | v50 (sidste udgivelse; `ro.build.version.release` ikke queried denne kørsel) |

## Resultater

| | Quest 2 | Quest 1 | Quest 3 (valgfri) |
|---|---|---|---|
| APK installerer | **ja** | **ja** | ikke testet |
| Appen starter | **ja** | **NEJ — crash ved start** | – |
| Starter **immersivt** (ikke fladt panel) | **ja** | nej (crasher før første frame) | – |
| Hovedtracking (grå kube står stille) | **ja** | nej | – |
| Venstre controller tracker | ikke bekræftet (controllere i dvale under capture, `valid=False`) | nej | – |
| Højre controller tracker | ikke bekræftet (som ovenfor) | nej | – |
| FPS fra HUD | **71,8** | – | – |
| Vulkan virkede | **ja** | – (crash før render) | – |
| GLES3-fallback nødvendig | nej | ukendt (crash før graphics-init nås) | – |

Quest 2 er grøn hele vejen: samme APK, samme opsætning. Fejlen er derfor isoleret til Quest 1's runtime, ikke til opsætningen.

## Logcat

**Quest 2 (virker) — HUD-telemetri, tag `OenM0a`:**

```
[OenM0a] PROJECT OEN - M0a | device: Oculus Quest 2 | gfx: Vulkan | unity: 6000.4.10f1
         fps: 71,8 | head: valid=True tracked=True pos=(-0.48, 0.84, 0.52)
         left: valid=False tracked=False | right: valid=False tracked=False
```

**Quest 1 (crash) — native abort i OpenXR-loaderen ved app-start (to identiske forsøg):**

```
--------- beginning of crash
F libc  : Fatal signal 6 (SIGABRT), code -1 (SI_QUEUE) in tid 4742 (Unity Main Thre), pid 4716 (ectoen.m0asmoke)
F DEBUG : signal 6 (SIGABRT), code -1 (SI_QUEUE)  >>> com.projectoen.m0asmoke <<<
    #07-#10  lib/arm64/libopenxr_loader.so
    #11-#14  lib/arm64/libUnityOpenXR.so
    #15-#20  lib/arm64/libunity.so
    #21      lib/arm64/libgame.so  Unity::UnityApplication::OnApplicationCommand(android_app*, int)+852
    #23      lib/arm64/libgame.so  Unity::UnityApplication::Loop()+240
    #25      lib/arm64/libgame.so  android_main+116
Tombstone written to: /storage/emulated/0/Android/data/com.projectoen.m0asmoke/files/tombstone_00
Zygote: Process 4716 exited due to signal 6 (Aborted)
```

Fortolkning: appen starter, Unity initialiserer XR, og **OpenXR-loaderen (`libopenxr_loader.so`) aborterer (SIGABRT)** kaldt fra Unitys `libUnityOpenXR.so` under opstart — før første frame. Det er ikke et manifest-/fladt-panel-problem (aktiviteten starter) og ikke et Vulkan-problem (crash sker før graphics-init). Den mest understøttede konklusion: Unitys OpenXR-provider (loader 1.14.3) kan ikke initialisere mod Quest 1's frosne v50 OpenXR-runtime. Den byte-præcise abort-årsag ligger i tombstonen på enheden, hvis der senere ønskes dybere analyse.

## Beslutning

- [ ] **`GO`**
- [ ] **`REDESIGN`**
- [x] **`DROP_Q1_RUNTIME`** — Q1 starter ikke på OpenXR. Exit-kriteriet i `docs/14` udløses.

### Begrundelse

Samme OpenXR-APK kører fejlfrit på Quest 2 (immersivt, hovedtracking `valid=True tracked=True`, 72 fps, Vulkan), men crasher deterministisk på Quest 1 med en native SIGABRT inde i `libopenxr_loader.so` under XR-opstart. Det er præcis det udfald ADR-019 og `docs/30` beskrev som "starter ikke → et andet XR-backend". Quest 1 kan ikke bære Unitys OpenXR-provider.

## Konsekvens efter beslutning (`DROP_Q1_RUNTIME`)

Opdatér ADR-004 og ADR-019. Fjern `Q1_LEGACY` fra aktive buildprofiler i `docs/08` og arkivér som frossen demo-plan. Justér berørte items/estimater i `docs/17`. Fjern Q1 fra testmatricen i `docs/13` og fra COMPAT-001. Meld den frigjorte tid. Hovedprojektet bygges på Unity 6 LTS + OpenXR for Quest 2 (performancegulv) og Quest 3/3S (enhanced parity).

Dette er en forberedt beslutning truffet på evidens — den fjerner projektets dyreste valgfrie del (en separat Quest 1 XR-lane) før der bygges gameplay ovenpå antagelsen.
