#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any

from foley_human_review_support import FoleyReviewError, expected_bindings, load_context


def build_template(context: dict[str, Any]) -> dict[str, Any]:
    contract = context["reviewContract"]
    take_decisions = {rel: "" for rel in sorted(context["takeRecords"])}
    take_notes = {rel: "" for rel in sorted(context["takeRecords"])}
    cues: dict[str, Any] = {}
    for cue_id in context["cueRecords"]:
        checks = {}
        for check_id, spec in contract["typedChecks"].items():
            checks[check_id] = {"result": None if spec.get("type") == "rating" else "", "note": ""}
        cues[cue_id] = {"decision": "", "note": "", "checks": checks}
    return {
        "version": contract["reviewExport"]["version"],
        "status": contract["reviewExport"]["status"],
        "reviewerAlias": "",
        "reviewedAt": "",
        "bindings": expected_bindings(context),
        "takeDecisions": take_decisions,
        "takeNotes": take_notes,
        "cueReviews": cues,
        "rule": "Human review only. Export does not promote source status; negative/rerecord evidence is valid."
    }


def _check_help(context: dict[str, Any]) -> dict[str, str]:
    out = {}
    for item in context["listeningQa"].get("requiredListeningChecks", []):
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            out[item["id"]] = str(item.get("question") or "")
    out["UNDER_WEATHER_READABILITY"] = "Does this cue remain physically readable at intended gain under a representative weather bed without fighting partner speech?"
    return out


def board_data(context: dict[str, Any], template: dict[str, Any]) -> dict[str, Any]:
    contract = context["reviewContract"]
    help_text = _check_help(context)
    cues = []
    for cue_id, records in context["cueRecords"].items():
        cues.append({
            "cueId": cue_id,
            "physicalSessionId": records[0]["physicalSessionId"],
            "takes": [
                {
                    "relativePath": record["relativePath"],
                    "filename": record["filename"],
                    "variant": record["variant"],
                    "sha256": record["sha256"],
                    "durationMs": record.get("durationMs"),
                    "peakDbfs": record.get("peakDbfs"),
                }
                for record in records
            ],
        })
    return {
        "template": template,
        "cues": cues,
        "typedChecks": contract["typedChecks"],
        "takeDecisionValues": contract["takeDecisionValues"],
        "cueDecisionValues": contract["cueDecisionValues"],
        "checkHelp": help_text,
    }


def render_board(data: dict[str, Any]) -> str:
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return f'''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>PROJECT ØEN — Foley human review</title>
<style>
body{{font-family:system-ui,sans-serif;max-width:1180px;margin:auto;padding:22px;background:#f3f1e9;color:#1e2421}}header,.cue{{background:white;border:1px solid #d7d8d2;border-radius:12px;padding:18px;margin:14px 0}}.cue h2{{margin-top:0}}.takes{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:10px}}.take,.check{{border:1px solid #ddd;border-radius:8px;padding:10px}}audio{{width:100%}}select,input,textarea{{font:inherit;max-width:100%}}textarea{{width:100%;min-height:55px}}.checks{{display:grid;grid-template-columns:repeat(auto-fit,minmax(310px,1fr));gap:10px}}code{{font-size:.82rem;word-break:break-all}}.muted{{color:#626861;font-size:.9rem}}button{{font:inherit;padding:10px 14px;margin:4px}}.warn{{background:#fff7d6;padding:10px;border-radius:8px}}label{{display:block;margin-top:6px;font-weight:600}}
</style>
<header><h1>PROJECT ØEN — Physical Foley human review</h1><p><b>73 raw takes / 17 cue families.</b> Technical intake already passed before this board can be generated. Listen to every variant, then evaluate each cue family as a set.</p><p class="warn">A negative result is valid. Choose <code>needs-rerecord</code> when the physical material or variation is not good enough. Do not mark weak takes as keep just to complete the pack.</p><label>Reviewer alias <input id="reviewer" autocomplete="off"></label><label>Reviewed at <input id="reviewedAt" placeholder="2026-08-14T12:34:56Z"></label><p><button onclick="stampNow()">Use current UTC time</button><button onclick="exportReview()">Export foley_human_review.json</button></p><p class="muted">UNDER_WEATHER_READABILITY must be judged while comparing the cue against a representative weather bed at intended game-like level. This board does not fabricate that listening condition.</p></header>
<div id="app"></div>
<script>const DATA={payload}; const state=structuredClone(DATA.template);
function esc(s){{return String(s).replace(/[&<>\"]/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]))}}
function opts(values,current,blank=true){{let a=blank?['']:[];a=a.concat(values);return a.map(v=>`<option value="${{esc(v)}}" ${{v===current?'selected':''}}>${{v||'— choose —'}}</option>`).join('')}}
function checkControl(cueId,id,spec){{const e=state.cueReviews[cueId].checks[id];const help=DATA.checkHelp[id]||'';let control;if(spec.type==='rating'){{control=`<select data-kind="check" data-cue="${{esc(cueId)}}" data-check="${{id}}">${{opts([1,2,3,4,5].map(String),e.result==null?'':String(e.result))}}</select>`}}else{{control=`<select data-kind="check" data-cue="${{esc(cueId)}}" data-check="${{id}}">${{opts(spec.values,e.result||'')}}</select>`}}return `<div class="check"><b>${{id}}</b><p class="muted">${{esc(help)}}</p>${{control}}<textarea data-kind="checknote" data-cue="${{esc(cueId)}}" data-check="${{id}}" placeholder="Evidence / listening note">${{esc(e.note||'')}}</textarea></div>`}}
function render(){{document.getElementById('reviewer').value=state.reviewerAlias||'';document.getElementById('reviewedAt').value=state.reviewedAt||'';document.getElementById('app').innerHTML=DATA.cues.map(c=>{{const cr=state.cueReviews[c.cueId];return `<section class="cue"><h2>${{esc(c.cueId)}}</h2><p class="muted">Physical session: <code>${{esc(c.physicalSessionId)}}</code></p><div class="takes">${{c.takes.map(t=>`<div class="take"><b>v${{String(t.variant).padStart(2,'0')}}</b> · ${{Math.round(t.durationMs)}} ms<audio controls preload="none" src="${{esc(t.relativePath)}}"></audio><code>${{esc(t.filename)}}</code><p class="muted">SHA ${{esc(t.sha256.slice(0,16))}}… · peak ${{t.peakDbfs==null?'n/a':t.peakDbfs+' dBFS'}}</p><select data-kind="take" data-path="${{esc(t.relativePath)}}">${{opts(DATA.takeDecisionValues,state.takeDecisions[t.relativePath])}}</select><textarea data-kind="takenote" data-path="${{esc(t.relativePath)}}" placeholder="Take note">${{esc(state.takeNotes[t.relativePath]||'')}}</textarea></div>`).join('')}}</div><h3>Cue-family decision</h3><select data-kind="cue" data-cue="${{esc(c.cueId)}}">${{opts(DATA.cueDecisionValues,cr.decision)}}</select><textarea data-kind="cuenote" data-cue="${{esc(c.cueId)}}" placeholder="Cue-family note">${{esc(cr.note||'')}}</textarea><h3>Typed listening checks</h3><div class="checks">${{Object.entries(DATA.typedChecks).map(([id,s])=>checkControl(c.cueId,id,s)).join('')}}</div></section>`}}).join('');bind()}}
function bind(){{document.querySelectorAll('[data-kind]').forEach(el=>el.onchange=()=>{{const k=el.dataset.kind;if(k==='take')state.takeDecisions[el.dataset.path]=el.value;if(k==='takenote')state.takeNotes[el.dataset.path]=el.value;if(k==='cue')state.cueReviews[el.dataset.cue].decision=el.value;if(k==='cuenote')state.cueReviews[el.dataset.cue].note=el.value;if(k==='check'){{const spec=DATA.typedChecks[el.dataset.check];state.cueReviews[el.dataset.cue].checks[el.dataset.check].result=spec.type==='rating'?(el.value?Number(el.value):null):el.value}}if(k==='checknote')state.cueReviews[el.dataset.cue].checks[el.dataset.check].note=el.value}})}}
function stampNow(){{state.reviewedAt=new Date().toISOString();document.getElementById('reviewedAt').value=state.reviewedAt}}
function exportReview(){{state.reviewerAlias=document.getElementById('reviewer').value.trim();state.reviewedAt=document.getElementById('reviewedAt').value.trim();document.querySelectorAll('textarea').forEach(e=>e.dispatchEvent(new Event('change')));const blob=new Blob([JSON.stringify(state,null,2)+'\n'],{{type:'application/json'}});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='foley_human_review.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)}}
render();</script></html>'''


def prepare(session_root: Path) -> dict[str, Any]:
    context = load_context(session_root)
    template = build_template(context)
    root = context["sessionRoot"]
    template_path = root / "foley_human_review.template.json"
    board_path = root / "foley_human_review_board.html"
    template_path.write_text(json.dumps(template, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    board_path.write_text(render_board(board_data(context, template)), encoding="utf-8")
    return {"template": template_path, "board": board_path, "cueCount": len(context["cueRecords"]), "takeCount": len(context["takeRecords"])}


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a browser-based, hash-bound human review board for a technically accepted PROJECT OEN Foley session.")
    parser.add_argument("--session", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = prepare(args.session)
    except FoleyReviewError as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"Prepared Foley human review: {result['cueCount']} cues / {result['takeCount']} take bindings")
    print(f"Board: {result['board']}")
    print("No human decision is prefilled and no source status is promoted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
