# Unity project settings checklist

Endelige værdier låses efter M0.

- [ ] Android Build Support + SDK/NDK/OpenJDK installeret gennem Unity Hub.
- [ ] IL2CPP / ARM64.
- [ ] OpenXR loader for Android.
- [ ] Oculus Touch interaction profile.
- [ ] Input System active.
- [ ] URP mobile renderer.
- [ ] Linear color space, hvis fysisk device-test er stabil.
- [ ] Vulkan (eneste graphics API - GLES3-fallback droppet, ADR-018).
- [ ] Multithreaded rendering testet.
- [ ] Texture compression ASTC.
- [ ] Managed stripping sat og smoke-testet.
- [ ] Internet permission for Photon.
- [ ] Microphone permission kun hvis voice senere aktiveres.
- [ ] Product/package IDs separate for dev/alpha.
- [ ] Quest supportedDevices manifest håndteres pr. buildprofile.
- [ ] 72 Hz requested som default.
- [ ] Development logging strip i release.
- [ ] Keystore og secrets uden for repo.
