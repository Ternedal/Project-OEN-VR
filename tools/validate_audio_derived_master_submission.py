#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from audio_derived_master_support import ROOT, DerivedError, validate_technical_submission


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate PROJECT OEN derived audio masters against source-approved provenance and technical format rules.")
    parser.add_argument("--submission", type=Path, required=True)
    parser.add_argument("--source-approved-receipt", type=Path, required=True)
    parser.add_argument("--masters-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        receipt = validate_technical_submission(args.submission.resolve(), args.source_approved_receipt.resolve(), args.masters_dir.resolve(), ROOT)
    except DerivedError as exc:
        print(f"ERROR: {exc}")
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Derived master technical intake OK: {receipt['validatedMasterCount']} master(s); status={receipt['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
