#!/usr/bin/env python3
"""Rebuild audited PROJECT OEN music candidates and require exact byte identity."""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "content/audio/music_candidate_audit.source.json"
CONTRACT = ROOT / "content/audio/music_candidate_reproducibility.source.json"
GENERATOR = ROOT / "tools/generate_authored_adaptive_music.py"

EXPECTED_PYTHON = "3.12.13"
EXPECTED_NUMPY = "2.3.5"
EXPECTED_ARCH = "x86_64"
PASS_STATUS = "exact-byte-reproducibility-verified-in-pinned-ci-environment"


class ReproError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def require_environment() -> None:
    errors = []
    if platform.python_version() != EXPECTED_PYTHON:
        errors.append(f"python {platform.python_version()} != {EXPECTED_PYTHON}")
    if np.__version__ != EXPECTED_NUMPY:
        errors.append(f"numpy {np.__version__} != {EXPECTED_NUMPY}")
    if platform.machine() != EXPECTED_ARCH:
        errors.append(f"architecture {platform.machine()} != {EXPECTED_ARCH}")
    if errors:
        raise ReproError("authoring environment mismatch: " + "; ".join(errors))


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise ReproError(f"cannot parse {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ReproError(f"{path}: expected JSON object")
    return value


def validate_contract(contract: dict, audit: dict) -> None:
    if contract.get("generator") != "tools/generate_authored_adaptive_music.py":
        raise ReproError("contract generator path changed")
    if contract.get("origin", {}).get("generatorBlobSha") != "e857bb1be24cc1de413f43e5b370fb133cb81b30":
        raise ReproError("contract no longer pins the audited PR6 generator blob")
    expected = contract.get("expected", {})
    files = audit.get("files")
    if not isinstance(files, list) or len(files) != expected.get("fileCount"):
        raise ReproError("audit/contract file count mismatch")
    if audit.get("technical", {}).get("sourceFamilyCount") != expected.get("sourceFamilyCount"):
        raise ReproError("audit/contract source-family count mismatch")
    if audit.get("provenance", {}).get("thirdPartySamples") is not False:
        raise ReproError("audit no longer states thirdPartySamples=false")
    observed = contract.get("crossEnvironmentObservation", {})
    if observed.get("exactHashMatches") != 12 or observed.get("exactHashTotal") != 14:
        raise ReproError("cross-environment observation must preserve the measured 12/14 result")
    if set(observed.get("mismatches", [])) != {
        "MUS_Finale_Success_01.wav",
        "MUS_Finale_Success_02.wav",
    }:
        raise ReproError("cross-environment mismatch identities changed")


def rebuild_and_compare(audit: dict) -> dict:
    with tempfile.TemporaryDirectory(prefix="oen-music-repro-") as temp:
        out = Path(temp) / "music"
        proc = subprocess.run(
            [sys.executable, str(GENERATOR), "--clean", "--output", str(out)],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if proc.returncode != 0:
            raise ReproError(
                "generator failed:\n" + proc.stdout[-4000:] + "\n" + proc.stderr[-4000:]
            )

        expected_rows = audit.get("files", [])
        expected = {row["file"]: row for row in expected_rows}
        actual_names = {p.name for p in out.glob("*.wav")}
        if actual_names != set(expected):
            missing = sorted(set(expected) - actual_names)
            extra = sorted(actual_names - set(expected))
            raise ReproError(f"rendered filename set differs; missing={missing}, extra={extra}")

        mismatches = []
        for name in sorted(expected):
            path = out / name
            row = expected[name]
            got_hash = sha256(path)
            got_bytes = path.stat().st_size
            if got_hash != row.get("sha256") or got_bytes != row.get("bytes"):
                mismatches.append(
                    {
                        "file": name,
                        "expectedSha256": row.get("sha256"),
                        "actualSha256": got_hash,
                        "expectedBytes": row.get("bytes"),
                        "actualBytes": got_bytes,
                    }
                )

        manifest = load_json(out / "pack_manifest.json")
        if manifest.get("file_count") != 14 or manifest.get("event_count") != 6:
            raise ReproError("rendered pack manifest count mismatch")
        if manifest.get("sample_rate_hz") != 48000 or manifest.get("bit_depth") != 24 or manifest.get("channels") != 2:
            raise ReproError("rendered technical format mismatch")
        if manifest.get("third_party_samples") is not False:
            raise ReproError("rendered manifest must preserve third_party_samples=false")
        if manifest.get("generator_version") != "1.0.0":
            raise ReproError("rendered generator version mismatch")
        if manifest.get("numpy_version") != EXPECTED_NUMPY:
            raise ReproError("rendered manifest NumPy version mismatch")

        return {"mismatches": mismatches, "generatorStdout": proc.stdout.strip()}


def main() -> int:
    try:
        require_environment()
        audit = load_json(AUDIT)
        contract = load_json(CONTRACT)
        validate_contract(contract, audit)
        result = rebuild_and_compare(audit)
        if result["mismatches"]:
            raise ReproError(
                "exact SHA-256 mismatch: "
                + json.dumps(result["mismatches"], ensure_ascii=False)
            )
        print(
            f"Music candidate reproducibility OK: 14/14 exact SHA-256 matches; "
            f"python={platform.python_version()} numpy={np.__version__}; "
            f"status={PASS_STATUS}"
        )
        return 0
    except ReproError as exc:
        print(f"Music candidate reproducibility FAILED: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
