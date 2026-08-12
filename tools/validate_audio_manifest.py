#!/usr/bin/env python3
"""Static consistency checks for ProjectOen.Audio production data.

Stdlib-only by design so it can run locally or in CI without Unity.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "content" / "audio" / "audio_asset_manifest.csv"
ENUM_FILE = ROOT / "src" / "unity" / "ProjectOen.Audio" / "AudioEventId.cs"

MEMBER_RE = re.compile(r"^\s*(?P<name>[A-Za-z0-9_]+)\s*=\s*(?P<value>[A-Za-z0-9_]+),\s*$")


def parse_enum(text: str) -> dict[str, int]:
    values: dict[str, int] = {}
    for line in text.splitlines():
        match = MEMBER_RE.match(line)
        if not match:
            continue

        name = match.group("name")
        raw = match.group("value")
        if raw.isdigit():
            values[name] = int(raw)
        elif raw in values:
            values[name] = values[raw]
        else:
            raise ValueError(f"Unresolved enum value: {name} = {raw}")
    return values


def main() -> int:
    errors: list[str] = []

    if not MANIFEST.exists():
        errors.append(f"Missing manifest: {MANIFEST}")
    if not ENUM_FILE.exists():
        errors.append(f"Missing enum: {ENUM_FILE}")
    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors))
        return 1

    enum_text = ENUM_FILE.read_text(encoding="utf-8")
    try:
        enum_values = parse_enum(enum_text)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1

    with MANIFEST.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    event_ids = [row["event_id"].strip() for row in rows]
    seen: set[str] = set()
    for event_id in event_ids:
        if event_id in seen:
            errors.append(f"Duplicate manifest event_id: {event_id}")
        seen.add(event_id)
        if event_id not in enum_values:
            errors.append(f"Manifest event missing from AudioEventId: {event_id}")

    if len(rows) != 115:
        errors.append(f"Expected 115 manifest events, found {len(rows)}")

    try:
        variation_total = sum(int(row["variations"]) for row in rows)
    except (TypeError, ValueError) as exc:
        errors.append(f"Invalid variations value: {exc}")
        variation_total = -1

    if variation_total != 788:
        errors.append(f"Expected 788 planned variations, found {variation_total}")

    canonical_status = {
        "SFX_STS_Injury_Warn": 1100,
        "SFX_STS_ColdWet_Warn": 1101,
        "SFX_STS_Fatigue_Warn": 1102,
        "SFX_STS_Health_Damage": 1103,
        "SFX_STS_Health_Critical": 1104,
    }
    for name, expected in canonical_status.items():
        actual = enum_values.get(name)
        if actual != expected:
            errors.append(f"Canonical status {name} expected {expected}, found {actual}")

    # Transitional compatibility: the production manifest still contains the original
    # Hunger/Thirst labels. They must remain aliases only, never independent IDs.
    legacy_aliases = {
        "SFX_STS_Hunger_Warn": "SFX_STS_Injury_Warn",
        "SFX_STS_Thirst_Warn": "SFX_STS_ColdWet_Warn",
    }
    for legacy, canonical in legacy_aliases.items():
        if enum_values.get(legacy) != enum_values.get(canonical):
            errors.append(f"Legacy alias {legacy} must resolve to {canonical}")
        if f'[System.Obsolete("Legacy manifest alias. Use {canonical}.")]' not in enum_text:
            errors.append(f"Legacy alias {legacy} must remain explicitly obsolete")

    numeric_to_names: dict[int, list[str]] = {}
    for name, value in enum_values.items():
        if name == "None":
            continue
        numeric_to_names.setdefault(value, []).append(name)

    allowed_duplicate_values = {1100, 1101}
    for value, names in numeric_to_names.items():
        if len(names) > 1 and value not in allowed_duplicate_values:
            errors.append(f"Unexpected duplicate enum value {value}: {', '.join(names)}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(
        "Audio validation OK: "
        f"{len(rows)} events, {variation_total} planned variations, "
        f"{len(set(enum_values.values()) - {0})} unique runtime IDs."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
