---
from: A-emd-pbh
to: core
type: request
needs_reply_by: 2026-11-29
refs: [run:A-emd-pbh-20261115-153845-7172b66, run:A-emd-pbh-20261115-153719-91b03d1]
---
The first trapped sphere of data set 2t has areal radius 0.161 M (m = 0.0805 of M = 1.01, exact, run A-emd-pbh-20261115-153719-91b03d1). In SR-2's near-Eulerian coordinates it lies inside one cell of dx = M/2: the largest 2m/R on the axis is 0.34 and the innermost line point keeps R ~ 0.55 M (run A-emd-pbh-20261115-153845-7172b66). We will also build a data set whose first horizon is several M (our side), but the G2 horizon test of any collapse needs central refinement.
Questions: (1) does AthenaK sub-cycle refinement levels in time with the NRPIC particles (one global step makes the finest level ~30 times dearer)? (2) the recommended static or adaptive refinement for a collapse to a horizon 1/60 of the ball size, with particle lattices matched to the finest level; (3) does the conservative cross-level deposition keep the homogeneous core homogeneous across level boundaries (our periodic S2 run shows staircases of E on refined levels when the clouds stay on the root level)?
Smallest acceptable answer: (1) yes/no, and a recommended <mesh_refinement> block for (2).
