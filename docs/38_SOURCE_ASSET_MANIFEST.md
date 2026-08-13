# Source asset manifest — PROJECT ØEN

**Ejer:** ChatGPT  
**Unity-integration:** Claude  
**Dato:** 2026-08-13  
**Status:** Autoritativ source-asset oversigt; runtime/release-status ligger ikke her

## Formål

Dette er den autoritative funktions-/ID-liste over **source assets**, som ChatGPT definerer eller producerer uden for Unity, og som Claude efterfølgende kan importere, konfigurere og optimere i Unity.

Den aktuelle machine-readable produktionsstatus findes i `content/source_inventory.source.json`.

Manifestet låser **funktion, identitet og handoff-kontrakt**, men ikke endelig balance, shaderimplementering, collider, prefab eller runtime-LOD-strategi.

## Handoff-regel

- ChatGPT ejer source artwork, source textures, ikonografi, visuel reference, asset-ID og acceptance criteria.
- Claude ejer Unity-import, materialer/shaders, prefab-opsætning, colliders, LOD/runtime-optimering og performance.
- Ingen asset må bære gameplaykritisk information udelukkende gennem farve.
- Ingen private/personaliserede assets må ligge i repositoryet.

## Statusord

- **Source master produceret** — konkret import-/afledningsklar sourcefil findes.
- **Source reference produceret** — konkret concept/state/readability-reference findes; final 3D/world asset er stadig Claude-/senere produktionsarbejde.
- **Spec klar** — designkontrakten findes, men konkret source master/reference mangler endnu.
- **Mangler produktion** — sourcearbejde er stadig åbent.
- **Gated** — source kan eksistere, men gameplaybrug må ikke gøres canonical før navngiven gate/beslutning.

Ingen af disse statusser betyder automatisk **Unity-integreret** eller **release approved**.

## Source master-standard

Som udgangspunkt:

- source textures: lossless master (`PNG`/`TIF`) med transparent baggrund hvor relevant
- UI/icons: SVG eller højopløst transparent PNG; Unity-format besluttes ved import
- concept/reference: SVG/PNG/JPG
- 3D source: OBJ, FBX eller glTF afhængigt af asset og kompleksitet; textures bevares separat hvor relevant
- navngivning følger `ENV_`, `PRP_`, `ITM_`, `CHR_`, `VFX_`, `UI_`, `MAT_`, `TEX_`, `ANM_`
- source asset må ikke indeholde Unity-specifik opsætning som eneste dokumentation

---

# Prioritetskoder

- **A — gameplaykritisk:** nødvendig for M3-M5 / release 1.
- **B — fuld Stormnatten:** nødvendig for M6.
- **C — polish:** M7 eller senere.
- **P — personalization:** M8/private package.

Produktion kan være gated, men specifikationen må være klar tidligere.

---

# Miljø og zonesæt

| ID | Navn | Pri. | Funktion | Source-leverance | Status |
|---|---|---:|---|---|---|
| `ENV_BEACH_CAMP_001` | Strand/lejr base kit | A | Primært hubområde, intro, planning, storm | layout/state/reference | **Source reference produceret** (`source_art/environment/a4/`) |
| `ENV_WRECKAGE_001` | Vrag-landmark | A | Visuelt landmark og intro-kontekst | hero silhouette/reference | **Source reference produceret** |
| `ENV_CAMP_GROUND_001` | Lejrterræn/underlag | A | Grounding af camp, byggezoner | dry/wet material/readability ref | **Source reference produceret** |
| `ENV_JUNGLE_PATH_001` | Junglesti kit | B | Gathering/exploration | path/readability reference | **Source reference produceret** (`source_art/environment/b1/`) |
| `ENV_RAVINE_001` | Kløft-kit | B | Ravine rescue | route/role/readability reference | **Source reference produceret** |
| `ENV_RIDGE_001` | Højderyg/udsigt | B | Signal-/skibsruteinformation | vista/readability reference | **Source reference produceret** |
| `ENV_STORM_CAMP_001` | Stormvariant af camp | A | M5 finale | damaged/wet state reference | **Source reference produceret** via A4 camp-state/A3 storm refs |
| `ENV_EPILOGUE_001` | Epilog-/lejrbålsområde | C | Efterspil/finale | mood/world concept | **Spec klar**; neutral ending-content produceret separat |

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
| `PRP_FIREPIT_001` | Lejrbål | A | Hub, save-/statuspunkt | cold / ember / small / strong | **Source reference produceret** (A2 concept/state) |
| `PRP_SHELTER_FRAME_001` | Shelter frame | A | Bygge-/stormstate | stage 0-3 | **Source reference produceret** |
| `PRP_SHELTER_TARP_001` | Presenning/tagdug | A | Shelter og stormfeedback | dry / wet / torn | **Source reference produceret** |
| `PRP_SHELTER_BEAM_001` | Bærende bjælke | A | Tohåndsstabilisering | intact / damaged | **Source reference produceret** |
| `PRP_SHELTER_ROPE_001` | Shelter-reb | A | Binding/repair | loose / tensioned / tied | **Source reference produceret** |
| `PRP_SIGNAL_FRAME_001` | Signalstativ | A | Finaleprogression | stage 0-3 | **Source reference produceret** (`SIGNAL_FRAME_REFERENCE_001.svg`) |
| `PRP_SIGNAL_FUEL_001` | Signalbrændsel | A | Final signal | dry / wet | **Source master produceret** (`source_art/props/a5/PRP_SIGNAL_FUEL_001.obj`) |
| `PRP_PLAN_TABLE_001` | Planlægningsbord | A | Fire effort markers/cards | neutral table + snap areas | **Source reference produceret** (A2 concept) |
| `PRP_RADIO_001` | Radio | A | Narrative/status/finale | dead / weak / active | **Source reference produceret** (`RADIO_SOURCE_REFERENCE_001.svg`) |
| `PRP_HEAVY_CRATE_001` | Tung kasse | A | Intro + kollapsgenbrug | closed / opened | **Source reference produceret** (A2 concept) |
| `PRP_SUPPLY_CRATE_001` | Forsyningskasse | B | Shared resources | open / sealed | **Source master produceret** (`source_art/props/b1/`) |
| `PRP_WATERPROOF_ENDING_CRATE_001` | Vandtæt finalekasse | P | Personalization hook | neutral / personal | **Spec klar**; neutral indholdspakke produceret |

---

# Ressourcer og items

| ID | Navn | Pri. | Gameplayfunktion | Readability-krav | Status |
|---|---|---:|---|---|---|
| `ITM_WOOD_BUNDLE_001` | Træbundt | A | Ild/shelter | stor mørk silhuet, bundtform | **Source master produceret** |
| `ITM_FIBER_BUNDLE_001` | Fiberbundt | B | Reb/binding | flettet/lys form | **Source master produceret** |
| `ITM_FOOD_PARCEL_001` | Mad/forsyning | A | Food security | lukket pose/kasse; ikke små items | **Source master produceret** |
| `ITM_HERB_BUNDLE_001` | Urter | B | Behandling | ikonisk bladform + labelform | **Source master produceret** |
| `ITM_GENERAL_SUPPLIES_001` | Supplies bundle | A | General resource pool | tydeligt generisk kit | **Source master produceret** |
| `ITM_EMBER_CARRIER_001` | Gløde-/ildbærer | A | Signal-finale | tydelig bærer/state | **Spec klar; source master ikke committed** |
| `ITM_TINDER_001` | Tinder/tørt materiale | A | Fire-start | stort, gribbart bundt | **Source master produceret** (`source_art/props/a2/`) |
| `ITM_CLOTH_001` | Klud | A | Intro/crafting | foldet, tydelig tekstilform | **Source master produceret** |
| `ITM_MAP_FRAGMENT_001` | Kortfragment | A | Intro/narrative | stor læsbar grafisk flade | **Source master produceret** |
| `ITM_RADIO_BATTERY_001` | Radio-strømkilde | B | Narrative progression | tydelig socket-form | **Source master produceret** |

---

# Værktøjer og interaktionsprops

| ID | Navn | Pri. | Funktion | Designkrav | Status |
|---|---|---:|---|---|---|
| `ITM_FIRESTEEL_001` | Ildstål | A | Fire-start | overdimensioneret greb, tydelig strike-zone | **Source master produceret / Gated af issue #8** |
| `ITM_KNIFE_001` | Kniv/værktøj | B | Crafting/fiber | utility-look, ikke våbenfokus | **Mangler produktion** |
| `ITM_HAMMER_001` | Hammer/mallet | B | Repair/build | stor kontaktflade | **Spec klar; source master ikke committed** |
| `ITM_ROPE_COIL_001` | Rebspole | A | Binding/ravine | stor coil, tydelig endeføring | **Source master produceret** |
| `PRP_RAVINE_ANCHOR_001` | Reb-anker | B | Rescue | høj visuel kontrast/form | **Source master produceret** (`source_art/environment/b1/`) |
| `PRP_RAVINE_GUIDE_MARKERS_001` | Sikre greb/markører | B | Sekundær rolle | form + ikon, ikke farve-only | **Source master produceret** |
| `PRP_WIND_SHIELD_001` | Ild-/glødeskærm | A | Fire/storm | stor fysisk skærm | **Source master produceret** (`source_art/props/a5/*.obj`) |
| `PRP_DRY_FUEL_CACHE_001` | Tørt brændsel-cache | A | Storm phase 2 | tydelig beskyttet cache | **Source master produceret** (`source_art/props/a5/*.obj`) |

---

# Planlægning, status og release UI

| ID | Navn | Pri. | Funktion | Source-design | Status |
|---|---|---:|---|---|---|
| `UI_EFFORT_MARKER_P1_001` | Spiller 1 effort marker | A | Planning | fysisk token + symbol | **Source master produceret** |
| `UI_EFFORT_MARKER_P2_001` | Spiller 2 effort marker | A | Planning | fysisk token + andet symbol | **Source master produceret** |
| `UI_ACTION_CARD_BASE_001` | Action card base | A | Planning | titel, cost, risk, outcome hint | **Source master produceret** |
| `UI_ACTION_ICON_SHELTER_001` | Shelter ikon | A | Planning/status | formstærkt ikon | **Source master produceret** |
| `UI_ACTION_ICON_FIRE_001` | Fire ikon | A | Planning/status | formstærkt ikon | **Source master produceret** |
| `UI_ACTION_ICON_FOOD_001` | Food ikon | A | Planning/status | formstærkt ikon | **Source master produceret** |
| `UI_ACTION_ICON_SIGNAL_001` | Signal ikon | A | Planning/status | formstærkt ikon | **Source master produceret** |
| `UI_ACTION_ICON_MEDICAL_001` | Medical ikon | B | Planning/status | formstærkt ikon | **Source master produceret** |
| `UI_ACTION_ICON_EXPLORE_001` | Explore ikon | B | Planning/status | formstærkt ikon | **Source master produceret** |
| `UI_WRIST_STATUS_FRAME_001` | Armbånd/statusramme | A | Player status | simple slots, high contrast | **Source master produceret** |
| `UI_STATUS_HEALTH_001` | Health ikon | B | Player state | ikon + form | **Source master produceret** |
| `UI_STATUS_FATIGUE_001` | Fatigue ikon | B | Player state | ikon + form | **Source master produceret** |
| `UI_STATUS_WET_COLD_001` | Wet/cold ikon | B | Modifier | ikon + form | **Source master produceret** |
| `UI_STATUS_INJURY_001` | Injury ikon | B | Injury | ikon + form | **Source master produceret** |
| `UI_JOIN_CODE_PANEL_001` | Join-code visual frame | A | Lobby | læsbar kode | **Source master produceret** |
| `UI_RECONNECT_PANEL_001` | Reconnect visual | A | Failure flow | rolig, tydelig state | **Source master produceret** |
| `UI_FIRST_LAUNCH_SETUP_001` | First-launch setup | A | seated/standing + handedness | enkel setup hierarchy | **Source master produceret** |
| `UI_PAUSE_PANEL_001` | Pause panel | A | resume/settings/recovery | release hierarchy | **Source master produceret** |
| `UI_CONNECTED_READY_001` | Connected/ready panel | A | P1/P2 + ready | shape + text identity | **Source master produceret** |
| `UI_SUBTITLE_BAND_001` | Subtitle band | A | tale/subtitle parity | speaker + 1–2 linjer | **Source master produceret** |

---

# Feedback-decals og world cues

| ID | Navn | Pri. | Funktion | Status |
|---|---|---:|---|---|
| `TEX_SNAP_PREVIEW_001` | Magnetisk snap-preview | A | Placement feedback | **Source master produceret** |
| `TEX_GRIP_INVITE_001` | Grip/invite markering | A | Onboarding | **Source master produceret** |
| `TEX_TENSION_GUIDE_001` | Rope tension guide | A | Coop feedback | **Source master produceret** |
| `TEX_REPAIR_NODE_001` | Repair node cue | A | Storm repair | **Source master produceret** |
| `TEX_WARNING_SHAPE_001` | Advarselssymbol | A | Error/risk | **Source master produceret** |
| `TEX_SUCCESS_SHAPE_001` | Success-symbol | A | Confirmation | **Source master produceret** |
| `TEX_PARTIAL_SHAPE_001` | Partial-success-symbol | B | Outcome | **Source master produceret** |

---

# VFX source/reference-pakke

ChatGPT leverer look/reference og source textures/sprites; Claude bygger runtime-systemet.

| ID | Cue | Pri. | Source-leverance | Status |
|---|---|---:|---|---|
| `VFX_RAIN_001` | Regn | A | droplet/streak source + density reference | **Source master/reference produceret** |
| `VFX_WIND_DEBRIS_001` | Vinddebris | A | debris source + motion ref | **Source master/reference produceret** |
| `VFX_FIRE_EMBERS_001` | Gløder | A | ember source + state ref | **Source master/reference produceret** |
| `VFX_FIRE_SMOKE_001` | Røg | A | smoke source + intensity ref | **Source master/reference produceret** |
| `VFX_ROPE_STRAIN_001` | Rebspænding | B | dust/fiber cue ref | **Mangler særskilt VFX-source**; UI tension cue findes |
| `VFX_IMPACT_001` | Impact/build hit | B | small impact source set | **Source master/reference produceret** |
| `VFX_WETNESS_REFERENCE_001` | Wetness look | A | dry→wet reference board | **Source reference produceret** |
| `VFX_STORM_PHASE_REF_001` | Storm intensitetsguide | A | phase visual target sheet | **Source reference produceret** |

---

# Avatar/source identity

| ID | Navn | Pri. | Krav | Status |
|---|---|---:|---|---|
| `CHR_HAND_P1_001` | Player 1 hands | A | stiliseret, symbol A, neutral hud/handwear | **Mangler produktion** |
| `CHR_HAND_P2_001` | Player 2 hands | A | stiliseret, symbol B, neutral hud/handwear | **Mangler produktion** |
| `CHR_TORSO_BASE_001` | Simple torso | C | enkel silhouette, ingen Meta Avatar-afhængighed | **Mangler produktion** |
| `UI_PLAYER_SYMBOL_A_001` | Player symbol A | A | farve + unik shape | **Source master produceret** |
| `UI_PLAYER_SYMBOL_B_001` | Player symbol B | A | farve + unik shape | **Source master produceret** |

---

# Personalization hooks — source placeholders

Private filer produceres/lagres uden for repo. Her dokumenteres kun hooket.

| Hook | Neutral fallback | Privat source-type | Status/krav |
|---|---|---|---|
| `ENDING_CRATE_PHOTO` | `NEU_ENDING_CHART_001` | billede | neutral source produceret; privat hook senere |
| `RADIO_FINAL_MESSAGE` | neutral rescue-message | audio | copy + recording queue klar; faktisk recording mangler |
| `CAMP_MEMENTO_1` | `NEU_MEMENTO_COMPASS_001` | billede/prop-ref | neutral source produceret |
| `CAMP_MEMENTO_2` | `NEU_MEMENTO_ROUTE_CARD_001` | billede/prop-ref | neutral source produceret |
| `CAMP_MEMENTO_3` | `NEU_MEMENTO_SIGNAL_TAG_001` | billede/prop-ref | neutral source produceret |

Detaljer: `docs/41_PERSONALIZATION_PACKAGE_SPEC.md` og `docs/54_NEUTRAL_FALLBACK_PACKAGE.md`.

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

Materialefamilierne er fortsat primært **retning/reference**; final Unity materials/shaders er Claude-ejet.

---

# Asset acceptance criteria

Et source asset er **klar til Claude-handoff**, når:

1. ID og filnavn/coverage matcher manifestet eller en dokumenteret referencepakke.
2. Gameplayfunktion er kendt.
3. Front/side/silhouette eller relevant 2D/master/reference er tydelig.
4. Alle gameplaykritiske states er repræsenteret.
5. Ingen nødvendig information er color-only.
6. Privat/licensbegrænset materiale er mærket korrekt.
7. Provenance følger `docs/43_IP_AND_ASSET_PROVENANCE.md` og relevant per-pack `PROVENANCE.md`.
8. Source master/reference er bevaret; Unity-optimeret afledt fil er ikke eneste kopi.
9. Claude kan forstå ønsket state/brug uden at skulle opfinde produktdesignet.

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

Aktuel source-batchlogik:

1. **A1 — gameplay-readable UI/feedback:** produceret source-set.
2. **A2 — core interactions/props:** briefs/concepts + udvalgte individuelle masters; fortsætter hvor det reducerer Unity-gætteri.
3. **A3 — storm source:** produceret reference/source-set; runtime VFX hos Claude.
4. **A4 — release 1 camp:** layout/state/wreck/ground/radio/signal reference produceret; richer final world art venter stabil geometry.
5. **B1 — full-scenario environment/world:** jungle/ravine/ridge/resources + supply crate; fortsat delvis sourceproduktion.
6. **B2 — events:** presentation source + mapping produceret.
7. **C — polish:** avatar/torso og richer variation efter geometry/performance evidence.
8. **P — private personalization:** kun i privat package, aldrig i public repo.

M-Pre/M3/device-evidens kan ændre timing og final polish, men den må ikke få produceret source til at blive markeret som “mangler” igen.
