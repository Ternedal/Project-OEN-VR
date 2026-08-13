# Stormnatten action source

This folder separates **player-facing/action semantics** from **current placeholder balance values**.

## Files

### `stormnatten.actions.source.json`

Authoring source for:

- action IDs
- localization keys
- icon IDs
- category
- qualitative gain/risk intent
- primary/secondary role intent

Its current embedded `effortCost` fields are **deprecated as balance authority**. They were introduced during authoring and must not be consumed as canonical costs.

### `current_placeholder_costs.source.json`

The explicit mirror of the **current placeholder costs** in `examples/stormnatten.scenario.json`:

- wood 1
- food 1
- shelter 2
- cliff 1
- secure supplies 1
- reinforce roof 2
- fiber 1
- herbs 1
- signal 2
- ridge 1
- treat injury 1

These are still **not final balance**. `docs/10_DATA_CONTENT_SAVE_SCHEMAS.md` states that final balancing waits for M3.

## Consumption rule

Until the action source is normalized in a later atomic cleanup:

- use `stormnatten.actions.source.json` for content/card semantics
- use scenario data / `current_placeholder_costs.source.json` for current placeholder effort cost
- do not infer final balance from either

This explicit split prevents the authoring layer from silently overriding the existing scenario example.
