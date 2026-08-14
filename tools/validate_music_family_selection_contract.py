#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from music_family_selection_support import MATERIALIZE_CONTRACT, ROOT, SELECTION_CONTRACT, SelectionError, audit_context, load_json


def main() -> int:
    try:
        context = audit_context(ROOT)
        selection = load_json(ROOT / SELECTION_CONTRACT)
        materialize = load_json(ROOT / MATERIALIZE_CONTRACT)
    except SelectionError as exc:
        print("ERROR:", exc)
        return 1
    errors = []
    if selection.get("version") != 1 or selection.get("status") != "family-selection-tooling-ready-not-selected":
        errors.append("family selection contract version/status drift")
    if selection.get("input", {}).get("status") != "human-music-audition-evidence-unapproved":
        errors.append("selection input must remain normalized unapproved human audition evidence")
    if selection.get("normalizedStatus") != "human-music-family-selection-evidence-unapproved":
        errors.append("family selection normalized status must remain explicitly unapproved")
    if selection.get("canonicalFamilyCount") != 5 or len(context["mappingByTarget"]) != 5:
        errors.append("canonical music family count must remain five")
    if selection.get("decisionValues") != ["select", "needs-new-source", "needs-more-listening"]:
        errors.append("music family decision values drift")
    if "MUS_Warning_LowPulse" not in selection.get("unmappedPolicy", ""):
        errors.append("Warning family unmapped policy missing")
    if materialize.get("version") != 1 or materialize.get("status") != "materialization-tooling-ready-no-selected-music-source":
        errors.append("music materialization contract version/status drift")
    gate = materialize.get("input", {})
    if gate.get("reviewKind") != "music-canonical-family-selection" or gate.get("normalizedStatus") != selection.get("normalizedStatus"):
        errors.append("music materialization input does not match family selection output")
    if gate.get("readyFlag") != "readyForSourceMaterialization" or gate.get("readyFlagMustBe") is not True:
        errors.append("music materialization ready gate drift")
    material = materialize.get("materialization", {})
    if material.get("copyOnly") is not True or material.get("preserveSourceBytes") is not True or material.get("sourceAndOutputShaMustMatch") is not True or material.get("expectedCanonicalCueCount") != 5:
        errors.append("music materialization copy/hash/count invariants drift")
    if materialize.get("output", {}).get("filenamePattern") != "{canonicalCueId}.wav":
        errors.append("canonical music source filename pattern drift")
    files = context["fileByName"]
    warning = [f for f in files.values() if f.get("event_id") == "MUS_Warning_LowPulse"]
    mapped = [f for f in files.values() if f.get("canonicalTarget") is not None]
    if len(files) != 14 or len(warning) != 3 or len(mapped) != 11:
        errors.append(f"current music audit shape drift: total={len(files)} mapped={len(mapped)} warning={len(warning)}")
    if errors:
        for error in errors:
            print("ERROR:", error)
        return 1
    print("Music family selection contract OK: 14 audited candidates, 5 canonical families, 3 unmapped warning candidates, negative-result-safe selection and copy-only materialization.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
