#!/usr/bin/env python3
from __future__ import annotations
import json, shutil, tempfile, unittest
from pathlib import Path
from validate_ember_carrier_source import validate, ROOT

class Tests(unittest.TestCase):
    def test_valid_source(self): self.assertEqual(validate(ROOT), [])
    def test_missing_obj_fails(self):
        with tempfile.TemporaryDirectory() as td:
            dst=Path(td); shutil.copytree(ROOT/"source_art", dst/"source_art"); shutil.copytree(ROOT/"content", dst/"content")
            (dst/"source_art/items/a5/ITM_EMBER_CARRIER_001.obj").unlink(); self.assertTrue(any("missing" in e for e in validate(dst)))
    def test_state_drift_fails(self):
        with tempfile.TemporaryDirectory() as td:
            dst=Path(td); shutil.copytree(ROOT/"source_art", dst/"source_art"); shutil.copytree(ROOT/"content", dst/"content")
            p=dst/"content/items/itm_ember_carrier.source.json"; data=json.loads(p.read_text(encoding="utf-8")); data["logicalStates"][1]["id"]="hot"; p.write_text(json.dumps(data),encoding="utf-8")
            self.assertTrue(any("state order" in e for e in validate(dst)))

if __name__=="__main__": unittest.main()
