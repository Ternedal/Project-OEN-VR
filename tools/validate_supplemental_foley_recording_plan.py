#!/usr/bin/env python3
"""Validate the Project OEN supplemental physical-Foley recording contract."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIO = ROOT / "content/audio"
CANONICAL = AUDIO / "audio_asset_manifest.csv"
MAIN_FOLEY = AUDIO / "foley_recording_plan.csv"
SUPPLEMENTAL = AUDIO / "supplemental_foley_recording_plan.csv"

ALIASES = {
    "SFX_STS_Hunger_Warn": "SFX_STS_Injury_Warn",
    "SFX_STS_Thirst_Warn": "SFX_STS_ColdWet_Warn",
}

EXPECTED_EVENTS = 13
EXPECTED_VARIATIONS = 90
REQUIRED_FIELDS = (
    "session",
    "prop_or_surface",
    "performance",
    "mic_setup",
    "take_strategy",
    "post",
    "target_duration",
)


def canonicalize(value: str) -> str:
    cleaned = value.strip()
    return ALIASES.get(cleaned, cleaned)


def read(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise SystemExit(f"missing file: {path.relative_to(ROOT)}")
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def positive_int(value: str, label: str) -> int:
    try:
        result = int(value)
    except (TypeError, ValueError) as exc:
        raise SystemExit(f"invalid integer for {label}: {value!r}") from exc
    if result <= 0:
        raise SystemExit(f"non-positive integer for {label}: {result}")
    return result


def main() -> int:
    canonical_rows = read(CANONICAL)
    main_rows = read(MAIN_FOLEY)
    rows = read(SUPPLEMENTAL)

    canonical_variations: dict[str, int] = {}
    for row in canonical_rows:
        event_id = canonicalize(row.get("event_id", ""))
        if not event_id:
            raise SystemExit("canonical manifest contains blank event_id")
        canonical_variations[event_id] = positive_int(
            row.get("variations", ""), f"canonical variations for {event_id}"
        )

    main_events = {
        canonicalize(row.get("event_id", ""))
        for row in main_rows
        if row.get("event_id", "").strip()
    }

    if len(rows) != EXPECTED_EVENTS:
        raise SystemExit(f"expected {EXPECTED_EVENTS} supplemental Foley events, got {len(rows)}")

    seen: set[str] = set()
    total = 0
    for row in rows:
        event_id = canonicalize(row.get("event_id", ""))
        if not event_id:
            raise SystemExit("supplemental Foley plan contains blank event_id")
        if event_id in seen:
            raise SystemExit(f"duplicate supplemental Foley event: {event_id}")
        seen.add(event_id)

        if event_id not in canonical_variations:
            raise SystemExit(f"supplemental Foley event is not canonical: {event_id}")
        if event_id in main_events:
            raise SystemExit(f"supplemental Foley overlaps main 40-event plan: {event_id}")

        variations = positive_int(row.get("variations", ""), f"variations for {event_id}")
        if variations != canonical_variations[event_id]:
            raise SystemExit(
                f"variation mismatch for {event_id}: supplemental={variations}, "
                f"canonical={canonical_variations[event_id]}"
            )
        total += variations

        if row.get("status", "").strip() != "recording-needed":
            raise SystemExit(f"unexpected supplemental Foley status for {event_id}: {row.get('status')!r}")

        for field in REQUIRED_FIELDS:
            if not row.get(field, "").strip():
                raise SystemExit(f"supplemental Foley event {event_id} lacks required field {field!r}")

    if total != EXPECTED_VARIATIONS:
        raise SystemExit(
            f"expected {EXPECTED_VARIATIONS} supplemental Foley variations, got {total}"
        )

    print(
        f"Supplemental Foley recording-plan validation OK: "
        f"{len(rows)} events / {total} planned variations"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
