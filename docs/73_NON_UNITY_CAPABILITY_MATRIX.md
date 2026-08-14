# Non-Unity capability matrix

`content/non_unity_capability_matrix.source.json` is the machine-readable answer to a different question than `content/source_inventory.source.json`.

- `source_inventory.source.json` answers: **what source/content exists, and what state is it in?**
- `non_unity_capability_matrix.source.json` answers: **which non-Unity workflow lanes are mechanically ready, and what real evidence is still missing?**

Keeping those concerns separate prevents a common status error: a lane can be technically complete while every actual human/device gate is still open.

## Current boundary

The matrix intentionally keeps the following as open gates:

- M-Pre actual human sessions — issue #7
- M0b physical Quest 2/Quest 3 cross-device evidence — issue #3
- fire-start owner disposition — issue #8
- human listening/source selection for acquired ambience/Foley
- **actual physical Foley recording for 13 cues / 53 planned performances**
- actual authorized radio VO recording and human take selection
- human music audition/canonical family selection
- human re-listening after any derived audio edit

`gateSatisfied=false` is therefore not a backlog bug. It is the correct state until the corresponding real evidence or owner decision exists.

## Audio pipeline now represented

The matrix captures the acquired-source pipeline already on `main`:

1. reproducible 27-source audition pack
2. preliminary human shortlist evidence
3. typed human source-approval gate
4. copy-only source-approved original materialization
5. explicit derived-master submission with edit recipe
6. 48 kHz / 24-bit integer PCM technical intake
7. repeated human listening on the derived bytes
8. explicit derived-master-approved materialization

The current 27-source boundary is 3 main originals + 15 extension sources/members + 9 field originals. The two newest field originals are pinned by `content/audio/acquisition_field_backlog_final_receipt.source.json`; `SFX_AMB_Beach_PalmCanopy` remains the only field acquisition gap and is not counted as acquired.

Physical Foley has a separate recording lane because heavy crate, rope/tarp and shelter-timber cues require actual material performances rather than stock-source substitution:

1. 3 queue sessions reconciled to 3 physical setups
2. 13 canonical Foley cue IDs
3. 53 exact filename/variation slots
4. operator recording board + provenance template
5. 48 kHz / 24-bit mono PCM technical intake
6. SHA-256/byte receipt and duplicate-byte rejection
7. later human material-fit, variation-value and under-weather listening

The Foley lane is mechanically ready only. It remains `gateSatisfied=false` until those recordings actually exist. Fire-start-specific Foley is excluded while issue #8 remains owner-gated.

Radio VO has its own parallel lane:

1. 9 canonical cues × 3 takes
2. canonical Danish recording board
3. technical intake
4. human pronunciation/delivery/semantic/rights review
5. one selected take per cue
6. byte-identical selected dry materialization

Music likewise has a separate audition/selection lane:

1. 14 audited deterministic candidates
2. human candidate audition
3. five canonical-family selections
4. `MUS_Warning_LowPulse` remains unmapped
5. byte-identical canonical source materialization

None of these tooling states imply runtime integration, Quest acceptance or release approval.

## Validation

Run:

```bash
python tools/validate_non_unity_capability_matrix.py
```

The validator checks:

- every referenced repo path exists;
- required lanes are present and unique;
- important lane statuses still match their underlying contracts;
- the audition pack represents 27 sources;
- Foley remains 13 cues / 53 physical take slots and explicitly open;
- radio VO remains 9 cues / 27 take candidates;
- music remains 14 candidates / 5 canonical mapped families;
- evidence-, device- and owner-gated lanes remain explicitly open.

CI runs the same validator whenever the matrix or its important backing contracts change.

## Working rule

When continuing non-Unity work, use the matrix to avoid recreating tooling that already exists. If all remaining next-actions require human listening, human sessions, actual recordings, physical Quest evidence or owner scope decisions, do not manufacture synthetic progress. Prepare deterministic handoff/evidence paths only where a concrete gap still exists.
