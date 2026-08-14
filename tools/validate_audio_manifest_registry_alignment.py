#!/usr/bin/env python3
from pathlib import Path
import json, re
ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/"content/audio/audio_cues.source.json"
MANIFEST=ROOT/"docs/39_AUDIO_CUE_MANIFEST.md"
ALIASES=ROOT/"content/audio/audio_cue_alias_reconciliation.source.json"
ID_RE=re.compile(r"`((?:SFX|MUS|VO|UIA)_[A-Z0-9_]+)`")
def main():
    errors=[]
    reg_ids={c.get("id") for c in json.loads(REGISTRY.read_text(encoding="utf-8")).get("cues",[]) if isinstance(c,dict)}
    manifest=MANIFEST.read_text(encoding="utf-8")
    data=json.loads(ALIASES.read_text(encoding="utf-8"))
    for item in data.get("aliases",[]):
        old=item.get("old"); canonical=item.get("canonical")
        if old in manifest: errors.append(f"stale alias remains in docs39: {old}")
        if canonical not in manifest: errors.append(f"canonical replacement missing from docs39: {canonical}")
        if canonical not in reg_ids: errors.append(f"canonical target absent from registry: {canonical}")
    note="Machine runtime binding IDs come from `content/audio/audio_cues.source.json`."
    if note not in manifest: errors.append("missing machine-registry authority note")
    docs_ids=set(ID_RE.findall(manifest))
    spec_only=sorted(x for x in docs_ids if x not in reg_ids)
    if errors:
        for e in errors: print("ERROR:",e)
        return 1
    print(f"Audio manifest alignment OK: {len(data.get('aliases',[]))} aliases reconciled.")
    print(f"Design/spec-only human manifest IDs (non-binding until registered): {len(spec_only)}")
    return 0
if __name__=="__main__":
    raise SystemExit(main())
