#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "content/audio/foley_recording_queue.source.json"
RECONCILIATION = ROOT / "content/audio/foley_session_reconciliation.source.json"
CONTRACT = ROOT / "content/audio/foley_session_contract.source.json"
DEFAULT_OUT = ROOT / "PrivateContent/FoleySession"


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"{path}: root must be an object")
    return value


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def physical_session_index(reconciliation: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    sessions = reconciliation.get("sessions")
    if reconciliation.get("status") != "recording-session-reconciliation-ready-not-recorded" or not isinstance(sessions, list):
        raise RuntimeError("Foley reconciliation is missing or not in ready-not-recorded state")
    by_cue: dict[str, dict[str, Any]] = {}
    valid_sessions: list[dict[str, Any]] = []
    for session in sessions:
        if not isinstance(session, dict) or not isinstance(session.get("id"), str):
            raise RuntimeError("Foley reconciliation contains an invalid physical session")
        intents = session.get("mainCueIntents")
        if not isinstance(intents, list) or not intents:
            raise RuntimeError(f"{session['id']}: mainCueIntents missing")
        valid_sessions.append(session)
        for cue_id in intents:
            if not isinstance(cue_id, str) or not cue_id:
                raise RuntimeError(f"{session['id']}: invalid cue intent")
            if cue_id in by_cue:
                raise RuntimeError(f"cue is mapped to multiple physical sessions: {cue_id}")
            by_cue[cue_id] = session
    return by_cue, valid_sessions


def build_session(queue: dict[str, Any], reconciliation: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    queue_sessions = queue.get("sessions")
    if queue.get("status") != "recording-queue-ready" or not isinstance(queue_sessions, list):
        raise RuntimeError("Foley recording queue is missing or not ready")
    by_cue, physical_sessions = physical_session_index(reconciliation)
    expected_takes: list[dict[str, Any]] = []
    cue_sheet: list[dict[str, Any]] = []
    cue_ids: set[str] = set()

    for queue_session in queue_sessions:
        if not isinstance(queue_session, dict) or not isinstance(queue_session.get("id"), str):
            raise RuntimeError("Foley queue contains an invalid session")
        cues = queue_session.get("cues")
        if not isinstance(cues, list) or not cues:
            raise RuntimeError(f"{queue_session['id']}: cue list missing")
        for cue in cues:
            if not isinstance(cue, dict):
                raise RuntimeError(f"{queue_session['id']}: invalid cue")
            cue_id = cue.get("id")
            variants = cue.get("variants")
            target = cue.get("targetLengthMs")
            pattern = cue.get("filenamePattern")
            if not isinstance(cue_id, str) or cue_id in cue_ids:
                raise RuntimeError(f"invalid or duplicate cue id: {cue_id!r}")
            cue_ids.add(cue_id)
            if not isinstance(variants, int) or variants < 1:
                raise RuntimeError(f"{cue_id}: invalid variants")
            if not isinstance(target, list) or len(target) != 2 or not all(isinstance(v, int) and v > 0 for v in target):
                raise RuntimeError(f"{cue_id}: invalid targetLengthMs")
            if not isinstance(pattern, str) or "vNN" not in pattern:
                raise RuntimeError(f"{cue_id}: invalid filenamePattern")
            physical = by_cue.get(cue_id)
            if physical is None:
                raise RuntimeError(f"{cue_id}: no physical-session reconciliation mapping")
            filenames = []
            for variant in range(1, variants + 1):
                filename = pattern.replace("vNN", f"v{variant:02d}")
                filenames.append(filename)
                expected_takes.append({
                    "queueSessionId": queue_session["id"],
                    "physicalSessionId": physical["id"],
                    "priority": queue_session.get("priority"),
                    "cueId": cue_id,
                    "variant": variant,
                    "filename": filename,
                    "relativePath": f"takes/{queue_session['id']}/{filename}",
                    "targetLengthMs": target,
                    "captureIntent": cue.get("captureIntent"),
                })
            cue_sheet.append({
                "queueSessionId": queue_session["id"],
                "physicalSessionId": physical["id"],
                "priority": queue_session.get("priority"),
                "cueId": cue_id,
                "variantCount": variants,
                "targetLengthMs": target,
                "captureIntent": cue.get("captureIntent"),
                "filenames": filenames,
                "physicalSetup": physical.get("physicalSetup", []),
                "performances": physical.get("performances", []),
                "qa": physical.get("qa", []),
            })

    shape = contract.get("captureShape", {})
    expected_shape = (
        shape.get("expectedQueueSessionCount"),
        shape.get("expectedPhysicalSessionCount"),
        shape.get("expectedCueCount"),
        shape.get("expectedTakeCount"),
    )
    actual_shape = (len(queue_sessions), len(physical_sessions), len(cue_sheet), len(expected_takes))
    if actual_shape != expected_shape:
        raise RuntimeError(f"Foley capture shape drift: actual={actual_shape} contract={expected_shape}")

    return {
        "version": 1,
        "status": "prepared-not-recorded",
        "bindings": {
            "queueSha256": sha256_file(QUEUE),
            "reconciliationSha256": sha256_file(RECONCILIATION),
            "contractSha256": sha256_file(CONTRACT),
        },
        "expectedQueueSessionCount": len(queue_sessions),
        "expectedPhysicalSessionCount": len(physical_sessions),
        "expectedCueCount": len(cue_sheet),
        "expectedTakeCount": len(expected_takes),
        "expectedTakes": expected_takes,
        "cueSheet": cue_sheet,
        "physicalSessionIds": [session["id"] for session in physical_sessions],
        "rule": "Every slot requires a distinct raw physical performance. Preparation is not recording evidence.",
    }


def render_board(session: dict[str, Any], contract: dict[str, Any]) -> str:
    cards: list[str] = []
    for cue in session["cueSheet"]:
        filenames = "".join(f"<li><code>{html.escape(name)}</code></li>" for name in cue["filenames"])
        setup = "".join(f"<li>{html.escape(str(item))}</li>" for item in cue.get("physicalSetup", []))
        qa = "".join(f"<li>{html.escape(str(item))}</li>" for item in cue.get("qa", []))
        lo, hi = cue["targetLengthMs"]
        checks = " &nbsp; ".join(f"☐ v{i:02d}" for i in range(1, cue["variantCount"] + 1))
        cards.append(f"""
<article>
<h2>{html.escape(cue['cueId'])}</h2>
<p><b>Intent:</b> {html.escape(str(cue.get('captureIntent') or ''))}</p>
<p><b>Physical session:</b> <code>{html.escape(cue['physicalSessionId'])}</code> · <b>Target:</b> {lo}–{hi} ms</p>
<details><summary>Setup / QA</summary><h3>Setup</h3><ul>{setup}</ul><h3>QA</h3><ul>{qa}</ul></details>
<ul>{filenames}</ul><p class="check">{checks}</p>
</article>""")
    tech = contract["technicalAcceptance"]
    return """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PROJECT ØEN — Foley recording board</title><style>body{font-family:system-ui,sans-serif;max-width:1050px;margin:auto;padding:24px;background:#f4f2eb;color:#202522}header,article{background:white;border:1px solid #d8d8d0;border-radius:12px;padding:18px;margin:14px 0}.check{font-size:1.05rem}code{font-size:.9rem}details{margin:10px 0}@media print{body{background:white;padding:0}header,article{break-inside:avoid;box-shadow:none}}</style><header><h1>PROJECT ØEN — Foley recording board</h1><p>13 cues · 53 planned raw physical performances. One checkbox is one distinct performance — not a gain/pitch copy.</p>""" + f"<p><b>Technical source:</b> {tech['sampleRateHz']/1000:g} kHz · {tech['bitDepth']}-bit integer PCM · mono · WAV · no full-scale samples.</p><p>Preserve raw takes. Material-fit, variation value and under-weather readability are human listening gates after technical intake.</p></header>" + "".join(cards) + "</html>"


def default_provenance(physical_ids: list[str]) -> dict[str, Any]:
    return {
        "recordistAlias": "",
        "recordedAtUtc": "",
        "recordingChain": "",
        "rightsStatement": "",
        "commercialReuseAllowed": None,
        "physicalSessions": {
            session_id: {
                "sourceMaterials": [],
                "locationClass": "",
                "backgroundSpeechNone": None,
                "backgroundMusicNone": None,
                "notes": "",
            }
            for session_id in physical_ids
        },
    }


def prepare(output: Path) -> dict[str, Any]:
    queue = load_object(QUEUE)
    reconciliation = load_object(RECONCILIATION)
    contract = load_object(CONTRACT)
    session = build_session(queue, reconciliation, contract)
    output = output.resolve()
    for queue_session_id in sorted({take["queueSessionId"] for take in session["expectedTakes"]}):
        (output / "takes" / queue_session_id).mkdir(parents=True, exist_ok=True)
    (output / "recording_session.json").write_text(json.dumps(session, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (output / "recording_board.html").write_text(render_board(session, contract), encoding="utf-8")
    provenance_path = output / contract["provenance"]["filename"]
    if not provenance_path.exists():
        provenance_path.write_text(json.dumps(default_provenance(session["physicalSessionIds"]), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return session


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare the PROJECT OEN physical Foley recording session without claiming recordings exist.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    try:
        session = prepare(args.output)
    except (RuntimeError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"Prepared Foley session: {session['expectedCueCount']} cues / {session['expectedTakeCount']} raw take slots + recording_board.html under {args.output.resolve()}")
    print("No recording, material-fit or listening approval is claimed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
