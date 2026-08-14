#!/usr/bin/env python3
import unittest

import normalize_audio_human_review as mod

SHA_A = "a" * 64
SHA_B = "b" * 64
SHA_C = "c" * 64

class Tests(unittest.TestCase):
    def main_context(self):
        return {
            "AMB_WIND_WORLD":{"filename":"wind.wav","sha256":SHA_A},
            "AMB_RAIN_ALT":{"filename":"rain.flac","sha256":SHA_B},
            "SFX_FIRE_ALT":{"filename":"fire.wav","sha256":SHA_C},
        }

    def main_payload(self):
        ctx=self.main_context()
        records=[]
        for target in mod.MAIN_CHECKS:
            records.append({"target":target,"disposition":"candidate-pass","overall":"heard","checks":{i:{"result":"pass","note":"ok"} for i in mod.MAIN_CHECKS[target]}})
        return {"version":2,"status":mod.MAIN_STATUS,"reviewedAt":"2026-08-14T00:00:00Z","bindings":{k:v["sha256"] for k,v in ctx.items()},"records":records}

    def test_main_hash_bound(self):
        out=mod.normalize_main(self.main_payload(),self.main_context(),set().union(*mod.MAIN_CHECKS.values()))
        self.assertEqual(mod.OUTPUT_STATUS,out["status"])
        self.assertTrue(out["coverage"]["complete"])
        self.assertEqual(SHA_A,[r for r in out["records"] if r["target"]=="AMB_WIND_WORLD"][0]["sourceSha256"])

    def test_main_complete_gate_requires_check_results(self):
        p=self.main_payload()
        p["records"][0]["checks"]["CONTAMINATION"]["result"]=""
        with self.assertRaises(mod.ReviewError):
            mod.normalize_main(p,self.main_context(),set().union(*mod.MAIN_CHECKS.values()),require_complete=True)

    def test_main_stale_binding_rejected(self):
        p=self.main_payload(); p["bindings"]["AMB_WIND_WORLD"]="0"*64
        with self.assertRaises(mod.ReviewError):
            mod.normalize_main(p,self.main_context(),set().union(*mod.MAIN_CHECKS.values()))

    def ext_context(self):
        return {
            "audio/ocean/a.flac":{"target":"AMB_OCEAN_ALT","sourcePath":"a.flac","sha256":SHA_A,"sourceKind":"direct-original"},
            "audio/wood/b.wav":{"target":"SFX_WOOD_PACK_ALT","sourcePath":"b.wav","sha256":SHA_B,"sourceKind":"archive-member"},
        }

    def test_extension_partial_is_unapproved(self):
        ctx=self.ext_context()
        p={"version":2,"status":mod.EXT_STATUS,"createdAt":"2026-08-14T00:00:00Z","bindings":{k:v["sha256"] for k,v in ctx.items()},"reviews":{"audio/ocean/a.flac":{"fit":"keep","notes":"usable"}}}
        out=mod.normalize_extension(p,ctx)
        self.assertEqual(mod.OUTPUT_STATUS,out["status"])
        self.assertFalse(out["coverage"]["complete"])
        self.assertEqual(1,out["coverage"]["reviewed"])

    def test_extension_complete_gate(self):
        ctx=self.ext_context(); p={"version":2,"status":mod.EXT_STATUS,"bindings":{k:v["sha256"] for k,v in ctx.items()},"reviews":{}}
        with self.assertRaises(mod.ReviewError): mod.normalize_extension(p,ctx,require_complete=True)

    def test_project_context_when_running_in_repo(self):
        receipt_path = mod.ROOT / "content/audio/acquisition_receipt.source.json"
        if not receipt_path.exists():
            self.skipTest("repo fixtures unavailable in local syntax test")
        canonical = mod.canonical_context(mod.load_json(receipt_path))
        self.assertEqual(set(mod.MAIN_CHECKS), set(canonical))
        extension = mod.extension_context(
            mod.load_json(mod.ROOT / "content/audio/acquisition_extension_receipt.source.json"),
            mod.load_json(mod.ROOT / "content/audio/acquisition_extension_member_shortlist.source.json"),
        )
        self.assertEqual(15, len(extension))
        self.assertTrue(all(len(item["sha256"]) == 64 for item in extension.values()))

    def test_extension_unknown_path_rejected(self):
        ctx=self.ext_context(); p={"version":2,"status":mod.EXT_STATUS,"bindings":{k:v["sha256"] for k,v in ctx.items()},"reviews":{"audio/nope.wav":{"fit":"keep"}}}
        with self.assertRaises(mod.ReviewError): mod.normalize_extension(p,ctx)

if __name__ == '__main__': unittest.main()
