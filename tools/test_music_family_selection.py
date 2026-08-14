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

import materialize_music_selected_sources as materializer
import music_family_selection_support as support
import normalize_music_family_selection as normalizer
import prepare_music_family_selection as preparer


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def make_fixture(root: Path):
    repo = root / "repo"
    candidates = root / "candidates"
    candidates.mkdir(parents=True)
    mappings = [
        ("MUS_CAMP_BASE_001", "MUS_Camp_WarmTexture", 3, True),
        ("MUS_STORM_BASE_001", "MUS_Storm_Phase1", 2, True),
        ("MUS_STORM_PRESSURE_001", "MUS_Storm_Phase2", 2, True),
        ("MUS_SIGNAL_FINAL_001", "MUS_Storm_Phase3", 2, True),
        ("MUS_RESCUE_RELEASE_001", "MUS_Finale_Success", 2, False),
    ]
    files = []
    review_records = []
    for target, family, count, loop in mappings:
        for variant in range(1, count + 1):
            filename = f"{family}_{variant:02d}.wav"
            data = f"fixture:{filename}".encode()
            (candidates / filename).write_bytes(data)
            record = {
                "event_id": family,
                "variant": variant,
                "file": filename,
                "state": "fixture",
                "loop": loop,
                "duration_seconds": 1.0,
                "channels": 2,
                "sample_rate_hz": 48000,
                "bit_depth": 24,
                "bytes": len(data),
                "sha256": sha(data),
                "canonicalTarget": target,
                "mappingStatus": "candidate-for-canonical-audition",
            }
            files.append(record)
            checks = {name: {"result": "pass", "note": "fixture"} for name in support.expected_checks(record)}
            review_records.append({
                "file": filename,
                "sha256": record["sha256"],
                "candidateFamily": family,
                "canonicalTarget": target,
                "mappingStatus": record["mappingStatus"],
                "fit": "keep" if variant == 1 else "maybe",
                "checks": checks,
                "overallNote": "fixture",
            })
    for variant in range(1, 4):
        family = "MUS_Warning_LowPulse"
        filename = f"{family}_{variant:02d}.wav"
        data = f"fixture:{filename}".encode()
        (candidates / filename).write_bytes(data)
        record = {
            "event_id": family,
            "variant": variant,
            "file": filename,
            "state": "warning",
            "loop": True,
            "duration_seconds": 1.0,
            "channels": 2,
            "sample_rate_hz": 48000,
            "bit_depth": 24,
            "bytes": len(data),
            "sha256": sha(data),
            "canonicalTarget": None,
            "mappingStatus": "unmapped-extra-candidate",
        }
        files.append(record)
        review_records.append({
            "file": filename,
            "sha256": record["sha256"],
            "candidateFamily": family,
            "canonicalTarget": None,
            "mappingStatus": record["mappingStatus"],
            "fit": "keep",
            "checks": {name: {"result": "pass", "note": "fixture"} for name in support.expected_checks(record)},
            "overallNote": "fixture warning only",
        })
    assert len(files) == 14
    audit = {
        "version": 1,
        "status": "artifact-audited-audition-ready-not-source-approved",
        "canonicalMappings": [{"canonicalCueId": t, "candidateFamily": f, "rule": "fixture"} for t, f, _, _ in mappings],
        "unmappedFamilies": [{"candidateFamily": "MUS_Warning_LowPulse", "reason": "fixture unmapped"}],
        "files": files,
    }
    write_json(repo / support.AUDIT, audit)
    write_json(repo / support.AUDIO_CUES, {"cues": [{"id": t} for t, _, _, _ in mappings]})
    for rel in (support.SELECTION_CONTRACT, support.MATERIALIZE_CONTRACT):
        target = repo / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, target)
    audition = root / "music_audition.normalized.json"
    write_json(audition, {
        "version": 1,
        "status": "human-music-audition-evidence-unapproved",
        "reviewedAt": "2026-08-14T08:00:00Z",
        "reviewerRole": "fixture-reviewer",
        "candidateAudit": str(support.AUDIT),
        "records": review_records,
    })
    return repo, candidates, audition, mappings


def fill_selection(template: dict, mappings, *, negative: bool = False) -> dict:
    payload = copy.deepcopy(template)
    payload["reviewedAt"] = "2026-08-14T08:15:00Z"
    payload["reviewerAlias"] = "fixture-selector"
    family_to_first = {family: f"{family}_01.wav" for _, family, _, _ in mappings}
    for i, item in enumerate(payload["families"]):
        if negative and i == 0:
            item["decision"] = "needs-new-source"
            item["selectedFile"] = ""
        else:
            item["decision"] = "select"
            item["selectedFile"] = family_to_first[item["candidateFamily"]]
        item["note"] = "fixture selection"
    return payload


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        repo, candidates, audition, mappings = make_fixture(root)
        template = preparer.prepare(audition, candidates, repo)
        assert len(template["families"]) == 5
        assert len(template["bindings"]["candidateHashes"]) == 14
        html = (candidates / "music_family_selection.html").read_text(encoding="utf-8")
        assert "MUS_CAMP_BASE_001" in html
        assert "MUS_Warning_LowPulse_01.wav" not in json.dumps(template)

        positive_payload = fill_selection(template, mappings)
        positive = normalizer.normalize(positive_payload, audition, repo, require_complete=True)
        assert positive["status"] == "human-music-family-selection-evidence-unapproved"
        assert positive["coverage"] == {"decided": 5, "total": 5, "selected": 5, "complete": True}
        assert positive["readyForSourceMaterialization"] is True
        assert positive["unmappedFamiliesExcluded"] == ["MUS_Warning_LowPulse"]

        negative = normalizer.normalize(fill_selection(template, mappings, negative=True), audition, repo, require_complete=True)
        assert negative["coverage"]["complete"] is True
        assert negative["readyForSourceMaterialization"] is False
        assert any(r["decision"] == "needs-new-source" for r in negative["records"])

        bad = fill_selection(template, mappings)
        first = bad["families"][0]
        first["selectedFile"] = f"{first['candidateFamily']}_02.wav"
        try:
            normalizer.normalize(bad, audition, repo, require_complete=True)
        except support.SelectionError as exc:
            assert "not an eligible" in str(exc)
        else:
            raise AssertionError("maybe candidate must be ineligible for selection")

        positive_path = root / "music_selection.normalized.json"
        write_json(positive_path, positive)
        output = root / "selected"
        receipt = materializer.materialize(positive_path, audition, candidates, output, repo)
        assert receipt["selectedCount"] == 5
        assert receipt["unmappedFamiliesMaterialized"] == []
        assert receipt["sourceApprovalPromoted"] is False
        assert not (output / "MUS_Warning_LowPulse.wav").exists()
        for record in receipt["records"]:
            src = candidates / record["sourceFilename"]
            dst = output / record["selectedSourceFilename"]
            assert src.read_bytes() == dst.read_bytes()
            assert record["sourceSha256"] == record["selectedSourceSha256"]

        negative_path = root / "negative.normalized.json"
        write_json(negative_path, negative)
        try:
            materializer.materialize(negative_path, audition, candidates, root / "nope", repo)
        except support.SelectionError as exc:
            assert "not ready" in str(exc)
        else:
            raise AssertionError("negative selection must not materialize")

        chosen = candidates / mappings[0][1] / "not-used"
        actual = candidates / f"{mappings[0][1]}_01.wav"
        actual.write_bytes(actual.read_bytes() + b"tamper")
        try:
            materializer.materialize(positive_path, audition, candidates, root / "tampered", repo)
        except support.SelectionError as exc:
            assert "hash mismatch" in str(exc)
        else:
            raise AssertionError("tampered candidate bytes must be rejected")

    print("Music family selection self-test OK: 5 positive selections + negative complete result + maybe/unmapped/tampered guards + byte-identical materialization.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
