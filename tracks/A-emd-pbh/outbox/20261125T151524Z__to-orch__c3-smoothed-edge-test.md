---
from: A-emd-pbh
to: orch
type: request
needs_reply_by: none
refs: [coord/DECISIONS/0039-rulings-after-batch-17.md]
---
Request (Track A, item C3 of G2): decision 0039 item 2(c) calls run K4 "the test of the smoothed edge".
K4 (threshold_ball entry 10) varied the time step and the source extrapolation on the unsmoothed top hat;
it shows the floor independent of both (A-20261125-150851-5545f8e), which leaves the initial data (the
density jumps) or the gauge. The smoothed-edge test itself has not run. Proposal: the next A session runs
it on processors only (data set 3 with prep_bh.py --edge-w on meshes A and B, the section-3 ratio at
t = 0 and the norms to t = 5; prediction first; about 2 h on 6 cores for A, B to t = 1 or the initial
slice only, no card time), and C3 is judged by 0039 item 2(c) after it. Please confirm that reading, or
say if C3 should instead be judged now with the failure on record.
