#!/usr/bin/env python3
"""Validate the Project OEN Foley recording plan against the canonical audio manifest."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "content" / "audio" / "audio_asset_manifest.csv"
FOLEY_PLAN = ROOT / "content" / "audio" / "foley_recording_plan.csv"

EXPECTED_ROWS = 40
EXPECTED_VARIATIONS = 388
EXPECTED_STATUS = "recording-needed"


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    manifest_rows = load_csv(MANIFEST)
    foley_rows = load_csv(FOLEY_PLAN)

    manifest = {row["event_id"]: row for row in manifest_rows}
    errors: list[str] = []
    seen: set[str] = set()
    variation_total = 0

    if len(foley_rows) != EXPECTED_ROWS:
        errors.append(
            f"Foley plan row count mismatch: expected {EXPECTED_ROWS}, got {len(foley_rows)}"
        )

    for index, row in enumerate(foley_rows, start=2):
        event_id = row.get("event_id", "").strip()
        if not event_id:
            errors.append(f"row {index}: missing event_id")
            continue

        if event_id in seen:
            errors.append(f"row {index}: duplicate event_id {event_id}")
        seen.add(event_id)

        manifest_row = manifest.get(event_id)
        if manifest_row is None:
            errors.append(f"row {index}: {event_id} is not in audio_asset_manifest.csv")
            continue

        try:
            planned_variations = int(row.get("variations", ""))
        except ValueError:
            errors.append(f"row {index}: invalid variations for {event_id}")
            continue

        try:
            canonical_variations = int(manifest_row["variations"])
        except ValueError:
            errors.append(f"manifest: invalid variations for {event_id}")
            continue

        variation_total += planned_variations
        if planned_variations != canonical_variations:
            errors.append(
                f"row {index}: {event_id} variations mismatch; "
                f"plan={planned_variations}, manifest={canonical_variations}"
            )

        if row.get("status", "").strip() != EXPECTED_STATUS:
            errors.append(
                f"row {index}: {event_id} status must be {EXPECTED_STATUS!r}"
            )

        for required in (
            "session",
            "prop_or_surface",
            "performance",
            "mic_setup",
            "take_strategy",
            "post",
            "target_duration",
        ):
            if not row.get(required, "").strip():
                errors.append(f"row {index}: {event_id} missing {required}")

    if variation_total != EXPECTED_VARIATIONS:
        errors.append(
            f"Foley variation total mismatch: expected {EXPECTED_VARIATIONS}, got {variation_total}"
        )

    if errors:
        print("Foley recording-plan validation FAILED:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "Foley recording-plan validation OK: "
        f"{len(foley_rows)} events / {variation_total} planned variations"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
