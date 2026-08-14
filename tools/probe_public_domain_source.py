#!/usr/bin/env python3
"""Download one manually verified Wikimedia source and print its SHA-256 for pinning.

This helper is intentionally separate from production builds: a source must be license-reviewed
on its Commons page first, then probed, then copied into the pinned production registry. The
probe output alone is never proof of licensing or listening approval.
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

USER_AGENT = "ProjectOEN-AudioSourceProbe/1.0 (https://github.com/Ternedal/Project-OEN-VR)"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    args = parser.parse_args()

    if not args.url.startswith("https://upload.wikimedia.org/"):
        raise SystemExit("probe URL must be an upload.wikimedia.org original asset")

    request = urllib.request.Request(
        args.url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "audio/ogg,audio/*,video/webm,application/octet-stream;q=0.8,*/*;q=0.5",
        },
    )

    with tempfile.TemporaryDirectory(prefix="oen-audio-probe-") as tmp:
        target = Path(tmp) / "source.bin"
        try:
            with urllib.request.urlopen(request, timeout=180) as response, target.open("wb") as out:
                shutil.copyfileobj(response, out)
        except (urllib.error.HTTPError, urllib.error.URLError) as exc:
            raise SystemExit(f"source probe download failed: {exc}") from exc

        print(f"url={args.url}")
        print(f"bytes={target.stat().st_size}")
        print(f"sha256={sha256(target)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
