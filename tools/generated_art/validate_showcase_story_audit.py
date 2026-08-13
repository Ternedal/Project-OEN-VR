#!/usr/bin/env python3
"""Static contract for imported Stormnatten camp/signal story auditing.

The builder-specific gates prove authored source intent. This gate makes sure the
main Unity showcase audit independently re-checks the saved/imported scene:
exact roots/children, canonical prefab variants, bounded placement, zero runtime
cost components and per-story triangle/material budgets.
"""
from __future__ import annotations

import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EDITOR = ROOT / "src" / "unity" / "ProjectOen.Art" / "Editor"
AUDIT = EDITOR / "ProductionArtShowcaseAudit.cs"
CAMP = EDITOR / "ProductionArtStormCampStoryBuilder.cs"
SIGNAL = EDITOR / "ProductionArtSignalFinaleStoryBuilder.cs"
WORKFLOW = ROOT / ".github" / "workflows" / "generate-project-oen-art.yml"

SPEC_RE = re.compile(
    r'new StorySpec\("([^"]+)",\s*"([^"]+)",\s*"([^"]+)",\s*'
    r'new Vector3\(([-0-9.]+)f,\s*([-0-9.]+)f,\s*([-0-9.]+)f\)',
    re.MULTILINE,
)
AUDIT_SPEC_RE = re.compile(
    r'new StoryAuditSpec\("([^"]+)",\s*"([^"]+)",\s*"([^"]+)"\)'
)

CAMP_CENTER = (-1.00, 0.75)
CAMP_RADIUS = 3.10
SIGNAL_CENTER = (5.40, 5.80)
SIGNAL_RADIUS = 2.45

AUDIT_REQUIRED = (
    'using UnityEngine.SceneManagement;',
    'CampStoryRootName = "Storm Camp Micro Story"',
    'CampStoryExpectedCount = 9',
    'CampStoryTriangleHardLimit = 60000',
    'CampStoryMaterialSlotHardLimit = 36',
    'CampStoryMaxRadius = 3.10f',
    'SignalStoryRootName = "Signal Finale Micro Story"',
    'SignalStoryExpectedCount = 8',
    'SignalStoryTriangleHardLimit = 50000',
    'SignalStoryMaterialSlotHardLimit = 32',
    'SignalStoryMaxRadius = 2.45f',
    'AuditStoryLayer(',
    'SceneManager.GetActiveScene()',
    'activeScene.GetRootGameObjects()',
    'root.transform.childCount != expectedCount',
    'root.GetComponentsInChildren<Collider>(true).Length',
    'root.GetComponentsInChildren<Rigidbody>(true).Length',
    'root.GetComponentsInChildren<ParticleSystem>(true).Length',
    'root.GetComponentsInChildren<Light>(true).Length',
    'root.GetComponentsInChildren<Animation>(true).Length',
    'root.GetComponentsInChildren<Animator>(true).Length',
    'filter.sharedMesh.triangles.LongLength / 3L',
    'skin.sharedMesh.triangles.LongLength / 3L',
    'renderer.sharedMaterials == null ? 0 : renderer.sharedMaterials.Length',
    'Vector2.Distance(',
    'PrefabUtility.GetPrefabAssetPathOfNearestInstanceRoot(child.gameObject)',
    'wrong canonical prefab on',
    'runtimeCost=',
)

WORKFLOW_REQUIRED = (
    '- name: Validate imported Stormnatten story audit contract',
    'run: python tools/generated_art/validate_showcase_story_audit.py',
)


def load(path: Path, label: str, errors: list[str]) -> str:
    if not path.exists():
        errors.append(f"missing {label}: {path.relative_to(ROOT)}")
        return ""
    return path.read_text(encoding="utf-8")


def parse_builder_specs(text: str) -> list[tuple[str, str, str, float, float, float]]:
    specs = []
    for match in SPEC_RE.finditer(text):
        name, prefix, token, x, y, z = match.groups()
        specs.append((name, prefix, token, float(x), float(y), float(z)))
    return specs


def parse_audit_specs(text: str) -> list[tuple[str, str, str]]:
    return [tuple(match.groups()) for match in AUDIT_SPEC_RE.finditer(text)]


def check_radius(
    specs: list[tuple[str, str, str, float, float, float]],
    center: tuple[float, float],
    radius: float,
    label: str,
    errors: list[str],
) -> None:
    for name, _prefix, _token, x, _y, z in specs:
        distance = math.dist((x, z), center)
        if distance > radius + 1e-6:
            errors.append(
                f"{label} authored prop outside {radius:.2f}m audit radius: "
                f"{name} at {distance:.3f}m"
            )


def main() -> int:
    errors: list[str] = []
    audit = load(AUDIT, "Stormnatten showcase audit", errors)
    camp = load(CAMP, "camp story builder", errors)
    signal = load(SIGNAL, "signal finale story builder", errors)
    workflow = load(WORKFLOW, "art workflow", errors)

    for token in AUDIT_REQUIRED:
        if audit and token not in audit:
            errors.append(f"showcase audit missing imported-story contract: {token}")
    for token in WORKFLOW_REQUIRED:
        if workflow and token not in workflow:
            errors.append(f"art workflow missing imported-story audit gate: {token}")

    for forbidden in (
        'ProductionArtStormCampStoryBuilder.BuildIntoShowcase',
        'ProductionArtSignalFinaleStoryBuilder.BuildIntoShowcase',
        'EditorSceneManager.SaveScene',
        'AssetDatabase.SaveAssets',
        'BuildPipeline.BuildPlayer',
    ):
        if audit and forbidden in audit:
            errors.append(f"showcase audit must stay read-only; forbidden token: {forbidden}")

    camp_specs = parse_builder_specs(camp)
    signal_specs = parse_builder_specs(signal)
    audit_specs = parse_audit_specs(audit)

    if len(camp_specs) != 9:
        errors.append(f"expected 9 authored camp story specs, found {len(camp_specs)}")
    if len(signal_specs) != 8:
        errors.append(f"expected 8 authored signal story specs, found {len(signal_specs)}")
    if len(audit_specs) != 17:
        errors.append(f"expected 17 imported-story audit expectations, found {len(audit_specs)}")

    expected = [(name, prefix, token) for name, prefix, token, *_ in camp_specs + signal_specs]
    if audit_specs != expected:
        errors.append("showcase audit story expectations drifted from builder canonical specs/order")

    check_radius(camp_specs, CAMP_CENTER, CAMP_RADIUS, "camp story", errors)
    check_radius(signal_specs, SIGNAL_CENTER, SIGNAL_RADIUS, "signal story", errors)

    if audit and audit.count('AuditStoryLayer(') != 3:
        errors.append("showcase audit must define AuditStoryLayer once and invoke it exactly twice")
    if audit and 'roots.Length != 1' not in audit:
        errors.append("showcase audit must require exactly one top-level root per story")
    if audit and 'expectations.Length != expectedCount' not in audit:
        errors.append("showcase audit must self-check expectation-count drift")
    if audit and 'hardFailures.Add(label + " object outside "' not in audit:
        errors.append("showcase audit must hard-fail story props outside their bounded radius")

    print("Project ØEN imported Stormnatten story audit QA")
    print("  camp story      : 9 exact canonical children / <=60k triangles / <=36 material slots / <=3.10m")
    print("  signal finale   : 8 exact canonical children / <=50k triangles / <=32 material slots / <=2.45m")
    print("  runtime cost    : 0 colliders / rigidbodies / particles / lights / Animation / Animator")
    print("  imported scene  : main Unity showcase audit re-checks saved prefab sources and positions")

    if errors:
        print(f"\nFAILED with {len(errors)} issue(s):")
        for error in errors:
            print(" - " + error)
        return 1

    print("\nPASS: imported Stormnatten story layers are explicitly covered by the read-only Unity showcase audit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
