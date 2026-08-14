#!/usr/bin/env python3
from __future__ import annotations

from audio_source_approval_support import APPROVAL_CONTRACT, LISTENING_QA, MATERIALIZE_CONTRACT, ROOT, ApprovalError, current_source_context, load_json


def main() -> int:
    try:
        approval = load_json(ROOT / APPROVAL_CONTRACT)
        materialize = load_json(ROOT / MATERIALIZE_CONTRACT)
        listening = load_json(ROOT / LISTENING_QA)
        sources = current_source_context(ROOT)
    except ApprovalError as exc:
        print("ERROR:", exc)
        return 1
    errors = []
    expected_ids = [x.get("id") for x in listening.get("requiredListeningChecks", []) if isinstance(x, dict)]
    if set(expected_ids) != set(approval.get("typedChecks", {})) or len(expected_ids) != 8:
        errors.append("typed source approval checks must exactly match the eight listening-QA check IDs")
    descriptions = {x.get("id"): x.get("result", "") for x in listening.get("requiredListeningChecks", []) if isinstance(x, dict)}
    for check_id in ("MATERIAL_MATCH", "VARIATION_VALUE"):
        spec = approval.get("typedChecks", {}).get(check_id, {})
        if spec.get("type") != "rating" or spec.get("min") != 1 or spec.get("max") != 5 or "1-5" not in descriptions.get(check_id, ""):
            errors.append(f"{check_id}: typed 1-5 rating contract drift")
    material = approval.get("typedChecks", {}).get("MATERIAL_MATCH", {})
    if material.get("approvalMin") != 3:
        errors.append("MATERIAL_MATCH approval threshold must remain >=3")
    approval_rules = " | ".join(listening.get("approvalRule", {}).get("sourceApprovedRequires", [])).lower()
    if "material match >= 3" not in approval_rules or "license evidence preserved" not in approval_rules or "sha-256 preserved" not in approval_rules:
        errors.append("typed gate no longer matches listening-QA sourceApprovedRequires")
    eligibility = set(approval.get("sourceApprovedEligibilityRequires", []))
    for identity_rule in ("reviewerAlias is non-empty", "reviewedAt is non-empty"):
        if identity_rule not in eligibility:
            errors.append(f"source approval eligibility must require human review identity: {identity_rule}")
    upstream = approval.get("upstreamEvidence", {})
    if upstream.get("normalizedStatus") != listening.get("reviewEvidence", {}).get("normalizedStatus"):
        errors.append("typed approval upstream status must match preliminary human-review normalizer output")
    if upstream.get("acceptedKinds") != ["main-acquired-originals", "extension-source-selection", "field-backlog-source-selection"]:
        errors.append("typed approval upstream review kinds drift")
    if materialize.get("input", {}).get("status") != approval.get("normalizedStatus"):
        errors.append("source-approved materializer input must match typed approval normalizer output")
    m = materialize.get("materialization", {})
    if m.get("copyOnly") is not True or m.get("preserveSourceBytes") is not True or m.get("sourceAndOutputShaMustMatch") is not True:
        errors.append("source-approved materialization must remain exact-byte copy only")
    main_count = sum(1 for x in sources.values() if x["reviewKind"] == "main-acquired-originals")
    ext_count = sum(1 for x in sources.values() if x["reviewKind"] == "extension-source-selection")
    field_count = sum(1 for x in sources.values() if x["reviewKind"] == "field-backlog-source-selection")
    if (main_count, ext_count, field_count, len(sources)) != (3, 15, 7, 25):
        errors.append(f"current audition source context drift: main={main_count}, extension={ext_count}, field={field_count}, total={len(sources)}")
    if errors:
        for error in errors:
            print("ERROR:", error)
        return 1
    print("Audio source approval contract OK: 25 current sources, typed 1-5 gate aligned to sourceApprovedRequires, reviewer identity/timestamp required, exact-byte explicit promotion only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
