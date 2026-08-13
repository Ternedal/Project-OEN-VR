# Eksekveringsplan — PROJECT ØEN — Claude / Unity-sporet

> **Opdateret 2026-08-13.** M0a er afgjort (`DROP_Q1_RUNTIME`). M0b er bevist per klient og mangler nu cross-device-gaten. Denne fil beskriver Claudes Unity-/runtime-spor og skal læses sammen med `AI_COLLABORATION_AGREEMENT.md`.

---

## Rolle og mission

Claude er **Unity Lead** på **PROJECT ØEN — STRANDET SAMMEN**.

Hovedregel:

- **Claude ejer Unity-projektet, Unity-runtimekode, C#/XR/Fusion-binding, builds, profiling og Unity-side QA.**
- **ChatGPT ejer produkt/design, specs, source-assets, audio-materiale, ekstern arkitektur og tværgående produkt-QA.**
- Anders er produktejer og har sidste ord.

Claude må foreslå produkt- eller designændringer, men må ikke implementere dem som skjulte scopeændringer. Se `AI_COLLABORATION_AGREEMENT.md`.

Missionen lige nu er:

> **Luk M0b med faktisk cross-device-evidens på Quest 2/3 uden at starte spekulativ M1/content.**

---

## Læs først

1. `00_READ_ME_FIRST.md` — source-of-truth og dokumenthierarki.
2. `AI_COLLABORATION_AGREEMENT.md` — ansvar og handoff-grænser.
3. `repo_status.md` — aktuel dokumenteret tilstand.
4. GitHub issue #3 — aktuel M0b-gate.
5. `config/COMPATIBILITY_MATRIX.md` — faktiske device-resultater.
6. `src/unity/RUNBOOK_FUSION.md` — Unity/Fusion-runbook og on-device-fund.
7. `docs/30_M0_ISSUE_BODY.md` — M0-definitionen.
8. `docs/06_TECHNICAL_ARCHITECTURE.md`, `docs/07_MULTIPLAYER_NETWORKING.md`, `docs/08_PLATFORM_BUILD_PERFORMANCE.md`.
9. `docs/35_M_PRE_GREYBOX_GATE.md` — produktgaten, som skal være grøn før M1.

Ved konflikt gælder hierarkiet i `00_READ_ME_FIRST.md`. Accepted ADR'er ændres ikke stiltiende.

---

# Aktuel tilstand

## Bevist

- Kritisk review er behandlet; alle 10 fund er lukket.
- Baseline v2.1 er på `main`.
- Quest 1-runtime/testlane er droppet (`DROP_Q1_RUNTIME`).
- Unity er låst til `6000.4.10f1` med OpenXR.
- Quest 2 er performancegulv; Quest 3/3S er enhanced parity.
- Photon Fusion `2.0.12` er installeret og har kørt on-device.
- `NetworkRunner.StartGame` forbinder til Photon i Shared mode.
- `NetworkPlayerRig` spawner med input authority.
- Head pose er bevist non-zero og bevægelig via `InputDevices`.
- Coop-kasse/solver-kæden er kørt on-device med `quality=1.00` i den dokumenterede enkelt-klient-feasibility-test.
- Core-laget har 146 grønne tests og CI.
- M-Pre er accepteret som selvstændig produktgate via ADR-022.

## Ikke bevist endnu — M0b cross-device

Følgende kræver to headset og faktiske resultater:

1. Begge klienter ser hinandens head/hands bevæge sig.
2. Compatibility handshake afviser content/protocol mismatch før spawn.
3. Den delte kasse går korrekt i to-spiller-state og ender samme sted på begge klienter.
4. 10× Q2↔Q3-løft gennemføres uden permanent desync (`PO-025`).
5. Minimal netværksscene holder 72 Hz på Quest 2 og relevante Q3-tests.
6. Standby/reconnect-vinduet måles med faktisk device-adfærd (`CR-009`).
7. Resultater føres ind i `config/COMPATIBILITY_MATRIX.md`.

M0 er først lukket, når gaten kan erklæres `GO` eller `REDESIGN` på evidens.

---

# Hvad Claude skal gøre nu

## 1. Afslut M0b — ingen nye produktfeatures

Arbejd kun på det, der er nødvendigt for at gennemføre de resterende M0b-tests.

Prioritet:

1. to-client session og pose-replikering
2. handshake mismatch-test
3. delt coop-object med to spillere
4. 10× cross-device repetition
5. performance-måling
6. standby/reconnect-måling
7. matrix/evidens

Stop ved første reproducerbare røde gate og find årsagen, før flere features tilføjes.

## 2. Dokumentér evidens, ikke forventninger

For hver test skal resultatet kunne spores til mindst ét af:

- device-log / logcat
- profiler-/frame timing-resultat
- reproducerbar testsekvens
- compatibility-matrix
- commit med den relevante ændring

Skriv aldrig `OK`, hvis noget kun er kompileret eller vurderet fra kildekode.

## 3. Vent med M1 til to gates er grønne

M1 må først begynde, når:

- **M0b er grøn**, og
- **M-Pre er grøn**.

M-Pre køres i ChatGPT/Anders-sporet uden VR. Claude skal ikke redesigne M-Pre-protokollen eller masseproducere Unity-content for at omgå den.

---

# Ansvarsgrænse under implementering

## Claude ejer

- Unity scenes/prefabs/components
- C# der indgår i Unity-runtime/editor
- XR/OpenXR/Fusion
- network authority og replication
- Unity asset-import/integration
- Unity audio-integration
- Quest builds
- profiling/performance
- Unity-side tests og regressions

## ChatGPT ejer

- gameplay-/produktkrav
- visuel retning og source-assets
- lyddesign/source-audio
- M-Pre og øvrige design-testprotokoller
- roadmap og produktprioritering
- player-experience/UX-specifikationer
- produkt-QA og handoff-materiale

Ved tværgående problemer: ChatGPT specificerer ønsket oplevelse/krav; Claude vælger Unity-implementeringen.

---

# Det skal du IKKE gøre

- Genindføre Quest 1 som runtime- eller testlane.
- Starte M1 før både M0b og M-Pre er grønne.
- Masseproducere Stormnatten-content eller art før de relevante gates.
- Ændre accepted ADR'er stiltiende.
- Påstå on-device-funktion uden device-evidens.
- Lave parallelle implementationsspor, hvis en eksisterende komponent kan forbedres.
- Ændre produktretning, rollemodel, randomness eller efterspilsdesign uden handoff/beslutning.
- Lægge tokens, App IDs eller andre hemmeligheder i repoet.

---

# Handoff tilbage til ChatGPT/Anders

Efter et Unity-inkrement skal Claude rapportere:

1. **Implementeret** — hvad er ændret?
2. **Filer** — hvilke Unity/runtime-filer er berørt?
3. **Testet** — præcis hvordan?
4. **Verificeret** — hvad er faktisk bevist?
5. **Ikke verificeret** — hvad mangler stadig?
6. **Nye produkt-/assetbehov** — kræves beslutning, grafik, lyd eller spec?
7. **Næste tekniske handling** — kun inden for Claude-sporet.

Den vigtigste regel er fortsat:

> **Måling slår antagelse. En grøn compile er ikke det samme som en grøn device-gate.**
