# Backlog ownership & status overlay — PROJECT ØEN

**Dato:** 2026-08-13  
**Formål:** Gøre `docs/17_BACKLOG_AND_MILESTONES.md` eksekverbart under den nye Claude/ChatGPT-arbejdsdeling uden at forfalske den eksisterende workbook-status.

## Vigtigt

`docs/17_BACKLOG_AND_MILESTONES.md` / workbooken er fortsat den formelle backlog. Mange rækker står stadig `Not Started`, selv om:

- dele af fundamentet allerede er bygget/testet
- ChatGPT nu har lavet produkt-/content-/source-prework
- nogle tasks har både en ChatGPT-del og en Claude-del

Dette dokument er derfor et **overlay**, ikke en erstatning.

### Statusord i dette overlay

- `SPEC_READY` — ChatGPT-side er specificeret nok til handoff, men implementation/produktion kan mangle.
- `SOURCE_READY` — source content/copy/manifest findes; runtime-binding mangler.
- `PARTIAL` — dokumenteret delarbejde findes, men backlog-itemets acceptance criteria er ikke opfyldt.
- `EVIDENCE_WAIT` — kræver human/device evidence.
- `CLAUDE` — primært Unity/runtime-arbejde.
- `CHATGPT` — primært produkt/content/source-arbejde.
- `SHARED` — ChatGPT leverer krav/source; Claude implementerer/binder.
- `HUMAN` — acceptance kræver fysisk/human test.

Et backlog-item markeres **ikke Done** her, medmindre dets egentlige acceptance criteria er bevist.

---

# 1. Ejerskabsregler

## Claude primary

Som udgangspunkt:

- Unity project/setup
- XR/OpenXR/Fusion
- runtime C# / Unity integration
- build profiles
- scene/prefab/component implementation
- save/reconnect runtime
- profiling/performance
- device QA execution

## ChatGPT primary

Som udgangspunkt:

- game/product design
- scenario/content authoring
- narrative/copy/localization source
- source art/audio design og assets
- UX/information architecture
- personalization source package
- provenance/licensing register
- human test design
- release/gift experience

## Shared

Typisk:

- interaction content
- source assets/audio → Unity binding
- UI/copy → runtime UI
- VFX source/design → runtime VFX
- personalization hooks → loader/runtime
- metrics definition → runtime telemetry

---

# 2. M0 / M-Pre

| ID | Titel | Primær | Overlay-status | Note |
|---|---|---|---|---|
| `PO-000` | Behandl Claude-review og baseline | ChatGPT/owner | **Faktisk udført** | Reviewfund er dispositioneret og baseline v2.1 merget; backlogtekst er historisk stale |
| `PO-001` | Pin Unity editor | Claude | PARTIAL/CLAUDE | Unity 6000.4.10f1 dokumenteret on-device; formel backlog closure hos Claude |
| `PO-002` | Android IL2CPP/OpenXR | Claude | PARTIAL/CLAUDE | M0a/M0b evidence findes |
| `PO-003` | BuildInfo/platform detection | Claude | CLAUDE | product info requirements findes |
| `PO-005` | Q2_BASE profile | Claude | PARTIAL/CLAUDE | Q2 OpenXR on-device evidence findes |
| `PO-006` | Q3_ENHANCED profile | Claude | CLAUDE/EVIDENCE_WAIT | Q3 evidence kræves |
| `PO-008` | Compatibility matrix | Claude | PARTIAL | matrix findes; Q2↔Q3 gate åben |
| `PO-017`–`PO-025` | Fusion/session/handshake/replication/box | Claude | PARTIAL/EVIDENCE_WAIT | issue #3 er aktiv source of truth |
| `PO-094` | Content/schema CI validation | Shared | PARTIAL | repo-validator findes og kører; acceptance skal vurderes mod fuldt item |
| `PO-101` | Core test suite | Claude/Core | PARTIAL | 146 tests dokumenteret; tracker ikke reconcilet |
| `PO-103` | Device test checklist | Claude/Anders | PARTIAL | compatibility matrix/runbooks findes; item er deferred i backlog |
| `PO-110` | M-Pre greybox gate | ChatGPT/Human | **EVIDENCE_WAIT** | materialet er komplet; issue #7 afventer 3 sessions |

---

# 3. M1 — Interaction foundation

M1 implementation åbner først efter grøn M0b + M-Pre. Produktforberedelse kan laves nu.

| ID | Titel | Primær | ChatGPT-prework | Runtime/evidence der mangler |
|---|---|---|---|---|
| `PO-009` | XR Origin/gulvkalibrering | Claude | setup/comfort copy + IA klar | Unity + device |
| `PO-010` | Teleport | Claude | UX/comfort krav klar | Unity + human/device |
| `PO-011` | Snap turn | Claude | settings copy + 15/30/45 krav klar | Unity + human/device |
| `PO-012` | Grab/reset | Claude | onboarding + critical-object copy/QA klar | Unity |
| `PO-013` | Snap target preview | Shared | visual/UX source spec klar | source production + Unity |
| `PO-014` | Two-hand object | Claude | player-experience QA/intro use klar | Unity/device |
| `PO-015` | Haptics | Claude | product intent/accessibility klar | deferred runtime |
| `PO-016` | Reach/seated playtest | Human | **testprotokol klar** (`docs/42`) | physical test |
| `PO-073` | Handedness | Claude | settings copy/IA klar | Unity |
| `PO-075` | Comfort menu | Shared | **SPEC_READY** (`docs/48`, `docs/40`) | Unity UI |
| `PO-076` | Critical object return/reset | Shared | **SPEC_READY** copy + QA | Unity |

---

# 4. M3 — One-day prototype / planning

| ID | Titel | Primær | Overlay-status | ChatGPT leverance |
|---|---|---|---|---|
| `PO-027`–`PO-029` | Scenario flow | Claude | CLAUDE | product phase/content contract findes |
| `PO-030` | Seed/deterministic selection | Claude | deferred | randomness policy partly OQ-008-gated |
| `PO-031`/`032` | Debug/simulation | Claude | deferred | — |
| `PO-033` | Four effort markers | Shared | **SPEC_READY + EVIDENCE_WAIT** | M-Pre package + planning brief |
| `PO-034` | Plan lock race | Claude | product recovery/copy klar | runtime |
| `PO-035` | Shared resource state | Claude | resource product model exists | runtime |
| `PO-036`/`037` | Player/camp status | Shared | UX/status language + visual rules klar | runtime; deferred in current scope |
| `PO-038` | Physical planning table | Shared | **SPEC_READY** | asset manifest + planning brief + UI IA + copy |
| `PO-039` | External one-day playtest | Human | **test protocol ready** | M3 build + human evidence |
| `PO-040` | InteractionSequence model | Claude | multiple player-experience briefs ready | runtime/data model |
| `PO-041` | Quality scoring | Claude | outcome UX rules exist | deferred/tuning evidence |
| `PO-042` | Shelter greybox interaction | Shared | **SPEC_READY** | `design/interactions/SHELTER_REINFORCEMENT.md` |
| `PO-044` | Fire-start | Shared | **SPEC_READY but scope conflict** | interaction brief; issue #8 |
| `PO-054` | Greybox beach/camp | Shared | coverage/style/source manifest ready | current backlog says Defer |

---

# 5. M4 — Consequences

| ID | Titel | Primær | Overlay-status | ChatGPT-prework |
|---|---|---|---|---|
| `PO-043` | Tool durability | Claude | deferred | event authoring guards against hard dependency |
| `PO-046` | Assisted repetition | Claude | product rule documented | deferred |
| `PO-047` | Event loader/validator | Claude | event contract/catalog ready | runtime |
| `PO-048` | Delayed event queue | Claude | causal content rules ready | runtime/Core foundation exists |
| `PO-049` | Tags/conditions | Claude | authoring intent ready | runtime |
| `PO-050` | Open food → animal chain | Shared | **CONTENT_SPEC_READY** | existing event JSON + event catalog + QA |
| `PO-051` | Injury → infection | Shared | **CONTENT_SPEC_READY** | event catalog; implementation deferred |
| `PO-052` | Causal after-action report | Shared | **PRODUCT_SPEC_READY** | `docs/49`, copy patterns, metrics |
| `PO-053` | Event validation tests | Claude | authoring rules ready | deferred runtime tests |

---

# 6. M5 — Release 1 storm slice

| ID | Titel | Primær | Overlay-status | ChatGPT-prework |
|---|---|---|---|---|
| `PO-045` | Signal frame interaction | Shared | PARTIAL SPEC | finale brief + asset/audio/copy; dedicated finer brief may still be useful |
| `PO-060` | Storm phase 1-2 | Shared | **SPEC_READY** | storm finale brief + coverage + source/audio/copy |
| `PO-061` | Storm phase 3-5 | Shared | **SPEC_READY / OQ-008 part gated** | storm brief; phase 3 probability not locked |
| `PO-062` | Win/lose/retry | Shared | **PRODUCT_SPEC_READY** | gift flow + after-action/replay copy |
| `PO-083` | Storm VFX profiles | Shared | **SOURCE_SPEC_READY** | asset manifest + style bible; runtime profile Claude |
| `PO-105` | Storm soak | Claude/Anders | EVIDENCE_WAIT | human-side test protocol exists; technical soak Claude |

---

# 7. M6 — Full Stormnatten content

| ID | Titel | Primær | Overlay-status | ChatGPT-prework |
|---|---|---|---|---|
| `PO-055` | Jungle zone | Shared | SOURCE_SPEC_READY | asset/style/coverage; deferred current scope |
| `PO-056` | Ravine rescue | Shared | **SPEC_READY** | dedicated interaction brief + assets/audio/QA |
| `PO-057` | Day 1 content | ChatGPT/Shared | PARTIAL | bible + coverage + event/copy; backlog Defer |
| `PO-058` | Day 2 content | ChatGPT/Shared | **PARTIAL SPEC** | coverage, action copy, event catalog |
| `PO-059` | Day 3 preparation | ChatGPT/Shared | **PARTIAL + CONTRACT_GAP** | coverage; issue #8 tracks missing phase representation |
| `PO-063` | Tune 10 events | ChatGPT/Human | **AUTHORING_READY / TUNING_WAIT** | ten-event catalog ready; tuning waits evidence |
| `PO-064` | Full scenario external playtest | Human | **TEST_READY / EVIDENCE_WAIT** | M6 protocol in docs/42 |
| `PO-071` | Save migration | Claude | deferred | — |
| `PO-072` | Standby tests | Claude/Anders | EVIDENCE_WAIT | human/device protocol context exists |
| `PO-074` | Subtitle system | Claude | deferred | **source Danish copy already exists** |
| `PO-077` | Onboarding hint controller | Shared | **COPY/SPEC_READY** | hint catalog exists; runtime controller Claude |
| `PO-099` | Local log export | Claude | CLAUDE | product privacy/metric contract ready |

---

# 8. M7 — Art/audio/performance

| ID | Titel | Primær | Overlay-status | ChatGPT-prework |
|---|---|---|---|---|
| `PO-080` | Shared material palette | Shared | **STYLE_SPEC_READY** | style bible/material families; runtime materials Claude |
| `PO-081` | Camp art pass | ChatGPT + Claude | SOURCE_MANIFEST_READY | mass production deferred |
| `PO-082` | Jungle/ravine art | ChatGPT + Claude | SOURCE_MANIFEST_READY | mass production deferred |
| `PO-084` | Adaptive ambience/storm audio | ChatGPT + Claude | **AUDIO_SPEC_READY** | full cue manifest; source production/mix later |
| `PO-085` | Avatar polish | ChatGPT + Claude | SOURCE_SPEC_READY | player identity rules ready |
| `PO-086` | Q2 optimization | Claude | CLAUDE | visual/source principles respect Q2 |
| `PO-087` | Q3 enhancement | Claude | CLAUDE | product parity rule fixed |

---

# 9. M8 — Personalization / gift release

| ID | Titel | Primær | Overlay-status | ChatGPT-prework |
|---|---|---|---|---|
| `PO-088` | PersonalizationProfile loader | Claude | CLAUDE | package/schema/product contract ready |
| `PO-089` | Private asset validation | Shared | **VALIDATION_SPEC_READY** | source/privacy checklist ready; runtime validator Claude |
| `PO-090` | Ending crate/radio hooks | Shared | **PRODUCT_SPEC_READY** | hook set, fallback, gift flow ready |
| `PO-091` | Integrate private image/audio | Shared | deferred | source requirements ready; private actual assets later |
| `PO-092` | Neutral fallback E2E | Shared/Human | **CONTENT_SPEC_READY** | neutral copy/flow defined; runtime test later |
| `PO-093` | Personal finale playtest | Human | deferred/evidence | test rules prepared |
| `PO-096` | Signing/keystore | Claude/Anders | CLAUDE | — |
| `PO-097` | Alpha release flow | Claude/Anders | CLAUDE | gift player flow defined |

---

# 10. M9 — Release QA

| ID | Titel | Primær | Overlay-status |
|---|---|---|---|
| `PO-078` | Comfort playtest | Human | TEST_PROTOCOL_READY |
| `PO-079` | Color/shape accessibility | ChatGPT/Human | DESIGN_RULES_READY; human review later |
| `PO-100` | Artifact/rollback archive | Claude | CLAUDE |
| `PO-106` | Regression matrix | Claude/Anders | EVIDENCE_WAIT |
| `PO-107` | P0/P1 closure | Shared | future |
| `PO-108` | RC clean-install | Human/Claude | TEST_PROTOCOL_READY; build later |

---

# 11. Localization / source content

`PO-104` remains formally deferred as the full localization/subtitle content pass.

However, ChatGPT has already delivered **prework**:

- source key/copy catalog: `docs/40_UX_COPY_AND_LOCALIZATION_CATALOG.md`
- machine-readable Danish source: `content/localization/da.source.json`

This does not mean `PO-104` is Done. It means later implementation no longer begins from zero.

---

# 12. Product telemetry

`PO-109` remains deferred as runtime performance telemetry in backlog.

ChatGPT product-prework exists separately:

- `docs/50_PRODUCT_TELEMETRY_AND_METRICS.md`

It defines product metrics/privacy and does not replace Claude's runtime/performance implementation.

---

# 13. What this overlay changes operationally

The backlog should no longer be interpreted as:

> “Everything is Not Started, therefore ChatGPT should wait.”

Instead:

- many Unity acceptance criteria remain genuinely unimplemented
- many content/art/audio items have **source/spec prework completed**
- human gates remain genuinely unproven
- balance remains intentionally unlocked

The next planning question for each item is now:

> **Which layer is missing — product/source, Unity/runtime, or evidence?**

That keeps Claude and ChatGPT from duplicating work or declaring partial prework “Done”.
