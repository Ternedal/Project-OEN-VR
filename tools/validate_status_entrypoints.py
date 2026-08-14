#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    "repo_status": ROOT / "repo_status.md",
    "workstream": ROOT / "docs/36_CHATGPT_WORKSTREAM.md",
}

REQUIRED_COMMON = [
    "content/source_inventory.source.json",
    "content/non_unity_capability_matrix.source.json",
    "docs/37_NON_UNITY_GAP_AUDIT.md",
    "issue #3",
    "issue #7",
    "issue #8",
    "implementationAllowed=false",
    "1.012 accepted timer / 439 deferred timer",
]

REQUIRED_PIPELINE_MARKERS = [
    "25-source",
    "source_approval_contract.source.json",
    "derived_master_contract.source.json",
    "9 cues × 3 takes",
    "radio_vo_human_review_contract.source.json",
    "radio_vo_selected_dry_contract.source.json",
    "14 deterministic",
    "music_family_selection_contract.source.json",
    "music_selected_source_contract.source.json",
]

# Avoid broad phrases such as "M-Pre er grøn": those also occur in correct future
# conditions like "M1 starts when M0b + M-Pre are green". Open-gate truth is
# protected by REQUIRED_COMMON, explicit evidence-boundary language, the capability
# matrix validator and the gap-closeout validator. These phrases represent actual
# false completion claims rather than conditional wording.
FORBIDDEN_FALSE_PROGRESS = [
    "source approval er gennemført",
    "derived-master approval er gennemført",
    "radio vo er optaget",
    "music selection er godkendt",
]

REQUIRED_EVIDENCE_BOUNDARIES = {
    "repo_status": [
        "mangler",
        "ingen synthetic/self-test må lukke denne gate",
        "der er fortsat ingen påståede menneskesessioner",
    ],
    "workstream": [
        "mangler",
        "ingen synthetic/self-test lukker gaten",
        "tre faktiske menneskesessioner",
    ],
}


def main() -> int:
    errors: list[str] = []
    texts = {}
    for name, path in FILES.items():
        if not path.is_file():
            errors.append(f"missing status entrypoint: {path.relative_to(ROOT)}")
            continue
        texts[name] = path.read_text(encoding="utf-8")

    for name, text in texts.items():
        low = text.lower()
        for marker in REQUIRED_COMMON:
            if marker.lower() not in low:
                errors.append(f"{name}: missing common status marker {marker!r}")
        for marker in REQUIRED_PIPELINE_MARKERS:
            if marker.lower() not in low:
                errors.append(f"{name}: missing current pipeline marker {marker!r}")
        for marker in REQUIRED_EVIDENCE_BOUNDARIES.get(name, []):
            if marker.lower() not in low:
                errors.append(f"{name}: missing explicit open-evidence marker {marker!r}")
        for marker in FORBIDDEN_FALSE_PROGRESS:
            if marker.lower() in low:
                errors.append(f"{name}: false-progress claim present: {marker!r}")
        if "synthetic" not in low or "human" not in low or "quest" not in low:
            errors.append(f"{name}: evidence-boundary language is incomplete")

    status = texts.get("repo_status", "")
    if "prioritet nu" not in status.lower():
        errors.append("repo_status: missing current priority section")
    workstream = texts.get("workstream", "")
    if "arbejdsregel ved “kør videre”" not in workstream.lower():
        errors.append("workstream: missing explicit kør videre rule")

    backing_paths = [
        "content/non_unity_capability_matrix.source.json",
        "docs/37_NON_UNITY_GAP_AUDIT.md",
        "content/audio/source_approval_contract.source.json",
        "content/audio/derived_master_contract.source.json",
        "content/audio/radio_vo_human_review_contract.source.json",
        "content/audio/radio_vo_selected_dry_contract.source.json",
        "content/audio/music_family_selection_contract.source.json",
        "content/audio/music_selected_source_contract.source.json",
    ]
    for rel in backing_paths:
        if not (ROOT / rel).is_file():
            errors.append(f"missing backing status/contract path: {rel}")

    if errors:
        for error in errors:
            print("ERROR:", error)
        print(f"Status entrypoint validation FAILED: {len(errors)} error(s).")
        return 1

    print("Status entrypoints OK: source/tooling/evidence states separated; current audio/VO/music lanes referenced; real-world gates remain explicit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
