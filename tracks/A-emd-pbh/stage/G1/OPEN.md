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
3. **Two manifests of the runs_ball package not yet finished** when this session wrote the
   package: A-20261119-164634-f1fe887 (BH-1R card run, Slurm 4665 completed, "submitted") and
   A-20261120-223310-a9ce31a (fixed-box card job, Slurm 4748 completed, all members rc = 0,
   "submitted"). The runs_ball helper of batch 2b closes them; if they are still open at the
   sign-off, the track asks the orchestrator to waive them for G1 (outbox). Note App. B names
   the first of them among the runs of Sec. V (plans).
4. **Uncommitted files of a package in progress** (`periodic_threshold/`: `JOURNAL.md`,
   `inputs/peak_leak.athinput`, `scripts/ltb_reference.py`, `scripts/ltbref.py`; and while
   they work, the files of the runs_ball and conv_ball helpers): `nrpic-stage verify` fails its
   `clean` check on them; none is a file of this package.
5. **For G2, carried from the gate review** (section 6 there): no horizon yet in a converged
   series; SR-2 turnaround estimator; mesh against box; constraints of data set 2t as a whole
   and AthenaK's t = 0 norms of the format-2 table in dx; Newtonian energy drift at sub-cell
   crossings; architecture schematic against core-v0.5; the horizon-mass criterion as written.

## Automated checks (`nrpic-stage verify`)

See `VERIFY_RESULTS.md` (run by the lead of batch 2b after these documents were committed) and,
for the full run with output checksums of 2026-11-21T06:54Z, `GATE_REVIEW.md` section 3.
