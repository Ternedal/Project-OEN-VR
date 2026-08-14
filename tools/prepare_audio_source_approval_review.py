#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from audio_source_approval_support import APPROVAL_CONTRACT, ROOT, ApprovalError, collect_upstream, expected_bindings, load_json, verify_pack_sources


def build_template(context: dict) -> dict:
    contract = context["contract"]
    records = []
    for key in sorted(context["selected"]):
        source = context["selected"][key]
        checks = {}
        for check_id, spec in contract["typedChecks"].items():
            checks[check_id] = {"value": None if spec["type"] == "rating" else "", "note": ""}
        records.append({
            "sourceKey": key,
            "reviewKind": source["reviewKind"],
            "target": source["target"],
            "reviewPath": source["reviewPath"],
            "sourcePath": source["sourcePath"],
            "sourceSha256": source["sha256"],
            "license": source["license"],
            "sourceDecision": "",
            "checks": checks,
            "overallNote": "",
        })
    return {
        "version": contract["reviewExport"]["version"],
        "status": contract["reviewExport"]["status"],
        "reviewedAt": "",
        "reviewerAlias": "",
        "bindings": expected_bindings(context),
        "records": records,
    }


def render_html(context: dict, template: dict) -> str:
    contract = context["contract"]
    payload = json.dumps({"contract": contract, "review": template}, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    return """<!doctype html><html lang="da"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PROJECT ØEN — Typed source approval review</title>
<style>body{font-family:system-ui,sans-serif;max-width:1160px;margin:auto;padding:24px;background:#f2f0e9;color:#202522}header,.card{background:white;border:1px solid #d6d5cf;border-radius:14px;padding:18px;margin:14px 0}.grid{display:grid;grid-template-columns:240px 180px 1fr;gap:8px;align-items:center;margin:8px 0}audio{width:100%}select,input,textarea{font:inherit;padding:7px;border:1px solid #b9bcb5;border-radius:7px}textarea{width:98%;min-height:58px}.sticky{position:sticky;bottom:8px;padding:10px;background:#f2f0e9e8;backdrop-filter:blur(4px)}button{font:inherit;font-weight:700;padding:10px 15px;border:1px solid #999;border-radius:9px;background:white}.warn{background:#fff2c8;padding:12px;border-radius:9px}.hash{font-family:ui-monospace,monospace;font-size:.78rem;word-break:break-all}@media(max-width:760px){.grid{grid-template-columns:1fr}}</style>
<header><h1>PROJECT ØEN — Typed human source approval</h1><p>Dette er den eksplicitte human gate efter shortlist. MATERIAL_MATCH og VARIATION_VALUE er 1–5 her; de øvrige checks er kategoriske. Et negativt resultat er gyldig evidens.</p><p class="warn"><b>Shortlist ≠ source-approved.</b> Denne reviewfil evaluerer approval-kriterier; selve source-approved materialization sker først i et separat guarded step.</p><div class="grid"><label>Reviewer alias</label><input id="reviewer"><span></span></div></header><main id="cards"></main><div class="sticky"><button onclick="downloadReview()">Eksportér source_approval_review.json</button></div>
<script>const D=__DATA__;const R=D.review;const labels={CONTAMINATION:'Contamination',MATERIAL_MATCH:'Material/context match (1–5)',LOOP_OR_SLICE:'Loop/slice usefulness',NOISE_FLOOR:'Noise floor',TRANSIENT_QUALITY:'Transient quality',SPACE_IDENTITY:'Space identity',VARIATION_VALUE:'Variation value (1–5)',SPEECH_SPACE:'Speech space'};function e(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}function control(i,id,spec){if(spec.type==='rating')return `<select data-i="${i}" data-c="${id}" data-k="value"><option value=""></option><option>1</option><option>2</option><option>3</option><option>4</option><option>5</option></select>`;return `<select data-i="${i}" data-c="${id}" data-k="value"><option></option>${spec.allowed.map(x=>`<option>${e(x)}</option>`).join('')}</select>`}function render(){const host=document.getElementById('cards');R.records.forEach((r,i)=>{let checks=Object.entries(D.contract.typedChecks).map(([id,spec])=>`<div class="grid"><label><b>${e(labels[id]||id)}</b></label>${control(i,id,spec)}<input data-i="${i}" data-c="${id}" data-k="note" placeholder="Konkret observation"></div>`).join('');host.insertAdjacentHTML('beforeend',`<article class="card"><h2>${e(r.target)}</h2><p>${e(r.reviewKind)} · ${e(r.sourcePath)} · license=${e(r.license)}</p><p class="hash">SHA-256 ${e(r.sourceSha256)}</p><audio controls preload="metadata" src="${encodeURI(r.reviewPath)}"></audio><div class="grid"><label>Source decision</label><select data-i="${i}" data-k="sourceDecision"><option></option><option>approve-source</option><option>reject-source</option><option>needs-more-listening</option></select><textarea data-i="${i}" data-k="overallNote" placeholder="Samlet begrundelse"></textarea></div>${checks}</article>`)});host.querySelectorAll('[data-i]').forEach(el=>el.oninput=()=>{const r=R.records[+el.dataset.i];if(el.dataset.c){let v=el.value;if(D.contract.typedChecks[el.dataset.c].type==='rating')v=v===''?null:Number(v);r.checks[el.dataset.c][el.dataset.k]=v}else r[el.dataset.k]=el.value})}document.getElementById('reviewer').oninput=e=>R.reviewerAlias=e.target.value;function downloadReview(){R.reviewedAt=new Date().toISOString();const b=new Blob([JSON.stringify(R,null,2)+'\n'],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='source_approval_review.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)}render();</script></html>""".replace("__DATA__", payload)


def prepare(upstream: list[Path], pack_root: Path, repo_root: Path = ROOT) -> dict:
    context = collect_upstream(upstream, repo_root)
    verify_pack_sources(pack_root, context["selected"])
    template = build_template(context)
    pack_root = pack_root.resolve()
    (pack_root / "source_approval_review.template.json").write_text(json.dumps(template, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (pack_root / "source_approval_review.html").write_text(render_html(context, template), encoding="utf-8")
    return template


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare typed human source approval review from shortlisted PROJECT OEN audio evidence.")
    parser.add_argument("--upstream", type=Path, action="append", required=True, help="Normalized main/extension/field shortlist evidence; repeat as needed")
    parser.add_argument("--pack-root", type=Path, required=True, help="Hash-verified audio audition pack root")
    args = parser.parse_args()
    try:
        result = prepare([x.resolve() for x in args.upstream], args.pack_root)
    except ApprovalError as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"Prepared typed source approval review for {len(result['records'])} shortlisted source(s) in {args.pack_root.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
