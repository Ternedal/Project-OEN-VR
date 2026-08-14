#!/usr/bin/env python3
"""Acquire license-verified external audio originals without committing binaries."""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CANDIDATES = ROOT / "content" / "audio" / "acquisition_candidates.source.json"
CANDIDATES = DEFAULT_CANDIDATES
DEFAULT_OUTPUT = ROOT / "PrivateContent" / "AudioSourceIncoming"
USER_AGENT = "Project-OEN-VR-source-acquisition/1.3"
DEFAULT_RETRIES = 4
DEFAULT_INTER_DOWNLOAD_DELAY = 1.5


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
    result = subprocess.run([
        executable, "-v", "error", "-select_streams", "a:0",
        "-show_entries", "stream=codec_name,sample_rate,channels,bits_per_raw_sample:format=duration,bit_rate",
        "-of", "json", str(path),
    ], capture_output=True, text=True, check=False)
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


def load_candidates(path: Path = CANDIDATES) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    candidates = data.get("candidates")
    if not isinstance(candidates, list):
        raise RuntimeError("candidate source must contain a candidates list")
    return [item for item in candidates if isinstance(item, dict)]


def load_excluded_targets(path: Path | None) -> set[str]:
    if path is None:
        return set()
    resolved = resolve_candidate_source(path)
    data = json.loads(resolved.read_text(encoding="utf-8"))
    records = data.get("records")
    if not isinstance(records, list):
        raise RuntimeError("exclude-targets source must contain a records list")
    return {item.get("target") for item in records if isinstance(item, dict) and isinstance(item.get("target"), str)}


def _retry_delay(exc: urllib.error.HTTPError, attempt: int) -> float:
    retry_after = exc.headers.get("Retry-After") if exc.headers else None
    if retry_after:
        try:
            return min(90.0, max(2.0, float(retry_after)))
        except ValueError:
            pass
    return min(90.0, (3.0 ** attempt) + random.uniform(0.5, 2.0))


def _download_bytes(url: str, part_path: Path, timeout: int, retries: int) -> None:
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response, part_path.open("wb") as output:
                while True:
                    block = response.read(1024 * 1024)
                    if not block:
                        break
                    output.write(block)
            return
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code not in {429, 500, 502, 503, 504} or attempt >= retries:
                raise
            delay = _retry_delay(exc, attempt)
            part_path.unlink(missing_ok=True)
            print(f"RETRY HTTP {exc.code}: attempt {attempt + 2}/{retries + 1} in {delay:.1f}s", file=sys.stderr)
            time.sleep(delay)
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
            if attempt >= retries:
                raise
            delay = min(90.0, (3.0 ** attempt) + random.uniform(0.5, 2.0))
            part_path.unlink(missing_ok=True)
            print(f"RETRY transport error: attempt {attempt + 2}/{retries + 1} in {delay:.1f}s", file=sys.stderr)
            time.sleep(delay)
    if last_error:
        raise last_error


def download(candidate: dict, originals: Path, timeout: int, retries: int = DEFAULT_RETRIES) -> dict:
    target = candidate.get("target")
    url = candidate.get("directDownload")
    filename = candidate.get("filename")
    if not all(isinstance(value, str) and value for value in (target, url, filename)):
        raise RuntimeError(f"{target or '<unknown>'}: direct-download metadata is incomplete")

    originals.mkdir(parents=True, exist_ok=True)
    final_path = originals / filename
    part_path = originals / f"{filename}.part"
    part_path.unlink(missing_ok=True)
    _download_bytes(url, part_path, timeout, retries)
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


def write_manifest(manifest_path: Path, candidate_source: Path, records: list[dict]) -> None:
    manifest = {
        "version": 1,
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        "candidateSource": str(candidate_source.relative_to(ROOT)).replace("\\", "/"),
        "records": sorted(records, key=lambda item: str(item.get("target"))),
        "rule": "acquired-original is not listening-approved, derived-master-approved, Unity-integrated or release-approved",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-source", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--target", action="append", default=[])
    parser.add_argument("--all-direct", action="store_true")
    parser.add_argument("--exclude-targets-from", type=Path, help="JSON receipt with records[].target values to skip.")
    parser.add_argument("--allow-empty", action="store_true", help="Write an empty manifest and succeed when selection is empty.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--timeout", type=int, default=90)
    parser.add_argument("--retries", type=int, default=DEFAULT_RETRIES)
    parser.add_argument("--inter-download-delay", type=float, default=DEFAULT_INTER_DOWNLOAD_DELAY)
    args = parser.parse_args()

    candidate_source = resolve_candidate_source(args.candidate_source)
    candidates = load_candidates(candidate_source)
    excluded = load_excluded_targets(args.exclude_targets_from)
    direct = [item for item in candidates if item.get("directDownload") and item.get("target") not in excluded]
    requested = set(args.target)
    selected = direct if args.all_direct else [item for item in direct if item.get("target") in requested]

    output_root = args.output if args.output.is_absolute() else ROOT / args.output
    output_root = output_root.resolve()
    originals = output_root / "originals"
    manifest_path = output_root / "acquisition_manifest.json"
    output_root.mkdir(parents=True, exist_ok=True)

    if not selected:
        if args.allow_empty:
            write_manifest(manifest_path, candidate_source, [])
            print(f"No unexcluded direct targets selected; wrote empty manifest: {manifest_path}")
            return 0
        available = ", ".join(str(item.get("target")) for item in direct)
        print("No direct-download candidate selected.")
        print(f"Available direct targets: {available}")
        return 2

    records: list[dict] = []
    failures = 0
    for index, candidate in enumerate(selected):
        target = candidate.get("target")
        if index and args.inter_download_delay > 0:
            time.sleep(args.inter_download_delay)
        try:
            record = download(candidate, originals, args.timeout, max(0, args.retries))
            records.append(record)
            print(f"ACQUIRED {target}: {record['bytes']} bytes sha256={record['sha256']}")
        except Exception as exc:  # noqa: BLE001
            failures += 1
            print(f"FAILED {target}: {exc}", file=sys.stderr)

    write_manifest(manifest_path, candidate_source, records)
    print(f"Manifest: {manifest_path}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
