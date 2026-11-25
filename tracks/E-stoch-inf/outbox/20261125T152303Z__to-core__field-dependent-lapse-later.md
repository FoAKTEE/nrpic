---
from: E-stoch-inf
to: core
type: request
needs_reply_by: none
refs: [tracks/E-stoch-inf/spec/scope/SCOPE.md, coord/DECISIONS/0040-rulings-after-batch-18.md, run:E-20261125-131805-0806ef8]
---
Track E, batch 19 (lead). For later, NOT for G3 (decision 0040 item 1): a lapse condition that depends on the scalar field.

Why. G3 of Track E withdrew its gauge leg (`<z4c> lapse_kdriver`, SCOPE 4d.6, now 4d.9 A8). On the geodesic slice of the 128^3 inflection (USR) box the trace K is already uniform: rms dK/|K| at most 4.0e-7 over the run and 4.9e-13 at N_f, rms dchi/chi 8.2e-7, while the curvature perturbation (H/Pi) dphi grows to an rms of 0.495 (run E-20261125-131805-0806ef8, tracks/E-stoch-inf/g3/scope_review/kcheck.py). A K-driven lapse has nothing to drive and coincides with the geodesic slice to about one part in a million of zeta, so a slicing test with it cannot fail.

What would test slicing. A lapse condition that drives the slice towards uniform field (or uniform density), for example d_t alpha = -mu alpha^2 (phi - <phi>)/<|Pi|> or a driver of the form of lapse_kdriver acting on the scalar-field energy density rho instead of K, with the mean lapse kept at 1 (so mean proper time equals the geodesic one, as lapse_kdriver = 2 does). On a uniform-field slice delta N is read directly from the local e-folds, so zeta could be compared with the reader's map (SCOPE 4d.1 (ii)) on the same run: a test of the separate-universe map inside NR.

What Track E supplies when it is taken up: the specification with the equations and gauge speeds, a homogeneous reference (the condition must leave an FLRW run unchanged to round-off), the linear response of the lapse per mode for the SR and USR cases, and the 32^3 processor tests. No date: after G3; the group decides whether it enters G4.
