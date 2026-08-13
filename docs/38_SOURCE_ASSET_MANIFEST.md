# Source asset manifest — PROJECT ØEN

**Ejer:** ChatGPT  
**Unity-integration:** Claude  
**Dato:** 2026-08-13  
**Status:** Produktionsberedskab; ikke autorisation til dyr artproduktion

## Formål

Dette er den autoritative liste over **source assets**, som ChatGPT skal definere/producere uden for Unity, og som Claude efterfølgende kan importere, konfigurere og optimere i Unity.

Manifestet låser **funktion, identitet og handoff-kontrakt**, men ikke endelig balance, shaderimplementering eller runtime-LOD-strategi.

## Handoff-regel

- ChatGPT ejer source artwork, source textures, ikonografi, visuel reference, asset-ID og acceptance criteria.
- Claude ejer Unity-import, materialer/shaders, prefab-opsætning, colliders, LOD/runtime-optimering og performance.
- Ingen asset må bære gameplaykritisk information udelukkende gennem farve.
- Ingen private/personaliserede assets må ligge i repositoryet.

## Source master-standard

Som udgangspunkt:

- source textures: tabsfri lossless master (`PNG`/`TIF`) med transparent baggrund hvor relevant
- UI/icons: SVG eller højopløst transparent PNG; Unity-format besluttes ved import
- concept/reference: PNG/JPG
- 3D source, hvis produceret eksternt: FBX eller glTF + separate texture masters
- navngivning følger `ENV_`, `PRP_`, `ITM_`, `CHR_`, `VFX_`, `UI_`, `MAT_`, `TEX_`, `ANM_`
- source asset må ikke indeholde Unity-specifik opsætning som eneste dokumentation

---

# Prioritetskoder

- **A — gameplaykritisk:** nødvendig for M3-M5 / release 1.
- **B — fuld Stormnatten:** nødvendig for M6.
- **C — polish:** M7 eller senere.
- **P — personalization:** M8/private package.

Produktion kan være gated, men specifikationen må være klar nu.

---

# Miljø og zonesæt

| ID | Navn | Pri. | Funktion | Source-leverance | Status |
|---|---|---:|---|---|---|
| `ENV_BEACH_CAMP_001` | Strand/lejr base kit | A | Primært hubområde, intro, planning, storm | concept sheet + modular kit spec | Spec klar |
| `ENV_WRECKAGE_001` | Vrag-landmark | A | Visuelt landmark og intro-kontekst | hero prop concept + silhouette views | Mangler produktion |
| `ENV_CAMP_GROUND_001` | Lejrterræn/underlag | A | Grounding af camp, byggezoner | texture/reference set | Mangler produktion |
| `ENV_JUNGLE_PATH_001` | Junglesti kit | B | Gathering/exploration | modular foliage/rock/path spec | Mangler produktion |
| `ENV_RAVINE_001` | Kløft-kit | B | Ravine rescue | rock/ledge/rope anchor concept | Mangler produktion |
| `ENV_RIDGE_001` | Højderyg/udsigt | B | Signal-/skibsruteinformation | vista + landmark concept | Mangler produktion |
| `ENV_STORM_CAMP_001` | Stormvariant af camp | A | M5 finale | damaged/wet variant reference | Mangler produktion |
| `ENV_EPILOGUE_001` | Epilog-/lejrbålsområde | C | Efterspil/finale | mood concept | Mangler produktion |

## Miljøfamilier

Alle miljøkits skal visuelt hænge sammen via:

- håndbygget/stiliseret formgivning
- grove, tydelige silhuetter
- begrænset materialefamilie
- tydelig navigation via landmarks
- readable interaction silhouettes på Quest 2-distance

---

# Camp og konstruktion

| ID | Navn | Pri. | Gameplayfunktion | Varianter/states | Status |
|---|---|---:|---|---|---|
| `PRP_FIREPIT_001` | Lejrbål | A | Hub, save-/statuspunkt | cold / ember / small / strong | Spec klar |
| `PRP_SHELTER_FRAME_001` | Shelter frame | A | Bygge-/stormstate | stage 0-3 | Spec klar |
| `PRP_SHELTER_TARP_001` | Presenning/tagdug | A | Shelter og stormfeedback | dry / wet / torn | Spec klar |
| `PRP_SHELTER_BEAM_001` | Bærende bjælke | A | Tohåndsstabilisering | intact / damaged | Spec klar |
| `PRP_SHELTER_ROPE_001` | Shelter-reb | A | Binding/repair | loose / tensioned / tied | Spec klar |
| `PRP_SIGNAL_FRAME_001` | Signalstativ | A | Finaleprogression | stage 0-3 | Spec klar |
| `PRP_SIGNAL_FUEL_001` | Signalbrændsel | A | Final signal | dry / wet | Mangler produktion |
| `PRP_PLAN_TABLE_001` | Planlægningsbord | A | Fire effort markers/cards | neutral table + snap areas | Spec klar |
| `PRP_RADIO_001` | Radio | A | Narrative/status/finale | dead / weak / active | Spec klar |
| `PRP_HEAVY_CRATE_001` | Tung kasse | A | Intro + kollapsgenbrug | closed / opened | Spec klar |
| `PRP_SUPPLY_CRATE_001` | Forsyningskasse | B | Shared resources | open / sealed | Mangler produktion |
| `PRP_WATERPROOF_ENDING_CRATE_001` | Vandtæt finalekasse | P | Personalization hook | neutral / personal | Spec klar |

---

# Ressourcer og items

| ID | Navn | Pri. | Gameplayfunktion | Readability-krav | Status |
|---|---|---:|---|---|---|
| `ITM_WOOD_BUNDLE_001` | Træbundt | A | Ild/shelter | stor mørk silhuet, bundtform | Mangler produktion |
| `ITM_FIBER_BUNDLE_001` | Fiberbundt | B | Reb/binding | flettet/lys form | Mangler produktion |
| `ITM_FOOD_PARCEL_001` | Mad/forsyning | A | Food security | lukket pose/kasse; ikke små items | Mangler produktion |
| `ITM_HERB_BUNDLE_001` | Urter | B | Behandling | ikonisk bladform + labelform | Mangler produktion |
| `ITM_GENERAL_SUPPLIES_001` | Supplies bundle | A | General resource pool | tydeligt generisk kit | Mangler produktion |
| `ITM_EMBER_CARRIER_001` | Gløde-/ildbærer | A | Signal-finale | lys/varme + fysisk skærm | Spec klar |
| `ITM_TINDER_001` | Tinder/tørt materiale | A | Fire-start | stort, gribbart bundt | Mangler produktion |
| `ITM_CLOTH_001` | Klud | A | Intro/crafting | foldet, tydelig tekstilform | Mangler produktion |
| `ITM_MAP_FRAGMENT_001` | Kortfragment | A | Intro/narrative | stor læsbar grafisk flade | Mangler produktion |
| `ITM_RADIO_BATTERY_001` | Radio-strømkilde | B | Narrative progression | tydelig socket-form | Mangler produktion |

---

# Værktøjer og interaktionsprops

| ID | Navn | Pri. | Funktion | Designkrav | Status |
|---|---|---:|---|---|---|
| `ITM_FIRESTEEL_001` | Ildstål | A | Fire-start | overdimensioneret greb, tydelig strike-zone | Spec klar |
| `ITM_KNIFE_001` | Kniv/værktøj | B | Crafting/fiber | utility-look, ikke våbenfokus | Mangler produktion |
| `ITM_HAMMER_001` | Hammer/mallet | B | Repair/build | stor kontaktflade | Mangler produktion |
| `ITM_ROPE_COIL_001` | Rebspole | A | Binding/ravine | stor coil, tydelig endeføring | Spec klar |
| `PRP_RAVINE_ANCHOR_001` | Reb-anker | B | Rescue | høj visuel kontrast/form | Mangler produktion |
| `PRP_RAVINE_GUIDE_MARKERS_001` | Sikre greb/markører | B | Sekundær rolle | form + ikon, ikke farve-only | Mangler produktion |
| `PRP_WIND_SHIELD_001` | Ild-/glødeskærm | A | Fire/storm | kan holdes med én/two hands | Mangler produktion |
| `PRP_DRY_FUEL_CACHE_001` | Tørt brændsel-cache | A | Storm phase 2 | tydeligt shelter fra regn | Mangler produktion |

---

# Planlægning og diegetisk UI

| ID | Navn | Pri. | Funktion | Source-design | Status |
|---|---|---:|---|---|---|
| `UI_EFFORT_MARKER_P1_001` | Spiller 1 effort marker | A | Planning | fysisk token + symbol | Spec klar |
| `UI_EFFORT_MARKER_P2_001` | Spiller 2 effort marker | A | Planning | fysisk token + andet symbol | Spec klar |
| `UI_ACTION_CARD_BASE_001` | Action card base | A | Planning | titel, cost, risk, outcome hint | Spec klar |
| `UI_ACTION_ICON_SHELTER_001` | Shelter ikon | A | Planning/status | formstærkt ikon | Mangler produktion |
| `UI_ACTION_ICON_FIRE_001` | Fire ikon | A | Planning/status | formstærkt ikon | Mangler produktion |
| `UI_ACTION_ICON_FOOD_001` | Food ikon | A | Planning/status | formstærkt ikon | Mangler produktion |
| `UI_ACTION_ICON_SIGNAL_001` | Signal ikon | A | Planning/status | formstærkt ikon | Mangler produktion |
| `UI_ACTION_ICON_MEDICAL_001` | Medical ikon | B | Planning/status | formstærkt ikon | Mangler produktion |
| `UI_ACTION_ICON_EXPLORE_001` | Explore ikon | B | Planning/status | formstærkt ikon | Mangler produktion |
| `UI_WRIST_STATUS_FRAME_001` | Armbånd/statusramme | A | Player status | simple slots, high contrast | Spec klar |
| `UI_STATUS_HEALTH_001` | Health ikon | B | Player state | ikon + form | Mangler produktion |
| `UI_STATUS_FATIGUE_001` | Fatigue ikon | B | Player state | ikon + form | Mangler produktion |
| `UI_STATUS_WET_COLD_001` | Wet/cold ikon | B | Modifier | ikon + form | Mangler produktion |
| `UI_STATUS_INJURY_001` | Injury ikon | B | Injury | ikon + form | Mangler produktion |
| `UI_JOIN_CODE_PANEL_001` | Join-code visual frame | A | Lobby | læsbar 5-6 chars | Spec klar |
| `UI_RECONNECT_PANEL_001` | Reconnect/pause visual | A | Failure flow | rolig, tydelig state | Mangler produktion |

---

# Feedback-decals og world cues

| ID | Navn | Pri. | Funktion | Status |
|---|---|---:|---|---|
| `TEX_SNAP_PREVIEW_001` | Magnetisk snap-preview | A | Placement feedback | Mangler produktion |
| `TEX_GRIP_INVITE_001` | Grip/invite markering | A | Onboarding | Mangler produktion |
| `TEX_TENSION_GUIDE_001` | Rope tension guide | A | Coop feedback | Mangler produktion |
| `TEX_REPAIR_NODE_001` | Repair node cue | A | Storm repair | Mangler produktion |
| `TEX_WARNING_SHAPE_001` | Advarselssymbol | A | Error/risk | Mangler produktion |
| `TEX_SUCCESS_SHAPE_001` | Success-symbol | A | Confirmation | Mangler produktion |
| `TEX_PARTIAL_SHAPE_001` | Partial-success-symbol | B | Outcome | Mangler produktion |

---

# VFX source/reference-pakke

ChatGPT leverer look/reference og source textures/sprites; Claude bygger runtime-systemet.

| ID | Cue | Pri. | Source-leverance | Status |
|---|---|---:|---|---|
| `VFX_RAIN_001` | Regn | A | droplet/streak texture + density reference | Mangler |
| `VFX_WIND_DEBRIS_001` | Vinddebris | A | leaf/debris sprite sheet + motion ref | Mangler |
| `VFX_FIRE_EMBERS_001` | Gløder | A | ember sprite + state ref | Mangler |
| `VFX_FIRE_SMOKE_001` | Røg | A | smoke sprites + intensity ref | Mangler |
| `VFX_ROPE_STRAIN_001` | Rebspænding | B | dust/fiber cue ref | Mangler |
| `VFX_IMPACT_001` | Impact/build hit | B | small impact sprite set | Mangler |
| `VFX_WETNESS_REFERENCE_001` | Wetness look | A | dry→wet reference board | Mangler |
| `VFX_STORM_PHASE_REF_001` | Storm intensitetsguide | A | phase 0-3 visual target sheet | Mangler |

---

# Avatar/source identity

| ID | Navn | Pri. | Krav | Status |
|---|---|---:|---|---|
| `CHR_HAND_P1_001` | Player 1 hands | A | stiliseret, symbol A, neutral hud/handwear | Mangler |
| `CHR_HAND_P2_001` | Player 2 hands | A | stiliseret, symbol B, neutral hud/handwear | Mangler |
| `CHR_TORSO_BASE_001` | Simple torso | C | enkel silhouette, ingen Meta Avatar-afhængighed | Mangler |
| `UI_PLAYER_SYMBOL_A_001` | Player symbol A | A | farve + unik shape | Mangler |
| `UI_PLAYER_SYMBOL_B_001` | Player symbol B | A | farve + unik shape | Mangler |

---

# Personalization hooks — source placeholders

Private filer produceres/lagres uden for repo. Her dokumenteres kun hooket.

| Hook | Neutral fallback | Privat source-type | Krav |
|---|---|---|---|
| `ENDING_CRATE_PHOTO` | neutralt island/skibsfoto | billede | crop-safe, ingen metadata nødvendig |
| `RADIO_FINAL_MESSAGE` | neutral rescue-message | audio | kort, max ca. 90 sek finale samlet |
| `CAMP_MEMENTO_1` | generisk kompas/memento | billede/prop-ref | må ikke ændre balance |
| `CAMP_MEMENTO_2` | generisk billet/kort | billede/prop-ref | optional |
| `CAMP_MEMENTO_3` | generisk souvenir | billede/prop-ref | optional |

Detaljer: `docs/41_PERSONALIZATION_PACKAGE_SPEC.md`.

---

# Materiale-/texturefamilier

Disse er source-designfamilier; Unity-master-materialer tilhører Claude.

| ID | Familie | Anvendelse | Source-behov |
|---|---|---|---|
| `MAT_FAMILY_WOOD_001` | weathered wood | shelter, wreck, signal | albedo/roughness look refs + packed-mask source |
| `MAT_FAMILY_ROPE_001` | fiber/rope | bindings, rescue | texture master + tension variation |
| `MAT_FAMILY_CLOTH_001` | tarp/cloth | shelter, packs | dry/wet/torn refs |
| `MAT_FAMILY_ROCK_001` | island rock | ravine/ridge | 2-3 tiling source variants |
| `MAT_FAMILY_SAND_001` | beach/sand | camp | tiling source + footprint/readability ref |
| `MAT_FAMILY_FOLIAGE_001` | tropical foliage | jungle | atlas source + silhouette set |
| `MAT_FAMILY_METAL_001` | worn utility metal | radio/tools/crates | limited shared set |

---

# Asset acceptance criteria

Et source asset er **klar til Claude-handoff**, når:

1. ID og filnavn matcher manifestet.
2. Gameplayfunktion er kendt.
3. Front/side/silhouette eller relevant 2D-master er tydelig.
4. Alle gameplaykritiske states er repræsenteret.
5. Ingen nødvendig information er color-only.
6. Privat/licensbegrænset materiale er mærket korrekt.
7. Provenance er registreret i `docs/43_IP_AND_ASSET_PROVENANCE.md`.
8. Source master er bevaret; Unity-optimeret afledt fil er ikke eneste kopi.
9. Claude kan forstå ønsket state/brug uden at skulle opfinde designet.

## Ikke acceptance criteria for ChatGPT

Følgende tilhører Claude og afgør ikke source-asset-færdighed:

- Unity import settings
- shader choice
- material instancing
- runtime compression
- mipmaps
- collider/prefab setup
- actual LOD implementation
- draw-call/performance tuning

---

# Produktionsrækkefølge

Når relevant gate åbner assetproduktion:

1. **A1 — gameplay readable:** markers, action cards, heavy crate, fire, shelter, signal, rope, key icons.
2. **A2 — release 1 environment:** camp/wreck + storm state.
3. **A3 — release 1 feedback:** snap/grip/repair cues + storm VFX source.
4. **B — full scenario:** jungle, ravine, ridge, extended resources.
5. **C — polish:** avatar/torso, richer environment variation.
6. **P — private personalization:** kun i privat package, aldrig i repo.

Denne rækkefølge kan ændres efter M-Pre/M3-evidens, men manifestet giver nu et konkret produktionsgrundlag i stedet for “lav alt grafik”.
