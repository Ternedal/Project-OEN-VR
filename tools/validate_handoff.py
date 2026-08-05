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


def main() -> int:
    errors: list[str] = []
    check_required(errors)
    check_json(errors)
    check_yaml(errors)
    check_markdown_links(errors)
    check_private_payload(errors)
    print(f"\nValidation complete: {len(errors)} error(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
