#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import shutil
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


prep_session = load("rv_prepare_fixture", "prepare_radio_vo_session.py")
support = load("rv_review_support", "radio_vo_human_review_support.py")
prep_review = load("rv_prepare_review", "prepare_radio_vo_human_review.py")
normalizer = load("rv_review_normalizer", "normalize_radio_vo_human_review.py")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def make_session(root: Path) -> Path:
    session = root / "session"
    prepared = prep_session.prepare(session)
    (session / "performer_provenance.json").write_text(json.dumps({
        "sourceType": "human-performer",
        "sourceNameOrAlias": "Fixture performer",
        "permissionOrLicense": "test permission",
        "recordedOrGeneratedAt": "2026-08-14T07:00:00Z",
        "commercialReuseAllowed": False,
        "identifiablePublicPersonImitation": False,
    }) + "\n", encoding="utf-8")
    records = []
    for item in prepared["expectedTakes"]:
        data = ("fixture-audio:" + item["filename"]).encode()
        path = session / "takes" / item["filename"]
        path.write_bytes(data)
        records.append({
            "cueId": item["cueId"],
            "take": item["take"],
            "filename": item["filename"],
            "sha256": sha(data),
            "bytes": len(data),
            "durationSec": 1.0,
            "peakDbfs": -12.0,
        })
    (session / "radio_vo_intake_receipt.json").write_text(json.dumps({
        "version": 1,
        "status": "technical-intake-passed-not-listening-approved",
        "expectedTakeCount": 27,
        "validatedTakeCount": 27,
        "records": records,
        "warnings": [],
    }, indent=2) + "\n", encoding="utf-8")
    return session


def fill_review(template: dict, *, negative: bool = False) -> dict:
    payload = copy.deepcopy(template)
    payload["reviewedAt"] = "2026-08-14T07:30:00Z"
    payload["reviewerAlias"] = "Fixture reviewer"
    payload["rightsDecision"] = "accepted"
    payload["rightsNote"] = "Fixture rights checked."
    for i, cue in enumerate(payload["cues"]):
        if negative and i == 0:
            cue["decision"] = "needs-rerecord"
            cue["selectedFilename"] = ""
        else:
            cue["decision"] = "select"
            cue["selectedFilename"] = f"{cue['cueId']}__T01.wav"
        for check_id, check in cue["checks"].items():
            check["result"] = "fail" if negative and i == 0 and check_id == "DELIVERY" else "pass"
            check["note"] = "Fixture observation."
        cue["note"] = "Fixture cue note."
    return payload


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        session = make_session(Path(td))
        template = prep_review.prepare(session, ROOT)
        assert len(template["cues"]) == 9
        assert len(template["bindings"]["takes"]) == 27
        assert not template["reviewerAlias"]
        html = (session / "radio_vo_human_review.html").read_text(encoding="utf-8")
        assert "human-radio-vo-review-unvalidated" in html
        assert "VO_RADIO_NIGHT1_01__T01.wav" in html

        positive = normalizer.normalize(fill_review(template), session, ROOT, require_complete=True)
        assert positive["status"] == "human-review-evidence-unapproved"
        assert positive["coverage"]["complete"] is True
        assert positive["readyForDryMasterSelection"] is True
        assert sum(1 for x in positive["records"] if x["selectedSha256"]) == 9

        negative = normalizer.normalize(fill_review(template, negative=True), session, ROOT, require_complete=True)
        assert negative["coverage"]["complete"] is True
        assert negative["readyForDryMasterSelection"] is False
        assert any(x["decision"] == "needs-rerecord" for x in negative["records"])

        stale = fill_review(template)
        stale["bindings"]["takes"]["VO_RADIO_NIGHT1_01__T01.wav"] = "0" * 64
        try:
            normalizer.normalize(stale, session, ROOT)
        except normalizer.ReviewError as exc:
            assert "bindings are stale" in str(exc)
        else:
            raise AssertionError("stale review binding must be rejected")

        take = session / "takes/VO_RADIO_DAY3_01__T01.wav"
        take.write_bytes(take.read_bytes() + b"drift")
        try:
            support.load_context(session, ROOT)
        except support.ReviewError as exc:
            assert "stale take bytes" in str(exc)
        else:
            raise AssertionError("changed take bytes must be rejected")

    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        session = make_session(temp)
        fake_repo = temp / "repo"
        for rel in (support.QUEUE, support.LOCALIZATION, support.CONTRACT):
            target = fake_repo / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, target)
        loc_path = fake_repo / support.LOCALIZATION
        loc = json.loads(loc_path.read_text(encoding="utf-8"))
        loc["strings"]["vo.radio.day3.02"] += " ændret"
        loc_path.write_text(json.dumps(loc, ensure_ascii=False), encoding="utf-8")
        try:
            support.load_context(session, fake_repo)
        except support.ReviewError as exc:
            assert "canonical text drift" in str(exc)
        else:
            raise AssertionError("localization drift after recording must be rejected")

    print("Radio VO human review self-test OK: positive + negative complete evidence + stale binding/take + localization drift rejection.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
