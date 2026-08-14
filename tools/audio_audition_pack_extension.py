from __future__ import annotations
from pathlib import Path
from typing import Any
from audio_audition_pack_support import Artifact, PackError, atomic_write, extract_nested_member, locate_direct, records_index, require_sha, tech_text

EXT_STATUS='human-review-not-canonical-approval'

def review_path(target:str,source_path:str)->str:
    if target=='SFX_WOOD_PACK_ALT': return f'audio/wood/{Path(source_path).name}'
    if target=='SFX_CLOTH_PACK_ALT': return f'audio/cloth/{Path(source_path).name}'
    raise PackError(f'Unsupported extension archive target: {target}')

def build_extension(ext:dict[str,Any],shortlist:dict[str,Any],artifacts:list[Artifact],out:Path):
    records=records_index(ext,'extension receipt'); items=[]; provenance=[]; bindings={}; reviews={}
    ocean=records.get('AMB_OCEAN_ALT')
    if not ocean: raise PackError('extension receipt: AMB_OCEAN_ALT missing')
    filename=ocean.get('filename')
    if not isinstance(filename,str): raise PackError('extension ocean: filename missing')
    expected=require_sha(ocean.get('sha256'),'extension ocean')
    located=locate_direct(artifacts,filename,expected,{'extension-receipt'}); path=f'audio/ocean/{filename}'; atomic_write(out/path,located.data)
    technical=ocean.get('technical') if isinstance(ocean.get('technical'),dict) else {}
    items.append({'target':'AMB_OCEAN_ALT','file':filename,'sourcePath':filename,'reviewPath':path,'sha':expected,'bytes':len(located.data),'provider':ocean.get('provider',''),'license':ocean.get('license',''),'duration':technical.get('durationSeconds'),'tech':tech_text(technical),'candidateUse':['wave character','short ambience building block'],'flags':ocean.get('qaFlags',[]) if isinstance(ocean.get('qaFlags'),list) else []})
    provenance.append({'reviewPath':path,'artifact':located.artifact.path.name,'artifactMember':located.member_path,'sha256':expected}); bindings[path]=expected; reviews[path]={'fit':'','notes':''}
    members=shortlist.get('members')
    if not isinstance(members,list): raise PackError('extension shortlist: members must be a list')
    cache={}
    for member in members:
        if not isinstance(member,dict): raise PackError('extension shortlist: invalid member')
        target,source_path=member.get('archiveTarget'),member.get('path')
        if not isinstance(target,str) or not isinstance(source_path,str): raise PackError('extension shortlist: member identity incomplete')
        parent=records.get(target)
        if not parent: raise PackError(f'extension receipt missing archive target {target}')
        archive_name=parent.get('filename')
        if not isinstance(archive_name,str): raise PackError(f'extension receipt {target}: filename missing')
        if archive_name not in cache:
            cache[archive_name]=locate_direct(artifacts,archive_name,require_sha(parent.get('sha256'),f'extension archive {target}'),{'extension-receipt'})
        expected=require_sha(member.get('sha256'),f'extension member {target}/{source_path}')
        data=extract_nested_member(cache[archive_name].data,source_path,expected,archive_name); path=review_path(target,source_path); atomic_write(out/path,data)
        codec=member.get('codec'); technical={'sampleRateHz':member.get('sampleRateHz'),'channels':member.get('channels'),'codec':codec}
        flags=list(member.get('qaFlags',[])) if isinstance(member.get('qaFlags'),list) else []
        if codec=='vorbis': flags.append('lossy Vorbis: avoid repeated transcodes')
        items.append({'target':target,'file':Path(source_path).name,'sourcePath':source_path,'reviewPath':path,'sha':expected,'bytes':len(data),'tech':tech_text(technical),'candidateUse':member.get('candidateUse',[]),'flags':flags,'provider':parent.get('provider',''),'license':parent.get('license','')})
        src=cache[archive_name]; provenance.append({'reviewPath':path,'artifact':src.artifact.path.name,'artifactMember':src.member_path,'nestedArchive':archive_name,'nestedMember':source_path,'sha256':expected}); bindings[path]=expected; reviews[path]={'fit':'','notes':''}
    return items, {'version':2,'status':EXT_STATUS,'createdAt':'','bindings':bindings,'reviews':reviews}, provenance
