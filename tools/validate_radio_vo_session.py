#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,math,wave
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
QUEUE=ROOT/"content/audio/radio_vo_recording_queue.source.json"
CONTRACT=ROOT/"content/audio/radio_vo_session_contract.source.json"
DEFAULT_SESSION=ROOT/"PrivateContent/RadioVOSession"
def sha256_file(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()
def peak24(raw):
    if len(raw)%3: raise ValueError("invalid 24-bit frame bytes")
    peak=full=0
    for i in range(0,len(raw),3):
        v=raw[i]|(raw[i+1]<<8)|(raw[i+2]<<16)
        if v&0x800000: v-=1<<24
        a=abs(v); peak=max(peak,a)
        if v in (-8388608,8388607): full+=1
    db=float("-inf") if peak==0 else 20*math.log10(peak/8388607)
    return db,full
def inspect_wav(p):
    with wave.open(str(p),"rb") as w:
        ch,sw,rate,n,ct=w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes(),w.getcomptype()
        raw=w.readframes(n)
    db,full=peak24(raw) if sw==3 and ch==1 else (None,None)
    return {"channels":ch,"bitDepth":sw*8,"sampleRateHz":rate,"frames":n,"durationSec":n/rate if rate else 0,"compressionType":ct,"peakDbfs":db,"fullScaleSampleCount":full}
def build_expected(q):
    return [{"cue":cue,"take":t,"filename":f"{cue['id']}__T{t:02d}.wav"} for cue in q["cues"] for t in range(1,q["takesPerCue"]+1)]
def provenance_errors(p,c):
    if not p.is_file(): return ["missing performer_provenance.json"]
    try: d=json.loads(p.read_text())
    except Exception as e: return [f"invalid provenance JSON: {e}"]
    e=[]
    for f in c["provenance"]["requiredFields"]:
        if f not in d: e.append(f"provenance missing {f}")
    if d.get("sourceType") not in c["provenance"]["allowedSourceTypes"]: e.append("unsupported provenance sourceType")
    for f in ("sourceNameOrAlias","permissionOrLicense","recordedOrGeneratedAt"):
        if not isinstance(d.get(f),str) or not d[f].strip(): e.append(f"provenance {f} must be non-empty")
    if not isinstance(d.get("commercialReuseAllowed"),bool): e.append("commercialReuseAllowed must be boolean")
    if d.get("identifiablePublicPersonImitation") is not False: e.append("identifiablePublicPersonImitation must be false")
    return e
def validate_session(session,require_complete=True):
    q=json.loads(QUEUE.read_text()); c=json.loads(CONTRACT.read_text()); spec=c["technicalAcceptance"]
    errors=provenance_errors(session/c["provenance"]["filename"],c); warnings=[]; records=[]
    expected=build_expected(q); edir=session/"takes"
    names={p.name for p in edir.glob("*.wav")} if edir.is_dir() else set(); exp={x["filename"] for x in expected}
    if names-exp: errors.append("unexpected WAV take(s): "+", ".join(sorted(names-exp)))
    for x in expected:
        cue,take,name=x["cue"],x["take"],x["filename"]; p=edir/name
        if not p.is_file():
            if require_complete: errors.append(f"missing take: {name}")
            continue
        try: tech=inspect_wav(p)
        except Exception as exc: errors.append(f"{name}: unreadable PCM WAV: {exc}"); continue
        if tech["compressionType"]!="NONE": errors.append(f"{name}: WAV must be uncompressed PCM")
        if tech["sampleRateHz"]!=spec["sampleRateHz"]: errors.append(f"{name}: wrong sample rate")
        if tech["bitDepth"]!=spec["bitDepth"]: errors.append(f"{name}: wrong bit depth")
        if tech["channels"]!=spec["channels"]: errors.append(f"{name}: expected mono")
        if tech["fullScaleSampleCount"] is not None and tech["fullScaleSampleCount"]>spec["fullScaleSampleCountMax"]: errors.append(f"{name}: full-scale sample(s)")
        lo,hi=cue["targetDurationSec"]; ok=lo<=tech["durationSec"]<=hi
        if not ok: warnings.append(f"{name}: duration {tech['durationSec']:.3f}s outside {lo}-{hi}s target")
        records.append({"cueId":cue["id"],"take":take,"filename":name,"sha256":sha256_file(p),"bytes":p.stat().st_size,"sampleRateHz":tech["sampleRateHz"],"bitDepth":tech["bitDepth"],"channels":tech["channels"],"durationSec":round(tech["durationSec"],6),"peakDbfs":None if tech["peakDbfs"] is None else round(tech["peakDbfs"],3),"fullScaleSampleCount":tech["fullScaleSampleCount"],"durationTargetSec":cue["targetDurationSec"],"durationWithinTarget":ok})
    status=c["receipt"]["statusOnPass"] if not errors and len(records)==len(expected) else "technical-intake-incomplete-or-failed"
    return {"version":1,"status":status,"expectedTakeCount":len(expected),"validatedTakeCount":len(records),"records":records,"warnings":warnings,"rule":"Technical intake is not pronunciation, delivery, semantic, listening, source-selection, Unity or release approval."},errors,warnings
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--session",type=Path,default=DEFAULT_SESSION); ap.add_argument("--output",type=Path); ap.add_argument("--allow-incomplete",action="store_true"); a=ap.parse_args()
    s=a.session.resolve(); receipt,errors,warnings=validate_session(s,not a.allow_incomplete); out=a.output or s/"radio_vo_intake_receipt.json"; out.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n")
    for x in warnings: print("WARNING:",x)
    for x in errors: print("ERROR:",x)
    if errors: return 1
    print(f"Radio VO technical intake PASS: {receipt['validatedTakeCount']}/{receipt['expectedTakeCount']} takes")
    print("Human pronunciation/delivery/semantic selection remains pending.")
    return 0
if __name__=="__main__": raise SystemExit(main())
