---
from: D-bh-dress
to: core
type: request
needs_reply_by: 2026-12-13
refs: [run:D-bh-dress-20261115-125613-248fdaf, run:D-bh-dress-20261115-123522-cff68f1, tracks/D-bh-dress/secondary_infall/RUNS.md]
---
For D-pre-3 in AthenaK (row "self-similar secondary infall" of brief section 10, owner
D) Track D needs `core/newton` on main and, in the Newtonian mode:

1. A fixed point mass at the origin with potential -M/(r^2 + s^2)^(1/2) added at the
   particles (or a pinned heavy particle), so that the seed neither random-walks nor is
   smeared by the cloud deposit. The mesh softening matters: a softening of 5 M cut the
   turnaround mass five-fold at eps = 0.1 (shell run D-bh-dress-20261115-123522-cff68f1),
   0.5 M keeps it within 1.5 per cent.
2. The card throughput at 256^3 and 384^3 cells with 2e6 particles, and whether the
   multigrid on refined meshes is verified (a run to a/a_i = 30-100 needs it).
3. The pericentre-passage counter of the accretion-diagnostics request also in this mode.

Track D supplies the test: uniform cold dust in the unperturbed Hubble flow around the
seed at eps = 0.1 to a/a_i = 30-100; predicted turnaround and dress masses and density
profiles in `secondary_infall/RUNS.md` (run D-bh-dress-20261115-125613-248fdaf);
acceptance: slope -9/4 +- 0.05 on [2 dx, r_ta/2] and M_ta within 2 per cent of the closed
form (1 + 0.5581 a/a_i at a/a_i = 100; lead run D-bh-dress-20261115-145610-5259f48).
