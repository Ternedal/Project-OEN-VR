# Beslutningspakke DP-001 — PROJEKT ØEN (STRANDET SAMMEN)

> **Placering i repo:** `docs/32_DECISION_PACKAGE_DP-001.md`. ADR-numre tildelt: **ADR-019 til ADR-022**.

## Metadata

- **Dokument-ID:** DP-001
- **Dato:** 2026-08-05
- **Status:** Låst (afventer indarbejdelse i `docs/`)
- **Grundlag:** `claude_PROJECT-OEN-review-2026-08-05.md` (review v1.0, verdict `PROCEED_WITH_BLOCKERS`) + ejerbesvarelse af Q-001 og Q-007
- **Beslutningstager:** Anders (ejer)
- **Indarbejdet:** 2026-08-05 på branch `chore/dp-001-decision-package`.

### Afvigelser fundet ved indarbejdelse

Beslutningspakken blev oprindeligt skrevet uden repo-adgang. Følgende afveg fra antagelserne:

| Antagelse i DP-001 | Virkelighed |
|---|---|
| 14 filer berørt | 38 filer indeholdt Q1-referencer, inkl. GitHub-labels, PR- og issue-templates |
| `docs/` går til 23 | `docs/` går til 31; DP-001 lagt som `docs/32` |
| ADR-numre 020-023 | Højeste eksisterende var ADR-018; tildelt ADR-019 til ADR-022 |
| Ny risiko = R-011 | R-011 var optaget (purchased assets clash); tildelt R-013 |
| `docs/23` er Q1-kompatibilitetsmatrix | `docs/23` er `GITHUB_BOOTSTRAP.md`; ikke Q1-relateret |
| Ikke forudset | `docs/27_SCOPE_FREEZE.md` og `docs/28_ACCEPTED_BASELINE.md` fandtes og krævede opdatering |
| Ikke forudset | Q1-drop rammer også ADR-006, ADR-009, ADR-016 og ADR-018, ikke kun ADR-004 |

Bevidst ikke ændret: `CHANGELOG.md` (historik omskrives ikke bagud - der er tilføjet en ny v2.1-post), `VALIDATION_REPORT.md`, `01_PROMPT_FOR_CLAUDE.md`, `docs/03_CURRENT_MASTER_SPEC_v1.1.md` og `review/`.

---

## 1. Konklusion

Fire beslutninger er låst. Den vigtigste konsekvens er, at **Quest 1-lanen falder helt væk**, og at den binding var den eneste reelle grund til at holde stacken på Unity 2022.3 LTS. Det åbner for en engine-baseline der stadig er understøttet — 2022.3 LTS er ude af standard-support siden maj 2025, og den provider-plugin (Oculus XR Plugin), pakken byggede på, er nu officielt deprecated og planlagt til fjernelse.

Sagt lige ud: **den oprindelige stack var på vej til at være forældet, og Q1-beslutningen var det eneste, der holdt den i live.** Nu hvor den falder, er det billigste tidspunkt at skifte engine-baseline lige nu — der er nul kodelinjer skrevet, så omkostningen er dokumentationsredigering, ikke migration.

Sekundært fund: Photon Fusion 2.1 (stabil siden ~juli 2026) indeholder tre features, der rammer direkte ind i CR-004 og CR-005. Det ændrer ikke beslutningerne, men det ændrer hvad M0/M2-spikes skal afprøve.

| # | Beslutning | Låst valg | Lukker |
|---|---|---|---|
| D-1 | Quest 1 som runtime-target | **DROP_Q1_RUNTIME** — Q1 udgår helt, ikke engang kompatibilitetsdemo | CR-001, CR-008, OQ-001..003 |
| D-2 | Engine/provider-baseline | **Unity 6 LTS (6000.3.x) + Unity OpenXR Plugin + XRI 3.x**, betinget af M0-gate | Følgekonsekvens af D-1 |
| D-3 | Kernehypotese-bevis | **M-Pre indføres som obligatorisk gate før M0** (10–20 t, fladskærm/greybox) | CR-002 |
| D-4 | Primært release-mål | **Gave-slice = afslutning af M5** (1 dag + reduceret storm). Fuld Stormnatten er stretch | CR-003 |

---

## 2. Status

**Statusfarve: Gul.**

Ikke grøn, fordi kernehypotesen (R-003 / OQ-006) stadig er ubevist, og fordi to tekniske spikes (CR-004 coordinator-loss, CR-005 coop-jitter) fortsat kan vælte fundamentet. Ikke rød, fordi ingen af de tilbageværende blockers forhindrer arbejde i at starte — de forhindrer kun binding til fuld contentproduktion.

Reviewets `PROCEED_WITH_BLOCKERS` står ved magt, men blocker-listen er nu kortere: CR-001 er lukket, CR-008 er lukket som følge, og CR-002/CR-003 er konverteret fra "uafklaret risiko" til "planlagt aktivitet".

---

## 3. Beslutningsgrundlag

| Spørgsmål | Svar | Direkte konsekvens |
|---|---|---|
| **Q-001:** Ejer gavemodtageren en Quest 1? | **Nej** — Quest 2 eller nyere | Q1-lanen har ingen modtager. Den er ren teknisk gæld uden aftager → drop |
| **Q-007:** Er der en deadline/anledning? | **Nej, ingen deadline** | Gave-slicen (D-4) skifter begrundelse: den er ikke længere deadline-sikring, men **momentum-sikring**. Se §8 |
| **Q-003:** Er en 1-dags + storm-slice en acceptabel gave? | **Ja** (implicit ved at låse CR-003) | Bekræft eksplicit — hele D-4 hviler på det |

### Om "ingen deadline"

Det er ikke godt nyt, og det bør ikke behandles som om det er. Uden ekstern deadline er den dominerende dødsårsag for et 500+ timers soloprojekt ikke, at man misser en dato — det er, at der aldrig er en dag hvor det er *for sent til at udskyde*. Reviewets R-005 ("gaven bliver aldrig færdig") bliver **mere** sandsynlig uden deadline, ikke mindre.

Derfor gør fraværet af deadline gave-slicen (D-4) *mere* nødvendig, ikke mindre. Se ny risiko R-013 i §8.

---

## 4. Låste beslutninger — ADR-format

Klar til at indsætte i `docs/18_DECISION_LOG.md`. Erstat ADR-numre med næste ledige ID.

---

### ADR-019: Quest 1 udgår som runtime-target

**Status:** Accepteret (2026-08-05)
**Erstatter:** ADR-004 (Q1-kompatibilitet som designbinding) — markér ADR-004 som *superseded by ADR-020*

**Kontekst**
Hele stack-valget i `docs/06` og `docs/08` (Unity 2022.3 LTS, konservativ provider-lane, mulig to-manifest-fork `modern`/`legacy-q1`, tre buildprofiler) var motiveret af ønsket om at bevare Quest 1 som spilbart target. Reviewet identificerede dette som den dominerende tekniske risiko (CR-001) og som kilden til en sandsynlig stackkonflikt (CR-008: sidste Q1-kompatible Oculus-provider v3.3.0 vs. XRI 3.x).

Ejeren har bekræftet, at den tiltænkte gavemodtager **ikke** ejer en Quest 1.

**Beslutning**
Quest 1 udgår som runtime-target. Ikke "reduceret til kompatibilitetsdemo" — **helt ud**. Der bygges ikke Q1-profil, der vedligeholdes ikke Q1-manifest, og Q1 optræder ikke i test- eller devicematrix.

**Begrundelse**
- Lanen har ingen aftager. Den eneste person, gaven er til, har ikke enheden.
- Selv en "kompatibilitetsdemo" koster buildprofil, manifestvedligehold, en COMPAT-testcase og løbende regressionsomkostning — for nul modtagerværdi.
- Bindingen tvang stacken ned på en provider-lane, der nu er deprecated (se ADR-021).
- Reviewet estimerede 15–25 % merarbejde på berørte områder ved at beholde lanen.

**Konsekvenser**
- Positivt: to-manifest-forken forsvinder. Buildprofiler går fra 3 til 2 (Q2/Q3, evt. 1 med device-tier-switch). PO-002/PO-004/PO-007 kan skrives markant ned. OQ-001..003 lukkes ubesvarede. Perf-budgettet får Quest 2 som eneste gulv i stedet for Q1.
- Negativt: projektet kan ikke længere markedsføres/deles som "kører på al Quest-hardware". Irrelevant for en privat gave; relevant hvis v2.0-linjen (offentlig udgivelse) nogensinde aktiveres. Noteres i `docs/14`.
- Uigenkaldelighed: **lav.** Hvis Q1 mod forventning bliver et krav, koster genindførelsen sandsynligvis engine-downgrade. Behandl beslutningen som endelig.

**Alternativer forkastet**
- *Behold fuld Q1-support:* forkastet — ingen modtager.
- *Kompatibilitetsdemo:* forkastet — betaler næsten hele den arkitektoniske pris for en brøkdel af værdien. Det er den værste af de tre muligheder, fordi den fastholder stackbindingen.

---

### ADR-020: Engine-baseline hæves til Unity 6 LTS

**Status:** Accepteret med verifikationsgate (2026-08-05)
**Erstatter:** den del af `docs/06`/`docs/08` der fastlægger Unity 2022.3 LTS

**Kontekst**
2022.3 LTS blev valgt for at bevare Q1-lanen (ADR-020 fjerner nu den begrundelse). Verificeret pr. 2026-08-05:

- Unity 2022.3 LTS er ude af standard LTS-support (2 års vindue fra 30. maj 2023 → udløbet maj 2025). Kun Enterprise/Industry-abonnenter har et tredje år.
- Nuværende Unity-LTS-spor er 6000.0.x og 6000.3.x.
- **Oculus XR Plugin er deprecated og planlagt til fjernelse.** Meta anbefaler Unity OpenXR Plugin fremadrettet.
- Unity OpenXR Plugin kræver **Unity 6 eller nyere** + Meta XR SDK v74+. Oculus XR Plugin dækker Unity 2022+ men kun Meta XR SDK v73 eller ældre, og features fra v74+ er muligvis inkompatible med den.
- Photon Fusion 2.1 understøtter Unity 2021.3.45, 2022.3.45, **6.0.x og 6.3.x**.
- XRI 3.x er den aktuelle toolkit-generation og er den, aktuelle Quest-workflows bygger på.

**Beslutning**
Baseline sættes til **Unity 6 LTS, 6000.3.x** (nyeste patch), med **Unity OpenXR Plugin** som provider, **XRI 3.x** som interaktionslag, URP + Vulkan, og **Photon Fusion 2.1**.

Meta XR Core SDK tilføjes **kun** hvis en konkret feature kræver det (jf. eksisterende princip om ingen Meta Platform SDK i core). Hånd-tracking er ikke i scope for gaveversionen.

**Verifikationsgate (M0, første arbejde)**
Beslutningen er betinget. Bevises inden for M0's første ~8 timer:

1. Tomt Unity 6000.3.x-projekt, URP, Android/Vulkan, bygger og kører på Quest 2.
2. XRI 3.x XR Origin-rig med grab + teleport + snap turn fungerer på device.
3. Fusion 2.1 importeret, Asset Serialization = Force Text, to klienter forbinder i Shared Mode.
4. Tom scene holder 72 Hz stabilt på Quest 2.

**Fallback hvis gaten fejler:** Unity 6000.0.x LTS (også Fusion-understøttet). Kun hvis *begge* Unity 6-spor fejler, overvejes 2022.3.45 — og det skal i så fald noteres som accepteret teknisk gæld med en kendt EOL-provider.

**Konsekvenser**
- `docs/22_SOURCE_REGISTER.md` skal have alle Unity/XR-kilder udskiftet. De eksisterende er indsamlet under en anden præmis.
- Perf-budgetterne i `docs/08` (72 Hz / 13,9 ms, CPU/GPU/draw calls/trekanter) er sat for 2022.3 + Q1-gulv. De er **ikke ugyldige**, men de er nu konservative. Behold dem som startbudgetter; device-profiler forbliver autoritative.
- Unity 6's URP bruger Render Graph. Ingen migrationsomkostning her, da der ikke findes eksisterende render-features. Men custom shader-/render-arbejde senere skal skrives Render Graph-kompatibelt fra start.
- Risiko: Unity 6 har flere bevægelige dele end en moden 2022.3. Modvægten er, at 2022.3-sporet ikke længere får fixes.

**Alternativer forkastet**
- *Bliv på 2022.3 LTS:* forkastet. Uden Q1 er der ingen fordel tilbage, kun en EOL-engine og en deprecated provider.
- *Unity 6000.4 / mainline:* forkastet. Ikke LTS. Et soloprojekt over 6+ måneder skal have et stabilt spor.

---

### ADR-021: M-Pre indføres som obligatorisk gate før M0

**Status:** Accepteret (2026-08-05)

**Kontekst**
Produktets kernehypotese — at allokering af fire markører skaber reel diskussion mellem to spillere frem for administration (R-003, OQ-006) — bevises i den nuværende plan først i M3 (PO-039), efter ~200+ timers platform- og netværksarbejde. Det er den dyreste tænkelige rækkefølge for den vigtigste ukendte.

**Beslutning**
Der indføres en ny milepæl **M-Pre** før M0. Estimat 10–20 t. Indhold: en fladskærms-/papir-/greybox-prototype af planlægnings- og konsekvens-loopet. Ingen VR. Ingen netværk. Ingen Unity-krav — må gerne være fysiske kort og et regneark, hvis det er hurtigere.

**Gate-kriterium (skal være målbart, ikke fornemmelse)**
To testere, der ikke har set designet før, spiller mindst to runder. Gaten er grøn hvis:

1. Testerne **diskuterer indbyrdes** før mindst 3 ud af 4 markørallokeringer, uden at udvikleren forklarer noget.
2. Mindst én tester ytrer uopfordret uenighed eller tvivl om en prioritering.
3. Ved afsløring af konsekvens reagerer mindst én tester på tidligere valg ("vi skulle have…").
4. Ingen af testerne beskriver loopet som administration/bogholderi ved efterspil.

Rødt på 1 eller 3 → **redesign af loopet før alt andet arbejde.** Ikke "vi ser på det i M3".

**Konsekvenser**
- Roadmappet får en ny milepæl foran. Alle øvrige ID'er bevares.
- PO-039 nedskaleres fra "bevis hypotesen" til "genverificér hypotesen i VR".
- OQ-006 og OQ-007 kan lukkes efter M-Pre.
- Hvis M-Pre fejler, er den samlede besparelse potentielt hele M0–M2 (~250 t).

---

### ADR-022: Gave-slice er primært release-mål

**Status:** Accepteret (2026-08-05)

**Kontekst**
Den fokuserede gavevej er estimeret til 500–810 t (~8–13 måneder ved 15 t/uge). Reviewet vurderer R-005 (gaven bliver aldrig færdig) som den mest sandsynlige dødsårsag. Ejeren har bekræftet, at der ingen ekstern deadline er, hvilket øger risikoen for drift.

**Beslutning**
**Afslutningen af M5 defineres som en afsendbar gave (Release 1).** Indhold: 1 spilbar dag + storm-finale reduceret til 3 faser (vind → regn/ild → signal). Storm-fase 3 (skade/dyr) og 4 (kollaps) er stretch.

Fuld 3-dages Stormnatten, art-pass, personalisering og RC (M6–M9) er **stretch oven på en allerede afsendbar gave** — ikke forudsætninger for at give den.

**Gate-kriterium for Release 1**
Spilbar ende-til-ende af to personer i ét sammenhængende forløb uden udviklerindgriben, 72 Hz stabilt på Quest 2 gennem hele stormen, checkpoint-resume virker, og komfortindstillinger er tilgængelige inden for to klik fra pause.

**Konsekvenser**
- `docs/12` og `docs/17` skal have et eksplicit Release 1-mål ved M5, ikke kun en scope-ladder.
- Storm-fase 3 og 4 flyttes til stretch-listen. Content-arbejde til dem påbegyndes ikke før Release 1 er i hus.
- Psykologisk vigtigt: der findes fra M5 en version, der **kan gives**. Alt derefter er forbedring af en gave, der allerede eksisterer.

---

## 5. Verificeret versionsgrundlag pr. 2026-08-05

Alt i denne tabel er slået op i dag. Erstat de tilsvarende rækker i `docs/22_SOURCE_REGISTER.md`.

| Påstand | Status | Kilde |
|---|---|---|
| Unity 2022.3 LTS ude af 2-årig standardsupport (fra 30. maj 2023) | Verificeret | unity.com/releases/2022-lts, docs.unity3d.com 2022.3 manual, endoflife.date/unity |
| Aktuelle Unity LTS-spor: 6000.0.x og 6000.3.x | Verificeret | en.wikipedia.org/wiki/Unity_(game_engine), endoflife.date/unity |
| Fusion 2.1 understøtter Unity 2021.3.45 / 2022.3.45 / 6.0.x / 6.3.x | Verificeret | doc.photonengine.com/fusion/current/getting-started/sdk-download |
| Fusion 2.1 kræver Realtime 5, ikke kompatibel med Fusion 2.0 | Verificeret | doc.photonengine.com/fusion/v2/getting-started/sdk-download |
| Fusion 2.1 tilføjer Forecast Physics (inkl. Shared Mode-support) | Verificeret | blog.photonengine.com/fusion-2-1-stable-release/ |
| Fusion 2.1 tilføjer konfigurerbar Shared Mode tickrate + send rate | Verificeret | blog.photonengine.com/fusion-2-1-stable-release/ |
| Fusion 2.1 tilføjer forbedret Master Client-switching | Verificeret | blog.photonengine.com/fusion-2-1-stable-release/ |
| Fusion kræver Asset Serialization = Force Text | Verificeret | doc.photonengine.com/fusion/current/getting-started/sdk-download |
| Oculus XR Plugin er deprecated og planlagt til fjernelse | Verificeret | developers.meta.com/horizon/documentation/unity/unity-project-setup/ |
| Unity OpenXR Plugin kræver Unity 6+ og Meta XR SDK v74+ | Verificeret | developers.meta.com/horizon/documentation/unity/unity-project-setup/ |
| Oculus XR Plugin dækker Unity 2022+, men kun Meta XR SDK v73 eller ældre | Verificeret | developers.meta.com/horizon/documentation/unity/unity-xr-plugin/ |
| XRI 3.x er aktuel toolkit-generation for Quest via OpenXR | Verificeret | docs.unity3d.com XRI 3.0-manual |
| Præcis nyeste 6000.3.x-patchnummer | **Ikke verificeret** | Tjek Unity Hub ved M0-start |
| Præcis nyeste XRI 3.x-minorversion | **Ikke verificeret** | Tjek Package Manager ved M0-start |
| Fusion 2.1's faktiske Shared Mode-jitter på Quest 2 | **Ikke verificeret — skal måles** | CR-005-spike, M0 |

### Vigtigt sidefund: Fusion 2.1 rammer ind i CR-004 og CR-005

Tre af 2.1-featurene er ikke tilfældigt relevante:

- **Forbedret Master Client-switching.** I Shared Mode *er* Master Client i praksis det, pakken kalder "logical coordinator". Hvis Fusion 2.1's switching er robust nok, bliver CR-004's dyre problem (ægte handover ≈ host-migration i forklædning) muligvis billigt. **Undersøg i M2 — men commit stadig til checkpoint-resume som fallback.** Byg ikke en handover, der afhænger af, at det virker.
- **Konfigurerbar Shared Mode tickrate og send rate.** Direkte håndtag på CR-005. Gør det til en parameter i M0-kassetesten: mål jitter ved mindst to tickrates, så I kender kurven i stedet for ét datapunkt.
- **Forecast Physics med Shared Mode-support.** Potentielt relevant for coop-objektet. **Men:** dette må ikke i sig selv vælte ADR-012 (kinematisk coop-solver). Et to-hånds båret objekt med to autoritative input er stadig et determinisme-problem, ikke et fysikproblem. Evaluér i M0, omgør kun ADR-012 hvis måling viser det.

---

## 6. Ændringer pr. fil

Verificér mod de faktiske filer før udførelse — listen er afledt af reviewet, ikke af filinspektion.

| Fil | Ændring | Kilde |
|---|---|---|
| `00_READ_ME_FIRST.md` | Fjern Q1 fra target-liste. Opdatér stack-linje til Unity 6 LTS / OpenXR / XRI 3.x / Fusion 2.1. Tilføj M-Pre og Release 1 (M5) | D-1, D-2, D-3, D-4 |
| `docs/01_EXECUTIVE_HANDOFF.md` | Definér Release 1 = M5 som gavemål. Justér budgettal (§7) | D-4 |
| `docs/06_TECHNICAL_ARCHITECTURE.md` | Erstat engine/provider/XRI-afsnit. Fjern to-manifest-fork (`modern`/`legacy-q1`) helt. Notér Render Graph-kompatibilitet som krav | ADR-021 |
| `docs/07_MULTIPLAYER_NETWORKING.md` | Opdatér til Fusion 2.1. Tilføj Master Client-switching som M2-undersøgelse. §14 go/no-go gøres kvantitativ (se CR-005) | ADR-021, CR-004, CR-005 |
| `docs/08_PLATFORM_BUILD_PERFORMANCE.md` | Fjern Q1-profil. Buildprofiler 3 → 2. Perf-gulv = Quest 2. Notér budgetter som konservative under ny baseline | ADR-020, ADR-021 |
| `docs/12_PRODUCTION_ROADMAP.md` | Indsæt M-Pre før M0. Markér M5 som Release 1. Flyt storm-fase 3+4 til stretch | ADR-022, ADR-023 |
| `docs/13_TEST_QA_ACCEPTANCE.md` | Fjern Q1 fra devicematrix. Tilføj "maks. to klik fra pause til komfort" som eksplicit gate. Ret CONFLICT-001 og CONFLICT-002 | ADR-020, CR-010 |
| `docs/14_RISK_SCOPE_BUDGET.md` | Genberegn budget. Nedgradér Q1-relaterede risici. Tilføj R-013 (momentum-drift). Notér at Q1-drop lukker "kører på al Quest-hardware" for v2.0-linjen | §7, §8 |
| `docs/17_BACKLOG_AND_MILESTONES.md` | Omskriv PO-002/004/007 (Q1-dele fjernes, erstattes af Unity 6-verifikationsgate). Fjern COMPAT-001 Q1-case. Ret DEV-001 til "M2 løbende, M6 formel" | ADR-020, ADR-021, CR-010 |
| `docs/18_DECISION_LOG.md` | Indsæt ADR-019..022 med rigtige numre. Markér ADR-004 som superseded | §4 |
| `docs/19_OPEN_QUESTIONS.md` | Luk OQ-001, OQ-002, OQ-003 som "bortfaldet, jf. ADR-020". Tilføj Q-008 | ADR-020, §9 |
| `docs/22_SOURCE_REGISTER.md` | Udskift alle Unity/XR/provider-kilder med tabellen i §5 | §5 |
| `docs/23_*` (kompatibilitets-/platformdok., jf. review CR-001) | Fjern eller reducér kraftigt — Q1-kompatibilitetsmatrix er nu tom | ADR-020 |
| `tools/validate_handoff.py` | Kør efter alle ændringer. Skal fortsat give 0 fejl | Verifikation |

---

## 7. Budgetkonsekvens

**Jeg kan ikke give et præcist nyt totaltal uden `docs/14`'s linjeposter.** Nedenstående er afledt af reviewets fragmenter og skal genberegnes.

Kendte tal fra reviewet: 622 t (P0), 500–810 t (fokuseret gavevej), 1.447 t (fuld backlog), stop/go ved 250 t (M0–M2) og 600 t samlet, M5 = 70–110 t.

| Post | Estimat | Grundlag |
|---|---|---|
| M-Pre (nyt) | +10–20 t | Nyt arbejde, ADR-022 |
| Q1-drop, besparelse | −40 til −90 t | Afledt af reviewets "15–25 % på berørte områder": buildprofiler, manifest-fork, COMPAT-Q1, PO-002/004/007. **Usikkert** |
| Gave-slice (M-Pre + M0–M5) | ~340–470 t | Afledt: 250 t (M0–M2, stop/go-tal) + M5 70–110 t + M3–M4 ukendt + M-Pre − Q1-besparelse. **M3–M4 er hullet i beregningen** |
| Ved 15 t/uge | ~23–31 uger ≈ **5,5–7,5 mdr.** | Beregnet af ovenstående |

Sammenlignet med 8–13 måneder for den fokuserede vej er det den reelle gevinst ved D-1 + D-4: **gaven kan eksistere omkring et halvt år tidligere.**

Stop/go-gates bevares uændret: 250 t efter M2, 600 t samlet.

---

## 8. Ny risiko

| ID | Risiko | Alvorlighed | Sandsynlighed | Mitigation |
|---|---|---:|---:|---|
| R-013 | **Momentum-drift.** Ingen ekstern deadline → ingen dag hvor udskydelse er for dyr. Projektet dør stille frem for at fejle synligt | Høj | Høj | (1) Sæt selvvalgt dato for M-Pre: **senest 1. oktober 2026**. (2) Log timer pr. uge; under 5 t/uge i 4 sammenhængende uger = eksplicit revurdering, ikke stiltiende pause. (3) Release 1 ved M5 er det eneste sted, hvor "færdig" må defineres |

Eksisterende R-005 (gaven bliver aldrig færdig) nedgraderes ikke — den mitigeres af D-4, men grundårsagen er nu R-013.

---

## 9. Stadig åbne spørgsmål

| ID | Spørgsmål | Blokerer | Skal besvares senest |
|---|---|---|---|
| **Q-008 (ny)** | Hvilken headset-model præcist? Quest 2, 3 eller 3S? | Perf-budget i `docs/08`. Quest 3 hæver gulvet markant og reducerer pres på R-006 og CR-005 | Før M0-perf-arbejde |
| Q-002 | Samme rum, fjernspil eller begge for Release 1? | `docs/07` — voice, latency-mål, hvor meget reconnect skal prioriteres | Før M2 |
| Q-004 | Kan du få ≥2 eksterne testpar uden at spolere gaven? | CR-007, `docs/13` | Før M-Pre — **M-Pre kræver to testere, der ikke er gavemodtageren** |
| Q-005 | Dansk-only eller engelsk med fra første content-pass? | `docs/19`, M6 | Før M6 |
| Q-006 | Er den personlige finale et krav, eller er neutral ending nok? | M8 — men M8 er nu stretch, så presset er lavere | Før M8 |

**Q-004 er rykket frem og er nu tættest på kritisk.** M-Pre kan ikke køres meningsfuldt af udvikleren alene, og gaten kræver eksplicit testere uden forhåndskendskab. To venner, et regneark og en aften er nok — men de skal findes.

---

## 10. Maskinlæsbar blok

```json
{
  "document_id": "DP-001",
  "date": "2026-08-05",
  "based_on": "review 1.0 (claude_PROJECT-OEN-review-2026-08-05.md)",
  "status": "locked",
  "decisions": [
    {
      "id": "D-1",
      "adr": "ADR-019",
      "closes": ["CR-001", "CR-008", "OQ-001", "OQ-002", "OQ-003"],
      "decision": "DROP_Q1_RUNTIME",
      "summary": "Quest 1 udgaar helt som runtime-target. Ingen kompatibilitetsdemo.",
      "trigger": "Q-001 besvaret: gavemodtager ejer ikke Quest 1.",
      "reversibility": "low",
      "affected_files": ["00_READ_ME_FIRST.md", "docs/06_TECHNICAL_ARCHITECTURE.md", "docs/08_PLATFORM_BUILD_PERFORMANCE.md", "docs/13_TEST_QA_ACCEPTANCE.md", "docs/14_RISK_SCOPE_BUDGET.md", "docs/17_BACKLOG_AND_MILESTONES.md", "docs/18_DECISION_LOG.md", "docs/19_OPEN_QUESTIONS.md"]
    },
    {
      "id": "D-2",
      "adr": "ADR-020",
      "closes": [],
      "decision": "UNITY_6_LTS_BASELINE",
      "summary": "Unity 6000.3.x LTS + Unity OpenXR Plugin + XRI 3.x + URP/Vulkan + Fusion 2.1.",
      "trigger": "Foelgekonsekvens af D-1. Oculus XR Plugin deprecated; Unity 2022.3 LTS ude af standardsupport.",
      "conditional": true,
      "gate": "M0 foerste ~8 t: tom scene bygger og koerer 72 Hz paa Quest 2 med XRI 3.x rig og Fusion 2.1 Shared Mode-forbindelse mellem to klienter.",
      "fallback": "Unity 6000.0.x LTS. Kun ved dobbelt fejl overvejes 2022.3.45 som accepteret teknisk gaeld.",
      "affected_files": ["docs/06_TECHNICAL_ARCHITECTURE.md", "docs/07_MULTIPLAYER_NETWORKING.md", "docs/08_PLATFORM_BUILD_PERFORMANCE.md", "docs/22_SOURCE_REGISTER.md"]
    },
    {
      "id": "D-3",
      "adr": "ADR-021",
      "closes": ["CR-002"],
      "decision": "M_PRE_MANDATORY_GATE",
      "summary": "Ny milepael M-Pre (10-20 t) foer M0: fladskaerms/greybox-test af planlaegningsloopet.",
      "gate": "To eksterne testere, 2 runder: diskussion foer 3 af 4 allokeringer uden dev-forklaring; mindst en ytring af uenighed; reaktion paa afsloeret konsekvens; ingen beskriver loopet som administration.",
      "on_red": "Redesign af kerneloop foer alt andet arbejde.",
      "affected_files": ["docs/04_GAME_DESIGN_DEEP_DIVE.md", "docs/12_PRODUCTION_ROADMAP.md", "docs/17_BACKLOG_AND_MILESTONES.md", "docs/19_OPEN_QUESTIONS.md"]
    },
    {
      "id": "D-4",
      "adr": "ADR-022",
      "closes": ["CR-003"],
      "decision": "GIFT_SLICE_AT_M5",
      "summary": "Afslutning af M5 = Release 1, en afsendbar gave. 1 dag + storm reduceret til 3 faser.",
      "trigger": "Q-007 besvaret: ingen deadline, hvilket oeger momentum-risiko.",
      "stretch": ["storm fase 3 (skade/dyr)", "storm fase 4 (kollaps)", "M6-M9 fuld Stormnatten, art, personalisering, RC"],
      "affected_files": ["docs/01_EXECUTIVE_HANDOFF.md", "docs/12_PRODUCTION_ROADMAP.md", "docs/14_RISK_SCOPE_BUDGET.md", "docs/17_BACKLOG_AND_MILESTONES.md"]
    }
  ],
  "still_open": [
    {"id": "CR-004", "status": "open", "note": "Coordinator-loss. Undersoeg Fusion 2.1 Master Client-switching i M2, men commit til checkpoint-resume som fallback."},
    {"id": "CR-005", "status": "open", "note": "Coop-objekt-jitter. M0-kassetest skal vaere kvantitativ og maale ved mindst to Shared Mode-tickrates."},
    {"id": "CR-006", "status": "open", "note": "90s live-reconnect udskudt til v1.1. Gave-MVP: pause + checkpoint-resume."},
    {"id": "CR-007", "status": "escalated", "note": "Eksterne testere er nu paakraevet tidligere end foer, da M-Pre-gaten kraever dem."},
    {"id": "CR-009", "status": "open", "note": "IP-review som haardt gate paa v2.0-linjen. Uaendret."},
    {"id": "CR-010", "status": "open", "note": "CONFLICT-001 og CONFLICT-002 rettes som del af §6."}
  ],
  "new_risks": [
    {"id": "R-013", "summary": "Momentum-drift uden ekstern deadline.", "severity": "high", "likelihood": "high", "mitigation": "M-Pre senest 2026-10-01; timelog; under 5 t/uge i 4 uger udloeser revurdering."}
  ],
  "new_questions": [
    {"id": "Q-008", "question": "Hvilken headset-model praecist: Quest 2, 3 eller 3S?", "blocks": "docs/08 perf-budget"}
  ],
  "budget_estimate": {
    "gift_slice_hours": [340, 470],
    "confidence": "low",
    "note": "Afledt af reviewets fragmenter. M3-M4 er ikke daekket af kendte tal. Skal genberegnes mod docs/14 linjeposter.",
    "at_15h_per_week_months": [5.5, 7.5]
  }
}
```

---

## 11. Næste konkrete handlinger

1. **Bekræft Q-003 eksplicit** — er en 1-dags + 3-fase-storm-slice en gave, du faktisk vil give? Hele D-4 hviler på et ja.
2. **Besvar Q-008** — præcis headset-model. Ét spørgsmål, ændrer hele perf-budgettet.
3. **Indsæt ADR-019..022 i `docs/18`** med rigtige numre; markér ADR-004 som superseded.
4. **Kør redigeringslisten i §6** mod repoet, ét dokument ad gangen.
5. **Kør `tools/validate_handoff.py`** — skal fortsat give 0 fejl.
6. **Find to testere til M-Pre** (Q-004). Dette er den reelle kritiske sti nu.
7. **Book M-Pre. Senest 1. oktober 2026.**

---

## 12. Notion-opdatering

```
PROJEKT ØEN — Statusopdatering 2026-08-05

Status: Gul
Fase: Pre-M0, beslutningspakke DP-001 låst

Låste beslutninger:
- Quest 1 droppet som runtime-target (ADR-020)
- Engine-baseline hævet til Unity 6 LTS 6000.3.x + Unity OpenXR Plugin + XRI 3.x + Fusion 2.1 (ADR-021, betinget af M0-gate)
- Ny milepæl M-Pre indført før M0: greybox-test af kerneloop (ADR-022)
- Release 1 defineret som afslutning af M5 — 1 dag + 3-fase storm (ADR-023)

Effekt: gavemål flyttet fra ~8-13 mdr. til ~5,5-7,5 mdr. (estimat, lav konfidens)

Kritisk sti: to eksterne testere til M-Pre (Q-004)
Deadline sat: M-Pre kørt senest 1. oktober 2026
Ny risiko: R-013 momentum-drift (høj/høj)

Åbne blockers: CR-004 (coordinator-loss, M2), CR-005 (coop-jitter, M0)
Åbne spørgsmål: Q-002, Q-004, Q-005, Q-006, Q-008
```
