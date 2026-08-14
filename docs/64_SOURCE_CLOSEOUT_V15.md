# Source closeout v15 — PROJECT ØEN

**Branch:** `agent/source-closeout-v15`  
**Owner:** ChatGPT / non-Unity source  
**Runtime owner:** Claude

## Scope

This closeout covers the remaining automatable source-side gaps identified by `docs/55_SOURCE_PRODUCTION_BATCH_PLAN.md`:

- `ITM_KNIFE_001` utility/fiber tool source master
- `CHR_TORSO_BASE_001` neutral torso source reference
- `ENV_EPILOGUE_001` reuse-first post-storm camp source reference
- stale source-manifest/inventory reconciliation
- six unambiguous human audio-manifest aliases reconciled to `content/audio/audio_cues.source.json`

## Explicit non-claims

This does **not** close:

- M0b cross-device/device evidence
- M-Pre human playtest evidence
- natural-audio creative/listening approval
- radio VO recording
- final music production
- Unity import/runtime/device QA
- issue #8 manual fire-start owner decision

## Rebase note

The branch was created from `ed3683d71fae19c656d2068ddbd7d51e72f43152`. `main` advanced afterward with audio human-review/backlog tooling only; the compare showed no overlapping v15 target files. The PR must still run against current `main` CI before merge consideration.
