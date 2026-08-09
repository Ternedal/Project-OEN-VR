# Åbne spørgsmål

## Skal afgøres i M0

| ID | Spørgsmål | Beslutningsmetode |
|---|---|---|
| ~~OQ-001~~ | **Besvaret 2026-08-08 (M0a):** OpenXR starter stabilt på Q2 (og Q3), ikke på Q1. Editor låst til Unity 6 LTS. | Lukket |
| ~~OQ-002~~ | **Bortfaldet 2026-08-08:** kun ét manifest, da Q1-lanen er droppet (DROP_Q1_RUNTIME). | Lukket |
| ~~OQ-003~~ | **Droppet 2026-08-08:** spiket var betinget af Q1-lanen. Vulkan er bekræftet på Quest 2 i M0a; GLES3-fallback udgår (ADR-018 resolved). | Lukket |
| OQ-004 | Kan Fusion Shared håndtere coop box uden permanent desync? | 10x cross-device interaction test |
| OQ-005 | Hvordan håndteres coordinator loss mest robust? | Prototype handover vs checkpoint resume |

## Skal afgøres i designprototype

| ID | Spørgsmål | Beslutningsmetode |
|---|---|---|
| OQ-006 | Skaber fire effort markers nok diskussion? | Ekstern one-day playtest |
| OQ-007 | Er rollerne for asymmetriske eller for ens? | Observeret arbejdsfordeling |
| OQ-008 | Hvor meget randomness føles fair? | A/B event outcome tests |
| OQ-009 | Skal spillerroller vælges eller skifte automatisk? | To prototypevarianter |
| OQ-010 | Er efterspils-konkurrence ønskelig i gavebuild? | Test med målbrugerne efter neutral run |

## Product owner input senere

- Skal spillet primært kunne spilles i samme rum eller også optimeres til fjernspil fra første release?
- Skal den personlige finale være romantisk, humoristisk eller primært eventyrlig?
- Skal karaktererne være eksplicit baseret på spillerne eller neutrale overlevende?
- Hvor hård må standard-sværhedsgraden være?
- Er dansk eneste launch-sprog, eller skal engelsk med fra første content pass?

Disse spørgsmål blokerer ikke M0-M2.
