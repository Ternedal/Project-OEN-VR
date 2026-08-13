# Implementeringsrækkefølge — gate-baseret

> **Opdateret 2026-08-13.** Review v1.0 er behandlet. Denne plan beskriver rækkefølgen fra den aktuelle M0b-status fremad og skal læses sammen med `AI_COLLABORATION_AGREEMENT.md`.

Projektet styres af gates, ikke af en antagelse om at næste PR automatisk må startes.

---

## Nu — luk M0b

Per-client M0b er allerede bevist. Claude/Unity-sporet skal kun lukke de resterende cross-device-punkter:

1. remote head/hands mellem to klienter
2. compatibility mismatch-afvisning før spawn
3. delt coop-kasse i to-spiller-state
4. 10× Q2↔Q3-løft uden permanent desync
5. 72 Hz i minimal netværksscene
6. standby/reconnect-måling
7. faktisk evidens i `config/COMPATIBILITY_MATRIX.md`

**Gate:** M0b = `GO` eller `REDESIGN` på device-evidens.

---

## Parallelt — M-Pre

ChatGPT/produkt-sporet har gjort M-Pre ready-to-run under `prototype/m-pre/`.

M-Pre køres med mennesker og tester, om fire indsatsmarkører skaber reel diskussion frem for administration.

**Gate:** mindst to af tre sessioner opfylder kriterierne i `docs/35_M_PRE_GREYBOX_GATE.md`.

---

# Stoplinje før M1

**M1 må ikke begynde, før både M0b og M-Pre er grønne.**

Ved rød M0b → teknisk redesign i Claude-sporet.

Ved rød M-Pre → kerneloop-redesign i ChatGPT/produkt-sporet før mere gameplay-implementation.

---

# Efter grøn M0b + M-Pre

## M1 — Interaction foundation

ChatGPT leverer player-experience/UX-handoff. Claude implementerer Unity-delen.

Unity-scope:

- XR rig og kalibrering
- locomotion/comfort
- grab wrapper/reset
- snap targets
- lokalt tohåndsobjekt
- feedback/haptics efter godkendte krav
- seated/standing-verifikation

**Gate:** kerneinteraktioner kan udføres gentagne gange af testere uden reset, og comfort-/reach-krav er opfyldt.

---

## M2 — Multiplayer hardening

- ready/lobby-flow
- authority-regler for øvrige objekter
- disconnect/reconnect og safe pause
- checkpoint/resync
- network debug UI
- failure/latency-hardening efter backlogscope

**Gate:** session cycles og state transfer uden skjult divergence.

---

## M3 — One-day greybox

Først her åbnes den egentlige one-day gameplay-greybox:

- camp
- planning markers
- én dags faseflow
- shelter-action
- dusk/night
- relevante resources/player/camp states

**Gate:** ekstern test kan gennemføre dagen uden udviklerforklaring og oplever et reelt prioriteringsvalg.

---

## M4 — Consequences

- delayed event chains
- injury/treatment
- weather/state branches
- after-action causal report

**Gate:** tester kan forklare mindst én forsinket årsag/virkning-kæde.

---

## M5 — Storm vertical slice / Release 1

- stormens tre faser
- to aktive roller pr. fase
- branches fra tidligere state
- win/lose/retry
- performance soak

**Gate:** afsendbar storm vertical slice med stabil Quest 2-performance og netværk.

---

# Art, audio og content

- Source asset-/audio-manifests må forberedes gate-aware.
- Dyr masseproduktion af art eller fuld Stormnatten-content må ikke starte før de relevante gameplay-gates er grønne.
- ChatGPT ejer source-materiale og retning.
- Claude ejer Unity-import, integration, runtime-adfærd og performance.

---

# Historisk mapping

Den gamle PR-rækkefølge var:

1. repository/bootstrap
2. XR device spike
3. Photon session spike
4. coop object proof
5. save/state skeleton
6. one-day greybox

De første feasibilitydele er nu helt eller delvist gennemført. Denne fil må derfor ikke læses som en ordre om at bygge dem om.

---

# Hovedregel

> **Næste milestone åbnes af evidens, ikke af momentum.**
