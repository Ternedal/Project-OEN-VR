#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "content/audio/foley_human_review_contract.source.json"
MATERIALIZE = ROOT / "content/audio/foley_source_materialization_contract.source.json"
SESSION = ROOT / "content/audio/foley_session_contract.source.json"
LISTENING = ROOT / "content/audio/listening_qa.source.json"
QUEUE = ROOT / "content/audio/foley_recording_queue.source.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []
    try:
        review = load(REVIEW); materialize = load(MATERIALIZE); session = load(SESSION); listening = load(LISTENING); queue = load(QUEUE)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: cannot parse Foley review contracts: {exc}")
        return 1

    if review.get("version") != 1 or review.get("status") != "human-review-tooling-ready-not-reviewed":
        errors.append("Foley human review version/status drift")
    if review.get("requiredTechnicalReceiptStatus") != session.get("receipt", {}).get("statusOnPass"):
        errors.append("Foley review technical input status must match session intake pass status")
    if (review.get("expectedCueCount"), review.get("expectedTakeCount")) != (13, 53):
        errors.append("Foley human review must remain 13 cues / 53 takes")
    if review.get("takeDecisionValues") != ["keep", "needs-rerecord", "needs-more-listening"]:
        errors.append("Foley take decision values drift")
    if review.get("cueDecisionValues") != ["accept-current-set", "needs-rerecord", "needs-more-listening"]:
        errors.append("Foley cue decision values drift")

    canonical = [x.get("id") for x in listening.get("requiredListeningChecks", []) if isinstance(x, dict)]
    typed = review.get("typedChecks", {})
    if len(canonical) != 8 or set(typed) != set(canonical) | {"UNDER_WEATHER_READABILITY"}:
        errors.append("Foley review must contain the exact eight canonical listening checks plus UNDER_WEATHER_READABILITY")
    for check_id in ("MATERIAL_MATCH", "VARIATION_VALUE"):
        spec = typed.get(check_id, {})
        if spec.get("type") != "rating" or spec.get("min") != 1 or spec.get("max") != 5 or spec.get("approvalMin") != 3:
            errors.append(f"{check_id}: Foley approval rating must remain 1-5 with >=3 threshold")
    weather = typed.get("UNDER_WEATHER_READABILITY", {})
    if weather.get("type") != "result" or weather.get("approval") != ["pass"]:
        errors.append("UNDER_WEATHER_READABILITY must remain explicit pass-only approval")

    eligibility = set(review.get("sourceApprovedEligibilityRequires", []))
    required_phrases = {
        "reviewerAlias is non-empty",
        "reviewedAt is non-empty",
        "commercialReuseAllowed is true",
        "all 53 take decisions are keep",
        "all 13 cue decisions are accept-current-set",
        "MATERIAL_MATCH >= 3 per cue",
        "VARIATION_VALUE >= 3 per cue",
        "UNDER_WEATHER_READABILITY is pass per cue",
    }
    if not required_phrases <= eligibility:
        errors.append(f"Foley source approval eligibility missing guards: {sorted(required_phrases - eligibility)}")

    if materialize.get("version") != 1 or materialize.get("status") != "source-approved-materialization-tooling-ready-no-foley-source-approved":
        errors.append("Foley materialization version/status drift")
    if materialize.get("input", {}).get("status") != review.get("normalizedStatus"):
        errors.append("Foley materializer input status must equal human-review normalized status")
    mat = materialize.get("materialization", {})
    if (mat.get("expectedCueCount"), mat.get("expectedTakeCount")) != (13, 53):
        errors.append("Foley materialization must remain 13 cues / 53 sources")
    for key in ("copyOnly", "preserveSourceBytes", "sourceAndOutputShaMustMatch", "overwriteRequiresExplicitReplace"):
        if mat.get(key) is not True:
            errors.append(f"Foley materialization guard must remain true: {key}")

    queue_sessions = queue.get("sessions")
    cue_count = take_count = 0
    if isinstance(queue_sessions, list):
        for session_entry in queue_sessions:
            if not isinstance(session_entry, dict) or not isinstance(session_entry.get("cues"), list):
                continue
            cue_count += len(session_entry["cues"])
            take_count += sum(c.get("variants", 0) for c in session_entry["cues"] if isinstance(c, dict) and isinstance(c.get("variants"), int))
    if (cue_count, take_count) != (13, 53):
        errors.append(f"current Foley queue drift: {cue_count} cues / {take_count} takes")

    if "SFX_FIRESTEEL_STRIKE_001" in json.dumps(queue):
        errors.append("owner-gated firesteel cue must not enter the current Foley recording queue")
    if "issue #8" not in " ".join(review.get("rules", [])).lower():
        errors.append("Foley human review must preserve fire-start issue #8 boundary")

    if errors:
        for error in errors:
            print("ERROR:", error)
        print(f"Foley human review contract FAILED: {len(errors)} error(s).")
        return 1
    print("Foley human review contract OK: 13 cues / 53 takes, 8 canonical checks + weather readability, >=3 material/variation thresholds, explicit copy-only promotion, fire-start excluded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
