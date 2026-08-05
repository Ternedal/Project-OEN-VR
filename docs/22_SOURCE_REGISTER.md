# Kilderegister

**Senest genvalideret:** 2026-08-05 (Unity-, provider- og Fusion-kilder verificeret i forbindelse med DP-001).

**Ikke verificeret og skal tjekkes ved M0-start:** præcis nyeste 6000.3.x-patchnummer, præcis nyeste XRI 3.x-minorversion, og Fusion 2.1's faktiske Shared Mode-jitter på Quest 2 (skal måles, ikke slås op). Kilder skal genvalideres før package upgrades eller offentlig release. Editor- og packageversioner er kandidater, indtil M0 er bestået fysisk.

| Område | Kilde | URL | Relevans |
|---|---|---|---|
| Unity LTS | Unity 2022 LTS release overview | https://unity.com/releases/2022-lts | To års standardsupport fra 2023-05-30; udløbet maj 2025. Verificeret 2026-08-05 |
| Unity LTS | Unity endoflife-oversigt | https://endoflife.date/unity | LTS udgives årligt, to års support; aktuelle spor 6000.0.x og 6000.3.x. Verificeret 2026-08-05 |
| Provider | Meta: Set up Unity for VR development | https://developers.meta.com/horizon/documentation/unity/unity-project-setup/ | Oculus XR Plugin er deprecated og planlagt til fjernelse; Unity OpenXR Plugin kræver Unity 6+ og Meta XR SDK v74+. Verificeret 2026-08-05 |
| Provider | Meta: XR Plugin Management for Meta Quest | https://developers.meta.com/horizon/documentation/unity/unity-xr-plugin/ | Oculus XR Plugin dækker Unity 2022+, men kun Meta XR SDK v73 eller ældre. Verificeret 2026-08-05 |
| Fusion | Photon Fusion 2 SDK requirements | https://doc.photonengine.com/fusion/current/getting-started/sdk-download | Understøtter Unity 2021.3.45, 2022.3.45, 6.0.x, 6.3.x; Asset Serialization skal være Force Text. Verificeret 2026-08-05 |
| Fusion | Photon Fusion 2.1 stable release | https://blog.photonengine.com/fusion-2-1-stable-release/ | Forecast Physics inkl. Shared Mode, konfigurerbar Shared Mode tickrate/send rate, forbedret Master Client-switching. Relevant for CR-004 og CR-005. Verificeret 2026-08-05 |
| Meta setup | Set up Unity for VR development | https://developers.meta.com/horizon/documentation/unity/unity-project-setup/ | Officiel Unity/Quest setup |
| OpenXR | Meta Unity and OpenXR compatibility | https://developers.meta.com/horizon/documentation/unity/unity-and-openxr-compatibility/ | OpenXR relation på Horizon OS |
| OpenXR Unity | Unity OpenXR package | https://docs.unity3d.com/Packages/com.unity.xr.openxr@latest/ | Package compatibility og features |
| XRI | XR Interaction Toolkit | https://docs.unity3d.com/Packages/com.unity.xr.interaction.toolkit@3.0/manual/index.html | Interaction og locomotion foundation |
| Performance | Meta testing and performance analysis | https://developers.meta.com/horizon/documentation/unity/unity-perf/ | 72 FPS minimum for interactive apps |
| Device budgets | Meta device optimization comparison | https://developers.meta.com/horizon/resources/device-optimization-comparison/ | Quest 2 vs Quest 3 memory/performance recommendations |
| Frame budget | Meta basic optimization workflow | https://developers.meta.com/horizon/documentation/unity/po-perf-opt-mobile/ | 72 FPS ≈ 13.9 ms |
| Release | Meta release channels | https://developers.meta.com/horizon/resources/publish-release-channels/ | Alpha/Beta/RC private distribution |
| Release invites | Add users to release channel | https://developers.meta.com/horizon/resources/publish-release-channels-add-users/ | Invite-only test distribution |
| Photon VR | Fusion VR Shared sample | https://doc.photonengine.com/arvr/current/technical-samples/fusion-vr-shared | Officiel Shared Mode VR sample |
| Photon input | Shared Mode Player Input | https://doc.photonengine.com/fusion/current/manual/input/shared-mode-input | Input/state authority model |
| Photon reliability | Reliability exceptions | https://doc.photonengine.com/fusion/current/concepts-and-patterns/reliability-exceptions | Shared Mode authority race/desync risks |
| Photon encryption | Fusion connection encryption | https://doc.photonengine.com/fusion/current/manual/advanced/encryption | Transport/encryption muligheder |
| Network config | Photon Fusion Network Project Config | https://doc.photonengine.com/fusion/v2/manual/network-project-config | Shared Mode tick/send rate, VR Latest State input og network condition simulation |
