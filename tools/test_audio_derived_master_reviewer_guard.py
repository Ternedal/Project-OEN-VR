#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import audio_derived_master_support as support
import materialize_derived_master_approved_audio as materializer
import normalize_audio_derived_master_review as normalizer
import prepare_audio_derived_master_review as preparer
import test_audio_derived_master_pipeline as fixture


def write_json(path: Path, value) -> Path:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def make_positive_fixture(root: Path):
    masters = root / "masters"
    masters.mkdir()
    fixture.write_pcm24(masters / "dm_a.wav", [1000, -1000, 2000, -2000] * 100)
    fixture.write_pcm24(masters / "dm_b.wav", [1500, -1500, 2500, -2500] * 100)
    source_receipt = fixture.source_receipt(root / "source_receipt.json")
    submission = fixture.submission(root / "submission.json")
    technical = support.validate_technical_submission(submission, source_receipt, masters, ROOT)
    technical_path = write_json(root / "technical.json", technical)
    template = preparer.prepare(technical_path, submission, source_receipt, masters, ROOT)
    payload = fixture.fill_review(template)
    payload["records"][1]["decision"] = "approve-derived-master"
    for check in payload["records"][1]["checks"].values():
        if check["value"] in {"not-applicable", "pass"}:
            check["value"] = "pass"
    return masters, source_receipt, submission, technical_path, payload


def assert_identity_blocks(payload: dict, masters: Path, source_receipt: Path, submission: Path, technical_path: Path, root: Path) -> None:
    normalized = normalizer.normalize(payload, technical_path, submission, source_receipt, masters, ROOT, require_complete=False)
    assert normalized["coverage"]["complete"] is False
    assert normalized["coverage"]["eligibleForDerivedMasterApproval"] == 0
    assert not any(record["derivedMasterApprovedEligible"] for record in normalized["records"])
    path = write_json(root / "identity-missing.normalized.json", normalized)
    try:
        materializer.materialize(path, technical_path, submission, source_receipt, masters, root / "blocked", ROOT)
    except support.DerivedError as exc:
        assert "no derived master is eligible" in str(exc)
    else:
        raise AssertionError("derived review without reviewer identity must never materialize approved masters")


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        masters, source_receipt, submission, technical_path, positive_payload = make_positive_fixture(root)

        blank_reviewer = copy.deepcopy(positive_payload)
        blank_reviewer["reviewerAlias"] = ""
        assert_identity_blocks(blank_reviewer, masters, source_receipt, submission, technical_path, root)

        blank_timestamp = copy.deepcopy(positive_payload)
        blank_timestamp["reviewedAt"] = ""
        assert_identity_blocks(blank_timestamp, masters, source_receipt, submission, technical_path, root)

        positive = normalizer.normalize(positive_payload, technical_path, submission, source_receipt, masters, ROOT, require_complete=True)
        assert positive["coverage"]["eligibleForDerivedMasterApproval"] == 2

        tampered_reviewer = copy.deepcopy(positive)
        tampered_reviewer["reviewerAlias"] = ""
        path = write_json(root / "tampered-reviewer.json", tampered_reviewer)
        try:
            materializer.materialize(path, technical_path, submission, source_receipt, masters, root / "tampered-reviewer-out", ROOT)
        except support.DerivedError as exc:
            assert "stored eligibility disagrees" in str(exc)
        else:
            raise AssertionError("removing reviewer alias after normalization must invalidate derived eligibility")

        tampered_timestamp = copy.deepcopy(positive)
        tampered_timestamp["reviewedAt"] = ""
        path = write_json(root / "tampered-timestamp.json", tampered_timestamp)
        try:
            materializer.materialize(path, technical_path, submission, source_receipt, masters, root / "tampered-timestamp-out", ROOT)
        except support.DerivedError as exc:
            assert "stored eligibility disagrees" in str(exc)
        else:
            raise AssertionError("removing reviewedAt after normalization must invalidate derived eligibility")

    print("Derived master reviewer guard self-test OK: reviewer/timestamp are required for eligibility and revalidated at materialization.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
