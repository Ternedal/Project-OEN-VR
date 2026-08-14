#!/usr/bin/env python3
from __future__ import annotations

from audio_derived_master_support import CONTRACT, ROOT, SOURCE_APPROVAL_CONTRACT, DerivedError, load_json


def main() -> int:
    try:
        derived = load_json(ROOT / CONTRACT)
        source = load_json(ROOT / SOURCE_APPROVAL_CONTRACT)
    except DerivedError as exc:
        print("ERROR:", exc)
        return 1
    errors = []
    if derived.get("version") != 1 or derived.get("status") != "derived-master-intake-review-tooling-ready-no-master-approved":
        errors.append("derived master contract version/status drift")
    if derived.get("sourceApprovedReceipt", {}).get("requiredStatus") != "source-approved-original-materialized-from-human-gate":
        errors.append("derived input must remain explicit source-approved receipt")
    submission = derived.get("submission", {})
    if submission.get("status") != "derived-master-submission-unvalidated" or "editRecipe" not in submission.get("requiredPerMaster", []):
        errors.append("derived submission must require explicit editRecipe")
    if "no edit is needed" not in submission.get("editRecipeRule", "").lower():
        errors.append("no-edit sources must not be relabelled as derived masters")
    technical = derived.get("technicalIntake", {})
    if (
        technical.get("passStatus") != "derived-master-technical-intake-passed-not-listening-approved"
        or technical.get("sampleRateHz") != 48000
        or technical.get("bitDepth") != 24
        or technical.get("channelsAllowed") != [1, 2]
        or technical.get("codec") != "integer PCM WAV"
        or technical.get("fullScaleSampleCountMax") != 0
        or technical.get("derivedShaMustDifferFromSourceSha") is not True
    ):
        errors.append("derived technical 48k/24-bit/no-full-scale/new-identity contract drift")
    human = derived.get("humanReview", {})
    if human.get("normalizedStatus") != "human-derived-master-review-evidence-evaluated-not-materialized":
        errors.append("derived human normalized status must remain explicitly unmaterialized")
    if human.get("typedChecksSource") != SOURCE_APPROVAL_CONTRACT.as_posix():
        errors.append("derived human review must reuse typed source-approval checks")
    if set(source.get("typedChecks", {})) != {"CONTAMINATION","MATERIAL_MATCH","LOOP_OR_SLICE","NOISE_FLOOR","TRANSIENT_QUALITY","SPACE_IDENTITY","VARIATION_VALUE","SPEECH_SPACE"}:
        errors.append("source typed check set drift")
    if source.get("typedChecks", {}).get("MATERIAL_MATCH", {}).get("approvalMin") != 3:
        errors.append("derived material-match threshold depends on source approvalMin=3")
    eligibility = set(derived.get("derivedMasterApprovedEligibilityRequires", []))
    for rule in ("reviewerAlias is non-empty", "reviewedAt is non-empty", "MATERIAL_MATCH >= 3"):
        if rule not in eligibility:
            errors.append(f"derived approval eligibility missing: {rule}")
    materialization = derived.get("materialization", {})
    if (
        materialization.get("receiptStatus") != "derived-master-approved-materialized-from-human-gate"
        or materialization.get("copyOnly") is not True
        or materialization.get("sourceAndOutputShaMustMatch") is not True
        or materialization.get("overwriteRequiresExplicitReplace") is not True
    ):
        errors.append("derived approval materialization must remain explicit exact-byte copy gate")
    rules = " | ".join(derived.get("rules", [])).lower()
    if "does not imply unity-integrated" not in rules or "human review" not in rules:
        errors.append("derived runtime/listening boundary guardrail missing")
    if errors:
        for error in errors:
            print("ERROR:", error)
        return 1
    print("Derived master contract OK: source-approved binding, explicit edit recipe, 48k/24-bit PCM technical intake, repeated typed human listening with reviewer identity, exact-byte approval materialization only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
