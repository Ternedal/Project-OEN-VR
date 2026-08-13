#!/usr/bin/env python3
"""Fail closed if reacquired extension audio differs from pinned receipts/shortlist."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "content" / "audio" / "acquisition_extension_receipt.source.json"
SHORTLIST = ROOT / "content" / "audio" / "acquisition_extension_member_shortlist.source.json"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True, help="Extension acquisition output root")
    args = parser.parse_args()

    root = args.root if args.root.is_absolute() else ROOT / args.root
    manifest_path = root / "acquisition_manifest.json"
    originals = root / "originals"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    shortlist = json.loads(SHORTLIST.read_text(encoding="utf-8"))
    errors: list[str] = []

    expected = {record["target"]: record for record in receipt.get("records", [])}
    actual = {record["target"]: record for record in manifest.get("records", [])}
    if set(actual) != set(expected):
        errors.append(f"target set mismatch: actual={sorted(actual)} expected={sorted(expected)}")

    archive_paths: dict[str, Path] = {}
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
        if path.suffix.lower() == ".zip":
            archive_paths[target] = path

    zip_cache: dict[str, zipfile.ZipFile] = {}
    try:
        for member in shortlist.get("members", []):
            target = member.get("archiveTarget")
            member_path = member.get("path")
            expected_hash = member.get("sha256")
            archive = archive_paths.get(str(target))
            if archive is None:
                errors.append(f"{target}: shortlist member has no acquired archive")
                continue
            if target not in zip_cache:
                zip_cache[str(target)] = zipfile.ZipFile(archive)
            zf = zip_cache[str(target)]
            if member_path not in zf.namelist():
                errors.append(f"{target}: missing archive member {member_path}")
                continue
            digest = sha256_bytes(zf.read(str(member_path)))
            if digest != expected_hash:
                errors.append(f"{target}:{member_path}: SHA-256 drift {digest} != {expected_hash}")
    finally:
        for zf in zip_cache.values():
            zf.close()

    cloth = archive_paths.get("SFX_CLOTH_PACK_ALT")
    if cloth:
        with zipfile.ZipFile(cloth) as zf:
            license_names = [name for name in zf.namelist() if Path(name).name.lower() == "license.txt"]
            if not license_names:
                errors.append("SFX_CLOTH_PACK_ALT: embedded license.txt missing")
            else:
                text = zf.read(license_names[0]).decode("utf-8", errors="replace").lower()
                if "cc0" not in text and "publicdomain/zero" not in text:
                    errors.append("SFX_CLOTH_PACK_ALT: embedded license no longer declares CC0/public-domain-zero")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"Extension acquisition integrity FAILED: {len(errors)} error(s).")
        return 1

    print(f"Extension acquisition integrity OK: {len(expected)} source files and {len(shortlist.get('members', []))} pinned archive members.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
