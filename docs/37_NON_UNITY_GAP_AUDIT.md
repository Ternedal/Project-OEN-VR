# Non-Unity gap audit — PROJECT ØEN

**Ejer:** ChatGPT  
**Projektejer:** Anders  
**Opdateret:** 2026-08-14  
**Scope:** Alt uden for Unity jf. `AI_COLLABORATION_AGREEMENT.md`

## Konklusion

Den oprindelige gap-audit fra 2026-08-13 var et arbejdsdokument. Dens N-002–N-010 leverancer er nu faktisk oprettet på `main` og må ikke længere behandles som manglende arbejde.

Det betyder **ikke**, at PROJECT ØEN er færdigt. Den korrekte status er nu:

> Den brede automatable non-Unity foundation er leveret. De primære resterende gates kræver faktisk menneskeevidens, fysisk Quest-evidens eller en eksplicit owner-beslutning.

Tooling readiness, source readiness og CI er ikke det samme som human approval, Unity integration eller release approval.

Autoritative statusflader:

- source/content state: `content/source_inventory.source.json`
- non-Unity workflow/tooling state: `content/non_unity_capability_matrix.source.json`
- asset/function IDs: `docs/38_SOURCE_ASSET_MANIFEST.md`
- current repo summary: `repo_status.md`

---

# 1. Closeout af den oprindelige N-00x-kø

| ID | Oprindelig leverance | Aktuel source of truth | Status nu |
|---|---|---|---|
| N-001 | Non-Unity gap audit | `docs/37_NON_UNITY_GAP_AUDIT.md` | **Reconciled** |
| N-002 | Source asset manifest | `docs/38_SOURCE_ASSET_MANIFEST.md` | **Leveret** |
| N-003 | Audio cue manifest | `docs/39_AUDIO_CUE_MANIFEST.md` | **Leveret** |
| N-004 | UX/copy/localization catalog | `docs/40_UX_COPY_AND_LOCALIZATION_CATALOG.md` + `content/localization/da.source.json` | **Leveret** |
| N-005 | Personalization package spec | `docs/41_PERSONALIZATION_PACKAGE_SPEC.md` | **Leveret kontrakt; private assets produceres senere** |
| N-006 | Human QA/playtest pack | `docs/42_HUMAN_QA_PLAYTEST_PACK.md` + `prototype/m-pre/` | **Leveret; real human execution mangler hvor gate kræver det** |
| N-007 | IP/provenance register | `docs/43_IP_AND_ASSET_PROVENANCE.md` + `source_art/PROVENANCE_INDEX.md` | **Leveret workflow/register** |
| N-008 | Content coverage matrix | `docs/44_CONTENT_COVERAGE_MATRIX.md` | **Leveret** |
| N-009 | Releasekritiske interaction briefs | `design/interactions/` | **Leveret product/player-experience briefs; evidensafhængige valg står åbne** |
| N-010 | Gift/release product flow | `docs/45_GIFT_EXPERIENCE_AND_RELEASE_FLOW.md` | **Leveret product flow** |

## N-009 coverage

`design/interactions/` indeholder nu:

- `PLANNING_TABLE.md`
- `SHELTER_REINFORCEMENT.md`
- `FIRE_START.md`
- `RAVINE_RESCUE.md`
- `STORM_FINALE.md`

`STORM_FINALE.md` dækker storm phase 1–5 inklusive final signal/signal-frame payoff. Det er derfor ikke korrekt længere at oprette separate briefs bare for at tilfredsstille den gamle auditliste.

Fire-start-briefet er en specification/source reference. Det promoverer **ikke** owner-gated PO-044 eller onboarding-fire-start til accepted gift scope.

---

# 2. Non-Unity foundation der siden er landet

Ud over den oprindelige N-00x-kø findes nu machine-readable/product/source/tooling for blandt andet:

- canonical onboarding og Day 3 planning
- issue #8 reconciliation med fire-start som owner-gated node
- after-action presentation
- event presentation og finale contract
- neutral personalization fallback
- expanded source-art inventory og provenance
- actual acquired audio receipts/technical QA
- reproducible 25-source human audition pack
- typed human source-approval gate
- derived-master technical intake + repeated human listening gate
- radio VO 9 cues × 3 takes operator/intake/review/selection/materialization pipeline
- 14 deterministic music candidates + exact-byte reproducibility
- human canonical-family music selection + materialization
- M-Pre evaluator + tamper-evident evidence bundle
- validated non-Unity capability matrix

Se `content/non_unity_capability_matrix.source.json` for den maskinlæsbare pipeline-status.

---

# 3. Faktiske åbne gates

## A. M0b — issue #3 — fysisk device evidence

Claude/Anders-lane.

Mangler fortsat faktisk Quest 2/Quest 3 cross-device evidence, herunder:

- remote head/hands
- compatibility mismatch rejection
- shared two-player state
- 10× Q2↔Q3 coop-object løft uden permanent desync
- 72 Hz minimal network scene
- standby/reconnect
- faktisk compatibility matrix

Synthetic repo-tests må ikke lukke gaten.

## B. M-Pre — issue #7 — faktisk menneskeevidens

Tooling og ready-to-run material er klar. Gaten kræver stadig:

- 3 reelle menneskesessioner
- mindst 2 forskellige testerpar
- ingen gavemodtager som tester
- anonym raw evidence + evaluator + valid evidence bundle

AI/simulation må ikke erstatte disse sessioner.

## C. Fire-start — issue #8 — owner decision

Onboarding og Day 3 er canonical. Kun fire-start-disposition mangler.

Safe default forbliver:

- `implementationAllowed=false`
- ikke accepted gift scope
- 1.012 accepted timer / 439 deferred timer uændret

Anders skal eksplicit vælge remove/skip, minimal onboarding beat eller full PO-044 før scope/totals ændres.

## D. Human audio evidence

Tooling er klar, men følgende kan ikke produceres syntetisk:

- faktisk audition/selection af acquired ambience/Foley
- typed human source approval
- faktisk radio VO recording
- human pronunciation/delivery/semantic/rights review
- human music audition/family selection
- human re-listening på eventuelle derived masters

## E. Unity/Quest physical QA

Draft PR #5/#6 og øvrig Unity/runtime/device acceptance er Claude/device-lane og må ikke promoveres alene på CI.

---

# 4. Åbne produktspørgsmål der kræver evidens

Følgende må fortsat ikke lukkes på AI-vurdering alene:

- OQ-006: skaber effort-marker planning reel diskussion?
- OQ-007/OQ-009: rolleasymmetri / rollepolitik
- OQ-008: randomness fairness
- OQ-010: after-action competition
- endelig scenario-balance og sværhedsgrad
- endelig 35–45 min content density

Placeholder-tal skal forblive testinput, ikke falsk final balance.

---

# 5. Hvad ChatGPT stadig må gøre autonomt

Fortsat tilladt uden at fabrikere evidens:

1. rette dokumenteret contract/status drift
2. forbedre fail-closed validators og deterministic handoff tooling ved konkrete gaps
3. producere source/content kun når en konkret manglende master reducerer implementation ambiguity
4. ingestere og validere faktisk menneske-/device-evidens når Anders/Claude leverer den
5. opdatere roadmap/status atomisk efter faktisk gate-resultat
6. forberede M1 handoff når både M0b og M-Pre er grønne

Undgå:

- nye PRs kun for aktivitetens skyld
- at genoprette allerede leverede N-00x docs
- at kalde synthetic tests human/device evidence
- at promovere acquired/candidate audio uden human gate
- at vælge fire-start scope på Anders' vegne

---

# 6. Definition of done for non-Unity gaveversion-sporet

Non-Unity-sporet kan først kaldes færdigt, når:

1. M-Pre har faktisk GRØNT/RØDT resultat og konsekvenserne er behandlet
2. owner-gated fire-start er disponeret
3. evidensafhængige OQ'er er behandlet på faktisk data
4. nødvendige audio sources/masters har human evidence og korrekt provenance
5. private personalization source er produceret/QA'et når det faktisk skal bruges, eller neutral fallback er den accepterede release-løsning
6. alle produkt/content handoffs til Claude er source-stable og uden skjulte produktbeslutninger
7. status/backlog er reconcilet mod faktisk device/human evidence

Indtil da er den korrekte formulering:

> **Automatable non-Unity foundation: langt fremskreden og hovedsageligt lukket. Real-world evidence/owner gates: fortsat åbne.**
