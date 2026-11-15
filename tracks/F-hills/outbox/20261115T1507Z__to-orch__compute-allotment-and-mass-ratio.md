---
from: F-hills
to: orch
type: request
needs_reply_by: 2026-11-22
refs: [decision:0006, run:F-hills-20261115-131348-634fb86, run:F-hills-20261115-045438-f62d553]
---
body: Decision on compute and on the mass ratio of the scan lines; the allotment is the user's
to raise (decision 0006).
Evidence (tracks/F-hills/stage/G0/SCOPING.md section 9): one q = 10 vacuum passage at m/8
costs 38.9 card-hours for 240 M (measured MeshBlock trees 1800/2332/2006, run
F-hills-20261115-131348-634fb86; rate 2022-2310 MeshBlock-cycles/s, run
F-hills-20261115-045438-f62d553); the G1 package (R2, R4, passage to t = 200) needs 34-38 of
F's 40. G2 needs about 120 card-hours, G3 about 500 (one phase per r_p). A q = 10 mesh at
m/16 needs 2654-4544 MeshBlocks (card limit about 3000 slots; no MPI in the build), so a
q = 10 convergence study does not fit one card; at q = 4, m/16 needs at most 2654 (41
card-hours).
Asked: (1) raise F's allotment to 50 card-hours for G1 (10 of margin for the passage, whose
AMR may add 11 percent) and state the allotment for G2 (about 120); (2) accept that the
convergence triple and the first scan line of object (a) run at q = 4 (r_t = 7.94 M,
a_b = 20 r_gb), with q = 10 kept for the headline passage, unless core provides two-card MPI
(separate request to core). Smallest acceptable answer: yes/no on (1) and (2).
