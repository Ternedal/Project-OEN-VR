# M0a — resultat

Udfyldes af Anders efter test. Dette dokument er evidensen bag CR-002, ADR-019 og hele Quest 1-beslutningen. Skriv hvad der faktisk skete — ikke hvad der burde ske.

## Opsætning

| Felt | Værdi |
|---|---|
| Dato | |
| Unity-version | |
| `com.unity.xr.openxr` version | |
| `com.unity.xr.interaction.toolkit` version | |
| Graphics API brugt | Vulkan / GLES3 |
| Quest 1 OS-version (`adb shell getprop ro.build.version.release`) | |

## Resultater

| | Quest 2 | Quest 1 | Quest 3 (valgfri) |
|---|---|---|---|
| APK installerer | ja / nej | ja / nej | ja / nej |
| Appen starter | ja / nej | ja / nej | ja / nej |
| Starter **immersivt** (ikke fladt panel) | ja / nej | ja / nej | ja / nej |
| Hovedtracking (grå kube står stille) | ja / nej | ja / nej | ja / nej |
| Venstre controller tracker | ja / nej | ja / nej | ja / nej |
| Højre controller tracker | ja / nej | ja / nej | ja / nej |
| FPS fra HUD | | | |
| Vulkan virkede | ja / nej | ja / nej | ja / nej |
| GLES3-fallback nødvendig | ja / nej | ja / nej | ja / nej |

Fejlede noget på Quest 2, er det opsætningen — ret det, før Quest 1-resultatet tælles.

## Logcat

Vedhæft eller indsæt de relevante linjer. Særligt interessant ved fejl: alt med `XR_ERROR`, `openxr`, `loader`, `AndroidRuntime`.

```
```

## Beslutning

Sæt ét kryds.

- [ ] **`GO`** — Quest 1 starter og tracker på OpenXR. Q1 er en buildprofil. Editor låses til den testede Unity 6-version, og M0b fortsætter som planlagt.
- [ ] **`REDESIGN`** — Q1 virker kun med ændringer, der påvirker Q2/Q3 (fx tvungen GLES3 på alle profiler). Beskriv hvad, og hvad det koster.
- [ ] **`DROP_Q1_RUNTIME`** — Q1 starter ikke eller tracker ikke på OpenXR. Exit-kriteriet i `docs/14` udløses.

### Begrundelse

_(2-5 linjer. Hvad så du helt konkret?)_

## Konsekvens efter beslutning

**Ved `GO`:** lås `ProjectVersion.txt`, `manifest.json` og `packages-lock.json`. Udfyld `config/COMPATIBILITY_MATRIX.md`. Sæt ADR-006, ADR-018 og ADR-019 til `Accepted` via response matrix. Fortsæt M0b (PO-025).

**Ved `DROP_Q1_RUNTIME`:** opdatér ADR-004 og ADR-019. Fjern `Q1_LEGACY` fra aktive buildprofiler i `docs/08` og arkivér den som frossen demo-plan. Justér de berørte items og estimater i `docs/17`. Fjern Q1 fra testmatricen i `docs/13` og fra COMPAT-001. Meld den frigjorte tid.

Ingen af de to udfald er et nederlag. `DROP_Q1_RUNTIME` er en forberedt beslutning, der fjerner projektets dyreste valgfrie del — og den træffes på evidens i stedet for optimisme.
