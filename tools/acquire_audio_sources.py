#!/usr/bin/env python3
"""Acquire license-verified external audio originals without committing binaries."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CANDIDATES = ROOT / "content" / "audio" / "acquisition_candidates.source.json"
# Backward-compatible public constant retained for existing contract tests/importers.
CANDIDATES = DEFAULT_CANDIDATES
DEFAULT_OUTPUT = ROOT / "PrivateContent" / "AudioSourceIncoming"
USER_AGENT = "Project-OEN-VR-source-acquisition/1.1"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ffprobe(path: Path) -> dict | None:
    executable = shutil.which("ffprobe")
    if not executable:
        return None
    result = subprocess.run(
        [
            executable,
            "-v", "error",
            "-select_streams", "a:0",
            "-show_entries", "stream=codec_name,sample_rate,channels,bits_per_raw_sample:format=duration",
            "-of", "json",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return {"error": result.stderr.strip() or "ffprobe failed"}
    return json.loads(result.stdout)


def resolve_candidate_source(value: Path) -> Path:
    path = value if value.is_absolute() else ROOT / value
    path = path.resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise RuntimeError("candidate source must stay inside the repository") from exc
    if not path.is_file():
        raise RuntimeError(f"candidate source does not exist: {path}")
    return path


def load_candidates(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    candidates = data.get("candidates")
    if not isinstance(candidates, list):
        raise RuntimeError("candidate source must contain a candidates list")
    return [item for item in candidates if isinstance(item, dict)]


def download(candidate: dict, originals: Path, timeout: int) -> dict:
    target = candidate.get("target")
    url = candidate.get("directDownload")
    filename = candidate.get("filename")
    if not all(isinstance(value, str) and value for value in (target, url, filename)):
        raise RuntimeError(f"{target or '<unknown>'}: direct-download metadata is incomplete")

    originals.mkdir(parents=True, exist_ok=True)
    final_path = originals / filename
    part_path = originals / f"{filename}.part"

    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response, part_path.open("wb") as output:
        while True:
            block = response.read(1024 * 1024)
            if not block:
                break
            output.write(block)
    part_path.replace(final_path)

    return {
        "target": target,
        "filename": filename,
        "provider": candidate.get("provider"),
        "sourcePage": candidate.get("sourcePage"),
        "directDownload": url,
        "license": candidate.get("license"),
        "bytes": final_path.stat().st_size,
        "sha256": sha256_file(final_path),
        "acquiredAtUtc": datetime.now(timezone.utc).isoformat(),
        "relativePath": str(final_path.relative_to(ROOT)).replace("\\", "/") if final_path.is_relative_to(ROOT) else str(final_path),
        "sourceFormatClaim": candidate.get("sourceFormat"),
        "technicalProbe": ffprobe(final_path),
        "status": "acquired-original-not-listening-approved",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-source", type=Path, default=DEFAULT_CANDIDATES,
                        help="Repository-local candidate JSON. Defaults to canonical acquisition_candidates.source.json.")
    parser.add_argument("--target", action="append", default=[], help="Acquire one target; repeat as needed.")
    parser.add_argument("--all-direct", action="store_true", help="Acquire every candidate with directDownload metadata.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--timeout", type=int, default=90)
    args = parser.parse_args()

    candidate_source = resolve_candidate_source(args.candidate_source)
    candidates = load_candidates(candidate_source)
    direct = [item for item in candidates if item.get("directDownload")]
    requested = set(args.target)
    selected = direct if args.all_direct else [item for item in direct if item.get("target") in requested]

    if not selected:
        available = ", ".join(str(item.get("target")) for item in direct)
        print("No direct-download candidate selected.")
        print(f"Available direct targets: {available}")
        print("Use --target TARGET or --all-direct.")
        return 2

    output_root = args.output if args.output.is_absolute() else ROOT / args.output
    output_root = output_root.resolve()
    originals = output_root / "originals"
    manifest_path = output_root / "acquisition_manifest.json"
    output_root.mkdir(parents=True, exist_ok=True)

    previous: dict = {"version": 1, "records": []}
    if manifest_path.exists():
        try:
            previous = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            previous = {"version": 1, "records": []}
    records = [item for item in previous.get("records", []) if isinstance(item, dict)]

    failures = 0
    for candidate in selected:
        target = candidate.get("target")
        try:
            record = download(candidate, originals, args.timeout)
            records = [item for item in records if item.get("target") != target]
            records.append(record)
            print(f"ACQUIRED {target}: {record['bytes']} bytes sha256={record['sha256']}")
        except Exception as exc:  # noqa: BLE001
            failures += 1
            print(f"FAILED {target}: {exc}", file=sys.stderr)

    manifest = {
        "version": 1,
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        "candidateSource": str(candidate_source.relative_to(ROOT)).replace("\\", "/"),
        "records": sorted(records, key=lambda item: str(item.get("target"))),
        "rule": "acquired-original is not listening-approved, derived-master-approved, Unity-integrated or release-approved",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Manifest: {manifest_path}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
