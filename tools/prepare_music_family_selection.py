#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from music_family_selection_support import ROOT, SELECTION_CONTRACT, SelectionError, family_groups, load_json, load_normalized_audition, sha256_file


def verify_candidate_dir(candidate_dir: Path, context: dict) -> None:
    for filename, source in context["fileByName"].items():
        path = candidate_dir / filename
        if not path.is_file():
            raise SelectionError(f"candidate WAV missing: {filename}")
        actual = sha256_file(path)
        if actual != source["sha256"]:
            raise SelectionError(f"candidate WAV hash mismatch for {filename}: expected={source['sha256']} actual={actual}")


def build_template(context: dict, contract: dict) -> dict:
    return {
        "version": contract["selectionExport"]["version"],
        "status": contract["selectionExport"]["status"],
        "reviewedAt": "",
        "reviewerAlias": "",
        "bindings": {
            "candidateAuditSha256": context["auditSha256"],
            "normalizedAuditionSha256": context["reviewSha256"],
            "candidateHashes": {name: context["fileByName"][name]["sha256"] for name in sorted(context["fileByName"])},
        },
        "families": [
            {
                "canonicalTarget": group["canonicalTarget"],
                "candidateFamily": group["candidateFamily"],
                "decision": "",
                "selectedFile": "",
                "note": "",
            }
            for group in family_groups(context)
        ],
    }


def render_html(context: dict, contract: dict, template: dict) -> str:
    payload = json.dumps({"groups": family_groups(context), "contract": contract, "selection": template}, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    return """<!doctype html><html lang="da"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PROJECT ØEN — Music family selection</title>
<style>body{font-family:system-ui,sans-serif;max-width:1120px;margin:auto;padding:24px;background:#f2f0e9;color:#202522}header,.card{background:#fff;border:1px solid #d6d5cf;border-radius:14px;padding:18px;margin:14px 0}.candidate{border:1px solid #ddd;border-radius:10px;padding:10px;margin:8px 0}.eligible{border-color:#78a47c}.blocked{opacity:.65;background:#f7f5f1}audio{width:100%}.grid{display:grid;grid-template-columns:220px 220px 1fr;gap:8px;align-items:center}select,input,textarea{font:inherit;padding:7px;border:1px solid #b9bcb5;border-radius:7px}textarea{width:98%;min-height:55px}.sticky{position:sticky;bottom:8px;padding:10px;background:#f2f0e9e8;backdrop-filter:blur(4px)}button{font:inherit;font-weight:700;padding:10px 15px;border:1px solid #999;border-radius:9px;background:white}.warn{background:#fff2c8;padding:12px;border-radius:9px}@media(max-width:700px){.grid{grid-template-columns:1fr}}</style>
<header><h1>PROJECT ØEN — Human music family selection</h1><p>Vælg højst én menneskeligt auditioneret kandidat til hver af de fem canonical music cues. Kandidater med <code>maybe</code>/<code>reject</code> eller et ikke-bestået check er synlige men kan ikke vælges.</p><p class="warn"><b>Negativt resultat er tilladt.</b> Brug <code>needs-new-source</code> hvis ingen kandidat er god nok; systemet må ikke tvinge en selection.</p><div class="grid"><label>Reviewer alias</label><input id="reviewer"><span></span></div></header><main id="cards"></main><div class="sticky"><button onclick="downloadSelection()">Eksportér music_family_selection.json</button></div>
<script>const D=__DATA__;const S=D.selection;function e(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}function render(){const host=document.getElementById('cards');D.groups.forEach((g,i)=>{let candidates=g.candidates.map(c=>`<div class="candidate ${c.eligibleForSelection?'eligible':'blocked'}"><label>${c.eligibleForSelection?`<input type="radio" name="sel${i}" value="${e(c.file)}">`:''} <b>${e(c.file)}</b> — fit=${e(c.fit)} — ${c.eligibleForSelection?'eligible':'ikke valgbar'}</label><audio controls preload="metadata" src="${encodeURIComponent(c.file)}"></audio><small>SHA ${e(c.sha256)} · ${e(c.durationSeconds)} s · ${c.loop?'loop':'ending'}</small></div>`).join('');host.insertAdjacentHTML('beforeend',`<article class="card"><h2>${e(g.canonicalTarget)}</h2><p>Candidate family: <code>${e(g.candidateFamily)}</code></p>${candidates}<div class="grid"><label>Beslutning</label><select data-i="${i}" data-k="decision"><option></option><option>select</option><option>needs-new-source</option><option>needs-more-listening</option></select><textarea data-i="${i}" data-k="note" placeholder="Hvorfor?"></textarea></div></article>`)});host.querySelectorAll('input[type=radio]').forEach(el=>el.onchange=()=>S.families[+el.name.slice(3)].selectedFile=el.value);host.querySelectorAll('[data-i]').forEach(el=>el.oninput=()=>S.families[+el.dataset.i][el.dataset.k]=el.value)}document.getElementById('reviewer').oninput=e=>S.reviewerAlias=e.target.value;function downloadSelection(){S.reviewedAt=new Date().toISOString();const b=new Blob([JSON.stringify(S,null,2)+'\n'],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='music_family_selection.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)}render();</script></html>""".replace("__DATA__", payload)


def prepare(audition: Path, candidate_dir: Path, repo_root: Path = ROOT) -> dict:
    context = load_normalized_audition(audition.resolve(), repo_root)
    candidate_dir = candidate_dir.resolve()
    verify_candidate_dir(candidate_dir, context)
    contract = load_json(repo_root / SELECTION_CONTRACT)
    template = build_template(context, contract)
    (candidate_dir / "music_family_selection.template.json").write_text(json.dumps(template, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (candidate_dir / "music_family_selection.html").write_text(render_html(context, contract, template), encoding="utf-8")
    return template


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare hash-bound human family selection from normalized PROJECT OEN music audition evidence.")
    parser.add_argument("--audition", type=Path, required=True)
    parser.add_argument("--candidate-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = prepare(args.audition, args.candidate_dir)
    except SelectionError as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"Prepared music family selection for {len(result['families'])} canonical cues in {args.candidate_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
