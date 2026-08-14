#!/usr/bin/env python3
"""Validate the example Stormnatten phase list against canonical Day 3 planning."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENARIO_PATH = ROOT / "examples/stormnatten.scenario.json"
DAY3_PATH = ROOT / "content/phases/stormnatten.day3_planning.source.json"
STALE_PROPOSAL_IDS = {"INT_REPAIR_SHELTER_008", "INT_COLLECT_DRY_FUEL_014"}
ERRORS: list[str] = []


def fail(message: str) -> None:
    ERRORS.append(message)


def load(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        fail(f"cannot parse {path.relative_to(ROOT)}: {exc}")
        return {}
    if not isinstance(data, dict):
        fail(f"{path.relative_to(ROOT)} must contain a JSON object")
        return {}
    return data


def main() -> int:
    scenario = load(SCENARIO_PATH)
    contract = load(DAY3_PATH)

    phases = scenario.get("phases")
    if not isinstance(phases, list):
        fail("scenario phases must be a list")
        phases = []

    phase_ids: list[str] = []
    phase_by_id: dict[str, dict] = {}
    for index, phase in enumerate(phases):
        if not isinstance(phase, dict):
            fail(f"phase[{index}] must be an object")
            continue
        pid = phase.get("id")
        if not isinstance(pid, str) or not pid:
            fail(f"phase[{index}] is missing id")
            continue
        if pid in phase_by_id:
            fail(f"duplicate phase id: {pid}")
        phase_ids.append(pid)
        phase_by_id[pid] = phase

    canonical_id = contract.get("id")
    insert_after = contract.get("insertAfter")
    insert_before = contract.get("insertBefore")
    if not all(isinstance(v, str) and v for v in (canonical_id, insert_after, insert_before)):
        fail("Day 3 contract must define id, insertAfter and insertBefore")
    else:
        for required in (insert_after, canonical_id, insert_before):
            if phase_ids.count(required) != 1:
                fail(f"phase {required} must occur exactly once")
        if all(phase_ids.count(v) == 1 for v in (insert_after, canonical_id, insert_before)):
            a = phase_ids.index(insert_after)
            d = phase_ids.index(canonical_id)
            b = phase_ids.index(insert_before)
            if not (d == a + 1 and b == d + 1):
                fail(
                    f"canonical order must be {insert_after} -> {canonical_id} -> {insert_before}; "
                    f"actual sequence is {' -> '.join(phase_ids)}"
                )

        phase = phase_by_id.get(canonical_id, {})
        if phase.get("type") != contract.get("type"):
            fail(f"{canonical_id}: type must match canonical contract")
        if phase.get("checkpoint") is not contract.get("checkpoint"):
            fail(f"{canonical_id}: checkpoint must match canonical contract")
        if phase.get("actions") != contract.get("actions"):
            fail(f"{canonical_id}: actions must exactly match canonical contract order")

    catalog = scenario.get("actionCatalog")
    catalog_ids = {
        row.get("id")
        for row in catalog
        if isinstance(catalog, list) and isinstance(row, dict) and isinstance(row.get("id"), str)
    } if isinstance(catalog, list) else set()
    if not catalog_ids:
        fail("scenario actionCatalog is missing or empty")

    for phase in phases:
        if not isinstance(phase, dict):
            continue
        pid = phase.get("id", "?")
        actions = phase.get("actions", [])
        if not isinstance(actions, list):
            fail(f"{pid}: actions must be a list")
            continue
        for action_id in actions:
            if action_id not in catalog_ids:
                fail(f"{pid}: action {action_id!r} is not in actionCatalog")

    serialized = json.dumps(scenario, ensure_ascii=False)
    for stale_id in sorted(STALE_PROPOSAL_IDS):
        if stale_id in serialized:
            fail(f"stale proposal-only action ID reintroduced: {stale_id}")

    if scenario.get("supportedBuildProtocol") != 1:
        fail("this content-only alignment must not change supportedBuildProtocol")
    if scenario.get("contentVersion") != "stormnatten-1.0":
        fail("this alignment intentionally preserves contentVersion stormnatten-1.0")

    if ERRORS:
        for error in ERRORS:
            print(f"ERROR: {error}")
        print(f"Stormnatten phase alignment FAILED: {len(ERRORS)} error(s).")
        return 1

    print(
        "Stormnatten phase alignment OK: "
        "DAY2_PLANNING -> DAY3_PLANNING -> DAY3_STORM; "
        "canonical actions exact; no stale proposal IDs."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
