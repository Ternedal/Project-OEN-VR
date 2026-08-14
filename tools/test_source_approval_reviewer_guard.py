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

import materialize_source_approved_audio as materializer
import normalize_audio_source_approval_review as normalizer
import test_audio_source_approval as fixture


def write_json(path: Path, value) -> Path:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def assert_not_promotable(payload: dict, upstream: list[Path], pack: Path, repo: Path, root: Path) -> None:
    normalized = normalizer.normalize(payload, upstream, pack, repo, require_complete=False)
    assert normalized["coverage"]["complete"] is False
    assert normalized["coverage"]["eligibleForSourceApproval"] == 0
    assert not any(record["sourceApprovedEligible"] for record in normalized["records"])
    path = write_json(root / "missing-reviewer-evidence.json", normalized)
    try:
        materializer.materialize(path, upstream, pack, root / "blocked", repo)
    except materializer.ApprovalError as exc:
        assert "no source is eligible" in str(exc)
    else:
        raise AssertionError("review without complete reviewer identity must never materialize source-approved bytes")


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        repo, pack, upstream, _ = fixture.make_fixture(root)
        template = fixture.preparer.prepare(upstream, pack, repo)

        blank_reviewer = fixture.fill_review(template)
        blank_reviewer["reviewerAlias"] = ""
        assert_not_promotable(blank_reviewer, upstream, pack, repo, root)

        blank_timestamp = fixture.fill_review(template)
        blank_timestamp["reviewedAt"] = ""
        assert_not_promotable(blank_timestamp, upstream, pack, repo, root)

        positive = normalizer.normalize(fixture.fill_review(template), upstream, pack, repo, require_complete=True)
        assert positive["coverage"]["eligibleForSourceApproval"] == 2

        tampered_reviewer = copy.deepcopy(positive)
        tampered_reviewer["reviewerAlias"] = ""
        path = write_json(root / "tampered-reviewer.json", tampered_reviewer)
        try:
            materializer.materialize(path, upstream, pack, root / "tampered-reviewer-out", repo)
        except materializer.ApprovalError as exc:
            assert "stored sourceApprovedEligible disagrees" in str(exc)
        else:
            raise AssertionError("removing reviewer alias after normalization must invalidate stored eligibility")

        tampered_timestamp = copy.deepcopy(positive)
        tampered_timestamp["reviewedAt"] = ""
        path = write_json(root / "tampered-timestamp.json", tampered_timestamp)
        try:
            materializer.materialize(path, upstream, pack, root / "tampered-timestamp-out", repo)
        except materializer.ApprovalError as exc:
            assert "stored sourceApprovedEligible disagrees" in str(exc)
        else:
            raise AssertionError("removing review timestamp after normalization must invalidate stored eligibility")

    print("Source approval reviewer guard self-test OK: blank reviewer/timestamp produce zero eligibility and post-normalization identity tampering blocks materialization.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
