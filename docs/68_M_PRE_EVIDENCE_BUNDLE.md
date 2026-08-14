# M-Pre evidence bundle — PROJECT ØEN

**Gate:** issue #7 / ADR-022 / PO-110  
**Evidence:** humans only  
**Tool owner:** ChatGPT  
**Status:** packaging/verification ready; no human evidence claimed

The facilitator runner already exports evaluator-compatible anonymous CSV plus per-session raw-note JSON. The missing operational step is to bind those files together so the gate result can always be traced back to the exact raw evidence used.

## After three real sessions

Keep the three exported note files and the batch CSV, then run:

```bash
python tools/package_mpre_evidence.py \
  --csv mpre_sessions.csv \
  --notes mpre_notes_S01.json \
  --notes mpre_notes_S02.json \
  --notes mpre_notes_S03.json \
  --output PrivateContent/MPreEvidence
```

The packager calls the canonical `tools/evaluate_mpre.py`; it does not reimplement or relax the gate. Invalid evaluator input returns no valid bundle.

It also requires:

- exactly one notes document for every session in the CSV;
- matching anonymous `session_id` and `pair_id`;
- three day entries and the existing facilitator-runner note structure;
- at least some qualitative raw-note content for each session;
- no obvious participant-name/email/phone/address **field names** in the structured data.

Free-text still needs human privacy discipline: use anonymous IDs and do not type names/contact details into observations.

## Output

A valid private bundle contains:

```text
PrivateContent/MPreEvidence/
  mpre_sessions.csv
  notes/
    mpre_notes_S01.json
    mpre_notes_S02.json
    mpre_notes_S03.json
  mpre_evidence_manifest.json
```

The manifest stores SHA-256 + byte count for all four raw inputs, a deterministic snapshot of the evaluator results and the calculated `GREEN`/`RED` gate.

Its status is deliberately:

`human-evidence-bundle-valid-unaccepted`

That means the evidence is structurally valid and bound. It does **not** close issue #7, update roadmap status or authorize M1 by itself.

## Reverify later

```bash
python tools/validate_mpre_evidence_bundle.py PrivateContent/MPreEvidence
```

Any changed CSV/note file, changed evaluator result or missing bound file fails validation.

## Human/product closure remains explicit

After a valid real bundle exists, the project still needs the issue #7 post-result steps: document the result in the M-Pre gate spec, update affected OQs/status/backlog and explicitly decide whether M1 may start. The tooling never performs those acceptance actions automatically.
