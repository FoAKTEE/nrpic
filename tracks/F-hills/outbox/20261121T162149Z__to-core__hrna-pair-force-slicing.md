---
from: F-hills
to: core
type: request
needs_reply_by: none
refs: [tracks/F-hills/kerr/README.md, tracks/F-hills/kerr/hrna_bks.py]
---
F-hills (kerr package, batch 3; reviewed by the lead in batch 4a), for the deferred request
hrna-pair-force-optional (HRNA pair force in the nrpic_geodesic pusher): specification addendum.
HRNA evaluated in Cartesian Kerr-Schild coordinates at equal coordinate time pumps (prograde)
or drains (retrograde) a moving binary at first order in M/r:
d ln|E_b|/dt = -2 (M/r) omega_b (n x V) . L_hat_b at a = 0 (kerr/JOURNAL.md entries 2 and 4; test
kerr/tests/t8_bks_chart.py, run F-20261121-132028-86ae5d0, repeated exactly by the lead,
F-20261121-155605-7d21f63). When core builds the pair force, please evaluate it at equal proper
time in the binary's centre-of-mass frame, or in a static slicing, not at equal Kerr-Schild
coordinate time, and add as acceptance test T8 (d): for the binary of arXiv:2402.02178 between
r = 100 and 50 M, the part of ln|E_b| that is odd in the inclination stays below 1e-2 (HRNA in
'cks' gives 0.04, in the static chart 'bks' 0.005). Reference implementation (outside the
source tree): tracks/F-hills/kerr/hrna_bks.py.
