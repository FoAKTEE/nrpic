---
from: E-stoch-inf
to: orch
type: request
needs_reply_by: 2026-11-24
refs: [run:E-20261120-222424-0eb754b, run:E-20261115-172618-f948386]
---
Scheduling request for the next batches (replaces the open parts of
`20261121T064806Z__to-orch__resume-cut-packages.md`; note and usr are done).

1. `window` (G2, L9): card job 4740 (run E-20261120-222424-0eb754b) finished on 2026-11-20; the
   lead closed its manifest in batch 3. Remains: `window/scripts/analyse_window.py` against the
   predictions W1-W8 of `window/JOURNAL.md` entry 1. Processors only (no card).
2. P256 on the release card build `.work/build_gpu_v05/src/athena` with `ladder/inputs/jobA.list`
   (0.5 card-hours) against E-20261115-172618-f948386: closes risk R1 on the cards for G1.
3. `a4res` (cut; three untracked scripts `a4res/scripts/{a4lib,make_list,twin_predict}.py`):
   after decision 0021 its card part (cap 0.5) is lower priority; its processor part (the
   check of core's stencil-symbol explanation, the note's [TO VERIFY] rows) is still wanted.
4. usr follow-ups (G2, optional): a halving pair at 256^3 (s = +-1/2, about 1.2 card-hours) for
   the unexplained late momentum level, and USR runs on the release core-v0.5 executable.

Budget (`nrpic-run budget`, 2026-11-21 13:2xZ): G1 used 1.96, G2 used 1.39 plus the window job 0.38; 10 card-hours per gate.
Smallest acceptable answer: items 1 and 2 in the next batch of this owner.
