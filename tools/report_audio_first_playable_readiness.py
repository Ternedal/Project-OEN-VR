#!/usr/bin/env python3
"""Report Project OEN audio first-playable production readiness.

The canonical manifest is the inventory. Authored/environment build registries prove what has
actual generated candidate files; main Foley, supplemental Foley, reviewed-field and source
backlog registries explain every known missing lane. No runtime event is allowed to remain
silently unassigned.

The production manifest still carries two historical status labels. They are canonicalized here
to the stable runtime names without rewriting the source manifest, because Unity/runtime IDs and
new authored assets use Injury/ColdWet while old manifest rows remain compatibility data.
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIO = ROOT / "content/audio"

CANONICAL = AUDIO / "audio_asset_manifest.csv"
AUTHORED = AUDIO / "authored_audio_manifest.csv"
MUSIC = AUDIO / "authored_adaptive_music_manifest.csv"
ENVIRONMENT = AUDIO / "environment_candidate_build.csv"
FOLEY = AUDIO / "foley_recording_plan.csv"
SUPPLEMENTAL_FOLEY = AUDIO / "supplemental_foley_recording_plan.csv"
REVIEWED = AUDIO / "reviewed_field_recording_jobs.csv"
BACKLOG = AUDIO / "audio_production_backlog.csv"

LEGACY_EVENT_ALIASES = {
    "SFX_STS_Hunger_Warn": "SFX_STS_Injury_Warn",
    "SFX_STS_Thirst_Warn": "SFX_STS_ColdWet_Warn",
}


def canonicalize_event_id(event_id: str) -> str:
    cleaned = event_id.strip()
    return LEGACY_EVENT_ALIASES.get(cleaned, cleaned)


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
        "manifest_event_id",
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
        "- Missing runtime events without an explicit production lane: **0**",
        "",
        "Historical manifest labels `SFX_STS_Hunger_Warn` and `SFX_STS_Thirst_Warn` are reported "
        "as canonical runtime `SFX_STS_Injury_Warn` and `SFX_STS_ColdWet_Warn`; the source manifest "
        "is intentionally not rewritten by this report.",
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

    lines.extend([
        "",
        "## Event inventory",
        "",
        "| Event | Lane | Produced / canonical variations |",
        "| --- | --- | ---: |",
    ])
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
    parser.add_argument("--expect-produced-events", type=int, default=47)
    parser.add_argument("--expect-produced-files", type=int, default=173)
    parser.add_argument("--expect-main-foley-events", type=int, default=40)
    parser.add_argument("--expect-supplemental-foley-events", type=int, default=13)
    parser.add_argument("--expect-backlog-events", type=int, default=11)
    args = parser.parse_args()

    canonical_rows = read_csv(CANONICAL)
    authored_rows = read_csv(AUTHORED)
    music_rows = read_csv(MUSIC)
    environment_rows = read_csv(ENVIRONMENT)
    foley_rows = read_csv(FOLEY)
    supplemental_foley_rows = read_csv(SUPPLEMENTAL_FOLEY)
    reviewed_rows = read_csv(REVIEWED)
    backlog_rows = read_csv(BACKLOG)

    canonical_order: list[str] = []
    canonical_by_id: dict[str, dict[str, str]] = {}
    manifest_event_id_by_canonical: dict[str, str] = {}
    for row in canonical_rows:
        manifest_event_id = row.get("event_id", "").strip()
        if not manifest_event_id:
            raise SystemExit("canonical manifest contains blank event_id")
        event_id = canonicalize_event_id(manifest_event_id)
        if event_id in canonical_by_id:
            raise SystemExit(
                f"duplicate canonical event_id after alias normalization: {event_id} "
                f"(latest manifest label {manifest_event_id})"
            )
        canonical_order.append(event_id)
        canonical_by_id[event_id] = row
        manifest_event_id_by_canonical[event_id] = manifest_event_id

    canonical = set(canonical_by_id)
    if len(canonical) != args.expect_canonical_events:
        raise SystemExit(
            f"expected {args.expect_canonical_events} canonical events, got {len(canonical)}"
        )

    produced_variations: Counter[str] = Counter()
    produced_lane: dict[str, str] = {}

    for row in authored_rows:
        event_id = canonicalize_event_id(row["event_id"])
        produced_variations[event_id] += int_field(row, "variations", "authored audio manifest")
        produced_lane[event_id] = "produced-authored"

    for row in music_rows:
        event_id = canonicalize_event_id(row["event_id"])
        produced_variations[event_id] += int_field(row, "variations", "adaptive music manifest")
        produced_lane[event_id] = "produced-authored-candidate"

    environment_counts: Counter[str] = Counter()
    for row in environment_rows:
        event_id = canonicalize_event_id(row["event_id"])
        environment_counts[event_id] += 1
    for event_id, count in environment_counts.items():
        if event_id in produced_variations:
            raise SystemExit(f"event is produced by multiple first-playable source lanes: {event_id}")
        produced_variations[event_id] = count
        produced_lane[event_id] = "produced-environment-candidate"

    produced = set(produced_variations)
    foley = {
        canonicalize_event_id(row["event_id"])
        for row in foley_rows
        if row.get("event_id", "").strip()
    }
    supplemental_foley = {
        canonicalize_event_id(row["event_id"])
        for row in supplemental_foley_rows
        if row.get("event_id", "").strip()
    }
    reviewed = {
        canonicalize_event_id(row["event_id"])
        for row in reviewed_rows
        if row.get("event_id", "").strip()
    }

    backlog_lane: dict[str, str] = {}
    for row in backlog_rows:
        event_id = canonicalize_event_id(row.get("event_id", ""))
        if not event_id:
            raise SystemExit("audio production backlog contains blank event_id")
        if event_id in backlog_lane:
            raise SystemExit(f"duplicate audio production backlog event: {event_id}")
        production_lane = row.get("production_lane", "").strip()
        if production_lane not in {"field-source", "public-domain-candidate"}:
            raise SystemExit(f"invalid production_lane for {event_id}: {production_lane!r}")
        target_variations = int_field(row, "target_variations", "audio production backlog")
        canonical_variations = int_field(canonical_by_id.get(event_id, {}), "variations", f"canonical event {event_id}")
        if target_variations != canonical_variations:
            raise SystemExit(
                f"backlog target variation mismatch for {event_id}: "
                f"{target_variations} != canonical {canonical_variations}"
            )
        if not row.get("source_strategy", "").strip() or not row.get("acceptance", "").strip():
            raise SystemExit(f"backlog event lacks source strategy/acceptance: {event_id}")
        backlog_lane[event_id] = production_lane

    backlog = set(backlog_lane)
    ensure_known(produced, canonical, "produced registries")
    ensure_known(foley, canonical, "main Foley recording plan")
    ensure_known(supplemental_foley, canonical, "supplemental Foley recording plan")
    ensure_known(reviewed, canonical, "reviewed field-recording jobs")
    ensure_known(backlog, canonical, "audio production backlog")

    if len(foley) != args.expect_main_foley_events:
        raise SystemExit(f"expected {args.expect_main_foley_events} main Foley events, got {len(foley)}")
    if len(supplemental_foley) != args.expect_supplemental_foley_events:
        raise SystemExit(
            f"expected {args.expect_supplemental_foley_events} supplemental Foley events, "
            f"got {len(supplemental_foley)}"
        )
    if len(backlog) != args.expect_backlog_events:
        raise SystemExit(f"expected {args.expect_backlog_events} backlog events, got {len(backlog)}")

    produced_files = sum(produced_variations.values())
    if len(produced) != args.expect_produced_events:
        raise SystemExit(
            f"expected {args.expect_produced_events} produced events, got {len(produced)}"
        )
    if produced_files != args.expect_produced_files:
        raise SystemExit(
            f"expected {args.expect_produced_files} produced files, got {produced_files}"
        )

    lane_sets = {
        "produced": produced,
        "main-foley": foley,
        "supplemental-foley": supplemental_foley,
        "reviewed": reviewed - produced,
        "backlog": backlog,
    }
    lane_names = list(lane_sets)
    overlaps: set[str] = set()
    for i, left in enumerate(lane_names):
        for right in lane_names[i + 1:]:
            overlaps.update(lane_sets[left] & lane_sets[right])
    if overlaps:
        raise SystemExit(
            "audio readiness missing-production lanes overlap: " + ", ".join(sorted(overlaps))
        )

    missing = canonical - produced
    missing_foley = missing & foley
    missing_supplemental_foley = missing & supplemental_foley
    missing_reviewed = (missing & reviewed) - foley - supplemental_foley
    missing_backlog = missing & backlog
    reviewed_upgrades = sorted(produced & reviewed)

    unassigned = missing - foley - supplemental_foley - reviewed - backlog
    unexpected_backlog = backlog - missing
    if unassigned or unexpected_backlog:
        details = []
        if unassigned:
            details.append("unassigned=" + ",".join(sorted(unassigned)))
        if unexpected_backlog:
            details.append("backlog-not-missing=" + ",".join(sorted(unexpected_backlog)))
        raise SystemExit("audio readiness lane coverage mismatch: " + "; ".join(details))

    rows: list[dict[str, str]] = []
    lane_counts: Counter[str] = Counter()
    for event_id in canonical_order:
        canonical_row = canonical_by_id[event_id]
        if event_id in produced:
            lane = produced_lane[event_id]
        elif event_id in missing_foley:
            lane = "missing-foley-recording"
        elif event_id in missing_supplemental_foley:
            lane = "missing-supplemental-foley-recording"
        elif event_id in missing_reviewed:
            lane = "missing-reviewed-field-source"
        elif event_id in missing_backlog:
            lane = "missing-" + backlog_lane[event_id]
        else:
            raise SystemExit(f"internal readiness classification gap: {event_id}")

        lane_counts[lane] += 1
        rows.append(
            {
                "event_id": event_id,
                "manifest_event_id": manifest_event_id_by_canonical[event_id],
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

    backlog_counts = Counter(backlog_lane.values())
    print(
        "Audio first-playable readiness OK: "
        f"{len(produced)}/{len(canonical)} events produced ({produced_files} WAVs); "
        f"missing={len(missing)} [main-foley={len(missing_foley)}, "
        f"supplemental-foley={len(missing_supplemental_foley)}, "
        f"reviewed-field={len(missing_reviewed)}, backlog={len(missing_backlog)}: "
        f"field-source={backlog_counts['field-source']}, "
        f"public-domain={backlog_counts['public-domain-candidate']}]; "
        f"unassigned={len(unassigned)}; reviewed-upgrades={len(reviewed_upgrades)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
