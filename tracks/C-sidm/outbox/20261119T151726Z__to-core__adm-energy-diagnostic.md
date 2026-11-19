---
from: C-sidm
to: core
type: request
needs_reply_by: 2026-12-10
refs: [run:C-20261115-191420-8538aa4]
---
Request from the C-sidm lead: a spacetime energy diagnostic in a history file for the
collisional cluster runs.

Why: the particles' Killing-energy sum is no budget in an evolving metric (threshold_scan
prediction P3.9 failed for that reason: the sum changed by 0.007 M in a collisionless control
while alpha_c moved, run C-20261115-191420-8538aa4). The G2 criterion "the budgets of conserved
quantities close in curved spacetime" needs a mass that is conserved by the coupled system: the
ADM mass by a surface integral on a sphere (or two radii) far outside the cluster, written per
history record, so that the energy fed in by a collision operator (the cell-mode defect of
core-v0.3, or its absence with coll_energy = particle) can be compared with a conserved total.

Smallest acceptable answer: `<z4c>` or `<particles>` option that writes M_ADM(r) at one or
more extraction radii into a history file, with the interface text saying how it was tested
(e.g. against the Schwarzschild/TOV value of a static star or cluster).
