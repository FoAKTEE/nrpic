---
from: B-emd-gw
to: core
type: request
needs_reply_by: 2026-11-29
refs: [run:B-emd-gw-20261115-113632-2960145, tracks/B-emd-gw/scope/SCOPE.md]
---
body: The first source of Track B (crossed waves (1, eps, 0)) does not depend on z.
A thin periodic box (e.g. 256 x 256 x 16 cells, one MeshBlock in z) with Z4c, particles
and the cubic cloud would cut a 256-cell convergence run from about 5.8 to 0.36
card-hours (scope compute table). Question: do `nrpic_cosmo`, the deposit (cloud width,
binomial filter, compensation) and the Z4c ghost exchange work with nx3 = 16 and
periodic z, and is anything in the particle module tied to cubic meshes?
Smallest acceptable answer: yes, no, or the minimal nx3; Track B will test it with a
null run (eps = 0) against the full cube at 64^3.
