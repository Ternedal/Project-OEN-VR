# Compatibility matrix

Udfyldes med **faktiske** on-device-resultater, ikke forventninger. Tom celle = ikke testet endnu.

**Quest 1 indgår ikke:** OpenXR-runtimen kan ikke initialisere på v50 (`DROP_Q1_RUNTIME`, M0a 2026-08-08).
Evidens: `prototype/m0a-openxr-smoke/RESULTAT.md`.

## Enheder i lanen

| Egenskab | Quest 2 | Quest 3 / 3S |
|---|---|---|
| Rolle | Autoritativ baseline og performancegulv | Enhanced parity |
| Serial (testenhed) | `1WMHH818L30444` | |
| OS-version | | |
| Graphics API | Vulkan (bekræftet M0a) | |
| Editor | Unity 6000.4.10f1 | Unity 6000.4.10f1 |

## Pakkematrix

| Pakke | Version | Q2 | Q3 |
|---|---|---|---|
| com.unity.xr.openxr | 1.14.3 | Bekræftet M0a | |
| com.unity.xr.management | 4.5.0 | Bekræftet M0a | |
| com.unity.xr.interaction.toolkit | 3.0.8 | | |
| com.unity.inputsystem | 1.11.2 | Bekræftet M0a | |
| Photon Fusion | 2.0.12 | Bekræftet M0b | |

## Protokol og indhold

| Felt | Værdi | Q2 | Q3 |
|---|---|---|---|
| Network protocol version | | | |
| Content hash | | | |
| Save schema version | | | |

## Resultater

| # | Test | Q2 | Q3 | Q2↔Q3 | Noter |
|---|---|---|---|---|---|
| 1 | App starter immersivt | OK (M0a) | | — | 71,8 fps, Vulkan |
| 2 | Head-tracking ikke-nul | OK (M0b) | | — | Via `InputDevices`; se `src/unity/RUNBOOK_FUSION.md` §8 |
| 3 | Photon Shared-session forbinder | OK (M0b) | | | |
| 4 | Rig spawner m. input authority | OK (M0b) | | | |
| 5 | Head/hands replikeres mellem klienter | | | | **Afventer to headset** |
| 6 | Handshake afviser version-mismatch | | | | **Afventer to headset** |
| 7 | Kasse: greb → solver flytter | OK (M0b) | | | Simuleret greb; `quality` 1,00 |
| 8 | 10× løftetest identisk slutposition (PO-025) | | | | **Afventer to headset** |
| 9 | 72 Hz i minimal netværksscene | | | | **Afventer måling** |
