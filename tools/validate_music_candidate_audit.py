#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/"content/audio/music_candidate_audit.source.json"
CUES=ROOT/"content/audio/audio_cues.source.json"
def main():
    a=json.loads(AUDIT.read_text()); c=json.loads(CUES.read_text()); e=[]
    files=a.get("files",[])
    if a.get("status")!="artifact-audited-audition-ready-not-source-approved": e.append("wrong audit status")
    if len(files)!=14: e.append("audit must contain 14 files")
    hashes=[x.get("sha256") for x in files]
    if len(hashes)!=len(set(hashes)): e.append("duplicate file hashes")
    if a.get("provenance",{}).get("thirdPartySamples") is not False: e.append("third-party-sample claim must be false")
    families={x.get("event_id") for x in files}
    expected={"MUS_Camp_WarmTexture","MUS_Warning_LowPulse","MUS_Storm_Phase1","MUS_Storm_Phase2","MUS_Storm_Phase3","MUS_Finale_Success"}
    if families!=expected: e.append("candidate family set mismatch")
    canonical={x.get("id") for x in c.get("cues",[]) if isinstance(x,dict)}
    mappings=a.get("canonicalMappings",[])
    if len(mappings)!=5: e.append("exactly five canonical mappings required")
    mapped_families=set()
    for m in mappings:
        if m.get("canonicalCueId") not in canonical: e.append(f"unknown canonical cue: {m.get('canonicalCueId')}")
        mapped_families.add(m.get("candidateFamily"))
    if "MUS_Warning_LowPulse" in mapped_families: e.append("warning family must remain unmapped")
    warning=[x for x in files if x.get("event_id")=="MUS_Warning_LowPulse"]
    if not warning or any(x.get("canonicalTarget") is not None for x in warning): e.append("warning candidates must have null canonicalTarget")
    for x in files:
        if x.get("sample_rate_hz")!=48000 or x.get("bit_depth")!=24 or x.get("channels")!=2: e.append(f"{x.get('file')}: format mismatch")
        if len(x.get("sha256",""))!=64: e.append(f"{x.get('file')}: invalid hash")
    if e:
        for x in e: print("ERROR:",x)
        return 1
    print("Music candidate audit OK: 14 hashed files, 5 canonical families + 1 explicitly unmapped family.")
    return 0
if __name__=="__main__": raise SystemExit(main())
