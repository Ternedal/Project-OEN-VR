# Source closeout v15 — QA contract

Repository CI for this branch must pass all of the following before merge consideration:

1. `tools/validate_utility_knife_source.py`
2. `tools/validate_avatar_torso_source.py`
3. `tools/validate_epilogue_source.py`
4. `tools/validate_source_closeout_v15.py`
5. `tools/validate_audio_manifest_registry_alignment.py`
6. `tools/validate_source_inventory_backing.py`

Local package QA before branch publication passed the same v15 source validators plus two idempotent apply runs and Python syntax compilation.

Human/device gates are intentionally outside this QA contract and must not be inferred from a green repository run.
