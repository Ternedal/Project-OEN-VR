#!/usr/bin/env python3
"""Static QA for source-stamped on-machine Unity art verification."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VERIFY = ROOT / "prototype/m0b-bootstrap/Verify-ProductionArt.ps1"
RUNBOOK = ROOT / "prototype/m0b-bootstrap/RUNBOOK.md"
GITIGNORE = ROOT / ".gitignore"

VERIFY_REQUIRED = (
    'git -C $repo rev-parse HEAD',
    'git -C $repo rev-parse --abbrev-ref HEAD',
    'git -C $repo status --porcelain -- @trackedScope',
    '$sourceSha -notmatch',
    '$sourceBranch -eq "HEAD"',
    'Assets/ProjectOEN/ProductionArt',
    'src/unity/ProjectOen.Art',
    'prototype/m0b-bootstrap/Review-ProductionArt.ps1',
    'prototype/m0b-bootstrap/Verify-ProductionArt.ps1',
    '& $reviewScript -UnityPath $UnityPath -ProjectPath $ProjectPath -OneShot',
    '$report.status -ne "PASS"',
    '[int]$report.failed -ne 0',
    'sourceBranch',
    'sourceSha',
    'sourceWorktreeClean',
    'sourceStampedUtc',
    'sourceStampTool',
    'ConvertTo-Json -Depth 10',
    'source-stemplet verification-rapport bestod ikke round-trip kontrol',
)

RUNBOOK_REQUIRED = (
    '.\\Verify-ProductionArt.ps1',
    'sourceBranch',
    'sourceSha',
    'sourceWorktreeClean',
    'review-art-verification.json',
    'Debug fallback',
)

GITIGNORE_REQUIRED = (
    'prototype/m0b-bootstrap/review-art-*.log',
    'prototype/m0b-bootstrap/review-art-verification.json',
)


def read(path: Path, label: str, errors: list[str]) -> str:
    if not path.exists():
        errors.append(f"missing {label}: {path.relative_to(ROOT)}")
        return ""
    return path.read_text(encoding="utf-8")


def require(text: str, tokens: tuple[str, ...], label: str, errors: list[str]) -> None:
    for token in tokens:
        if token not in text:
            errors.append(f"{label} missing contract token: {token}")


def main() -> int:
    errors: list[str] = []
    verify = read(VERIFY, "source-stamped verification wrapper", errors)
    runbook = read(RUNBOOK, "M0b runbook", errors)
    gitignore = read(GITIGNORE, ".gitignore", errors)

    require(verify, VERIFY_REQUIRED, "verification wrapper", errors)
    require(runbook, RUNBOOK_REQUIRED, "runbook", errors)
    require(gitignore, GITIGNORE_REQUIRED, ".gitignore", errors)

    lower = verify.lower()
    for forbidden in (
        "git commit",
        "git add",
        "git reset",
        "git clean",
        "git stash",
        "git checkout",
        "git switch",
        "git restore",
    ):
        if forbidden in lower:
            errors.append(f"verification wrapper must stay Git-read-only; forbidden token: {forbidden}")

    if verify.count('Add-Member -NotePropertyName sourceSha') != 1:
        errors.append("verification wrapper must stamp sourceSha exactly once")
    if verify.count('Add-Member -NotePropertyName sourceBranch') != 1:
        errors.append("verification wrapper must stamp sourceBranch exactly once")
    if 'if ($dirty.Count -gt 0)' not in verify:
        errors.append("verification wrapper must hard-fail a dirty scoped worktree")
    if '$roundTrip.sourceSha -ne $sourceSha.ToLowerInvariant()' not in verify:
        errors.append("verification wrapper must round-trip verify the stamped SHA")
    if '$roundTrip.sourceBranch -ne $sourceBranch' not in verify:
        errors.append("verification wrapper must round-trip verify the stamped branch")

    print("Project ØEN source-stamped Unity verification QA")
    print("  source identity : named branch + 40-char commit SHA")
    print("  worktree        : production-art scope must be clean")
    print("  JSON stamp      : branch / SHA / clean / UTC / stamp tool")
    print("  round-trip      : stamped branch + SHA + clean flag re-read")
    print("  local output    : logs/report are gitignored")

    if errors:
        print(f"\nFAILED with {len(errors)} issue(s):")
        for error in errors:
            print(" - " + error)
        return 1

    print("\nPASS: physical Unity verification reports are source-identifiable at repo level.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
