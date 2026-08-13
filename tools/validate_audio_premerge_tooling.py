#!/usr/bin/env python3
"""Static integrity checks for Project OEN audio pre-merge evidence tooling."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIN = ROOT / "content/audio/first_playable_artifact_pin.json"
QA = ROOT / "content/audio/audio_premerge_qa.csv"
BATCH = ROOT / "src/unity/ProjectOen.Audio.Editor/ProjectOenAudioPremergeBatch.cs"
IMPORTER = ROOT / "tools/import_audio_unity_premerge_evidence.py"
PIN_VERIFIER = ROOT / "tools/verify_first_playable_artifact_pin.py"
WORKFLOW = ROOT / ".github/workflows/audio-validation.yml"
UNITY_GATES = {
    "unity_import_compile",
    "unity_first_playable_audit",
    "unity_active_scene_audit",
}
QUEST_GATES = {
    "quest2_functional_smoke",
    "quest2_mix_listening",
    "quest2_performance_soak",
}
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def require(text: str, token: str, label: str) -> None:
    if token not in text:
        raise SystemExit(f"{label}: missing required token {token!r}")


def main() -> int:
    pin = json.loads(PIN.read_text(encoding="utf-8"))
    if pin.get("schema_version") != 1:
        raise SystemExit("artifact pin schema drift")
    if pin.get("artifact_name") != "oen-unity-first-playable-audio-v1":
        raise SystemExit("artifact pin name drift")
    if pin.get("unity_version") != "6000.4.10f1":
        raise SystemExit("artifact pin Unity version drift")
    if pin.get("clip_count") != 173 or pin.get("event_count") != 47:
        raise SystemExit(
            f"artifact pin coverage drift: expected 173/47, got {pin.get('clip_count')}/{pin.get('event_count')}"
        )
    for key in ("github_artifact_wrapper_sha256", "inner_zip_sha256", "manifest_sha256"):
        if not HEX64.fullmatch(str(pin.get(key, ""))):
            raise SystemExit(f"artifact pin invalid {key}")

    with QA.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    by_id = {row["gate_id"].strip(): row for row in rows}
    if set(by_id) != UNITY_GATES | QUEST_GATES:
        raise SystemExit(
            "premerge QA gate drift: "
            f"expected={sorted(UNITY_GATES | QUEST_GATES)}, actual={sorted(by_id)}"
        )
    for gate_id in UNITY_GATES:
        if by_id[gate_id]["category"] != "unity":
            raise SystemExit(f"{gate_id}: expected category=unity")
    for gate_id in QUEST_GATES:
        if by_id[gate_id]["category"] != "quest2":
            raise SystemExit(f"{gate_id}: expected category=quest2")
    if any(row["required_for_merge"].strip().lower() != "yes" for row in rows):
        raise SystemExit("all audio premerge gates must remain required_for_merge=yes")

    batch = BATCH.read_text(encoding="utf-8")
    for token in (
        "public static class ProjectOenAudioPremergeBatch",
        "public static void Run()",
        'SceneArg = "-oenAudioScene"',
        'EvidenceArg = "-oenAudioEvidence"',
        'ManifestFileName = "FIRST_PLAYABLE_MANIFEST.csv"',
        "ProjectOenAudioFirstPlayableManifestAudit.Audit()",
        "ProjectOenAudioOneClickFirstPlayableBuilder.BuildOneClick()",
        "ProjectOenAudioOneClickFirstPlayableBuilder.AuditOneClick()",
        "ProjectOenAudioSceneInstaller.InstallIntoActiveScene()",
        "ProjectOenAudioSceneInstaller.AuditActiveScene()",
        "GameObjectUtility.GetMonoBehavioursWithMissingScriptCount",
        'gateId = "unity_import_compile"',
        'gateId = "unity_first_playable_audit"',
        'gateId = "unity_active_scene_audit"',
        "JsonUtility.ToJson(evidence, true)",
        "EditorApplication.Exit(exitCode)",
    ):
        require(batch, token, "Unity premerge batch runner")
    if "EditorSceneManager.SaveScene" in batch:
        raise SystemExit("Unity premerge batch runner must not save the target gameplay scene")

    importer = IMPORTER.read_text(encoding="utf-8")
    for token in (
        'pin["unity_version"]',
        'pin["manifest_sha256"]',
        'pin["clip_count"]',
        'pin["event_count"]',
        'evidence.get("missingScriptCount") != 0',
        'evidence.get("errorCount") != len(errors)',
        'evidence.get("warningCount") != len(warnings)',
        'if errors:',
        "set(gates) != UNITY_GATES",
        'row["status"] = "passed"',
        "quest_rows",
        "expect_rejected(stale_manifest",
        "expect_rejected(errored",
        "expect_rejected(missing_gate",
        "--self-test",
        "--apply",
    ):
        require(importer, token, "Unity premerge evidence importer")

    verifier = PIN_VERIFIER.read_text(encoding="utf-8")
    for token in (
        'DEFAULT_ZIP = ROOT / "build/oen-unity-first-playable-audio-v1.zip"',
        'expected_zip_sha = pin.get("inner_zip_sha256")',
        'expected_manifest_sha = pin.get("manifest_sha256")',
        'clip_count != pin.get("clip_count")',
        'event_count != pin.get("event_count")',
        "Re-verify the new payload physically before updating the pin",
    ):
        require(verifier, token, "first-playable artifact pin verifier")

    workflow = WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "python tools/validate_audio_premerge_tooling.py",
        "python tools/import_audio_unity_premerge_evidence.py --self-test",
        "python tools/verify_first_playable_artifact_pin.py",
        "Stage Unity first-playable audio pack",
        "Verify staged Unity pack against committed QA pin",
        "Upload Unity first-playable audio pack",
    ):
        require(workflow, token, "Audio Validation premerge enforcement")
    if workflow.index("Stage Unity first-playable audio pack") > workflow.index(
        "Verify staged Unity pack against committed QA pin"
    ):
        raise SystemExit("Audio Validation must stage the Unity pack before verifying its pin")
    if workflow.index("Verify staged Unity pack against committed QA pin") > workflow.index(
        "Upload Unity first-playable audio pack"
    ):
        raise SystemExit("Audio Validation must verify the pin before uploading the Unity artifact")

    print(
        "Audio premerge tooling OK: pinned 173/47 payload, six-gate registry, Unity batch evidence runner, "
        "hardened manifest-bound importer, Quest-gate isolation and post-staging pin enforcement"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
