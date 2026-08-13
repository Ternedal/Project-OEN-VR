# Claude-instruktion for PROJECT ØEN

Begynd altid med:

1. `00_READ_ME_FIRST.md`
2. `AI_COLLABORATION_AGREEMENT.md`
3. `repo_status.md`
4. `docs/32_OPUS_EXECUTION_PLAN.md`

`01_PROMPT_FOR_CLAUDE.md` er **arkiveret review-materiale** fra review v1.0 og er ikke den aktuelle opgave.

## Samarbejdsmodel

`AI_COLLABORATION_AGREEMENT.md` er autoritativ for rolle- og ansvarsdelingen.

- **Claude = Unity:** Unity-projekt, C#/runtime/editor, XR/OpenXR/Fusion, scenes/prefabs, integration, builds, profiling og Unity-side QA.
- **ChatGPT = alt andet:** produkt/design, specs, source-assets, audio-materiale, roadmap, design-tests og tværgående produkt-QA.
- Anders er produktejer og har sidste ord.

## Aktuel opgave

**Luk M0b cross-device-gaten.**

Per-client M0b er allerede bevist. Det der mangler er faktisk to-headset-evidens for:

1. remote head/hands-replikering
2. compatibility-handshake mismatch-afvisning
3. delt coop-kasse i to-spiller-state
4. 10× Q2↔Q3-løft uden permanent desync
5. 72 Hz i minimal netværksscene
6. standby/reconnect-vindue
7. opdatering af `config/COMPATIBILITY_MATRIX.md`

Se GitHub issue #3 og `src/unity/RUNBOOK_FUSION.md`.

## Ufravigelige rammer

- Quest 2 er performance- og kvalitetsbaseline.
- Quest 1 er udgået som runtime/testlane (`DROP_Q1_RUNTIME`).
- Quest 3/3S har samme gameplay og kun additive forbedringer.
- MVP/gaveversionen har præcis to spillere.
- Projektet er original IP.
- Påstå ikke device-success uden device-evidens.
- Accepted ADR'er ændres ikke stiltiende.
- Ingen dyr content/artproduktion før de relevante gates.
- M1 starter først, når **både M0b og M-Pre er grønne**.

## Handoff

Når et Unity-inkrement er færdigt, rapportér:

- hvad der er implementeret
- hvilke filer der er ændret
- hvordan det er testet
- hvad der faktisk er verificeret
- hvad der ikke er verificeret
- hvilke produkt-/asset-/lydbehov der skal tilbage til ChatGPT
- næste tekniske handling inden for Unity-sporet
