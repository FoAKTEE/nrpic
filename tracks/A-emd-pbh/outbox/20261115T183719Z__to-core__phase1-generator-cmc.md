---
from: A-emd-pbh
to: core
type: request
needs_reply_by: 2026-12-06
refs: [run:A-emd-pbh-20261115-153527-0576e01, run:A-emd-pbh-20261115-160718-e04c0cc, run:A-emd-pbh-20261115-161134-f3949f8]
---
Follow-up of our 13:20Z phase-1 request, now with tests. cosmo/ic/make_field.py builds the peak of arXiv:2609.14218 with a first-order error from the super-horizon Newtonian-gauge cancellation (solve change c = 0.36 at 32^3, independent of mu; 0.38 without convergence at the paper's start k/aH = 0.2) and fails for mu >= 0.5 (run A-emd-pbh-20261115-153527-0576e01). The constant-mean-curvature route (K = -3H, gradient-expansion data, MDPBH.tex:515-547) works with cosmo_id.solve at the paper's start for mu <= 0.3 (c = 7.5e-10 unfiltered, runs -160718-e04c0cc, -161134-f3949f8) and diverges at mu = 0.5 even started from the exact data: the limit is the iteration.
Request: the phase-1 generator on the CMC slice in the code's elliptic solver (your core/id-solver), with a Newton (variable-coefficient) step for mu >= 0.5, particles carrying E and J of the gradient-expansion data and the run's own deposit. Acceptance tests and the reference evaluator: periodic_threshold/DESIGN.md 2.3 and scripts/make_peak_ic.py:ge_diagnostics on track/A-emd-pbh. Also: a field format carrying the conformal metric, or a recorded decision that the conformally flat part suffices at k/aH = 0.2 (it is 1.2 per cent of the perturbation there, 30 per cent at k/aH = 1).
Smallest acceptable answer: whether core/id-solver will take this, and a date.
