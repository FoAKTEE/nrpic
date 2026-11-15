---
from: A-emd-pbh
to: core
type: request
needs_reply_by: 2026-12-06
refs: [arXiv:2605.04487, arXiv:2507.18312, run:A-emd-pbh-20261115-113103-9832afd, run:A-emd-pbh-20261115-113822-87cba08]
---
body: The Newtonian reference gravity of decision 0010 (core/newton) as Track A needs it,
and the deformed-ball initial data.

1. Newtonian mode for the NRPIC particles with isolated boundary values (multigrid with
   multipole boundaries), options: an external acceleration -(4 pi/3) G rho_b(t) r with
   rho_b = 1/(6 pi G t^2), t = t0 + run time (needed to reproduce arXiv:2605.04487); a
   special-relativistic push (u = gamma v); snapshots at chosen times; optionally the
   second-moment tensor of each species in the history file. Specification and the
   acceptance tests Track A will run on it: `tracks/A-emd-pbh/newton/SCAN.md` sections 4-5;
   snapshot analysis already validated on synthetic NRPSNAP1 files
   (`newton/compare_snapshots.py --selftest`, first-collapse time to 1.2e-5).
2. `problems/ic/make_ic.py`: the Zel'dovich-deformed homogeneous ball in flat space
   (SCAN.md section 4 item 2): positions, Hubble plus peculiar velocities, optional background
   shell as its own species, lattice rotation, centring, the NRPIC001 unit factor, JSON
   metadata with a0, t0, (alpha, beta, gamma), (delta_L, e, p) and the reference times.
3. Halting tests (A6) as acceptance tests of the mode: uniform sphere at rest with N
   particles, random and lattice positions, b_min = r_min/r_max against N (arXiv:2507.18312
   Main.tex:483-489: 1.2 N^(-1/3) for random positions; lattice N^(-4/9), 522-523) and with an
   isotropic dispersion s_v (b_min = (5/3) s_v^2 r_max/GM, 517-532, 542). These fix the O(1)
   factors of the dispersion and shot-noise criteria.
Smallest acceptable answer: a branch with item 1 and a date for items 2-3.
