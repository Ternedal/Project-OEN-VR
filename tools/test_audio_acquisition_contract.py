#!/usr/bin/env python3
"""Offline QA for PROJECT ØEN natural-audio acquisition contracts.

No network access and no audio acquisition happens in this test. It verifies that the
candidate/listening pipeline cannot silently drift into a produced/release state.
"""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from urllib.parse import urlparse

import acquire_audio_sources

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "content" / "audio" / "acquisition_candidates.source.json"
LISTENING = ROOT / "content" / "audio" / "listening_qa.source.json"
GITIGNORE = ROOT / ".gitignore"


class AudioAcquisitionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.candidate_data = json.loads(CANDIDATES.read_text(encoding="utf-8"))
        cls.listening_data = json.loads(LISTENING.read_text(encoding="utf-8"))
        cls.candidates = cls.candidate_data["candidates"]

    def test_candidate_lane_is_explicitly_not_acquired(self) -> None:
        self.assertEqual("license-verified-candidates-not-acquired", self.candidate_data["status"])
        self.assertTrue(self.candidate_data["policy"]["sourceFilesRequiredBeforeProducedStatus"])
        self.assertEqual("CC0", self.candidate_data["policy"]["preferredLicense"])

    def test_all_accepted_candidates_are_unique_cc0_with_source_evidence(self) -> None:
        targets = []
        pages = []
        for item in self.candidates:
            self.assertEqual("CC0", item["license"], item.get("target"))
            self.assertTrue(item.get("target"))
            self.assertTrue(item.get("provider"))
            self.assertTrue(item.get("title"))
            self.assertTrue(item.get("use"))
            self.assertTrue(item.get("caveat"))
            self.assertIn(item.get("priority"), {"A", "B"})
            parsed = urlparse(item["sourcePage"])
            self.assertEqual("https", parsed.scheme)
            self.assertTrue(parsed.netloc)
            targets.append(item["target"])
            pages.append(item["sourcePage"])
        self.assertEqual(len(targets), len(set(targets)), "candidate target IDs must be unique")
        self.assertEqual(len(pages), len(set(pages)), "source pages must not be duplicated accidentally")

    def test_direct_download_metadata_is_safe_and_unambiguous(self) -> None:
        direct = [item for item in self.candidates if item.get("directDownload")]
        self.assertGreater(len(direct), 0, "at least one reproducible direct-download source is required")
        filenames = []
        for item in direct:
            filename = item.get("filename")
            self.assertIsInstance(filename, str)
            self.assertEqual(filename, Path(filename).name, "filename must not contain directories")
            self.assertNotIn("..", filename)
            parsed = urlparse(item["directDownload"])
            self.assertEqual("https", parsed.scheme)
            self.assertTrue(parsed.netloc)
            filenames.append(filename)
        self.assertEqual(len(filenames), len(set(filenames)), "direct filenames must be unique")

    def test_acquisition_tool_stays_in_ignored_private_output(self) -> None:
        expected = ROOT / "PrivateContent" / "AudioSourceIncoming"
        self.assertEqual(expected, acquire_audio_sources.DEFAULT_OUTPUT)
        ignored = GITIGNORE.read_text(encoding="utf-8")
        self.assertIn("PrivateContent/", ignored)
        self.assertNotIn("source_audio", str(acquire_audio_sources.DEFAULT_OUTPUT.relative_to(ROOT)))

    def test_acquisition_tool_reads_the_authoritative_candidate_source(self) -> None:
        self.assertEqual(CANDIDATES, acquire_audio_sources.CANDIDATES)
        loaded = acquire_audio_sources.load_candidates()
        self.assertEqual(len(self.candidates), len(loaded))
        self.assertEqual(
            {item["target"] for item in self.candidates},
            {item["target"] for item in loaded},
        )

    def test_sha256_helper_is_deterministic(self) -> None:
        payload = b"PROJECT-OEN-audio-acquisition-contract\n"
        expected = hashlib.sha256(payload).hexdigest()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "source.bin"
            path.write_bytes(payload)
            self.assertEqual(expected, acquire_audio_sources.sha256_file(path))

    def test_listening_gate_has_no_shortcut_to_produced_or_release(self) -> None:
        states = self.listening_data["states"]
        self.assertEqual(
            [
                "candidate",
                "acquired-original-not-listening-approved",
                "listening-rejected",
                "source-approved",
                "derived-master-approved",
                "Unity-integrated",
                "release-approved",
            ],
            states,
        )
        source_requirements = self.listening_data["approvalRule"]["sourceApprovedRequires"]
        derived_requirements = self.listening_data["approvalRule"]["derivedMasterApprovedRequires"]
        self.assertIn("license evidence preserved", source_requirements)
        self.assertIn("SHA-256 preserved", source_requirements)
        self.assertIn("all applicable required listening checks completed", source_requirements)
        self.assertIn("source-approved original", derived_requirements)
        self.assertIn("listening QA repeated on derived file", derived_requirements)

    def test_rejected_sources_keep_a_reason(self) -> None:
        rejected = self.candidate_data.get("rejectedExamples")
        self.assertIsInstance(rejected, list)
        self.assertGreater(len(rejected), 0)
        for item in rejected:
            self.assertTrue(item.get("title"))
            self.assertTrue(item.get("reason"))


if __name__ == "__main__":
    unittest.main()
