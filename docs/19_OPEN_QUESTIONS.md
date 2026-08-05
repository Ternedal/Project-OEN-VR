# Åbne spørgsmål

## Skal afgøres i M0

| ID | Spørgsmål | Beslutningsmetode |
|---|---|---|
| OQ-001 | ~~Kan Unity 2022.3 + provider starte stabilt på Q1/Q2/Q3?~~ | **Bortfaldet** jf. ADR-019/ADR-020. Erstattet af engine-baseline-gaten i `docs/06` §3 |
| OQ-002 | ~~Kræves to package manifests for Quest 1 vs modern?~~ | **Bortfaldet** jf. ADR-019. Kun én package lock |
| OQ-003 | ~~Vulkan stabil på Quest 1?~~ | **Bortfaldet** jf. ADR-019. Vulkan valideres på Quest 2 |
| OQ-004 | Kan Fusion Shared håndtere coop box uden permanent desync? | 10x cross-device interaction test |
| OQ-005 | Hvordan håndteres coordinator loss mest robust? | M2: undersøg Fusion 2.1 Master Client-switching, men commit til checkpoint-resume som besluttet fallback (CR-004) |

## Skal afgøres i designprototype

| ID | Spørgsmål | Beslutningsmetode |
|---|---|---|
| OQ-006 | Skaber fire effort markers nok diskussion? | **M-Pre-gaten** (ADR-021). Lukkes efter M-Pre |
| OQ-007 | Er rollerne for asymmetriske eller for ens? | Observeret arbejdsfordeling under **M-Pre**. Lukkes efter M-Pre |
| OQ-008 | Hvor meget randomness føles fair? | A/B event outcome tests |
| OQ-009 | Skal spillerroller vælges eller skifte automatisk? | To prototypevarianter |
| OQ-010 | Er efterspils-konkurrence ønskelig i gavebuild? | Test med målbrugerne efter neutral run |

## Besvaret af ejeren 2026-08-05 (DP-001)

| ID | Spørgsmål | Svar |
|---|---|---|
| Q-001 | Ejer gavemodtageren en Quest 1? | Nej. Udløste ADR-019 |
| Q-007 | Er der en deadline eller anledning? | Nej. Udløste ADR-022 og R-013 |

## Nye åbne spørgsmål

| ID | Spørgsmål | Blokerer |
|---|---|---|
| Q-008 | Hvilken headset-model præcist: Quest 2, 3 eller 3S? | Perf-budget i `docs/08` kan ikke låses uden svar. Quest 3 hæver gulvet markant og reducerer pres på R-006 og CR-005 |

## Product owner input senere

- Skal spillet primært kunne spilles i samme rum eller også optimeres til fjernspil fra første release?
- Skal den personlige finale være romantisk, humoristisk eller primært eventyrlig?
- Skal karaktererne være eksplicit baseret på spillerne eller neutrale overlevende?
- Hvor hård må standard-sværhedsgraden være?
- Er dansk eneste launch-sprog, eller skal engelsk med fra første content pass?

Disse spørgsmål blokerer ikke M0-M2.
