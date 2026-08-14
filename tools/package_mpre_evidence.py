#!/usr/bin/env python3
"""Package real M-Pre human-session CSV + raw notes into a hash-bound evidence bundle."""
from __future__ import annotations
import argparse, csv, hashlib, importlib.util, json, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/"content/mpre/evidence_bundle_contract.source.json"
EVALUATOR=ROOT/"tools/evaluate_mpre.py"
DEFAULT_OUTPUT=ROOT/"PrivateContent/MPreEvidence"
DENY_KEYS={"tester_a","tester_b","tester_name","participant_name","participant_email","email","phone","telephone","address"}

def sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def load_evaluator():
    spec=importlib.util.spec_from_file_location("evaluate_mpre",EVALUATOR)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod

def csv_pairs(path:Path)->dict[str,str]:
    with path.open("r",encoding="utf-8-sig",newline="") as f:
        rows=list(csv.DictReader(f))
    return {r["session_id"].strip():r["pair_id"].strip() for r in rows}

def recursive_keys(value):
    if isinstance(value,dict):
        for k,v in value.items(): yield str(k).lower(); yield from recursive_keys(v)
    elif isinstance(value,list):
        for x in value: yield from recursive_keys(x)

def validate_notes(data:dict,session_id:str,pair_id:str,contract:dict)->list[str]:
    errors=[]; req=contract["notesRequirements"]
    for field in req["requiredTopLevelFields"]:
        if field not in data: errors.append(f"{session_id}: notes missing {field}")
    if data.get("session_id")!=session_id: errors.append(f"{session_id}: notes session_id mismatch")
    if data.get("pair_id")!=pair_id: errors.append(f"{session_id}: notes pair_id mismatch")
    bad=sorted(set(recursive_keys(data))&DENY_KEYS)
    if bad: errors.append(f"{session_id}: structured PII-like key(s) not allowed: {', '.join(bad)}")
    days=data.get("days")
    if not isinstance(days,list) or len(days)!=req["dayCount"]:
        errors.append(f"{session_id}: notes must contain exactly {req['dayCount']} days"); days=[]
    day_numbers=[]; qualitative=[]
    for d in days:
        if not isinstance(d,dict): errors.append(f"{session_id}: day entry must be object"); continue
        day_numbers.append(d.get("day"))
        for field in req["requiredDayFields"]:
            if field not in d: errors.append(f"{session_id}: day {d.get('day')} missing {field}")
        for field in ("proposal_a","proposal_b","observations"):
            v=d.get(field,"")
            if isinstance(v,str) and v.strip(): qualitative.append(v.strip())
    if days and sorted(day_numbers)!=[1,2,3]: errors.append(f"{session_id}: day numbers must be 1,2,3")
    debrief=data.get("debrief","")
    if isinstance(debrief,str) and debrief.strip(): qualitative.append(debrief.strip())
    if req.get("qualitativeContentRequired") and not qualitative: errors.append(f"{session_id}: raw notes contain no qualitative content")
    status=data.get("status_after_day3")
    if not isinstance(status,dict): errors.append(f"{session_id}: status_after_day3 must be object")
    else:
        for field in ("food","shelter","health","signal"):
            if not isinstance(status.get(field),(int,float)): errors.append(f"{session_id}: status_after_day3.{field} must be numeric")
    return errors

def build_bundle(csv_path:Path,notes_paths:list[Path],output:Path)->tuple[dict,list[str]]:
    contract=json.loads(CONTRACT.read_text(encoding="utf-8")); errors=[]; evaluator=load_evaluator()
    try: gate,results=evaluator.evaluate(csv_path)
    except (OSError,ValueError) as exc: return {},[f"CSV/evaluator input invalid: {exc}"]
    pairs=csv_pairs(csv_path); notes_by_id={}
    for p in notes_paths:
        try: data=json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc: errors.append(f"{p}: invalid notes JSON: {exc}"); continue
        sid=data.get("session_id")
        if not isinstance(sid,str) or not sid.strip(): errors.append(f"{p}: missing session_id"); continue
        if sid in notes_by_id: errors.append(f"duplicate notes for session {sid}"); continue
        notes_by_id[sid]=(p,data)
    missing=sorted(set(pairs)-set(notes_by_id)); extra=sorted(set(notes_by_id)-set(pairs))
    if missing: errors.append("missing notes for session(s): "+", ".join(missing))
    if extra: errors.append("notes reference unknown session(s): "+", ".join(extra))
    for sid,pair in pairs.items():
        if sid in notes_by_id: errors.extend(validate_notes(notes_by_id[sid][1],sid,pair,contract))
    if errors: return {},errors
    output.mkdir(parents=True,exist_ok=True); notes_dir=output/"notes"; notes_dir.mkdir(exist_ok=True)
    csv_dest=output/contract["csvFilename"]; shutil.copy2(csv_path,csv_dest)
    file_records=[{"role":"session-csv","path":csv_dest.name,"sha256":sha256_file(csv_dest),"bytes":csv_dest.stat().st_size}]
    for sid in sorted(pairs):
        source,_=notes_by_id[sid]; name=contract["notesFilenamePattern"].format(session_id=sid); dest=notes_dir/name; shutil.copy2(source,dest)
        file_records.append({"role":"raw-session-notes","session_id":sid,"path":str(dest.relative_to(output)).replace("\\","/"),"sha256":sha256_file(dest),"bytes":dest.stat().st_size})
    manifest={"version":1,"status":contract["bundleStatusOnValid"],"gateCalculation":gate,"sessionCount":len(results),"distinctPairCount":len({x["pair_id"] for x in results}),"sessions":results,"files":file_records,"contract":"content/mpre/evidence_bundle_contract.source.json","evaluator":"tools/evaluate_mpre.py","rule":"This manifest proves structural validity and hashes supplied human evidence. Gate acceptance/issue closure is a separate explicit project action."}
    (output/contract["manifestFilename"]).write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return manifest,[]

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--csv",type=Path,required=True); ap.add_argument("--notes",type=Path,action="append",required=True); ap.add_argument("--output",type=Path,default=DEFAULT_OUTPUT); a=ap.parse_args()
    manifest,errors=build_bundle(a.csv.resolve(),[p.resolve() for p in a.notes],a.output.resolve())
    for e in errors: print("ERROR:",e)
    if errors: return 2
    print(f"M-Pre evidence bundle valid: {manifest['sessionCount']} human sessions / {manifest['distinctPairCount']} pairs / calculated gate {manifest['gateCalculation']}")
    print("Bundle remains unaccepted; issue #7 is not changed automatically.")
    return 0
if __name__=="__main__": raise SystemExit(main())
