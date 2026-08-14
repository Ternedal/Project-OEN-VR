#!/usr/bin/env python3
"""Normalize hash-bound human audition evidence for the external music candidate artifact."""
from __future__ import annotations
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/"content/audio/music_candidate_audit.source.json"
ALLOWED_FIT={"keep","maybe","reject"}
ALLOWED_CHECK={"pass","fail","needs-more-listening","not-applicable"}
def normalize(data,require_complete=True):
    audit=json.loads(AUDIT.read_text())
    source={x["file"]:x for x in audit["files"]}
    errors=[]
    recs=data.get("records")
    if not isinstance(recs,list): return None,["records must be a list"]
    seen=set(); out=[]
    for r in recs:
        fn=r.get("file")
        if fn in seen: errors.append(f"duplicate review record: {fn}"); continue
        seen.add(fn)
        src=source.get(fn)
        if not src: errors.append(f"unknown candidate file: {fn}"); continue
        if r.get("sha256")!=src["sha256"]: errors.append(f"{fn}: SHA-256 does not match audited artifact")
        if r.get("candidateFamily")!=src["event_id"]: errors.append(f"{fn}: candidate family mismatch")
        if r.get("canonicalTarget")!=src["canonicalTarget"]: errors.append(f"{fn}: canonical target mismatch")
        if r.get("mappingStatus")!=src["mappingStatus"]: errors.append(f"{fn}: mapping status mismatch")
        fit=r.get("fit")
        if require_complete and fit not in ALLOWED_FIT: errors.append(f"{fn}: fit must be keep/maybe/reject")
        elif fit not in ALLOWED_FIT|{"unreviewed"}: errors.append(f"{fn}: invalid fit")
        checks=r.get("checks",{})
        if not isinstance(checks,dict): errors.append(f"{fn}: checks must be object"); checks={}
        for name,obj in checks.items():
            result=obj.get("result") if isinstance(obj,dict) else None
            if require_complete and result not in ALLOWED_CHECK: errors.append(f"{fn}/{name}: incomplete check")
            elif result and result not in ALLOWED_CHECK: errors.append(f"{fn}/{name}: invalid result")
        out.append({
          "file":fn,"sha256":src["sha256"],"candidateFamily":src["event_id"],
          "canonicalTarget":src["canonicalTarget"],"mappingStatus":src["mappingStatus"],
          "fit":fit,"checks":checks,"overallNote":r.get("overallNote","")
        })
    missing=sorted(set(source)-seen)
    if require_complete and missing: errors.append("missing candidate review(s): "+", ".join(missing))
    result={
      "version":1,
      "status":"human-music-audition-evidence-unapproved" if not errors and len(out)==len(source) else "human-music-audition-incomplete-or-invalid",
      "reviewedAt":data.get("reviewedAt",""),
      "reviewerRole":data.get("reviewerRole",""),
      "candidateAudit":str(AUDIT.relative_to(ROOT)).replace("\\","/"),
      "records":out,
      "rule":"Normalized human audition evidence does not promote source approval, runtime binding, Unity integration or release approval."
    }
    if require_complete and (not isinstance(result["reviewedAt"],str) or not result["reviewedAt"].strip()): errors.append("reviewedAt is required")
    if require_complete and (not isinstance(result["reviewerRole"],str) or not result["reviewerRole"].strip()): errors.append("reviewerRole is required")
    if errors: result["status"]="human-music-audition-incomplete-or-invalid"
    return result,errors
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--input",type=Path,required=True); ap.add_argument("--output",type=Path,required=True); ap.add_argument("--require-complete",action="store_true"); a=ap.parse_args()
    data=json.loads(a.input.read_text()); result,errors=normalize(data,a.require_complete)
    a.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    for e in errors: print("ERROR:",e)
    if errors: return 1
    print("Music audition evidence normalized: hash-bound, human-reviewed, still unapproved.")
    return 0
if __name__=="__main__": raise SystemExit(main())
