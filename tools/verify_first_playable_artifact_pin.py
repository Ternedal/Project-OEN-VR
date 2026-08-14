#!/usr/bin/env python3
"""Verify the freshly staged Unity first-playable payload against its committed QA pin."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PIN = ROOT / "content/audio/first_playable_artifact_pin.json"
DEFAULT_ZIP = ROOT / "build/oen-unity-first-playable-audio-v1.zip"
MANIFEST_NAME = "FIRST_PLAYABLE_MANIFEST.csv"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pin", type=Path, default=DEFAULT_PIN)
    parser.add_argument("--zip", dest="zip_path", type=Path, default=DEFAULT_ZIP)
    args = parser.parse_args()

    pin = json.loads(args.pin.read_text(encoding="utf-8"))
    if pin.get("schema_version") != 1:
        raise SystemExit("first-playable artifact pin schema drift")
    if pin.get("artifact_name") != "oen-unity-first-playable-audio-v1":
        raise SystemExit("first-playable artifact pin name drift")
    if not args.zip_path.is_file():
        raise SystemExit(f"missing staged Unity first-playable ZIP: {args.zip_path}")

    zip_bytes = args.zip_path.read_bytes()
    actual_zip_sha = sha256_bytes(zip_bytes)
    expected_zip_sha = pin.get("inner_zip_sha256")
    if actual_zip_sha != expected_zip_sha:
        raise SystemExit(
            "first-playable artifact pin mismatch: deterministic ZIP SHA-256 drift; "
            f"expected {expected_zip_sha}, got {actual_zip_sha}. Re-verify the new payload physically before updating the pin."
        )

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        names = archive.namelist()
        if MANIFEST_NAME not in names:
            raise SystemExit(f"staged Unity ZIP missing {MANIFEST_NAME}")
        manifest_bytes = archive.read(MANIFEST_NAME)

    actual_manifest_sha = sha256_bytes(manifest_bytes)
    expected_manifest_sha = pin.get("manifest_sha256")
    if actual_manifest_sha != expected_manifest_sha:
        raise SystemExit(
            "first-playable artifact pin mismatch: manifest SHA-256 drift; "
            f"expected {expected_manifest_sha}, got {actual_manifest_sha}"
        )

    rows = list(csv.DictReader(io.StringIO(manifest_bytes.decode("utf-8"))))
    clip_count = len(rows)
    event_count = len({row.get("event_id", "").strip() for row in rows if row.get("event_id", "").strip()})
    if clip_count != pin.get("clip_count") or event_count != pin.get("event_count"):
        raise SystemExit(
            "first-playable artifact pin mismatch: coverage drift; "
            f"expected {pin.get('clip_count')}/{pin.get('event_count')}, got {clip_count}/{event_count}"
        )

    print(
        "First-playable artifact pin OK: freshly staged deterministic ZIP + manifest match pinned "
        f"SHA-256 and {clip_count}/{event_count} coverage."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
