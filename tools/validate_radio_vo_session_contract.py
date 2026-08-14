#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
QUEUE=ROOT/"content/audio/radio_vo_recording_queue.source.json"
CONTRACT=ROOT/"content/audio/radio_vo_session_contract.source.json"
def main():
    q=json.loads(QUEUE.read_text()); c=json.loads(CONTRACT.read_text()); e=[]
    if len(q.get("cues",[]))!=9: e.append("queue must contain 9 cues")
    if q.get("takesPerCue")!=3: e.append("queue must require 3 takes")
    if c.get("takeNaming",{}).get("expectedTakeCount")!=27: e.append("contract must require 27 takes")
    for k in ("sampleRateHz","bitDepth","channels"):
        if q.get("sourceSpec",{}).get(k)!=c.get("technicalAcceptance",{}).get(k): e.append(f"spec mismatch {k}")
    ids=[x.get("id") for x in q.get("cues",[])]
    if len(ids)!=len(set(ids)): e.append("duplicate cue IDs")
    for cue in q.get("cues",[]):
        if cue.get("dryFilename")!=f"{cue.get('id')}.wav": e.append(f"{cue.get('id')}: dry filename mismatch")
        if not cue.get("localizationKey") or not cue.get("criticalSemantic"): e.append(f"{cue.get('id')}: missing semantic metadata")
    if c.get("provenance",{}).get("publicPersonImitationMustBe") is not False: e.append("public person imitation guard must be false")
    if e:
        for x in e: print("ERROR:",x)
        return 1
    print("Radio VO session contract OK: 9 cues x 3 takes = 27 dry PCM take slots.")
    return 0
if __name__=="__main__": raise SystemExit(main())
