#!/usr/bin/env python3
"""Validate the planning/status UI source contract against canonical source data.

This validator stays outside Unity. It verifies that the handoff contract references
real source assets and localization keys, and that authored Stormnatten actions remain
the single source for title/description/icon/cost/category.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "content" / "ui" / "planning_status_ui.source.json"
DEFAULT_LOCALIZATION = ROOT / "content" / "localization" / "da.source.json"
DEFAULT_ACTIONS = ROOT / "content" / "actions" / "stormnatten.actions.source.json"
A1 = ROOT / "source_art" / "ui" / "a1"

EXPECTED_BINDINGS = {
    "title": "actions[].nameKey",
    "description": "actions[].shortKey",
    "icon": "actions[].iconId",
    "cost": "actions[].effortCost",
    "category": "actions[].category",
}

ERRORS: list[str] = []


def fail(message: str) -> None:
    ERRORS.append(message)


def load_json(path: Path, owner: str) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        fail(f"{owner}: cannot parse {path.relative_to(ROOT)}: {exc}")
        return None
    if not isinstance(data, dict):
        fail(f"{owner}: root must be an object")
        return None
    return data


def resolve_relative(value: object, owner: str) -> Path | None:
    if not isinstance(value, str) or not value:
        fail(f"{owner}: missing path")
        return None
    path = ROOT / value
    if not path.is_file():
        fail(f"{owner}: missing file {value}")
        return None
    return path


def validate_copy_keys(keys: object, strings: dict, owner: str) -> None:
    if not isinstance(keys, list):
        fail(f"{owner}: copyKeys must be a list")
        return
    for key in keys:
        if not isinstance(key, str) or not key:
            fail(f"{owner}: invalid localization key {key!r}")
        elif key not in strings:
            fail(f"{owner}: missing localization key {key}")


def main() -> int:
    contract = load_json(CONTRACT, "PLANNING_STATUS_UI")
    if contract is None:
        return report()

    locale_path = resolve_relative(contract.get("localeSource"), "PLANNING_STATUS_UI.localeSource")
    action_path = resolve_relative(contract.get("actionSource"), "PLANNING_STATUS_UI.actionSource")

    if locale_path is not None and locale_path != DEFAULT_LOCALIZATION:
        fail("PLANNING_STATUS_UI: localeSource must point at canonical da.source.json")
    if action_path is not None and action_path != DEFAULT_ACTIONS:
        fail("PLANNING_STATUS_UI: actionSource must point at canonical Stormnatten actions")

    localization = load_json(locale_path, "LOCALIZATION_DA") if locale_path else None
    actions_data = load_json(action_path, "STORMNATTEN_ACTIONS") if action_path else None
    strings = localization.get("strings") if isinstance(localization, dict) else None
    if not isinstance(strings, dict):
        fail("LOCALIZATION_DA: strings must be an object")
        strings = {}

    planning = contract.get("planning")
    if not isinstance(planning, dict):
        fail("PLANNING_STATUS_UI: planning must be an object")
    else:
        resolve_relative(planning.get("cardBase"), "planning.cardBase")
        bindings = planning.get("actionBindings")
        if bindings != EXPECTED_BINDINGS:
            fail(f"planning.actionBindings must equal canonical mapping {EXPECTED_BINDINGS}")
        validate_copy_keys(planning.get("copyKeys"), strings, "planning")

        markers = planning.get("markers")
        if not isinstance(markers, list) or len(markers) != 2:
            fail("planning.markers must contain exactly two player markers")
        else:
            players: set[str] = set()
            for index, marker in enumerate(markers):
                owner = f"planning.markers[{index}]"
                if not isinstance(marker, dict):
                    fail(f"{owner}: marker must be an object")
                    continue
                player = marker.get("player")
                if player not in {"A", "B"}:
                    fail(f"{owner}: player must be A or B")
                elif player in players:
                    fail(f"{owner}: duplicate player {player}")
                else:
                    players.add(player)
                resolve_relative(marker.get("source"), f"{owner}.source")
                resolve_relative(marker.get("identity"), f"{owner}.identity")
            if players != {"A", "B"}:
                fail("planning.markers must cover players A and B")

    wrist = contract.get("wristStatus")
    if not isinstance(wrist, dict):
        fail("PLANNING_STATUS_UI: wristStatus must be an object")
    else:
        resolve_relative(wrist.get("frame"), "wristStatus.frame")
        fields = wrist.get("fields")
        seen_fields: set[str] = set()
        if not isinstance(fields, list) or not fields:
            fail("wristStatus.fields must be a non-empty list")
        else:
            for index, field in enumerate(fields):
                owner = f"wristStatus.fields[{index}]"
                if not isinstance(field, dict):
                    fail(f"{owner}: field must be an object")
                    continue
                field_id = field.get("id")
                if not isinstance(field_id, str) or not field_id:
                    fail(f"{owner}: id is required")
                elif field_id in seen_fields:
                    fail(f"{owner}: duplicate id {field_id}")
                else:
                    seen_fields.add(field_id)
                resolve_relative(field.get("icon"), f"{owner}.icon")
                validate_copy_keys(field.get("copyKeys"), strings, owner)
        validate_copy_keys(wrist.get("stateCopyKeys"), strings, "wristStatus.stateCopyKeys")

    actions = actions_data.get("actions") if isinstance(actions_data, dict) else None
    action_count = 0
    if not isinstance(actions, list) or not actions:
        fail("STORMNATTEN_ACTIONS: actions must be a non-empty list")
    else:
        seen_actions: set[str] = set()
        for index, action in enumerate(actions):
            owner = f"actions[{index}]"
            if not isinstance(action, dict):
                fail(f"{owner}: action must be an object")
                continue
            action_count += 1
            action_id = action.get("id")
            if not isinstance(action_id, str) or not action_id:
                fail(f"{owner}: id is required")
            elif action_id in seen_actions:
                fail(f"{owner}: duplicate id {action_id}")
            else:
                seen_actions.add(action_id)

            for field_name in ("nameKey", "shortKey", "iconId", "effortCost", "category"):
                if field_name not in action:
                    fail(f"{owner}: missing field {field_name}")

            for key_field in ("nameKey", "shortKey"):
                key = action.get(key_field)
                if not isinstance(key, str) or key not in strings:
                    fail(f"{owner}: {key_field} does not resolve in localization: {key!r}")

            icon_id = action.get("iconId")
            if not isinstance(icon_id, str) or not icon_id:
                fail(f"{owner}: invalid iconId")
            else:
                icon_path = A1 / f"{icon_id}.svg"
                if not icon_path.is_file():
                    fail(f"{owner}: iconId does not resolve to A1 SVG: {icon_id}")

            effort_cost = action.get("effortCost")
            if not isinstance(effort_cost, int) or isinstance(effort_cost, bool) or effort_cost < 0:
                fail(f"{owner}: effortCost must be a non-negative integer")
            category = action.get("category")
            if not isinstance(category, str) or not category:
                fail(f"{owner}: category must be a non-empty string")

    if ERRORS:
        return report()

    print(
        "Planning/status UI source links OK: "
        f"{action_count} actions, {len(strings)} localization strings, canonical A1 mappings valid."
    )
    return 0


def report() -> int:
    for error in ERRORS:
        print(f"ERROR: {error}")
    print(f"Planning/status UI validation FAILED: {len(ERRORS)} error(s).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
