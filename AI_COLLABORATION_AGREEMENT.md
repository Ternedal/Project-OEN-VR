# Samarbejdsaftale – PROJECT ØEN

**Parter:** ChatGPT og Claude  
**Projektejer:** Anders  
**Projekt:** PROJECT ØEN / STRANDET SAMMEN  
**Status:** Gældende arbejdsdeling  
**Dato:** 2026-08-13

## 1. Formål

Formålet med denne aftale er at gøre ansvarsdelingen mellem ChatGPT og Claude entydig, så arbejdet på PROJECT ØEN kan fortsætte uden dobbeltarbejde, uklare ejerskaber eller parallelle implementeringer.

Den grundlæggende arbejdsdeling er:

> **Claude ejer alt, der foregår i eller direkte vedrører Unity-projektet.**  
> **ChatGPT ejer alt øvrigt arbejde omkring PROJECT ØEN.**

Anders er produktejer og har altid sidste ord.

### Forhold til øvrige projektdokumenter

Denne fil er autoritativ for **rolle-, ansvar- og handoff-grænser mellem ChatGPT og Claude**.

Den ændrer ikke produkt-, platform-, gameplay- eller arkitekturbeslutninger i de eksisterende source-of-truth-dokumenter. Ved konflikt gælder dokumenthierarkiet i `00_READ_ME_FIRST.md` for produkt- og tekniske beslutninger.

Eksempel: Quest 1 er fortsat udgået som runtime og testlane i hovedprojektet. Denne samarbejdsaftale må ikke fortolkes som en genindførelse af Quest 1-understøttelse.

---

## 2. Claude – fuldt ansvar for Unity

Claude er **Unity Lead** og har ejerskab over hele Unity-projektet.

Dette omfatter blandt andet:

### Unity-projektet

- Unity-projektstruktur
- Scenes
- GameObjects
- Components
- Prefabs
- ScriptableObjects
- Packages
- Project Settings
- Input System
- Tags og Layers
- Physics
- Lighting
- Cameras
- Animation Controllers
- Timeline
- Addressables
- Unity asset management

### Programmering i Unity

- C# scripts
- Gameplay systems
- State machines
- Interaction systems
- AI i spillet
- Player controllers
- Inventory
- Crafting
- Building
- Survival systems
- Multiplayer/netcode
- Save/load
- Quest-specifik kode
- Performancekode
- Editor scripts
- Custom inspectors
- Unity tooling

### XR / Meta Quest

Claude ejer hele Unity-siden af:

- Quest 2 som performance- og kvalitetsbaseline
- Quest 3 / Quest 3S kompatibilitet og additive forbedringer
- OpenXR
- Meta XR SDK, hvis og hvor projektets gældende arkitektur anvender det
- Controller input
- Hand tracking, hvis det indgår i godkendt scope
- VR interactions
- Locomotion
- Passthrough, hvis det indgår i godkendt scope
- XR rig
- Rendering setup
- Platform permissions

Quest 1 er udgået som runtime og testlane jf. `00_READ_ME_FIRST.md`.

### Grafikintegration

Claude ejer **implementeringen** af grafik i Unity:

- import settings
- sprites
- textures
- materials
- shaders
- atlases
- sprite slicing
- mipmaps
- LOD
- compression
- transparency
- animation
- particle systems
- VFX
- terrain integration
- vegetation systems
- UI implementation

Claude skal ikke nødvendigvis skabe kildegrafikken. Det er ChatGPTs domæne.

### Lydintegration

Claude ejer Unity-implementeringen af:

- AudioSources
- AudioListeners
- AudioMixer
- spatial audio
- ambience systems
- sound triggers
- dynamic music
- attenuation
- audio zones
- Quest audio performance

Selve lydmaterialet, lydretningen og lyd-designet udarbejdes uden for Unity af ChatGPT.

### Builds

Claude ejer:

- Unity build configuration
- Android / Quest builds
- APK builds
- development builds
- build errors
- signing-konfiguration relateret til Unity
- Unity Profiler
- memory profiling
- frame timing
- draw calls
- Quest performance
- Unity-side CI/build scripts

---

## 3. ChatGPT – ansvar for alt uden for Unity

ChatGPT fungerer som:

**Product Lead + Creative Lead + Technical Architect + Asset Lead + QA/Coordinator**

ChatGPT ejer blandt andet:

### Produktdesign

- spilkoncept
- gameplay vision
- game loop
- progression
- balancing-koncept
- crafting-design
- survival-design
- spilregler
- missionsdesign
- encounters
- events
- difficulty progression
- onboarding
- UX-koncept

### Game Design Documents og projektdokumentation

ChatGPT vedligeholder og udvikler:

- master game design document
- feature specifications
- gameplay specifications
- systembeskrivelser
- acceptance criteria
- roadmap
- backlog
- milepæle
- prioritering
- handoff-materiale

Alle ændringer skal respektere dokumenthierarkiet og beslutningsloggen i repoet.

### Visuelt design

ChatGPT ejer:

- art direction
- visuel identitet
- miljødesign
- UI-design
- mockups
- concept art
- referencebilleder
- asset specifications
- texture specifications
- ikoner
- illustrationer
- grafiske source assets

Når assets skal bruges i Unity:

> **ChatGPT leverer/speciferer asset → Claude implementerer asset i Unity.**

---

## 4. Assetproduktion

ChatGPT står for at definere og/eller producere de nødvendige source assets til PROJECT ØEN.

Det kan eksempelvis være:

- træ
- sten
- planter
- presenninger
- reb
- værktøj
- beholdere
- byggematerialer
- bål
- mad
- crafting-genstande
- UI-elementer
- ikoner
- dekorationer
- skilte
- miljøelementer
- props
- decals
- textures
- referencegrafik

Assets skal så vidt muligt leveres i formater, størrelser og strukturer, der er direkte anvendelige af Claude i Unity.

ChatGPT ejer **source-asset-kvaliteten**. Claude ejer **Unity-import, runtime-opsætning og optimering**.

---

## 5. Lyddesign

ChatGPT ejer:

- soundscape
- lydliste
- ambience-design
- musikretning
- lydeffekt-specifikation
- lydassets
- voice-design
- miljølyde

Eksempel:

ChatGPT kan levere `campfire_loop.wav` sammen med specifikation af loop-adfærd, ønsket oplevelse, afstand og kontekst.

Claude implementerer derefter materialet korrekt i Unity.

---

## 6. Arkitektur uden for Unity

ChatGPT ejer alle systemer uden for selve Unity-applikationen, herunder når de findes i projektets godkendte scope:

- backend services
- API'er
- webservices
- asset pipelines
- AI-services
- content pipelines
- build-support tooling uden for Unity
- serverarkitektur
- databaser
- telemetry-design
- dokumentation
- integrationsarkitektur

Grænseregel:

> Hvis kode eller konfiguration er en del af Unity-projektets runtime/editor-implementering → Claude ejer den.  
> Hvis det er en ekstern service, pipeline eller ikke-Unity-værktøj → ChatGPT ejer den.

---

## 7. Repository-regler

GitHub er projektets tekniske source of truth.

Ingen af parterne må antage, at en feature eksisterer eller mangler, uden først at kontrollere repositoryets aktuelle tilstand.

Før større ændringer skal den ansvarlige AI:

1. inspicere relevant eksisterende kode/materiale
2. læse relevante source-of-truth-dokumenter
3. forstå nuværende arkitektur
4. undgå unødvendig duplikering
5. genbruge eksisterende komponenter, hvor det giver mening
6. bevare fungerende funktionalitet
7. markere reelle dokumentkonflikter efter repoets gældende konfliktprocedure

---

## 8. Ejerskabsgrænse

Den vigtigste regel er:

> **Claude ændrer Unity.**  
> **ChatGPT ændrer ikke Unity, medmindre Anders udtrykkeligt beder om det.**

Omvendt:

> **ChatGPT ejer designet og de øvrige leverancer omkring Unity.**

Claude bør ikke på egen hånd ændre grundlæggende:

- game design
- visuel retning
- gameplay-regler
- roadmap
- produktstrategi
- godkendt scope

Claude må og bør foreslå forbedringer, når implementeringsarbejdet afdækker problemer eller bedre løsninger.

Forslag skal adskilles tydeligt fra allerede godkendte beslutninger og må ikke implementeres som skjulte scope- eller designændringer.

---

## 9. Handoff: ChatGPT → Claude

Når ChatGPT designer eller specificerer en Unity-feature, skal Claude have en konkret implementeringspakke, som efter behov omfatter:

### Feature
Hvad skal laves?

### Formål
Hvorfor findes funktionen?

### Player experience
Hvordan oplever spilleren funktionen?

### Funktionelle krav
Hvad skal systemet konkret kunne?

### Assets
Hvilke assets bruges eller mangler?

### UI/UX
Hvordan skal funktionen præsenteres og betjenes?

### Edge cases
Hvad kan gå galt?

### Performance/platform
Hvilke gældende Quest 2/3-krav er relevante?

### Acceptance criteria
Hvornår er featuren færdig?

Claude vælger derefter den konkrete Unity-arkitektur inden for projektets eksisterende tekniske beslutninger.

---

## 10. Handoff: Claude → ChatGPT

Når Claude afslutter eller afleverer en Unity-feature, skal Claude rapportere:

### Implementeret
Hvad er lavet?

### Filer ændret
Hvilke scripts, scenes, prefabs, assets eller settings er ændret?

### Sådan testes det
En konkret testprocedure.

### Verifikation
Hvilke relevante compile-, runtime-, build- og performancechecks er gennemført?

### Kendte begrænsninger
Hvad mangler eller er endnu ikke bevist?

### Nye behov
Kræves der eksempelvis:

- grafik
- lyd
- produktbeslutninger
- UX-design
- specs
- nye assets
- ændringer i eksisterende krav

Disse opgaver sendes tilbage til ChatGPT/Anders som eksplicitte handoff-punkter.

---

## 11. Ingen pseudo-implementering

Begge AI'er skal arbejde ud fra faktiske projektdata.

Det er ikke tilstrækkeligt at beskrive, hvordan noget *kunne* implementeres, hvis opgaven konkret er at implementere det, og nødvendige værktøjer/repository-adgang er tilgængelige.

Når implementering er godkendt efter projektets gældende milepæls- og reviewflow, skal arbejdet udføres i det faktiske projekt.

---

## 12. Ingen dobbeltarbejde

Før nyt arbejde startes, skal eksisterende projektstatus kontrolleres.

Hvis en funktion allerede findes, skal den eksisterende implementering som udgangspunkt forbedres frem for at skabe en parallel version.

Parallelle implementeringer må kun oprettes bevidst, eksempelvis som isoleret prototype eller benchmark, og skal i så fald mærkes tydeligt.

---

## 13. QA

Begge parter er ansvarlige for kvalitet inden for deres eget område.

### Claude verificerer

- Unity compilation
- runtime errors
- scene references
- prefab references
- Quest 2/3 kompatibilitet
- performance
- regressions
- input
- builds
- relevante Unity-tests

### ChatGPT verificerer

- krav
- gameplay consistency
- UX
- art consistency
- asset completeness
- roadmap alignment
- dokumentation
- samlet produktkvalitet
- sammenhæng mellem specs, backlog og leverancer

---

## 14. Bugs

Hvis problemet primært er Unity-relateret, ejer Claude fejlen.

Eksempler:

- `NullReferenceException`
- prefab virker ikke
- shaderfejl
- controller input
- frame rate
- scene loading
- buildfejl

Hvis problemet primært ligger uden for Unity, ejer ChatGPT fejlen.

Eksempler:

- forkert source asset
- manglende grafikelement
- forkert spilregel/specifikation
- backendfejl
- manglende dokumentation
- forkert produktflow

---

## 15. Tværgående problemer

Hvis et problem krydser grænsen, deles det efter domæne.

Eksempel: **Bålet ser forkert ud.**

ChatGPT vurderer eksempelvis:

- hvordan bålet bør se ud
- visuel reference
- ønsket karakter af flammer og gløder
- lydretning
- kontekst og gameplay-formål

Claude vurderer eksempelvis:

- particle system
- shaders
- animation
- lighting
- audio implementation
- runtime-adfærd
- performance

---

## 16. Beslutningshierarki

Ved uenighed mellem parterne gælder:

1. Anders' eksplicitte instruktion
2. Repoets gældende source-of-truth-hierarki
3. dokumenterede og accepterede projektkrav
4. dokumenterede beslutninger/ADR'er
5. eksisterende implementering, når den ikke strider mod ovenstående
6. teknisk vurdering fra domæneejeren

Claude har det tekniske implementeringsansvar **inden for Unity**, medmindre Anders beslutter andet.

ChatGPT har design-/produkt-/asset-/ekstern-arkitekturansvar **uden for Unity**, medmindre Anders beslutter andet.

Anders har altid sidste ord.

---

## 17. Fokus

Målet er ikke at producere flest mulige dokumenter eller størst mulig kodebase.

Målet er:

> **At få PROJECT ØEN til at blive et sammenhængende, flot, performant og spilbart VR-spil.**

Begge AI'er skal derfor foretrække:

- færdige features
- reel integration
- testbare resultater
- genbrugelige systemer
- målbar Quest 2-performance
- høj kvalitet

frem for:

- mock-implementeringer, når reel implementering er mulig
- placeholder-systemer uden klar udskiftningsplan
- unødvendig kompleksitet
- parallelle systemer
- lange planer uden efterfølgende implementation

---

## 18. Permanent arbejdsdeling

Fra denne aftales ikrafttræden gælder som standard:

> 🎮 **CLAUDE = UNITY**

> 🧭 **CHATGPT = ALT ANDET**

Gråzoner afgøres først ud fra spørgsmålet:

> **Skal ændringen foretages inde i Unity-projektet?**

Hvis ja → Claude.

Hvis nej → ChatGPT.

Hvis begge dele er nødvendige:

> **ChatGPT specificerer/producerer inputtet → Claude implementerer Unity-delen.**

---

## 19. Standardarbejdsflow

```text
Anders
  ↓
beskriver mål / prioritet
  ↓
ChatGPT
  ↓
design / specs / grafik / lyd / assets / ekstern arkitektur / plan
  ↓
Claude
  ↓
Unity-implementering
  ↓
Claude
  ↓
build + test + teknisk rapport
  ↓
ChatGPT
  ↓
produkt-QA + asset/design-opfølgning + næste iteration
  ↓
Anders
  ↓
godkendelse / ny retning
```

---

## Hovedregel

> **Claude skal gøre Øen teknisk virkelig i Unity.**

> **ChatGPT skal sørge for, at Claude ved præcis, hvad der skal bygges, og levere alt det omkringliggende materiale, der skal til for at gøre Øen til det rigtige spil.**
