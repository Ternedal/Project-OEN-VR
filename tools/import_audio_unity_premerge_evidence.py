#!/usr/bin/env python3
"""Validate/import physical Unity audio pre-merge evidence.

The Unity batch runner writes a JSON evidence file. This tool binds that evidence to the
pinned first-playable artifact identity before marking the three Unity rows in
content/audio/audio_premerge_qa.csv as passed. Quest 2 gates are never modified here.

Without --apply the command is read-only. --self-test exercises the importer against a
temporary registry using synthetic evidence bound to the current pin; it never touches the
real QA registry.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "content/audio/audio_premerge_qa.csv"
DEFAULT_PIN = ROOT / "content/audio/first_playable_artifact_pin.json"
UNITY_GATES = {
    "unity_import_compile",
    "unity_first_playable_audit",
    "unity_active_scene_audit",
}
HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"unable to read valid JSON from {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"{path}: expected a JSON object")
    return value


def validate_pin(pin: dict) -> None:
    if pin.get("schema_version") != 1:
        raise SystemExit("artifact pin: schema_version must be 1")
    if pin.get("artifact_name") != "oen-unity-first-playable-audio-v1":
        raise SystemExit("artifact pin: unexpected artifact_name")
    if pin.get("unity_version") != "6000.4.10f1":
        raise SystemExit("artifact pin: Unity version drift")
    if not HEX40.fullmatch(str(pin.get("source_head_sha", ""))):
        raise SystemExit("artifact pin: source_head_sha must be 40 lowercase hex characters")
    for key in (
        "github_artifact_wrapper_sha256",
        "inner_zip_sha256",
        "manifest_sha256",
    ):
        if not HEX64.fullmatch(str(pin.get(key, ""))):
            raise SystemExit(f"artifact pin: {key} must be 64 lowercase hex characters")
    for key in (
        "source_audio_validation_run",
        "source_workflow_run_id",
        "source_artifact_id",
        "clip_count",
        "event_count",
    ):
        value = pin.get(key)
        if not isinstance(value, int) or value <= 0:
            raise SystemExit(f"artifact pin: {key} must be a positive integer")
    if pin["clip_count"] < 160 or pin["event_count"] < 45:
        raise SystemExit("artifact pin: payload falls below the stable Unity first-playable floor")


def validate_iso_utc(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SystemExit("Unity evidence: generatedUtc is required")
    text = value.strip()
    normalized = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise SystemExit(f"Unity evidence: generatedUtc is not valid ISO-8601: {text!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise SystemExit("Unity evidence: generatedUtc must include a UTC offset/Z")
    if parsed.utcoffset().total_seconds() != 0:
        raise SystemExit("Unity evidence: generatedUtc must be UTC")
    return text


def validate_string_array(evidence: dict, key: str) -> list[str]:
    value = evidence.get(key)
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise SystemExit(f"Unity evidence: {key} must be an array of strings")
    return value


def validate_evidence(evidence: dict, pin: dict) -> dict[str, dict]:
    if evidence.get("schemaVersion") != 1:
        raise SystemExit("Unity evidence: schemaVersion must be 1")
    if evidence.get("unityVersion") != pin["unity_version"]:
        raise SystemExit(
            "Unity evidence: Unity version mismatch; "
            f"expected {pin['unity_version']}, got {evidence.get('unityVersion')!r}"
        )
    if evidence.get("manifestSha256") != pin["manifest_sha256"]:
        raise SystemExit("Unity evidence: manifest SHA-256 does not match pinned first-playable payload")
    if evidence.get("manifestClipCount") != pin["clip_count"]:
        raise SystemExit("Unity evidence: manifest clip count does not match artifact pin")
    if evidence.get("manifestEventCount") != pin["event_count"]:
        raise SystemExit("Unity evidence: manifest event count does not match artifact pin")
    if evidence.get("missingScriptCount") != 0:
        raise SystemExit("Unity evidence: generated runtime contains Missing Script references")

    errors = validate_string_array(evidence, "errors")
    warnings = validate_string_array(evidence, "warnings")
    if evidence.get("errorCount") != len(errors):
        raise SystemExit("Unity evidence: errorCount does not match errors array")
    if evidence.get("warningCount") != len(warnings):
        raise SystemExit("Unity evidence: warningCount does not match warnings array")
    if errors:
        raise SystemExit("Unity evidence: Unity batch run emitted error logs")

    scene = evidence.get("scenePath")
    if (
        not isinstance(scene, str)
        or not scene.startswith("Assets/")
        or not scene.lower().endswith(".unity")
    ):
        raise SystemExit("Unity evidence: scenePath must be an Assets/.../*.unity path")
    validate_iso_utc(evidence.get("generatedUtc"))

    gate_rows = evidence.get("gates")
    if not isinstance(gate_rows, list):
        raise SystemExit("Unity evidence: gates must be an array")
    gates: dict[str, dict] = {}
    for row in gate_rows:
        if not isinstance(row, dict):
            raise SystemExit("Unity evidence: every gate must be an object")
        gate_id = str(row.get("gateId", "")).strip()
        if not gate_id or gate_id in gates:
            raise SystemExit(f"Unity evidence: blank/duplicate gateId {gate_id!r}")
        gates[gate_id] = row

    if set(gates) != UNITY_GATES:
        raise SystemExit(
            "Unity evidence gate drift: "
            f"missing={sorted(UNITY_GATES - set(gates))}, extra={sorted(set(gates) - UNITY_GATES)}"
        )
    for gate_id, row in gates.items():
        if row.get("passed") is not True:
            raise SystemExit(f"Unity evidence: {gate_id} is not passed")
        detail = row.get("detail")
        if not isinstance(detail, str) or not detail.strip():
            raise SystemExit(f"Unity evidence: {gate_id} detail is required")
    return gates


def read_registry(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            fieldnames = reader.fieldnames
            rows = list(reader)
    except OSError as exc:
        raise SystemExit(f"unable to read QA registry {path}: {exc}") from exc
    if not fieldnames:
        raise SystemExit("QA registry: missing header")
    required = {"gate_id", "category", "required_for_merge", "status", "evidence", "acceptance"}
    if not required.issubset(fieldnames):
        raise SystemExit(f"QA registry: missing columns {sorted(required - set(fieldnames))}")
    return fieldnames, rows


def apply_to_registry(
    registry: Path,
    evidence: dict,
    pin: dict,
    *,
    output: Path | None = None,
) -> Path:
    fieldnames, rows = read_registry(registry)
    by_id = {row["gate_id"].strip(): row for row in rows}
    missing = UNITY_GATES - set(by_id)
    if missing:
        raise SystemExit(f"QA registry: missing Unity gates {sorted(missing)}")

    evidence_ref = (
        "unity-batch;"
        f"unity={evidence['unityVersion']};"
        f"manifest_sha256={pin['manifest_sha256']};"
        f"clips={pin['clip_count']};events={pin['event_count']};"
        f"utc={evidence['generatedUtc']};scene={evidence['scenePath']}"
    )
    for gate_id in UNITY_GATES:
        row = by_id[gate_id]
        if row.get("required_for_merge", "").strip().lower() != "yes":
            raise SystemExit(f"QA registry: {gate_id} must remain required_for_merge=yes")
        if row.get("category", "").strip() != "unity":
            raise SystemExit(f"QA registry: {gate_id} category must remain unity")
        row["status"] = "passed"
        row["evidence"] = evidence_ref

    destination = output or registry
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return destination


def synthetic_evidence(pin: dict) -> dict:
    return {
        "schemaVersion": 1,
        "generatedUtc": "2099-01-01T00:00:00Z",
        "unityVersion": pin["unity_version"],
        "scenePath": "Assets/Scenes/SyntheticAudioPremerge.unity",
        "manifestSha256": pin["manifest_sha256"],
        "manifestClipCount": pin["clip_count"],
        "manifestEventCount": pin["event_count"],
        "missingScriptCount": 0,
        "errorCount": 0,
        "warningCount": 0,
        "gates": [
            {"gateId": gate_id, "passed": True, "detail": "synthetic importer self-test"}
            for gate_id in sorted(UNITY_GATES)
        ],
        "errors": [],
        "warnings": [],
    }


def expect_rejected(evidence: dict, pin: dict, label: str) -> None:
    try:
        validate_evidence(evidence, pin)
    except SystemExit:
        return
    raise SystemExit(f"self-test failed: {label} evidence was unexpectedly accepted")


def run_self_test(pin: dict, registry: Path) -> None:
    evidence = synthetic_evidence(pin)
    validate_evidence(evidence, pin)

    stale_manifest = synthetic_evidence(pin)
    stale_manifest["manifestSha256"] = "0" * 64
    expect_rejected(stale_manifest, pin, "stale-manifest")

    errored = synthetic_evidence(pin)
    errored["errorCount"] = 1
    errored["errors"] = ["synthetic Unity error"]
    expect_rejected(errored, pin, "error-log")

    missing_gate = synthetic_evidence(pin)
    missing_gate["gates"] = missing_gate["gates"][:-1]
    expect_rejected(missing_gate, pin, "missing-gate")

    with tempfile.TemporaryDirectory(prefix="oen-audio-unity-evidence-") as temp:
        target = Path(temp) / "qa.csv"
        shutil.copyfile(registry, target)
        apply_to_registry(target, evidence, pin)
        _, rows = read_registry(target)
        by_id = {row["gate_id"]: row for row in rows}
        for gate_id in UNITY_GATES:
            if by_id[gate_id]["status"] != "passed":
                raise SystemExit(f"self-test failed: {gate_id} was not promoted")
        quest_rows = [row for row in rows if row["category"] == "quest2"]
        if not quest_rows or any(row["status"] == "passed" for row in quest_rows):
            raise SystemExit("self-test failed: Quest rows were unexpectedly promoted")
    print(
        "Unity premerge evidence importer self-test OK: valid pinned evidence accepted; stale/error/incomplete "
        "evidence rejected; 3 Unity gates promoted in temp registry; Quest gates untouched."
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--pin", type=Path, default=DEFAULT_PIN)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    pin = load_json(args.pin)
    validate_pin(pin)

    if args.self_test:
        run_self_test(pin, args.registry)
        return 0

    if args.evidence is None:
        raise SystemExit("--evidence is required unless --self-test is used")
    evidence = load_json(args.evidence)
    validate_evidence(evidence, pin)

    if args.apply:
        destination = apply_to_registry(
            args.registry,
            evidence,
            pin,
            output=args.output,
        )
        print(f"Unity premerge evidence accepted and applied to: {destination}")
    else:
        print(
            "Unity premerge evidence OK: pinned manifest/artifact identity matches and all "
            "3 Unity gates passed. Read-only validation only; use --apply to update the QA registry."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
