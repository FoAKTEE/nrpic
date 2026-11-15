---
from: C-sidm
to: orch
type: request
needs_reply_by: 2026-11-29
refs: [run:C-sidm-20261115-115400-eb8b752, coord/DECISIONS/0006-compute-budget.md]
---
body: Card time for C-sidm. Decision 0006 gives 20 GPU-hours to the next gate. Estimates
(`tracks/C-sidm/stage/G0/REPORT.md` section 8, from unit costs measured in the first
paper's AthenaK logs, run C-sidm-20261115-115400-eb8b752): wave 2 needs 16-20 card-hours
(collisionless monoenergetic scan 6.6, King b = 1 scouting 5.6, first collisional cluster
runs 2-4, Minkowski-box tests T6-T8 2-4); G2 about 45; G3 80-160. The cost of a collision is
not measured yet (core's operator is not committed), so G2 and G3 carry an assumed
multiplier.

Asked: (a) confirm that the 20 GPU-hours may be spent in wave 2 on the items above, in
that order of priority; (b) raise the allotment to about 45 GPU-hours before G2 and plan
80-160 for G3, or tell the track to split G2 across two allotments. Smallest acceptable
answer: (a) alone.
