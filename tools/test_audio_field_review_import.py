#!/usr/bin/env python3
import unittest

import normalize_audio_field_review as mod

SHA_A = "a" * 64
SHA_B = "b" * 64


class Tests(unittest.TestCase):
    def context(self):
        return {
            "FIELD_A": {
                "target": "FIELD_A",
                "runtimeEventCandidate": "EVENT_A",
                "filename": "a.ogg",
                "sha256": SHA_A,
                "license": "Public Domain",
                "status": mod.EXPECTED_SOURCE_STATUS,
            },
            "FIELD_B": {
                "target": "FIELD_B",
                "runtimeEventCandidate": "EVENT_B",
                "filename": "b.wav",
                "sha256": SHA_B,
                "license": "CC0",
                "status": mod.EXPECTED_SOURCE_STATUS,
            },
        }

    def payload(self):
        ctx = self.context()
        return {
            "version": 2,
            "status": mod.FIELD_STATUS,
            "createdAt": "2026-08-14T00:00:00Z",
            "bindings": {target: record["sha256"] for target, record in ctx.items()},
            "reviews": {
                "FIELD_A": {"fit": "keep", "notes": "usable candidate"},
                "FIELD_B": {"fit": "maybe", "notes": "needs another listen"},
            },
        }

    def test_field_review_is_hash_bound_and_unapproved(self):
        out = mod.normalize_field(self.payload(), self.context(), require_complete=True)
        self.assertEqual(mod.OUTPUT_STATUS, out["status"])
        self.assertTrue(out["coverage"]["complete"])
        self.assertEqual(2, out["coverage"]["reviewed"])
        self.assertEqual(SHA_A, [r for r in out["records"] if r["target"] == "FIELD_A"][0]["sourceSha256"])

    def test_stale_binding_rejected(self):
        payload = self.payload()
        payload["bindings"]["FIELD_A"] = "0" * 64
        with self.assertRaises(mod.ReviewError):
            mod.normalize_field(payload, self.context())

    def test_unknown_target_rejected(self):
        payload = self.payload()
        payload["reviews"]["NOPE"] = {"fit": "keep", "notes": "bad"}
        with self.assertRaises(mod.ReviewError):
            mod.normalize_field(payload, self.context())

    def test_complete_gate_rejects_partial_review(self):
        payload = self.payload()
        payload["reviews"]["FIELD_B"]["fit"] = ""
        with self.assertRaises(mod.ReviewError):
            mod.normalize_field(payload, self.context(), require_complete=True)

    def test_invalid_decision_rejected(self):
        payload = self.payload()
        payload["reviews"]["FIELD_A"]["fit"] = "approved"
        with self.assertRaises(mod.ReviewError):
            mod.normalize_field(payload, self.context())

    def test_project_receipt_matches_canonical_field_review_group(self):
        receipt_path = mod.ROOT / "content/audio/acquisition_field_backlog_receipt.source.json"
        listening_path = mod.ROOT / "content/audio/listening_qa.source.json"
        if not receipt_path.exists() or not listening_path.exists():
            self.skipTest("repo fixtures unavailable")
        context = mod.field_context(mod.load_json(receipt_path))
        listening = mod.load_json(listening_path)
        groups = {
            group.get("id"): group
            for group in listening.get("reviewGroups", [])
            if isinstance(group, dict) and isinstance(group.get("id"), str)
        }
        field_group = groups.get("FIELD_BACKLOG_ACQUIRED")
        self.assertIsInstance(field_group, dict)
        targets = field_group.get("targets")
        self.assertIsInstance(targets, list)
        self.assertEqual(set(context), set(targets))
        self.assertEqual(len(targets), len(set(targets)))
        self.assertTrue(all(len(record["sha256"]) == 64 for record in context.values()))
        self.assertTrue(all(record["status"] == mod.EXPECTED_SOURCE_STATUS for record in context.values()))


if __name__ == "__main__":
    unittest.main()
