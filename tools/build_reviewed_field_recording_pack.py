#!/usr/bin/env python3
"""Build Project OEN reviewed field-recording derivatives from manually acquired originals.

This lane is intentionally separate from the auto-download Public Domain/CC0 builder.
It never scrapes preview audio and never downloads from authenticated libraries such
as Freesound. Originals are placed in a local source directory after manual license
review, pinned by SHA-256 in the source registry, and only then become buildable.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import zipfile
from pathlib import Path

ALLOWED_LICENSES = {"CC0", "CC0-1.0", "Public-Domain"}
READY = "ready"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def require_columns(path: Path, rows: list[dict[str, str]], columns: set[str]) -> None:
    if not rows:
        raise SystemExit(f"{path}: registry must not be empty")
    missing = columns.difference(rows[0])
    if missing:
        raise SystemExit(f"{path}: missing columns: {', '.join(sorted(missing))}")


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def probe(path: Path) -> dict:
    proc = subprocess.run(
        [
            "ffprobe", "-v", "error", "-select_streams", "a:0",
            "-show_entries", "stream=sample_rate,channels,bits_per_raw_sample:format=duration",
            "-of", "json", str(path),
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


def audit_sources(sources: list[dict[str, str]], source_dir: Path) -> int:
    problems = 0
    print("source_key,status,file,sha256")
    for row in sources:
        source = source_dir / row["expected_filename"]
        if not source.is_file():
            print(f"{row['source_key']},missing,{source},")
            problems += 1
            continue
        actual = sha256(source)
        expected = row["expected_sha256"].strip().lower()
        if not expected:
            print(f"{row['source_key']},needs-pin,{source},{actual}")
            problems += 1
        elif actual != expected:
            print(f"{row['source_key']},hash-mismatch,{source},{actual}")
            problems += 1
        else:
            print(f"{row['source_key']},verified,{source},{actual}")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sources", type=Path, default=Path("content/audio/reviewed_field_recording_sources.csv"))
    parser.add_argument("--jobs", type=Path, default=Path("content/audio/reviewed_field_recording_jobs.csv"))
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("build/oen-reviewed-field-recordings"))
    parser.add_argument("--zip", dest="zip_path", type=Path)
    parser.add_argument("--audit-sources", action="store_true")
    parser.add_argument("--strict-audit", action="store_true", help="Return non-zero if an audited source is missing/unpinned/mismatched")
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()

    sources = load_csv(args.sources)
    jobs = load_csv(args.jobs)
    require_columns(
        args.sources,
        sources,
        {"source_key", "source_page_url", "creator", "title", "license", "expected_filename", "expected_sha256", "status", "notes"},
    )
    require_columns(
        args.jobs,
        jobs,
        {"source_key", "event_id", "variation", "output_name", "start_seconds", "duration_seconds", "channels", "kind", "extra_filters", "landing_path", "loop_intent", "qa_status", "status", "notes"},
    )

    source_map: dict[str, dict[str, str]] = {}
    for row in sources:
        key = row["source_key"].strip()
        if not key or key in source_map:
            raise SystemExit(f"duplicate/blank source_key: {key!r}")
        if row["license"] not in ALLOWED_LICENSES:
            raise SystemExit(f"{key}: unsupported license {row['license']!r}")
        expected = row["expected_sha256"].strip().lower()
        if row["status"] == READY and (len(expected) != 64 or any(ch not in "0123456789abcdef" for ch in expected)):
            raise SystemExit(f"{key}: ready sources require a pinned 64-character SHA-256")
        source_map[key] = row

    output_names: set[str] = set()
    for row in jobs:
        if row["source_key"] not in source_map:
            raise SystemExit(f"job references unknown source_key: {row['source_key']}")
        if row["output_name"] in output_names:
            raise SystemExit(f"duplicate output_name: {row['output_name']}")
        output_names.add(row["output_name"])

    if args.audit_sources:
        problems = audit_sources(sources, args.source_dir)
        if args.strict_audit and problems:
            return 2
        return 0

    for tool in ("ffmpeg", "ffprobe"):
        if shutil.which(tool) is None:
            raise SystemExit(f"{tool} is required on PATH")

    ready_jobs = [row for row in jobs if row["status"] == READY and source_map[row["source_key"]]["status"] == READY]
    if not ready_jobs:
        print("No ready reviewed field-recording jobs. Run with --audit-sources after placing originals in --source-dir.")
        return 0

    if args.clean:
        shutil.rmtree(args.output, ignore_errors=True)
    args.output.mkdir(parents=True, exist_ok=True)

    needed_keys = sorted({row["source_key"] for row in ready_jobs})
    source_paths: dict[str, Path] = {}
    source_hashes: dict[str, str] = {}
    for key in needed_keys:
        meta = source_map[key]
        source = args.source_dir / meta["expected_filename"]
        if not source.is_file():
            raise SystemExit(f"{key}: missing reviewed original: {source}")
        actual = sha256(source)
        expected = meta["expected_sha256"].strip().lower()
        if actual != expected:
            raise SystemExit(f"{key}: SHA-256 mismatch; expected {expected}, got {actual}")
        source_paths[key] = source
        source_hashes[key] = actual

    provenance: list[dict[str, str]] = []
    for row in ready_jobs:
        source_meta = source_map[row["source_key"]]
        out_rel = Path(row["landing_path"]) / row["output_name"]
        out_path = args.output / out_rel
        out_path.parent.mkdir(parents=True, exist_ok=True)

        filters: list[str] = []
        if row["extra_filters"].strip():
            filters.append(row["extra_filters"].strip())
        filters.append("aresample=48000")
        integrated = -24 if row["kind"].strip().lower() == "bed" else -18
        filters.append(f"loudnorm=I={integrated}:TP=-3:LRA=12")

        command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
        if row["start_seconds"].strip():
            command += ["-ss", row["start_seconds"]]
        command += ["-i", str(source_paths[row["source_key"]])]
        if row["duration_seconds"].strip():
            command += ["-t", row["duration_seconds"]]
        command += ["-map", "0:a:0", "-vn", "-af", ",".join(filters), "-ar", "48000"]

        channels = row["channels"].strip().lower()
        if channels == "mono":
            command += ["-ac", "1"]
        elif channels == "stereo":
            command += ["-ac", "2"]
        elif channels != "source":
            raise SystemExit(f"{row['output_name']}: invalid channels={channels}")

        command += ["-c:a", "pcm_s24le", str(out_path)]
        run(command)

        metadata = probe(out_path)
        stream = metadata["streams"][0]
        if int(stream["sample_rate"]) != 48000:
            raise SystemExit(f"{out_path}: expected 48 kHz")
        if channels == "mono" and int(stream["channels"]) != 1:
            raise SystemExit(f"{out_path}: expected mono")
        if channels == "stereo" and int(stream["channels"]) != 2:
            raise SystemExit(f"{out_path}: expected stereo")

        provenance.append(
            {
                "event_id": row["event_id"],
                "variation": row["variation"],
                "output_path": out_rel.as_posix(),
                "output_sha256": sha256(out_path),
                "source_key": row["source_key"],
                "source_sha256": source_hashes[row["source_key"]],
                "source_page_url": source_meta["source_page_url"],
                "creator": source_meta["creator"],
                "license": source_meta["license"],
                "qa_status": row["qa_status"],
            }
        )

    provenance_path = args.output / "PROVENANCE.csv"
    with provenance_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(provenance[0].keys()))
        writer.writeheader()
        writer.writerows(provenance)

    (args.output / "README.txt").write_text(
        "Project OEN reviewed field-recording derivative pack\n\n"
        "Only manually acquired, license-reviewed and SHA-256-pinned originals are accepted.\n"
        "Preview audio is never accepted as a production source. Outputs are 48 kHz / 24-bit PCM.\n"
        "PROVENANCE.csv records source and output hashes. Headset/listening QA remains mandatory.\n",
        encoding="utf-8",
    )

    if args.zip_path:
        deterministic_zip(args.output, args.zip_path)

    print(f"built {len(provenance)} reviewed derivative WAV files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
