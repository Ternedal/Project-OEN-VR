#!/usr/bin/env python3
import importlib.util,json,math,tempfile,wave
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load():
    p=ROOT/"tools/validate_radio_vo_session.py"; s=importlib.util.spec_from_file_location("rv",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
def pcm24(path,dur,rate=48000,channels=1):
    path.parent.mkdir(parents=True,exist_ok=True); amp=int(.2*8388607); data=bytearray()
    for i in range(int(dur*rate)):
        v=int(amp*math.sin(2*math.pi*220*i/rate))
        if v<0: v+=1<<24
        b=bytes((v&255,(v>>8)&255,(v>>16)&255)); data.extend(b*channels)
    with wave.open(str(path),"wb") as w: w.setnchannels(channels); w.setsampwidth(3); w.setframerate(rate); w.writeframes(data)
def prov(s):
    (s/"performer_provenance.json").write_text(json.dumps({"sourceType":"human-performer","sourceNameOrAlias":"Synthetic fixture","permissionOrLicense":"test-only","recordedOrGeneratedAt":"2026-08-14T00:00:00Z","commercialReuseAllowed":False,"identifiablePublicPersonImitation":False})+"\n")
def populate(m,s,stereo=False):
    q=json.loads(m.QUEUE.read_text())
    for x in m.build_expected(q):
        lo,hi=x["cue"]["targetDurationSec"]; ch=2 if stereo and x["filename"]=="VO_RADIO_NIGHT1_01__T01.wav" else 1
        pcm24(s/"takes"/x["filename"],(lo+hi)/2,channels=ch)
def main():
    m=load()
    with tempfile.TemporaryDirectory() as td:
        s=Path(td); prov(s); populate(m,s); r,e,w=m.validate_session(s,True); assert not e,e; assert r["status"]=="technical-intake-passed-not-listening-approved"; assert r["validatedTakeCount"]==27
    with tempfile.TemporaryDirectory() as td:
        s=Path(td); prov(s); populate(m,s); (s/"takes/VO_RADIO_NIGHT1_01__T03.wav").unlink(); r,e,w=m.validate_session(s,True); assert any("missing take" in x for x in e); assert r["status"]=="technical-intake-incomplete-or-failed"
    with tempfile.TemporaryDirectory() as td:
        s=Path(td); prov(s); populate(m,s,True); r,e,w=m.validate_session(s,True); assert any("expected mono" in x for x in e)
    print("Radio VO intake self-test OK: pass + missing-take + stereo rejection.")
    return 0
if __name__=="__main__": raise SystemExit(main())
