#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import sys
import tempfile
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import audio_derived_master_support as support
import materialize_derived_master_approved_audio as materializer
import normalize_audio_derived_master_review as normalizer
import prepare_audio_derived_master_review as preparer


def write_json(path: Path, value) -> Path:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def write_pcm24(path: Path, samples: list[int], *, rate: int = 48000, channels: int = 1) -> None:
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(channels); wav.setsampwidth(3); wav.setframerate(rate)
        wav.writeframes(b"".join(int(sample).to_bytes(3, "little", signed=True) for sample in samples))


def write_pcm16(path: Path, samples: list[int], *, rate: int = 48000) -> None:
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(rate)
        wav.writeframes(b"".join(int(sample).to_bytes(2, "little", signed=True) for sample in samples))


def source_receipt(path: Path, sha1: str = "1" * 64, sha2: str = "2" * 64) -> Path:
    return write_json(path, {
        "version": 1,
        "status": "source-approved-original-materialized-from-human-gate",
        "records": [
            {"sourceKey": "main::A", "approvedSha256": sha1, "sourceApproved": True},
            {"sourceKey": "field::B", "approvedSha256": sha2, "sourceApproved": True},
        ],
    })


def submission(path: Path, sha1: str = "1" * 64, sha2: str = "2" * 64, *, empty_recipe: bool = False) -> Path:
    recipe = [] if empty_recipe else [{"operation": "trim-and-fade", "details": "Trim clean region and apply 20 ms edge fades."}]
    return write_json(path, {
        "version": 1,
        "status": "derived-master-submission-unvalidated",
        "masters": [
            {"masterId": "DM_A", "sourceKey": "main::A", "sourceApprovedSha256": sha1, "filename": "dm_a.wav", "intendedUse": "ambience bed", "editRecipe": recipe},
            {"masterId": "DM_B", "sourceKey": "field::B", "sourceApprovedSha256": sha2, "filename": "dm_b.wav", "intendedUse": "field one-shot", "editRecipe": [{"operation": "resample-and-fade", "details": "Quality resample to 48 kHz and fade edges."}]},
        ],
    })


def fill_review(template: dict, *, low_material: bool = False, all_reject: bool = False) -> dict:
    payload = copy.deepcopy(template)
    payload["reviewedAt"] = "2026-08-14T09:00:00Z"
    payload["reviewerAlias"] = "fixture-derived-reviewer"
    for i, record in enumerate(payload["records"]):
        record["decision"] = "reject-derived-master" if all_reject or i == 1 else "approve-derived-master"
        for check_id, check in record["checks"].items():
            if check_id == "MATERIAL_MATCH": check["value"] = 2 if low_material and i == 0 else 4
            elif check_id == "VARIATION_VALUE": check["value"] = 4
            elif check_id in {"LOOP_OR_SLICE", "TRANSIENT_QUALITY", "SPEECH_SPACE"}: check["value"] = "not-applicable" if i == 1 else "pass"
            else: check["value"] = "pass"
            check["note"] = "fixture derived observation"
        record["overallNote"] = "fixture derived overall"
    return payload


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td); masters = root / "masters"; masters.mkdir()
        write_pcm24(masters / "dm_a.wav", [1000, -1000, 2000, -2000] * 100)
        write_pcm24(masters / "dm_b.wav", [1500, -1500, 2500, -2500] * 100)
        src = source_receipt(root / "source_receipt.json")
        sub = submission(root / "submission.json")
        tech = support.validate_technical_submission(sub, src, masters, ROOT)
        assert tech["status"] == "derived-master-technical-intake-passed-not-listening-approved"
        assert tech["validatedMasterCount"] == 2
        assert all(x["technicalProbe"]["sampleRateHz"] == 48000 and x["technicalProbe"]["bitDepth"] == 24 and x["technicalProbe"]["fullScaleSampleCount"] == 0 for x in tech["records"])
        tech_path = write_json(root / "technical.json", tech)

        template = preparer.prepare(tech_path, sub, src, masters, ROOT)
        assert len(template["records"]) == 2
        assert (masters / "derived_master_review.html").is_file()

        mixed = normalizer.normalize(fill_review(template), tech_path, sub, src, masters, ROOT, require_complete=True)
        assert mixed["coverage"] == {"decided": 2, "total": 2, "eligibleForDerivedMasterApproval": 1, "complete": True}
        assert sum(1 for x in mixed["records"] if x["derivedMasterApprovedEligible"]) == 1
        review_path = write_json(root / "review.normalized.json", mixed)
        out = root / "approved"
        receipt = materializer.materialize(review_path, tech_path, sub, src, masters, out, ROOT)
        assert receipt["approvedCount"] == 1
        assert (out / "dm_a.wav").read_bytes() == (masters / "dm_a.wav").read_bytes()
        assert not (out / "dm_b.wav").exists()
        assert receipt["records"][0]["derivedMasterApproved"] is True
        assert receipt["records"][0]["runtimeApproved"] is False and receipt["records"][0]["releaseApproved"] is False

        low = normalizer.normalize(fill_review(template, low_material=True), tech_path, sub, src, masters, ROOT, require_complete=True)
        assert low["coverage"]["eligibleForDerivedMasterApproval"] == 0
        low_path = write_json(root / "low.json", low)
        try: materializer.materialize(low_path, tech_path, sub, src, masters, root / "low-out", ROOT)
        except support.DerivedError as exc: assert "no derived master is eligible" in str(exc)
        else: raise AssertionError("material score below threshold must block derived approval")

        tampered = copy.deepcopy(mixed); tampered["records"][0]["derivedMasterApprovedEligible"] = False
        tampered_path = write_json(root / "tampered.json", tampered)
        try: materializer.materialize(tampered_path, tech_path, sub, src, masters, root / "tampered-out", ROOT)
        except support.DerivedError as exc: assert "stored eligibility disagrees" in str(exc)
        else: raise AssertionError("tampered derived eligibility must be rejected")

        rejected = normalizer.normalize(fill_review(template, all_reject=True), tech_path, sub, src, masters, ROOT, require_complete=True)
        assert rejected["coverage"]["complete"] is True and rejected["coverage"]["eligibleForDerivedMasterApproval"] == 0

        changed = masters / "dm_a.wav"; data = changed.read_bytes(); changed.write_bytes(data + b"drift")
        try: preparer.prepare(tech_path, sub, src, masters, ROOT)
        except support.DerivedError as exc: assert "technical receipt is stale" in str(exc)
        else: raise AssertionError("changed derived bytes must invalidate technical receipt")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td); masters = root / "masters"; masters.mkdir()
        write_pcm16(masters / "dm_a.wav", [100, -100] * 20); write_pcm24(masters / "dm_b.wav", [100, -100] * 20)
        src = source_receipt(root / "source.json"); sub = submission(root / "sub.json")
        try: support.validate_technical_submission(sub, src, masters, ROOT)
        except support.DerivedError as exc: assert "expected 24-bit PCM" in str(exc)
        else: raise AssertionError("16-bit derived master must be rejected")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td); masters = root / "masters"; masters.mkdir()
        write_pcm24(masters / "dm_a.wav", [8388607, 0, -100] * 20); write_pcm24(masters / "dm_b.wav", [100, -100] * 20)
        src = source_receipt(root / "source.json"); sub = submission(root / "sub.json")
        try: support.validate_technical_submission(sub, src, masters, ROOT)
        except support.DerivedError as exc: assert "full-scale/clipping" in str(exc)
        else: raise AssertionError("full-scale samples must be rejected")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td); masters = root / "masters"; masters.mkdir()
        write_pcm24(masters / "dm_a.wav", [100, -100] * 20); write_pcm24(masters / "dm_b.wav", [100, -100] * 20)
        src = source_receipt(root / "source.json"); sub = submission(root / "sub.json", empty_recipe=True)
        try: support.validate_technical_submission(sub, src, masters, ROOT)
        except support.DerivedError as exc: assert "editRecipe" in str(exc)
        else: raise AssertionError("empty edit recipe must be rejected")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td); masters = root / "masters"; masters.mkdir()
        write_pcm24(masters / "dm_a.wav", [100, -100] * 20); write_pcm24(masters / "dm_b.wav", [100, -100] * 20)
        same = support.sha256_file(masters / "dm_a.wav")
        src = source_receipt(root / "source.json", sha1=same); sub = submission(root / "sub.json", sha1=same)
        try: support.validate_technical_submission(sub, src, masters, ROOT)
        except support.DerivedError as exc: assert "derived bytes equal source-approved original" in str(exc)
        else: raise AssertionError("byte-identical source must not be relabelled as derived")

    print("Derived master pipeline self-test OK: 48k/24 PCM intake + edit/source binding + clipping/format/no-edit guards + repeated human listening + explicit approval materialization.")
    return 0


if __name__ == "__main__": raise SystemExit(main())
