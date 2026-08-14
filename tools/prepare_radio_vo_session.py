#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
QUEUE=ROOT/"content/audio/radio_vo_recording_queue.source.json"
CONTRACT=ROOT/"content/audio/radio_vo_session_contract.source.json"
DEFAULT_OUT=ROOT/"PrivateContent/RadioVOSession"
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",type=Path,default=DEFAULT_OUT); a=ap.parse_args()
    q=json.loads(QUEUE.read_text()); c=json.loads(CONTRACT.read_text())
    if q.get("takesPerCue")!=3 or len(q.get("cues",[]))!=9: raise SystemExit("queue must be 9 cues x 3 takes")
    out=a.output.resolve(); (out/"takes").mkdir(parents=True,exist_ok=True)
    expected=[]
    for cue in q["cues"]:
        for take in range(1,4):
            expected.append({"cueId":cue["id"],"take":take,"filename":f"{cue['id']}__T{take:02d}.wav","phase":cue["phase"],"localizationKey":cue["localizationKey"],"delivery":cue["delivery"],"criticalSemantic":cue["criticalSemantic"],"targetDurationSec":cue["targetDurationSec"]})
    (out/"recording_session.json").write_text(json.dumps({"version":1,"status":"prepared-not-recorded","expectedTakeCount":len(expected),"expectedTakes":expected,"rule":"Untouched dry WAV takes only; no radio processing."},indent=2,ensure_ascii=False)+"\n")
    prov=out/c["provenance"]["filename"]
    if not prov.exists(): prov.write_text(json.dumps({"sourceType":"","sourceNameOrAlias":"","permissionOrLicense":"","recordedOrGeneratedAt":"","commercialReuseAllowed":None,"identifiablePublicPersonImitation":False,"notes":""},indent=2)+"\n")
    print(f"Prepared {len(expected)} take slots under {out/'takes'}")
    return 0
if __name__=="__main__": raise SystemExit(main())
