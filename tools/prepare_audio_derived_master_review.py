#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from audio_derived_master_support import ROOT, DerivedError, load_review_context


def build_template(context: dict) -> dict:
    contract = context["contract"]
    records = []
    for master in context["technicalReceipt"]["records"]:
        checks = {check_id: {"value": None if spec["type"] == "rating" else "", "note": ""} for check_id, spec in context["typedChecks"].items()}
        records.append({
            "masterId": master["masterId"],
            "sourceKey": master["sourceKey"],
            "sourceApprovedSha256": master["sourceApprovedSha256"],
            "filename": master["filename"],
            "derivedSha256": master["derivedSha256"],
            "intendedUse": master["intendedUse"],
            "editRecipe": master["editRecipe"],
            "decision": "",
            "checks": checks,
            "overallNote": "",
        })
    return {
        "version": 1,
        "status": contract["humanReview"]["exportStatus"],
        "reviewedAt": "",
        "reviewerAlias": "",
        "bindings": {"technicalReceiptSha256": context["technicalReceiptSha256"], "derivedHashes": {x["masterId"]: x["derivedSha256"] for x in context["technicalReceipt"]["records"]}},
        "records": records,
    }


def render_html(context: dict, template: dict) -> str:
    payload = json.dumps({"typedChecks": context["typedChecks"], "decisions": context["contract"]["humanReview"]["decisionValues"], "review": template}, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    return """<!doctype html><html lang="da"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PROJECT ØEN — Derived master re-listening</title><style>body{font-family:system-ui,sans-serif;max-width:1160px;margin:auto;padding:24px;background:#f2f0e9;color:#202522}header,.card{background:white;border:1px solid #d6d5cf;border-radius:14px;padding:18px;margin:14px 0}.grid{display:grid;grid-template-columns:240px 180px 1fr;gap:8px;align-items:center;margin:8px 0}audio{width:100%}select,input,textarea{font:inherit;padding:7px;border:1px solid #b9bcb5;border-radius:7px}textarea{width:98%;min-height:58px}.sticky{position:sticky;bottom:8px;padding:10px;background:#f2f0e9e8;backdrop-filter:blur(4px)}button{font:inherit;font-weight:700;padding:10px 15px;border:1px solid #999;border-radius:9px;background:white}.warn{background:#fff2c8;padding:12px;border-radius:9px}.hash{font-family:ui-monospace,monospace;font-size:.78rem;word-break:break-all}@media(max-width:760px){.grid{grid-template-columns:1fr}}</style><header><h1>PROJECT ØEN — Derived master human re-listening</h1><p>Den derived WAV har ny identitet og skal lyttes igen. Source-approval arves ikke gennem et edit.</p><p class="warn"><b>Negativt resultat er gyldig evidens.</b> Vælg reject/needs-more-listening hvis edit, loop, noise eller materialefit ikke holder.</p><div class="grid"><label>Reviewer alias</label><input id="reviewer"><span></span></div></header><main id="cards"></main><div class="sticky"><button onclick="downloadReview()">Eksportér derived_master_review.json</button></div><script>const D=__DATA__;const R=D.review;function e(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}function ctl(i,id,s){if(s.type==='rating')return `<select data-i="${i}" data-c="${id}" data-k="value"><option value=""></option><option>1</option><option>2</option><option>3</option><option>4</option><option>5</option></select>`;return `<select data-i="${i}" data-c="${id}" data-k="value"><option></option>${s.allowed.map(x=>`<option>${e(x)}</option>`).join('')}</select>`}function render(){const host=document.getElementById('cards');R.records.forEach((r,i)=>{let checks=Object.entries(D.typedChecks).map(([id,s])=>`<div class="grid"><label>${e(id)}</label>${ctl(i,id,s)}<input data-i="${i}" data-c="${id}" data-k="note" placeholder="Observation"></div>`).join('');host.insertAdjacentHTML('beforeend',`<article class="card"><h2>${e(r.masterId)}</h2><p>${e(r.intendedUse)} · source=${e(r.sourceKey)}</p><p class="hash">Derived SHA ${e(r.derivedSha256)}</p><audio controls preload="metadata" src="${encodeURIComponent(r.filename)}"></audio><details><summary>Edit recipe</summary><pre>${e(JSON.stringify(r.editRecipe,null,2))}</pre></details><div class="grid"><label>Decision</label><select data-i="${i}" data-k="decision"><option></option>${D.decisions.map(x=>`<option>${e(x)}</option>`).join('')}</select><textarea data-i="${i}" data-k="overallNote" placeholder="Samlet note"></textarea></div>${checks}</article>`)});host.querySelectorAll('[data-i]').forEach(el=>el.oninput=()=>{const r=R.records[+el.dataset.i];if(el.dataset.c){let v=el.value;if(D.typedChecks[el.dataset.c].type==='rating')v=v===''?null:Number(v);r.checks[el.dataset.c][el.dataset.k]=v}else r[el.dataset.k]=el.value})}document.getElementById('reviewer').oninput=e=>R.reviewerAlias=e.target.value;function downloadReview(){R.reviewedAt=new Date().toISOString();const b=new Blob([JSON.stringify(R,null,2)+'\n'],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='derived_master_review.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)}render();</script></html>""".replace("__DATA__", payload)


def prepare(technical_receipt: Path, submission: Path, source_receipt: Path, masters_dir: Path, repo_root: Path = ROOT) -> dict:
    context = load_review_context(technical_receipt, submission, source_receipt, masters_dir, repo_root)
    template = build_template(context)
    masters_dir = masters_dir.resolve()
    (masters_dir / "derived_master_review.template.json").write_text(json.dumps(template, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (masters_dir / "derived_master_review.html").write_text(render_html(context, template), encoding="utf-8")
    return template


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare human re-listening review for technically accepted PROJECT OEN derived masters.")
    parser.add_argument("--technical-receipt", type=Path, required=True)
    parser.add_argument("--submission", type=Path, required=True)
    parser.add_argument("--source-approved-receipt", type=Path, required=True)
    parser.add_argument("--masters-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = prepare(args.technical_receipt.resolve(), args.submission.resolve(), args.source_approved_receipt.resolve(), args.masters_dir.resolve())
    except DerivedError as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"Prepared derived master re-listening for {len(result['records'])} master(s) in {args.masters_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
