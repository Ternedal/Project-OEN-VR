#!/usr/bin/env python3
"""Fail closed on pinned field audio while allowing explicit first-acquisition bootstrap."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "content" / "audio" / "acquisition_field_backlog_receipt.source.json"
CANDIDATES = ROOT / "content" / "audio" / "acquisition_candidates.field_backlog.source.json"
EXPECTED_STATUS = "acquired-original-not-listening-approved"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument(
        "--allow-unpinned-new",
        action="store_true",
        help="Allow newly declared candidate targets that do not have a receipt yet. Existing pinned targets still fail closed.",
    )
    args = parser.parse_args()

    root = args.root if args.root.is_absolute() else ROOT / args.root
    originals = root / "originals"
    manifest = json.loads((root / "acquisition_manifest.json").read_text(encoding="utf-8"))
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    candidates = json.loads(CANDIDATES.read_text(encoding="utf-8"))
    errors: list[str] = []

    pinned = {record["target"]: record for record in receipt.get("records", []) if isinstance(record, dict)}
    actual = {record["target"]: record for record in manifest.get("records", []) if isinstance(record, dict)}
    declared = {item["target"]: item for item in candidates.get("candidates", []) if isinstance(item, dict)}

    if set(actual) != set(declared):
        errors.append(f"manifest/candidate target mismatch: actual={sorted(actual)} declared={sorted(declared)}")

    missing_pinned = sorted(set(pinned) - set(actual))
    if missing_pinned:
        errors.append(f"missing pinned target(s): {missing_pinned}")

    unpinned = sorted(set(actual) - set(pinned))
    if unpinned and not args.allow_unpinned_new:
        errors.append(f"unpinned target(s) require receipt before strict validation: {unpinned}")

    for target, record in actual.items():
        candidate = declared.get(target)
        if not candidate:
            continue
        filename = candidate.get("filename")
        if not isinstance(filename, str) or not filename:
            errors.append(f"{target}: candidate filename missing")
            continue
        if record.get("filename") != filename:
            errors.append(f"{target}: manifest filename {record.get('filename')!r} != candidate {filename!r}")
        path = originals / filename
        if not path.is_file():
            errors.append(f"{target}: missing acquired file {filename}")
            continue
        size = path.stat().st_size
        digest = sha256_file(path)
        if record.get("sha256") != digest:
            errors.append(f"{target}: manifest SHA-256 does not match downloaded bytes")
        if record.get("bytes") != size:
            errors.append(f"{target}: manifest byte count does not match downloaded bytes")
        if record.get("status") != EXPECTED_STATUS:
            errors.append(f"{target}: unexpected acquisition status {record.get('status')!r}")

        pinned_record = pinned.get(target)
        if pinned_record:
            if size != pinned_record.get("bytes"):
                errors.append(f"{target}: byte size drift {size} != {pinned_record.get('bytes')}")
            if digest != pinned_record.get("sha256"):
                errors.append(f"{target}: SHA-256 drift {digest} != {pinned_record.get('sha256')}")
        elif args.allow_unpinned_new:
            print(f"UNPINNED {target}: {size} bytes sha256={digest}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"Field-backlog acquisition integrity FAILED: {len(errors)} error(s).")
        return 1

    print(
        f"Field-backlog acquisition integrity OK: {len(pinned)} pinned original(s), "
        f"{len(unpinned)} explicitly unpinned candidate(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
