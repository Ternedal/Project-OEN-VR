#!/usr/bin/env python3
"""Stage Project OEN audio artifacts into a Unity-ready Assets/ProjectOen/Audio tree.

The input packs stay independent production artifacts. This tool combines their WAVs into
one deterministic first-playable ZIP whose folder tokens drive the Unity AudioImporter
postprocessor and whose filenames can be mapped directly to AudioEventId.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import re
import shutil
import zipfile
from pathlib import Path

AUDIO_ROOT = Path("Assets/ProjectOen/Audio")
CLIP_RE = re.compile(r"^(?P<event>.+)_(?P<variation>\d{2})\.wav$", re.IGNORECASE)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def deterministic_zip(root: Path, zip_path: Path) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(p for p in root.rglob("*") if p.is_file()):
            rel = path.relative_to(root).as_posix()
            info = zipfile.ZipInfo(rel)
            info.date_time = (1980, 1, 1, 0, 0, 0)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, path.read_bytes())


def parse_clip(path: Path) -> tuple[str, int]:
    match = CLIP_RE.match(path.name)
    if not match:
        raise SystemExit(f"non-canonical WAV filename: {path}")
    return match.group("event"), int(match.group("variation"))


def authored_landing(event_id: str) -> Path:
    if event_id.startswith("SFX_UI_"):
        return AUDIO_ROOT / "2D/OneShots/UI"
    if event_id.startswith("SFX_STS_"):
        return AUDIO_ROOT / "2D/OneShots/Status"
    if event_id.startswith("SFX_INT_"):
        return AUDIO_ROOT / "2D/OneShots/Interaction"
    if event_id.startswith("SFX_CRF_"):
        return AUDIO_ROOT / "2D/OneShots/Crafting"
    if event_id.startswith("STG_"):
        return AUDIO_ROOT / "2D/Compressed/Stinger"
    if event_id.startswith("MUS_"):
        if event_id == "MUS_Finale_Success":
            return AUDIO_ROOT / "2D/Compressed/Music"
        return AUDIO_ROOT / "2D/Streaming/Music"
    raise SystemExit(f"no authored Unity landing rule for {event_id}")


def environment_landing(relative: Path, event_id: str) -> Path:
    parts = relative.parts
    if parts and parts[0] in {"2D", "Spatial"}:
        return AUDIO_ROOT / relative.parent

    if event_id.startswith("SFX_AMB_"):
        return AUDIO_ROOT / "2D/Streaming/Ambience"
    if event_id.startswith("SFX_NAT_"):
        return AUDIO_ROOT / "Spatial/OneShots/Nature"
    if event_id in {"SFX_ENV_Fire_Idle", "SFX_ENV_Fire_Low"}:
        return AUDIO_ROOT / "Spatial/Streaming/Environment"
    if event_id.startswith("SFX_ENV_"):
        return AUDIO_ROOT / "Spatial/OneShots/Environment"
    if event_id in {
        "SFX_WTH_Rain_Light",
        "SFX_WTH_Rain_Heavy",
        "SFX_WTH_Rain_OnTarp",
        "SFX_WTH_Storm_Wind",
        "SFX_WTH_Storm_RoughOcean",
    }:
        return AUDIO_ROOT / "2D/Streaming/Weather"
    if event_id.startswith("SFX_WTH_"):
        return AUDIO_ROOT / "Spatial/OneShots/Weather"
    raise SystemExit(f"no environmental Unity landing rule for {event_id}")


def copy_pack(
    source_root: Path,
    output_root: Path,
    pack_name: str,
    environment: bool,
    rows: list[dict[str, str]],
    destinations: set[str],
) -> None:
    if not source_root.is_dir():
        raise SystemExit(f"missing input pack directory: {source_root}")

    wavs = sorted(source_root.rglob("*.wav"))
    if not wavs:
        raise SystemExit(f"input pack has no WAV files: {source_root}")

    for source in wavs:
        event_id, variation = parse_clip(source)
        relative = source.relative_to(source_root)
        landing_dir = environment_landing(relative, event_id) if environment else authored_landing(event_id)
        destination_rel = landing_dir / source.name
        destination_key = destination_rel.as_posix()
        if destination_key in destinations:
            raise SystemExit(f"duplicate staged destination: {destination_key}")
        destinations.add(destination_key)

        destination = output_root / destination_rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)

        rows.append(
            {
                "event_id": event_id,
                "variation": f"{variation:02d}",
                "source_pack": pack_name,
                "unity_path": destination_rel.as_posix(),
                "sha256": sha256(destination),
                "bytes": str(destination.stat().st_size),
            }
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ui-status", type=Path, required=True)
    parser.add_argument("--gameplay-stingers", type=Path, required=True)
    parser.add_argument("--adaptive-music", type=Path, required=True)
    parser.add_argument("--environment", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("build/oen-unity-first-playable-audio-v1"))
    parser.add_argument("--zip", dest="zip_path", type=Path)
    parser.add_argument("--expect-files", type=int, default=163)
    parser.add_argument("--expect-events", type=int, default=46)
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()

    if args.clean:
        shutil.rmtree(args.output, ignore_errors=True)
    args.output.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, str]] = []
    destinations: set[str] = set()
    copy_pack(args.ui_status, args.output, "oen-authored-ui-status-v1", False, rows, destinations)
    copy_pack(args.gameplay_stingers, args.output, "oen-authored-gameplay-stingers-v1", False, rows, destinations)
    copy_pack(args.adaptive_music, args.output, "oen-authored-adaptive-music-v1", False, rows, destinations)
    copy_pack(args.environment, args.output, "oen-public-domain-environment-v0", True, rows, destinations)

    rows.sort(key=lambda row: (row["event_id"], int(row["variation"]), row["unity_path"]))
    events = {row["event_id"] for row in rows}

    if len(rows) != args.expect_files:
        raise SystemExit(f"expected {args.expect_files} staged WAVs, got {len(rows)}")
    if len(events) != args.expect_events:
        raise SystemExit(f"expected {args.expect_events} populated events, got {len(events)}")

    manifest = args.output / "FIRST_PLAYABLE_MANIFEST.csv"
    with manifest.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["event_id", "variation", "source_pack", "unity_path", "sha256", "bytes"],
        )
        writer.writeheader()
        writer.writerows(rows)

    (args.output / "README.txt").write_text(
        "Project OEN Unity first-playable audio pack v1\n\n"
        "Extract this ZIP at the Unity project root so the included Assets/ProjectOen/Audio tree lands in Assets.\n"
        "Save/open the target gameplay scene, then run: Project Oen > Audio > Build + Install First Playable (One Click).\n"
        "The command verifies 163 canonical clips / 46 events before creating definitions, catalog, baseline profiles and AudioRuntime_FirstPlayable.prefab, then installs exactly one generated runtime instance into the active scene.\n"
        "Scene installation refuses Prefab Mode, unsaved scenes, duplicate AudioService ownership and stale/incomplete audio imports.\n"
        "WorldFauna binds to exactly one active AudioListener; otherwise it stays disabled rather than emitting from a wrong world position.\n"
        "The first WorldFauna lane is Jungle Day cicadas, active only outdoors during Calm, with randomized 14-34 second cadence around the listener-relative anchor.\n"
        "The scene is marked dirty but never auto-saved. Existing designer tuning and generated runtime/profile assets are preserved on reruns.\n"
        "Unavailable Night/Ridge/Camp/Shelter ambience resolves to an explicit empty fallback rather than stale or unrelated audio.\n"
        "Distant-thunder candidates are included from the SHA256-pinned Public Domain Tonitrus recording and still require headset/listening approval.\n"
        "Lower-level build/install/audit commands remain available for manual production integration.\n"
        "Environmental and adaptive-music material remains candidate-headset-listen until physical listening QA.\n",
        encoding="utf-8",
    )

    if args.zip_path:
        deterministic_zip(args.output, args.zip_path)

    print(
        f"Unity first-playable audio staging OK: {len(rows)} WAV files across "
        f"{len(events)} events under {AUDIO_ROOT.as_posix()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
