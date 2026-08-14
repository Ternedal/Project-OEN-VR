#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("builder", HERE / "build_audio_source_audition_pack.py")
assert SPEC and SPEC.loader
sys.path.insert(0, str(HERE))
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def make_zip(path: Path, files: dict[str, bytes]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED) as z:
        for name, data in files.items():
            z.writestr(name, data)
    return builder.sha256_file(path)


class BuilderTests(unittest.TestCase):
    def fixture(self, root: Path, *, stale_member: bool = False, omit_field: bool = False):
        main_bytes = {"wind.wav": b"wind-source", "rain.flac": b"rain-source", "fire.wav": b"fire-source"}
        ocean = b"ocean-source"; wood_member = b"wood-member"; cloth_member = b"cloth-member"; field_a = b"field-a"; field_b = b"field-b"
        nested_wood = root / "wood.zip"; nested_cloth = root / "cloth.zip"
        make_zip(nested_wood, {"floor_creak1.wav": wood_member}); make_zip(nested_cloth, {"OGG/cloth1.ogg": cloth_member})
        wood_archive = nested_wood.read_bytes(); cloth_archive = nested_cloth.read_bytes()
        base_artifact = root / "base.zip"; base_digest = make_zip(base_artifact, {f"originals/{k}": v for k, v in main_bytes.items()})
        ext_artifact = root / "extension.zip"; ext_digest = make_zip(ext_artifact, {"AudioSourceExtension/originals/ocean.flac": ocean,"AudioSourceExtension/originals/woodpack.zip": wood_archive,"AudioSourceExtension/originals/clothpack.zip": cloth_archive})
        field_artifact = root / "field.zip"; field_files = {"originals/field_a.ogg": field_a}
        if not omit_field: field_files["originals/field_b.wav"] = field_b
        field_digest = make_zip(field_artifact, field_files)
        content = root / "content/audio"; tools = root / "tools"; tools.mkdir(parents=True, exist_ok=True)
        (tools / "audio_source_audition_template.html").write_text('<html><script>const D=__AUDITION_DATA_JSON__;</script></html>', encoding="utf-8")
        main_records = []
        for target, filename in [("AMB_WIND_WORLD","wind.wav"),("AMB_RAIN_ALT","rain.flac"),("SFX_FIRE_ALT","fire.wav")]:
            main_records.append({"target":target,"filename":filename,"provider":"Fixture","license":"CC0","sha256":sha(main_bytes[filename]),"technical":{"codec":"pcm","sampleRateHz":48000,"channels":2,"bitDepth":24,"durationSeconds":2.0},"status":"acquired-original-not-listening-approved"})
        write_json(content / "acquisition_receipt.source.json", {"workflow":{"artifactSha256":base_digest},"records":main_records})
        write_json(content / "acquisition_extension_receipt.source.json", {"workflow":{"artifactSha256":ext_digest},"records":[{"target":"AMB_OCEAN_ALT","filename":"ocean.flac","provider":"Fixture","license":"CC0","sha256":sha(ocean),"technical":{"codec":"flac","sampleRateHz":44100,"channels":2,"bitDepth":24,"durationSeconds":4.0}},{"target":"SFX_WOOD_PACK_ALT","filename":"woodpack.zip","provider":"Fixture","license":"CC0","sha256":sha(wood_archive)},{"target":"SFX_CLOTH_PACK_ALT","filename":"clothpack.zip","provider":"Fixture","license":"CC0","sha256":sha(cloth_archive)}]})
        write_json(content / "acquisition_extension_member_shortlist.source.json", {"members":[{"archiveTarget":"SFX_WOOD_PACK_ALT","path":"floor_creak1.wav","sha256":("0"*64 if stale_member else sha(wood_member)),"codec":"pcm_s16le","sampleRateHz":48000,"channels":1,"candidateUse":["wood"]},{"archiveTarget":"SFX_CLOTH_PACK_ALT","path":"OGG/cloth1.ogg","sha256":sha(cloth_member),"codec":"vorbis","sampleRateHz":48000,"channels":2,"candidateUse":["cloth"]}]})
        write_json(content / "acquisition_field_backlog_receipt.source.json", {"evidenceRuns":[{"runId":123,"artifactDigest":f"sha256:{field_digest}"}],"records":[{"target":"FIELD_A","runtimeEventCandidate":"SFX_A","filename":"field_a.ogg","provider":"Fixture","license":"CC0","sha256":sha(field_a),"status":"acquired-original-not-listening-approved","technicalProbe":{"codec":"vorbis","sampleRateHz":44100,"channels":2,"durationSeconds":3.0},"objectiveQa":{"note":"listen"}},{"target":"FIELD_B","runtimeEventCandidate":"SFX_B","filename":"field_b.wav","provider":"Fixture","license":"CC0","sha256":sha(field_b),"status":"acquired-original-not-listening-approved","technicalProbe":{"codec":"pcm_s16le","sampleRateHz":44100,"channels":1,"durationSeconds":1.0},"objectiveQa":{"note":"listen"}}]})
        write_json(content / "listening_review_targets.source.json", {"records":[{"target":target,"reviewWindows":[{"label":"typical","startSeconds":0,"endSeconds":1}],"peakInspection":{"timeSeconds":1}} for target in builder.MAIN_CHECKS]})
        all_checks = sorted({c for checks in builder.MAIN_CHECKS.values() for c in checks}); write_json(content / "listening_qa.source.json", {"requiredListeningChecks":[{"id":cid,"question":f"Question {cid}?"} for cid in all_checks]})
        return [base_artifact, ext_artifact, field_artifact]

    def test_builds_hash_bound_pack(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); artifacts = self.fixture(root); out = root / "out"; manifest = builder.build_pack(root, artifacts, out, source_sha="f" * 40)
            self.assertEqual(manifest["counts"], {"main":3,"extension":3,"field":2,"total":8}); self.assertTrue(manifest["allAudioHashesVerified"]); self.assertFalse(manifest["reviewPrefilled"])
            self.assertEqual(json.loads((out / "main_review.template.json").read_text())["status"], builder.MAIN_STATUS); self.assertEqual(json.loads((out / "extension_review.template.json").read_text())["status"], builder.EXT_STATUS); self.assertEqual(json.loads((out / "field_review.template.json").read_text())["status"], builder.FIELD_STATUS)
            self.assertEqual((out / "audio/wood/floor_creak1.wav").read_bytes(), b"wood-member"); self.assertEqual((out / "audio/cloth/cloth1.ogg").read_bytes(), b"cloth-member")
            html = (out / "review.html").read_text(encoding="utf-8"); self.assertNotIn("__AUDITION_DATA_JSON__", html); self.assertIn(builder.MAIN_STATUS, html); self.assertTrue(all(row["matchesCommittedWrapperDigest"] for row in manifest["artifactVerification"]))

    def test_rejects_stale_nested_member_hash(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); artifacts=self.fixture(root,stale_member=True)
            with self.assertRaisesRegex(builder.PackError,"sha mismatch"): builder.build_pack(root,artifacts,root/"out")

    def test_rejects_missing_expected_source(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); artifacts=self.fixture(root,omit_field=True)
            with self.assertRaisesRegex(builder.PackError,"Missing exact source bytes"): builder.build_pack(root,artifacts,root/"out")

    def test_source_hash_can_accept_new_wrapper_but_strict_mode_rejects(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); artifacts=self.fixture(root); original=artifacts[0]; repacked=root/"base-repacked.zip"
            with zipfile.ZipFile(original) as src, zipfile.ZipFile(repacked,"w",compression=zipfile.ZIP_STORED) as dst:
                for name in src.namelist(): dst.writestr(name,src.read(name))
                dst.writestr("wrapper-note.txt",b"new artifact wrapper")
            new_artifacts=[repacked,*artifacts[1:]]; manifest=builder.build_pack(root,new_artifacts,root/"out"); row=next(r for r in manifest["artifactVerification"] if r["file"]=="base-repacked.zip"); self.assertFalse(row["matchesCommittedWrapperDigest"])
            with self.assertRaisesRegex(builder.PackError,"Unpinned artifact wrapper rejected"): builder.build_pack(root,new_artifacts,root/"strict",require_pinned_artifact_wrapper=True)

if __name__ == "__main__": unittest.main(verbosity=2)
