#!/usr/bin/env python3
from __future__ import annotations
import json,shutil,tempfile,unittest
from pathlib import Path
from validate_repair_mallet_source import validate,ROOT
class Tests(unittest.TestCase):
    def test_valid(self): self.assertEqual(validate(ROOT),[])
    def test_missing_svg(self):
        with tempfile.TemporaryDirectory() as td:
            d=Path(td);shutil.copytree(ROOT/"source_art",d/"source_art");shutil.copytree(ROOT/"content",d/"content");(d/"source_art/items/a5/ITM_HAMMER_001.svg").unlink();self.assertTrue(any("missing" in e for e in validate(d)))
    def test_contact_contract(self):
        with tempfile.TemporaryDirectory() as td:
            d=Path(td);shutil.copytree(ROOT/"source_art",d/"source_art");shutil.copytree(ROOT/"content",d/"content");p=d/"content/items/itm_repair_mallet.source.json";data=json.loads(p.read_text());data["contactZones"]=data["contactZones"][:1];p.write_text(json.dumps(data));self.assertTrue(any("two contact" in e for e in validate(d)))
if __name__=="__main__":unittest.main()
