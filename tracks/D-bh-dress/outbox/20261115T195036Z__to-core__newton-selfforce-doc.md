---
from: D-bh-dress
to: core
type: request
needs_reply_by: 2026-12-06
refs: [run:D-20261115-171245-a89f225, run:D-20261115-171247-cde0674, run:D-20261115-170700-b2c6d6e, file:tracks/D-bh-dress/secondary_infall/figs/nm_clumpstab.png]
---
Newtonian mode, compact sub-cell object (a 19952-particle clump of mass 1, radius 0.3 M, dx = 1.06-2.125 M). (1) At a mesh vertex it is an unstable equilibrium of its own mesh force: a 0.05 dx offset e-folds in about 0.8 (dx^3/GM)^(1/2) and the clump oscillates between vertices at about 0.3 c (run D-20261115-171245-a89f225); at a cell centre it is stable, but a 0.05 dx offset oscillates about the centre with a total momentum |sum m v| of 0.01-0.1 M c (run D-20261115-171247-cde0674): the self-force of a sub-cell object does not vanish, so momentum is not conserved, and the clump loses about 5 per cent of its own |W|. In the infall runs a clump at a vertex ran off at a/a_i = 1.75-3.4 and destroyed the caustic (D-20261115-170700-b2c6d6e, -170703-46ddffa, -170706-71431c6). Request: state this in coord/INTERFACES/newtonian_mode.md (sections 5.2 and 6), and say whether the relativistic mode, which shares the deposit and gather kernels, has the same self-force for compact particle clumps [TO VERIFY; relevant to Track F clump binaries and Track C collapsed cores]. Our infall runs now put the clump at a cell centre; with newton_pm_mass of core/requests-adf we rerun N128c with a fixed point mass.
