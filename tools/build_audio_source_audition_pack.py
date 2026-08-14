#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from audio_audition_pack_support import PackError, atomic_write, contract_paths, expected_artifact_digests, index_artifacts, load_json, sha256_file, source_main_sha
from audio_audition_pack_main import MAIN_STATUS, MAIN_CHECKS, build_main, check_questions, navigation_index
from audio_audition_pack_extension import EXT_STATUS, build_extension
from audio_audition_pack_field import FIELD_STATUS, build_field

ROOT=Path(__file__).resolve().parents[1]

def verify_output_hashes(out:Path,items:Iterable[dict[str,Any]])->None:
    for item in items:
        actual=sha256_file(out/item['reviewPath'])
        if actual!=item['sha']: raise PackError(f"output hash mismatch for {item['reviewPath']}: expected={item['sha']} actual={actual}")

def build_pack(repo_root:Path,artifact_paths:list[Path],out_dir:Path,*,require_pinned_artifact_wrapper:bool=False,source_sha:str|None=None)->dict[str,Any]:
    paths=contract_paths(repo_root)
    main,ext,shortlist,field,targets,qa=(load_json(paths[k]) for k in ('main','extension','shortlist','field','targets','qa'))
    questions=check_questions(qa); artifacts=index_artifacts(artifact_paths,expected_artifact_digests(main,ext,field),require_pinned_artifact_wrapper)
    with tempfile.TemporaryDirectory(prefix='oen-audition-build-') as td:
        staging=Path(td)/'pack'; staging.mkdir(parents=True)
        main_items,main_template,main_prov=build_main(main,navigation_index(targets),artifacts,staging)
        ext_items,ext_template,ext_prov=build_extension(ext,shortlist,artifacts,staging)
        field_items,field_template,field_prov=build_field(field,artifacts,staging)
        all_items=[*main_items,*ext_items,*field_items]; verify_output_hashes(staging,all_items)
        data={'main':main_items,'extension':ext_items,'field':field_items,'questions':questions,'mainTemplate':main_template,'extensionTemplate':ext_template,'fieldTemplate':field_template}
        html_template=paths['html'].read_text(encoding='utf-8'); marker='__AUDITION_DATA_JSON__'
        if html_template.count(marker)!=1: raise PackError(f'HTML template must contain exactly one {marker} marker')
        atomic_write(staging/'review.html',html_template.replace(marker,json.dumps(data,ensure_ascii=False,separators=(',',':'))).encode())
        for filename,payload in (('main_review.template.json',main_template),('extension_review.template.json',ext_template),('field_review.template.json',field_template)):
            atomic_write(staging/filename,(json.dumps(payload,indent=2,ensure_ascii=False)+'\n').encode())
        manifest={'version':2,'status':'audition-pack-unreviewed','createdAtUtc':datetime.now(timezone.utc).isoformat(),'sourceMainSha':source_sha or source_main_sha(repo_root),'artifactVerification':[{'file':a.path.name,'sha256':a.sha256,'matchesCommittedWrapperDigest':a.known_label is not None,'committedWrapperLabel':a.known_label,'bytes':a.path.stat().st_size} for a in artifacts],'counts':{'main':len(main_items),'extension':len(ext_items),'field':len(field_items),'total':len(all_items)},'allAudioHashesVerified':True,'reviewPrefilled':False,'provenance':[*main_prov,*ext_prov,*field_prov],'items':all_items,'rule':'Source-byte SHA verification and human review evidence do not imply source/master/runtime/release approval.'}
        atomic_write(staging/'AUDITION_MANIFEST.json',(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n').encode())
        readme="""# PROJECT ØEN — Audio source audition pack\n\nOpen `review.html` locally. Every included source file/member is copied byte-for-byte and SHA-256 checked against the committed receipts/shortlist.\n\nExports are compatible with `normalize_audio_human_review.py` and `normalize_audio_field_review.py`. A successful normalizer run still produces `human-review-evidence-unapproved`; it never promotes a source automatically.\n\n`AUDITION_MANIFEST.json` records source hashes plus artifact-wrapper identities. Use `--require-pinned-artifact-wrapper` only when exact historical wrapper identity is required.\n"""
        atomic_write(staging/'README.md',readme.encode())
        if out_dir.exists(): shutil.rmtree(out_dir)
        shutil.copytree(staging,out_dir)
    return manifest

def main_cli()->int:
    parser=argparse.ArgumentParser(description='Build a hash-bound PROJECT OEN human audio source audition pack from acquired GitHub artifact ZIPs.')
    parser.add_argument('--repo-root',type=Path,default=ROOT); parser.add_argument('--artifact',type=Path,action='append',required=True); parser.add_argument('--out-dir',type=Path,required=True); parser.add_argument('--zip-output',type=Path); parser.add_argument('--require-pinned-artifact-wrapper',action='store_true'); parser.add_argument('--source-main-sha')
    args=parser.parse_args()
    try:
        manifest=build_pack(args.repo_root.resolve(),[p.resolve() for p in args.artifact],args.out_dir.resolve(),require_pinned_artifact_wrapper=args.require_pinned_artifact_wrapper,source_sha=args.source_main_sha)
        if args.zip_output:
            zip_path=args.zip_output.resolve(); zip_path.parent.mkdir(parents=True,exist_ok=True)
            if zip_path.exists(): zip_path.unlink()
            with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
                for path in sorted(args.out_dir.resolve().rglob('*')):
                    if path.is_file(): archive.write(path,path.relative_to(args.out_dir.resolve()).as_posix())
        c=manifest['counts']; print(f"OK audition pack: {c['total']} sources ({c['main']} main, {c['extension']} extension, {c['field']} field); all source hashes verified"); return 0
    except PackError as exc:
        print(f'ERROR: {exc}'); return 1

if __name__=='__main__': raise SystemExit(main_cli())
