# Non-Unity gap audit — PROJECT ØEN

**Ejer:** ChatGPT  
**Projektejer:** Anders  
**Dato:** 2026-08-13  
**Scope:** Alt uden for Unity jf. `AI_COLLABORATION_AGREEMENT.md`

## Konklusion

PROJECT ØEN er **langt fra færdig uden for Unity**.

Den tidligere arbejdsregel, hvor source asset/audio-manifests først blev åbnet efter grøn M-Pre, var for restriktiv. M-Pre skal blokere **irreversible eller dyre design-/produktionsbeslutninger**, ikke det forberedende arbejde der gør projektet eksekverbart.

Den korrekte regel er derfor:

> **Specifikation, katalogisering, content coverage, copy, QA-design, personaliseringskontrakter og produktionsberedskab må laves før M-Pre.**
>
> **Tuning, dyr masseproduktion og designvalg som M-Pre/OQ-tests faktisk skal afgøre, venter på evidens.**

Dette dokument er ChatGPTs samlede mangelliste og prioriteringsgrundlag.

---

# 1. Status pr. arbejdsområde

| Område | Status | Må arbejdes nu? | Primær ejer |
|---|---|---:|---|
| Produktvision / core loop | God baseline, enkelte åbne designspørgsmål | Ja, men ikke lukke evidensspørgsmål | ChatGPT |
| M-Pre | Materiale klar, menneskedata mangler | Testen kræver mennesker | ChatGPT/Anders |
| Scenario/content | Bible + eksempeldata findes, men produktionsspec er ufuldstændig | **Ja** | ChatGPT |
| Narrative/copy | Spredt i docs, intet samlet katalog | **Ja** | ChatGPT |
| UX/information architecture | Principper findes, konkrete states/copy mangler | **Ja** | ChatGPT |
| Source assets | Retning findes, autoritativ assetliste mangler | **Ja** | ChatGPT |
| Audio | Retning findes, cue-/source-manifest mangler | **Ja** | ChatGPT |
| VFX design | Retning findes, cue-/state-spec mangler | **Ja** | ChatGPT; Unity-implementation Claude |
| Personalization | Schema/example findes, produktionspakke mangler | **Ja** | ChatGPT |
| Localization | Krav/key-regel findes, source-string-katalog mangler | **Ja** som forberedelse |
| Human QA | Releasekrav findes, milepælsvise testpakker mangler | **Ja** | ChatGPT |
| Device/Unity QA | M0b + senere device-gates | Nej, Claude-spor | Claude/Anders |
| Release/gaveoplevelse | Tekniske releasekrav findes, bruger-/gaveflow er tyndt | **Ja** | ChatGPT + Claude for build |
| IP/licenser/provenance | Risiko dokumenteret, ingen operationel asset-registerproces | **Ja** | ChatGPT |
| Telemetry/after-action product spec | Grundprincip findes, præsentationsspec mangler | **Ja** | ChatGPT |
| Marketing/offentlig release | Ikke nødvendigt til gaveversionen | Senere | ChatGPT |

---

# 2. Verificerede non-Unity-huller

## A. Source asset manifest mangler

`docs/11_ART_AUDIO_UI_DIRECTION.md` beskriver stil, men ikke **hvilke konkrete source assets der skal produceres**.

Backloggen indeholder blandt andet:

- `PO-038` fysisk planlægningsbord
- `PO-042` shelter greybox interaction
- `PO-044` fire-start interaction
- `PO-045` signal frame interaction
- `PO-054` strand/camp
- `PO-055` jungle
- `PO-056` ravine rescue
- `PO-080` shared material palette
- `PO-081` camp art
- `PO-082` jungle/ravine art
- `PO-083` storm VFX
- `PO-085` avatar polish

Der mangler en autoritativ liste med asset-ID, funktion, zone, milepæl, source-format, variation, status og Unity-handoff.

**Handling:** `docs/38_SOURCE_ASSET_MANIFEST.md`.

---

## B. Audio cue/source manifest mangler

Audio-retningen siger bl.a. zone ambience, vindlag, tagknirken, rebspænding, fire-state, dyr og adaptiv musik, men der findes ikke et cue-katalog.

Backlog-item `PO-084` dækker implementeringen/produktionen senere, men source-design og katalogisering kan udføres nu.

**Handling:** `docs/39_AUDIO_CUE_MANIFEST.md`.

---

## C. UX-copy og localization source catalog mangler

Repoet har:

- key-regel i `docs/10`
- subtitle/accessibility-krav i `docs/09`
- tutorialprincipper i `docs/05`
- `PO-104` localization/subtitle content senere

Men der findes ikke ét sted med alle spillerrettede tekster, hints, errors, radio-linjer og neutral fallback-copy.

Det gør UI- og content-handoffs unødvendigt uklare.

**Handling:** `docs/40_UX_COPY_AND_LOCALIZATION_CATALOG.md`.

---

## D. Personalization er kun en datakontrakt — ikke en produktionspakke

Der findes schema og eksempelprofil, men der mangler konkrete regler for:

- private filers source-format
- safe-zone/crop for billeder
- audio source master
- memento-slots
- neutral fallback-copy
- hvordan romantisk/personligt indhold holdes adskilt fra canonical gameplay
- QA før private assets gives til Claude
- hvad der aldrig må ende i log/repo

**Handling:** `docs/41_PERSONALIZATION_PACKAGE_SPEC.md`.

---

## E. Human QA er beskrevet som gates, men ikke pakket som milepælstests

`docs/13` definerer releasekrav, men en facilitator/tester har ikke en ready-to-run-pakke for:

- M1 reach/comfort
- M3 one-day cooperation
- M5 storm slice
- M6 full scenario
- M8 personalization/fallback
- M9 release/comfort

**Handling:** `docs/42_HUMAN_QA_PLAYTEST_PACK.md`.

---

## F. IP/licens/provenance er en risiko, men ikke en arbejdsgang

R-009 er åben. Projektet siger original IP, men der mangler et konkret register for:

- købte assets
- genererede assets
- egne assets
- referencekilder
- musik/SFX-licens
- fonts
- billeder i personalization
- dokumentation for tilladt brug

**Handling:** `docs/43_IP_AND_ASSET_PROVENANCE.md`.

---

## G. Content coverage er fragmenteret

Scenario-biblen beskriver beats, og `examples/stormnatten.scenario.json` beskriver logisk content, men der mangler en matrix der forbinder:

**beat → interaction → source asset → audio cue → UI/copy → event/tag → test → Unity-handoff**.

Det er den vigtigste koordinationsflade mellem ChatGPT og Claude efter samarbejdsaftalen.

**Handling:** `docs/44_CONTENT_COVERAGE_MATRIX.md`.

---

## H. Interaktionsdesign er for ofte kun én linje i backloggen

Flere Unity-features har designintention, men ikke implementeringsklar player-experience-spec:

- shelter reinforcement
- fire start
- signal frame
- ravine rescue
- plan table
- storm phase 1-5
- final signal

ChatGPT bør levere disse som **interaction briefs** uden Unity-arkitektur.

**Handling:** opret `design/interactions/` og briefs for de releasekritiske sekvenser.

---

## I. Gave-/releaseoplevelsen er teknisk beskrevet, men ikke produktmæssigt

Der mangler blandt andet:

- first-launch flow
- hvordan den anden spiller inviteres
- hvad der vises før spillet uden at spoile gaven
- neutral fallback hvis private content ikke er tilgængeligt
- finale/epilog experience contract
- post-game/replay flow

**Handling:** senere `docs/45_GIFT_EXPERIENCE_AND_RELEASE_FLOW.md`.

---

# 3. Arbejde der er blokeret af evidens

Følgende må **ikke** lukkes på AI-vurdering:

- OQ-006: om fire effort markers skaber diskussion
- OQ-007/OQ-009: rolleasymmetri / rollevalg
- OQ-008: randomness fairness
- OQ-010: efterspils-konkurrence
- M-Pre gate
- endelig balance af scenario-tal
- endelig sværhedsgrad
- endelig 35-45 min content density

`docs/10` markerer eksplicit tallene i `examples/stormnatten.scenario.json` som **placeholdere til validering, ikke balancering**. De skal ikke gøres canonical før playtest.

---

# 4. Arbejde der er blokeret af Unity/device-evidens

Claude/Anders ejer:

- M0b cross-device
- concrete locomotion implementation
- XRI/Fusion binding
- runtime materials/shaders
- VFX implementation
- audio implementation/mix in Unity
- builds/signing
- Quest profiling
- device regressions

ChatGPT kan stadig levere krav, assets, source audio, copy og testcases til ovenstående.

---

# 5. Korrigeret prioriteret ChatGPT-kø

## Nu — ingen gateblokering

| ID | Leverance | Resultat |
|---|---|---|
| N-001 | Non-Unity gap audit | Dette dokument |
| N-002 | Source asset manifest | `docs/38_SOURCE_ASSET_MANIFEST.md` |
| N-003 | Audio cue manifest | `docs/39_AUDIO_CUE_MANIFEST.md` |
| N-004 | UX/copy/localization catalog | `docs/40_UX_COPY_AND_LOCALIZATION_CATALOG.md` |
| N-005 | Personalization package spec | `docs/41_PERSONALIZATION_PACKAGE_SPEC.md` |
| N-006 | Human QA/playtest pack | `docs/42_HUMAN_QA_PLAYTEST_PACK.md` |
| N-007 | IP/provenance register | `docs/43_IP_AND_ASSET_PROVENANCE.md` |
| N-008 | Content coverage matrix | `docs/44_CONTENT_COVERAGE_MATRIX.md` |
| N-009 | Releasekritiske interaction briefs | `design/interactions/` |
| N-010 | Gift/release product flow | `docs/45_GIFT_EXPERIENCE_AND_RELEASE_FLOW.md` |

## Afventer mennesker

- M-Pre / issue #7
- OQ-008/OQ-009/OQ-010 testresultater
- senere full-scenario playtests

## Afventer grøn gate før dyr produktion

- masseproduktion af environment art
- final audio production pass
- final VFX art
- tuning af 10 events
- endelig private personalization-production

Men **specifikationerne for disse må og skal være klar før da**.

---

# 6. Definition of done for ChatGPT-sporet

ChatGPTs non-Unity-side er først reelt “færdig” til gaveversionen, når mindst følgende findes og er QA'et:

1. alle produktbeslutninger har evidens eller eksplicit owner decision
2. hele Stormnatten har content coverage
3. alle source assets har manifest + status + provenance
4. alle audio cues har manifest + source-status
5. alle spillerrettede strings har key + dansk source copy + fallback
6. alle releasekritiske interactions har player-experience brief
7. personalization-pakken har neutral fallback og privacy QA
8. alle human gates har ready-to-run testpakker
9. gave-/first-run-/replay-flowet er beskrevet
10. alle handoffs til Claude har acceptance criteria og ingen skjulte produktbeslutninger

Først dér giver det mening at sige, at “alt uden for Unity” er færdigt.
