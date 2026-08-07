# Kilderegister

**Senest genvalideret:** 2026-08-05. Kilder skal genvalideres før package upgrades eller offentlig release. Editor- og packageversioner er kandidater, indtil M0 er bestået fysisk.

| Område | Kilde | URL | Relevans |
|---|---|---|---|
| Quest 1 | Meta: Navigating Changes to Quest 1 | https://developers.meta.com/horizon/blog/managing-meta-quest-1-guidance-developers/ | Platform SDK v51+ starter ikke på Quest 1; multiplayer-versionvejledning |
| Oculus XR | Unity Oculus XR Plugin changelog 4.3 | https://docs.unity3d.com/Packages/com.unity.xr.oculus@4.3/changelog/CHANGELOG.html | v4/v51 fjernede Quest 1 target |
| Quest 1 Unity | Unity XR packages | https://docs.unity3d.com/6000.1/Documentation/Manual/xr-support-packages.html | Dokumenterer sidste kompatible Oculus provider v3.3.0 |
| Unity editor | Unity 2022.3.76f1 | https://unity.com/releases/editor/whats-new/2022.3.76f1 | Patch pr. 2026-05-06. **Bemærk:** ligger i det tredje LTS-år, som Unity forbeholder Enterprise/Industry |
| Unity LTS-politik | Unity Manual: New in Unity 2022 LTS | https://docs.unity3d.com/2022.3/Documentation/Manual/WhatsNew2022LTS.html | To års LTS-support for Personal og Pro; tre år for Enterprise og Industry |
| Unity XR-support | Unity Manual: XR packages | https://docs.unity3d.com/6000.0/Documentation/Manual/xr-support-packages.html | Understøttet udvikling for Quest 2/3/3S/Pro. Oculus-provider v4+ understøtter ikke Quest 1 |
| Oculus-provider | Oculus XR Plugin changelog 4.4 | https://docs.unity3d.com/Packages/com.unity.xr.oculus@4.4/changelog/CHANGELOG.html | Quest 1 fjernet som target device; v51-plugins understøtter ikke Quest 1; min. Unity hævet til 2022.3 |
| Provider-deprecation | Meta: XR Plugin Management for Meta Quest | https://developers.meta.com/horizon/documentation/unity/unity-xr-plugin/ | Oculus XR Plugin er deprecated og planlagt fjernet; OpenXR er anbefalet |
| Photon pricing | Photon pricing | https://doc.photonengine.com/photon/current/pricing | 100 CCU gratis til udvikling og kommerciel brug, én app |
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
