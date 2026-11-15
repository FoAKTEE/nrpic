# JOURNAL of core, work package coll (Monte Carlo collisions)

Append-only, newest at the bottom. Predictions are written before a test runs, outcomes
after. Labels: [VERIFIED], [BACKGROUND], [JUDGEMENT], [TO VERIFY]. Run outputs live under
`scratch/core/<run_id>/`, manifests under `tracks/core/runs/<run_id>/`.

## 2026-11-15 13:05 UTC  session core-coll  start, reading, design

Worktree `wt/core-coll`, branch `core/collisions`; merged `main` (a1c2237) and `core/rng`
(a6e5c46) -> 94dc093. Read: `CLAUDE.md`, charter to the end of "Owners", decision 0010,
brief lines 30-68, 84-137, 493-552, 688-706, 747-764, 834-860; `rng.md`; the particle
module (`particles.hpp`, `nrpic.cpp`, `nrpic_kernels.hpp`, `nrpic_mesh.hpp`,
`nrpic_metrics.hpp`, `nrpic_kick.cpp`, `nrpic_io.cpp` in part, `particles_tasks.cpp`);
`pgen/nrpic/nrpic_geodesic.cpp`; the track's package at `track/C-sidm` 4c76ca8
(`collide/SPEC.md`, `TESTS.md`, `RNG_REQUIREMENTS.md`, `README.md`).

Facts from the code that shaped the design [VERIFIED by reading]:
- `ParticlesIndex` interleaves positions and momenta: IPX=0, IPVX=1, IPY=2, IPVY=3,
  IPZ=4, IPVZ=5 (`athena.hpp:72`); IPM=6, IPTAU=7.
- With an analytic metric (`metric = kerr_schild` ...) `NrpicExcise` neither wraps the
  positions nor assigns MeshBlocks (`nrpic.cpp:628-634`): positions run out of a periodic
  box and PGID stays at the first block. The collision operator therefore wraps a copy of
  the position and looks the block up itself.
- With the mesh metric the pusher reconstructs the metric from `(x - xmin)/dx` of the
  particle's own MeshBlock, so particle states differ at rounding level between two
  MeshBlock divisions even without collisions (`rng.md` section 9). Exact layout
  independence can be shown only on the analytic path; on the mesh path the operator is
  layout independent given identical input states.
- The processor build is serial (`scripts/README.md`); the Boris pusher builds its triad
  with `nrpic::BuildTriad` (S S^T = gamma, coframe e^(m)_j = S[j][m]).
- MeshBlock edges come from `LeftEdgeX(lx, nmb, xmin, xmax)` with exact `xmin`, `xmax` at
  the mesh boundary (`meshblock.cpp:39-57`).

Design: `tracks/core/interfaces/collisions.md` sections 1-7 and 10, written before the
code. Decisions that go beyond the track's specification [JUDGEMENT]:
1. Cell index from tabulated global face positions (host table built with `LeftEdgeX`,
   block edges checked against it), not from the block-relative division: the set of
   particles of a cell is then exactly independent of the MeshBlock division.
2. Per-cell lists by counting sort on the device (atomic counts, prefix scan, atomic
   fill); the nondeterministic fill order is removed by the in-cell heap sort on
   (pairing word, tag), which the pairing needs anyway.
3. History records are per step (no running sums), so a restart needs no stored state.
4. Unequal masses: Nanbu-Yonemura rule, conservation in expectation, defect recorded;
   exact conservation only for equal masses (argument in section 3.6 of the interface).

Builds: baseline executables from a `git archive` of 94dc093 (`.work/build_cpu_base`,
`.work/build_gpu_base`), new ones in `.work/build_cpu`, `.work/build_gpu`.

### Predictions, written before any collision run (13:40 UTC)

Notation: N_tot particles of rest mass M in a periodic Minkowski box of volume V_box,
rho_0 = N_tot M / V_box, sigma = `coll_sigma`, theta = T/m, zeta = 1/theta,
Gamma = rho_0 sigma <v_Mol>, <v_Mol> = 4 K3(2 zeta)/(zeta K2(zeta)^2) (the track's
formula R; I check it by Monte Carlo over sampled pairs in the analysis before using it).
Box: `problems/tests/coll_box.athinput`, `pgen_name = nrpic_geodesic`,
`metric = kerr_schild` with `bh_mass = 0` (exactly flat: g = identity, lapse 1), box away
from the origin, periodic mesh, `deposit = false`: the fixed-metric path.

P0 Kernel (track's T0, 209 vectors with outputs from a 60-digit evaluation): every
   u_a', u_b' within 1e-13 max(1, |u_a|, |u_b|); pair four-momentum conserved to 4 eps of
   the pair energy. Refuted by one case outside.
P1 Regression: with no `collisions` option the new executable writes byte-identical
   output files to the baseline executable for the five existing set-ups of the rng
   regression (analytic metric; mesh metric with deposit; refined mesh with deposit and
   excision; Z4c with particle sources; restart with removal). Refuted by one differing
   byte in a case whose baseline is itself reproducible.
P2 `collisions = true` with `coll_sigma = 0`: particle snapshots byte-identical to the
   run without the option (the operator writes momenta only for accepted pairs).
P3 Rate, Maxwell-Juttner gas, theta in {0.01, 0.1, 1, 10}, positions uniform random:
   sum_P per step = (1/2) N_tot Gamma dt within 4 standard errors and 0.5 percent; the
   number of collisions equals sum_P within 4 sqrt(sum_P); with sub-cycling active
   (P before sub-cycling about 0.5, `coll_pmax = 0.1`) the same holds, with n_sub about 5;
   the gas stays at its temperature. A code with |v_a - v_b| instead of v_Mol would be
   off by tens of percent at theta >= 1. A wrong factor N - 1 (N or N/2 pairs) would
   show as a deviation of order 1/<N> (3 percent at <N> = 30) and grows for the small
   cells of P8.
P4 Conservation: with equal masses the pair defects are rounding: abs_dE/n_coll below
   8 eps x (2 M <W>) and abs_dP/n_coll below 4 eps x 2 M <|u|> + eps; total energy and
   total momentum from snapshots (exactly rounded sums) constant to 1e-13 relative
   (energy) and 1e-13 of sum M |u| (each momentum component) over the whole run. Rest
   masses and positions of all particles and the momenta of particles that did not
   collide are untouched (bit) by the collision step (replay dump).
P5 Relaxation of a non-thermal start: (a) monoenergetic isotropic shell |u| = u0 (the
   distribution of the Shapiro-Teukolsky clusters), u0 = 0.3 and u0 = 2; (b) two
   temperatures theta_1 = 3 theta_2, theta_2 = 0.01 and 1. After 20 collision times the
   distribution of |u| is Maxwell-Juttner at theta_eq fixed by the conserved energy
   (<W> = W(u0), or the mean of the two populations): Kolmogorov-Smirnov p > 1e-3,
   <u^2/W>/3 = theta_eq within 4 sigma; for (b) both tag populations at theta_eq within
   4 sigma, and the initial slope of theta_1 - theta_2 in the limit dt -> 0 equals
   -(4/3) sqrt(2/pi) rho_0 sigma sqrt(theta_1 + theta_2) (theta_1 - theta_2) at
   theta_2 = 0.01 within 3 percent (the track's non-relativistic closed form; relativistic
   corrections of order theta). Refuted by a KS failure or a slope off by more.
P6 Entropy: the estimate s = -sum_b p_b ln(p_b / vol_b) + (B - 1)/(2N) (radial histogram
   in |u|, Miller-Madow term) grows monotonically within its standard error from the
   start to s_MJ(theta_eq) = zeta <W> + ln(4 pi K2(zeta)/zeta) and stays there. Refuted by
   a decrease beyond 4 sqrt(2) standard errors between snapshots at least a quarter
   relaxation time apart, or an end value off by more than 4 standard errors plus the
   bias of the estimator measured on an exact Maxwell-Juttner sample of the same size.
P7 Reproducibility on the analytic path (two-temperature box, 1e5 particles, 100
   cycles, seed 7): final snapshots byte-identical for 1, 8 and 64 MeshBlocks and for a
   run restarted at cycle 37; integer columns of `coll.hst` identical; another seed gives
   a different state. Control on the mesh path (flat metric carried by the mesh, `<adm>`):
   restart identical, layouts NOT identical after 100 cycles (rounding of the metric
   reconstruction, amplified by the first acceptance that flips), statistics equal.
P8 Convergence. (a) Time step: the decay rate of theta_1 - theta_2 fitted over
   [0, 1/nu_0] is nu_eff = nu_0 (1 + nu_0 dt_c/2 + c), dt_c = dt/n_sub the collision
   sub-step and c independent of dt: first order, because disjoint pairs of one step all
   use the momenta at its start (forward Euler in expectation). Runs at nu_0 dt = 0.4,
   0.2, 0.1, 0.05 without sub-cycling: successive differences of nu_eff halve, ratio
   between 1.5 and 2.7 given the noise; the run with nu_0 dt = 0.4 and sub-cycling to
   `coll_pmax` such that n_sub ~ 8 agrees with the nu_0 dt = 0.05 run within noise.
   (b) Cell size, homogeneous gas: the rate of P3 holds within 4 sigma and 0.5 percent
   for mean occupations <N> from 0.5 to 500 per collision cell (same box, mesh cells
   8^3 to 64^3 and `coll_cell_factor` 1, 2, 4), because uniform random positions give
   E[N (N - 1)] = <N>^2 (1 - 1/N_tot); the relaxation curve of P5(b) is the same within
   noise. (c) Cell size with a gradient: decay of an isobaric temperature mode,
   k lambda = 0.3, cells dx/lambda = 2, 1, 1/2, 1/4 through `coll_cell_factor` and the
   mesh: the decay rate (conductivity) rises with the cell size, second order in
   dx/lambda [BACKGROUND: Alexander, Garcia & Alder 1998, not re-read], and the two
   finest differ by less than 3 percent. (c) runs only if card time is left.
P9 Card: rate and relaxation statistics as on the processor within 4 sigma; snapshots
   byte-identical between 1 and 64 MeshBlocks on the card. Processor and card states are
   not expected to be identical (contraction of products and sums in the kinematics).
P10 Curved spacetime, static homogeneous metric (lapse alpha_0, gamma_ij = constant,
   not diagonal), mesh path: collisions per coordinate step = flat value x
   alpha_0/sqrt(det gamma) for the same particle file with u_i = S u_hat; sum of M u_i
   conserved to rounding; relaxation to Maxwell-Juttner in the triad components.
P11 Stable relativistic cluster y_c = 0.819 (first paper, `problems/st`), 1e4 particles,
   Knudsen number of order 30 or more, 150 M: central lapse, mass-shell radii and
   constraint norms follow the collisionless run within the differences between seeds
   recorded in `docs/TESTLOG.md` (lapse 0.804 to 0.838); no particle lost; sum of rest
   mass identical to the bit; the pair defects are rounding; the change of the history
   sum_mW attributable to collisions is below 1e-4 of its value.
