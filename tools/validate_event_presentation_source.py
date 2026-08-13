#!/usr/bin/env python3
"""Validate event-presentation authoring source against canonical event authoring IDs.

Checks source-contract consistency only. It does not validate Unity runtime binding.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVENTS = ROOT / "content" / "events" / "stormnatten.events.source.json"
PRESENTATION = ROOT / "content" / "events" / "stormnatten.presentation.source.json"
B2_DIR = ROOT / "source_art" / "events" / "b2"


def main() -> int:
    events = json.loads(EVENTS.read_text(encoding="utf-8"))
    presentation = json.loads(PRESENTATION.read_text(encoding="utf-8"))

    canonical_ids = {item["id"] for item in events.get("events", []) if isinstance(item, dict) and isinstance(item.get("id"), str)}
    mapped = presentation.get("events")
    errors: list[str] = []

    if not isinstance(mapped, dict):
        print("ERROR: presentation source has no object field 'events'")
        return 1

    mapped_ids = set(mapped)
    for missing in sorted(canonical_ids - mapped_ids):
        errors.append(f"missing presentation mapping for {missing}")
    for extra in sorted(mapped_ids - canonical_ids):
        errors.append(f"presentation mapping exists for unknown event {extra}")

    for event_id, entry in sorted(mapped.items()):
        if not isinstance(entry, dict):
            errors.append(f"{event_id}: presentation entry must be an object")
            continue

        if not entry.get("telegraph"):
            errors.append(f"{event_id}: missing telegraph")
        if not entry.get("presentationMode"):
            errors.append(f"{event_id}: missing presentationMode")
        if not entry.get("persistence"):
            errors.append(f"{event_id}: missing persistence")

        asset_ids = entry.get("sourceAssetIds", [])
        if not isinstance(asset_ids, list):
            errors.append(f"{event_id}: sourceAssetIds must be an array")
            continue
        for asset_id in asset_ids:
            if isinstance(asset_id, str) and asset_id.startswith("B2_"):
                source = B2_DIR / f"{asset_id}.svg"
                if not source.exists():
                    errors.append(f"{event_id}: missing B2 source asset {source.relative_to(ROOT)}")

    required_guardrails = {
        "EVT_TOOL_BREAK_001": "scopeGuardrail",
        "EVT_DISTANT_SMOKE_001": "scopeGuardrail",
        "EVT_RADIO_FRAGMENT_001": "scopeGuardrail",
    }
    for event_id, field in required_guardrails.items():
        entry = mapped.get(event_id, {})
        if isinstance(entry, dict) and not entry.get(field):
            errors.append(f"{event_id}: missing required {field}")

    if errors:
        print("Event presentation source validation FAILED:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"Event presentation source OK: {len(canonical_ids)} event(s), B2 source references resolved.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
