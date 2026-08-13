# Issue #8 — canonical content resolution

**Owner:** ChatGPT / product-content  
**Runtime owner:** Claude  
**Status:** Intro + Day 3 resolved; fire-start owner gate remains open

## Canonical source of truth

Use these files for product/content semantics:

- `content/onboarding/stormnatten.onboarding.source.json`
- `content/phases/stormnatten.day3_planning.source.json`
- `content/contracts/issue8.reconciliation.source.json`

The older files under `content/proposals/` remain proposal history and are not canonical implementation input.

## Intro / onboarding

Onboarding is an explicit content-owned sequence rather than undocumented Unity special-case product logic.

Accepted-current-scope beats cover partner orientation, basic movement/grab, the shared heavy crate, starter-item orientation and the first shared planning allocation.

`ONB_FIRST_FIRE` is deliberately present as an **owner-gated node** so the unresolved decision is visible. Until Anders records a scope disposition:

- `implementationAllowed = false`
- `requiredForAcceptedGiftScope = false`
- accepted backlog hours do not change
- the full deferred fire-start system must not be inferred from the onboarding contract

This preserves the product question without silently expanding the accepted gift build.

## Day 3 planning

`DAY3_PLANNING` is canonical as a distinct checkpoint immediately before `DAY3_STORM`.

It reuses the existing planning mechanic and these existing canonical action IDs:

1. `INT_REINFORCE_ROOF_006` — camp/shelter
2. `INT_BUILD_SIGNAL_009` — rescue/signal
3. `INT_TREAT_INJURY_011` — medical risk
4. `INT_SECURE_SUPPLIES_005` — food/resource security

Availability/unlock state remains authoritative. Listing an action in the phase does not bypass its normal availability rule. Numeric balance remains M3/M4 evidence-gated.

The stale proposal-only IDs `INT_REPAIR_SHELTER_008` and `INT_COLLECT_DRY_FUEL_014` are superseded and must not be implemented.

## Runtime/example synchronization

`examples/stormnatten.scenario.json` currently reflects an older phase list. Its large full-file rewrite is intentionally not performed through the connector because the available write action only replaces the entire file and would create unnecessary corruption risk.

Until phase data is bound into the runtime model, the canonical Day-3 content source above is authoritative for the product contract. When Claude performs the gated runtime/data integration, the example/runtime phase representation must be synchronized to:

`DAY2_PLANNING -> DAY3_PLANNING -> DAY3_STORM`

No Core or Unity code change is authorized by this document before M0b + M-Pre are green.

## Remaining issue #8 owner decision

Only fire-start scope remains unresolved:

- include the explicitly minimal onboarding fire beat,
- remove/replace it,
- or choose another explicit disposition.

If the choice changes accepted hours, backlog totals must be reconciled before the issue can close.

## Acceptance

Intro and Day 3 are resolved when the canonical JSON contracts parse in CI and this document is merged. Issue #8 stays open until Anders records the fire-start scope disposition and any resulting hours are reconciled.
