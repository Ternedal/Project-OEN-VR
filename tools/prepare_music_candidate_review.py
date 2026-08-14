#!/usr/bin/env python3
"""Create a blank hash-bound review form from the audited music candidate artifact."""
from __future__ import annotations
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/"content/audio/music_candidate_audit.source.json"
def build_template():
    a=json.loads(AUDIT.read_text()); records=[]
    for f in a["files"]:
        names=["speechSpace","genreFit","dramaturgyFit","technicalStructure",("loopSeam" if f["loop"] else "endingShape")]
        records.append({"file":f["file"],"sha256":f["sha256"],"candidateFamily":f["event_id"],"canonicalTarget":f["canonicalTarget"],"mappingStatus":f["mappingStatus"],"fit":"unreviewed","checks":{n:{"result":"","note":""} for n in names},"overallNote":""})
    return {"version":1,"status":"human-music-audition-unreviewed","reviewedAt":"","reviewerRole":"","candidateAudit":str(AUDIT.relative_to(ROOT)).replace("\\","/"),"records":records,"rule":"Review evidence is hash-bound. keep/maybe/reject does not itself promote a source or bind runtime music."}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",type=Path,default=Path("music_candidate_review.template.json")); a=ap.parse_args()
    a.output.write_text(json.dumps(build_template(),indent=2,ensure_ascii=False)+"\n")
    print(f"Music audition template ready: 14 candidates -> {a.output}")
    return 0
if __name__=="__main__": raise SystemExit(main())
