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
- **actual physical Foley recording for 17 cues / 73 planned performances**
- **actual human Foley material/variation/weather review after recording**
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

Physical Foley is split into **two separate real-world gates** because heavy crate, rope/tarp and shelter-timber cues require actual material performances and then actual human listening:

### Foley recording / technical intake

1. 3 queue sessions reconciled to 3 physical setups
2. 13 canonical Foley cue IDs
3. 53 exact filename/variation slots
4. operator recording board + provenance template
5. 48 kHz / 24-bit mono PCM technical intake
6. SHA-256/byte receipt and duplicate-byte rejection

This lane remains `gateSatisfied=false` until the 53 physical recordings actually exist.

### Foley human review / explicit source promotion

After a real technical pass:

1. review tooling revalidates current session, provenance, technical receipt and all 73 take hashes
2. human reviewer decides keep/rerecord/more-listening per take
3. human reviewer decides accept/rerecord/more-listening per 17-cue family
4. the eight canonical listening checks are completed per cue family
5. MATERIAL_MATCH and VARIATION_VALUE must each be >=3
6. Foley-specific UNDER_WEATHER_READABILITY must pass
7. complete negative review remains valid evidence and does not fail normalization
8. only complete positive 53/53 + 13/13 evidence can enter copy-only source-approved materialization

The materializer recomputes eligibility and copies original WAV bytes unchanged. Any later edit enters the separate derived-master + repeated-human-listening gate.

Fire-start-specific Foley remains excluded while issue #8 is owner-gated.

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
- Foley recording remains 17 cues / 73 physical take slots and explicitly open;
- Foley human review remains a separate 13/53 evidence gate and explicitly open;
- radio VO remains 9 cues / 27 take candidates;
- music remains 14 candidates / 5 canonical mapped families;
- evidence-, device- and owner-gated lanes remain explicitly open.

CI runs the same validator whenever the matrix or its important backing contracts change.

## Working rule

When continuing non-Unity work, use the matrix to avoid recreating tooling that already exists. If all remaining next-actions require human listening, human sessions, actual recordings, physical Quest evidence or owner scope decisions, do not manufacture synthetic progress. Prepare deterministic handoff/evidence paths only where a concrete gap still exists.
