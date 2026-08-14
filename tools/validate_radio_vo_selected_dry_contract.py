#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(p): return json.loads(p.read_text(encoding='utf-8'))
def main():
    c=load(ROOT/'content/audio/radio_vo_selected_dry_contract.source.json')
    s=load(ROOT/'content/audio/radio_vo_session_contract.source.json')
    h=load(ROOT/'content/audio/radio_vo_human_review_contract.source.json')
    errors=[]
    if c.get('version')!=1 or c.get('status')!='materialization-tooling-ready-no-selected-dry-source': errors.append('selected-dry contract version/status drift')
    if c.get('input',{}).get('reviewKind')!='radio-vo-human-take-selection': errors.append('selected-dry reviewKind drift')
    if c.get('input',{}).get('normalizedStatus')!=h.get('normalizedStatus'): errors.append('selected-dry input status must match human normalizer output')
    if c.get('input',{}).get('readyFlag')!='readyForDryMasterSelection' or c.get('input',{}).get('readyFlagMustBe') is not True: errors.append('selected-dry ready gate must remain explicit true')
    out=c.get('output',{})
    if out.get('filenamePattern')!=s.get('takeNaming',{}).get('selectedDryMasterPattern'): errors.append('selected-dry filename pattern drift from session contract')
    if out.get('receiptStatus')!='selected-dry-source-materialized-from-human-review-not-processed': errors.append('selected-dry receipt status drift')
    m=c.get('materialization',{})
    if m.get('copyOnly') is not True or m.get('preserveSourceBytes') is not True or m.get('sourceAndOutputShaMustMatch') is not True or m.get('expectedCueCount')!=9: errors.append('selected-dry copy/hash/count invariants drift')
    rules=' | '.join(c.get('rules',[])).lower()
    for phrase in ('no trim','no',):
        pass
    if 'performs no trim' not in rules or 'does not promote' not in rules: errors.append('selected-dry non-processing/non-promotion guardrails missing')
    if errors:
        for e in errors: print('ERROR:',e)
        return 1
    print('Radio VO selected-dry contract OK: 9 copy-only sources, exact hash preservation, explicit human-ready input, no downstream approval promotion.')
    return 0
if __name__=='__main__': raise SystemExit(main())
