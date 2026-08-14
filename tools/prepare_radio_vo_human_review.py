#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from radio_vo_human_review_support import DEFAULT_SESSION, ROOT, ReviewError, load_context


def build_template(context: dict) -> dict:
    contract = context["contract"]
    checks = contract["checkIds"]
    cues = []
    for cue in context["cues"]:
        cues.append({
            "cueId": cue["cueId"],
            "decision": "",
            "selectedFilename": "",
            "checks": {check: {"result": "", "note": ""} for check in checks},
            "note": "",
        })
    return {
        "version": contract["reviewExport"]["version"],
        "status": contract["reviewExport"]["status"],
        "reviewedAt": "",
        "reviewerAlias": "",
        "rightsDecision": "",
        "rightsNote": "",
        "bindings": context["bindings"],
        "cues": cues,
    }


def render_html(context: dict, template: dict) -> str:
    payload = json.dumps({"context": context["cues"], "contract": context["contract"], "review": template}, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    return """<!doctype html><html lang="da"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PROJECT ØEN — Radio VO human review</title>
<style>body{font-family:system-ui,sans-serif;max-width:1120px;margin:auto;padding:24px;background:#f2f0e9;color:#202522}header,.card{background:#fff;border:1px solid #d6d5cf;border-radius:14px;padding:18px;margin:14px 0}.line{font-size:1.4rem;font-weight:750}.take{border:1px solid #ddd;border-radius:10px;padding:10px;margin:8px 0}audio{width:100%}.grid{display:grid;grid-template-columns:220px 180px 1fr;gap:8px;align-items:center;margin:7px 0}select,input,textarea{font:inherit;padding:7px;border:1px solid #b9bcb5;border-radius:7px}textarea{width:98%;min-height:54px}.sticky{position:sticky;bottom:8px;padding:10px;background:#f2f0e9e8;backdrop-filter:blur(4px)}button{font:inherit;font-weight:700;padding:10px 15px;border:1px solid #999;border-radius:9px;background:white}.warn{background:#fff2c8;padding:12px;border-radius:9px}@media(max-width:700px){.grid{grid-template-columns:1fr}}</style>
<header><h1>PROJECT ØEN — Radio VO human take review</h1><p>Lyt til T01/T02/T03 pr. cue. Dokumentér det du faktisk hører. Et negativt resultat er gyldig evidens; vælg ikke en take bare for at gøre pakken komplet.</p><p class="warn"><b>Dette er review-evidens, ikke automatisk approval.</b> Human review må ende i <code>needs-rerecord</code>. Claude ejer senere radio-treatment/runtime/Quest QA.</p><div class="grid"><label>Reviewer alias</label><input id="reviewer"><span></span><label>Rettigheder/provenance</label><select id="rights"><option></option><option>accepted</option><option>rejected</option><option>needs-review</option></select><input id="rightsNote" placeholder="Rettighedsnote"></div></header><main id="cards"></main><div class="sticky"><button onclick="downloadReview()">Eksportér radio_vo_human_review.json</button></div>
<script>const D=__DATA__;const R=D.review;const checkLabels={PRONUNCIATION:'Dansk udtale',DELIVERY:'Tone/delivery',SEMANTIC_PARITY:'Semantisk parity',NO_CRITICAL_ADLIB:'Ingen kritisk ad-lib'};function e(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}function render(){const host=document.getElementById('cards');D.context.forEach((cue,i)=>{let takes=cue.candidates.map(t=>`<div class="take"><label><input type="radio" name="sel${i}" value="${e(t.filename)}"> <b>T${String(t.take).padStart(2,'0')}</b> — <code>${e(t.filename)}</code></label><audio controls preload="metadata" src="takes/${encodeURIComponent(t.filename)}"></audio><small>SHA ${e(t.sha256)} · ${e(t.durationSec)} s · peak ${e(t.peakDbfs)} dBFS</small></div>`).join('');let checks=D.contract.checkIds.map(c=>`<div class="grid"><label>${e(checkLabels[c]||c)}</label><select data-i="${i}" data-c="${c}" data-k="result"><option></option><option>pass</option><option>fail</option><option>needs-more-listening</option></select><input data-i="${i}" data-c="${c}" data-k="note" placeholder="Konkret observation"></div>`).join('');host.insertAdjacentHTML('beforeend',`<article class="card"><h2>${e(cue.cueId)}</h2><p class="line">${e(cue.spokenText)}</p><p><b>Delivery:</b> ${e(cue.delivery)}<br><b>Critical semantic:</b> ${e(cue.criticalSemantic)}</p>${takes}<div class="grid"><label>Beslutning</label><select data-i="${i}" data-k="decision"><option></option><option>select</option><option>needs-rerecord</option><option>needs-more-listening</option></select><input data-i="${i}" data-k="note" placeholder="Samlet cue-note"></div>${checks}</article>`)});host.querySelectorAll('input[type=radio]').forEach(el=>el.onchange=()=>{const i=+el.name.slice(3);R.cues[i].selectedFilename=el.value});host.querySelectorAll('[data-i]').forEach(el=>el.oninput=()=>{const r=R.cues[+el.dataset.i];if(el.dataset.c)r.checks[el.dataset.c][el.dataset.k]=el.value;else r[el.dataset.k]=el.value})}document.getElementById('reviewer').oninput=e=>R.reviewerAlias=e.target.value;document.getElementById('rights').oninput=e=>R.rightsDecision=e.target.value;document.getElementById('rightsNote').oninput=e=>R.rightsNote=e.target.value;function downloadReview(){R.reviewedAt=new Date().toISOString();const b=new Blob([JSON.stringify(R,null,2)+'\n'],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='radio_vo_human_review.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)}render();</script></html>""".replace("__DATA__", payload)


def prepare(session_root: Path, repo_root: Path = ROOT) -> dict:
    context = load_context(session_root, repo_root)
    template = build_template(context)
    session_root = session_root.resolve()
    (session_root / "radio_vo_human_review.template.json").write_text(json.dumps(template, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (session_root / "radio_vo_human_review.html").write_text(render_html(context, template), encoding="utf-8")
    return template


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare hash-bound human A/B review for technically accepted PROJECT OEN radio VO takes.")
    parser.add_argument("--session", type=Path, default=ROOT / DEFAULT_SESSION)
    args = parser.parse_args()
    try:
        result = prepare(args.session)
    except ReviewError as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"Prepared human review for {len(result['cues'])} radio cues: {args.session.resolve() / 'radio_vo_human_review.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
