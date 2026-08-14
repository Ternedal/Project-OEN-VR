#!/usr/bin/env python3
"""Validate Project OEN field-source discovery without pretending candidates are mastered.

This gate sits before reviewed-field-recording ingest. It guarantees that every event still
assigned to the field-source lane has at least one source-page-verified, redistributable
candidate with enough metadata to acquire the canonical original. It deliberately does NOT
mark any source or job ready: original download, listening review and SHA-256 pinning remain
separate mandatory gates.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
AUDIO = ROOT / "content/audio"
BACKLOG = AUDIO / "audio_production_backlog.csv"
PLAN = AUDIO / "field_source_acquisition_plan.csv"

ALLOWED_LICENSES = {"CC0", "CC0-1.0", "Public-Domain"}
ACTIVE_STATUSES = {"primary-page-verified", "secondary-page-verified"}
PRIMARY_STATUS = "primary-page-verified"
ALLOWED_RANKS = {"primary", "secondary"}
BED_EVENTS = {
    "SFX_AMB_Beach_CoastalWind",
    "SFX_AMB_Beach_PalmCanopy",
    "SFX_AMB_Jungle_CanopyWind",
    "SFX_AMB_Jungle_DeepBed",
    "SFX_AMB_Ridge_WindBed",
    "SFX_WTH_Storm_RoughOcean",
}
MIN_BED_SOURCE_SECONDS = 120.0
REQUIRED_COLUMNS = {
    "event_id",
    "target_variations",
    "candidate_key",
    "source_page_url",
    "creator",
    "title",
    "license",
    "source_format",
    "sample_rate_hz",
    "bit_depth",
    "channels",
    "duration_seconds",
    "rank",
    "screening_status",
    "risk_flags",
    "review_action",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise SystemExit(f"missing required input: {path.relative_to(ROOT)}")
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise SystemExit(f"{path.relative_to(ROOT)}: missing CSV header")
        missing = REQUIRED_COLUMNS.difference(reader.fieldnames) if path == PLAN else set()
        if missing:
            raise SystemExit(f"{path.relative_to(ROOT)}: missing columns: {', '.join(sorted(missing))}")
        return list(reader)


def positive_int(value: str, label: str) -> int:
    try:
        result = int(value)
    except ValueError as exc:
        raise SystemExit(f"{label}: expected integer, got {value!r}") from exc
    if result <= 0:
        raise SystemExit(f"{label}: must be > 0")
    return result


def positive_float(value: str, label: str) -> float:
    try:
        result = float(value)
    except ValueError as exc:
        raise SystemExit(f"{label}: expected number, got {value!r}") from exc
    if result <= 0:
        raise SystemExit(f"{label}: must be > 0")
    return result


def main() -> int:
    backlog_rows = read_csv(BACKLOG)
    plan_rows = read_csv(PLAN)

    field_backlog: dict[str, dict[str, str]] = {}
    for row in backlog_rows:
        if row.get("production_lane", "").strip() != "field-source":
            continue
        event_id = row.get("event_id", "").strip()
        if not event_id or event_id in field_backlog:
            raise SystemExit(f"blank or duplicate field-source backlog event: {event_id!r}")
        if row.get("status", "").strip() != "source-needed":
            raise SystemExit(f"{event_id}: field-source backlog must remain source-needed until reviewed ingest is ready")
        field_backlog[event_id] = row

    if not field_backlog:
        raise SystemExit("no field-source backlog events found; remove this gate only after the lane is intentionally retired")

    by_event: dict[str, list[dict[str, str]]] = defaultdict(list)
    candidate_keys: set[str] = set()
    for row_number, row in enumerate(plan_rows, start=2):
        event_id = row.get("event_id", "").strip()
        candidate_key = row.get("candidate_key", "").strip()
        label = f"{PLAN.relative_to(ROOT)}:{row_number}"

        if event_id not in field_backlog:
            raise SystemExit(f"{label}: candidate references event not in current field-source backlog: {event_id!r}")
        if not candidate_key or candidate_key in candidate_keys:
            raise SystemExit(f"{label}: blank or duplicate candidate_key: {candidate_key!r}")
        candidate_keys.add(candidate_key)

        target = positive_int(row.get("target_variations", ""), f"{candidate_key}: target_variations")
        backlog_target = positive_int(field_backlog[event_id].get("target_variations", ""), f"{event_id}: backlog target")
        if target != backlog_target:
            raise SystemExit(f"{candidate_key}: target variation drift; plan={target}, backlog={backlog_target}")

        status = row.get("screening_status", "").strip()
        rank = row.get("rank", "").strip()
        if status not in ACTIVE_STATUSES:
            raise SystemExit(f"{candidate_key}: unsupported screening_status={status!r}")
        if rank not in ALLOWED_RANKS:
            raise SystemExit(f"{candidate_key}: unsupported rank={rank!r}")
        if (rank == "primary") != (status == PRIMARY_STATUS):
            raise SystemExit(f"{candidate_key}: primary rank/status must agree")

        license_name = row.get("license", "").strip()
        if license_name not in ALLOWED_LICENSES:
            raise SystemExit(f"{candidate_key}: unsupported license {license_name!r}")

        parsed = urlparse(row.get("source_page_url", "").strip())
        if parsed.scheme != "https" or parsed.netloc not in {"freesound.org", "www.freesound.org"}:
            raise SystemExit(f"{candidate_key}: source_page_url must be a canonical HTTPS Freesound page")

        for field in ("creator", "title", "source_format", "channels", "risk_flags", "review_action"):
            if not row.get(field, "").strip():
                raise SystemExit(f"{candidate_key}: missing {field}")

        positive_int(row.get("sample_rate_hz", ""), f"{candidate_key}: sample_rate_hz")
        bit_depth_raw = row.get("bit_depth", "").strip()
        try:
            bit_depth = int(bit_depth_raw)
        except ValueError as exc:
            raise SystemExit(f"{candidate_key}: bit_depth must be an integer (0 allowed only when source has no PCM bit depth)") from exc
        if bit_depth < 0:
            raise SystemExit(f"{candidate_key}: bit_depth must be >= 0")
        duration = positive_float(row.get("duration_seconds", ""), f"{candidate_key}: duration_seconds")
        if event_id in BED_EVENTS and status == PRIMARY_STATUS and duration < MIN_BED_SOURCE_SECONDS:
            raise SystemExit(
                f"{candidate_key}: primary bed candidate is only {duration:.3f}s; minimum discovery threshold is {MIN_BED_SOURCE_SECONDS:.0f}s"
            )

        by_event[event_id].append(row)

    plan_events = set(by_event)
    backlog_events = set(field_backlog)
    if plan_events != backlog_events:
        missing = sorted(backlog_events - plan_events)
        extra = sorted(plan_events - backlog_events)
        raise SystemExit(f"field-source acquisition coverage drift: missing={missing}, extra={extra}")

    for event_id in sorted(backlog_events):
        rows = by_event[event_id]
        if not any(row["screening_status"].strip() == PRIMARY_STATUS for row in rows):
            raise SystemExit(f"{event_id}: requires at least one primary source-page-verified candidate")
        if not all("download" in row["review_action"].lower() for row in rows):
            raise SystemExit(f"{event_id}: every candidate review_action must preserve canonical-original download as the next gate")

    primary_count = sum(1 for row in plan_rows if row["screening_status"].strip() == PRIMARY_STATUS)
    print(
        "Field-source acquisition plan OK: "
        f"{len(backlog_events)} backlog events covered by {len(plan_rows)} page-verified candidates "
        f"({primary_count} primary). Originals remain blocked on manual download, listening review and SHA-256 pinning."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
