#!/usr/bin/env python3
"""Human-readable report for portable runtime-mesh dimensions."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "content" / "items" / "runtime_mesh_scale_specs.json"


def main() -> int:
    payload = json.loads(SPEC.read_text(encoding="utf-8"))
    entries = [entry for entry in payload["entries"] if entry["scale_class"] != "authored_world_scale"]
    print(f"{'mesh':<72} {'class':<20} {'target':>8}")
    print("-" * 104)
    for entry in entries:
        print(f"{entry['path']:<72} {entry['scale_class']:<20} {entry['target_longest_m']:>7.3f}m")
    print(f"\n{len(entries)} portable variants; max readability oversize ratio: 1.35x")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
