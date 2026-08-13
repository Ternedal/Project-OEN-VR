# Personalization package spec — PROJECT ØEN

**Ejer af private source content:** ChatGPT / Anders  
**Unity-loader/integration:** Claude  
**Dato:** 2026-08-13  
**Milepæl:** M8, men kontrakten kan færdiggøres nu

## Formål

Gaveversionens personlige indhold skal kunne skiftes ind uden at:

- ændre gameplaybalance
- ændre netværksprotokol
- kræve specialkode pr. personlig genstand
- lække private billeder/lyd til repository, logs eller build artifacts uden hensigt
- gøre spillet ubrugeligt, hvis private filer mangler

`PersonalizationProfile` er allerede defineret i schema. Dette dokument beskriver den **praktiske produktions- og QA-kontrakt** omkring profilen.

---

# 1. Grundregel

Personalization er et **overlay på et færdigt neutralt spil**.

Hvis hele private pakken slettes, skal følgende stadig fungere:

- boot
- lobby
- hele Stormnatten
- neutral finale
- after-action report
- replay/retry

Ingen canonical gameplayregel må afhænge af private content.

---

# 2. Private package — anbefalet struktur

Denne struktur dokumenteres, men mappen må ikke committed til hovedrepoet:

```text
PrivateContent/
  profile.json
  Images/
    ending_photo.jpg
    memento_01.png
    memento_02.png
    memento_03.png
  Audio/
    final_message.wav
  References/
    README_PRIVATE.txt
```

`PrivateContent/` skal være gitignored i den faktiske Unity/workspace-integration.

## Repository-safe counterpart

Repoet må kun indeholde:

- schema
- example profile med placeholder-navne
- hook IDs
- neutral fallback assets/copy
- validation rules

---

# 3. Godkendte hooks

| Hook | Funktion | Neutral fallback | Privat content tilladt |
|---|---|---|---|
| `ENDING_CRATE_PHOTO` | billede i finalekasse | neutral island/rescue-photo | ja |
| `RADIO_FINAL_MESSAGE` | personlig slutbesked | neutral rescue-radio | ja |
| `CAMP_MEMENTO_1` | memento/prop | generisk kompas/souvenir | ja |
| `CAMP_MEMENTO_2` | memento/prop | generisk kort/billet | ja |
| `CAMP_MEMENTO_3` | memento/prop | generisk lille souvenir | ja |

Memento-hooks må kun ændre udseende/tekstur/label; de må ikke give ressourcer, stats eller unlocks.

---

# 4. Billedspecifikation

## `ENDING_CRATE_PHOTO`

Source master:

- JPEG eller PNG
- behold original master uden for repo
- minimum ca. 1600 px på længste led anbefales
- ingen vigtig information helt ude i kanten
- ansigter/centrale elementer bør ligge inden for midterste ~70 % af billedfladen
- undgå meget mørke billeder, hvor detaljen forsvinder i headset

Unity runtime-resize/compression besluttes af Claude.

## Memento images

- PNG foretrækkes hvis transparent baggrund er nyttig
- tydelig silhouette og få små detaljer
- skal kunne læses som personlig reference uden små tekster

---

# 5. Audio specification — `RADIO_FINAL_MESSAGE`

Source master:

- WAV, 48 kHz
- mono eller stereo afhængigt af source; radioeffekt tilføjes i implementation, ikke destruktivt til eneste master
- behold uredigeret master separat
- tale skal være forståelig uden aggressiv noise/music

## Længde

Hele den personlige finalesekvens må maksimalt vare ca. 90 sekunder jf. scenario-biblen.

Anbefaling for selve beskeden:

- **20-45 sekunder** er ideelt
- 60 sekunder er øvre normalgrænse
- resten af finalesekvensen skal have plads til spillernes reaktion og world state

## Indholdsregel

Beskeden bør:

- føles som en belønning efter missionen
- ikke kræve en bestemt win-grade, medmindre flere varianter produceres
- ikke indeholde information, der er nødvendig for gameplay
- kunne erstattes 1:1 af neutral fallback uden at scenen knækker

---

# 6. Personlige tekst-overrides

Godkendte kategorier:

- display names
- ending message copy
- labels på mementos
- korte private references i epilogen

Ikke godkendt:

- ændring af action costs
- resource names på en måde der ændrer forståelse
- skjulte hints
- player-specific buffs
- ændring af win/lose-regler

---

# 7. Tonevarianter

Det åbne product-owner-spørgsmål om finalens tone skal ikke blokere kontrakten.

Pakken understøtter tre content-retninger uden kodeændring:

## Eventyrlig

Fokus på: “I klarede den sammen.”

## Humoristisk

Fokus på fælles jokes/referencer, men ingen joke må underminere den følelsesmæssige payoff.

## Romantisk/personlig

Fokus på relationen og fælles oplevelser.

Den konkrete tone vælges senere af Anders; neutral fallback er altid eventyrlig.

---

# 8. Neutral finale — canonical fallback

Hvis private content mangler:

1. signalet observeres
2. radio: “Signal observeret.”
3. radio: “Bliv ved kysten. Vi har jeres position.”
4. radio: “Hold ud lidt endnu.”
5. neutral ending crate kan åbnes med et generisk foto/kort/souvenir
6. after-action report følger

Source-copy: `docs/40_UX_COPY_AND_LOCALIZATION_CATALOG.md`.

---

# 9. Private content validation

Før en privat pakke gives til Claude/Unity-flowet skal ChatGPT/Anders verificere:

- [ ] `profileId` unik
- [ ] `fallbackProfileId` findes
- [ ] højst to display names
- [ ] alle hooks er kendte
- [ ] alle paths er relative og ligger under `PrivateContent/`
- [ ] ingen `..` path traversal
- [ ] billeder kan åbnes
- [ ] audio kan afspilles
- [ ] filstørrelser er rimelige
- [ ] private filer er ikke tracked af git
- [ ] neutral fallback findes for hvert hook
- [ ] tekst-overrides indeholder ikke secrets/passwords/personfølsomme oplysninger ud over bevidst gaveindhold
- [ ] EXIF/location metadata fjernes fra billeder, hvis den ikke er ønsket
- [ ] private filenames er neutrale og behøver ikke indeholde fulde navne

Claude kan implementere automatiseret validering, men source-package-QA starter her.

---

# 10. Logging/privacy contract

Logs må gerne indeholde:

- hook-ID
- `profileId` hvis det er en neutral intern ID og ikke personnavn
- “asset present/missing/invalid”
- filtype/størrelsesklasse hvis nyttigt

Logs må **ikke** indeholde:

- private tekst-overrides
- display names hvis ikke nødvendigt
- private filindhold
- rå billedmetadata
- audio transcript
- fulde private absolute paths

Eksempel god log:

```text
Personalization hook RADIO_FINAL_MESSAGE: asset valid
```

Eksempel dårlig log:

```text
Loaded C:\Users\Anders\Desktop\LoveMessageFor<Name>.wav: "...private transcript..."
```

---

# 11. Build/artifact contract

Ved gift release skal Anders vide eksplicit, om private content er:

- baked ind i den konkrete APK/build
- kopieret som separat lokal content-pakke

Det tekniske valg tilhører Claude, men produktkravene er:

1. private content må ikke ende i en offentlig releasekanal ved et uheld
2. backup må være krypteret/privat
3. rollback-build skal have kendt private-content-state
4. neutral build skal altid kunne produceres

---

# 12. Personalization content worksheet

Udfyldes senere uden at private data nødvendigvis commits:

| Felt | Valg/status |
|---|---|
| Tone | Eventyrlig / humoristisk / romantisk |
| Display name P1 | Privat |
| Display name P2 | Privat |
| Ending photo | Mangler |
| Final audio message | Mangler |
| Memento 1 | Mangler |
| Memento 2 | Optional |
| Memento 3 | Optional |
| Neutral fallback QA | Skal bestå før privat integration |

---

# 13. Claude handoff

Når private source-pakken er klar, får Claude **ikke** lov til at opfinde nye hooks.

Handoff består af:

- validated `profile.json`
- privat asset-folder via sikker lokal kanal
- dette dokument
- hook-to-fallback-mapping
- ønsket tone
- QA-resultat

Claude ejer derefter loader, asset-binding og runtime fallback i Unity.

---

# 14. Definition of done for personalization source-side

ChatGPT-sporet er færdigt når:

- hook-listen er komplet
- neutral fallback-copy/assets er specificeret
- private source requirements er dokumenteret
- privacy/logging-regler er dokumenteret
- package validation checklist er bestået
- concrete private content er produceret og QA'et uden at ramme repoet

Selve `PersonalizationProfile`-loaderen, buildintegration og runtime fallback er Claude-arbejde.
