#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "docs/37_NON_UNITY_GAP_AUDIT.md"

DELIVERABLES = {
    "N-002": "docs/38_SOURCE_ASSET_MANIFEST.md",
    "N-003": "docs/39_AUDIO_CUE_MANIFEST.md",
    "N-004": "docs/40_UX_COPY_AND_LOCALIZATION_CATALOG.md",
    "N-005": "docs/41_PERSONALIZATION_PACKAGE_SPEC.md",
    "N-006": "docs/42_HUMAN_QA_PLAYTEST_PACK.md",
    "N-007": "docs/43_IP_AND_ASSET_PROVENANCE.md",
    "N-008": "docs/44_CONTENT_COVERAGE_MATRIX.md",
    "N-010": "docs/45_GIFT_EXPERIENCE_AND_RELEASE_FLOW.md",
}

INTERACTIONS = [
    "design/interactions/PLANNING_TABLE.md",
    "design/interactions/SHELTER_REINFORCEMENT.md",
    "design/interactions/FIRE_START.md",
    "design/interactions/RAVINE_RESCUE.md",
    "design/interactions/STORM_FINALE.md",
]

REQUIRED_STATUS_PATHS = [
    "content/source_inventory.source.json",
    "content/non_unity_capability_matrix.source.json",
    "repo_status.md",
]


def main() -> int:
    errors: list[str] = []
    text = AUDIT.read_text(encoding="utf-8")

    for item_id, rel in DELIVERABLES.items():
        if not (ROOT / rel).is_file():
            errors.append(f"{item_id}: missing delivered file {rel}")
        if item_id not in text or rel not in text:
            errors.append(f"{item_id}: closeout audit does not bind delivered file {rel}")

    for rel in INTERACTIONS:
        if not (ROOT / rel).is_file():
            errors.append(f"N-009: missing interaction brief {rel}")
        elif rel not in text and Path(rel).name not in text:
            errors.append(f"N-009: closeout audit does not mention {rel}")

    finale_path = ROOT / "design/interactions/STORM_FINALE.md"
    if finale_path.is_file():
        finale = finale_path.read_text(encoding="utf-8")
        for marker in ("Phase 1", "Phase 2", "Phase 3", "Phase 4", "Phase 5", "signal frame"):
            if marker.lower() not in finale.lower():
                errors.append(f"N-009: STORM_FINALE missing coverage marker {marker!r}")

    for rel in REQUIRED_STATUS_PATHS:
        if not (ROOT / rel).is_file():
            errors.append(f"missing authoritative status path {rel}")
        elif rel not in text:
            errors.append(f"closeout audit does not reference authoritative status path {rel}")

    required_open_gate_markers = [
        "issue #3",
        "issue #7",
        "issue #8",
        "implementationAllowed=false",
        "1.012 accepted timer / 439 deferred timer",
        "AI/simulation må ikke erstatte",
        "human audio evidence",
        "Unity/Quest physical QA",
    ]
    for marker in required_open_gate_markers:
        if marker.lower() not in text.lower():
            errors.append(f"closeout audit missing open-gate marker: {marker}")

    stale_claims = [
        "Source asset manifest mangler",
        "Audio cue/source manifest mangler",
        "UX-copy og localization source catalog mangler",
        "Content coverage er fragmenteret",
        "Gave-/releaseoplevelsen er teknisk beskrevet, men ikke produktmæssigt",
    ]
    for claim in stale_claims:
        if claim.lower() in text.lower():
            errors.append(f"stale gap claim reintroduced: {claim}")

    if errors:
        for error in errors:
            print("ERROR:", error)
        print(f"Non-Unity gap closeout FAILED: {len(errors)} error(s).")
        return 1

    print("Non-Unity gap closeout OK: N-002..N-010 deliverables backed by files; interaction coverage present; real-world gates remain explicit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
