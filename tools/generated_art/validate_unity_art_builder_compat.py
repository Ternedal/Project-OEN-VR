#!/usr/bin/env python3
"""Run the legacy global art validator with helper-aware review semantics.

Review-ProductionArt.ps1 now routes editor opening through Open-ShowcaseEditor.
The legacy validator still expects the concrete ProductionArtReviewMenu.OpenShowcase
method name after the sequential build/audit calls. This adapter preserves every
legacy check, but expands the verified helper call into that semantic marker before
the legacy order check runs.
"""
from __future__ import annotations

import sys
from pathlib import Path

import validate_unity_art_builder as legacy


_original_need = legacy.need


def helper_aware_need(path, label, tokens, errors):
    text = _original_need(path, label, tokens, errors)
    if path != legacy.REVIEW or not text:
        return text

    helper_method = '"ProjectOen.Art.Editor.ProductionArtReviewMenu.OpenShowcase"'
    helper_call = 'if ($OpenEditor) { Open-ShowcaseEditor }'
    fallback_marker = 'Run-UnityArtStep "Bygger production-art prefabs"'

    if helper_method not in text:
        errors.append("Fast review Open-ShowcaseEditor helper lost ProductionArtReviewMenu.OpenShowcase")
        return text

    fallback_start = text.find(fallback_marker)
    if fallback_start < 0:
        return text

    fallback = text[fallback_start:]
    if helper_call not in fallback:
        errors.append("Fast review sequential fallback no longer opens editor through Open-ShowcaseEditor")
        return text

    # Feed the legacy order check an explicit semantic marker at the helper call.
    semantic_call = helper_call + '\n# helper target: ProductionArtReviewMenu.OpenShowcase'
    patched_fallback = fallback.replace(helper_call, semantic_call, 1)
    return text[:fallback_start] + patched_fallback


legacy.need = helper_aware_need

if __name__ == "__main__":
    sys.exit(legacy.main())
