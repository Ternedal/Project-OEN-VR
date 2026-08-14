#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "content/audio/acquisition_field_backlog_final_receipt.source.json"
REGISTRY = ROOT / "content/audio/acquisition_candidates.field_backlog_pending.source.json"
COVERAGE = ROOT / "content/audio/field_backlog_coverage.source.json"
EXPECTED = {
    "SFX_AMB_JUNGLE_CANOPY_WIND_ALT_01": {
        "runtime": "SFX_AMB_Jungle_CanopyWind",
        "sha256": "0977950ade4efe3c1a975c4c7c983b1487bfeb4adb456895e4d0b637ba81373b",
        "bytes": 41941854,
        "sampleRateHz": 48000,
        "bitDepth": 16,
        "channels": 2,
        "fullScaleSampleCount": 0,
    },
    "SFX_WTH_STORM_ROUGH_OCEAN_ALT_01": {
        "runtime": "SFX_WTH_Storm_RoughOcean",
        "sha256": "3406e8219f093870a83584d6295e415b4ef175e75d25c9de081e3274b436cf9d",
        "bytes": 95825802,
        "sampleRateHz": 48000,
        "bitDepth": 24,
        "channels": 2,
        "fullScaleSampleCount": 1,
    },
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []
    receipt = load(RECEIPT)
    registry = load(REGISTRY)
    coverage = load(COVERAGE)

    evidence = receipt.get("evidenceRun", {})
    expected_evidence = {
        "runId": 31799582783,
        "headSha": "bfd42abdde2cde407a0c9334e033cf2cc431d7e5",
        "artifactId": 9218700659,
        "artifactDigest": "sha256:783dbaace081a2ecf234d4e9f39bf978d977f6bac614380b253eaf306c400833",
        "artifactSizeBytes": 137770738,
    }
    if evidence != expected_evidence:
        errors.append(f"final field evidence binding drift: {evidence!r}")

    records = {r.get("target"): r for r in receipt.get("records", []) if isinstance(r, dict)}
    candidates = {r.get("target"): r for r in registry.get("candidates", []) if isinstance(r, dict)}
    if set(records) != set(EXPECTED) or set(candidates) != set(EXPECTED):
        errors.append(f"final target set drift: receipt={sorted(records)} registry={sorted(candidates)}")

    for target, expected in EXPECTED.items():
        record = records.get(target, {})
        candidate = candidates.get(target, {})
        if record.get("runtimeEventCandidate") != expected["runtime"] or candidate.get("runtimeEventCandidate") != expected["runtime"]:
            errors.append(f"{target}: runtime mapping drift")
        for key in ("sha256", "bytes"):
            if record.get(key) != expected[key]:
                errors.append(f"{target}: {key} drift")
        if record.get("status") != "acquired-original-not-listening-approved":
            errors.append(f"{target}: source status must remain acquired-unapproved")
        if candidate.get("license") not in {"CC0", "Public Domain"}:
            errors.append(f"{target}: candidate license outside field policy")
        if not str(candidate.get("directDownload", "")).startswith("https://"):
            errors.append(f"{target}: direct original download missing")
        probe = record.get("technicalProbe", {})
        for key in ("sampleRateHz", "bitDepth", "channels"):
            if probe.get(key) != expected[key]:
                errors.append(f"{target}: technicalProbe {key} drift")
        qa = record.get("objectiveQa", {})
        if qa.get("fullScaleSampleCount") != expected["fullScaleSampleCount"]:
            errors.append(f"{target}: fullScaleSampleCount drift")
        if not isinstance(qa.get("note"), str) or "human" not in qa["note"].lower():
            errors.append(f"{target}: objective QA must preserve human-listening boundary")

    ocean = candidates.get("SFX_WTH_STORM_ROUGH_OCEAN_ALT_01", {})
    if ocean.get("directDownload") != "https://lasonotheque.org/UPLOAD/bwf-en/2570.wav":
        errors.append("rough-ocean direct permalink regressed to an unverified path")

    unresolved = registry.get("stillUnresolved")
    if not isinstance(unresolved, list) or len(unresolved) != 1 or unresolved[0].get("runtimeEvent") != "SFX_AMB_Beach_PalmCanopy":
        errors.append("PalmCanopy must remain the single explicit unresolved field acquisition")
    elif unresolved[0].get("status") != "source-acquisition-pending":
        errors.append("PalmCanopy must remain source-acquisition-pending")

    events = {r.get("eventId"): r for r in coverage.get("events", []) if isinstance(r, dict)}
    for expected in EXPECTED.values():
        event = events.get(expected["runtime"], {})
        if event.get("status") != "acquired-candidate-human-listening-pending":
            errors.append(f"{expected['runtime']}: coverage must be acquired candidate awaiting human listening")
        if event.get("receipt") != "content/audio/acquisition_field_backlog_final_receipt.source.json":
            errors.append(f"{expected['runtime']}: coverage receipt binding drift")
        if event.get("sourceSha256") != expected["sha256"]:
            errors.append(f"{expected['runtime']}: coverage SHA drift")

    palm = events.get("SFX_AMB_Beach_PalmCanopy", {})
    if palm.get("status") != "source-acquisition-pending":
        errors.append("PalmCanopy coverage must remain acquisition-pending")
    summary = coverage.get("summary")
    expected_summary = {
        "trackedRuntimeEvents": 11,
        "acquiredSourceCandidatePendingHuman": 10,
        "sourceAcquisitionPending": 1,
        "sourceApproved": 0,
        "runtimeProducedFromThisCoverage": 0,
    }
    if summary != expected_summary:
        errors.append(f"field coverage summary drift: {summary!r}")

    if errors:
        for error in errors:
            print("ERROR:", error)
        print(f"Final field acquisition validation FAILED: {len(errors)} error(s).")
        return 1

    print("Final field acquisition OK: 2 exact acquired originals pinned; field coverage 10 acquired / 1 pending; PalmCanopy remains open; 0 source approvals promoted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
