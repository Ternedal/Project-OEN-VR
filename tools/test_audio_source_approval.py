#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import audio_source_approval_support as support
import materialize_source_approved_audio as materializer
import normalize_audio_source_approval_review as normalizer
import prepare_audio_source_approval_review as preparer


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def make_fixture(root: Path):
    repo = root / "repo"
    pack = root / "pack"
    pack.mkdir(parents=True)
    main_bytes = b"main-source"
    wood_bytes = b"wood-source"
    field_bytes = b"field-source"
    main_file = "main.wav"
    wood_source_path = "floor_creak1.wav"
    field_file = "field.ogg"
    paths = {
        "main": pack / f"audio/main/{main_file}",
        "wood": pack / f"audio/wood/{wood_source_path}",
        "field": pack / f"audio/field/{field_file}",
    }
    for path, data in ((paths["main"], main_bytes), (paths["wood"], wood_bytes), (paths["field"], field_bytes)):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    write_json(repo / support.MAIN_RECEIPT, {"records": [{
        "target": "MAIN_TARGET", "filename": main_file, "sha256": sha(main_bytes),
        "license": "CC0", "provider": "Fixture", "sourcePage": "https://example.invalid/main"
    }]})
    write_json(repo / support.EXT_RECEIPT, {"records": [{
        "target": "SFX_WOOD_PACK_ALT", "filename": "wood.zip", "sha256": "a" * 64,
        "license": "CC0", "provider": "Fixture", "sourcePage": "https://example.invalid/wood"
    }]})
    write_json(repo / support.EXT_SHORTLIST, {"members": [{
        "archiveTarget": "SFX_WOOD_PACK_ALT", "path": wood_source_path, "sha256": sha(wood_bytes)
    }]})
    write_json(repo / support.FIELD_RECEIPT, {"records": [{
        "target": "FIELD_TARGET", "filename": field_file, "sha256": sha(field_bytes),
        "license": "Public Domain", "provider": "Fixture", "sourcePage": "https://example.invalid/field"
    }]})
    for rel in (support.APPROVAL_CONTRACT, support.MATERIALIZE_CONTRACT):
        target = repo / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, target)

    upstream = []
    upstream.append(write_json(root / "main.normalized.json", {
        "version": 1, "status": "human-review-evidence-unapproved", "reviewKind": "main-acquired-originals", "reviewedAt": "2026-08-14T08:00:00Z",
        "records": [{"target": "MAIN_TARGET", "sourceFilename": main_file, "sourceSha256": sha(main_bytes), "disposition": "candidate-pass", "overall": "fixture", "checks": {}}]
    }))
    upstream.append(write_json(root / "extension.normalized.json", {
        "version": 1, "status": "human-review-evidence-unapproved", "reviewKind": "extension-source-selection", "reviewedAt": "2026-08-14T08:00:00Z",
        "records": [{"reviewPath": f"audio/wood/{wood_source_path}", "target": "SFX_WOOD_PACK_ALT", "sourcePath": wood_source_path, "sourceSha256": sha(wood_bytes), "sourceKind": "archive-member", "decision": "keep", "note": "fixture"}]
    }))
    upstream.append(write_json(root / "field.normalized.json", {
        "version": 1, "status": "human-review-evidence-unapproved", "reviewKind": "field-backlog-source-selection", "reviewedAt": "2026-08-14T08:00:00Z",
        "records": [{"target": "FIELD_TARGET", "runtimeEventCandidate": "SFX_FIXTURE", "sourceFilename": field_file, "sourceSha256": sha(field_bytes), "license": "Public Domain", "decision": "keep", "note": "fixture"}]
    }))
    return repo, pack, upstream, paths


def fill_review(template: dict, *, field_material_rating: int = 4, all_reject: bool = False) -> dict:
    payload = copy.deepcopy(template)
    payload["reviewedAt"] = "2026-08-14T08:30:00Z"
    payload["reviewerAlias"] = "fixture-approver"
    for record in payload["records"]:
        record["sourceDecision"] = "reject-source" if all_reject or record["sourceKey"].startswith("extension::") else "approve-source"
        for check_id, check in record["checks"].items():
            if check_id == "MATERIAL_MATCH":
                check["value"] = field_material_rating if record["sourceKey"].startswith("field::") else 4
            elif check_id == "VARIATION_VALUE":
                check["value"] = 4
            elif check_id in {"LOOP_OR_SLICE", "TRANSIENT_QUALITY", "SPEECH_SPACE"}:
                check["value"] = "not-applicable" if record["sourceKey"].startswith("extension::") else "pass"
            else:
                check["value"] = "pass"
            check["note"] = "fixture observation"
        record["overallNote"] = "fixture overall"
    return payload


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        repo, pack, upstream, paths = make_fixture(root)
        template = preparer.prepare(upstream, pack, repo)
        assert len(template["records"]) == 3
        assert all(x["sourceDecision"] == "" for x in template["records"])
        html = (pack / "source_approval_review.html").read_text(encoding="utf-8")
        assert "Material/context match (1–5)" in html
        assert "audio/wood/floor_creak1.wav" in html

        mixed_payload = fill_review(template)
        mixed = normalizer.normalize(mixed_payload, upstream, pack, repo, require_complete=True)
        assert mixed["status"] == "human-source-approval-evidence-evaluated-not-materialized"
        assert mixed["coverage"] == {"decided": 3, "total": 3, "eligibleForSourceApproval": 2, "complete": True}
        eligible = [x for x in mixed["records"] if x["sourceApprovedEligible"]]
        assert len(eligible) == 2
        assert not any(x["sourceKey"].startswith("extension::") and x["sourceApprovedEligible"] for x in mixed["records"])

        low_rating = normalizer.normalize(fill_review(template, field_material_rating=2), upstream, pack, repo, require_complete=True)
        field = next(x for x in low_rating["records"] if x["sourceKey"].startswith("field::"))
        assert field["sourceDecision"] == "approve-source"
        assert field["sourceApprovedEligible"] is False
        assert low_rating["coverage"]["eligibleForSourceApproval"] == 1

        approval_path = write_json(root / "approval.normalized.json", mixed)
        out = root / "approved"
        receipt = materializer.materialize(approval_path, upstream, pack, out, repo)
        assert receipt["approvedCount"] == 2
        assert all(x["sourceApproved"] and not x["derivedMasterApproved"] and not x["runtimeApproved"] and not x["releaseApproved"] for x in receipt["records"])
        assert (out / "main/MAIN_TARGET/main.wav").read_bytes() == paths["main"].read_bytes()
        assert (out / "field/FIELD_TARGET/field.ogg").read_bytes() == paths["field"].read_bytes()
        assert not (out / "extension/SFX_WOOD_PACK_ALT/floor_creak1.wav").exists()

        tampered = copy.deepcopy(mixed)
        tampered["records"][0]["sourceApprovedEligible"] = not tampered["records"][0]["sourceApprovedEligible"]
        tampered_path = write_json(root / "tampered-approval.json", tampered)
        try:
            materializer.materialize(tampered_path, upstream, pack, root / "tampered-out", repo)
        except support.ApprovalError as exc:
            assert "disagrees with current evidence" in str(exc)
        else:
            raise AssertionError("tampered eligibility flag must be rejected")

        rejected = normalizer.normalize(fill_review(template, all_reject=True), upstream, pack, repo, require_complete=True)
        assert rejected["coverage"]["complete"] is True
        assert rejected["coverage"]["eligibleForSourceApproval"] == 0
        rejected_path = write_json(root / "rejected.json", rejected)
        try:
            materializer.materialize(rejected_path, upstream, pack, root / "none", repo)
        except support.ApprovalError as exc:
            assert "no source is eligible" in str(exc)
        else:
            raise AssertionError("complete negative review must not materialize any source-approved bytes")

        paths["main"].write_bytes(paths["main"].read_bytes() + b"tamper")
        try:
            preparer.prepare(upstream, pack, repo)
        except support.ApprovalError as exc:
            assert "SHA mismatch" in str(exc)
        else:
            raise AssertionError("changed audition-pack source bytes must be rejected")

    print("Audio source approval self-test OK: typed 1-5/categorical gate + threshold + mixed/negative evidence + tamper guards + explicit byte-identical source-approved materialization.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
