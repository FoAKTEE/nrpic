# What G2 of B-emd-gw still lacks (batch 39, 2026-11-27 evening)

**Gate G2 is HELD, not signed** (coord/GATES.md 2026-11-27; coord/DECISIONS/0050;
stage/G2/GATE_REVIEW.md). The independent review recommended a pass with reservations that
covers the band strain of the halo box only up to a = 49. The orchestrator reads the
convergence item (C2) over the whole range the track's science uses, so it is NOT MET after
a = 50: there the band strain differs between the two gauges by 5, 20 and 36 per cent at
a = 64, 100, 132 (reviewer's run B-20261128-032405-7c4aa64), and the particle-number leg was
run only with zero shift, not in the Gamma-driver gauge in which the strain is read.

| Item | State (CHECKLIST.md) | What settles it |
|---|---|---|
| C2 | FAIL as worded after a = 50; PASS for a <= 49 (mesh, particle number in zero shift, gauge within 1.6 per cent) | decision 0050 item 2: (a) a gauge-invariant measure of the late strain compared between the gauges, from the dumps that exist; or (b) the 128^3 member at eight particles per cell in the Gamma-driver gauge read against the one-per-cell member of that gauge. Then a second review limited to this item. |
| C1 | PASS under 0046 2(a); L2 as run FAILED on record; its cause OPEN AGAIN (the reference codes at H L = 4 are particle codes, draft.tex:360) | nothing for G2 |
| C3 | PASS under 0046 2(b) and 0039 2(c); M4, GM4, C3a early part FAILED on record | nothing for G2 |
| others | PASS or NA (gate review section 3) | the corrections of the review's section 6 are made in batch 39 |

Under way for item 2 (batch 39):
- (b) q0107, label `pop_s014_gr_p8_gd`, run B-20261128-034731-640f4f4, Slurm job 5585 (pending
  at 19:56 PST), about 0.85 card-h; predictions G8a-G8c in population/JOURNAL 2026-11-27 19:36.
  Read it with `population/scripts/compare_legs.py`-style band ratios against
  B-20261124-210431-6bf48af at a = 64, 100, 132 (and K1: no guard stop, constraint level).
- (a) the proper-volume magnetic Weyl invariant I_B = <B_ij B^ij>_V, predictions W0-W3 in
  population/JOURNAL 2026-11-27 19:37; reader tested on analytic fields
  (B-20261128-034232-f589717); data run B-20261128-034914-1e7a68f. Outcome: population/JOURNAL
  batch 39 and stage/REVIEW-wave3.md section "Batch 39".

Scope (decision 0050 item 3): scope/SCOPE.md section 6 now carries two dated amendments
(2026-11-27): the first-source mesh clause (unmet, placed as a G3 entry condition) and the
gauge leg G3 means (shift as run, plus a lapse variation to be specified in the G3 scope).

Pending, not required by any criterion as worded: the member 256^3 at eight particles per cell
(Gamma driver; decision 0048 item 3; 0050 item 2 says it is not waited for). Its initial data
run on one core since 2026-11-27 19:04 PST (B-20261128-030420-33ccdca, about two days;
predictions I1-I4, K1-K3 in population/JOURNAL 2026-11-27 19:02, 19:05).

Failures on record (no further run needed): as listed in batch 37 (X3, GD1 time part, N1p time
part, the particle leg's chain cut, N4 as written, GN2 after a = 36, NB1, VC1 second part, VC2 side
statements, the defective first band run, M1, M4, GN1 of batch 21, the slip a' = 4a, GM4 first part,
M2 masses at a = 64-72, M3 first part, Q1 high-k part, series-7 design claim and N7b constraint
part, C3 step-1 wall time, GM2 Omega part, GM3 counts at a = 121 and masses, C3a before a = 31, the
halo catalogue at one particle per cell, E2, P1 in part, P2 nearest-record pairing, the first
mem_fit run); batch 39: W0's discrimination clause (three map families, refuted), the first W0 run
(inv3) and the first data run (stopped by hand, row keys).

The standard stage check fails `runs` while B-20261128-030420-33ccdca (initial data) and the
q0107 chain are not finished; that is by design.
