# M0: Bevis fælles Quest 2/3 platform- og netværkslane

> Revideret 2026-08-06 efter Claude-review v1.0 (CR-001, CR-002). Tidligere udgave lagde netværksbeviset i M0's gate, men opgaverne i M2.

## Formål

Reducer den største tekniske risiko, før gameplay- og contentproduktion begynder.

## M0a — AFGJORT 2026-08-08: `DROP_Q1_RUNTIME`

Eksperimentet er kørt. Quest 2 kører samme OpenXR-APK immersivt (71,8 fps, Vulkan, head-tracking valid).
Quest 1 crasher deterministisk med native SIGABRT i `libopenxr_loader.so` under XR-opstart, før første
frame (to identiske forsøg, tombstone).

Konklusion: Unitys OpenXR-provider kan ikke initialisere mod Quest 1's frosne v50-runtime. Exit-kriteriet
i `docs/14` er udløst. Quest 1 er frossen sideload-demo, ikke en lane.
Evidens: `prototype/m0a-openxr-smoke/RESULTAT.md`.

Vulkan/GLES3-spiket (OQ-003) er droppet sammen med lanen — Vulkan er bekræftet på Quest 2 (ADR-018 resolved).

### Baggrund (før beslutningen)

- Unitys manual angiver understøttet udvikling for Quest 2, 3, 3S og Quest Pro. Quest 1 står ikke på listen.
- Oculus-provider v4+ har fjernet Quest 1 som target device; v51-plugins understøtter ikke Quest 1.
- Metas egen Unity-dokumentation angiver Oculus XR Plugin som deprecated og planlagt fjernet, med Unity OpenXR Plugin som anbefalet erstatning.
- Quest 1's sidste OS-udgivelse var v50 (feb. 2023), og sikkerhedsopdateringer sluttede aug. 2024. Sideload er derimod ikke blokeret — sideload-only-planen er farbar.
- Spørgsmålet blev afgjort på enheden 2026-08-08. Svaret er negativt.

## M0b — deliverables

- Unity project + pinned package candidates. **Editoren låses her, ikke før.**
- Q2/Q3 build profiles.
- XR tracking/grab.
- Photon create/join med privat join code (PO-017, PO-018).
- Compatibility handshake (PO-019).
- Head/hands replication (PO-020).
- Heavy shared box proof — `CoopObjectController` (PO-022).
- 10× cross-device løftetest (PO-025).
- Compatibility matrix.

## Definition of done

- Minimal build starter fysisk på Quest 2 og Quest 3. (Quest 1 udgået: `DROP_Q1_RUNTIME` meldt med evidens 2026-08-08.)
- Q2↔Q3 kan forbinde i privat Photon-session.
- Head/hands replikeres stabilt.
- Begge spillere kan løfte og snap'e samme kinematic coop-objekt 10/10 gange.
- Quest 2 og minimal Q3-scene holder 72 Hz.
- Package-, graphics API-, manifest- og protocolmatrix dokumenteres.
- M0a-resultatet er meldt: `DROP_Q1_RUNTIME` (2026-08-08). M0b afsluttes med eksplicit `GO` eller `REDESIGN`.

## Estimat

142-180 timer (backlogsum 158 t over 17 items efter at PO-004 og PO-007 er droppet, jf. DROP_Q1_RUNTIME). Stop/go afgøres ved afslutningen af M0 — ikke ved et timeloft.

## Ikke i scope

- Stormnatten-content.
- Art pass.
- Personalisering.
- Meta Platform SDK-integration.
- Ready-flow, reconnect-hardening og failure injection — det er M2.
