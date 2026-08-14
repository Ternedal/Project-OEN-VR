#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

from foley_human_review_support import FoleyReviewError, REVIEW_CONTRACT, load_context
from materialize_foley_source_approved import materialize
from normalize_foley_human_review import normalize
from prepare_foley_human_review import prepare as prepare_review
from prepare_foley_session import CONTRACT, prepare as prepare_session
from test_foley_session import populate
from validate_foley_session import validate_session


def write_technical_receipt(root: Path) -> None:
    receipt, errors, _ = validate_session(root)
    if errors:
        raise AssertionError(f"fixture technical intake failed: {errors}")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    (root / contract["receipt"]["filename"]).write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")


def build_session(root: Path, commercial_reuse: bool = True) -> None:
    prepare_session(root)
    populate(root)
    provenance = root / "foley_provenance.json"
    data = json.loads(provenance.read_text(encoding="utf-8"))
    data["commercialReuseAllowed"] = commercial_reuse
    provenance.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    write_technical_receipt(root)


def positive_review(root: Path) -> dict:
    prepare_review(root)
    path = root / "foley_human_review.template.json"
    review = json.loads(path.read_text(encoding="utf-8"))
    review["reviewerAlias"] = "fixture-reviewer"
    review["reviewedAt"] = "2026-08-14T13:00:00Z"
    for key in review["takeDecisions"]:
        review["takeDecisions"][key] = "keep"
        review["takeNotes"][key] = "distinct physical fixture performance"
    context = load_context(root)
    typed = context["reviewContract"]["typedChecks"]
    for cue_id, cue in review["cueReviews"].items():
        cue["decision"] = "accept-current-set"
        cue["note"] = "fixture cue family accepted"
        for check_id, spec in typed.items():
            cue["checks"][check_id]["result"] = 4 if spec["type"] == "rating" else spec["approval"][0]
            cue["checks"][check_id]["note"] = "fixture human-evidence placeholder for contract test"
    return review


def normalize_to(root: Path, review: dict, name: str, require_complete: bool = True) -> tuple[dict, Path]:
    normalized = normalize(review, root, require_complete=require_complete)
    path = root / name
    path.write_text(json.dumps(normalized, indent=2) + "\n", encoding="utf-8")
    return normalized, path


def assert_not_ready(normalized: dict, label: str) -> None:
    if normalized.get("readyForSourceMaterialization") is not False:
        raise AssertionError(f"{label}: expected readyForSourceMaterialization=false")


def main() -> int:
    review_contract = json.loads(REVIEW_CONTRACT.read_text(encoding="utf-8"))
    expected_takes = review_contract["expectedTakeCount"]
    expected_cues = review_contract["expectedCueCount"]
    if (expected_cues, expected_takes) != (17, 73):
        raise AssertionError(f"current Foley human review contract must remain 17 cues / 73 takes; got {(expected_cues, expected_takes)}")

    with tempfile.TemporaryDirectory(prefix="oen-foley-review-test-") as td:
        base = Path(td)
        clean = base / "clean"
        build_session(clean)
        review = positive_review(clean)
        normalized, normalized_path = normalize_to(clean, review, "positive.normalized.json")
        if normalized.get("reviewComplete") is not True or normalized.get("readyForSourceMaterialization") is not True:
            raise AssertionError(f"positive {expected_takes}/{expected_takes} + {expected_cues}/{expected_cues} review should be complete and ready")
        expected_coverage = {
            "reviewedTakes": expected_takes,
            "expectedTakes": expected_takes,
            "completeCues": expected_cues,
            "expectedCues": expected_cues,
            "complete": True,
        }
        if normalized["coverage"] != expected_coverage:
            raise AssertionError(f"unexpected positive coverage: {normalized['coverage']}")
        output = base / "positive-output"
        receipt = materialize(clean, normalized_path, output)
        if receipt["sourceCount"] != expected_takes or receipt["cueCount"] != expected_cues:
            raise AssertionError(f"positive materialization did not copy {expected_takes} sources / {expected_cues} cues")
        for record in receipt["records"]:
            source = clean / record["sourceRelativePath"]
            copied = output / record["outputRelativePath"]
            if not copied.is_file() or source.read_bytes() != copied.read_bytes():
                raise AssertionError(f"copy-only materialization drift: {record['sourceRelativePath']}")
            if not record["sourceApproved"] or record["derivedMasterApproved"] or record["UnityIntegrated"] or record["QuestApproved"] or record["releaseApproved"]:
                raise AssertionError("promotion state boundary drift")

        negative = json.loads(json.dumps(review))
        first_path = sorted(negative["takeDecisions"])[0]
        negative["takeDecisions"][first_path] = "needs-rerecord"
        negative["takeNotes"][first_path] = "fixture requires rerecord"
        neg_norm, neg_path = normalize_to(clean, negative, "negative.normalized.json")
        if neg_norm.get("reviewComplete") is not True:
            raise AssertionError("complete negative review must remain valid complete evidence")
        assert_not_ready(neg_norm, "needs-rerecord")
        try:
            materialize(clean, neg_path, base / "negative-output")
            raise AssertionError("negative review unexpectedly materialized")
        except FoleyReviewError:
            pass

        low_material = json.loads(json.dumps(review))
        cue_id = sorted(low_material["cueReviews"])[0]
        low_material["cueReviews"][cue_id]["checks"]["MATERIAL_MATCH"]["result"] = 2
        mat_norm, _ = normalize_to(clean, low_material, "low-material.normalized.json")
        assert_not_ready(mat_norm, "material-match-2")

        low_variation = json.loads(json.dumps(review))
        low_variation["cueReviews"][cue_id]["checks"]["VARIATION_VALUE"]["result"] = 2
        var_norm, _ = normalize_to(clean, low_variation, "low-variation.normalized.json")
        assert_not_ready(var_norm, "variation-value-2")

        weather_fail = json.loads(json.dumps(review))
        weather_fail["cueReviews"][cue_id]["checks"]["UNDER_WEATHER_READABILITY"]["result"] = "fail"
        weather_norm, _ = normalize_to(clean, weather_fail, "weather-fail.normalized.json")
        assert_not_ready(weather_norm, "under-weather-fail")

        anonymous = json.loads(json.dumps(review))
        anonymous["reviewerAlias"] = ""
        anonymous["reviewedAt"] = ""
        anon_norm, _ = normalize_to(clean, anonymous, "anonymous.normalized.json", require_complete=False)
        if anon_norm.get("reviewComplete") is not False:
            raise AssertionError("blank reviewer/timestamp must make review incomplete")
        assert_not_ready(anon_norm, "anonymous")

        tampered = json.loads(json.dumps(neg_norm))
        tampered["readyForSourceMaterialization"] = True
        tampered_path = clean / "tampered-ready.normalized.json"
        tampered_path.write_text(json.dumps(tampered, indent=2) + "\n", encoding="utf-8")
        try:
            materialize(clean, tampered_path, base / "tampered-output")
            raise AssertionError("tampered ready flag unexpectedly materialized")
        except FoleyReviewError as exc:
            if "readyForSourceMaterialization" not in str(exc):
                raise

        stale = base / "stale"
        shutil.copytree(clean, stale)
        stale_take = stale / next(iter(load_context(stale)["takeRecords"]))
        raw = bytearray(stale_take.read_bytes())
        raw[-1] ^= 1
        stale_take.write_bytes(raw)
        try:
            load_context(stale)
            raise AssertionError("stale raw take bytes unexpectedly accepted")
        except FoleyReviewError:
            pass

        rights = base / "rights-false"
        build_session(rights, commercial_reuse=False)
        rights_review = positive_review(rights)
        rights_norm, _ = normalize_to(rights, rights_review, "rights-false.normalized.json")
        if rights_norm.get("reviewComplete") is not True:
            raise AssertionError("rights=false review can still be complete human evidence")
        assert_not_ready(rights_norm, "rights-false")

        stale_prov = base / "stale-provenance"
        shutil.copytree(clean, stale_prov)
        prov = stale_prov / "foley_provenance.json"
        data = json.loads(prov.read_text(encoding="utf-8")); data["recordingChain"] += " changed"
        prov.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        try:
            load_context(stale_prov)
            raise AssertionError("stale provenance unexpectedly accepted")
        except FoleyReviewError:
            pass

    print(f"Foley human review tests OK: positive {expected_takes}/{expected_takes} materialization across {expected_cues} cues plus negative, threshold, weather, identity, rights, stale-byte/provenance and tampered-ready guards verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
