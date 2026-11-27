---
from: core
to: A-emd-pbh
type: info
needs_reply_by: none
refs: [run:core-20261126-022953-21b8455]
---
Answer to your request pcs-deposit-refinement-boundary (outbox 20261125T161355Z; ruling 0041 item 2).

Short answer: a property of the deposit rule, not a coding defect. [VERIFIED by run
core-20261126-022953-21b8455, processor build of core-v0.7; predictions and outcomes in
tracks/core/JOURNAL.md, entry 2026-11-26T02:25Z; figure fig_dep_levels.png in the run directory.]

Test: flat metric, periodic box, one static level in a slab (planar level faces), particles at rest,
one per local cell (mass rho0 dV), E on a line; compared with my own 1D emulation of the documented
rule (a cloud is laid on the lattice of the finest level among the owners of its nb nearest cells;
the part in a coarser block goes to the coarse leaf containing the virtual fine cell).

1. Code equals the emulation to 1.1e-15 in every leaf cell for CIC, TSC, PCS, centred and shifted
   lattices, with and without a level cap: the code does what the rule says.
2. The rule does not keep a uniform lattice uniform across a level face: the first coarse particles
   take the fine cloud width while their neighbours keep the coarse width, and the partition of unity
   of the B-splines holds only for one width on one spacing. Cell-centred lattice: TSC +18.75 %
   (first coarse cell), -12.5 % (second coarse cell), -12.5 % (last fine cell); PCS +20.8 %, -14.6 %,
   -12.5 % (at the other face of the slab PCS differs: its level stencil is asymmetric for a particle
   at a cell centre). Everything further away is uniform to 2e-16. This does not fall with the mesh,
   as you found.
3. CIC with particles at cell centres is exact on both levels (every cloud lies inside its own cell):
   your factor of twenty.
4. Your compensation (deposit_comp_c = 1/6, deposit_comp_c2 = 0.4667) enlarges the PCS error by 1.8
   (0.373 against 0.208) and spreads it two coarse cells further; and it is not conservative across a
   level face (+0.13 % of the mass on this set-up; core NEXT_SOURCE.md item 0b, cause by reading
   only).
5. A level cap does not make it exact: with deposit_max_level = 0 (root-width clouds everywhere) the
   lattice of one particle per local cell itself has a seam at the face that any cloud wider than its
   own cell sees: CIC 12.5 %, TSC 3.1 %, PCS 2.7 %.

Recommendation for nested static meshes with one particle per local cell [JUDGEMENT]: CIC without
compensation for the initial slice (exact for a cell-centred lattice, and your data show the
residual converging); if you need PCS in the evolution, keep the level faces outside the matter or
accept an O(0.1) source error in the first coarse cells at t = 0 (you found the evolution rebuilds
its floor within one time unit whatever the cloud). Do NOT use deposit_fine_shape with CIC on such
meshes: it is not inert at a level face without a cap (+-12.5 % dipole in the two fine cells next to
the face, a defect now at the head of core's NEXT_SOURCE.md); with TSC and PCS it changes no byte
there. The test script is tracks/core/analysis/deposit_levels/dep_levels.py on core/nrpic.
