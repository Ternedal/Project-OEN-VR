#!/usr/bin/env python3
"""Validate explicit Project OEN public-domain candidate audit decisions.

The audit is intentionally conservative: a pinned source may be legal and technically valid
without being suitable for a specific runtime event. Passing candidates must exist in the
current environmental build registry. Rejected sources must move back to a real acquisition
lane instead of remaining falsely 'candidate-source-existing'.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIO = ROOT / "content/audio"
AUDIT = AUDIO / "public_domain_candidate_audit.csv"
BUILD = AUDIO / "environment_candidate_build.csv"
BACKLOG = AUDIO / "audio_production_backlog.csv"
SOURCES = AUDIO / "public_domain_environment_sources.csv"

EXPECTED = {
    "SFX_AMB_Shore_Wash": ("waves_pd", 10, "pass-candidate"),
    "SFX_AMB_Ridge_WindBed": ("wind_cc0", 4, "reject-source"),
    "SFX_WTH_Storm_WindGust": ("wind_cc0", 10, "reject-source"),
    "SFX_ENV_Fire_Pop": ("fire_pd", 14, "reject-source"),
}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise SystemExit(f"missing required audit input: {path.relative_to(ROOT)}")
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    audit_rows = read_csv(AUDIT)
    build_rows = read_csv(BUILD)
    backlog_rows = read_csv(BACKLOG)
    source_rows = read_csv(SOURCES)

    if len(audit_rows) != len(EXPECTED):
        raise SystemExit(f"expected {len(EXPECTED)} public-domain audit rows, got {len(audit_rows)}")

    source_keys = {row["source_key"] for row in source_rows}
    audit_by_event: dict[str, dict[str, str]] = {}
    for row in audit_rows:
        event_id = row.get("event_id", "").strip()
        if not event_id or event_id in audit_by_event:
            raise SystemExit(f"blank or duplicate audited event: {event_id!r}")
        audit_by_event[event_id] = row

    if set(audit_by_event) != set(EXPECTED):
        missing = sorted(set(EXPECTED) - set(audit_by_event))
        extra = sorted(set(audit_by_event) - set(EXPECTED))
        raise SystemExit(f"public-domain audit event drift: missing={missing}, extra={extra}")

    built_counts = Counter(row["event_id"].strip() for row in build_rows)
    backlog_by_event = {row["event_id"].strip(): row for row in backlog_rows}

    for event_id, (source_key, target_variations, result) in EXPECTED.items():
        row = audit_by_event[event_id]
        if row.get("source_key", "").strip() != source_key:
            raise SystemExit(f"{event_id}: source_key drift")
        if source_key not in source_keys:
            raise SystemExit(f"{event_id}: source key is not pinned in source registry: {source_key}")
        if int(row.get("target_variations", "0")) != target_variations:
            raise SystemExit(f"{event_id}: target variation drift")
        if row.get("audit_result", "").strip() != result:
            raise SystemExit(f"{event_id}: audit result drift")
        if not row.get("evidence", "").strip():
            raise SystemExit(f"{event_id}: missing audit evidence")

        if result == "pass-candidate":
            if built_counts[event_id] != target_variations:
                raise SystemExit(
                    f"{event_id}: passed audit must build {target_variations} candidates, got {built_counts[event_id]}"
                )
            if event_id in backlog_by_event:
                raise SystemExit(f"{event_id}: produced candidate must not remain in missing-production backlog")
            if row.get("status", "").strip() != "candidate-build-approved":
                raise SystemExit(f"{event_id}: passed audit must be candidate-build-approved")
        else:
            backlog = backlog_by_event.get(event_id)
            if backlog is None:
                raise SystemExit(f"{event_id}: rejected source must remain assigned in production backlog")
            if backlog.get("production_lane", "").strip() != "field-source":
                raise SystemExit(f"{event_id}: rejected source must move to field-source acquisition")
            if backlog.get("status", "").strip() != "source-needed":
                raise SystemExit(f"{event_id}: rejected source must be source-needed")
            if built_counts[event_id] != 0:
                raise SystemExit(f"{event_id}: rejected source must not produce candidate files")
            if row.get("replacement_lane", "").strip() != "field-source":
                raise SystemExit(f"{event_id}: rejected audit must name field-source replacement lane")
            if row.get("status", "").strip() != "new-source-needed":
                raise SystemExit(f"{event_id}: rejected audit must be new-source-needed")

    print(
        "Public-domain candidate audit OK: 1 source accepted for candidate build, "
        "3 source/event pairings rejected and reassigned to field-source acquisition"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
