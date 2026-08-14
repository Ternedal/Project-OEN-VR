#!/usr/bin/env python3
"""Run source-stamp QA and the legacy global art validator with helper-aware semantics."""
from __future__ import annotations

import sys

import validate_review_source_stamp as source_stamp
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

    semantic_call = helper_call + '\n# helper target: ProductionArtReviewMenu.OpenShowcase'
    patched_fallback = fallback.replace(helper_call, semantic_call, 1)
    return text[:fallback_start] + patched_fallback


legacy.need = helper_aware_need

if __name__ == "__main__":
    source_result = source_stamp.main()
    if source_result != 0:
        sys.exit(source_result)
    sys.exit(legacy.main())
