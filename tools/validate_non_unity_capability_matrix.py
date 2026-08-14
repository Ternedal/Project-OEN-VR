#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "content/non_unity_capability_matrix.source.json"

EXPECTED = {
    "FOLEY_RECORDING": ("content/audio/foley_session_contract.source.json", "session-intake-ready-not-recorded"),
    "FOLEY_HUMAN_REVIEW": ("content/audio/foley_human_review_contract.source.json", "human-review-tooling-ready-not-reviewed"),
    "RADIO_VO_RECORDING": ("content/audio/radio_vo_session_contract.source.json", "session-intake-ready-not-recorded"),
    "RADIO_VO_HUMAN_REVIEW": ("content/audio/radio_vo_human_review_contract.source.json", "human-review-tooling-ready-not-reviewed"),
    "RADIO_VO_SELECTED_DRY": ("content/audio/radio_vo_selected_dry_contract.source.json", "materialization-tooling-ready-no-selected-dry-source"),
    "MUSIC_CANDIDATE_AUDITION": ("content/audio/music_candidate_audit.source.json", "artifact-audited-audition-ready-not-source-approved"),
    "MUSIC_CANONICAL_FAMILY_SELECTION": ("content/audio/music_family_selection_contract.source.json", "family-selection-tooling-ready-not-selected"),
    "MUSIC_SELECTED_SOURCE": ("content/audio/music_selected_source_contract.source.json", "materialization-tooling-ready-no-selected-music-source"),
    "AUDIO_TYPED_SOURCE_APPROVAL": ("content/audio/source_approval_contract.source.json", "typed-human-source-approval-tooling-ready-no-source-approved"),
    "AUDIO_DERIVED_MASTER": ("content/audio/derived_master_contract.source.json", "derived-master-intake-review-tooling-ready-no-master-approved"),
    "M_PRE_EVIDENCE": ("content/mpre/evidence_bundle_contract.source.json", "bundle-tooling-ready-no-human-evidence"),
}

PATH_FIELDS = {
    "sourceState", "contract", "materializationContract", "operatorDoc", "tool",
    "technicalTool", "reviewTool", "normalizer", "materializer", "validator",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []
    try:
        data = load(MATRIX)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: cannot parse capability matrix: {exc}")
        return 1

    if data.get("version") != 1:
        errors.append("matrix version must remain 1")
    if data.get("status") != "tooling-reconciled-human-device-owner-gates-open":
        errors.append("matrix top-level status drift")
    if data.get("sourceState") != "content/source_inventory.source.json":
        errors.append("matrix must keep source inventory as source-state authority")

    lanes = data.get("lanes")
    if not isinstance(lanes, list):
        errors.append("lanes must be a list")
        lanes = []
    by_id = {}
    for lane in lanes:
        if not isinstance(lane, dict):
            errors.append("lane must be an object")
            continue
        lane_id = lane.get("id")
        if not isinstance(lane_id, str) or not lane_id:
            errors.append("lane without id")
            continue
        if lane_id in by_id:
            errors.append(f"duplicate lane id: {lane_id}")
        by_id[lane_id] = lane

        for field in PATH_FIELDS:
            value = lane.get(field)
            if value is None:
                continue
            if not isinstance(value, str) or not value:
                errors.append(f"{lane_id}: {field} must be a non-empty path")
                continue
            if not (ROOT / value).exists():
                errors.append(f"{lane_id}: missing {field} path {value}")

        evidence_required = any(lane.get(flag) is True for flag in (
            "humanEvidenceRequired", "deviceEvidenceRequired", "ownerDecisionRequired"
        ))
        if evidence_required and lane.get("gateSatisfied") is not False:
            errors.append(f"{lane_id}: evidence/owner-gated lane must remain gateSatisfied=false until real evidence/decision exists")

    for lane_id, (contract_path, expected_status) in EXPECTED.items():
        lane = by_id.get(lane_id)
        if lane is None:
            errors.append(f"missing required capability lane: {lane_id}")
            continue
        if lane.get("contract") != contract_path:
            errors.append(f"{lane_id}: contract path drift")
            continue
        try:
            contract = load(ROOT / contract_path)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{lane_id}: cannot parse contract: {exc}")
            continue
        if contract.get("status") != expected_status:
            errors.append(f"{lane_id}: contract status drift: {contract.get('status')!r} != {expected_status!r}")

    audition = by_id.get("AUDIO_SOURCE_AUDITION_PACK", {})
    approval = by_id.get("AUDIO_TYPED_SOURCE_APPROVAL", {})
    if audition.get("expectedSourceCount") != 27:
        errors.append("AUDIO_SOURCE_AUDITION_PACK expectedSourceCount must remain 27")
    if approval.get("currentAuditionSourceCount") != 27:
        errors.append("AUDIO_TYPED_SOURCE_APPROVAL currentAuditionSourceCount must remain 27")
    for lane_id in ("FOLEY_RECORDING", "FOLEY_HUMAN_REVIEW"):
        lane = by_id.get(lane_id, {})
        if (lane.get("expectedCueCount"), lane.get("expectedTakeCount")) != (17, 73):
            errors.append(f"{lane_id} must remain 17 cues / 73 distinct physical take slots")
    foley_review = by_id.get("FOLEY_HUMAN_REVIEW", {})
    if foley_review.get("materializationContract") != "content/audio/foley_source_materialization_contract.source.json":
        errors.append("FOLEY_HUMAN_REVIEW must retain explicit source materialization contract")
    radio = by_id.get("RADIO_VO_RECORDING", {})
    if (radio.get("expectedCueCount"), radio.get("expectedTakeCount")) != (9, 27):
        errors.append("RADIO_VO_RECORDING must remain 9 cues x 3 takes = 27")
    music = by_id.get("MUSIC_CANDIDATE_AUDITION", {})
    if (music.get("candidateCount"), music.get("canonicalMappedFamilyCount")) != (14, 5):
        errors.append("MUSIC_CANDIDATE_AUDITION must remain 14 candidates / 5 mapped families")

    open_gate_ids = {"FOLEY_RECORDING", "FOLEY_HUMAN_REVIEW", "M_PRE_EVIDENCE", "M0B_CROSS_DEVICE", "FIRE_START_SCOPE"}
    for gate_id in open_gate_ids:
        if by_id.get(gate_id, {}).get("gateSatisfied") is not False:
            errors.append(f"{gate_id}: real-world gate must remain explicitly open")

    blocked = data.get("blockedByEvidence")
    if not isinstance(blocked, list):
        errors.append("blockedByEvidence must be a list")
    else:
        for marker in ("actual physical Foley recording", "actual human Foley material/variation/weather review"):
            if marker not in blocked:
                errors.append(f"blockedByEvidence missing: {marker}")

    if errors:
        for error in errors:
            print("ERROR:", error)
        print(f"Non-Unity capability matrix FAILED: {len(errors)} error(s).")
        return 1

    print(f"Non-Unity capability matrix OK: {len(lanes)} lanes; 27-source acquisition review plus 17-cue/73-take Foley recording+human-review boundaries current; real-world gates remain open.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
