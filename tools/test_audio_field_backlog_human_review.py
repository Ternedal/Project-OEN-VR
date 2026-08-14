#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import tempfile
from pathlib import Path

import normalize_audio_field_backlog_review as mod

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "content/audio/field_backlog_human_review.template.json"


def expect_error(payload, root, contains: str, require_complete: bool = False):
    try:
        mod.normalize(payload, root=root, require_complete=require_complete)
    except mod.ReviewError as exc:
        if contains not in str(exc):
            raise AssertionError(f"expected error containing {contains!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected ReviewError containing {contains!r}")


def main() -> int:
    template = json.loads(TEMPLATE.read_text(encoding="utf-8"))

    # The committed template should normalize as incomplete evidence without promotion.
    incomplete = mod.normalize(template, require_complete=False)
    assert incomplete["status"] == mod.OUTPUT_STATUS
    assert incomplete["coverage"]["complete"] is False
    expect_error(template, ROOT, "incomplete", require_complete=True)

    # A complete human-shaped payload should normalize successfully.
    complete = copy.deepcopy(template)
    complete["createdAt"] = "2026-08-14T06:00:00+02:00"
    record = complete["records"][0]
    record["disposition"] = "candidate-pass"
    record["overall"] = "Human test fixture; not a real listening judgement."
    for check in record["checks"].values():
        check["result"] = "pass"
        check["note"] = "fixture"
    normalized = mod.normalize(complete, require_complete=True)
    assert normalized["coverage"]["complete"] is True
    assert normalized["records"][0]["sourceSha256"] == complete["bindings"][record["target"]]

    # Hash drift must fail closed.
    stale = copy.deepcopy(complete)
    target = stale["records"][0]["target"]
    stale["bindings"][target] = "0" * 64
    expect_error(stale, ROOT, "bindings")

    # Missing checks must fail closed.
    missing = copy.deepcopy(complete)
    missing["records"][0]["checks"].pop("NOISE_FLOOR")
    expect_error(missing, ROOT, "check set mismatch")

    print("Field-backlog human review normalizer self-test OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
