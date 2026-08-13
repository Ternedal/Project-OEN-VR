#!/usr/bin/env python3
"""Validate/import structured Quest 2 audio pre-merge evidence.

This cannot create physical evidence. It only rejects incomplete, stale-payload or under-budget
checklists before promoting the three Quest 2 rows in audio_premerge_qa.csv. Unity rows are never
modified by this importer.
"""
from __future__ import annotations

import argparse
import copy
import csv
import json
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "content/audio/audio_premerge_qa.csv"
DEFAULT_PIN = ROOT / "content/audio/first_playable_artifact_pin.json"
DEFAULT_TEMPLATE = ROOT / "content/audio/quest2_premerge_evidence_template.json"
QUEST_GATES = {
    "quest2_functional_smoke",
    "quest2_mix_listening",
    "quest2_performance_soak",
}
FUNCTIONAL_CHECKS = {
    "beach_day_calm",
    "jungle_day_calm",
    "missing_states_resolve_to_silence",
    "storm_calm_wind_rainfire_signal",
    "shelter_roundtrip",
    "cicada_state_gating",
    "thunder_state_gating",
    "listener_relative_spatial_motion",
    "no_duplicate_emitters_or_coroutines",
    "no_missing_important_cues",
    "no_audible_streaming_stalls",
}
MIX_CHECKS = {
    "shore_wash",
    "thunder_far",
    "environmental_beds",
    "adaptive_storm_music",
    "biome_weather_music_transitions",
    "loop_seams_acceptable",
    "storm_masking_acceptable",
    "no_unacceptable_clipping",
    "no_unacceptable_contamination",
    "spatial_perspective_scale_credible",
}


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"unable to read valid JSON from {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"{path}: expected a JSON object")
    return value


def validate_iso_utc(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SystemExit("Quest evidence: tested_utc is required")
    text = value.strip()
    normalized = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise SystemExit(f"Quest evidence: tested_utc is not valid ISO-8601: {text!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        raise SystemExit("Quest evidence: tested_utc must be UTC (Z/+00:00)")
    return text


def require_nonempty(data: dict, key: str, label: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise SystemExit(f"Quest evidence: {label}.{key} is required")
    return value.strip()


def require_bool_true(data: dict, key: str, label: str) -> None:
    if data.get(key) is not True:
        raise SystemExit(f"Quest evidence: {label}.{key} must be true")


def validate_section(data: object, checks: set[str], label: str) -> dict:
    if not isinstance(data, dict):
        raise SystemExit(f"Quest evidence: {label} must be an object")
    require_bool_true(data, "passed", label)
    for key in sorted(checks):
        require_bool_true(data, key, label)
    return data


def validate_evidence(evidence: dict, pin: dict) -> None:
    if evidence.get("schema_version") != 1:
        raise SystemExit("Quest evidence: schema_version must be 1")
    if evidence.get("device") != "Quest 2":
        raise SystemExit("Quest evidence: device must be exactly 'Quest 2'")
    if evidence.get("profile") != "Q2_BASE":
        raise SystemExit("Quest evidence: profile must be Q2_BASE")
    if evidence.get("artifact_manifest_sha256") != pin.get("manifest_sha256"):
        raise SystemExit("Quest evidence: artifact manifest SHA-256 does not match current pin")
    if evidence.get("artifact_clip_count") != pin.get("clip_count"):
        raise SystemExit("Quest evidence: artifact clip count does not match current pin")
    if evidence.get("artifact_event_count") != pin.get("event_count"):
        raise SystemExit("Quest evidence: artifact event count does not match current pin")

    require_nonempty(evidence, "build_id", "root")
    require_nonempty(evidence, "tester", "root")
    require_nonempty(evidence, "evidence_reference", "root")
    validate_iso_utc(evidence.get("tested_utc"))

    validate_section(evidence.get("functional_smoke"), FUNCTIONAL_CHECKS, "functional_smoke")
    validate_section(evidence.get("mix_listening"), MIX_CHECKS, "mix_listening")

    performance = evidence.get("performance_soak")
    if not isinstance(performance, dict):
        raise SystemExit("Quest evidence: performance_soak must be an object")
    require_bool_true(performance, "passed", "performance_soak")

    duration = performance.get("duration_minutes")
    if not isinstance(duration, (int, float)) or isinstance(duration, bool) or duration < 20:
        raise SystemExit("Quest evidence: performance_soak.duration_minutes must be >= 20")
    if performance.get("target_hz") != 72:
        raise SystemExit("Quest evidence: performance_soak.target_hz must be 72")
    require_bool_true(performance, "sustained_72_hz", "performance_soak")

    stalls = performance.get("audio_streaming_stalls")
    if not isinstance(stalls, int) or isinstance(stalls, bool) or stalls != 0:
        raise SystemExit("Quest evidence: performance_soak.audio_streaming_stalls must be integer 0")
    if performance.get("audio_induced_sustained_frame_regression") is not False:
        raise SystemExit(
            "Quest evidence: performance_soak.audio_induced_sustained_frame_regression must be false"
        )
    if performance.get("material_audio_memory_growth") is not False:
        raise SystemExit("Quest evidence: performance_soak.material_audio_memory_growth must be false")

    voices = performance.get("max_simultaneous_audio_voices")
    if not isinstance(voices, int) or isinstance(voices, bool) or voices <= 0:
        raise SystemExit(
            "Quest evidence: performance_soak.max_simultaneous_audio_voices must be a measured positive integer"
        )
    exception = performance.get("voice_budget_exception")
    if voices > 24 and (not isinstance(exception, str) or not exception.strip()):
        raise SystemExit(
            "Quest evidence: audio voices exceeded the documented <24 target; voice_budget_exception is required"
        )
    require_nonempty(performance, "metrics_reference", "performance_soak")


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
    missing = QUEST_GATES - set(by_id)
    if missing:
        raise SystemExit(f"QA registry: missing Quest gates {sorted(missing)}")

    evidence_ref = (
        "quest2-structured;"
        f"build={evidence['build_id']};"
        f"manifest_sha256={pin['manifest_sha256']};"
        f"clips={pin['clip_count']};events={pin['event_count']};"
        f"utc={evidence['tested_utc']};tester={evidence['tester']};"
        f"evidence={evidence['evidence_reference']}"
    )
    for gate_id in QUEST_GATES:
        row = by_id[gate_id]
        if row.get("required_for_merge", "").strip().lower() != "yes":
            raise SystemExit(f"QA registry: {gate_id} must remain required_for_merge=yes")
        if row.get("category", "").strip() != "quest2":
            raise SystemExit(f"QA registry: {gate_id} category must remain quest2")
        row["status"] = "passed"
        row["evidence"] = evidence_ref

    destination = output or registry
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return destination


def synthetic_evidence(template: dict, pin: dict) -> dict:
    evidence = copy.deepcopy(template)
    evidence["artifact_manifest_sha256"] = pin["manifest_sha256"]
    evidence["artifact_clip_count"] = pin["clip_count"]
    evidence["artifact_event_count"] = pin["event_count"]
    evidence["build_id"] = "synthetic-q2-build"
    evidence["tested_utc"] = "2099-01-01T00:00:00Z"
    evidence["tester"] = "CI synthetic self-test"
    evidence["evidence_reference"] = "synthetic://not-physical-evidence"

    functional = evidence["functional_smoke"]
    functional["passed"] = True
    for key in FUNCTIONAL_CHECKS:
        functional[key] = True

    mix = evidence["mix_listening"]
    mix["passed"] = True
    for key in MIX_CHECKS:
        mix[key] = True

    performance = evidence["performance_soak"]
    performance.update(
        {
            "passed": True,
            "duration_minutes": 20,
            "target_hz": 72,
            "sustained_72_hz": True,
            "audio_streaming_stalls": 0,
            "audio_induced_sustained_frame_regression": False,
            "material_audio_memory_growth": False,
            "max_simultaneous_audio_voices": 23,
            "voice_budget_exception": "",
            "metrics_reference": "synthetic://ovr-metrics",
        }
    )
    return evidence


def expect_rejected(evidence: dict, pin: dict, label: str) -> None:
    try:
        validate_evidence(evidence, pin)
    except SystemExit:
        return
    raise SystemExit(f"self-test failed: {label} Quest evidence was unexpectedly accepted")


def run_self_test(pin: dict, template: dict, registry: Path) -> None:
    evidence = synthetic_evidence(template, pin)
    validate_evidence(evidence, pin)

    stale = copy.deepcopy(evidence)
    stale["artifact_manifest_sha256"] = "0" * 64
    expect_rejected(stale, pin, "stale-manifest")

    short_soak = copy.deepcopy(evidence)
    short_soak["performance_soak"]["duration_minutes"] = 19
    expect_rejected(short_soak, pin, "short-soak")

    over_voice_budget = copy.deepcopy(evidence)
    over_voice_budget["performance_soak"]["max_simultaneous_audio_voices"] = 25
    expect_rejected(over_voice_budget, pin, "voice-budget-without-exception")

    incomplete_mix = copy.deepcopy(evidence)
    incomplete_mix["mix_listening"]["shore_wash"] = False
    expect_rejected(incomplete_mix, pin, "incomplete-mix")

    with tempfile.TemporaryDirectory(prefix="oen-audio-q2-evidence-") as temp:
        target = Path(temp) / "qa.csv"
        shutil.copyfile(registry, target)
        apply_to_registry(target, evidence, pin)
        _, rows = read_registry(target)
        by_id = {row["gate_id"]: row for row in rows}
        for gate_id in QUEST_GATES:
            if by_id[gate_id]["status"] != "passed":
                raise SystemExit(f"self-test failed: {gate_id} was not promoted")
        unity_rows = [row for row in rows if row["category"] == "unity"]
        if not unity_rows or any(row["status"] == "passed" for row in unity_rows):
            raise SystemExit("self-test failed: Unity rows were unexpectedly promoted")

    print(
        "Quest 2 premerge evidence importer self-test OK: pinned complete evidence accepted; stale/short/"
        "over-budget/incomplete evidence rejected; Quest gates promoted only in temp registry; Unity gates untouched."
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--pin", type=Path, default=DEFAULT_PIN)
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    pin = load_json(args.pin)
    template = load_json(args.template)

    if args.self_test:
        run_self_test(pin, template, args.registry)
        return 0

    if args.evidence is None:
        raise SystemExit("--evidence is required unless --self-test is used")
    evidence = load_json(args.evidence)
    validate_evidence(evidence, pin)

    if args.apply:
        destination = apply_to_registry(args.registry, evidence, pin, output=args.output)
        print(f"Quest 2 premerge evidence accepted and applied to: {destination}")
    else:
        print(
            "Quest 2 premerge evidence OK: pinned artifact identity, functional smoke, listening checklist and "
            "20-minute Q2_BASE performance soak all satisfy the structured gate. Read-only validation only; "
            "use --apply to update the QA registry."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
