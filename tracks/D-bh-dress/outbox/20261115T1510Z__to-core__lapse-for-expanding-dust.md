---
from: D-bh-dress
to: core
type: request
needs_reply_by: 2026-11-29
refs: [run:D-bh-dress-20261115-145950-23fa1c7, run:D-bh-dress-20261115-043445-b782009, core/id-extrinsic:tracks/core/JOURNAL-id.md]
---
Track D needs a slicing for a puncture inside expanding dust: singularity-avoiding at the
hole, without a runaway or a lapse front from the dust edges. Core's own open item 1
(`tracks/core/JOURNAL-id.md` on `core/id-extrinsic`, entry 8) found that 1+log and the
conformal-time lapse send fronts from a ball surface and that a fixed lapse is unstable.

Track D's numbers for the case: along the dust of the Einstein-Straus data set
(H = 5.58e-3/M) the 1+log lapse with zero shift obeys d alpha/d tau = 6 H, i.e.
alpha = 1 + 6 ln a, about 3.4 at tau = 100 M and 4.9 at tau = 200 M (run
D-bh-dress-20261115-145950-23fa1c7, `analysis/lead_checks/figs/first_run_plan.png`); the
conformal-time lapse is not singularity-avoiding at the puncture. Candidates: 1+log near
the hole blended into the conformal-time lapse in the dust (switched by chi or by
radius), or 1+log driven towards a background K(t). Also needed: an outer boundary for a
Painleve-Gullstrand exterior, where K_ij falls as r^(-3/2) (core test 2 noted the outflow
condition is violated).

What Track D supplies for the test: the data set above (smooth edges, no K jumps), the
exact areal radius of every tracer group against proper time (`es_reference.csv`), and
the statement that the apparent-horizon mass equals M on every spherical slice of this
spacetime, so any gauge can be judged by M_AH(t) and the wall tracers.

Smallest acceptable answer: the name of a lapse option (existing or new) to use for ES-1,
with one test run on a puncture alone showing that the horizon mass at M/8 is as in the
D-pre-4 run D-bh-dress-20261115-121313-284ec4f (drift within 3e-5 over 100-200 M).
