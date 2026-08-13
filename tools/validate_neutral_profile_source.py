#!/usr/bin/env python3
"""Validate neutral personalization fallback resolution."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "content" / "personalization" / "neutral_profile.source.json"
LOCALIZATION = ROOT / "content" / "localization" / "da.source.json"


def main() -> int:
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    loc = json.loads(LOCALIZATION.read_text(encoding="utf-8"))
    errors: list[str] = []

    if profile.get("profileId") != "NEUTRAL_DEFAULT":
        errors.append("profileId must be NEUTRAL_DEFAULT")
    if profile.get("fallbackProfileId") != "NEUTRAL_DEFAULT":
        errors.append("neutral profile must fall back to itself")

    final_key = profile.get("finalMessageKey")
    overrides = profile.get("textOverrides")
    strings = loc.get("strings")
    if not isinstance(final_key, str) or not final_key:
        errors.append("finalMessageKey must be a non-empty string")
    else:
        override_ok = isinstance(overrides, dict) and isinstance(overrides.get(final_key), str) and bool(overrides.get(final_key))
        localization_ok = isinstance(strings, dict) and isinstance(strings.get(final_key), str) and bool(strings.get(final_key))
        if not (override_ok or localization_ok):
            errors.append(f"finalMessageKey does not resolve: {final_key}")

    if profile.get("imageAssets") not in ([], None):
        errors.append("neutral profile must not depend on private image assets")
    if profile.get("audioAssets") not in ([], None):
        errors.append("neutral profile must not depend on private audio assets")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(f"Neutral profile OK: {final_key} resolves without private assets.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
