#!/usr/bin/env python3
"""Verify current_placeholder_costs.source.json mirrors the current scenario example.

This validates consistency only. It does not approve the values as final balance.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = ROOT / "examples" / "stormnatten.scenario.json"
MIRROR = ROOT / "content" / "actions" / "current_placeholder_costs.source.json"


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def main() -> int:
    scenario = json.loads(SCENARIO.read_text(encoding="utf-8"))
    mirror = json.loads(MIRROR.read_text(encoding="utf-8"))

    found: dict[str, int] = {}
    for obj in walk(scenario):
        item_id = obj.get("id")
        cost = obj.get("effortCost")
        if isinstance(item_id, str) and item_id.startswith("INT_") and isinstance(cost, int):
            if item_id in found and found[item_id] != cost:
                print(f"ERROR: conflicting effortCost for {item_id} inside scenario: {found[item_id]} vs {cost}")
                return 1
            found[item_id] = cost

    expected = mirror.get("costs")
    if not isinstance(expected, dict):
        print("ERROR: mirror file has no object field 'costs'")
        return 1

    if not found:
        print("ERROR: no INT_* effortCost values found in scenario example")
        return 1

    errors = []
    for item_id, cost in sorted(found.items()):
        if expected.get(item_id) != cost:
            errors.append(f"{item_id}: scenario={cost}, mirror={expected.get(item_id)!r}")
    for item_id in sorted(set(expected) - set(found)):
        errors.append(f"{item_id}: exists in mirror but not as an effortCost action in scenario")

    if errors:
        print("Action placeholder cost mirror FAILED:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"Action placeholder cost mirror OK: {len(found)} action(s). Values remain non-final until M3.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
