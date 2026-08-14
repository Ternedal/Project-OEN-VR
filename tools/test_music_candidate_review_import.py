#!/usr/bin/env python3
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def mod(name,path):
    s=importlib.util.spec_from_file_location(name,ROOT/path); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
def good(p):
    d=p.build_template(); d["reviewedAt"]="2026-08-14T00:00:00Z"; d["reviewerRole"]="synthetic-self-test"
    for r in d["records"]:
        r["fit"]="maybe"
        for obj in r["checks"].values(): obj["result"]="needs-more-listening"; obj["note"]="synthetic fixture only"
    return d
def main():
    p=mod("prep","tools/prepare_music_candidate_review.py"); n=mod("norm","tools/normalize_music_candidate_review.py")
    d=good(p); out,e=n.normalize(d,True); assert not e,e; assert out["status"]=="human-music-audition-evidence-unapproved"; assert len(out["records"])==14
    d=good(p); d["records"][0]["sha256"]="0"*64; out,e=n.normalize(d,True); assert any("SHA-256" in x for x in e)
    d=good(p); d["records"]=d["records"][:-1]; out,e=n.normalize(d,True); assert any("missing candidate" in x for x in e)
    d=good(p); w=next(r for r in d["records"] if r["candidateFamily"]=="MUS_Warning_LowPulse"); w["canonicalTarget"]="MUS_STORM_BASE_001"; out,e=n.normalize(d,True); assert any("canonical target mismatch" in x for x in e)
    print("Music audition import self-test OK: pass + hash + completeness + unmapped-family guard.")
    return 0
if __name__=="__main__": raise SystemExit(main())
