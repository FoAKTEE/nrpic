# HANDOFF of package repro/figs (Track E)

State: 2026-11-24, batch R4 (last pass). Every figure of arXiv:2512.14649 is remade from our
registered runs; RSF256 (SR 256^3 with metric dumps) has ended at t = 8.5 and is in the figures.
`RESULTS.md` holds the verdicts (no PENDING row once the last pass is in), `JOURNAL.md` the
predictions and outcomes (entry 14 for this pass), `README.md` how to rerun.

## For package repro/continue (this package may not edit it)

RSF256's fourth continuation, shared-queue entry q0034, ran as **E-20261124-214913-5956891** (job
5215, 14:06-14:23 PST, "Terminating on time limit" at t = 8.5, cycle 1386, dumps 00017-00034). It is
closed in the run tool (`nrpic-run finish`, completed; commit e93cf790). Still to do in
repro/continue, as its `HANDOFF.md` says:

1. append `E-20261124-214913-5956891` to `"RSF256"` in `repro/continue/scripts/conts.json`;
2. rerun its join check (or adopt this package's, below) and record K2 in its journal.

Meanwhile this package keeps its own copy `conts_rsf256.json` (that `conts.json` with the id
appended) and ran repro/continue's `join_check.py --conts conts_rsf256.json --labels RSF256` as its
own registered run **E-20261124-225720-444aecc**: complete, J1, J2 (958 of 958 lines identical), J3
(as amended at cycle 0), J4 (dumps 17-21 byte-identical between 0b1ce0c and 5956891) and
records_gapless all true; joined record cycles 0-1386, dumps 00000-00034 (`RSF256.dumps.tsv`: 0 from
the original, 1-16 from 0b1ce0c, 17-34 from 5956891). `figures/runs.py` reads RSF256's joined
record from that run (`JOINED["RSF256"]`).

## Runs of this pass

- E-20261124-225720-444aecc: join check of RSF256 (above).
- E-20261124-225826-0bf3842: dump pass, group `rsf256` (35 dumps), bit checks against P256v6 at
  t = 0, 4.0, 8.5.
- the figure run (ledger in `RESULTS.md` section 4).

## Nothing waits

No card run of this package is queued or running. Open questions are listed in `RESULTS.md`
section 6 (requests).
