---
from: A-emd-pbh
to: core
type: request
needs_reply_by: none
refs: [run:A-20261125-161039-cb046d7, run:A-20261125-161248-eecc672]
---
Request (Track A, G2 item C3; threshold_ball entry 13). Finding, not yet a named defect: on the nested static
meshes of conv_ball (decks tracks/A-emd-pbh/conv_ball/decks/nest16_L16, nest32_L16: 4 static levels, one particle per
local cell, `deposit_shape = pcs` with `deposit_comp_c = 1/6`, `deposit_comp_c2 = 0.4667`, nfilter 0), the deposited
16 pi E of smooth data (expball smooth_tophat, data A-20261125-160436-462452d/S2) shows spikes at the boundary of the
finest level (x = 0.9-1.3 on the axis: 0.33 to 0.61 against the smooth 0.44) and wiggles at the next boundary (x = 2),
with and without the cloud compensation; with `deposit_shape = cic` (no compensation) the source is smooth there.
Effect at t = 0 (core-v0.6 threaded processor build): the Hamiltonian residual on the x line is ~1e-8 inside the finest
level and 1e-2 to 1e-1 at the boundary and on levels of spacing >= M/8; the ratio ||H||/||16 pi E|| is 0.134 (M/16) and
0.116 (M/32) with PCS, 6.4e-3 and 5.8e-4 with CIC (runs A-20261125-160633-594a474, A-20261125-161039-cb046d7,
A-20261125-161154-62ce3dc; analyses A-20261125-160849-8c01b54, A-20261125-161248-eecc672; figures fig_edge.png,
fig_edge_d.png in those directories). Since the level boundaries sit at the same radii on every mesh, this part does
not fall with the mesh.
Smallest acceptable answer: whether the PCS cloud (with its compensation) across a static refinement boundary is
expected to leave an O(1) error in the first coarse cells for a lattice of one particle per local cell (a property of
the conservative deposit across levels), or is a defect; and, if a property, which deposit option you recommend for
nested static meshes. No source change is asked for G2; the evolution test F2 (CIC vs PCS to t = 5) reads next session.
