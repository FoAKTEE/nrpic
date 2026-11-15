---
from: C-sidm
to: core
type: request
needs_reply_by: 2026-12-06
refs: [tracks/C-sidm/collide/TESTS.md, tracks/C-sidm/collide/SPEC.md]
---
body: Test T12 of `collide/TESTS.md` (collisions in curved spacetime, G2) needs a static,
homogeneous, non-flat metric: constant lapse alpha0 and conformal factor psi0, zero shift,
particles with collisions, no Z4c evolution, periodic box. Pass criterion: collisions per
coordinate step and coordinate volume equal alpha0 psi0^6 times the flat value at the same
proper density and temperature, within 4 sigma; conservation of sum M u_i as in T1. Asked:
an option of the `nrpic_geodesic` problem generator (for example `metric = static_conformal`
with `alpha0`, `psi0`), or the name of an existing set-up that gives this. Smallest
acceptable answer: whether it can be done with an existing option.
