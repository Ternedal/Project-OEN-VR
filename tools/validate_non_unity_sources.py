#!/usr/bin/env python3
"""Validate PROJECT ØEN non-Unity authoring/source artifacts.

This validator deliberately checks contracts owned outside Unity:
- JSON source parses cleanly and carries expected metadata.
- Danish localization keys referenced by action/event source exist.
- Source SVG files are well-formed XML and use a viewBox.
- Action icon IDs resolve to A1 SVG source or the source-asset manifest.
- Audio cue IDs referenced by events are declared in the audio manifest.
- Natural-audio acquisition/listening contracts remain safe and reproducible.
- proposal-not-canonical data stays under content/proposals/.
- obvious private-content folders/files are not committed.

It does NOT validate gameplay balance or Unity runtime behavior.
"""

from __future__ import annotations

import io
import json
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []
WARNINGS: list[str] = []


def fail(message: str) -> None:
    ERRORS.append(message)


def warn(message: str) -> None:
    WARNINGS.append(message)


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - validation should report all parse failures
        fail(f"JSON parse failed: {path.relative_to(ROOT)}: {exc}")
        return None


def validate_all_json() -> dict[Path, object]:
    loaded: dict[Path, object] = {}
    content_root = ROOT / "content"
    if not content_root.exists():
        fail("Missing content/ directory")
        return loaded

    for path in sorted(content_root.rglob("*.json")):
        data = load_json(path)
        if data is not None:
            loaded[path] = data

        if path.name.endswith(".source.json") and isinstance(data, dict):
            if "status" not in data and "profileId" not in data:
                warn(f"Source JSON has no explicit status/profile marker: {path.relative_to(ROOT)}")

        if isinstance(data, dict) and data.get("status") == "proposal-not-canonical":
            proposals_dir = ROOT / "content" / "proposals"
            try:
                path.relative_to(proposals_dir)
            except ValueError:
                fail(f"proposal-not-canonical file is outside content/proposals/: {path.relative_to(ROOT)}")

    return loaded


def localization_keys(loaded: dict[Path, object]) -> set[str]:
    path = ROOT / "content" / "localization" / "da.source.json"
    data = loaded.get(path)
    if not isinstance(data, dict):
        fail("Missing/invalid content/localization/da.source.json")
        return set()
    strings = data.get("strings")
    if not isinstance(strings, dict):
        fail("da.source.json must contain object field 'strings'")
        return set()
    return set(strings.keys())


def validate_actions(loaded: dict[Path, object], keys: set[str]) -> None:
    path = ROOT / "content" / "actions" / "stormnatten.actions.source.json"
    data = loaded.get(path)
    if not isinstance(data, dict):
        fail("Missing/invalid action source JSON")
        return
    actions = data.get("actions")
    if not isinstance(actions, list) or not actions:
        fail("Action source must contain non-empty actions[]")
        return

    seen_ids: set[str] = set()
    manifest_text = (ROOT / "docs" / "38_SOURCE_ASSET_MANIFEST.md").read_text(encoding="utf-8")
    svg_names = {p.stem for p in (ROOT / "source_art").rglob("*.svg")} if (ROOT / "source_art").exists() else set()

    for idx, action in enumerate(actions):
        if not isinstance(action, dict):
            fail(f"Action #{idx} is not an object")
            continue
        action_id = action.get("id")
        if not isinstance(action_id, str) or not action_id.startswith("INT_"):
            fail(f"Invalid action id at index {idx}: {action_id!r}")
            continue
        if action_id in seen_ids:
            fail(f"Duplicate action id: {action_id}")
        seen_ids.add(action_id)

        for field in ("nameKey", "shortKey"):
            value = action.get(field)
            if not isinstance(value, str) or value not in keys:
                fail(f"{action_id}: localization key missing for {field}: {value!r}")

        icon_id = action.get("iconId")
        if not isinstance(icon_id, str):
            fail(f"{action_id}: missing iconId")
        elif icon_id not in svg_names and icon_id not in manifest_text:
            fail(f"{action_id}: iconId not found in source_art or asset manifest: {icon_id}")

        if not action.get("primaryRole") or not action.get("secondaryRole"):
            fail(f"{action_id}: both primaryRole and secondaryRole are required")


def validate_events(loaded: dict[Path, object], keys: set[str]) -> None:
    path = ROOT / "content" / "events" / "stormnatten.events.source.json"
    data = loaded.get(path)
    if not isinstance(data, dict):
        fail("Missing/invalid event source JSON")
        return
    events = data.get("events")
    if not isinstance(events, list) or len(events) < 10:
        fail("Stormnatten event source must contain at least 10 events")
        return

    seen_ids: set[str] = set()
    audio_text = (ROOT / "docs" / "39_AUDIO_CUE_MANIFEST.md").read_text(encoding="utf-8")

    for idx, event in enumerate(events):
        if not isinstance(event, dict):
            fail(f"Event #{idx} is not an object")
            continue
        event_id = event.get("id")
        if not isinstance(event_id, str) or not event_id.startswith("EVT_"):
            fail(f"Invalid event id at index {idx}: {event_id!r}")
            continue
        if event_id in seen_ids:
            fail(f"Duplicate event id: {event_id}")
        seen_ids.add(event_id)

        for key in event.get("copyKeys", []):
            if key not in keys:
                fail(f"{event_id}: referenced localization key does not exist: {key}")

        for cue in event.get("audioCueIds", []):
            if cue not in audio_text:
                fail(f"{event_id}: referenced audio cue not declared in docs/39: {cue}")

        roles = event.get("roles", [])
        if not isinstance(roles, list) or len(roles) < 2:
            fail(f"{event_id}: event authoring source must define two role intents")

        if not event.get("failForward"):
            fail(f"{event_id}: missing failForward authoring rule")


def validate_svgs() -> None:
    source_root = ROOT / "source_art"
    if not source_root.exists():
        fail("Missing source_art/ directory")
        return

    svg_paths = sorted(source_root.rglob("*.svg"))
    if not svg_paths:
        fail("No source SVG files found")
        return

    for path in svg_paths:
        try:
            root = ET.parse(path).getroot()
        except Exception as exc:  # noqa: BLE001
            fail(f"SVG XML parse failed: {path.relative_to(ROOT)}: {exc}")
            continue
        if root.tag.split("}")[-1] != "svg":
            fail(f"SVG root element invalid: {path.relative_to(ROOT)}")
        if not root.attrib.get("viewBox"):
            fail(f"SVG missing viewBox: {path.relative_to(ROOT)}")

    for pack in (source_root / "ui" / "a1", source_root / "neutral"):
        if pack.exists() and not (pack / "PROVENANCE.md").exists():
            fail(f"Source-art pack missing PROVENANCE.md: {pack.relative_to(ROOT)}")


def validate_private_content_absence() -> None:
    forbidden_dirs = [ROOT / "PrivateContent", ROOT / "private_content"]
    for path in forbidden_dirs:
        if path.exists():
            fail(f"Private content directory must not be committed: {path.relative_to(ROOT)}")

    # This is intentionally conservative: only known dangerous filename markers.
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        lower = path.name.lower()
        if any(marker in lower for marker in ("final_message_private", "ending_photo_private", "private_voice")):
            fail(f"Possible private asset committed: {path.relative_to(ROOT)}")


def validate_neutral_profile(loaded: dict[Path, object]) -> None:
    path = ROOT / "content" / "personalization" / "neutral_profile.source.json"
    data = loaded.get(path)
    if not isinstance(data, dict):
        fail("Missing/invalid neutral personalization source profile")
        return
    if data.get("profileId") != "NEUTRAL_DEFAULT":
        fail("Neutral profileId must be NEUTRAL_DEFAULT")
    if data.get("fallbackProfileId") != "NEUTRAL_DEFAULT":
        fail("Neutral profile must fall back to itself")
    names = data.get("displayNames")
    if not isinstance(names, list) or len(names) != 2:
        fail("Neutral profile must define exactly two displayNames")
    if data.get("imageAssets") not in ([], None):
        fail("Neutral source profile should not depend on private image assets")
    if data.get("audioAssets") not in ([], None):
        fail("Neutral source profile should not depend on private audio assets")


def validate_audio_acquisition_contract() -> None:
    """Run the offline natural-audio contract test suite inside the existing CI guard."""
    try:
        from test_audio_acquisition_contract import AudioAcquisitionContractTests
    except Exception as exc:  # noqa: BLE001
        fail(f"Audio acquisition contract tests could not be imported: {exc}")
        return

    stream = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(AudioAcquisitionContractTests)
    result = unittest.TextTestRunner(stream=stream, verbosity=1).run(suite)
    if not result.wasSuccessful():
        details = " ".join(line.strip() for line in stream.getvalue().splitlines() if line.strip())
        fail(f"Audio acquisition contract QA failed: {details}")


def main() -> int:
    loaded = validate_all_json()
    keys = localization_keys(loaded)
    validate_actions(loaded, keys)
    validate_events(loaded, keys)
    validate_neutral_profile(loaded)
    validate_svgs()
    validate_private_content_absence()
    validate_audio_acquisition_contract()

    for warning in WARNINGS:
        print(f"WARNING: {warning}")
    if ERRORS:
        for error in ERRORS:
            print(f"ERROR: {error}")
        print(f"\nNon-Unity source validation FAILED: {len(ERRORS)} error(s), {len(WARNINGS)} warning(s).")
        return 1

    print(f"Non-Unity source validation OK: {len(loaded)} JSON source file(s), "
          f"{len(list((ROOT / 'source_art').rglob('*.svg')))} SVG source file(s), "
          f"{len(WARNINGS)} warning(s); audio acquisition contract valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
