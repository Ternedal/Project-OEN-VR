#!/usr/bin/env python3
"""Validate the machine-readable PROJECT OEN Storm finale contract.

This validator checks canonical machine-readable IDs/gates. Human/device evidence remains external.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/"content/finale/storm_finale.source.json"
LOC=ROOT/"content/localization/da.source.json"
AUDIO=ROOT/"content/audio/audio_cues.source.json"
ASSETS=ROOT/"docs/38_SOURCE_ASSET_MANIFEST.md"
EXPECTED_PHASES=["STORM_PHASE_1_WIND_SHELTER","STORM_PHASE_2_RAIN_FIRE","STORM_PHASE_3_EARNED_CONSEQUENCE","STORM_PHASE_4_PARTIAL_COLLAPSE","STORM_PHASE_5_SIGNAL_DAWN"]

def validate_data(c:dict,loc:dict,audio:dict,asset_doc:str)->list[str]:
    errors=[]; phases=c.get("phases")
    if not isinstance(phases,list): return ["phases must be a list"]
    ids=[p.get("id") for p in phases if isinstance(p,dict)]
    if ids!=EXPECTED_PHASES: errors.append(f"phase order drift: {ids}")
    if [p.get("ordinal") for p in phases] != [1,2,3,4,5]: errors.append("phase ordinals must be 1..5")
    strings=loc.get("strings",{}); registry={x.get("id"):x for x in audio.get("cues",[]) if isinstance(x,dict)}
    for p in phases:
        pid=p.get("id"); roles=p.get("roles")
        if not isinstance(roles,list) or len(roles)!=2: errors.append(f"{pid}: exactly two roles required")
        for keyfield in ["titleKey","objectiveKey"]:
            key=p.get(keyfield)
            if key not in strings: errors.append(f"{pid}: missing localization {key}")
        for aid in p.get("assetIds",[]):
            if f"`{aid}`" not in asset_doc: errors.append(f"{pid}: asset ID absent from docs/38: {aid}")
        for cue in p.get("audioCueIds",[])+p.get("musicCueIds",[]):
            if cue not in registry: errors.append(f"{pid}: audio registry missing {cue}")
    rnd=phases[2].get("randomness",{})
    if rnd.get("gate")!="OQ-008": errors.append("phase 3 must be gated by OQ-008")
    if rnd.get("weights") is not None: errors.append("phase 3 weights must remain null")
    if rnd.get("finalProbabilityLocked") is not False: errors.append("phase 3 final probability must remain unlocked")
    if c.get("gates",{}).get("phase3Randomness",{}).get("weights") is not None: errors.append("global phase3 weights must remain null")
    if phases[3].get("technicalGate")!="M0b": errors.append("phase 4 must retain M0b technical gate")
    p5=phases[4]
    for required in ["ITM_EMBER_CARRIER_001","PRP_SIGNAL_FRAME_001","PRP_SIGNAL_FUEL_001"]:
        if required not in p5.get("assetIds",[]): errors.append(f"phase 5 missing {required}")
    if "MUS_SIGNAL_FINAL_001" not in p5.get("musicCueIds",[]): errors.append("phase 5 missing signal-final music")
    success=c.get("successSequence",{})
    if success.get("musicCueId")!="MUS_RESCUE_RELEASE_001": errors.append("success must use rescue-release music")
    for cue in success.get("radioVoCueFamily",[]):
        if cue not in registry: errors.append(f"success VO registry missing {cue}")
    if c.get("numericTuningStatus")!="evidence-gated-not-locked": errors.append("numeric tuning status must remain evidence-gated")
    return errors

def validate(root:Path=ROOT)->list[str]:
    rels=[CONTRACT,LOC,AUDIO,ASSETS]
    for p in rels:
        rp=root/p.relative_to(ROOT)
        if not rp.is_file(): return [f"missing {rp.relative_to(root)}"]
    try:
        c=json.loads((root/CONTRACT.relative_to(ROOT)).read_text(encoding="utf-8")); loc=json.loads((root/LOC.relative_to(ROOT)).read_text(encoding="utf-8")); audio=json.loads((root/AUDIO.relative_to(ROOT)).read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError) as exc: return [f"cannot load JSON: {exc}"]
    assets=(root/ASSETS.relative_to(ROOT)).read_text(encoding="utf-8")
    return validate_data(c,loc,audio,assets)

def main():
    errors=validate()
    if errors:
        for e in errors: print("STORM FINALE INVALID:",e,file=sys.stderr)
        return 1
    print("Storm finale contract OK: five phases, two roles each, Phase 3 remains OQ-008-gated."); return 0
if __name__=="__main__": raise SystemExit(main())
