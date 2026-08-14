#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "content/audio/radio_vo_recording_queue.source.json"
CONTRACT = ROOT / "content/audio/radio_vo_session_contract.source.json"
LOCALIZATION = ROOT / "content/localization/da.source.json"
DEFAULT_OUT = ROOT / "PrivateContent/RadioVOSession"


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"{path}: root must be an object")
    return value


def build_session(queue: dict[str, Any], localization: dict[str, Any]) -> dict[str, Any]:
    cues = queue.get("cues")
    if queue.get("takesPerCue") != 3 or not isinstance(cues, list) or len(cues) != 9:
        raise RuntimeError("queue must be 9 cues x 3 takes")
    if localization.get("locale") != "da-DK" or not isinstance(localization.get("strings"), dict):
        raise RuntimeError("canonical da-DK localization is missing or invalid")
    strings = localization["strings"]
    expected = []
    cue_sheet = []
    for cue in cues:
        if not isinstance(cue, dict):
            raise RuntimeError("queue contains invalid cue")
        key = cue.get("localizationKey")
        if not isinstance(key, str) or not isinstance(strings.get(key), str) or not strings[key].strip():
            raise RuntimeError(f"missing canonical Danish radio text for {cue.get('id')}: {key}")
        spoken_text = strings[key]
        cue_sheet.append({
            "cueId": cue["id"],
            "phase": cue["phase"],
            "localizationKey": key,
            "spokenText": spoken_text,
            "delivery": cue["delivery"],
            "criticalSemantic": cue["criticalSemantic"],
            "targetDurationSec": cue["targetDurationSec"],
            "takeFilenames": [f"{cue['id']}__T{take:02d}.wav" for take in range(1, 4)],
        })
        for take in range(1, 4):
            expected.append({
                "cueId": cue["id"],
                "take": take,
                "filename": f"{cue['id']}__T{take:02d}.wav",
                "phase": cue["phase"],
                "localizationKey": key,
                "spokenText": spoken_text,
                "delivery": cue["delivery"],
                "criticalSemantic": cue["criticalSemantic"],
                "targetDurationSec": cue["targetDurationSec"],
            })
    return {
        "version": 2,
        "status": "prepared-not-recorded",
        "locale": "da-DK",
        "expectedTakeCount": len(expected),
        "expectedTakes": expected,
        "cueSheet": cue_sheet,
        "rule": "Record the canonical spokenText exactly. Untouched dry WAV takes only; no radio processing.",
    }


def render_board(session: dict[str, Any]) -> str:
    cards = []
    for cue in session["cueSheet"]:
        takes = "".join(f"<li><code>{html.escape(name)}</code></li>" for name in cue["takeFilenames"])
        lo, hi = cue["targetDurationSec"]
        cards.append(f"""
<article><h2>{html.escape(cue['cueId'])}</h2>
<p class="line">{html.escape(cue['spokenText'])}</p>
<dl><dt>Delivery</dt><dd>{html.escape(cue['delivery'])}</dd>
<dt>Critical semantic</dt><dd>{html.escape(cue['criticalSemantic'])}</dd>
<dt>Target</dt><dd>{lo}–{hi} s</dd></dl>
<ul>{takes}</ul><p class="check">☐ T01 &nbsp; ☐ T02 &nbsp; ☐ T03</p></article>""")
    return """<!doctype html><html lang="da"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PROJECT ØEN — Radio VO recording board</title><style>body{font-family:system-ui,sans-serif;max-width:980px;margin:auto;padding:24px;background:#f4f2eb;color:#202522}header,article{background:white;border:1px solid #d8d8d0;border-radius:12px;padding:18px;margin:14px 0}.line{font-size:1.45rem;font-weight:700}.check{font-size:1.1rem}dt{font-weight:700}dd{margin:0 0 8px}code{font-size:.9rem}@media print{body{background:white;padding:0}header,article{break-inside:avoid;box-shadow:none}}</style><header><h1>PROJECT ØEN — Radio VO recording board</h1><p>9 canonical danske cues × 3 dry takes. Læs replikken ordret; delivery-noten styrer tone, ikke indhold. Ingen radio-EQ/static i source takes.</p><p><b>Teknisk:</b> 48 kHz · 24-bit integer PCM · mono · dry/unprocessed.</p></header>""" + "".join(cards) + "</html>"


def prepare(output: Path, queue_path: Path = QUEUE, contract_path: Path = CONTRACT, localization_path: Path = LOCALIZATION) -> dict[str, Any]:
    queue = load_object(queue_path)
    contract = load_object(contract_path)
    localization = load_object(localization_path)
    session = build_session(queue, localization)
    output = output.resolve()
    (output / "takes").mkdir(parents=True, exist_ok=True)
    (output / "recording_session.json").write_text(json.dumps(session, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (output / "recording_board.html").write_text(render_board(session), encoding="utf-8")
    provenance = output / contract["provenance"]["filename"]
    if not provenance.exists():
        provenance.write_text(json.dumps({
            "sourceType": "",
            "sourceNameOrAlias": "",
            "permissionOrLicense": "",
            "recordedOrGeneratedAt": "",
            "commercialReuseAllowed": None,
            "identifiablePublicPersonImitation": False,
            "notes": "",
        }, indent=2) + "\n", encoding="utf-8")
    return session


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    try:
        session = prepare(args.output)
    except (RuntimeError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"Prepared {session['expectedTakeCount']} take slots + recording_board.html under {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
