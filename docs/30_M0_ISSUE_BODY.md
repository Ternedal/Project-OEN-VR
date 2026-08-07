# M0: Bevis fælles Quest 1/2/3 platform- og netværkslane

> Revideret 2026-08-06 efter Claude-review v1.0 (CR-001, CR-002). Tidligere udgave lagde netværksbeviset i M0's gate, men opgaverne i M2.

## Formål

Reducer den største tekniske risiko, før gameplay- og contentproduktion begynder.

## M0a — det afgørende eksperiment (kør først, alt andet venter)

**Byg en tom OpenXR-scene og installér den fysisk på Quest 1.**

Alt andet i M0 er billigere at udføre, når dette svar foreligger — og en del af det er spildt arbejde, hvis svaret er negativt.

| Udfald | Betydning | Handling |
|---|---|---|
| Starter og tracker | Quest 1 er en **buildprofil**. Én pakkelane, ét interaktionslag. | Fortsæt M0b som planlagt. Editor låses til Unity 6 LTS. |
| Starter ikke / tracker ikke | Quest 1 kræver Oculus-provider v3.x — et **andet XR-backend**, ikke en ældre version. Det betyder fork af interaktionslaget, og providerpakken er dokumenteret deprecated og planlagt fjernet. | Udløs exit-kriteriet i `docs/14` **med det samme**. Quest 1 bliver frossen demo. Hovedprojektet bygges på Unity 6 LTS. Meld `DROP_Q1_RUNTIME`. |

Vulkan/GLES3-spiket (OQ-003) køres **efter** dette, ikke før. Falder Q1-lanen, forsvinder halvdelen af spikets begrundelse.

### Dokumenteret baggrund

- Unitys manual angiver understøttet udvikling for Quest 2, 3, 3S og Quest Pro. Quest 1 står ikke på listen.
- Oculus-provider v4+ har fjernet Quest 1 som target device; v51-plugins understøtter ikke Quest 1.
- Metas egen Unity-dokumentation angiver Oculus XR Plugin som deprecated og planlagt fjernet, med Unity OpenXR Plugin som anbefalet erstatning.
- Quest 1's sidste OS-udgivelse var v50 (feb. 2023), og sikkerhedsopdateringer sluttede aug. 2024. Sideload er derimod ikke blokeret — sideload-only-planen er farbar.
- **Hvorvidt Unitys OpenXR-provider faktisk starter på Q1's frosne v50-runtime er ikke dokumenteret noget sted.** Det kan kun afgøres på enheden. Det er derfor eksperimentet.

## M0b — deliverables

- Unity project + pinned package candidates. **Editoren låses her, ikke før.**
- Q1/Q2/Q3 build profiles.
- XR tracking/grab.
- Photon create/join med privat join code (PO-017, PO-018).
- Compatibility handshake (PO-019).
- Head/hands replication (PO-020).
- Heavy shared box proof — `CoopObjectController` (PO-022).
- 10× cross-device løftetest (PO-025).
- Compatibility matrix.

## Definition of done

- Minimal build starter fysisk på Quest 1, Quest 2 og Quest 3 — eller `DROP_Q1_RUNTIME` er meldt med evidens.
- Q1↔Q2 og Q2↔Q3 kan forbinde i privat Photon-session.
- Head/hands replikeres stabilt.
- Begge spillere kan løfte og snap'e samme kinematic coop-objekt 10/10 gange.
- Quest 2 og minimal Q1/Q3-scene holder 72 Hz.
- Package-, graphics API-, manifest- og protocolmatrix dokumenteres.
- Resultatet er eksplicit `GO`, `REDESIGN` eller `DROP_Q1_RUNTIME`.

## Estimat

160-200 timer (backlogsum 176 t over 19 items). Stop/go afgøres ved afslutningen af M0 — ikke ved et timeloft.

## Ikke i scope

- Stormnatten-content.
- Art pass.
- Personalisering.
- Meta Platform SDK-integration.
- Ready-flow, reconnect-hardening og failure injection — det er M2.
