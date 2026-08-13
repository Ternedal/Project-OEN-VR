#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
BATCH = ROOT / "src/unity/ProjectOen.Art/Editor/ProductionArtBatchVerification.cs"
REVIEW = ROOT / "prototype/m0b-bootstrap/Review-ProductionArt.ps1"
RUNBOOK = ROOT / "prototype/m0b-bootstrap/RUNBOOK.md"

errors = []
for path in (BATCH, REVIEW, RUNBOOK):
    if not path.exists():
        errors.append(f"missing: {path.relative_to(ROOT)}")

if errors:
    print("FAILED")
    for error in errors:
        print(" - " + error)
    sys.exit(1)

print("PASS: one-shot Unity review files are present.")
