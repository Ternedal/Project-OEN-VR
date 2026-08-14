# A2 core source provenance

**Class:** `OWN`  
**Created for:** PROJECT ØEN  
**Date:** 2026-08-13  
**Status:** SOURCE REFERENCES + UV-MAPPED PRODUCTION MESH PACK / Unity integration pending

All A2 briefs, reference sheets and source masters in this folder are project-original and derive from PROJECT ØEN's own design documents and interaction briefs.

No third-party models, stock artwork, external game screenshots or traced artwork are included.

## Individual source masters currently committed in this production pass

Current count: **10 individual SVG source masters**.

- `ITM_FIRESTEEL_001.svg`
- `ITM_TINDER_001.svg`
- `ITM_ROPE_COIL_001.svg`
- `PRP_PLAN_TABLE_001.svg`
- `PRP_HEAVY_CRATE_001.svg`
- `PRP_SHELTER_BEAM_001.svg`
- `PRP_SHELTER_ROPE_001.svg`
- `PRP_SHELTER_TARP_001.svg`
- `PRP_SHELTER_FRAME_001.svg`
- `PRP_SIGNAL_FRAME_001.svg`

The plan-table master preserves six large card bays, four physical effort markers, two-sided reach intent and distinct editable / ready / locked shapes without relying on color alone.

The heavy-crate master preserves a broad two-person silhouette, opposed carry handles and distinct closed / placed / open readability without defining runtime carry behaviour.

The shelter-beam master preserves two broad hold regions and makes the alternate structural state change the silhouette and load line rather than relying on a small surface mark alone.

The shelter-rope master preserves chunky visible fiber, oversized attachment loops and three geometry-led load states: loose/sag, controlled and high-load. State readability is shape/position first, never color-only.

The shelter-tarp master preserves four large shelter states: dry/taut, wet/heavy sag, loose/flapping and torn/weak. Wetness changes drape, loose state breaks the stable plane, and torn state removes a substantial silhouette edge; tie points stay oversized and discoverable.

The shelter-frame master preserves a stage 0-3 physical silhouette progression from materials to a recognizable frame, stabilized ridge/binding and cross-braced finished structure, with broad nodes and no progress-bar grammar.

The signal-frame master preserves a stage 0-3 landmark progression from materials to frame, stabilized structure and a clearly prepared final state with signal cloth, fuel and a reachable low activation zone. The ready state is intentionally not shown as already ignited.

The corresponding Markdown files remain product/handoff contracts.

ChatGPT owns source shape/state/readability intent. Claude owns Unity implementation, XR scale tuning and Quest device QA.

## Production geometry

The A2 production lane now contains concrete metre-scaled OBJ/MTL source geometry, not only reference boards:

- three grabbable core items at this directory level: `ITM_FIRESTEEL_001`, `ITM_TINDER_001` and `ITM_ROPE_COIL_001`;
- fourteen Camp/world sources under `production/`, including the plan table, heavy crate, firepit, signal frame, shelter states, wreck landmark and support props;
- explicit UV indices, named semantic parts and resolved project-owned PNG material references.

The three fire-start-related source files do not make manual fire-start canonical; issue #8 remains an owner gate.

Source existence does not imply release approval; runtime readability, performance and interaction still require the relevant gates.
