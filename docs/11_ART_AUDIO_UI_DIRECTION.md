# Art-, audio- og UI-retning

## Visuel identitet

En stiliseret, håndbygget eventyrø: grove former, tydelige silhuetter, varme lejrbålsfarver og dramatiske vejromslag. Ikke fotorealisme og ikke tegnefilmsfjollet.

## Farvefamilier

- Camp/tryghed: rav, sand, dæmpet grøn.
- Udforskning: kølig grøn, blågrå skygge.
- Fare/storm: lav mætning, blågrå og rust-accenter.
- Interaktion: varm hvid/guld plus ikonform.
- Fejl: rust/rød plus knæk-/advarselsform.

## Materialestrategi

- Få shared master materials.
- Vertex colors og packed masks frem for mange unikke shaders.
- Wind animation via simple vertex offset.
- Wetness via global parameter, ikke individuelle dyre materialer.
- Quest 1 fallback uden dyre shader features.

## Miljø

Hver zone har ét navigationslandmark:

- Lejr: stort vrag/lejrbål.
- Jungle: skævt træ/stenport.
- Kløft: signalmast eller klippeprofil.
- Højderyg: udsigt og skibsrute.

## Avatarer

MVP:

- Hoved/hænder og enkel torso.
- Tydelig spillerfarve + symbol.
- Ingen Meta Avatars SDK-afhængighed.
- Arm IK kun hvis stabilt og billigt; ellers stiliserede floating hands.

## VFX

- Regn, vinddebris, gnister, røg og simple impact cues.
- Stormintensitet styres globalt.
- Partikler er kosmetik og må droppes pr. profile uden gameplaytab.

## Audio

Audio bærer øens reaktion:

- 3D ambience per zone.
- Vindlag i intensitetsniveauer.
- Tagknirken og rebspænding som gameplay feedback.
- Lejrbål giver status gennem lyd.
- Dyr antydes ofte før de ses.

Vigtige cues har både lyd og visuel feedback.

## Musik

- Minimal adaptiv musik.
- Lejrbål: varm, enkel tekstur.
- Varsel: lav puls.
- Storm: lag der følger phase og camp state.
- Finale: musik åbner først, når signalet lykkes.

## Voice

- Korte radio-/fortællerlinjer.
- Ingen lang exposition.
- Personlig voice ligger i separat profile.
- Alle linjer har undertekster og neutral fallback.

## UI style

- Fysiske kort, markører, armbånd og radio.
- Menuer ligner enkle feltjournal-sider, men prioriterer læsbarhed.
- Store targets og ingen små desktop-lignende knapper.

## Asset naming

`ENV_`, `PRP_`, `ITM_`, `CHR_`, `VFX_`, `SFX_`, `UI_`, `MAT_`, `TEX_`, `ANM_`.

## Art gate

Ingen dyr art-produktion før greybox vertical slice er sjov. Købte assets må modificeres til fælles stil og må ikke definere gameplayarkitekturen.
