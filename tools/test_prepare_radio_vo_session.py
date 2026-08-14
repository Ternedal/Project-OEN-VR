#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("prepare_radio_vo", ROOT / "tools/prepare_radio_vo_session.py")
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


def main() -> int:
    canonical = json.loads(module.LOCALIZATION.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "session"
        session = module.prepare(out)
        assert session["version"] == 2
        assert session["expectedTakeCount"] == 27
        assert len(session["cueSheet"]) == 9
        assert len(session["expectedTakes"]) == 27
        first = session["cueSheet"][0]
        assert first["spokenText"] == canonical["strings"][first["localizationKey"]]
        assert all(isinstance(x.get("spokenText"), str) and x["spokenText"] for x in session["expectedTakes"])
        board = (out / "recording_board.html").read_text(encoding="utf-8")
        for cue in session["cueSheet"]:
            assert cue["spokenText"] in board
            for filename in cue["takeFilenames"]:
                assert filename in board
        prov = out / "performer_provenance.json"
        custom = {"sentinel": "do-not-overwrite"}
        prov.write_text(json.dumps(custom), encoding="utf-8")
        module.prepare(out)
        assert json.loads(prov.read_text(encoding="utf-8")) == custom

    with tempfile.TemporaryDirectory() as td:
        bad = json.loads(module.LOCALIZATION.read_text(encoding="utf-8"))
        bad["strings"].pop("vo.radio.day3.02")
        bad_path = Path(td) / "bad-da.json"
        bad_path.write_text(json.dumps(bad, ensure_ascii=False), encoding="utf-8")
        try:
            module.prepare(Path(td) / "session", localization_path=bad_path)
        except RuntimeError as exc:
            assert "missing canonical Danish radio text" in str(exc)
        else:
            raise AssertionError("missing localization key must fail preparation")

    print("Radio VO preparation self-test OK: 27 spoken-text-bound takes + board + fail-closed localization + provenance preservation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
