from __future__ import annotations

import hashlib
import io
import json
import subprocess
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

MAIN_RECEIPT = Path('content/audio/acquisition_receipt.source.json')
EXT_RECEIPT = Path('content/audio/acquisition_extension_receipt.source.json')
EXT_SHORTLIST = Path('content/audio/acquisition_extension_member_shortlist.source.json')
FIELD_RECEIPT = Path('content/audio/acquisition_field_backlog_receipt.source.json')
LISTENING_TARGETS = Path('content/audio/listening_review_targets.source.json')
LISTENING_QA = Path('content/audio/listening_qa.source.json')
HTML_TEMPLATE = Path('tools/audio_source_audition_template.html')

class PackError(RuntimeError):
    pass

@dataclass(frozen=True)
class Artifact:
    path: Path
    sha256: str
    known_label: str | None

@dataclass(frozen=True)
class LocatedBytes:
    data: bytes
    artifact: Artifact
    member_path: str

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc:
        raise PackError(f'Cannot parse {path}: {exc}') from exc
    if not isinstance(value, dict):
        raise PackError(f'{path}: root must be an object')
    return value

def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_bytes(data)
    temp.replace(path)

def clean_hex(value: str) -> str:
    return value.removeprefix('sha256:').strip().lower()

def require_sha(value: Any, owner: str) -> str:
    if not isinstance(value, str) or len(clean_hex(value)) != 64:
        raise PackError(f'{owner}: invalid sha256')
    return clean_hex(value)

def source_main_sha(repo_root: Path) -> str | None:
    try:
        result = subprocess.run(['git','-C',str(repo_root),'rev-parse','HEAD'], check=True, capture_output=True, text=True, timeout=5)
        sha = result.stdout.strip()
        return sha if len(sha) == 40 else None
    except Exception:
        return None

def contract_paths(repo_root: Path) -> dict[str, Path]:
    return {
        'main': repo_root / MAIN_RECEIPT, 'extension': repo_root / EXT_RECEIPT,
        'shortlist': repo_root / EXT_SHORTLIST, 'field': repo_root / FIELD_RECEIPT,
        'targets': repo_root / LISTENING_TARGETS, 'qa': repo_root / LISTENING_QA,
        'html': repo_root / HTML_TEMPLATE,
    }

def expected_artifact_digests(main: dict[str, Any], ext: dict[str, Any], field: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for data, label in ((main,'main-receipt'),(ext,'extension-receipt')):
        workflow = data.get('workflow')
        if isinstance(workflow, dict) and workflow.get('artifactSha256'):
            out[require_sha(workflow['artifactSha256'], f'{label} artifact')] = label
    runs = field.get('evidenceRuns')
    if not isinstance(runs, list):
        raise PackError('field receipt: evidenceRuns must be a list')
    for run in runs:
        if not isinstance(run, dict):
            raise PackError('field receipt: invalid evidence run')
        out[require_sha(run.get('artifactDigest'), 'field receipt artifact')] = f"field-run-{run.get('runId','unknown')}"
    return out

def index_artifacts(paths: Iterable[Path], known: dict[str,str], require_pinned: bool) -> list[Artifact]:
    result: list[Artifact] = []
    for raw in paths:
        path = raw.resolve()
        if not path.is_file() or not zipfile.is_zipfile(path):
            raise PackError(f'Artifact is missing or not a ZIP: {path}')
        digest = sha256_file(path)
        label = known.get(digest)
        if require_pinned and label is None:
            raise PackError(f'Unpinned artifact wrapper rejected: {path.name} sha256={digest}')
        result.append(Artifact(path, digest, label))
    if not result:
        raise PackError('At least one --artifact ZIP is required')
    return result

def locate_direct(artifacts: list[Artifact], filename: str, expected_sha: str, preferred_labels: set[str] | None = None) -> LocatedBytes:
    matches: list[LocatedBytes] = []
    for artifact in artifacts:
        with zipfile.ZipFile(artifact.path) as archive:
            for name in sorted(archive.namelist()):
                if name.endswith('/') or Path(name).name != filename:
                    continue
                data = archive.read(name)
                if sha256_bytes(data) == expected_sha:
                    matches.append(LocatedBytes(data, artifact, name))
    if not matches:
        raise PackError(f'Missing exact source bytes for {filename} sha256={expected_sha}')
    preferred = preferred_labels or set()
    matches.sort(key=lambda x: (x.artifact.known_label not in preferred, x.artifact.path.name, x.member_path))
    return matches[0]

def extract_nested_member(archive_bytes: bytes, member_path: str, expected_sha: str, owner: str) -> bytes:
    try:
        with zipfile.ZipFile(io.BytesIO(archive_bytes)) as nested:
            if member_path not in nested.namelist():
                raise PackError(f'{owner}: missing nested member {member_path}')
            data = nested.read(member_path)
    except PackError:
        raise
    except Exception as exc:
        raise PackError(f'{owner}: cannot read nested ZIP: {exc}') from exc
    actual = sha256_bytes(data)
    if actual != expected_sha:
        raise PackError(f'{owner}/{member_path}: sha mismatch expected={expected_sha} actual={actual}')
    return data

def records_index(data: dict[str, Any], owner: str) -> dict[str, dict[str, Any]]:
    records = data.get('records')
    if not isinstance(records, list):
        raise PackError(f'{owner}: records must be a list')
    out: dict[str, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get('target'), str):
            raise PackError(f'{owner}: invalid record')
        target = record['target']
        if target in out:
            raise PackError(f'{owner}: duplicate target {target}')
        out[target] = record
    return out

def tech_text(technical: dict[str, Any]) -> str:
    pieces: list[str] = []
    rate,bits,channels,codec = technical.get('sampleRateHz'),technical.get('bitDepth'),technical.get('channels'),technical.get('codec')
    if isinstance(rate, int): pieces.append(f'{rate/1000:g} kHz')
    if isinstance(bits, int): pieces.append(f'{bits}-bit')
    if channels == 1: pieces.append('mono')
    elif channels == 2: pieces.append('stereo')
    if isinstance(codec, str) and codec: pieces.append(codec)
    return ' · '.join(pieces)
