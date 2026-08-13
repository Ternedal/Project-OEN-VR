# Åbne spørgsmål

## Skal afgøres i M0

| ID | Spørgsmål | Beslutningsmetode |
|---|---|---|
| ~~OQ-001~~ | **Besvaret 2026-08-08 (M0a):** OpenXR starter stabilt på Q2 (og Q3), ikke på Q1. Editor låst til Unity 6 LTS. | Lukket |
| ~~OQ-002~~ | **Bortfaldet 2026-08-08:** kun ét manifest, da Q1-lanen er droppet (DROP_Q1_RUNTIME). | Lukket |
| ~~OQ-003~~ | **Droppet 2026-08-08:** spiket var betinget af Q1-lanen. Vulkan er bekræftet på Quest 2 i M0a; GLES3-fallback udgår (ADR-018 resolved). | Lukket |
| OQ-004 | Kan Fusion Shared håndtere coop box uden permanent desync? | 10× cross-device interaction test; følges i issue #3 og `config/COMPATIBILITY_MATRIX.md` |
| OQ-005 | Hvordan håndteres coordinator loss mest robust? | Prototype handover vs checkpoint resume |

## Skal afgøres i designprototype

| ID | Spørgsmål | Beslutningsmetode |
|---|---|---|
| OQ-006 | Skaber fire effort markers nok diskussion? | **M-Pre greybox-gate** (ADR-022, `docs/35`) — ready-to-run-pakke i `prototype/m-pre/` |
| OQ-007 | Er rollerne for asymmetriske eller for ens? | M-Pre observerer **naturlig arbejdsdeling**; eksplicit rolleasymmetri må først lukkes sammen med OQ-009-data |
| OQ-008 | Hvor meget randomness føles fair? | Protokol klar: `prototype/design-tests/OQ-008_RANDOMNESS_FAIRNESS.md`; 1/6 vs 1/3 komplikationsrisiko, fairness/agency måles |
| OQ-009 | Skal spillerroller vælges eller skifte automatisk? | Protokol klar: `prototype/design-tests/OQ-009_ROLE_ASSIGNMENT.md`; selvvalgt/fikseret vs automatisk rotation |
| OQ-010 | Er efterspils-konkurrence ønskelig i gavebuild? | Protokol klar: `prototype/design-tests/OQ-010_AFTER_ACTION_COMPETITION.md`; fælles efterspil vs fælles+ikke-hierarkiske titler |

**Vigtigt:** “protokol klar” er ikke det samme som “spørgsmålet besvaret”. OQ-006–OQ-010 lukkes kun på observerede menneskedata og relevante gates.

## Product owner input senere

- Skal spillet primært kunne spilles i samme rum eller også optimeres til fjernspil fra første release?
- Skal den personlige finale være romantisk, humoristisk eller primært eventyrlig?
- Skal karaktererne være eksplicit baseret på spillerne eller neutrale overlevende?
- Hvor hård må standard-sværhedsgraden være?
- Er dansk eneste launch-sprog, eller skal engelsk med fra første content pass?

Disse spørgsmål blokerer ikke M0-M2.
