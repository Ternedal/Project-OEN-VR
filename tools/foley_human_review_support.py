from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from validate_foley_session import fresh_expected, validate_session

ROOT = Path(__file__).resolve().parents[1]
REVIEW_CONTRACT = ROOT / "content/audio/foley_human_review_contract.source.json"
MATERIALIZE_CONTRACT = ROOT / "content/audio/foley_source_materialization_contract.source.json"
LISTENING_QA = ROOT / "content/audio/listening_qa.source.json"
SESSION_CONTRACT = ROOT / "content/audio/foley_session_contract.source.json"


class FoleyReviewError(RuntimeError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise FoleyReviewError(f"Cannot parse {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise FoleyReviewError(f"{path}: root must be an object")
    return value


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _record_identity(record: dict[str, Any]) -> tuple[Any, ...]:
    return (
        record.get("queueSessionId"), record.get("physicalSessionId"), record.get("cueId"),
        record.get("variant"), record.get("filename"), record.get("relativePath"), record.get("sha256"),
        record.get("bytes"), record.get("sampleRateHz"), record.get("bitDepth"), record.get("channels"),
        record.get("fullScaleSampleCount"),
    )


def load_context(session_root: Path) -> dict[str, Any]:
    session_root = session_root.resolve()
    review_contract = load_json(REVIEW_CONTRACT)
    materialize_contract = load_json(MATERIALIZE_CONTRACT)
    listening = load_json(LISTENING_QA)
    session_contract = load_json(SESSION_CONTRACT)
    receipt_path = session_root / session_contract["receipt"]["filename"]
    session_path = session_root / "recording_session.json"
    provenance_path = session_root / session_contract["provenance"]["filename"]
    for path in (receipt_path, session_path, provenance_path):
        if not path.is_file():
            raise FoleyReviewError(f"missing required session evidence: {path.name}")

    stored_receipt = load_json(receipt_path)
    if stored_receipt.get("status") != review_contract.get("requiredTechnicalReceiptStatus"):
        raise FoleyReviewError("technical receipt has not passed the required intake state")
    fresh_receipt, intake_errors, _ = validate_session(session_root)
    if intake_errors:
        raise FoleyReviewError("current raw session no longer passes technical intake: " + " | ".join(intake_errors[:8]))
    for key in ("status", "bindings", "recordingSessionSha256", "provenanceSha256", "expectedCueCount", "expectedTakeCount", "validatedTakeCount"):
        if stored_receipt.get(key) != fresh_receipt.get(key):
            raise FoleyReviewError(f"technical receipt is stale or modified: {key}")
    stored_records = stored_receipt.get("records")
    fresh_records = fresh_receipt.get("records")
    expected_take_count = review_contract.get("expectedTakeCount")
    if not isinstance(expected_take_count, int) or expected_take_count < 1:
        raise FoleyReviewError("human review contract expectedTakeCount is invalid")
    if not isinstance(stored_records, list) or not isinstance(fresh_records, list) or len(stored_records) != expected_take_count or len(fresh_records) != expected_take_count:
        raise FoleyReviewError(f"technical receipt must contain exactly {expected_take_count} records")
    if [_record_identity(x) for x in stored_records] != [_record_identity(x) for x in fresh_records]:
        raise FoleyReviewError("technical receipt record identities no longer match current raw takes")

    expected, _ = fresh_expected()
    if expected.get("expectedTakeCount") != expected_take_count or expected.get("expectedCueCount") != review_contract.get("expectedCueCount"):
        raise FoleyReviewError("Foley session/review contract shape drift")
    expected_by_path = {x["relativePath"]: x for x in expected["expectedTakes"]}
    receipt_by_path: dict[str, dict[str, Any]] = {}
    for record in stored_records:
        rel = record.get("relativePath")
        if not isinstance(rel, str) or rel in receipt_by_path or rel not in expected_by_path:
            raise FoleyReviewError(f"invalid or duplicate technical receipt path: {rel!r}")
        take_path = session_root / rel
        if not take_path.is_file() or sha256_file(take_path) != record.get("sha256"):
            raise FoleyReviewError(f"raw take bytes no longer match technical receipt: {rel}")
        expected_take = expected_by_path[rel]
        for key in ("queueSessionId", "physicalSessionId", "cueId", "variant", "filename"):
            if record.get(key) != expected_take.get(key):
                raise FoleyReviewError(f"technical receipt mapping drift for {rel}: {key}")
        receipt_by_path[rel] = record

    provenance = load_json(provenance_path)
    if sha256_file(provenance_path) != stored_receipt.get("provenanceSha256"):
        raise FoleyReviewError("Foley provenance changed after technical intake")
    if sha256_file(session_path) != stored_receipt.get("recordingSessionSha256"):
        raise FoleyReviewError("recording_session.json changed after technical intake")

    canonical_checks = [x.get("id") for x in listening.get("requiredListeningChecks", []) if isinstance(x, dict)]
    typed = review_contract.get("typedChecks")
    if not isinstance(typed, dict) or set(canonical_checks) | {"UNDER_WEATHER_READABILITY"} != set(typed):
        raise FoleyReviewError("Foley typed checks do not match canonical listening QA + weather readability")

    cue_records: dict[str, list[dict[str, Any]]] = {}
    for record in stored_records:
        cue_records.setdefault(record["cueId"], []).append(record)
    if len(cue_records) != review_contract.get("expectedCueCount"):
        raise FoleyReviewError("technical receipt cue count drift")
    for records in cue_records.values():
        records.sort(key=lambda x: x["variant"])

    return {
        "sessionRoot": session_root,
        "reviewContract": review_contract,
        "materializeContract": materialize_contract,
        "listeningQa": listening,
        "sessionContract": session_contract,
        "technicalReceipt": stored_receipt,
        "technicalReceiptPath": receipt_path,
        "technicalReceiptSha256": sha256_file(receipt_path),
        "provenance": provenance,
        "provenancePath": provenance_path,
        "provenanceSha256": sha256_file(provenance_path),
        "recordingSessionPath": session_path,
        "takeRecords": receipt_by_path,
        "cueRecords": dict(sorted(cue_records.items())),
        "canonicalCheckIds": canonical_checks,
    }


def expected_bindings(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "technicalReceiptSha256": context["technicalReceiptSha256"],
        "provenanceSha256": context["provenanceSha256"],
        "takes": {rel: record["sha256"] for rel, record in sorted(context["takeRecords"].items())},
    }


def check_valid(spec: dict[str, Any], value: Any) -> bool:
    if spec.get("type") == "rating":
        return isinstance(value, int) and not isinstance(value, bool) and spec.get("min") <= value <= spec.get("max")
    return isinstance(value, str) and value in spec.get("values", []) and bool(value)


def check_approves(spec: dict[str, Any], value: Any) -> bool:
    if not check_valid(spec, value):
        return False
    if spec.get("type") == "rating":
        return value >= spec.get("approvalMin", spec.get("min"))
    return value in spec.get("approval", [])


def evaluate_normalized(normalized: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    contract = context["reviewContract"]
    reviewer_ok = isinstance(normalized.get("reviewerAlias"), str) and bool(normalized["reviewerAlias"].strip())
    time_ok = isinstance(normalized.get("reviewedAt"), str) and bool(normalized["reviewedAt"].strip())
    rights_ok = context["provenance"].get("commercialReuseAllowed") is True
    records = normalized.get("cueReviews")
    if not isinstance(records, list):
        return {"reviewComplete": False, "allCuesEligible": False, "readyForSourceMaterialization": False}
    cue_map = {x.get("cueId"): x for x in records if isinstance(x, dict) and isinstance(x.get("cueId"), str)}
    complete = reviewer_ok and time_ok and len(cue_map) == contract["expectedCueCount"]
    all_eligible = complete and rights_ok
    for cue_id, take_records in context["cueRecords"].items():
        cue = cue_map.get(cue_id)
        if not isinstance(cue, dict):
            complete = False; all_eligible = False; continue
        takes = cue.get("takes")
        expected_paths = [x["relativePath"] for x in take_records]
        if not isinstance(takes, list) or [x.get("relativePath") for x in takes if isinstance(x, dict)] != expected_paths:
            complete = False; all_eligible = False; continue
        if any(x.get("decision") not in contract["takeDecisionValues"] for x in takes if isinstance(x, dict)):
            complete = False; all_eligible = False
        if any(x.get("decision") != "keep" for x in takes if isinstance(x, dict)):
            all_eligible = False
        decision = cue.get("decision")
        if decision not in contract["cueDecisionValues"]:
            complete = False; all_eligible = False
        if decision != "accept-current-set":
            all_eligible = False
        checks = cue.get("checks")
        if not isinstance(checks, dict) or set(checks) != set(contract["typedChecks"]):
            complete = False; all_eligible = False; continue
        for check_id, spec in contract["typedChecks"].items():
            entry = checks.get(check_id)
            value = entry.get("result") if isinstance(entry, dict) else None
            note = entry.get("note") if isinstance(entry, dict) else None
            if not check_valid(spec, value) or not isinstance(note, str):
                complete = False; all_eligible = False
            elif not check_approves(spec, value):
                all_eligible = False
    return {
        "reviewComplete": complete,
        "reviewerIdentityPresent": reviewer_ok and time_ok,
        "commercialReuseAllowed": rights_ok,
        "allCuesEligible": all_eligible,
        "readyForSourceMaterialization": complete and all_eligible,
    }
