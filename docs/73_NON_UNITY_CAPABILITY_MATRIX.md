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
- actual authorized radio VO recording and human take selection
- human music audition/canonical family selection
- human re-listening after any derived audio edit

`gateSatisfied=false` is therefore not a backlog bug. It is the correct state until the corresponding real evidence or owner decision exists.

## Audio pipeline now represented

The matrix captures the full non-Unity pipeline that is already on `main`:

1. reproducible 25-source audition pack
2. preliminary human shortlist evidence
3. typed human source-approval gate
4. copy-only source-approved original materialization
5. explicit derived-master submission with edit recipe
6. 48 kHz / 24-bit integer PCM technical intake
7. repeated human listening on the derived bytes
8. explicit derived-master-approved materialization

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
- the audition pack still represents 25 sources;
- radio VO remains 9 cues / 27 take candidates;
- music remains 14 candidates / 5 canonical mapped families;
- evidence-, device- and owner-gated lanes remain explicitly open.

CI runs the same validator whenever the matrix or its important backing contracts change.

## Working rule

When continuing non-Unity work, use the matrix to avoid recreating tooling that already exists. If all remaining next-actions require human listening, human sessions, actual recordings, physical Quest evidence or owner scope decisions, do not manufacture synthetic progress. Prepare deterministic handoff/evidence paths only where a concrete gap still exists.
