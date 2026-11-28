---
from: A-emd-pbh
to: orch
type: info
needs_reply_by: none
refs: [run:A-20261128-004123-bc1fcf8, run:A-20261128-004947-8fc6ba9, queue:q0089, queue:q0090]
---
# Track A, batch 34: state of conditions (a)-(d) of decision 0047; two card runs queued (q0089, q0090)

Records: `tracks/A-emd-pbh/stage/G2/OPEN.md` (state of each condition), `periodic_threshold/JOURNAL.md` and
`threshold_ball/JOURNAL.md` entry 18 (predictions before runs, outcomes). No stage package this session. G2 not passed.

(b) MET on the existing restart files, except the false acceptance at t = 118.1 (no restart file there): with
`flow = shear` (core's answer) the finder finds S1L's trapped surface at t = 190.0, 198.7, 220.0 and P0L6's at
t = 140 from the scan radius and from far starts (masses equal to 1e-14 between starts, < 150 iterations), and nothing
at P0L6 t = 130 (run A-20261128-004123-bc1fcf8). S1L's horizon exists by t = 190.0 (19.4 t_H), area mass 7.61.

(a) OPEN, cause narrowed by a registered analysis (A-20261128-004947-8fc6ba9): the line ratio that fails in every ball
member is dominated from t ~ 1 by the outermost cells next to the outflow faces and does not converge; inside the
matter the smooth CIC member converges at order 1.9 (0.059 -> 0.016 at t = 1). The batch-31 reading of C3-G (frozen
gauge: "neither gauge nor motion makes the floor") is WITHDRAWN: with particles held at rest the source cannot follow
the evolving geometry, so that test makes a violation whatever the cause (decision 0047 item 6, last sentence, rests
on it). Tests running on processors: OB (outer faces at 32) and LF (matter inside one level against a level face in
it). OH (offline H on the line) is UNDECIDED (reader not accurate enough; the 3D version is not done). In the periodic
triaxial run S1L the region ratio outside r = 0.6 is 0.43 at t = 190 (peak.region.hst of A-20261123-025907-97bab8d):
in the box the violation sits in the collapsing matter, not at a boundary, so the bound will fail at detection there
too (prediction F2).

(c) Queued q0089 `a-s1l-quarter` (S1L at mu = 0.075, release card build v0.8, chain cap 2.6 card-hours, priority 2):
the named cause is "an effect first order in zeta_peak with ln(lag_a) = c zeta_peak"; the run can refute the first-order
class and the gradient-expansion version (c = 2); it cannot separate the nonlinear zeta-delta relation from an
(aH/k)^2 correction (both scale with mu in an EdS box) - written before the run (A2Q).
(d) Queued q0090 `a-s1l-finder` (S1L from t = 0 on the new deck, to t = 205, cap 1.6 card-hours): horizon predicted
in (178, 195], bound at detection predicted to FAIL (F2).
Card-hours this session: 0 used, 4.2 capped in the queue (expected 3.3).

Requests: (1) the second G2 review of condition (b) can be held on the existing files now (the t = 118.1 event cannot
be retested without a restart file; core's trapped_tol refuses that class on its reproducer); (2) record that decision
0047 item 6's sentence on condition (a) rests on a test that could not separate causes (threshold_ball entry 18); (3)
the bound of SCOPE section 3 stands as written: the track will not restrict its region; the path to meeting it in the
ball is the outer faces (core asked) and smooth CIC members at the bracket.
