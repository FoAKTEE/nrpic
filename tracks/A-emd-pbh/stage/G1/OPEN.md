# What G1 of A-emd-pbh still lacks (lead of batch 2b, 2026-11-21)

Every checklist item is PASS (C20 closed in this session by the owner's STATUS.md, JOURNAL.md,
HANDOFF.md, RISKS.md; C18 decided by the lead on the gate reviewer's evidence). The independent
gate review recommends PASS WITH RESERVATIONS (`GATE_REVIEW.md`); the lead's answers to each
reservation are in `../REVIEW-wave3.md` section 5. What remains open, none of it a G1 criterion:

1. **Rows of the note that nobody independent recomputed** (C18): SR-2 "largest 2m/R on the
   axes 0.34; apparent horizons found 0" (needs the field dumps), the predicted card-hours of
   the scouting runs (a cost model, compared with measured card time at G2), and the four
   cross-check differences of Table II (read from `crosscheck.json` of
   A-20261115-130257-a7374a4; their inputs are checksummed).
2. **Wave-1 provenance**: the outputs behind 18 ledger rows were checksummed only on
   2026-11-20 (A-20261120-222620-0304d9d); the lead's rerun of that listing on 2026-11-21
   (A-20261121-075933-338a6ff, L3) finds all 55 files unchanged. Before G2: rerun the wave-1
   producers through `nrpic-run` (minutes on processors).
3. **Manifests**: the four the reviewer found open are closed: A-20261119-164634-f1fe887 and
   A-20261120-223310-a9ce31a by the runs_ball helper of batch 2b (00:05 and 00:16 PST),
   A-20261120-223123-f436c39 and A-20261120-223422-8cc4241 by the lead. The only open manifest
   is conv_ball's live card job A-20261121-075926-d10c2c1 (Slurm 4776, queued), a G2 run.
4. **Uncommitted files of a package in progress** (`periodic_threshold/`: `JOURNAL.md`,
   `inputs/peak_leak.athinput`, `scripts/ltb_reference.py`, `scripts/ltbref.py`; and while
   they work, the files of the runs_ball and conv_ball helpers): `nrpic-stage verify` fails its
   `clean` check on them; none is a file of this package.
5. **For G2, carried from the gate review** (section 6 there): no horizon yet in a converged
   series; SR-2 turnaround estimator; mesh against box; constraints of data set 2t as a whole
   and AthenaK's t = 0 norms of the format-2 table in dx; Newtonian energy drift at sub-cell
   crossings; architecture schematic against core-v0.5; the horizon-mass criterion as written.

## Automated checks (`nrpic-stage verify`)

Full verify with output checksums on the export of 0368f927, 2026-11-21 08:07-08:37 UTC
(`VERIFY_RESULTS.md`): 13 PASS (sync, export, size, note, package, note-pdf, style,
fig-script, min-figs, status, rerun 9 of 9, compare 14 files, regenerate 14 of 14), run-notes
WARN (79 manifests read with defaults, waived by decision 0016 item 3), and two FAIL that do not
come from G1 evidence: `clean` (files of packages in progress, item 4) and `runs` (A-20261120-
223310-a9ce31a closed after the export; A-20261121-075926-d10c2c1 a queued G2 card job;
A-20261121-064515-aa13c8f the reviewer's failed first attempt, whose scratch script was edited
for its rerun: waiver asked in the outbox). Reading of each: `STAGE_REPORT.md`, last section.
