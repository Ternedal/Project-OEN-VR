from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
QUEUE = Path("content/audio/radio_vo_recording_queue.source.json")
LOCALIZATION = Path("content/localization/da.source.json")
CONTRACT = Path("content/audio/radio_vo_human_review_contract.source.json")
DEFAULT_SESSION = Path("PrivateContent/RadioVOSession")


class ReviewError(RuntimeError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ReviewError(f"Cannot parse {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ReviewError(f"{path}: root must be an object")
    return value


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def expected_cues(queue: dict[str, Any]) -> list[dict[str, Any]]:
    cues = queue.get("cues")
    if queue.get("takesPerCue") != 3 or not isinstance(cues, list) or len(cues) != 9:
        raise ReviewError("radio VO queue must contain 9 cues x 3 takes")
    return cues


def load_context(session_root: Path, repo_root: Path = ROOT) -> dict[str, Any]:
    session_root = session_root.resolve()
    queue_path = repo_root / QUEUE
    localization_path = repo_root / LOCALIZATION
    contract_path = repo_root / CONTRACT
    session_path = session_root / "recording_session.json"
    receipt_path = session_root / "radio_vo_intake_receipt.json"
    provenance_path = session_root / "performer_provenance.json"
    for path in (queue_path, localization_path, contract_path, session_path, receipt_path, provenance_path):
        if not path.is_file():
            raise ReviewError(f"missing required file: {path}")

    queue = load_json(queue_path)
    localization = load_json(localization_path)
    contract = load_json(contract_path)
    session = load_json(session_path)
    receipt = load_json(receipt_path)
    _ = load_json(provenance_path)

    cues = expected_cues(queue)
    strings = localization.get("strings")
    if localization.get("locale") != "da-DK" or not isinstance(strings, dict):
        raise ReviewError("canonical da-DK localization is missing or invalid")
    if receipt.get("status") != contract.get("requiredTechnicalReceiptStatus"):
        raise ReviewError(f"technical receipt status is not reviewable: {receipt.get('status')!r}")
    if receipt.get("expectedTakeCount") != 27 or receipt.get("validatedTakeCount") != 27:
        raise ReviewError("technical receipt must be a clean 27/27 intake")

    receipt_records = receipt.get("records")
    if not isinstance(receipt_records, list) or len(receipt_records) != 27:
        raise ReviewError("technical receipt must contain exactly 27 records")
    by_filename: dict[str, dict[str, Any]] = {}
    for record in receipt_records:
        if not isinstance(record, dict):
            raise ReviewError("technical receipt contains invalid record")
        filename = record.get("filename")
        sha = record.get("sha256")
        if not isinstance(filename, str) or not isinstance(sha, str) or len(sha) != 64:
            raise ReviewError("technical receipt record has invalid filename/hash")
        if filename in by_filename:
            raise ReviewError(f"duplicate technical receipt filename: {filename}")
        take_path = session_root / "takes" / filename
        if not take_path.is_file():
            raise ReviewError(f"review source take is missing: {filename}")
        actual = sha256_file(take_path)
        if actual != sha:
            raise ReviewError(f"stale take bytes for {filename}: expected={sha} actual={actual}")
        by_filename[filename] = record

    cue_sheet = session.get("cueSheet")
    expected_takes = session.get("expectedTakes")
    if session.get("version", 0) < 2 or not isinstance(cue_sheet, list) or len(cue_sheet) != 9:
        raise ReviewError("recording session must be V2+ with 9-cue cueSheet")
    if not isinstance(expected_takes, list) or len(expected_takes) != 27:
        raise ReviewError("recording session must contain 27 expectedTakes")
    sheet_by_id = {x.get("cueId"): x for x in cue_sheet if isinstance(x, dict)}
    if len(sheet_by_id) != 9:
        raise ReviewError("recording cueSheet has duplicate/invalid cue IDs")

    review_cues = []
    expected_names: set[str] = set()
    for cue in cues:
        cue_id = cue.get("id")
        key = cue.get("localizationKey")
        if not isinstance(cue_id, str) or not isinstance(key, str):
            raise ReviewError("queue contains invalid cue identity")
        current_text = strings.get(key)
        sheet = sheet_by_id.get(cue_id)
        if not isinstance(current_text, str) or not current_text.strip():
            raise ReviewError(f"missing current canonical text for {cue_id}: {key}")
        if not isinstance(sheet, dict) or sheet.get("spokenText") != current_text:
            raise ReviewError(f"canonical text drift for {cue_id}; reconcile recording before review")
        candidates = []
        for take in range(1, 4):
            filename = f"{cue_id}__T{take:02d}.wav"
            expected_names.add(filename)
            record = by_filename.get(filename)
            if not record or record.get("cueId") != cue_id or record.get("take") != take:
                raise ReviewError(f"technical receipt identity mismatch for {filename}")
            candidates.append({
                "take": take,
                "filename": filename,
                "sha256": record["sha256"],
                "durationSec": record.get("durationSec"),
                "peakDbfs": record.get("peakDbfs"),
            })
        review_cues.append({
            "cueId": cue_id,
            "phase": cue.get("phase"),
            "localizationKey": key,
            "spokenText": current_text,
            "delivery": cue.get("delivery"),
            "criticalSemantic": cue.get("criticalSemantic"),
            "candidates": candidates,
        })
    if set(by_filename) != expected_names:
        raise ReviewError("technical receipt take set does not match current 9x3 queue")

    bindings = {
        "intakeReceiptSha256": sha256_file(receipt_path),
        "recordingSessionSha256": sha256_file(session_path),
        "performerProvenanceSha256": sha256_file(provenance_path),
        "queueSha256": sha256_file(queue_path),
        "localizationSha256": sha256_file(localization_path),
        "takes": {name: by_filename[name]["sha256"] for name in sorted(by_filename)},
    }
    return {"contract": contract, "bindings": bindings, "cues": review_cues}
