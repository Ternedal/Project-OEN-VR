from __future__ import annotations

import base64
import shutil
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TRIGGER = REPO / "tools" / "generated_art" / "import_trigger.txt"
PAYLOAD_ROOT = REPO / "art_payloads"


def main() -> int:
    if not TRIGGER.exists():
        print("No production-art import trigger; nothing to do.")
        return 0

    batch = TRIGGER.read_text(encoding="utf-8").strip()
    if not batch:
        print("Empty production-art import trigger; nothing to do.")
        return 0

    batch_dir = PAYLOAD_ROOT / batch
    parts = sorted(batch_dir.glob("part_*.b64"))
    if not parts:
        raise RuntimeError(f"No payload parts found for {batch!r} at {batch_dir}")

    print(f"Importing production-art payload {batch} from {len(parts)} part(s)")
    encoded = b"".join(p.read_bytes().strip() for p in parts)
    archive_bytes = base64.b64decode(encoded, validate=True)

    archive = REPO / f".{batch}.zip"
    archive.write_bytes(archive_bytes)
    try:
        with zipfile.ZipFile(archive, "r") as zf:
            bad = zf.testzip()
            if bad:
                raise RuntimeError(f"Corrupt payload member: {bad}")
            for member in zf.infolist():
                target = (REPO / member.filename).resolve()
                if REPO.resolve() not in target.parents and target != REPO.resolve():
                    raise RuntimeError(f"Unsafe archive path: {member.filename}")
            zf.extractall(REPO)
    finally:
        archive.unlink(missing_ok=True)

    shutil.rmtree(batch_dir)
    if PAYLOAD_ROOT.exists() and not any(PAYLOAD_ROOT.iterdir()):
        PAYLOAD_ROOT.rmdir()
    TRIGGER.unlink(missing_ok=True)

    print(f"Imported {batch} into repository and removed temporary payload.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
