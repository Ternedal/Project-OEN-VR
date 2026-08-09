#!/usr/bin/env python3
"""Deterministic validation for the text-native PROJECT OEN repository."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "README.md",
    "CLAUDE.md",
    "00_READ_ME_FIRST.md",
    "01_PROMPT_FOR_CLAUDE.md",
    "02_CLAUDE_UPLOAD_AND_RETURN_GUIDE.md",
    "PROJECT_OEN_MASTER_HANDOFF_v2.0.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "docs/01_EXECUTIVE_HANDOFF.md",
    "docs/02_PRODUCT_REQUIREMENTS.md",
    "docs/03_CURRENT_MASTER_SPEC_v1.1.md",
    "docs/04_GAME_DESIGN_DEEP_DIVE.md",
    "docs/05_STORMNATTEN_CONTENT_BIBLE.md",
    "docs/06_TECHNICAL_ARCHITECTURE.md",
    "docs/07_MULTIPLAYER_NETWORKING.md",
    "docs/08_PLATFORM_BUILD_PERFORMANCE.md",
    "docs/09_VR_INTERACTION_COMFORT_ACCESSIBILITY.md",
    "docs/10_DATA_CONTENT_SAVE_SCHEMAS.md",
    "docs/11_ART_AUDIO_UI_DIRECTION.md",
    "docs/12_PRODUCTION_ROADMAP.md",
    "docs/13_TEST_QA_ACCEPTANCE.md",
    "docs/14_RISK_SCOPE_BUDGET.md",
    "docs/15_BUILD_RELEASE_OPERATIONS.md",
    "docs/16_REPOSITORY_ENGINEERING_STANDARDS.md",
    "docs/17_BACKLOG_AND_MILESTONES.md",
    "docs/18_DECISION_LOG.md",
    "docs/19_OPEN_QUESTIONS.md",
    "docs/20_IMPLEMENTATION_START_ORDER.md",
    "docs/21_GLOSSARY.md",
    "docs/22_SOURCE_REGISTER.md",
    "docs/23_GITHUB_BOOTSTRAP.md",
    "review/CLAUDE_REVIEW_TEMPLATE.md",
    "review/RESPONSE_MATRIX.md",
    "review/CLAUDE_RAW_REVIEW_PLACEHOLDER.md",
    "prototype/README.md",
    "diagrams/system_context.mmd",
    "diagrams/network_authority.mmd",
    "diagrams/gameplay_state_machine.mmd",
    "diagrams/build_pipeline.mmd",
]

EXAMPLE_SCHEMAS = {
    "examples/open_food_attracts_animal.event.json": "schemas/event.schema.json",
    "examples/personalization_profile.example.json": "schemas/personalization-profile.schema.json",
    "examples/savegame.example.json": "schemas/savegame.schema.json",
    "examples/shelter_reinforcement.recipe.json": "schemas/recipe.schema.json",
    "examples/stormnatten.scenario.json": "schemas/scenario.schema.json",
}


def check_scenario_contract(errors: list[str]) -> None:
    """CR-006: skemaet alene beviser ikke, at kontrakten er komplet."""
    import hashlib

    before = len(errors)
    scenario_path = ROOT / "examples/stormnatten.scenario.json"
    scenario = json.loads(scenario_path.read_text(encoding="utf-8"))
    catalog = {a["id"] for a in scenario.get("actionCatalog", [])}
    for phase in scenario.get("phases", []):
        for action in phase.get("actions", []):
            if action not in catalog:
                fail(
                    f"phase {phase['id']} refers to unknown action {action}",
                    errors,
                )
    if "supportedBuildProtocol" not in scenario:
        fail("scenario is missing supportedBuildProtocol", errors)

    save_path = ROOT / "examples/savegame.example.json"
    save = json.loads(save_path.read_text(encoding="utf-8"))
    body = {k: v for k, v in save.items() if k != "checksum"}
    expected = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    if save.get("checksum") != expected:
        fail(
            f"savegame checksum mismatch: expected {expected}, got {save.get('checksum')}",
            errors,
        )

    if len(errors) == before:
        print("PASS: scenario action catalog and savegame checksum")


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)
    print(f"FAIL: {message}")


def check_required(errors: list[str]) -> None:
    before = len(errors)
    for rel in REQUIRED:
        if not (ROOT / rel).is_file():
            fail(f"missing required file: {rel}", errors)
    if len(errors) == before:
        print("PASS: required repository files")


def check_json(errors: list[str]) -> None:
    for schema_path in sorted((ROOT / "schemas").glob("*.json")):
        try:
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(schema)
            print(f"PASS: schema {schema_path.relative_to(ROOT)}")
        except Exception as exc:  # noqa: BLE001
            fail(f"invalid schema {schema_path.relative_to(ROOT)}: {exc}", errors)

    for example_rel, schema_rel in EXAMPLE_SCHEMAS.items():
        try:
            instance = json.loads((ROOT / example_rel).read_text(encoding="utf-8"))
            schema = json.loads((ROOT / schema_rel).read_text(encoding="utf-8"))
            problems = sorted(
                Draft202012Validator(schema).iter_errors(instance),
                key=lambda error: list(error.path),
            )
            if problems:
                for problem in problems:
                    fail(
                        f"{example_rel} violates {schema_rel} at "
                        f"{list(problem.path)}: {problem.message}",
                        errors,
                    )
            else:
                print(f"PASS: {example_rel} against {schema_rel}")
        except Exception as exc:  # noqa: BLE001
            fail(f"cannot validate {example_rel}: {exc}", errors)


def check_yaml(errors: list[str]) -> None:
    paths = sorted(list(ROOT.rglob("*.yml")) + list(ROOT.rglob("*.yaml")))
    for path in paths:
        if ".git" in path.parts:
            continue
        try:
            yaml.safe_load(path.read_text(encoding="utf-8"))
            print(f"PASS: yaml {path.relative_to(ROOT)}")
        except Exception as exc:  # noqa: BLE001
            fail(f"invalid yaml {path.relative_to(ROOT)}: {exc}", errors)


def check_markdown_links(errors: list[str]) -> None:
    pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    before = len(errors)
    for path in sorted(ROOT.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        for raw in pattern.findall(text):
            target = raw.strip().split("#", 1)[0]
            if not target or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", target):
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                fail(f"broken relative link in {path.relative_to(ROOT)}: {raw}", errors)
    if len(errors) == before:
        print("PASS: markdown relative links")


def check_private_payload(errors: list[str]) -> None:
    forbidden_suffixes = {".keystore", ".jks", ".p12", ".pem", ".key", ".apk", ".aab"}
    before = len(errors)
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        rel = path.relative_to(ROOT)
        if path.suffix.lower() in forbidden_suffixes:
            fail(f"forbidden binary/secret extension detected: {rel}", errors)
        if any(part.lower() in {"privatecontent", "private_content"} for part in rel.parts):
            fail(f"private content directory detected: {rel}", errors)
    if len(errors) == before:
        print("PASS: no private assets or signing material")


def check_backlog_totals(errors: list[str]) -> None:
    """Recompute the backlog sums from docs/17 and compare against the totals quoted
    across the docs.

    Rationale: the hour totals are quoted in at least six documents. On 2026-08-09 all
    three aggregate figures had drifted from the table they claim to summarise (one
    dropped item was never subtracted, the deferred sum silently omitted P2, and a
    reduced item was not propagated). Numbers that nobody recomputes stop being facts.
    """
    before = len(errors)
    backlog = ROOT / "docs" / "17_BACKLOG_AND_MILESTONES.md"
    if not backlog.exists():
        fail("backlog file missing: docs/17_BACKLOG_AND_MILESTONES.md", errors)
        return

    totals: dict[str, float] = {}
    counts: dict[str, int] = {}
    for line in backlog.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| PO-"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 9:
            fail(f"backlog row has too few columns: {cells[0] if cells else line[:40]}", errors)
            continue
        gaveversion, hours = cells[6], cells[8]
        try:
            value = float(hours)
        except ValueError:
            fail(f"backlog row {cells[0]} has non-numeric hours: {hours!r}", errors)
            continue
        totals[gaveversion] = totals.get(gaveversion, 0.0) + value
        counts[gaveversion] = counts.get(gaveversion, 0) + 1

    if not totals:
        fail("backlog table produced no rows - has the format changed?", errors)
        return

    gift = totals.get("In", 0.0)
    deferred = totals.get("Defer", 0.0)
    active = gift + deferred
    active_items = counts.get("In", 0) + counts.get("Defer", 0)

    # Quoted figures that must stay in sync with the table above.
    expected = [
        ("gaveversion (Gaveversion = In)", gift, 997.0),
        ("udskudt (Gaveversion = Defer)", deferred, 439.0),
        ("aktiv backlog (In + Defer)", active, 1436.0),
    ]
    for label, actual, quoted in expected:
        if abs(actual - quoted) > 0.5:
            fail(
                f"backlog total drifted: {label} is {actual:.0f} t in docs/17 "
                f"but {quoted:.0f} t is quoted in the docs - recompute and update both",
                errors,
            )

    if active_items != 107:
        fail(f"active backlog item count is {active_items}, docs quote 107", errors)

    if len(errors) == before:
        print(
            f"PASS: backlog totals ({active_items} active items, "
            f"gift {gift:.0f} t, deferred {deferred:.0f} t)"
        )


def main() -> int:
    errors: list[str] = []
    check_required(errors)
    check_json(errors)
    check_scenario_contract(errors)
    check_yaml(errors)
    check_markdown_links(errors)
    check_backlog_totals(errors)
    check_private_payload(errors)
    print(f"\nValidation complete: {len(errors)} error(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
