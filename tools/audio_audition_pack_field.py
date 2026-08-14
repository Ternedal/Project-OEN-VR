from __future__ import annotations
from pathlib import Path
from typing import Any
from audio_audition_pack_support import Artifact, PackError, atomic_write, locate_direct, records_index, require_sha, tech_text

FIELD_STATUS='human-field-review-not-canonical-approval'

def build_field(field:dict[str,Any],artifacts:list[Artifact],out:Path):
    records=records_index(field,'field receipt')
    if not records: raise PackError('field receipt: no acquired records')
    items=[]; provenance=[]; bindings={}; reviews={}
    for target,record in records.items():
        filename,runtime=record.get('filename'),record.get('runtimeEventCandidate')
        if not isinstance(filename,str) or not isinstance(runtime,str): raise PackError(f'field receipt {target}: filename/runtimeEventCandidate missing')
        expected=require_sha(record.get('sha256'),f'field receipt {target}')
        preferred={f"field-run-{record.get('evidenceRunId')}"} if record.get('evidenceRunId') is not None else set()
        located=locate_direct(artifacts,filename,expected,preferred); path=f'audio/field/{filename}'; atomic_write(out/path,located.data)
        probe=record.get('technicalProbe') if isinstance(record.get('technicalProbe'),dict) else {}; qa=record.get('objectiveQa') if isinstance(record.get('objectiveQa'),dict) else {}
        items.append({'target':target,'runtime':runtime,'file':filename,'reviewPath':path,'sha':expected,'bytes':len(located.data),'provider':record.get('provider',''),'license':record.get('license',''),'duration':probe.get('durationSeconds'),'tech':tech_text(probe),'note':qa.get('note',''),'flags':[]})
        provenance.append({'reviewPath':path,'artifact':located.artifact.path.name,'artifactMember':located.member_path,'sha256':expected}); bindings[target]=expected; reviews[target]={'fit':'','notes':''}
    return items, {'version':2,'status':FIELD_STATUS,'createdAt':'','bindings':bindings,'reviews':reviews}, provenance
