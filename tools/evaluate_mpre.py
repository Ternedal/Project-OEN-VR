#!/usr/bin/env python3
"""Evaluate PROJECT OEN M-Pre human-playtest gate from anonymous CSV data.

Expected CSV columns:
session_id,pair_id,day1_seconds,day2_seconds,day3_seconds,disagreement_days,
administration_observed,changed_mind_count,regret_after_storm,human_session,
gift_recipient_used

The script never creates evidence. It only validates and evaluates supplied human data.
A valid RED result exits 0; incomplete/invalid input exits 2.
"""
from __future__ import annotations

import argparse
import csv
import statistics
import sys
from pathlib import Path

REQUIRED_COLUMNS = {
    "session_id",
    "pair_id",
    "day1_seconds",
    "day2_seconds",
    "day3_seconds",
    "disagreement_days",
    "administration_observed",
    "changed_mind_count",
    "regret_after_storm",
    "human_session",
    "gift_recipient_used",
}


def parse_bool(value: str, field: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes", "ja"}:
        return True
    if normalized in {"false", "0", "no", "nej"}:
        return False
    raise ValueError(f"{field}: expected boolean, got {value!r}")


def parse_nonnegative_int(value: str, field: str) -> int:
    number = int(value)
    if number < 0:
        raise ValueError(f"{field}: must be >= 0")
    return number


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - fields
        if missing:
            raise ValueError(f"missing columns: {', '.join(sorted(missing))}")
        return list(reader)


def evaluate(path: Path) -> tuple[str, list[dict]]:
    rows = load_rows(path)
    if len(rows) != 3:
        raise ValueError(f"expected exactly 3 sessions, found {len(rows)}")

    session_ids: set[str] = set()
    pair_ids: set[str] = set()
    results: list[dict] = []

    for row in rows:
        session_id = row["session_id"].strip()
        pair_id = row["pair_id"].strip()
        if not session_id:
            raise ValueError("session_id cannot be empty")
        if session_id in session_ids:
            raise ValueError(f"duplicate session_id: {session_id}")
        session_ids.add(session_id)
        if not pair_id:
            raise ValueError(f"{session_id}: pair_id cannot be empty")
        pair_ids.add(pair_id)

        human_session = parse_bool(row["human_session"], f"{session_id}.human_session")
        gift_recipient_used = parse_bool(row["gift_recipient_used"], f"{session_id}.gift_recipient_used")
        if not human_session:
            raise ValueError(f"{session_id}: data is not marked as a human session")
        if gift_recipient_used:
            raise ValueError(f"{session_id}: gift recipient cannot be used for M-Pre")

        day_seconds = [
            parse_nonnegative_int(row["day1_seconds"], f"{session_id}.day1_seconds"),
            parse_nonnegative_int(row["day2_seconds"], f"{session_id}.day2_seconds"),
            parse_nonnegative_int(row["day3_seconds"], f"{session_id}.day3_seconds"),
        ]
        median_seconds = float(statistics.median(day_seconds))
        disagreement_days = parse_nonnegative_int(row["disagreement_days"], f"{session_id}.disagreement_days")
        changed_mind_count = parse_nonnegative_int(row["changed_mind_count"], f"{session_id}.changed_mind_count")
        administration_observed = parse_bool(row["administration_observed"], f"{session_id}.administration_observed")
        regret_after_storm = parse_bool(row["regret_after_storm"], f"{session_id}.regret_after_storm")

        session_green = median_seconds >= 45.0 and disagreement_days >= 1 and not administration_observed
        results.append({
            "session_id": session_id,
            "pair_id": pair_id,
            "median_seconds": median_seconds,
            "disagreement_days": disagreement_days,
            "changed_mind_count": changed_mind_count,
            "regret_after_storm": regret_after_storm,
            "administration_observed": administration_observed,
            "green": session_green,
        })

    if len(pair_ids) < 2:
        raise ValueError("M-Pre requires at least 2 different pairs across the 3 sessions")

    green_count = sum(1 for item in results if item["green"])
    return ("GREEN" if green_count >= 2 else "RED"), results


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate M-Pre gate from anonymous human-session CSV data.")
    parser.add_argument("csv_path", type=Path)
    args = parser.parse_args()

    try:
        gate, results = evaluate(args.csv_path)
    except (OSError, ValueError) as exc:
        print(f"M-PRE INPUT INVALID: {exc}", file=sys.stderr)
        return 2

    for item in results:
        print(
            f"{item['session_id']}: median={item['median_seconds']:.0f}s "
            f"disagreement_days={item['disagreement_days']} "
            f"administration={'yes' if item['administration_observed'] else 'no'} "
            f"changed_mind={item['changed_mind_count']} "
            f"regret={'yes' if item['regret_after_storm'] else 'no'} "
            f"=> {'GREEN' if item['green'] else 'RED'}"
        )
    print(f"M-PRE GATE: {gate} ({sum(1 for item in results if item['green'])}/3 green sessions)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
