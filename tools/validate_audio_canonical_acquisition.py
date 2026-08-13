#!/usr/bin/env python3
"""Fail closed if reacquired canonical audio originals drift from the pinned receipt."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "content" / "audio" / "acquisition_receipt.source.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True, help="Canonical acquisition output root")
    args = parser.parse_args()

    root = args.root if args.root.is_absolute() else ROOT / args.root
    originals = root / "originals"
    manifest = json.loads((root / "acquisition_manifest.json").read_text(encoding="utf-8"))
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    errors: list[str] = []

    expected = {record["target"]: record for record in receipt.get("records", [])}
    actual = {record["target"]: record for record in manifest.get("records", [])}
    if set(actual) != set(expected):
        errors.append(f"target set mismatch: actual={sorted(actual)} expected={sorted(expected)}")

    for target, pinned in expected.items():
        record = actual.get(target)
        if not record:
            continue
        filename = pinned.get("filename")
        path = originals / str(filename)
        if not path.is_file():
            errors.append(f"{target}: missing acquired file {filename}")
            continue
        size = path.stat().st_size
        digest = sha256_file(path)
        if size != pinned.get("bytes"):
            errors.append(f"{target}: byte size drift {size} != {pinned.get('bytes')}")
        if digest != pinned.get("sha256"):
            errors.append(f"{target}: SHA-256 drift {digest} != {pinned.get('sha256')}")
        if record.get("sha256") != digest:
            errors.append(f"{target}: manifest SHA-256 does not match downloaded bytes")
        if record.get("bytes") != size:
            errors.append(f"{target}: manifest byte count does not match downloaded bytes")
        if record.get("status") != "acquired-original-not-listening-approved":
            errors.append(f"{target}: manifest acquisition status changed unexpectedly")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"Canonical acquisition integrity FAILED: {len(errors)} error(s).")
        return 1

    print(f"Canonical acquisition integrity OK: {len(expected)} pinned originals.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
