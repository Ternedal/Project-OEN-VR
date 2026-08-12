#!/usr/bin/env python3
"""Build a technically normalized Project ØEN environmental candidate pack.

The source registry contains only manually verified Public Domain / CC0 sources.
This builder downloads them, verifies pinned source hashes, creates 48 kHz / 24-bit
WAV derivatives and emits provenance hashes. Outputs are *candidate* assets until
headset listening and loop-edit QA approve them for production use.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

ALLOWED_LICENSES = {"Public-Domain", "CC0-1.0"}
USER_AGENT = "ProjectOEN-AudioBuilder/1.1 (https://github.com/Ternedal/Project-OEN-VR)"
RETRYABLE_HTTP = {429, 500, 502, 503, 504}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def download(url: str, target: Path, max_attempts: int = 6) -> None:
    if target.exists():
        return

    target.parent.mkdir(parents=True, exist_ok=True)
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "audio/ogg,audio/*,video/webm,application/octet-stream;q=0.8,*/*;q=0.5",
    }

    for attempt in range(1, max_attempts + 1):
        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=180) as response, target.open("wb") as out:
                shutil.copyfileobj(response, out)
            return
        except urllib.error.HTTPError as exc:
            target.unlink(missing_ok=True)
            if exc.code not in RETRYABLE_HTTP or attempt == max_attempts:
                raise

            retry_after = exc.headers.get("Retry-After")
            try:
                delay = max(float(retry_after), 1.0) if retry_after else float(2**attempt)
            except ValueError:
                delay = float(2**attempt)
            delay = min(delay, 60.0)
            print(f"HTTP {exc.code} fetching {url}; retry {attempt}/{max_attempts} in {delay:.1f}s")
            time.sleep(delay)
        except urllib.error.URLError as exc:
            target.unlink(missing_ok=True)
            if attempt == max_attempts:
                raise
            delay = min(float(2**attempt), 30.0)
            print(f"Network error fetching {url}: {exc}; retry {attempt}/{max_attempts} in {delay:.1f}s")
            time.sleep(delay)

    raise RuntimeError(f"failed to download {url}")


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def probe(path: Path) -> dict:
    proc = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-select_streams", "a:0",
            "-show_entries", "stream=sample_rate,channels,bits_per_raw_sample:format=duration",
            "-of", "json",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(proc.stdout)


def deterministic_zip(root: Path, zip_path: Path) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(p for p in root.rglob("*") if p.is_file()):
            rel = path.relative_to(root).as_posix()
            info = zipfile.ZipInfo(rel)
            info.date_time = (1980, 1, 1, 0, 0, 0)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, path.read_bytes())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sources", type=Path, default=Path("content/audio/public_domain_environment_sources.csv"))
    parser.add_argument("--build", type=Path, default=Path("content/audio/environment_candidate_build.csv"))
    parser.add_argument("--cache", type=Path, default=Path("build/environment-source-cache"))
    parser.add_argument("--output", type=Path, default=Path("build/oen-public-domain-environment-v0"))
    parser.add_argument("--zip", dest="zip_path", type=Path)
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()

    for tool in ("ffmpeg", "ffprobe"):
        if shutil.which(tool) is None:
            raise SystemExit(f"{tool} is required on PATH")

    sources = {row["source_key"]: row for row in load_csv(args.sources)}
    builds = load_csv(args.build)
    if not sources or not builds:
        raise SystemExit("source/build registry must not be empty")

    for key, row in sources.items():
        if row["license"] not in ALLOWED_LICENSES:
            raise SystemExit(f"{key}: unsupported license {row['license']}")
        if not row["direct_url"].startswith("https://upload.wikimedia.org/"):
            raise SystemExit(f"{key}: direct URL must be an upload.wikimedia.org asset")
        if not row["source_page_url"].startswith("https://commons.wikimedia.org/"):
            raise SystemExit(f"{key}: source page must be Wikimedia Commons")
        expected = row.get("expected_sha256", "").strip().lower()
        if len(expected) != 64 or any(ch not in "0123456789abcdef" for ch in expected):
            raise SystemExit(f"{key}: expected_sha256 must be a pinned 64-character hex digest")

    if args.clean:
        shutil.rmtree(args.output, ignore_errors=True)
    args.output.mkdir(parents=True, exist_ok=True)
    args.cache.mkdir(parents=True, exist_ok=True)

    source_paths: dict[str, Path] = {}
    source_hashes: dict[str, str] = {}
    for key, row in sources.items():
        suffix = Path(urllib.parse.urlparse(row["direct_url"]).path).suffix or ".bin"
        cached = args.cache / f"{key}{suffix}"
        download(row["direct_url"], cached)
        actual_hash = sha256(cached)
        expected_hash = row["expected_sha256"].strip().lower()
        if actual_hash != expected_hash:
            cached.unlink(missing_ok=True)
            raise SystemExit(
                f"{key}: source SHA256 mismatch; expected {expected_hash}, got {actual_hash}. "
                "Re-verify the original source page before updating the pin."
            )
        source_paths[key] = cached
        source_hashes[key] = actual_hash
        # Wikimedia asks automated clients to identify themselves and avoid bursty access.
        time.sleep(1.0)

    provenance_rows: list[dict[str, str]] = []
    for row in builds:
        key = row["source_key"]
        if key not in sources:
            raise SystemExit(f"unknown source_key: {key}")

        source = sources[key]
        out_rel = Path(row["landing_path"]) / row["output_name"]
        out_path = args.output / out_rel
        out_path.parent.mkdir(parents=True, exist_ok=True)

        filters = []
        if row["extra_filters"].strip():
            filters.append(row["extra_filters"].strip())
        filters += [
            "aresample=48000",
            f"loudnorm=I={-24 if row['kind'] == 'bed' else -18}:TP=-3:LRA=12",
        ]

        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
        if row["start_seconds"].strip():
            cmd += ["-ss", row["start_seconds"]]
        cmd += ["-i", str(source_paths[key])]
        if row["duration_seconds"].strip():
            cmd += ["-t", row["duration_seconds"]]
        cmd += ["-map", "0:a:0", "-vn", "-af", ",".join(filters), "-ar", "48000"]

        channels = row["channels"].strip().lower()
        if channels == "mono":
            cmd += ["-ac", "1"]
        elif channels == "stereo":
            cmd += ["-ac", "2"]
        elif channels != "source":
            raise SystemExit(f"{row['output_name']}: invalid channels={channels}")

        cmd += ["-c:a", "pcm_s24le", str(out_path)]
        run(cmd)

        metadata = probe(out_path)
        stream = metadata["streams"][0]
        if int(stream["sample_rate"]) != 48000:
            raise SystemExit(f"{out_path}: expected 48 kHz")
        if channels == "mono" and int(stream["channels"]) != 1:
            raise SystemExit(f"{out_path}: expected mono")
        if channels == "stereo" and int(stream["channels"]) != 2:
            raise SystemExit(f"{out_path}: expected stereo")

        provenance_rows.append(
            {
                "event_id": row["event_id"],
                "variation": row["variation"],
                "output_path": out_rel.as_posix(),
                "output_sha256": sha256(out_path),
                "source_key": key,
                "source_sha256": source_hashes[key],
                "source_page_url": source["source_page_url"],
                "creator": source["creator"],
                "license": source["license"],
                "qa_status": row["qa_status"],
            }
        )

    provenance_path = args.output / "PROVENANCE.csv"
    with provenance_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(provenance_rows[0].keys()))
        writer.writeheader()
        writer.writerows(provenance_rows)

    readme = args.output / "README.txt"
    readme.write_text(
        "Project ØEN public-domain environmental candidate pack v0\n"
        "\n"
        "These are technically normalized candidate derivatives, not final mastered assets.\n"
        "Every file is 48 kHz / 24-bit PCM and has source provenance in PROVENANCE.csv.\n"
        "Source downloads are SHA256-pinned and fail closed if an upstream file changes.\n"
        "Before promotion to production: listen in Quest headset, remove contamination,\n"
        "perform seamless-loop edits where loop_intent=yes, and approve variation quality.\n",
        encoding="utf-8",
    )

    if args.zip_path:
        deterministic_zip(args.output, args.zip_path)

    print(f"built {len(provenance_rows)} candidate WAV files")
    if args.zip_path:
        print(args.zip_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
