#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTING = ROOT / "content/audio/audio_source_routing.source.json"
CUES = ROOT / "content/audio/audio_cues.source.json"
FOLEY_QUEUE = ROOT / "content/audio/foley_recording_queue.source.json"
RECEIPTS = [
    ROOT / "content/audio/acquisition_receipt.source.json",
    ROOT / "content/audio/acquisition_extension_receipt.source.json",
    ROOT / "content/audio/acquisition_field_backlog_receipt.source.json",
    ROOT / "content/audio/acquisition_field_backlog_final_receipt.source.json",
]
EXPECTED_EXTENSION = {
    "SFX_FIRE_FUEL_ADD_001",
    "SFX_ANIMAL_CAMP_APPROACH_001",
    "SFX_ANIMAL_RETREAT_001",
    "SFX_FOOD_DISTURBED_001",
}
EXPECTED_PENDING = {"SFX_FIRE_IGNITION_001", "SFX_FIRE_WET_HISS_001"}
EXPECTED_LICENSED = {"SFX_ANIMAL_DISTANT_001"}
EXPECTED_DERIVED = {"SFX_SHELTER_COLLAPSE_PARTIAL_001"}
EXPECTED_OWNER = {"SFX_FIRESTEEL_STRIKE_001"}
BEACH_PARTIAL = "SFX_AMB_BEACH_CAMP_001"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def receipt_targets() -> set[str]:
    out: set[str] = set()
    for path in RECEIPTS:
        data = load(path)
        records = data.get("records")
        if not isinstance(records, list):
            raise RuntimeError(f"{path.name}: records must be a list")
        for record in records:
            if isinstance(record, dict) and isinstance(record.get("target"), str):
                out.add(record["target"])
    return out


def queue_cues() -> set[str]:
    data = load(FOLEY_QUEUE)
    out: set[str] = set()
    for session in data.get("sessions", []):
        if not isinstance(session, dict):
            continue
        for cue in session.get("cues", []):
            if not isinstance(cue, dict) or not isinstance(cue.get("id"), str):
                continue
            if cue["id"] in out:
                raise RuntimeError(f"duplicate Foley queue cue: {cue['id']}")
            out.add(cue["id"])
    return out


def main() -> int:
    errors: list[str] = []
    try:
        routing = load(ROUTING); cue_data = load(CUES); acquired_targets = receipt_targets(); foley = queue_cues()
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: cannot load source-routing inputs: {exc}")
        return 1

    needs_source = {
        cue.get("id") for cue in cue_data.get("cues", [])
        if isinstance(cue, dict) and cue.get("productionStatus") == "needs_source" and isinstance(cue.get("id"), str)
    }
    if len(needs_source) != 35:
        errors.append(f"audio cue catalog must currently contain exactly 35 needs_source cues, got {len(needs_source)}")

    routes = routing.get("routes")
    if not isinstance(routes, list):
        errors.append("routing routes must be a list")
        routes = []
    by_id: dict[str, dict] = {}
    allowed = set(routing.get("routeTypes", []))
    for route in routes:
        if not isinstance(route, dict) or not isinstance(route.get("cueId"), str):
            errors.append("invalid route entry")
            continue
        cue_id = route["cueId"]
        if cue_id in by_id:
            errors.append(f"duplicate route for {cue_id}")
        by_id[cue_id] = route
        if route.get("routeType") not in allowed:
            errors.append(f"{cue_id}: unsupported routeType {route.get('routeType')!r}")
        backing = route.get("backing")
        if not isinstance(backing, str) or not (ROOT / backing).is_file():
            errors.append(f"{cue_id}: missing backing path {backing!r}")
        if not isinstance(route.get("next"), str) or not route["next"].strip():
            errors.append(f"{cue_id}: next action missing")

    if set(by_id) != needs_source:
        errors.append(f"needs_source route coverage mismatch: missing={sorted(needs_source-set(by_id))}, extra={sorted(set(by_id)-needs_source)}")

    physical = {cue_id for cue_id, route in by_id.items() if route.get("routeType") == "physical-foley-session"}
    if physical != foley or len(physical) != 13:
        errors.append(f"physical Foley route set must exactly equal current 13-cue queue: routed={sorted(physical)} queue={sorted(foley)}")

    pools = {cue_id: route for cue_id, route in by_id.items() if route.get("routeType") == "acquired-candidate-pool"}
    if len(pools) != 13:
        errors.append(f"expected 13 acquired-candidate-pool routes, got {len(pools)}")
    for cue_id, route in pools.items():
        targets = route.get("sourceTargets")
        if not isinstance(targets, list) or not targets or not all(isinstance(x, str) and x for x in targets):
            errors.append(f"{cue_id}: acquired pool needs sourceTargets")
            continue
        missing = sorted(set(targets) - acquired_targets)
        if missing:
            errors.append(f"{cue_id}: acquired sourceTargets absent from receipts: {missing}")
        if "human-listening" not in str(route.get("status", "")):
            errors.append(f"{cue_id}: acquired candidate route must remain human-listening-pending")

    beach = by_id.get(BEACH_PARTIAL, {})
    if beach.get("routeType") != "acquired-candidate-pool" or beach.get("status") != "partial-candidate-coverage-human-listening-plus-palm-pending":
        errors.append("Beach Camp must remain the single explicit acquired-pool route with a known PalmCanopy acquisition dependency")
    if "PalmCanopy" not in str(beach.get("next", "")):
        errors.append("Beach Camp route must explicitly preserve the PalmCanopy acquisition gap")

    partitions = {
        "physical-recording-extension-pending": EXPECTED_EXTENSION,
        "source-acquisition-or-recording-pending": EXPECTED_PENDING,
        "licensed-source-acquisition-pending": EXPECTED_LICENSED,
        "derived-after-approved-sources": EXPECTED_DERIVED,
        "owner-gated": EXPECTED_OWNER,
    }
    for route_type, expected in partitions.items():
        actual = {cue_id for cue_id, route in by_id.items() if route.get("routeType") == route_type}
        if actual != expected:
            errors.append(f"{route_type} route set drift: got={sorted(actual)} expected={sorted(expected)}")

    owner = by_id.get("SFX_FIRESTEEL_STRIKE_001", {})
    if owner.get("status") != "issue-8-owner-decision-pending" or owner.get("backing") != "content/contracts/issue8.reconciliation.source.json":
        errors.append("firesteel must remain explicitly bound to issue #8 owner decision")
    for cue_id, route in by_id.items():
        if cue_id != "SFX_FIRESTEEL_STRIKE_001" and route.get("routeType") == "owner-gated":
            errors.append(f"{cue_id}: only firesteel is owner-gated in current source routing")

    collapse = by_id.get("SFX_SHELTER_COLLAPSE_PARTIAL_001", {})
    dependencies = set(collapse.get("sourceDependencies", []))
    if dependencies != {"SFX_SHELTER_CREAK_HIGH_001", "SFX_BEAM_SHIFT_001"} or not dependencies <= foley:
        errors.append("partial-collapse derivative dependencies must remain the approved shelter/timber source family")

    counts = Counter(route.get("routeType") for route in by_id.values())
    expected_counts = {
        "physical-foley-session": 13,
        "acquired-candidate-pool": 13,
        "derived-after-approved-sources": 1,
        "physical-recording-extension-pending": 4,
        "source-acquisition-or-recording-pending": 2,
        "licensed-source-acquisition-pending": 1,
        "owner-gated": 1,
    }
    if dict(counts) != expected_counts:
        errors.append(f"route type counts drift: got={dict(counts)} expected={expected_counts}")

    summary = routing.get("summary", {})
    if summary.get("needsSourceCueCount") != 35 or summary.get("sourceApproved") != 0:
        errors.append("routing summary must remain 35 needs-source / 0 source-approved")
    if summary.get("physicalFoleySessionReady") != 13:
        errors.append("routing summary must report 13 current physical-Foley cues")
    if summary.get("acquiredCandidatePool") != 12 or summary.get("partialCandidateCoverage") != 1:
        errors.append("routing summary must separate 12 acquired-pool cues without a known extra acquisition from 1 Beach/Palm partial route")
    if summary.get("acquiredCandidatePool", 0) + summary.get("partialCandidateCoverage", 0) != len(pools):
        errors.append("routing summary acquired+partial pool count must equal the 13 acquired-candidate-pool routes")
    expected_summary_rest = {
        "derivedAfterApprovedSources": 1,
        "physicalRecordingExtensionPending": 4,
        "sourceAcquisitionOrRecordingPending": 2,
        "licensedSourceAcquisitionPending": 1,
        "ownerGated": 1,
    }
    for key, value in expected_summary_rest.items():
        if summary.get(key) != value:
            errors.append(f"routing summary {key} drift: {summary.get(key)!r} != {value}")

    if errors:
        for error in errors:
            print("ERROR:", error)
        print(f"Audio source routing FAILED: {len(errors)} error(s).")
        return 1
    print("Audio source routing OK: all 35 needs-source cues have exactly one route; 13 current Foley, 13 acquired-pool routes (12 + 1 explicit Beach/Palm partial), 8 pending/derived/owner routes, 0 source approvals implied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
