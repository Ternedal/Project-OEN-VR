#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "content/audio/acquisition_candidates.field_backlog_pending.source.json"
EXPECTED_RUNTIME = {"SFX_AMB_Jungle_CanopyWind", "SFX_WTH_Storm_RoughOcean"}
EXPECTED_PENDING = {"SFX_AMB_Beach_PalmCanopy"}
ACQUIRED_STATUS = "acquired-original-not-listening-approved"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    root = args.root if args.root.is_absolute() else ROOT / args.root
    manifest_path = root / "acquisition_manifest.json"
    originals = root / "originals"
    errors: list[str] = []

    try:
        registry = load(CANDIDATES)
        manifest = load(manifest_path)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: cannot parse registry/manifest: {exc}")
        return 1

    policy = registry.get("policy", {})
    allowed_licenses = set(policy.get("acceptedLicenses", []))
    if allowed_licenses != {"CC0", "Public Domain"}:
        errors.append(f"accepted license policy drift: {sorted(allowed_licenses)}")
    for flag in ("commercialReuseRequired", "naturalSourceRequired", "directDownloadRequired", "acquisitionIsNotApproval", "humanListeningRequired"):
        if policy.get(flag) is not True:
            errors.append(f"policy flag {flag} must remain true")

    candidates = registry.get("candidates")
    if not isinstance(candidates, list):
        errors.append("candidates must be a list")
        candidates = []
    by_target = {}
    runtime_events = set()
    for item in candidates:
        if not isinstance(item, dict):
            errors.append("candidate entry must be an object")
            continue
        target = item.get("target")
        runtime = item.get("runtimeEventCandidate")
        if not isinstance(target, str) or not target:
            errors.append("candidate target missing")
            continue
        if target in by_target:
            errors.append(f"duplicate candidate target: {target}")
        by_target[target] = item
        if isinstance(runtime, str):
            runtime_events.add(runtime)
        if item.get("license") not in allowed_licenses:
            errors.append(f"{target}: license outside accepted policy")
        if not isinstance(item.get("directDownload"), str) or not item["directDownload"].startswith("https://"):
            errors.append(f"{target}: direct HTTPS download is required")
        if not isinstance(item.get("sourcePage"), str) or not item["sourcePage"].startswith("https://"):
            errors.append(f"{target}: source page missing")
        if not isinstance(item.get("caveat"), str) or "human" not in item["caveat"].lower():
            errors.append(f"{target}: human-listening caveat missing")

    if runtime_events != EXPECTED_RUNTIME:
        errors.append(f"runtime candidate set drift: got={sorted(runtime_events)} expected={sorted(EXPECTED_RUNTIME)}")

    unresolved = registry.get("stillUnresolved")
    unresolved_events = {x.get("runtimeEvent") for x in unresolved or [] if isinstance(x, dict)}
    if unresolved_events != EXPECTED_PENDING:
        errors.append(f"unresolved runtime set drift: got={sorted(unresolved_events)} expected={sorted(EXPECTED_PENDING)}")

    records = manifest.get("records")
    if not isinstance(records, list):
        errors.append("manifest records must be a list")
        records = []
    actual = {r.get("target"): r for r in records if isinstance(r, dict)}
    if set(actual) != set(by_target):
        errors.append(f"acquired target mismatch: actual={sorted(actual)} expected={sorted(by_target)}")

    for target, candidate in by_target.items():
        record = actual.get(target)
        if not record:
            continue
        filename = candidate.get("filename")
        if record.get("filename") != filename:
            errors.append(f"{target}: acquired filename mismatch")
            continue
        path = originals / filename
        if not path.is_file():
            errors.append(f"{target}: downloaded original missing: {filename}")
            continue
        digest = sha256_file(path)
        size = path.stat().st_size
        if record.get("sha256") != digest:
            errors.append(f"{target}: manifest SHA does not match downloaded bytes")
        if record.get("bytes") != size or size <= 1024:
            errors.append(f"{target}: invalid byte count {record.get('bytes')!r}/{size}")
        if record.get("status") != ACQUIRED_STATUS:
            errors.append(f"{target}: acquisition status must remain unapproved")
        for field in ("provider", "sourcePage", "directDownload", "license"):
            if record.get(field) != candidate.get(field):
                errors.append(f"{target}: manifest provenance drift in {field}")
        probe = record.get("technicalProbe")
        if not isinstance(probe, dict) or probe.get("error"):
            errors.append(f"{target}: ffprobe failed or missing")
            continue
        streams = probe.get("streams")
        if not isinstance(streams, list) or not streams:
            errors.append(f"{target}: no audio stream reported")
        else:
            stream = streams[0]
            try:
                sample_rate = int(stream.get("sample_rate", 0))
                channels = int(stream.get("channels", 0))
            except (TypeError, ValueError):
                sample_rate = channels = 0
            if sample_rate <= 0 or channels <= 0:
                errors.append(f"{target}: invalid technical probe sample-rate/channels")

    if errors:
        for error in errors:
            print("ERROR:", error)
        print(f"Pending field acquisition FAILED: {len(errors)} error(s).")
        return 1

    print(f"Pending field acquisition OK: {len(actual)} exact original(s) downloaded and probed; palm canopy remains explicit acquisition-pending; no source approval promoted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
