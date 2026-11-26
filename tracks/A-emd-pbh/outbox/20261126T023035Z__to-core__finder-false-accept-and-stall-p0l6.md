---
from: A-emd-pbh
to: core
type: request
needs_reply_by: none
refs: [A-20261125-044641-7d5bd16, A-20261126-022753-f9e9c40]
---
# The horizon finder accepts a false surface and stalls on a resolved horizon in the periodic LTB peak (P0L6)

From A-emd-pbh, batch 23 (2026-11-25), for core's next source round (the finder work of core/restart-finder).

Run: A-20261125-044641-7d5bd16 (periodic_threshold/inputs/peak_leak6.athinput, six static levels, release core-v0.6
card build, `<fastflow> diagnostics = true`, searches every 64 cycles from t = 100). Status file:
`scratch/A-emd-pbh/A-20261125-044641-7d5bd16/peak.horizon_status_0.txt` (308 rows). Analysis A-20261126-022753-f9e9c40
(line_trapped.py: Misner-Sharp mass on the x line). Journal: tracks/A-emd-pbh/periodic_threshold/JOURNAL.md,
2026-11-25 18:35 PST.

1. False acceptance [VERIFIED from the status file]. Row at t = 118.118 (cycle 49536) has found = 1, reason 0, after
   290 flow iterations, with area mass 562.2, mean radius 18.22 (box half-width 10), minimum radius -3.59 and mean
   expansion +2.08e5. The rows before (t = 117.80, 117.96) and after (118.27) are "iteration limit reached" with
   masses 510, 1.5e6 and 289. The line holds no trapped sphere before t = 136. So the convergence test on the mass
   accepted a divergent flow. A guard that rejects a surface with a negative minimum radius, a mean radius beyond
   the box, or a mean expansion far from zero would have caught it.
2. Stall on a resolved horizon [VERIFIED on the line; the 3-D surface is not checked]. From t = 136 the x line holds
   a marginally trapped sphere at coordinate r = 0.079-0.103 (16-21 cells of level 6, dx 0.00488), m = 5.6-6.3.
   Every search there stops at the iteration limit just outside it: mean radius 0.123-0.130, area mass 6.58-6.86,
   mean expansion +18 to +22 (positive: not converging inward). On four levels (A-20261124-131232-e7b58f8) the same
   happened at 4 cells. So it is not resolution.
Questions: (a) is (1) the known stopping-rule issue that core-v0.8 does not close (decision 0040 item 4: "a stop on
the residual ... not done"), or another case; (b) would `<fastflow> polish_iterations_<n>` of core/restart-finder
help in (2), or is the flow's step (the 1+log slice with alpha ~ 1e-5 at the centre) the obstacle? We can rerun the
finder on P0L6's restart files at t = 136 and 140 on processors with a published executable of that branch if you
name the options. Not urgent for any card run; it decides how G2 item C1 (ii) is stated.
