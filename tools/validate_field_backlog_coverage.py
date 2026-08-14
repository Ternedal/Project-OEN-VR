#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "content/audio/field_backlog_coverage.source.json"
EXPECTED_EVENTS = {
    "SFX_AMB_Beach_CoastalWind",
    "SFX_AMB_Beach_PalmCanopy",
    "SFX_AMB_Jungle_CanopyWind",
    "SFX_AMB_Jungle_DeepBed",
    "SFX_AMB_Ridge_WindBed",
    "SFX_WTH_Storm_RoughOcean",
    "SFX_WTH_Storm_WindGust",
    "SFX_WTH_Thunder_Near",
    "SFX_NAT_Bird_ShoreCall",
    "SFX_NAT_Insect_NightChirp",
    "SFX_ENV_Fire_Pop",
}
ALLOWED = {"source-acquisition-pending", "acquired-candidate-human-listening-pending"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    data = load(DATA)
    errors: list[str] = []
    events = data.get("events")
    if not isinstance(events, list):
        print("ERROR: events must be a list")
        return 1

    by_id = {}
    for item in events:
        if not isinstance(item, dict) or not isinstance(item.get("eventId"), str):
            errors.append("invalid event entry")
            continue
        event_id = item["eventId"]
        if event_id in by_id:
            errors.append(f"duplicate eventId {event_id}")
        by_id[event_id] = item
        if item.get("status") not in ALLOWED:
            errors.append(f"{event_id}: invalid status {item.get('status')!r}")

    if set(by_id) != EXPECTED_EVENTS:
        errors.append(f"event set mismatch: got={sorted(by_id)} expected={sorted(EXPECTED_EVENTS)}")

    acquired = 0
    pending = 0
    receipt_cache = {}
    for event_id, item in by_id.items():
        status = item.get("status")
        if status == "source-acquisition-pending":
            pending += 1
            if item.get("sourceTarget") or item.get("sourceSha256"):
                errors.append(f"{event_id}: pending row must not claim acquired source identity")
            continue
        if status == "acquired-candidate-human-listening-pending":
            acquired += 1
            receipt_rel = item.get("receipt")
            target = item.get("sourceTarget")
            sha = item.get("sourceSha256")
            if not all(isinstance(v, str) and v for v in (receipt_rel, target, sha)):
                errors.append(f"{event_id}: acquired candidate identity is incomplete")
                continue
            receipt_path = ROOT / receipt_rel
            if not receipt_path.is_file():
                errors.append(f"{event_id}: missing receipt {receipt_rel}")
                continue
            receipt = receipt_cache.setdefault(receipt_rel, load(receipt_path))
            records = {r.get("target"): r for r in receipt.get("records", []) if isinstance(r, dict)}
            record = records.get(target)
            if not record:
                errors.append(f"{event_id}: target {target} absent from {receipt_rel}")
                continue
            if record.get("sha256") != sha:
                errors.append(f"{event_id}: source SHA does not match receipt")
            if record.get("status") != "acquired-original-not-listening-approved":
                errors.append(f"{event_id}: receipt target is not in acquired-unapproved state")

    summary = data.get("summary")
    expected_summary = {
        "trackedRuntimeEvents": len(EXPECTED_EVENTS),
        "acquiredSourceCandidatePendingHuman": acquired,
        "sourceAcquisitionPending": pending,
        "sourceApproved": 0,
        "runtimeProducedFromThisCoverage": 0,
    }
    if summary != expected_summary:
        errors.append(f"summary mismatch: got={summary} expected={expected_summary}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"Field backlog coverage FAILED: {len(errors)} error(s).")
        return 1

    print(f"Field backlog coverage OK: {acquired} acquired candidate(s), {pending} acquisition-pending, 0 approved/produced.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
