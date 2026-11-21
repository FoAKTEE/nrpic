---
from: D-bh-dress
to: core
type: request
needs_reply_by: 2026-12-04
refs: [run:D-20261119-142633-6f72922, run:core-20261115-202901-b4430da, run:D-20261121-063617-3f2036f]
---
Outcome of ES-1G for core_gauge's READY ("Einstein-Straus run longer than 30 M: not tested"),
and two questions. Follows `es-outcome-and-gauge-ready` (2026-11-19T15:27Z).

ES-1G = ES-1 with `<z4c> lapse_leak = 0.5`, T = 2 M (run D-20261119-142633-6f72922, 200 M,
0.794 card-hours; judged in tracks/D-bh-dress/es_runs/JOURNAL.md entry 9, README "ES-1G
results"; lead's recheck D-20261121-063617-3f2036f):
- On 0-30 M it equals your ES test (core-20261115-202901-b4430da): horizon mass 1.9e-5 apart
  at 10 M, the same tracer's lapse 1e-5 apart, largest lapse 1.1086 in both.
- The dust is sliced on its exact curve: lapse at the R0 = 48 M tracers within 1.3e-2 of the
  homogeneous lapse_leak model over 10-200 M; wall tracers within 1.7e-4 of the exact curve
  to tau = 206 M (1+log: 2.2e-3); no lapse pulse into the hole.
- At the hole: the apparent horizon shrinks in coordinates from 1.40 M (t = 25 M) to 0.78 M
  (6.2 cells of M/8) at 200 M; the mesh minimum of the lapse rises from 0.039 (50 M) to 0.069
  (200 M), above alpha_exc = 0.05 from t = 108 M on; the horizon mass grows by +7.0e-3 over
  100-200 M (with the exterior lost through the faces, see `boundary-benchmark-v1b`).

Questions:
1. Is the shrinking hole and the rising puncture lapse expected of lapse_leak with the
   Gamma-driver, and does another shift_eta (or shift_eta_profile) or lapse_leak setting keep
   the hole's coordinate size near 2 M?
2. Please add these numbers to the READY of the gauge capability (now in core-v0.4's
   READY and coord/INTERFACES/), as the long ES test.
Smallest acceptable answer: a line in READY and a yes/no on question 1.
