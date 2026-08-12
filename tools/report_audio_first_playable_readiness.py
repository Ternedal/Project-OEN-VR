#!/usr/bin/env python3
"""Report Project OEN audio first-playable production readiness.

The canonical manifest is the inventory. Authored/environment build registries prove what has
actual generated candidate files; Foley and reviewed-field plans explain known missing lanes.
Everything else remains explicitly unassigned rather than being silently treated as done.
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIO = ROOT / "content/audio"

CANONICAL = AUDIO / "audio_asset_manifest.csv"
AUTHORED = AUDIO / "authored_audio_manifest.csv"
MUSIC = AUDIO / "authored_adaptive_music_manifest.csv"
ENVIRONMENT = AUDIO / "environment_candidate_build.csv"
FOLEY = AUDIO / "foley_recording_plan.csv"
REVIEWED = AUDIO / "reviewed_field_recording_jobs.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise SystemExit(f"missing required readiness input: {path.relative_to(ROOT)}")
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def int_field(row: dict[str, str], key: str, label: str) -> int:
    try:
        value = int(row[key])
    except (KeyError, TypeError, ValueError) as exc:
        raise SystemExit(f"invalid {key!r} in {label}: {row}") from exc
    if value <= 0:
        raise SystemExit(f"non-positive {key!r} in {label}: {row}")
    return value


def ensure_known(events: set[str], canonical: set[str], label: str) -> None:
    unknown = sorted(events - canonical)
    if unknown:
        raise SystemExit(f"{label} references non-canonical events: {', '.join(unknown)}")


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "event_id",
        "category",
        "subcategory",
        "canonical_variations",
        "produced_variations",
        "readiness_lane",
        "upgrade_planned",
        "canonical_status",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(
    path: Path,
    canonical_count: int,
    produced_event_count: int,
    produced_file_count: int,
    lane_counts: Counter[str],
    reviewed_upgrade_events: list[str],
    rows: list[dict[str, str]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    missing = canonical_count - produced_event_count
    lines = [
        "# Project ØEN audio first-playable readiness",
        "",
        f"- Canonical runtime events: **{canonical_count}**",
        f"- Events with actual produced candidate WAVs: **{produced_event_count}**",
        f"- Produced candidate WAV files represented by registries: **{produced_file_count}**",
        f"- Runtime events still without produced WAVs: **{missing}**",
        "",
        "## Readiness lanes",
        "",
        "| Lane | Events |",
        "| --- | ---: |",
    ]
    for lane in sorted(lane_counts):
        lines.append(f"| `{lane}` | {lane_counts[lane]} |")

    lines.extend(["", "## Reviewed-source upgrades to already produced events", ""])
    if reviewed_upgrade_events:
        for event_id in reviewed_upgrade_events:
            lines.append(f"- `{event_id}`")
    else:
        lines.append("- none")

    lines.extend(["", "## Event inventory", "", "| Event | Lane | Produced / canonical variations |", "| --- | --- | ---: |"])
    for row in rows:
        lines.append(
            f"| `{row['event_id']}` | `{row['readiness_lane']}` | "
            f"{row['produced_variations']} / {row['canonical_variations']} |"
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", dest="csv_path", type=Path)
    parser.add_argument("--markdown", dest="markdown_path", type=Path)
    parser.add_argument("--expect-canonical-events", type=int, default=115)
    parser.add_argument("--expect-produced-events", type=int, default=45)
    parser.add_argument("--expect-produced-files", type=int, default=160)
    args = parser.parse_args()

    canonical_rows = read_csv(CANONICAL)
    authored_rows = read_csv(AUTHORED)
    music_rows = read_csv(MUSIC)
    environment_rows = read_csv(ENVIRONMENT)
    foley_rows = read_csv(FOLEY)
    reviewed_rows = read_csv(REVIEWED)

    canonical_order: list[str] = []
    canonical_by_id: dict[str, dict[str, str]] = {}
    for row in canonical_rows:
        event_id = row.get("event_id", "").strip()
        if not event_id:
            raise SystemExit("canonical manifest contains blank event_id")
        if event_id in canonical_by_id:
            raise SystemExit(f"duplicate canonical event_id: {event_id}")
        canonical_order.append(event_id)
        canonical_by_id[event_id] = row

    canonical = set(canonical_by_id)
    if len(canonical) != args.expect_canonical_events:
        raise SystemExit(
            f"expected {args.expect_canonical_events} canonical events, got {len(canonical)}"
        )

    produced_variations: Counter[str] = Counter()
    produced_lane: dict[str, str] = {}

    for row in authored_rows:
        event_id = row["event_id"].strip()
        produced_variations[event_id] += int_field(row, "variations", "authored audio manifest")
        produced_lane[event_id] = "produced-authored"

    for row in music_rows:
        event_id = row["event_id"].strip()
        produced_variations[event_id] += int_field(row, "variations", "adaptive music manifest")
        produced_lane[event_id] = "produced-authored-candidate"

    environment_counts: Counter[str] = Counter()
    for row in environment_rows:
        event_id = row["event_id"].strip()
        environment_counts[event_id] += 1
    for event_id, count in environment_counts.items():
        if event_id in produced_variations:
            raise SystemExit(f"event is produced by multiple first-playable source lanes: {event_id}")
        produced_variations[event_id] = count
        produced_lane[event_id] = "produced-environment-candidate"

    produced = set(produced_variations)
    foley = {row["event_id"].strip() for row in foley_rows if row.get("event_id", "").strip()}
    reviewed = {row["event_id"].strip() for row in reviewed_rows if row.get("event_id", "").strip()}

    ensure_known(produced, canonical, "produced registries")
    ensure_known(foley, canonical, "Foley recording plan")
    ensure_known(reviewed, canonical, "reviewed field-recording jobs")

    produced_files = sum(produced_variations.values())
    if len(produced) != args.expect_produced_events:
        raise SystemExit(
            f"expected {args.expect_produced_events} produced events, got {len(produced)}"
        )
    if produced_files != args.expect_produced_files:
        raise SystemExit(
            f"expected {args.expect_produced_files} produced files, got {produced_files}"
        )

    missing = canonical - produced
    missing_foley = missing & foley
    missing_reviewed = (missing & reviewed) - foley
    missing_unassigned = missing - foley - reviewed
    reviewed_upgrades = sorted(produced & reviewed)

    rows: list[dict[str, str]] = []
    lane_counts: Counter[str] = Counter()
    for event_id in canonical_order:
        canonical_row = canonical_by_id[event_id]
        if event_id in produced:
            lane = produced_lane[event_id]
        elif event_id in missing_foley:
            lane = "missing-foley-recording"
        elif event_id in missing_reviewed:
            lane = "missing-reviewed-field-source"
        else:
            lane = "missing-unassigned-production"

        lane_counts[lane] += 1
        rows.append(
            {
                "event_id": event_id,
                "category": canonical_row.get("category", ""),
                "subcategory": canonical_row.get("subcategory", ""),
                "canonical_variations": canonical_row.get("variations", ""),
                "produced_variations": str(produced_variations.get(event_id, 0)),
                "readiness_lane": lane,
                "upgrade_planned": "yes" if event_id in reviewed_upgrades else "no",
                "canonical_status": canonical_row.get("status", ""),
            }
        )

    if args.csv_path:
        write_csv(args.csv_path, rows)
    if args.markdown_path:
        write_markdown(
            args.markdown_path,
            len(canonical),
            len(produced),
            produced_files,
            lane_counts,
            reviewed_upgrades,
            rows,
        )

    print(
        "Audio first-playable readiness OK: "
        f"{len(produced)}/{len(canonical)} events produced ({produced_files} WAVs); "
        f"missing={len(missing)} [foley={len(missing_foley)}, "
        f"reviewed-field={len(missing_reviewed)}, unassigned={len(missing_unassigned)}]; "
        f"reviewed-upgrades={len(reviewed_upgrades)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
