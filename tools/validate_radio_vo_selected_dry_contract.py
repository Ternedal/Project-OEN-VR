#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    contract = load(ROOT / "content/audio/radio_vo_selected_dry_contract.source.json")
    session = load(ROOT / "content/audio/radio_vo_session_contract.source.json")
    human = load(ROOT / "content/audio/radio_vo_human_review_contract.source.json")
    errors = []
    if contract.get("version") != 1 or contract.get("status") != "materialization-tooling-ready-no-selected-dry-source":
        errors.append("selected-dry contract version/status drift")
    input_gate = contract.get("input", {})
    if input_gate.get("reviewKind") != "radio-vo-human-take-selection":
        errors.append("selected-dry reviewKind drift")
    if input_gate.get("normalizedStatus") != human.get("normalizedStatus"):
        errors.append("selected-dry input status must match human normalizer output")
    if input_gate.get("readyFlag") != "readyForDryMasterSelection" or input_gate.get("readyFlagMustBe") is not True:
        errors.append("selected-dry ready gate must remain explicit true")
    output = contract.get("output", {})
    if output.get("filenamePattern") != session.get("takeNaming", {}).get("selectedDryMasterPattern"):
        errors.append("selected-dry filename pattern drift from session contract")
    if output.get("receiptStatus") != "selected-dry-source-materialized-from-human-review-not-processed":
        errors.append("selected-dry receipt status drift")
    materialization = contract.get("materialization", {})
    if (
        materialization.get("copyOnly") is not True
        or materialization.get("preserveSourceBytes") is not True
        or materialization.get("sourceAndOutputShaMustMatch") is not True
        or materialization.get("expectedCueCount") != 9
    ):
        errors.append("selected-dry copy/hash/count invariants drift")
    rules = " | ".join(contract.get("rules", [])).lower()
    if "performs no trim" not in rules or "does not promote" not in rules:
        errors.append("selected-dry non-processing/non-promotion guardrails missing")
    if errors:
        for error in errors:
            print("ERROR:", error)
        return 1
    print("Radio VO selected-dry contract OK: 9 copy-only sources, exact hash preservation, explicit human-ready input, no downstream approval promotion.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
