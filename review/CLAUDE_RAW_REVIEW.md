# Claude review — PROJECT ØEN

## Metadata

- **Reviewer/model:** Claude (Opus 5)
- **Dato:** 2026-08-06
- **Package version:** 2.0 (commit `cfe155f`)
- **Review version:** 1.0
- **Grundlag:** Fuld gennemlæsning af `docs/01`–`docs/31`, `schemas/`, `examples/`, `review/`, `.github/`, `tools/`. `python tools/validate_handoff.py` kørt lokalt: **0 errors**. Backlogtabellen i `docs/17` er parset og summeret programmatisk (tal gengivet nedenfor er beregnede, ikke afskrevne).

### Epistemisk mærkning brugt i dette review

- **[VERIFICERET]** — bekræftet mod officiel dokumentation eller ved kørsel/beregning i denne session.
- **[ANTAGELSE]** — kvalificeret vurdering baseret på erfaring; ikke bevist her.
- **[KRÆVER MÅLING]** — kan kun afgøres på fysisk hardware.

---

## A. Executive verdict

**`PROCEED_WITH_BLOCKERS`**

1. Produktidéen holder. Den er original, den har en ærlig kernefantasi, og "to markører pr. spiller + forsinkede konsekvenser + fysisk udførelse" er et reelt designsvar på hvorfor det skal være VR og ikke et brætspil.
2. Dokumentationskvaliteten er over niveauet for et hobbyprojekt. Authority-model, save-model og kinematic coop-fysik er valgt rigtigt og af de rigtige grunde.
3. Blockerne er **ikke** i produktet. De er i rækkefølge, platformvalg og estimatstyring.
4. Den alvorligste: M0's gate kan ikke bevises af M0's opgaver. Alt netværksarbejde ligger i M2, så projektets største dræberrisiko (Quest 1-lanen) får først svar efter op til 250 timer.
5. Den næstalvorligste: Quest 1-lanen er beskrevet som en pakkeversionsforskel. Den er reelt et andet XR-backend — og det backend er officielt deprecated og på vej ud.
6. Editorvalget er begrundet med en LTS-supportpåstand, der ikke gælder for en Personal/Pro-licens.
7. Estimatet 500-810 timer er et top-down-tal. Det er ikke udledt af backloggen, og der findes ingen scope-markering, der gør det sporbart.
8. Ingen af de fire ovenstående kræver redesign af spillet. De kræver, at M0 skæres om og at tre tekniske antagelser rettes, før første kodelinje.
9. Anbefalet handling: behandl CR-001 til CR-006 i response matrix, opdatér M0, og kør derefter M0 som planlagt.
10. Der er ingen grund til at STOP'e eller redesigne produktet.

---

## B. De ti vigtigste fund

| ID | Alvor | Område | Fund | Konsekvens | Anbefaling | Berørte filer |
|---|---|---|---|---|---|---|
| CR-001 | BLOCKER | Roadmap/sekvens | M0's deliverables og gate kræver Photon-session, head/hands-replication og coop-kasse. Alle disse opgaver ligger i M2 i backloggen. M0's 12 items (89 t, heraf 41 t P0) er kun Unity/build/XR. | Den største dræberrisiko (R-001) får først svar efter op til 250 t. Stop/go-beslutningen er reelt flyttet fra M0 til M2. | Flyt PO-017, PO-018, PO-019, PO-020, PO-022 og PO-025 til M0. Re-baselinér M0 til ca. 150-175 t. Alternativt: opdel i M0a (buildlane) og M0b (netværkslane) med én samlet gate. | `docs/12`, `docs/17`, `docs/14`, `docs/06` §3, `docs/30` |
| CR-002 | BLOCKER | Platform/XR | Quest 1-lanen beskrives som pakkedivergens ("kun XR/platformpakker må divergere"). Q1 kræver [VERIFICERET] Oculus-provider ≤ v3.x, mens Q2/Q3-planen er OpenXR-provider. Det er to forskellige XR-backends, ikke to versioner. Meta dokumenterer desuden Oculus XR Plugin som deprecated og planlagt fjernet. | `ProjectOen.Interaction` skal reelt forkes: forskellige interaction profiles, input-bindings og rig-opsætning. Det er langt mere end de 15-25 % merarbejde, `docs/01` estimerer. | M0 skal teste **OpenXR-provider på Quest 1 først**. Q1 har en OpenXR-runtime på OS v50. Virker det ikke, er det exit-trigger for Q1-lanen — ikke startskuddet til en Oculus-provider-fork. | `docs/06` §3, `docs/08` §2-3, `docs/14`, ADR-004, ADR-007 |
| CR-003 | HIGH | Engine/stack | ADR-006 og `docs/01` begrunder Unity 2022.3 LTS med "fortsat 3-årige LTS-patches". [VERIFICERET] Unitys egen manual: to års support for Personal og Pro; tredje år er kun Enterprise/Industry. 2022.3 udkom juni 2023 → Personal/Pro-support udløb medio 2025. Patchen fra 2026-05-06 i `docs/22` ligger i det Enterprise-only tredje år. | Et 8-13 måneders forløb startes august 2026 på en editor, der ikke længere patches på den relevante licens. Ingen platform- eller sikkerhedsrettelser. Nye XRI-/Fusion-versioner og assets sigter mod Unity 6. | Gør editorvalget afhængigt af CR-002's resultat. Virker OpenXR på Q1 → byg på Unity 6 LTS. Virker det ikke → byg alligevel på Unity 6 LTS og lad Q1 blive en frossen sidebuild. Lås ikke hele projektet til 2022.3 for en enhed med ~0 brugere. | `docs/01`, `docs/06` §2, `docs/22`, ADR-006 |
| CR-004 | HIGH | Platformpolitik | [VERIFICERET] Quest 2 udgik af salg ultimo 2024, får feature-opdateringer til december 2026 og kritiske opdateringer til december 2027. Projektets eget estimat (15 t/uge) lander gaveversionen tidligst medio 2027. | Som performancegulv er Q2 stadig et ærligt og konservativt anker — det er hardwaren i huset. Men `docs/01` kalder den "reelt målheadset" uden at nævne EOL, og v2.0-planen om offentlig udgivelse hviler på et dødt device. | Behold Q2 som performancegulv. Ret formuleringen i ADR-003 og `docs/08` til "performancegulv, EOL dec. 2027". Sæt Quest 3S som antaget baseline for alt efter v1.0. Billig rettelse, forhindrer en dyr langtidsbeslutning. | `docs/01`, `docs/08` §1, `docs/12` (v2.0), ADR-003 |
| CR-005 | HIGH | Estimat/scope | [VERIFICERET, beregnet] Backloggen: 108 items, 1447 t, P0 = 44 items/622 t. Roadmap-intervaller vs. backloggens milepælssummer: M2 45-70 t vs. 173 t · M3 55-85 t vs. 260 t · M6 70-115 t vs. 214 t · M7 55-90 t vs. 160 t. Kun M0 passer (60-100 vs. 89). Der findes ingen scope-kolonne; alle 108 items står `Not Started` uden ind/ud-markering. | Tallet 500-810 t kan hverken forsvares eller spores. Planen læser som om scopekontrol findes, mens hver eneste opgave nominelt stadig er med. | Tilføj kolonnen `Gaveversion` (In / Out / Defer) i `docs/17`. Vælg det itemsæt, der summerer til målet. Lad derefter roadmap-intervallerne **være** summen af de valgte items i stedet for et parallelt tal. | `docs/12`, `docs/14`, `docs/17`, `docs/01` |
| CR-006 | HIGH | Datakontrakt | `docs/10` beskriver felter, skemaerne ikke har: `ScenarioDefinition` mangler "supported build protocol" og "action catalog"; `EventDefinition` mangler `cooldown`. Alle skemaer har `additionalProperties: false`. [VERIFICERET] `validate_handoff.py` melder 0 fejl alligevel, fordi `initialState`, `sharedState` og `winRules` er utypede frie objekter. | Første implementerings-PR knækker enten CI eller afviger stiltiende fra `docs/10`. Valideringen giver falsk tryghed: den beviser at filerne er velformede, ikke at kontrakten er komplet. | Tilføj de manglende felter før kode. Typificér som minimum `winRules`/`loseRules`. Tilføj en validatorregel: hvert ID i `phases[].actions` skal findes i action-kataloget. | `docs/10`, `schemas/scenario.schema.json`, `schemas/event.schema.json`, `tools/validate_handoff.py` |
| CR-007 | HIGH | Design-gate | "Begge aktive" er produktets vigtigste løfte, men grænsen står tre steder med to værdier (12 sek. i `docs/04` §8, 20 sek. i `docs/02` og `docs/05`), og målemetoden er manuel observation (UX-002). | Projektets centrale designgate kan ikke afgøres objektivt og vil blive afgjort af hukommelse efter en playtest. | Instrumentér det. Event-journalen i `docs/06` §6 har allerede `ActionResolved` og `CompleteInteractionStepCommand`. Log aktive frames pr. spiller pr. handling og udskriv en rapport pr. run. Anslået 6-10 t. Vælg derefter én passivitetsgrænse. | `docs/02`, `docs/04` §8, `docs/05`, `docs/13` UX-002 |
| CR-008 | MEDIUM | Content/proces | Build fejler ved manglende localization key (`docs/10`), alle vigtige replikker skal have undertekster (`docs/09`), og `docs/19` spørger om dansk er eneste launchsprog. [VERIFICERET] Ingen af backloggens 108 items nævner lokalisering, sprog eller underteksttekstning. | Arbejdet findes, men er usynligt. Det dukker op som uplanlagt vækst i M6/M8. | Skriv en ADR: "Dansk er eneste sprog i gaveversionen; nøglestruktur på plads, ingen andet sprog." Tilføj ét backlog-item til nøgletabel + underteksttekstning. | `docs/10`, `docs/09`, `docs/17`, `docs/19` |
| CR-009 | MEDIUM | Netværk/drift | Reconnect-vinduet er foreslået til 90 sekunder, og standby behandles som disconnect. [ANTAGELSE] Quest går i standby få sekunder efter aftagning og kan tabe Wi-Fi i dybere sleep. 90 sekunder dækker ikke "jeg tog headsettet af for at åbne døren" — hvilket er præcis dét, der sker i en dagligstue. | Den hyppigste virkelige afbrydelse rammer den dyre sti (checkpoint-resume) i stedet for den billige. | [KRÆVER MÅLING] Mål faktisk standby → netværkstab på Q2/Q3 i M2 og sæt vinduet efter data. Gør derudover checkpoint-resume til den *gratis* standardvej, ikke undtagelsen. | `docs/07` §10, `docs/13` DEV-001 |
| CR-010 | MEDIUM | Proces | `docs/24` kræver disposition af alle BLOCKER/HIGH, indarbejdelse i specs + ADR-log og opdateret M0-scope, før implementering må starte. Det er reelt arbejde uden et eneste backlog-item. | Gaten kan ikke lukkes af dokumenterne selv, og arbejdet bliver usynligt i timeregnskabet. | Tilføj `PO-000` "Behandl review og opdatér baseline" som M0/P0, est. 8-16 t. | `docs/17`, `docs/24` |

---

## C. Detaljeret review

### 1. Produkt og spilleroplevelse

Spillerløftet i `docs/01` er det bedste enkeltstående afsnit i pakken: det siger præcis hvad oplevelsen er, og det er testbart. Målgruppen er to konkrete mennesker, og det er en styrke — ikke en svaghed — fordi det gør "Definition af succes" reelt afgørbar.

To ting bør skærpes:

**Den personlige finale er sat op til at bære for meget.** `docs/05` giver den 90 sekunder og kalder den udskiftelig, hvilket er rigtigt. Men `docs/14` R-010 identificerer selv risikoen ("kitschet"), og gaveversionens hele formål hviler på den. [ANTAGELSE] Risikoen er ikke at den bliver kitschet — det er, at den bliver *afkoblet*: 40 minutters overlevelsesspil efterfulgt af et fotoalbum. Modtræk: lad ét personligt element optræde **tidligt og funktionelt** (fx en genstand i kassen på stranden, der bruges i gameplay), så finalen lukker en løkke i stedet for at åbne en ny tone.

**"Ingen sabotage" er rigtigt, men konkurrencedelen er underspecificeret.** `docs/04` §11 lover efterspils-titler ("Kaosagenten"), som kræver telemetri, der ikke findes i datamodellen. Enten defineres de målte størrelser i `ScenarioState` nu, eller også skæres titlerne til 2-3 stykker, der kan udledes af eksisterende felter.

### 2. Gameplay-loop og systemdesign

Handlingsøkonomien er sund. Fire markører mod flere værdifulde handlinger end markører er den klassiske og korrekte konstruktion, og reglen "hvis der findes ét oplagt korrekt svar hver dag, er planlægningen mislykket" er den rigtige test.

**Udfaldsformlen i §9 er den svageste del af designet.** `Preparation + ToolQuality + RoleBonus + PhysicalExecution + Cooperation - Injury - Weather - EventRisk` har otte led uden vægte, skala eller tærskler. [ANTAGELSE] Med otte additive led ender resultatet i praksis omkring midten, og "Delvis succes med omkostning" bliver det næsten altid observerede udfald — hvilket læses som "spillet straffer os uanset hvad". Anbefaling: reducér til fire led før første prototype (Preparation, PhysicalExecution, Cooperation, Penalty), og fastlæg tærskler numerisk i scenariodata frem for i kode. Det er også nemmere at balancere med to testere end otte parametre er.

**Fail-forward-princippet er stærkt og bør beskyttes** i scope-ladderen. Det står ikke i "der skæres ikke først i"-listen i `docs/12`, men burde: uden fail-forward bliver spillet et retry-spil.

### 3. Scenarioet Stormnatten

Dramaturgien holder, og beat-strukturen er stram. Tidsbudgettet (32-48 min. i sum mod et mål på 30-45) er ærligt regnet.

**Dag 2 er overbelastet.** Seks nye handlinger introduceres samtidig med kløftsekvensen og stormvarslet, i et 10-12 minutters vindue. [ANTAGELSE] Det er dér, første eksterne playtest vil vise beslutningslammelse. Modtræk: flyt to af de seks handlinger (fx "Find urter" og "Behandl skade") til at blive låst op af en hændelse frem for at være tilgængelige fra morgenstunden. Det koster ingen kode — kun scenariodata.

**Nat 2-forgreningerne er den bedste mekanik i pakken** og bør være dét, M4 beviser. Kæden `åben mad → SCENT_HIGH → dyretrussel nat 2` er kort nok til at kunne forstås og lang nok til at føles kausal.

**`EVT_DISTANT_SMOKE_001` bør ud af MVP.** Den er eksplicit markeret som teaser uden gameplaygren. I en gaveversion, der spilles 2-4 gange, er en uindfriet teaser et løfte, der aldrig indfries. Flyt til v1.5.

### 4. VR-interaktion, komfort og onboarding

Dette kapitel er stort set uangribeligt: teleport + snap turn som default, ingen knælen, 0,6-1,6 m rækkevidde, undertekster, håndvalg, haptik med intensitetsindstilling. Onboarding uden separat tutorialrum er den rigtige beslutning.

To huller:

**Kalibrering af siddende/stående nævnes i `docs/02`, men interaktionsdesignet antager reelt stående.** Tohåndsløft af en tung kasse med "bred stabiliseringszone" er en anden bevægelse siddende. [KRÆVER MÅLING] Afklar i M1, om siddende er fuldt understøttet eller kun "ikke blokeret".

**Der er ingen defineret adfærd, hvis den ene spiller sidder og den anden står.** Højdeforskellen påvirker delte snap-zoner på coop-objektet. Det er et konkret testcase, der mangler i `docs/13`.

### 5. Multiplayer og authority

Det stærkeste tekniske kapitel. Tre beslutninger er rigtige og velbegrundede:

- **Fusion 2 Shared Mode til to klienter** — korrekt valg. Host/server-topologi ville koste prediction/resimulation-kompleksitet uden gevinst ved to spillere.
- **Kinematic coop-solver frem for netværksrigidbody** (ADR-012) — den enkelt vigtigste tekniske beslutning i pakken. Rå replikeret fysik mellem to VR-klienter er dét, der plejer at dræbe den slags projekter.
- **Ingen Meta Platform SDK i kerneflowet** (ADR-009) — [VERIFICERET] Metas egen udviklervejledning siger, at multiplayer-services kun understøttes mellem klienter med samme SDK-version, og at en v50-app på Quest 1 ikke kan spille med en v51-app på Quest 2. Ved at lægge sessionen på Photon omgår projektet præcis den fælde. Det er korrekt analyseret i `docs/08` §2.

**Det uafklarede punkt er coordinator-tabet.** `docs/07` §3 siger "forsøges kontrolleret overdragelse", OQ-005 kalder det åbent, og `docs/12` lægger prototypen i M2. Med to spillere er der ingen tredje klient at overdrage til: hvis coordinator forsvinder, er den anden klient per definition ny coordinator eller også er sessionen slut. Anbefaling: skær beslutningen nu — **ingen live handover**. Ved coordinator-tab: pause, checkpoint-resume, ny session. Det er én kodesti i stedet for to, og checkpoint-stien skal alligevel bygges og testes. Det sparer PO-023 (12 t) ned til en brøkdel og fjerner en hel klasse af desync-fejl.

**Idempotens via command-ID er rigtigt tænkt**, men `SAVE-001` er den eneste test af det. Tilføj en test for duplikeret `ConfirmPlanCommand` ved samtidig reconnect.

### 6. Unity/XR/Quest 1-2-3-strategi

Se CR-002, CR-003, CR-004. Uddybning af evidensgrundlaget:

**[VERIFICERET]** Unitys manual (XR packages) angiver, at Unity understøtter udvikling for Meta Quest 2, 3, 3S og Quest Pro — Quest 1 står ikke på listen. Samme side: version 4+ af Oculus-provideren understøtter ikke længere Quest 1-udvikling, og en tidligere version skal bruges. Oculus XR Plugin 4.x-changelogen bekræfter, at Quest 1 blev fjernet som target device i settings og manifest, og at v51-plugins ikke understøtter Quest 1.

**[VERIFICERET]** Metas egen Unity-dokumentation (opdateret 2026) angiver Oculus XR Plugin som deprecated og planlagt til fjernelse, med Unity OpenXR Plugin som anbefalet erstatning.

**[VERIFICERET]** Quest 1's sidste OS-udgivelse var v50 (februar 2023), sikkerhedsopdateringer sluttede august 2024, og butikken lukkede for nye og opdaterede Quest 1-apps. Sideload er derimod ikke blokeret — projektets sideload-only-plan for Q1 er derfor grundlæggende farbar.

**[KRÆVER MÅLING]** Om Unitys OpenXR-provider producerer en APK, der faktisk starter og tracker på Quest 1's frosne v50-runtime, er ikke dokumenteret nogen steder og kan kun afgøres på enheden. **Det er det eneste eksperiment, der betyder noget i M0.** Rækkefølgen bør være:

1. Byg tom OpenXR-scene, installér på Q1. Starter den og tracker den? → Q1-lanen er en pakkeprofil, og hele planen holder.
2. Starter den ikke → Q1 kræver Oculus-provider ≤3.x, og dermed en anden interaction-stak. Udløs exit-kriteriet i `docs/14` med det samme. Byg Q1 som frossen demo, ikke som en lane i hovedprojektet.

Det bør stå eksplicit i `docs/30`, som i dag blander bygge- og netværksbevis sammen uden at pege på det afgørende eksperiment.

**Vulkan/GLES3-spiket (OQ-003) er sekundært** og bør først køres, når trin 1 ovenfor er afgjort. Falder Q1-lanen, forsvinder halvdelen af spikets begrundelse.

### 7. Performance og assetpipeline

Budgetterne er realistiske og i den rigtige ende af konservative. 72 FPS ≈ 13,9 ms er korrekt, og opdelingen CPU < 8 ms typisk / < 11 ms worst-case er en fornuftig hobbyprojekt-margin. <100 draw calls og <500k trekanter er stramt, men opnåeligt for stiliseret art med bagt lys.

**Ét reelt hul:** stormen er beskrevet som "primært skybox, fog, audio, material animation og lokale overlays" — men `docs/05` fase 4 kræver et delvist kollaps af en central konstruktion med tohånds-stabilisering og snap-reparation. Det er et gameplay-tungt, animeret, netværkssynkroniseret event oven i stormens VFX-peak. [ANTAGELSE] Det er dér, Quest 2's frame budget knækker, ikke i regnpartiklerne. Anbefaling: byg kollapssekvensen som prototype i M5 *før* art pass, og mål den isoleret — den fortjener sit eget PERF-testcase ved siden af PERF-001.

**Foveated rendering** er korrekt håndteret ("aldrig som eneste vej til 72 Hz").

### 8. Save, reconnect, build og distribution

Save-modellen er rigtig: checkpoint frem for kontinuerlig fysik-save, atomisk skrivning via temp → checksum → rename, forrige checkpoint bevaret. Adskillelsen af `NetworkProtocolVersion`, `SaveSchemaVersion` og `ContentVersion` fra semver er præcis den slags detalje, der plejer at mangle.

**Checksummen er udefineret.** `savegame.schema.json` kræver feltet, men intet dokument siger, hvad der indgår i den, eller hvilken algoritme der bruges. Uden en defineret dækning er checksummen dekoration. Definér: algoritme, felt-rækkefølge, og at `checksum` selv er ekskluderet. Det er 30 minutters skrivearbejde nu og en umulig fejlsøgning senere.

**`revision` er valgfri i skemaet**, men `docs/07` §11 siger, at scenariestate har en monotont voksende revision, og resync-logikken afhænger af den. Gør den påkrævet.

**Signering:** PO-096 dækker keystore-backup, men `docs/15` kræver samme signing identity for opdateringer på samme kanal. For en gaveversion, der skal patches efter aflevering, er tabt keystore lig med "modtagerne skal afinstallere og miste deres save". Det bør stå eksplicit i `docs/15` som en P0-konsekvens, ikke kun som en backup-opgave.

### 9. QA og release gates

Testmatricen er god, og de otte kritiske testcases rammer de rigtige steder. `NET-001` (same-frame grab), `SAVE-001` (delayed event præcis én gang) og `CONTENT-001` (manglende personlig asset) er alle klassiske fejlkilder.

**Manglende testcases:**

- **Blandet siddende/stående** på coop-objektet (jf. afsnit 4).
- **Klokkeskævt build:** Q1 med gammelt content hash mod Q3 med nyt — `docs/07` §13 nævner "Mismatched scenario hash", men det er ikke et nummereret testcase i `docs/13`/`docs/17`.
- **Fuld disk / afbrudt skrivning under checkpoint.** Den atomiske skrivestrategi er kun værd noget, hvis den er testet.

**"Brug ikke kun udvikleren og kæresten som QA; mindst 2 eksterne par før release"** er den mest værdifulde sætning i hele QA-planen. Den bør flyttes op i `docs/12` som en eksplicit M6-gate, ikke stå i en protokolsektion.

### 10. Roadmap, estimering og scope

Se CR-001 og CR-005. Beregnede tal til response matrix:

| Milepæl | Roadmap-interval | Backlog-sum (alle) | Backlog-sum (P0) | Items |
|---|---|---:|---:|---:|
| M0 | 60-100 | 89 | 41 | 12 |
| M1 | 35-55 | 89 | 14 | 11 |
| M2 | 45-70 | 173 | 139 | 14 |
| M3 | 55-85 | 260 | 112 | 20 |
| M4 | 40-65 | 156 | 86 | 11 |
| M5 | 70-110 | 130 | 88 | 6 |
| M6 | 70-115 | 214 | 28 | 12 |
| M7 | 55-90 | 160 | 24 | 7 |
| M8 | 30-50 | 86 | 8 | 9 |
| M9 | 40-70 | 90 | 82 | 6 |
| **Sum** | **500-810** | **1447** | **622** | **108** |

Roadmap-intervallerne summerer korrekt til 500-810, og P0 summerer korrekt til 622. De to modeller er hver for sig konsistente — men der er ingen afbildning mellem dem. M3 er det tydeligste eksempel: 20 items, 260 timer, mod et interval på 55-85.

**Scope-ladderen er god, men mangler ét trin i toppen:** "Quest 1-lanen" bør stå som skærepunkt nr. 1 eller 2, ikke kun som et exit-kriterium gemt i `docs/14`. Det er den dyreste enkeltstående valgfrie ting i projektet.

**Tidsbudgettets stop/go efter 250 t er godt tænkt**, men bliver først meningsfuldt, når CR-001 er rettet. I dag rammer 250-timers-grænsen præcis midt i M2 — altså lige omkring det tidspunkt, hvor svaret på Q1-spørgsmålet endelig foreligger. Det er den værst tænkelige placering for en stop/go.

### 11. IP, privacy og øvrige risici

**IP-håndteringen er forbilledlig.** ADR-001, R-009 og de eksplicitte forbud mod kopieret regeltekst, kort og ikonografi er den rigtige tilgang. Én tilføjelse: "inspireret af"-grænsen bør have en konkret operationel test, ikke kun en hensigt. Foreslået formulering til `docs/14`: *"Ingen mekanik, tekst eller ikon må kunne genkendes af en spiller, der kender forlægget, som direkte oversættelse. Ved tvivl: omdøb og omform."*

**Privacy er godt håndteret.** Ingen voice recording, personlige assets uden for repo, neutral fallback obligatorisk, logs uden navne. [VERIFICERET] `validate_handoff.py` har allerede et check for private assets og signeringsmateriale i repoet, og det består.

**Én overset risiko:** Photons App ID ligger i buildet (korrekt, det er ikke hemmeligt), og join codes er 5-6 tegn. Med en privat gavebuild er trusselsmodellen reelt nul. Men `docs/06` §13 lover, at "offentlig version kræver stærkere entitlement/session policy" — det er en fremtidig arkitekturændring, der er nem at glemme. Notér den som en ADR med `Proposed`-status nu, så den ikke opdages under v2.0-planlægningen.

**[VERIFICERET] Budgettet holder på Photon-siden:** Fusion har en gratis 100 CCU-plan, der dækker både udvikling og kommerciel brug for én app. For to samtidige spillere er omkostningen 0 kr. Posten "Unity/Photon under hobby-/lav CCU-grænser: 0-1.500 kr." kan sættes til 0 kr., medmindre der købes en Unity-licens.

---

## D. Konfliktliste

| ID | Kilde A | Kilde B | Konflikt | Anbefalet autoritet |
|---|---|---|---|---|
| CONFLICT-001 | `docs/12` M0 (deliverables + gate: Photon, head/hands, coop-kasse, 10 løft) og `docs/06` §3 | `docs/17` (PO-017–PO-023, PO-025 er alle M2) | M0's gate kan ikke bevises af M0's opgavesæt. To dokumenter beskriver to forskellige M0'er. | `docs/12` er autoritativ — M0 **er** platform- *og* netværksspiket. `docs/17` rettes ved at flytte items. |
| CONFLICT-002 | `docs/04` §8: maksimal passiv periode 12 sekunder | `docs/02` og `docs/05`: ingen sekvens med >20 sekunders passivitet | To forskellige grænseværdier for projektets vigtigste designgate. | `docs/04` §8 (12 s) som **designregel**; 20 s som **testgrænse** i `docs/13`. Skriv forskellen eksplicit, eller vælg én værdi. |
| CONFLICT-003 | `docs/10`: `ScenarioDefinition` har "supported build protocol" og "action catalog"; `EventDefinition` har "priority/cooldown" | `schemas/scenario.schema.json` og `schemas/event.schema.json` med `additionalProperties: false` | Skemaerne mangler felter, som `docs/10` kræver, og er samtidig lukkede for tilføjelser. Implementering vil bryde CI. | `docs/10` er autoritativ — skemaerne opdateres. |
| CONFLICT-004 | `docs/01` og ADR-006: "Unity 2022.3 LTS ... modtager fortsat 3-årige LTS-patches"; `docs/22` citerer patch fra 2026-05-06 | Unitys officielle LTS-politik: to år for Personal/Pro, tredje år kun Enterprise/Industry | Begrundelsen for editorvalget hviler på en supportgaranti, der ikke gælder projektets licenstier. | Unitys dokumentation er autoritativ. `docs/01`, ADR-006 og `docs/22` rettes. |
| CONFLICT-005 | `docs/01`: "Kritisk P0-sti ... ca. 620 timer" | `docs/14` og beregnet backlogsum: 622 timer | Mindre talafvigelse, men i et dokument der bruges som tracker. | Beregnet sum (622) er autoritativ. Ret `docs/01`. |
| CONFLICT-006 | `docs/07` §11: scenariostate har monotont voksende revision, resync afhænger af den | `schemas/savegame.schema.json`: `revision` er valgfri | Et felt, resync-logikken afhænger af, er ikke påkrævet i kontrakten. | `docs/07` er autoritativ. Gør `revision` påkrævet. |

---

## E. Anbefalet ændringspakke

### Skal ændres før kode

1. **Skær M0 om** (CR-001). Flyt PO-017, PO-018, PO-019, PO-020, PO-022, PO-025 til M0. Re-baselinér M0 til ca. 150-175 t. Opdatér `docs/30` tilsvarende.
2. **Omdefinér Q1-eksperimentet** (CR-002). `docs/30` skal eksplicit sige: OpenXR-provider på Quest 1 testes **først**, og et negativt resultat udløser exit-kriteriet i `docs/14` — det starter ikke en Oculus-provider-fork.
3. **Ret editorbegrundelsen** (CR-003). ADR-006 omskrives; editorvalget gøres afhængigt af punkt 2.
4. **Ret Quest 2-formuleringen** (CR-004). ADR-003 og `docs/08` §1: "performancegulv, EOL dec. 2027". Quest 3S som antaget baseline efter v1.0.
5. **Tilføj scope-kolonne i backloggen** (CR-005) og lad roadmap-intervallerne følge de valgte items.
6. **Ret skemaerne** (CR-006, CONFLICT-003, CONFLICT-006): manglende felter, `revision` påkrævet, checksum-definition.
7. **Vælg én passivitetsgrænse** (CR-007, CONFLICT-002).
8. **Tilføj PO-000** (CR-010) og en lokaliserings-ADR + ét backlog-item (CR-008).
9. **Skær coordinator-handover** (afsnit 5): beslut "ingen live handover, kun checkpoint-resume" og reducér PO-023.

### Skal afklares med prototype

- **OpenXR på Quest 1** — det afgørende eksperiment. Alt andet i platformplanen afhænger af udfaldet.
- **Fire markører skaber diskussion** (OQ-006) — ekstern one-day playtest, som planlagt.
- **Udfaldsformlen med reducerede led** — mål fordelingen af udfaldskategorier over 20 simulerede runs, før den bygges i VR.
- **Standby → netværkstab-timing** på Q2/Q3 (CR-009).
- **Kollapssekvensens frame cost** isoleret, før art pass (afsnit 7).
- **Blandet siddende/stående** på coop-objektet (afsnit 4).

### Kan vente til efter vertical slice

- Efterspils-titler og telemetrien bag dem.
- Quest 3 visuelle enhancements.
- Photon Voice og fjernspil-optimering.
- 90 Hz-mode på Q3.
- Addressables ud over lokal organisering.
- ADR om entitlement/session policy til en eventuel offentlig version.

### Bør fjernes fra gaveversionen

- **`EVT_DISTANT_SMOKE_001`** — teaser uden indfrielse i et spil, der spilles 2-4 gange.
- **"3+ markører"-handlingskategorien** (`docs/04` §3) — defineret, men uden brug i standardloopet. Dødt design, der koster UI og validering.
- **Live coordinator-handover** — erstattes af checkpoint-resume.
- **Arm-IK** — allerede betinget i `docs/11`; gør beslutningen endelig nu, så det ikke genåbnes i M7.
- **Quest 1-lanen, hvis OpenXR-testen fejler.** Ikke som nederlag, men som den beslutning `docs/14` allerede har forberedt.

---

## F. Revideret roadmap

Kun M0-M2 ændres. Milepæls-ID'er bevares.

| ID | Nuværende | Revideret | Ændring |
|---|---|---|---|
| M0 | Platform feasibility, 60-100 t | **Platform- og netværksfeasibility, 150-175 t** | Optager PO-017–PO-020, PO-022, PO-025 fra M2. Gate uændret — men nu beviselig med M0's egne opgaver. Første deleksperiment: OpenXR på Q1. |
| M1 | Interaction foundation, 35-55 t | Uændret | — |
| M2 | Multiplayer foundation, 45-70 t | **Multiplayer hardening, 60-90 t** | Beholder handshake, authority-regler, reconnect, checkpoint-skelet, debug-UI og failure injection. Afgiver session-/replikationsgrundlaget til M0. |
| M3-M9 | — | Uændret i rækkefølge | Timetallene revideres, når scope-kolonnen i CR-005 er udfyldt. |

Stop/go-grænsen i `docs/14` flyttes fra "senest efter 250 t" til **"senest ved afslutningen af M0"**, hvilket med den reviderede M0 falder omkring 150-175 t — og nu faktisk på det tidspunkt, hvor beslutningsgrundlaget findes.

---

## G. Åbne spørgsmål til ejeren

| ID | Spørgsmål | Hvorfor det betyder noget | Blokerer |
|---|---|---|---|
| Q-001 | Hvis OpenXR ikke starter på Quest 1: dropper du Q1-lanen, eller er fysisk Q1-test et ufravigeligt krav? | Afgør om projektet kan bygges på Unity 6 LTS, eller om det låses til en udgået stak. Det er den dyreste enkeltbeslutning i projektet. | M0 |
| Q-002 | Er Quest 1 et ønske fra dig, eller fra modtageren? | Hvis begge spillere har Q2/Q3, er hele lanen valgfri polish. Hvis modtageren kun har Q1, er det et produktkrav. | M0 |
| Q-003 | Accepterer du "ingen live coordinator-handover, kun checkpoint-resume"? | Fjerner en hel klasse af desync-fejl og reducerer PO-023 markant. | M0/M2 |
| Q-004 | Hvilke af backloggens 108 items er **ude** af gaveversionen? | Uden det svar er 500-810 t et ønske, ikke en plan. | M0 |
| Q-005 | Er du på Unity Personal/Pro (ikke Enterprise/Industry)? | Afgør om 2022.3 stadig patches for dig. Jeg antager Personal/Pro. | M0 |
| Q-006 | Spilles gaveversionen primært i samme rum? | Afgør om reconnect-vinduet skal tunes mod Wi-Fi-standby eller mod internet-jitter, og om Photon Voice nogensinde bliver relevant. | M2 |
| Q-007 | Dansk som eneste sprog i gaveversionen? | Låser undertekst- og nøglearbejdet ned og forhindrer usynlig vækst i M6/M8. | M6 |
| Q-008 | Skal karaktererne være jer to eksplicit, eller neutrale overlevende? | Påvirker avatarbudget, voice, og hvor meget den personlige finale skal bære. | M8 |
| Q-009 | Hvor mange gange forventer du, det bliver spillet? | 2 gange og 4 gange giver vidt forskellige krav til event-variation — og dermed til M6's størrelse. | M6 |
| Q-010 | Hvad er den reelle deadline? Findes der en dato (fødselsdag, jul, jubilæum)? | Ingen af dokumenterne nævner en dato. Med 15 t/uge fra august 2026 lander gaveversionen tidligst medio 2027. Hvis der findes en dato før dét, skal scope skæres nu — ikke i M6. | Alt |

---

## H. Maskinlæsbar kommentarblok

```json
{
  "review_version": "1.0",
  "verdict": "PROCEED_WITH_BLOCKERS",
  "comments": [
    {
      "id": "CR-001",
      "severity": "BLOCKER",
      "category": "roadmap",
      "summary": "M0's gate kraever Photon-session, head/hands-replication og coop-kasse, men alle disse opgaver ligger i M2 i backloggen. M0 rummer 12 items, 89 timer, heraf 41 timer P0, og kun build/XR-arbejde.",
      "recommendation": "Flyt PO-017, PO-018, PO-019, PO-020, PO-022 og PO-025 til M0 og re-baselinér M0 til ca. 150-175 timer. Flyt stop/go-graensen fra 250 timer til afslutningen af M0.",
      "affected_files": ["docs/12_PRODUCTION_ROADMAP.md", "docs/17_BACKLOG_AND_MILESTONES.md", "docs/14_RISK_SCOPE_BUDGET.md", "docs/06_TECHNICAL_ARCHITECTURE.md", "docs/30_M0_ISSUE_BODY.md"],
      "requires_evidence": false
    },
    {
      "id": "CR-002",
      "severity": "BLOCKER",
      "category": "platform",
      "summary": "Quest 1-lanen beskrives som pakkedivergens, men Q1 kraever Oculus-provider v3.x mens Q2/Q3 bruger OpenXR-provider. Det er to XR-backends, ikke to versioner, og Oculus-provideren er dokumenteret deprecated og planlagt fjernet.",
      "recommendation": "M0 skal foerst teste OpenXR-provider fysisk paa Quest 1. Negativt resultat udloeser exit-kriteriet i docs/14 i stedet for at starte en interaction-fork.",
      "affected_files": ["docs/06_TECHNICAL_ARCHITECTURE.md", "docs/08_PLATFORM_BUILD_PERFORMANCE.md", "docs/14_RISK_SCOPE_BUDGET.md", "docs/18_DECISION_LOG.md", "docs/30_M0_ISSUE_BODY.md"],
      "requires_evidence": true
    },
    {
      "id": "CR-003",
      "severity": "HIGH",
      "category": "stack",
      "summary": "ADR-006 begrunder Unity 2022.3 med treaarige LTS-patches. Unitys egen politik giver to aar til Personal og Pro; tredje aar er kun Enterprise og Industry. 2022.3 udkom juni 2023, saa Personal/Pro-support udloeb medio 2025.",
      "recommendation": "Goer editorvalget afhaengigt af CR-002. Byg paa Unity 6 LTS medmindre Q1 beviseligt kraever andet, og laas ikke hele projektet til en udgaaet editor for en enhed uden brugere.",
      "affected_files": ["docs/01_EXECUTIVE_HANDOFF.md", "docs/06_TECHNICAL_ARCHITECTURE.md", "docs/22_SOURCE_REGISTER.md", "docs/18_DECISION_LOG.md"],
      "requires_evidence": false
    },
    {
      "id": "CR-004",
      "severity": "HIGH",
      "category": "platform",
      "summary": "Quest 2 udgik af salg ultimo 2024, faar feature-opdateringer til december 2026 og kritiske opdateringer til december 2027. Projektets eget estimat lander gaveversionen tidligst medio 2027.",
      "recommendation": "Behold Quest 2 som performancegulv, men omformulér ADR-003 og docs/08 til performancegulv med EOL december 2027. Saet Quest 3S som antaget baseline for alt efter v1.0.",
      "affected_files": ["docs/01_EXECUTIVE_HANDOFF.md", "docs/08_PLATFORM_BUILD_PERFORMANCE.md", "docs/12_PRODUCTION_ROADMAP.md", "docs/18_DECISION_LOG.md"],
      "requires_evidence": false
    },
    {
      "id": "CR-005",
      "severity": "HIGH",
      "category": "scope",
      "summary": "Roadmap-intervallerne er ikke udledt af backloggen. M3 staar til 55-85 timer mod 260 timer i backloggen, M2 til 45-70 mod 173, M6 til 70-115 mod 214. Der findes ingen scope-kolonne, og alle 108 items staar Not Started.",
      "recommendation": "Tilfoej kolonnen Gaveversion med vaerdierne In, Out og Defer i docs/17, vaelg itemsaettet, og lad roadmap-intervallerne vaere summen af de valgte items.",
      "affected_files": ["docs/12_PRODUCTION_ROADMAP.md", "docs/14_RISK_SCOPE_BUDGET.md", "docs/17_BACKLOG_AND_MILESTONES.md", "docs/01_EXECUTIVE_HANDOFF.md"],
      "requires_evidence": false
    },
    {
      "id": "CR-006",
      "severity": "HIGH",
      "category": "data",
      "summary": "Skemaerne mangler felter som docs/10 kraever: supported build protocol og action catalog i scenario, cooldown i event. Alle skemaer har additionalProperties false, saa implementering bryder CI. Valideringen melder alligevel nul fejl, fordi initialState og winRules er utypede.",
      "recommendation": "Tilfoej de manglende felter, typificér winRules og loseRules minimalt, definér checksummens daekning og algoritme, og tilfoej en validatorregel om at ID i phases.actions skal findes i action-kataloget.",
      "affected_files": ["docs/10_DATA_CONTENT_SAVE_SCHEMAS.md", "schemas/scenario.schema.json", "schemas/event.schema.json", "schemas/savegame.schema.json", "tools/validate_handoff.py"],
      "requires_evidence": false
    },
    {
      "id": "CR-007",
      "severity": "HIGH",
      "category": "design",
      "summary": "Kravet om at begge spillere er aktive er produktets vigtigste loefte, men graensen staar som 12 sekunder i docs/04 og 20 sekunder i docs/02 og docs/05, og maalemetoden er manuel observation.",
      "recommendation": "Instrumentér maalingen via event-journalen, log aktive frames pr. spiller pr. handling, udskriv rapport pr. run, og vaelg én passivitetsgraense.",
      "affected_files": ["docs/02_PRODUCT_REQUIREMENTS.md", "docs/04_GAME_DESIGN_DEEP_DIVE.md", "docs/05_STORMNATTEN_CONTENT_BIBLE.md", "docs/13_TEST_QA_ACCEPTANCE.md"],
      "requires_evidence": false
    },
    {
      "id": "CR-008",
      "severity": "MEDIUM",
      "category": "content",
      "summary": "Build fejler ved manglende localization key og alle vigtige replikker kraever undertekster, men ingen af backloggens 108 items naevner lokalisering, sprog eller underteksttekstning.",
      "recommendation": "Skriv en ADR om dansk som eneste sprog i gaveversionen og tilfoej ét backlog-item til noegletabel og underteksttekstning.",
      "affected_files": ["docs/09_VR_INTERACTION_COMFORT_ACCESSIBILITY.md", "docs/10_DATA_CONTENT_SAVE_SCHEMAS.md", "docs/17_BACKLOG_AND_MILESTONES.md", "docs/19_OPEN_QUESTIONS.md"],
      "requires_evidence": false
    },
    {
      "id": "CR-009",
      "severity": "MEDIUM",
      "category": "network",
      "summary": "Reconnect-vinduet er foreslaaet til 90 sekunder og standby behandles som disconnect. Quest gaar i standby faa sekunder efter aftagning, saa den hyppigste virkelige afbrydelse rammer den dyre sti.",
      "recommendation": "Maal faktisk standby til netvaerkstab paa Quest 2 og Quest 3 i M2 og saet vinduet efter data. Goer checkpoint-resume til den billige standardvej.",
      "affected_files": ["docs/07_MULTIPLAYER_NETWORKING.md", "docs/13_TEST_QA_ACCEPTANCE.md"],
      "requires_evidence": true
    },
    {
      "id": "CR-010",
      "severity": "MEDIUM",
      "category": "process",
      "summary": "Gaten i docs/24 kraever disposition af alle blockers, indarbejdelse i specs og ADR-log samt opdateret M0-scope, men der findes ingen backlog-item for det arbejde.",
      "recommendation": "Tilfoej PO-000 Behandl review og opdatér baseline som M0 P0 med estimat 8-16 timer.",
      "affected_files": ["docs/17_BACKLOG_AND_MILESTONES.md", "docs/24_REVIEW_TO_IMPLEMENTATION_GATE.md"],
      "requires_evidence": false
    }
  ],
  "conflicts": [
    {
      "id": "CONFLICT-001",
      "source_a": "docs/12_PRODUCTION_ROADMAP.md M0 og docs/06_TECHNICAL_ARCHITECTURE.md afsnit 3",
      "source_b": "docs/17_BACKLOG_AND_MILESTONES.md milepaelstildeling af PO-017 til PO-025",
      "conflict": "M0's gate kan ikke bevises af M0's opgavesaet. To dokumenter beskriver to forskellige M0.",
      "recommended_authority": "docs/12_PRODUCTION_ROADMAP.md"
    },
    {
      "id": "CONFLICT-002",
      "source_a": "docs/04_GAME_DESIGN_DEEP_DIVE.md afsnit 8, maksimal passiv periode 12 sekunder",
      "source_b": "docs/02_PRODUCT_REQUIREMENTS.md og docs/05_STORMNATTEN_CONTENT_BIBLE.md, 20 sekunder",
      "conflict": "To graensevaerdier for projektets vigtigste designgate.",
      "recommended_authority": "docs/04_GAME_DESIGN_DEEP_DIVE.md som designregel, 20 sekunder som testgraense"
    },
    {
      "id": "CONFLICT-003",
      "source_a": "docs/10_DATA_CONTENT_SAVE_SCHEMAS.md feltbeskrivelser",
      "source_b": "schemas/scenario.schema.json og schemas/event.schema.json med additionalProperties false",
      "conflict": "Skemaerne mangler felter som docs/10 kraever og er samtidig lukkede for tilfoejelser.",
      "recommended_authority": "docs/10_DATA_CONTENT_SAVE_SCHEMAS.md"
    },
    {
      "id": "CONFLICT-004",
      "source_a": "docs/01_EXECUTIVE_HANDOFF.md og ADR-006 om treaarige LTS-patches",
      "source_b": "Unitys officielle LTS-politik med to aar for Personal og Pro",
      "conflict": "Editorvalgets begrundelse hviler paa en supportgaranti der ikke gaelder projektets licenstier.",
      "recommended_authority": "Unitys dokumentation"
    },
    {
      "id": "CONFLICT-005",
      "source_a": "docs/01_EXECUTIVE_HANDOFF.md, ca. 620 timer",
      "source_b": "docs/14_RISK_SCOPE_BUDGET.md og beregnet backlogsum, 622 timer",
      "conflict": "Talafvigelse i et dokument der bruges som tracker.",
      "recommended_authority": "Beregnet backlogsum, 622"
    },
    {
      "id": "CONFLICT-006",
      "source_a": "docs/07_MULTIPLAYER_NETWORKING.md afsnit 11, monotont voksende revision",
      "source_b": "schemas/savegame.schema.json hvor revision er valgfri",
      "conflict": "Et felt som resync-logikken afhaenger af er ikke paakraevet i kontrakten.",
      "recommended_authority": "docs/07_MULTIPLAYER_NETWORKING.md"
    }
  ],
  "questions": [
    {"id": "Q-001", "question": "Hvis OpenXR ikke starter paa Quest 1: droppes Q1-lanen, eller er fysisk Q1-test et ufravigeligt krav?", "blocking_milestone": "M0"},
    {"id": "Q-002", "question": "Er Quest 1 et oenske fra dig eller fra modtageren?", "blocking_milestone": "M0"},
    {"id": "Q-003", "question": "Accepteres ingen live coordinator-handover, kun checkpoint-resume?", "blocking_milestone": "M0/M2"},
    {"id": "Q-004", "question": "Hvilke af backloggens 108 items er ude af gaveversionen?", "blocking_milestone": "M0"},
    {"id": "Q-005", "question": "Er licensen Unity Personal eller Pro, altsaa ikke Enterprise eller Industry?", "blocking_milestone": "M0"},
    {"id": "Q-006", "question": "Spilles gaveversionen primaert i samme rum?", "blocking_milestone": "M2"},
    {"id": "Q-007", "question": "Er dansk eneste sprog i gaveversionen?", "blocking_milestone": "M6"},
    {"id": "Q-008", "question": "Skal karaktererne vaere jer to eksplicit eller neutrale overlevende?", "blocking_milestone": "M8"},
    {"id": "Q-009", "question": "Hvor mange gennemspilninger forventes?", "blocking_milestone": "M6"},
    {"id": "Q-010", "question": "Findes der en reel deadline eller dato for gaven?", "blocking_milestone": "alle"}
  ]
}
```
