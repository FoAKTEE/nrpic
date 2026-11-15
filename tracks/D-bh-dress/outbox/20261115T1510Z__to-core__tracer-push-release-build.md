---
from: D-bh-dress
to: core
type: blocker
needs_reply_by: 2026-11-22
refs: [run:D-bh-dress-20261115-143918-a5c125a, run:D-bh-dress-20261115-121313-284ec4f, problems/puncture/horizon_calib.athinput]
---
The release card executable `/data/haiyangw/nrpic/.work/build_gpu_c3/src/athena` does
not push the six massless tracers of `problems/puncture/horizon_calib.athinput` along
geodesics. In Track D's run D-bh-dress-20261115-121313-284ec4f (that input with
tlim = 500) one tracer is excised at t = 0.31 M and the other five (three circular
equatorial orbits at r = 6, 8, 10 M, one inclined, one plunge) move outward together near
light speed and leave the mesh by 182 M. With the earlier executable
(`runs/puncture/single_v3`, same input) the circular orbits stay at r = 6-11 M for 250 M
and the plunges fall in. Figure: `puncture_drift/figs/tracer_check.png` (comparison run
D-bh-dress-20261115-143918-a5c125a, both runs' `punc.traj.bin` and `punc.nrpic.hst`).

The tracers carry no mass, so the spacetime and Track D's horizon-mass numbers are
unaffected; but every Track D matter run pushes particles with this executable, and the
first full-relativity run (ES-1) measures tracer areal radii against an exact solution.
Not investigated by Track D: whether the push itself or the reading of `p<n>_u<i>` (index
position or normalization of the initial four-velocity) differs between the builds.

Smallest acceptable answer: the cause, and either a fixed release build or the input
convention that makes the six tracers of `horizon_calib.athinput` follow their geodesics
again (acceptance: the circular orbits stay within 1 per cent of their radius for 250 M,
as in `single_v3`).
