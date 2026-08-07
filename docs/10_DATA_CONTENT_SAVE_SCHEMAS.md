# Data-, content- og save-specifikation

## Princip

Game design-data skal kunne ændres uden at omskrive netværks- eller interaktionskode. Unity ScriptableObjects er authoring-format; JSON-skemaer i `/schemas` beskriver den logiske kontrakt og bruges til review, validering og eventuel tooling.

## ID-regler

- Scenario: `SCN_<NAME>_<NNN>`.
- Event: `EVT_<NAME>_<NNN>`.
- Item: `ITM_<NAME>_<NNN>`.
- Recipe: `RCP_<NAME>_<NNN>`.
- Interaction: `INT_<NAME>_<NNN>`.
- Localization key: `<DOMAIN>.<ID>.<FIELD>`.

IDs ændres aldrig efter at saves/testcases refererer til dem.

## ScenarioDefinition

Indeholder:

- id/version/display key.
- player count.
- supported build protocol.
- phase graph.
- initial state.
- action catalog.
- event pools.
- win/lose rules.
- checkpoints.
- personalization hooks.

## EventDefinition

- trigger conditions.
- priority/cooldown.
- immediate effects.
- choices.
- tags.
- delayed effects.
- presentation sequence.
- fallback if required asset missing.

## ItemDefinition

- category, mass class og hand mode.
- stackability.
- network interaction type.
- gameplay tags.
- durability/tool quality.
- prefab references per quality profile.

## RecipeDefinition

- ingredients.
- station.
- interaction steps.
- parallel roles.
- result quality thresholds.
- failure/partial outcomes.

## PersonalizationProfile

- profile ID.
- display names.
- text keys/overrides.
- image/audio asset references.
- final message.
- internal reference props.
- neutral fallback mapping.

Profilen må ikke ændre balance eller netværksprotokol.

## Save schema

Save er checkpoint, ikke continuous physics save.

Felter:

- schema version.
- game/protocol/content versions.
- scenario and seed.
- current checkpoint/phase.
- shared resources and camp.
- player states.
- persistent object logical states.
- tags and delayed queue.
- completed actions.
- deterministic RNG cursor where needed.
- revision (monotont voksende, påkrævet — resync i `docs/07` §11 afhænger af den).
- checksum.

### Checksum-definition

Uden en defineret dækning er checksummen dekoration. Reglen er:

1. Fjern feltet `checksum` fra objektet.
2. Serialisér resten som kanonisk JSON: sorterede nøgler, ingen whitespace, UTF-8.
3. `SHA-256` over den byte-streng, gengivet som 64 hexadecimale tegn i lowercase.

`examples/savegame.example.json` indeholder en checksum beregnet efter præcis denne regel og kan bruges som testvektor.

## Migration

- Minor additive felter får defaults.
- Breaking ændring kræver migrator `vN -> vN+1`.
- Development builds kan wipe incompatible saves med tydelig besked.
- Gift release skal kunne bevare sidste stabile checkpoint gennem patch-opdateringer inden for samme major version.

## Effects og outcomeThresholds

`effects` afbilder `actionId → udfaldstier → effekt`. En effekt kan indeholde `resourceDeltas`, `campDeltas`, `addTags`, `removeTags` og `fatigueCost`.

Kontrakten er hård af to grunde:

- **Alle fire tiers skal være til stede for hver handling i `actionCatalog`.** En manglende `failForward` opdages ellers først, når to spillere står og undrer sig over, at intet skete.
- **Ingen effekt må være tom.** `docs/04` §9 forbyder "ingen effekt" — fejl skal have fremdrift.

`outcomeThresholds` (`partial` < `success` < `critical`) ligger i data, så balancering ikke kræver rebuild. Se `docs/33` for hvorfor de nuværende værdier er, som de er — de blev målt, ikke valgt.

**Værdierne i `examples/stormnatten.scenario.json` er placeholdere til validering, ikke balancering.** Rigtige tal kan først sættes, når nogen har spillet en dag igennem (M3).

## Content validation

Build stopper ved:

- action-ID i `phases[].actions` uden tilsvarende post i `actionCatalog`.
- `supportedBuildProtocol` der ikke matcher buildets `NetworkProtocolVersion`.
- duplicate IDs.
- missing localization key.
- event cycle uden exit.
- recipe step uden role.
- missing fallback prefab.
- personalization asset over size limit.
- checkpoint med ikke-serializable critical state.

## Eksempler

Se:

- `examples/stormnatten.scenario.json`
- `examples/open_food_attracts_animal.event.json`
- `examples/shelter_reinforcement.recipe.json`
- `examples/personalization_profile.example.json`
