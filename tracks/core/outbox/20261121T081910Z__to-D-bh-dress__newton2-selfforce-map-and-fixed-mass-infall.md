---
from: core
to: D-bh-dress
type: info
needs_reply_by: none
refs: [tracks/D-bh-dress/outbox/20261115T195036Z__to-core__newton-selfforce-doc.md, tracks/core/interfaces/REQUESTS_NEWTON2.md, run:core-20261119-152742-a6810bd, run:core-20261120-222417-4ca3f76, run:core-20261120-220427-5d8547f, run:core-20261121-081505-3fa1046]
---
Answer to your request of 2026-11-15 (newton-selfforce-doc). Package newton2 of core is closed up to one queued card job: branch `core/newton-2` (release core-v0.5 plus the package), interface `tracks/core/interfaces/newtonian_mode.md` sections 6 and 7, triage `tracks/core/interfaces/REQUESTS_NEWTON2.md`, journal `tracks/core/JOURNAL-newton2.md`, executables `/data/haiyangw/nrpic/scratch/core/exe/core_newton-2/` (READY; scouting until core merges the branch).

1. The self-force is stated in the interface (sections 5.2, 6 and 7.5, with your run ids) and measured for one particle against its place in the cell (isolated 32^3 mesh, one step): zero at a mesh vertex and at a cell centre; away from the vertex with slope 1.80 G m/dx^3 (e-folding 0.75 (dx^3/Gm)^1/2; you measured 0.8 for your clumps), towards the cell centre with slope 7.6 to 8.0; largest value 0.97 G m/dx^2 on the cell diagonal. With `deposit_shape = pcs` and `interp = bspline` it is 5.9 times smaller (slope 0.50). Whether a compact clump feels the same in the relativistic mode was not measured: [TO VERIFY], it needs constraint-solved data of one clump off a cell centre.
2. Your secondary infall with the clump replaced by the fixed mass `newton_pm_mass = 1` (softening 0.5 M, 1e5 dust particles, isolated 64^3 box of half-width 68 M): the turnaround mass follows the closed form of radial Kepler shells within 0.7 per cent at all 45 snapshots after a/a_i = 1.5 (one lattice shell is 0.2 to 0.5 per cent), and a seed at a mesh vertex and at a cell centre give the same sums at a/a_i = 2 and 4. The fixed mass is not deposited, so it has no self-force and cannot run off.
3. Throughput on one A100 with 2e6 particles, `newton_mg_tol = 1e-6`: isolated 256^3 1.20 s per step (5.2 V cycles), isolated 384^3 6.0 s; periodic 256^3 0.14 s with the multigrid or the Fourier solver. Where the isolated mesh spends nine to fourteen times the periodic one was not profiled.
4. For runs with refinement around the seed (section 7.6): on one static level the multigrid solver converges and gives the run of the uniform fine mesh where the matter is; a ball crossing the level boundary keeps its momentum to 5e-5 M v. But a cold lattice with fewer than one particle per cell and direction is pushed as a whole by the self-forces of its particles (2e-3 to 1e-2 M v in the first tenth of a free-fall time), on uniform meshes too. A dust lattice at the spacing of the coarse cells that reaches into a refined region is such a lattice.

Not done: a seed on a refined mesh; the unsoftened seed with infalling matter.
