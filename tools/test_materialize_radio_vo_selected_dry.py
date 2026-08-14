#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))


def load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, TOOLS / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


fixture = load("rv_human_fixture_for_materialize", "test_radio_vo_human_review.py")
materializer = load("rv_materializer", "materialize_radio_vo_selected_dry.py")


def write_review(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        session = fixture.make_session(root)
        template = fixture.prep_review.prepare(session, ROOT)
        positive = fixture.normalizer.normalize(fixture.fill_review(template), session, ROOT, require_complete=True)
        review_path = write_review(root / "positive.normalized.json", positive)
        out = root / "selected"
        receipt = materializer.materialize(review_path, session, ROOT, out)
        assert receipt["selectedCount"] == 9
        assert receipt["sourceApprovalPromoted"] is False
        assert receipt["derivedMasterApprovalPromoted"] is False
        assert receipt["runtimeApprovalPromoted"] is False
        for record in receipt["records"]:
            dest = out / record["selectedDryFilename"]
            source = session / "takes" / record["sourceFilename"]
            assert dest.read_bytes() == source.read_bytes()
            assert record["selectedDrySha256"] == record["sourceSha256"]
        saved = json.loads((out / "radio_vo_selected_dry_receipt.json").read_text(encoding="utf-8"))
        assert saved["status"] == "selected-dry-source-materialized-from-human-review-not-processed"

        try:
            materializer.materialize(review_path, session, ROOT, out)
        except materializer.ReviewError as exc:
            assert "not empty" in str(exc)
        else:
            raise AssertionError("non-empty selected output must require explicit replace")

        replaced = materializer.materialize(review_path, session, ROOT, out, replace=True)
        assert replaced["selectedCount"] == 9

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        session = fixture.make_session(root)
        template = fixture.prep_review.prepare(session, ROOT)
        negative = fixture.normalizer.normalize(fixture.fill_review(template, negative=True), session, ROOT, require_complete=True)
        review_path = write_review(root / "negative.normalized.json", negative)
        try:
            materializer.materialize(review_path, session, ROOT, root / "selected")
        except materializer.ReviewError as exc:
            assert "not ready" in str(exc)
        else:
            raise AssertionError("negative human review must never materialize selected dry sources")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        session = fixture.make_session(root)
        template = fixture.prep_review.prepare(session, ROOT)
        positive = fixture.normalizer.normalize(fixture.fill_review(template), session, ROOT, require_complete=True)
        tampered = copy.deepcopy(positive)
        tampered["records"][0]["selectedSha256"] = "0" * 64
        review_path = write_review(root / "tampered.normalized.json", tampered)
        try:
            materializer.materialize(review_path, session, ROOT, root / "selected")
        except materializer.ReviewError as exc:
            assert "selected SHA" in str(exc)
        else:
            raise AssertionError("tampered selected SHA must be rejected")

    print("Radio VO selected-dry self-test OK: 9 byte-identical copies + overwrite guard + negative-review and tampered-selection rejection.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
