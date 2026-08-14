#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import shutil
import struct
import tempfile
import wave
from pathlib import Path

from prepare_foley_session import CONTRACT, prepare
from validate_foley_session import validate_session


def sample24(value: int) -> bytes:
    if value < 0:
        value += 1 << 24
    return bytes((value & 0xFF, (value >> 8) & 0xFF, (value >> 16) & 0xFF))


def write_wav(path: Path, duration_ms: float, seed: int, *, bit_depth: int = 24, full_scale: bool = False) -> None:
    rate = 48000
    frames = max(1, int(rate * duration_ms / 1000))
    path.parent.mkdir(parents=True, exist_ok=True)
    width = bit_depth // 8
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(width)
        handle.setframerate(rate)
        if bit_depth == 24:
            raw = bytearray()
            frequency = 137 + seed * 11
            for index in range(frames):
                value = int(math.sin(2 * math.pi * frequency * index / rate) * 900000)
                if full_scale and index == frames // 2:
                    value = 8388607
                raw.extend(sample24(value))
            handle.writeframes(bytes(raw))
        elif bit_depth == 16:
            raw16 = bytearray()
            frequency = 137 + seed * 11
            for index in range(frames):
                value = int(math.sin(2 * math.pi * frequency * index / rate) * 4000)
                raw16.extend(struct.pack("<h", value))
            handle.writeframes(bytes(raw16))
        else:
            raise AssertionError("unsupported test bit depth")


def fill_provenance(root: Path) -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    path = root / contract["provenance"]["filename"]
    data = json.loads(path.read_text(encoding="utf-8"))
    data.update({
        "recordistAlias": "fixture-recordist",
        "recordedAtUtc": "2026-08-14T12:00:00Z",
        "recordingChain": "fixture-recorder + fixture-microphone",
        "rightsStatement": "owned project fixture recording",
        "commercialReuseAllowed": True,
    })
    for session_id, entry in data["physicalSessions"].items():
        entry.update({
            "sourceMaterials": [f"fixture-material-{session_id.lower()}"],
            "locationClass": "test-fixture-room",
            "backgroundSpeechNone": True,
            "backgroundMusicNone": True,
            "notes": "synthetic test fixture only",
        })
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def populate(root: Path) -> dict:
    session = json.loads((root / "recording_session.json").read_text(encoding="utf-8"))
    for index, take in enumerate(session["expectedTakes"], start=1):
        lo, hi = take["targetLengthMs"]
        duration = (lo + hi) / 2
        write_wav(root / take["relativePath"], duration, index)
    fill_provenance(root)
    return session


def clone(source: Path, parent: Path, name: str) -> Path:
    target = parent / name
    shutil.copytree(source, target)
    return target


def assert_has(errors: list[str], needle: str) -> None:
    if not any(needle in error for error in errors):
        raise AssertionError(f"expected error containing {needle!r}; got {errors}")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="oen-foley-test-") as td:
        base = Path(td)
        clean = base / "clean"
        prepared = prepare(clean)
        if (prepared["expectedCueCount"], prepared["expectedTakeCount"]) != (13, 53):
            raise AssertionError("Foley preparation must remain 13 cues / 53 takes")
        if not (clean / "recording_board.html").is_file():
            raise AssertionError("recording board missing")
        provenance_path = clean / "foley_provenance.json"
        provenance_path.write_text('{"sentinel":"preserve-me"}\n', encoding="utf-8")
        prepare(clean)
        if json.loads(provenance_path.read_text()) != {"sentinel": "preserve-me"}:
            raise AssertionError("prepare must not overwrite existing provenance")
        provenance_path.unlink()
        prepare(clean)
        session = populate(clean)

        receipt, errors, warnings = validate_session(clean)
        if errors or warnings:
            raise AssertionError(f"clean fixture should pass without errors/warnings: errors={errors} warnings={warnings}")
        if receipt["status"] != "technical-intake-passed-not-listening-approved" or receipt["validatedTakeCount"] != 53:
            raise AssertionError("clean fixture did not produce expected technical-only pass")
        if len({record["sha256"] for record in receipt["records"]}) != 53:
            raise AssertionError("clean fixture hashes must all be distinct")

        missing = clone(clean, base, "missing")
        (missing / session["expectedTakes"][0]["relativePath"]).unlink()
        _, errors, _ = validate_session(missing)
        assert_has(errors, "missing take")

        wrong_depth = clone(clean, base, "wrong-depth")
        take = session["expectedTakes"][1]
        lo, hi = take["targetLengthMs"]
        write_wav(wrong_depth / take["relativePath"], (lo + hi) / 2, 700, bit_depth=16)
        _, errors, _ = validate_session(wrong_depth)
        assert_has(errors, "bit depth")

        clipped = clone(clean, base, "full-scale")
        take = session["expectedTakes"][2]
        lo, hi = take["targetLengthMs"]
        write_wav(clipped / take["relativePath"], (lo + hi) / 2, 701, full_scale=True)
        _, errors, _ = validate_session(clipped)
        assert_has(errors, "full-scale sample")

        duplicate = clone(clean, base, "duplicate")
        first = duplicate / session["expectedTakes"][3]["relativePath"]
        second = duplicate / session["expectedTakes"][4]["relativePath"]
        second.write_bytes(first.read_bytes())
        _, errors, _ = validate_session(duplicate)
        assert_has(errors, "duplicate raw take bytes")

        stale = clone(clean, base, "stale")
        stale_path = stale / "recording_session.json"
        stale_data = json.loads(stale_path.read_text(encoding="utf-8"))
        stale_data["expectedTakeCount"] = 52
        stale_path.write_text(json.dumps(stale_data, indent=2) + "\n", encoding="utf-8")
        _, errors, _ = validate_session(stale)
        assert_has(errors, "expectedTakeCount mismatch")

    print("Foley session tests OK: 13 cues / 53 unique raw take slots; clean pass plus missing/depth/full-scale/duplicate/stale guards verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
