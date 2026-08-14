from __future__ import annotations
from pathlib import Path
from typing import Any
from audio_audition_pack_support import Artifact, PackError, atomic_write, locate_direct, records_index, require_sha, tech_text

MAIN_STATUS='human-listening-review-unvalidated'
MAIN_CHECKS={
 'AMB_WIND_WORLD':['CONTAMINATION','MATERIAL_MATCH','LOOP_OR_SLICE','NOISE_FLOOR','SPACE_IDENTITY','VARIATION_VALUE','SPEECH_SPACE'],
 'AMB_RAIN_ALT':['CONTAMINATION','MATERIAL_MATCH','LOOP_OR_SLICE','NOISE_FLOOR','SPACE_IDENTITY','VARIATION_VALUE','SPEECH_SPACE'],
 'SFX_FIRE_ALT':['CONTAMINATION','MATERIAL_MATCH','LOOP_OR_SLICE','NOISE_FLOOR','TRANSIENT_QUALITY','SPACE_IDENTITY','VARIATION_VALUE','SPEECH_SPACE'],
}

def check_questions(qa: dict[str,Any]) -> dict[str,str]:
    result={x['id']:x['question'] for x in qa.get('requiredListeningChecks',[]) if isinstance(x,dict) and isinstance(x.get('id'),str) and isinstance(x.get('question'),str)}
    missing=sorted({c for checks in MAIN_CHECKS.values() for c in checks if c not in result})
    if missing: raise PackError(f'listening QA missing required main checks: {missing}')
    return result

def navigation_index(targets: dict[str,Any]) -> dict[str,dict[str,Any]]:
    records=targets.get('records')
    if not isinstance(records,list): raise PackError('listening targets: records must be a list')
    return {r['target']:r for r in records if isinstance(r,dict) and isinstance(r.get('target'),str)}

def build_main(main: dict[str,Any], navigation: dict[str,dict[str,Any]], artifacts: list[Artifact], out: Path):
    records=records_index(main,'main receipt')
    if set(records)!=set(MAIN_CHECKS): raise PackError(f'main receipt target drift: expected={sorted(MAIN_CHECKS)} actual={sorted(records)}')
    items=[]; provenance=[]; bindings={}; reviews=[]
    for target,checks in MAIN_CHECKS.items():
        record=records[target]; filename=record.get('filename')
        if not isinstance(filename,str): raise PackError(f'main receipt {target}: filename missing')
        expected=require_sha(record.get('sha256'),f'main receipt {target}')
        located=locate_direct(artifacts,filename,expected,{'main-receipt'})
        review_path=f'audio/main/{filename}'; atomic_write(out/review_path,located.data)
        nav=navigation.get(target,{})
        windows=[[w.get('label'),w.get('startSeconds'),w.get('endSeconds')] for w in nav.get('reviewWindows',[]) if isinstance(w,dict)]
        peak=nav.get('peakInspection') if isinstance(nav,dict) else None
        technical=record.get('technical') if isinstance(record.get('technical'),dict) else {}
        if isinstance(peak,dict) and isinstance(peak.get('timeSeconds'),(int,float)):
            t=peak['timeSeconds']; windows.append(['peak',t,min(technical.get('durationSeconds',t+5),t+5)])
        attention=[x for x in technical.get('qaFlags',[]) if isinstance(x,str)]
        attention += [x for x in nav.get('requiredTechnicalAttention',[]) if isinstance(x,str) and x not in attention]
        items.append({'target':target,'file':filename,'sha':expected,'provider':record.get('provider',''),'license':record.get('license',''),'duration':technical.get('durationSeconds'),'tech':tech_text(technical),'checks':checks,'attention':attention,'windows':windows,'reviewPath':review_path,'bytes':len(located.data)})
        provenance.append({'reviewPath':review_path,'artifact':located.artifact.path.name,'artifactMember':located.member_path,'sha256':expected})
        bindings[target]=expected
        reviews.append({'target':target,'disposition':'unreviewed','overall':'','checks':{c:{'result':'','note':''} for c in checks}})
    return items, {'version':2,'status':MAIN_STATUS,'reviewedAt':'','bindings':bindings,'records':reviews}, provenance
