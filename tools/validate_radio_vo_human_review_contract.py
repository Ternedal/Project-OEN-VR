#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "content/audio/radio_vo_human_review_contract.source.json"
SESSION_CONTRACT = ROOT / "content/audio/radio_vo_session_contract.source.json"
QUEUE = ROOT / "content/audio/radio_vo_recording_queue.source.json"
LOCALIZATION = ROOT / "content/localization/da.source.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    c = load(CONTRACT); s = load(SESSION_CONTRACT); q = load(QUEUE); loc = load(LOCALIZATION)
    errors = []
    if c.get("version") != 1 or c.get("status") != "human-review-tooling-ready-not-reviewed":
        errors.append("human review contract version/status drift")
    if c.get("requiredTechnicalReceiptStatus") != s.get("receipt", {}).get("statusOnPass"):
        errors.append("human review contract technical status does not match session intake pass status")
    if c.get("normalizedStatus") != "human-review-evidence-unapproved":
        errors.append("normalizer status must remain explicitly unapproved")
    if c.get("reviewExport") != {"version": 1, "status": "human-radio-vo-review-unvalidated"}:
        errors.append("review export version/status drift")
    if c.get("cueDecisionValues") != ["select", "needs-rerecord", "needs-more-listening"]:
        errors.append("cue decision values drift")
    if c.get("checkIds") != ["PRONUNCIATION", "DELIVERY", "SEMANTIC_PARITY", "NO_CRITICAL_ADLIB"]:
        errors.append("human check IDs drift")
    if c.get("checkResultValues") != ["pass", "fail", "needs-more-listening"]:
        errors.append("human check result values drift")
    if c.get("rightsDecisionValues") != ["accepted", "rejected", "needs-review"]:
        errors.append("rights decision values drift")
    cues = q.get("cues")
    strings = loc.get("strings")
    if q.get("takesPerCue") != 3 or not isinstance(cues, list) or len(cues) != 9:
        errors.append("recording queue must remain 9 cues x 3 takes")
        cues = []
    if loc.get("locale") != "da-DK" or not isinstance(strings, dict):
        errors.append("da-DK localization missing")
        strings = {}
    ids = set()
    for cue in cues:
        cue_id = cue.get("id") if isinstance(cue, dict) else None
        key = cue.get("localizationKey") if isinstance(cue, dict) else None
        if not isinstance(cue_id, str) or cue_id in ids:
            errors.append(f"invalid/duplicate cue ID: {cue_id!r}")
            continue
        ids.add(cue_id)
        if not isinstance(key, str) or not isinstance(strings.get(key), str) or not strings[key].strip():
            errors.append(f"{cue_id}: missing canonical Danish localization")
    gates = " | ".join(s.get("humanGates", []))
    for phrase in ("pronunciation", "delivery/tone", "semantic parity", "one take selected", "permission accepted"):
        if phrase.lower() not in gates.lower():
            errors.append(f"session contract no longer carries human gate: {phrase}")
    if errors:
        for error in errors:
            print("ERROR:", error)
        return 1
    print("Radio VO human review contract OK: 9 cues, 27 take candidates, negative-result-safe human evidence lane, normalized status remains unapproved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
