#!/usr/bin/env python3
"""Report whether Project OEN audio has reached its intentional PR merge boundary.

Automated software/audio-build gates run before this reporter in Audio Validation. The remaining
merge blockers are physical Unity/Quest acceptance gates stored in audio_premerge_qa.csv.
Missing full-production Foley/field-source events are reported separately: they remain explicit
post-first-playable production work rather than being silently confused with software readiness.

Use --strict after recording physical evidence. It returns non-zero until every required merge
gate is passed with structured evidence bound to the current pinned first-playable payload.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIO = ROOT / "content/audio"
QA = AUDIO / "audio_premerge_qa.csv"
PIN = AUDIO / "first_playable_artifact_pin.json"
BACKLOG = AUDIO / "audio_production_backlog.csv"
FOLEY = AUDIO / "foley_recording_plan.csv"
SUPPLEMENTAL = AUDIO / "supplemental_foley_recording_plan.csv"

EXPECTED_GATES = {
    "unity_import_compile",
    "unity_first_playable_audit",
    "unity_active_scene_audit",
    "quest2_functional_smoke",
    "quest2_mix_listening",
    "quest2_performance_soak",
}
ALLOWED_STATUSES = {"pending-physical", "passed", "failed"}
REQUIRED_COLUMNS = {
    "gate_id",
    "category",
    "required_for_merge",
    "status",
    "evidence",
    "acceptance",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise SystemExit(f"missing required merge-readiness input: {path.relative_to(ROOT)}")
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise SystemExit(f"{path.relative_to(ROOT)}: missing CSV header")
        return list(reader)


def read_pin() -> dict:
    if not PIN.is_file():
        raise SystemExit(f"missing required merge-readiness input: {PIN.relative_to(ROOT)}")
    try:
        value = json.loads(PIN.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{PIN.relative_to(ROOT)}: invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"{PIN.relative_to(ROOT)}: expected JSON object")
    for key in ("manifest_sha256", "clip_count", "event_count", "unity_version"):
        if key not in value:
            raise SystemExit(f"{PIN.relative_to(ROOT)}: missing {key}")
    return value


def int_field(row: dict[str, str], key: str, label: str) -> int:
    try:
        value = int(row.get(key, ""))
    except ValueError as exc:
        raise SystemExit(f"{label}: invalid integer {key}={row.get(key)!r}") from exc
    if value <= 0:
        raise SystemExit(f"{label}: {key} must be > 0")
    return value


def require_passed_evidence(gate_id: str, category: str, evidence: str, pin: dict) -> None:
    manifest_token = f"manifest_sha256={pin['manifest_sha256']}"
    clip_token = f"clips={pin['clip_count']}"
    event_token = f"events={pin['event_count']}"

    if category == "unity":
        required = (
            "unity-batch;",
            f"unity={pin['unity_version']}",
            manifest_token,
            clip_token,
            event_token,
            "utc=",
            "scene=Assets/",
        )
    elif category == "quest2":
        required = (
            "quest2-structured;",
            "build=",
            manifest_token,
            clip_token,
            event_token,
            "utc=",
            "tester=",
            "evidence=",
        )
    else:
        raise SystemExit(f"{gate_id}: unsupported evidence category {category!r}")

    missing = [token for token in required if token not in evidence]
    if missing:
        raise SystemExit(
            f"{gate_id}: passed evidence is not structured/current-payload evidence; "
            f"missing markers={missing}. Use the category evidence importer instead of editing the CSV pass manually."
        )


def validate_qa(rows: list[dict[str, str]], pin: dict) -> list[dict[str, str]]:
    if not rows:
        raise SystemExit("audio pre-merge QA registry must not be empty")
    missing_columns = REQUIRED_COLUMNS.difference(rows[0])
    if missing_columns:
        raise SystemExit(
            "audio pre-merge QA registry missing columns: " + ", ".join(sorted(missing_columns))
        )

    by_id: dict[str, dict[str, str]] = {}
    for row in rows:
        gate_id = row.get("gate_id", "").strip()
        if not gate_id or gate_id in by_id:
            raise SystemExit(f"blank or duplicate pre-merge gate_id: {gate_id!r}")
        by_id[gate_id] = row

        if row.get("required_for_merge", "").strip().lower() != "yes":
            raise SystemExit(f"{gate_id}: all rows in audio_premerge_qa.csv must be required_for_merge=yes")

        category = row.get("category", "").strip()
        if category not in {"unity", "quest2"}:
            raise SystemExit(f"{gate_id}: unsupported merge-gate category {category!r}")

        status = row.get("status", "").strip()
        if status not in ALLOWED_STATUSES:
            raise SystemExit(f"{gate_id}: unsupported status {status!r}")
        evidence = row.get("evidence", "").strip()
        if status in {"passed", "failed"} and not evidence:
            raise SystemExit(f"{gate_id}: status={status} requires concrete evidence")
        if status == "passed":
            require_passed_evidence(gate_id, category, evidence, pin)
        if not row.get("acceptance", "").strip():
            raise SystemExit(f"{gate_id}: acceptance criteria must not be blank")

    actual = set(by_id)
    if actual != EXPECTED_GATES:
        raise SystemExit(
            "audio pre-merge gate drift: "
            f"missing={sorted(EXPECTED_GATES - actual)}, extra={sorted(actual - EXPECTED_GATES)}"
        )

    return [by_id[gate_id] for gate_id in sorted(EXPECTED_GATES)]


def production_backlog_summary() -> tuple[int, int, int, int, int]:
    backlog = read_csv(BACKLOG)
    field_source_events = {
        row.get("event_id", "").strip()
        for row in backlog
        if row.get("production_lane", "").strip() == "field-source"
        and row.get("event_id", "").strip()
    }

    foley = read_csv(FOLEY)
    supplemental = read_csv(SUPPLEMENTAL)
    foley_events = {row.get("event_id", "").strip() for row in foley if row.get("event_id", "").strip()}
    supplemental_events = {
        row.get("event_id", "").strip()
        for row in supplemental
        if row.get("event_id", "").strip()
    }
    foley_variations = sum(int_field(row, "variations", "main Foley") for row in foley)
    supplemental_variations = sum(
        int_field(row, "variations", "supplemental Foley") for row in supplemental
    )
    return (
        len(field_source_events),
        len(foley_events),
        foley_variations,
        len(supplemental_events),
        supplemental_variations,
    )


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["gate_id", "category", "status", "evidence", "acceptance"],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "gate_id": row["gate_id"],
                    "category": row["category"],
                    "status": row["status"],
                    "evidence": row["evidence"],
                    "acceptance": row["acceptance"],
                }
            )


def write_markdown(
    path: Path,
    rows: list[dict[str, str]],
    field_source_events: int,
    foley_events: int,
    foley_variations: int,
    supplemental_events: int,
    supplemental_variations: int,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    passed = [row for row in rows if row["status"] == "passed"]
    failed = [row for row in rows if row["status"] == "failed"]
    pending = [row for row in rows if row["status"] == "pending-physical"]
    merge_ready = len(passed) == len(rows) and not failed and not pending
    state = "MERGE-GATE-SATISFIED" if merge_ready else "PHYSICAL-QA-BLOCKED"

    lines = [
        "# Project ØEN audio merge readiness",
        "",
        f"**State: `{state}`**",
        "",
        "This report is generated after the automated audio validators in the Audio Validation workflow. "
        "The rows below are the deliberately physical gates for this first-playable audio PR. A passed row "
        "must contain structured evidence bound to the current pinned first-playable payload.",
        "",
        f"- Required physical gates: **{len(rows)}**",
        f"- Passed with evidence: **{len(passed)}**",
        f"- Pending physical execution: **{len(pending)}**",
        f"- Failed with evidence: **{len(failed)}**",
        "",
        "| Gate | Category | Status | Evidence |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        evidence = row["evidence"].strip() or "—"
        lines.append(
            f"| `{row['gate_id']}` | `{row['category']}` | `{row['status']}` | {evidence} |"
        )

    lines.extend(["", "## Acceptance criteria", ""])
    for row in rows:
        lines.append(f"- `{row['gate_id']}` — {row['acceptance']}")

    lines.extend(
        [
            "",
            "## Explicit full-production backlog (not hidden merge-readiness debt)",
            "",
            f"- Field-source acquisition lane: **{field_source_events} events** still require real originals/listening/SHA pinning before those events become produced.",
            f"- Main Foley plan: **{foley_events} events / {foley_variations} selected variations** still require physical recording/editing.",
            f"- Supplemental Foley plan: **{supplemental_events} events / {supplemental_variations} selected variations** still require physical recording/editing.",
            "",
            "Those production lanes remain explicit in readiness/backlog registries. They do not masquerade as completed assets. "
            "This first-playable PR is merge-blocked by the six physical Unity/Quest gates above, not by pretending the later full-production recording backlog is already complete.",
            "",
            "Run `python tools/report_audio_merge_readiness.py --strict` only after importing structured evidence for every physical gate. "
            "Strict mode exits non-zero until all six rows are `passed` with current-payload evidence.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", dest="csv_path", type=Path)
    parser.add_argument("--markdown", dest="markdown_path", type=Path)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    pin = read_pin()
    rows = validate_qa(read_csv(QA), pin)
    field_source_events, foley_events, foley_variations, supplemental_events, supplemental_variations = (
        production_backlog_summary()
    )

    if args.csv_path:
        write_csv(args.csv_path, rows)
    if args.markdown_path:
        write_markdown(
            args.markdown_path,
            rows,
            field_source_events,
            foley_events,
            foley_variations,
            supplemental_events,
            supplemental_variations,
        )

    passed = sum(row["status"] == "passed" for row in rows)
    pending = sum(row["status"] == "pending-physical" for row in rows)
    failed = sum(row["status"] == "failed" for row in rows)
    merge_ready = passed == len(rows) and pending == 0 and failed == 0

    print(
        "Audio merge readiness: "
        f"physical-gates={len(rows)} [passed={passed}, pending={pending}, failed={failed}]; "
        f"state={'MERGE-GATE-SATISFIED' if merge_ready else 'PHYSICAL-QA-BLOCKED'}; "
        f"post-first-playable-production=[field-source={field_source_events}, "
        f"main-foley={foley_events}/{foley_variations}, "
        f"supplemental-foley={supplemental_events}/{supplemental_variations}]"
    )

    if args.strict and not merge_ready:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
