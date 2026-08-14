#!/usr/bin/env python3
import csv,importlib.util,json,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def mod(name,path):
    s=importlib.util.spec_from_file_location(name,ROOT/path); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
FIELDS=["session_id","pair_id","day1_seconds","day2_seconds","day3_seconds","disagreement_days","administration_observed","changed_mind_count","regret_after_storm","human_session","gift_recipient_used"]
def write_csv(p,gift=False):
    rows=[["S01","P01",60,55,50,1,"false",1,"true","true","false"],["S02","P02",70,65,60,2,"false",2,"false","true","false"],["S03","P01",20,25,30,0,"true",0,"false","true","true" if gift else "false"]]
    with p.open("w",newline="") as f:
        w=csv.writer(f); w.writerow(FIELDS); w.writerows(rows)
def note(p,sid,pair):
    p.write_text(json.dumps({"session_id":sid,"pair_id":pair,"days":[{"day":1,"proposal_a":"food","proposal_b":"shelter","observations":"argued about shelter"},{"day":2,"proposal_a":"signal","proposal_b":"food","observations":"changed priority"},{"day":3,"proposal_a":"signal","proposal_b":"shelter","observations":"brief disagreement"}],"debrief":"They described a real priority tradeoff.","status_after_day3":{"food":4,"shelter":6,"health":4,"signal":5}})+"\n")
def main():
    p=mod("pack","tools/package_mpre_evidence.py"); v=mod("verify","tools/validate_mpre_evidence_bundle.py")
    with tempfile.TemporaryDirectory() as td:
        d=Path(td); csvp=d/"s.csv"; write_csv(csvp); notes=[]
        for sid,pair in [("S01","P01"),("S02","P02"),("S03","P01")]: q=d/f"{sid}.json"; note(q,sid,pair); notes.append(q)
        out=d/"bundle"; m,e=p.build_bundle(csvp,notes,out); assert not e,e; assert m["gateCalculation"]=="GREEN"; assert m["status"]=="human-evidence-bundle-valid-unaccepted"; assert not v.validate(out)
        (out/"notes/mpre_notes_S01.json").write_text("{}\n"); assert any("hash mismatch" in x for x in v.validate(out))
    with tempfile.TemporaryDirectory() as td:
        d=Path(td); csvp=d/"s.csv"; write_csv(csvp); notes=[]
        for sid,pair in [("S01","P01"),("S02","P02")]: q=d/f"{sid}.json"; note(q,sid,pair); notes.append(q)
        _,e=p.build_bundle(csvp,notes,d/"bundle"); assert any("missing notes" in x for x in e)
    with tempfile.TemporaryDirectory() as td:
        d=Path(td); csvp=d/"s.csv"; write_csv(csvp,gift=True); notes=[]
        for sid,pair in [("S01","P01"),("S02","P02"),("S03","P01")]: q=d/f"{sid}.json"; note(q,sid,pair); notes.append(q)
        _,e=p.build_bundle(csvp,notes,d/"bundle"); assert any("gift recipient" in x for x in e)
    print("M-Pre evidence bundle self-test OK: valid bundle + tamper + missing notes + gift-recipient rejection.")
    return 0
if __name__=="__main__": raise SystemExit(main())
