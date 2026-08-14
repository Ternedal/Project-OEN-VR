#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from audio_audition_pack_support import (
    PackError,
    contract_paths,
    expected_artifact_digests,
    load_field_receipts,
    load_json,
    merge_field_receipts,
    records_index,
    require_sha,
)
from audio_audition_pack_main import MAIN_CHECKS, check_questions, navigation_index

ROOT = Path(__file__).resolve().parents[1]


def validate(root: Path = ROOT) -> dict[str, int]:
    paths = contract_paths(root)
    main = load_json(paths['main'])
    ext = load_json(paths['extension'])
    shortlist = load_json(paths['shortlist'])
    field_receipts = load_field_receipts(root)
    field = merge_field_receipts(field_receipts)
    targets = load_json(paths['targets'])
    qa = load_json(paths['qa'])
    expected_artifact_digests(main, ext, *field_receipts)
    check_questions(qa)

    main_records = records_index(main, 'main receipt')
    if set(main_records) != set(MAIN_CHECKS):
        raise PackError(f'main target drift: {sorted(main_records)}')
    nav = navigation_index(targets)
    missing_nav = sorted(set(MAIN_CHECKS) - set(nav))
    if missing_nav:
        raise PackError(f'main listening navigation missing: {missing_nav}')

    ext_records = records_index(ext, 'extension receipt')
    required_ext = {'AMB_OCEAN_ALT', 'SFX_WOOD_PACK_ALT', 'SFX_CLOTH_PACK_ALT'}
    missing_ext = sorted(required_ext - set(ext_records))
    if missing_ext:
        raise PackError(f'extension receipt missing: {missing_ext}')
    for target in required_ext:
        require_sha(ext_records[target].get('sha256'), f'extension receipt {target}')

    members = shortlist.get('members')
    if not isinstance(members, list) or not members:
        raise PackError('extension shortlist must contain members')
    for member in members:
        if not isinstance(member, dict):
            raise PackError('extension shortlist contains invalid member')
        target = member.get('archiveTarget')
        source_path = member.get('path')
        if target not in {'SFX_WOOD_PACK_ALT', 'SFX_CLOTH_PACK_ALT'} or not isinstance(source_path, str) or not source_path:
            raise PackError(f'unsupported extension member identity: {target}/{source_path}')
        require_sha(member.get('sha256'), f'extension member {target}/{source_path}')

    field_records = records_index(field, 'field receipts')
    if not field_records:
        raise PackError('field receipts have no acquired records')
    for target, record in field_records.items():
        for key in ('filename', 'runtimeEventCandidate'):
            if not isinstance(record.get(key), str) or not record[key]:
                raise PackError(f'field receipt {target}: missing {key}')
        require_sha(record.get('sha256'), f'field receipt {target}')
        if record.get('status') != 'acquired-original-not-listening-approved':
            raise PackError(f'field receipt {target}: source status drift')

    if root == ROOT and len(field_records) != 9:
        raise PackError(f'current field source count must be 9, got {len(field_records)}')

    html = paths['html'].read_text(encoding='utf-8')
    if html.count('__AUDITION_DATA_JSON__') != 1:
        raise PackError('audio audition HTML template must contain exactly one data marker')

    return {'main': len(main_records), 'extensionMembers': len(members) + 1, 'field': len(field_records)}


def main() -> int:
    try:
        counts = validate()
        print(f"OK audition contracts: {counts['main']} main, {counts['extensionMembers']} extension, {counts['field']} field")
        return 0
    except PackError as exc:
        print(f'ERROR: {exc}')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
