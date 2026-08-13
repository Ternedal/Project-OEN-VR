# IP & asset provenance register — PROJECT ØEN

**Ejer:** ChatGPT  
**Dato:** 2026-08-13  
**Formål:** Operationel mitigation af R-009 og asset-license-risiko

> Dette dokument er en projektarbejdsgang, ikke juridisk rådgivning eller juridisk clearance.

## Grundregel

Intet eksternt eller genereret source asset går fra “reference” til “release asset”, før vi kan svare på:

1. Hvor kommer det fra?
2. Hvem har lavet/licenseret det?
3. Hvilken brug er tilladt?
4. Er attribution påkrævet?
5. Er redistribuering i et kommercielt/offentligt build tilladt, hvis projektet senere bliver offentligt?
6. Indeholder det tredjeparts varemærker, ansigter, musik eller andet der kræver særskilt vurdering?
7. Har vi en source master og dokumentation?

---

# 1. Provenance-klasser

| Klasse | Betydning | Standardstatus |
|---|---|---|
| `OWN` | Lavet af Anders/ChatGPT-produceret til projektet med dokumenteret proces | Kan bruges efter QA |
| `GEN` | Genereret med et værktøj/model | Kræver værktøj/model + prompt/job-dato registreret |
| `BOUGHT` | Købt asset/licens | Kræver kvittering/licenstekst |
| `FREE` | Gratis asset med licens | Kræver licens + kilde |
| `CC` | Creative Commons eller lignende | Kræver præcis variant/attribution-vurdering |
| `REF` | Kun reference/inspiration | Må ikke distribueres som asset |
| `PRIVATE` | Personligt foto/lyd | Kun privat gavepackage; rettighed/samtykke vurderes separat |
| `UNKNOWN` | Ukendt oprindelse | **Må ikke bruges i release** |

---

# 2. Asset register

Denne tabel udvides, når konkrete filer produceres.

| Asset ID | Fil/source | Klasse | Oprindelse | Licens/tilladelse | Attribution | Private? | Release status |
|---|---|---|---|---|---|---:|---|
| `ENV_*` | TBD | — | — | — | — | Nej | Ikke produceret |
| `PRP_*` | TBD | — | — | — | — | Nej | Ikke produceret |
| `ITM_*` | TBD | — | — | — | — | Nej | Ikke produceret |
| `UI_*` | TBD | — | — | — | — | Nej | Ikke produceret |
| `VFX_*` | TBD | — | — | — | — | Nej | Ikke produceret |
| `SFX_*` | TBD | — | — | — | — | Nej | Ikke produceret |
| `MUS_*` | TBD | — | — | — | — | Nej | Ikke produceret |
| `ENDING_CRATE_PHOTO` | privat | `PRIVATE` | Anders/private source | Privat gavebrug | Nej | Ja | Må ikke i repo |
| `RADIO_FINAL_MESSAGE` | privat | `PRIVATE` | Anders/private source | Privat gavebrug | Nej | Ja | Må ikke i repo |

Concrete IDs come from `docs/38_SOURCE_ASSET_MANIFEST.md` and `docs/39_AUDIO_CUE_MANIFEST.md`.

---

# 3. Record per source asset

For hvert faktisk asset registreres mindst:

```text
Asset ID:
Filename:
Provenance class:
Creator/vendor/model:
Source URL/order reference:
Acquired/generated date:
License name/version:
License copy stored at:
Attribution required: yes/no
Modification allowed: yes/no/unknown
Redistribution in compiled game: yes/no/unknown
Commercial/public use: yes/no/unknown
Private: yes/no
Trademark/real-person content: yes/no
Notes:
Reviewer:
Release status: APPROVED / HOLD / REFERENCE_ONLY
```

Hvis et felt der er nødvendigt for brugen er `unknown`, er default `HOLD`.

---

# 4. Generated content

For genererede source assets registreres:

- værktøj/model/service
- dato
- om input indeholdt tredjepartsreference
- prompt/brief-ID hvis praktisk
- efterfølgende manuel redigering
- asset-ID

## Reference-regel

En reference kan bruges til at beskrive generelle egenskaber som:

- “vejrbidt træ”
- “stiliseret adventure-island”
- “grov håndbygget presenning”

Undgå at instruere produktionen til at kopiere en identificerbar tredjeparts illustration, karakter, logo, UI-layout eller præcis komposition.

---

# 5. Original-IP guardrail

PROJECT ØEN er original IP. Scenario-baseret survival, indsatsallokering, lejrstatus og samarbejdsopgaver er generelle designidéer; projektet skal have sin egen konkrete udførelse.

Før offentlig release gennemgås mindst:

- navn/titel
- scenario-tekst
- visuel identitet
- ikoner/kortlayout
- event-navne og eventtekst
- konkrete regler og terminologi
- marketingtekst/screenshots

## Red flags for intern review

Flag til særskilt vurdering hvis noget:

- bruger et eksisterende spils navn/subtitle
- genbruger regeltekst ordret eller tæt omskrevet
- genskaber et kendt board/card-layout med samme information hierarchy
- kopierer illustration/ikonografi
- bruger karakter-/stednavne fra en eksisterende IP
- bevidst markedsføres som “VR-versionen af [tredjepartstitel]”

Project docs may mention inspirations for intern provenance/review, men release-facing material skal stå på egne ben.

---

# 6. Purchased/free assets

Hvis assets senere købes:

1. gem original invoice/order reference uden for repo hvis den indeholder persondata
2. gem licensteksten eller en permanent reference
3. registrér version/date
4. noter om source files må redistribueres til collaborators
5. commit ikke vendor asset til offentligt repo, hvis licensen ikke tillader det
6. registrér ændringer lavet for at passe til art direction

## No-license-file rule

Et asset med teksten “free” på en downloadside, men uden klar licens/tilladelse, klassificeres `UNKNOWN`, ikke `FREE`.

---

# 7. Fonts

Fonts er assets.

For hver font:

- family + version
- source
- license
- embedding/distribution permission
- attribution
- fallback font

Indtil en font er valgt, må UI-design ikke være afhængigt af en bestemt kommerciel font.

---

# 8. Audio/music

For SFX/music registreres:

- composer/creator/library
- recording vs composition rights hvor relevant
- license scope
- modification permission
- attribution
- loop/derivative status

“Royalty free” må ikke antages at betyde “uden betingelser”. Den konkrete licens registreres.

Private voice message ligger i `PRIVATE`-klassen og følger `docs/41_PERSONALIZATION_PACKAGE_SPEC.md`.

---

# 9. Photos / real persons

Personalization kan indeholde fotos af virkelige personer.

Project rule:

- hold dem uden for repo
- fjern metadata hvis uønsket
- brug kun bevidst valgte billeder
- undgå at genbruge private billeder i offentlig marketing/testmateriale
- neutral build må ikke indeholde private thumbnails/caches

---

# 10. External references folder policy

Hvis referencebilleder gemmes lokalt:

```text
References/
  <topic>/
    SOURCE_NOTES.md
    ...reference files...
```

`SOURCE_NOTES.md` registrerer source URL/creator/use = `REF`.

Referencefolderen må gerne være lokal/privat og behøver ikke være en release-artifact.

---

# 11. Release audit

Før M9/RC:

- [ ] alle release assets har provenance != `UNKNOWN`
- [ ] alle `BOUGHT/FREE/CC` har licensreference
- [ ] attribution-listen er komplet
- [ ] private assets findes ikke i neutral build/repo/logs
- [ ] fonts er clearet
- [ ] music/SFX er clearet
- [ ] ingen `REF` asset er kommet med som distribution asset
- [ ] alle asset filenames kan mappes tilbage til manifest-ID
- [ ] original-IP review er gennemført på title/copy/UI/visuals

---

# 12. Claude handoff

Ved source-asset handoff skal Claude kunne se:

- asset ID
- source file
- manifest entry
- provenance class/status

Claude skal ikke selv vurdere uklar licens som “sandsynligvis okay”. Hvis status er `HOLD`, må asset ikke gøres releasekritisk før den er afklaret.

---

# 13. Definition of done

Provenance-sporet er færdigt til release, når **hver distribueret asset** har en sporbar oprindelse og en dokumenteret tilladelses-/license-status, og private/reference-only filer er verificeret fraværende fra den forkerte kanal.
