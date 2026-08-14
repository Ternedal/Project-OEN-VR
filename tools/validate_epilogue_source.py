#!/usr/bin/env python3
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
SVG=ROOT/"source_art/environment/c1/ENV_EPILOGUE_001.svg"
DATA=ROOT/"content/environment/env_epilogue.source.json"
def main():
    errors=[]
    text=SVG.read_text(encoding="utf-8")
    data=json.loads(DATA.read_text(encoding="utf-8"))
    for token in ["Storm release","Camp history remains","Signal causality","Dawn direction","Epilogue focus"]:
        if token not in text: errors.append(f"SVG missing {token}")
    if data.get("productIntent",{}).get("zoneRule")!="existing camp after storm; not a new gameplay zone":
        errors.append("zone rule changed")
    for token in ["hard camera lock","forced edge movement","private content before deliberate reveal"]:
        if token not in data.get("productIntent",{}).get("mustNotRequire",[]):
            errors.append(f"missing guard {token}")
    if errors:
        for e in errors: print("ERROR:",e)
        return 1
    print("Epilogue source reference OK.")
    return 0
if __name__=="__main__": raise SystemExit(main())
