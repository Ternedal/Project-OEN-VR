#!/usr/bin/env python3
"""Revalidate a packaged M-Pre evidence bundle and every bound hash."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/"content/mpre/evidence_bundle_contract.source.json"
EVALUATOR=ROOT/"tools/evaluate_mpre.py"
def sha256_file(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()
def evaluator():
    s=importlib.util.spec_from_file_location("evaluate_mpre",EVALUATOR); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
def validate(bundle:Path):
    c=json.loads(CONTRACT.read_text()); mp=bundle/c["manifestFilename"]; errors=[]
    if not mp.is_file(): return ["missing evidence manifest"]
    try: m=json.loads(mp.read_text())
    except Exception as exc: return [f"invalid manifest JSON: {exc}"]
    if m.get("status")!=c["bundleStatusOnValid"]: errors.append("wrong bundle status")
    files=m.get("files")
    if not isinstance(files,list) or len(files)!=4: errors.append("manifest must bind CSV + 3 notes files"); files=[]
    for r in files:
        rel=Path(r.get("path", ""))
        if rel.is_absolute() or ".." in rel.parts: errors.append(f"unsafe manifest path: {rel}"); continue
        p=bundle/rel
        if not p.is_file(): errors.append(f"missing bound file: {rel}"); continue
        if sha256_file(p)!=r.get("sha256"): errors.append(f"hash mismatch: {rel}")
        if p.stat().st_size!=r.get("bytes"): errors.append(f"byte-size mismatch: {rel}")
    csv_path=bundle/c["csvFilename"]
    if csv_path.is_file():
        try: gate,results=evaluator().evaluate(csv_path)
        except (OSError,ValueError) as exc: errors.append(f"evaluator rejects bundled CSV: {exc}")
        else:
            if gate!=m.get("gateCalculation"): errors.append("gate calculation mismatch")
            if results!=m.get("sessions"): errors.append("session result snapshot mismatch")
    return errors
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("bundle",type=Path); a=ap.parse_args(); e=validate(a.bundle.resolve())
    for x in e: print("ERROR:",x)
    if e: return 2
    print("M-Pre evidence bundle verification PASS: hashes + evaluator result are internally consistent; acceptance remains separate.")
    return 0
if __name__=="__main__": raise SystemExit(main())
