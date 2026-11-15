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

## 2026-11-15 13:20-13:30 UTC  first build, smoke run, kernel test

- Processor and card builds compile (`.work/build_cpu`, `.work/build_gpu`).
- Smoke run (build check, not registered, no number taken from it for a result):
  20000 Maxwell-Juttner particles at theta = 0.1 in 8^3 cells, 50 steps, sigma = 8:
  about 494 collisions per step, sum of M W constant to 4e-15. Files in
  `scratch/core/coll-tmp/smoke1/`. Mistake: I first ran it in `scratch/core/tmp/smoke1/`,
  a directory of another core session (its `ball.*` files, written at 11:28 UTC, are
  untouched), and overwrote the `athena.log` there; my build logs
  `scratch/core/tmp/build_{cpu,gpu}{,_base}.out` may likewise have replaced files of
  the same name. From here on this package writes only under `scratch/core/coll-tmp/`
  and `scratch/core/<run_id>/`.
- The smoke run shows that the error model of prediction P3 is wrong, before P3 was
  run: sum_P per step was 492.60 +- 0.23 (scatter between steps) against the nominal
  494.45, i.e. -0.37 percent or 8 "standard errors". Two effects are not in the scatter
  between steps: (i) the cell populations hardly change in 50 steps, so
  sum_c N_c (N_c - 1) is one draw of a random number with relative standard deviation
  sqrt((4/mu + 2/mu^2)/C) (mu particles per cell, C cells: 1.4 percent here, 0.2 percent
  for 1e6 particles in 32^3 cells); (ii) the sample of 20000 has its own temperature
  (sum M W = 1.16649 against 1.16699 for theta = 0.1) and its own shape.
  Added to the history: column 27, sum_W (sum_P without the Moller speed), so that the
  pair counting and the kinematics can be tested separately.

### P3 restated before the run (13:30 UTC); the first version is superseded

P3a (exact, pair counting): at the cycle of the last snapshot,
   sum_W = sigma M dt/(2 V_cell) sum_c N_c (N_c - 1) with N_c counted from the snapshot
   positions, to 1e-12 relative, with and without sub-cycling.
P3b (kinematics): sum_P/sum_W summed over the run equals the mean Moller speed of
   random pairs of the actual particles (4e6 pairs from the first and the last snapshot)
   within 4 standard errors, and <v_Mol>(theta_s) of a Maxwell-Juttner gas at the
   temperature theta_s of the sample (from its sum M W) within 0.3 percent.
   theta in {0.01, 0.1, 1, 10}. |v_a - v_b| instead of v_Mol would be high by tens of
   percent at theta >= 1.
P3c (counting): collisions over the run = sum of sum_P within 4 sqrt(sum_P).
P3d (unconditional rate): sum of sum_W over the run = (1/2) N_tot rho_0 sigma dt x steps
   within 4 x sqrt((4/mu + 2/mu^2)/C) relative (one frozen configuration as the
   conservative error), i.e. 0.8 percent for 1e6 particles in 32^3 cells.
P3e the gas stays Maxwell-Juttner: |u| at the end against MJ(theta_s),
   Kolmogorov-Smirnov p > 1e-3.
Runs: 1e6 particles, 32^3 cells, 200 steps of dt = 0.01, Gamma dt = 0.015 with
`coll_pmax = 1` (no sub-cycling) and Gamma dt = 0.15 with `coll_pmax = 0.1`.

### Outcome P0 (13:26 UTC), run core-20261115-132556-a7dc8ab

Passed. 208 of the 209 vectors apply (one has unequal physical masses, which the kernel
does not treat: one species). Largest error of u' over max(1, |u|): 2.6e-16 (-O0, -O2,
-O3 without contraction, Python twin), 3.2e-16 with contraction; pair energy within
1.32 eps, momentum within 0.63 eps of the pair energy; Moller speed within 1.04e-15
relative (the case of identical velocities gives exactly 0, the 60-digit reference
4e-31). The three compilations without contraction give identical bits; the Python twin
differs from them in the last place in some outputs. Figure `fig_kernel_test.png` in the
run directory (looked at: all points three orders below the tolerance). The first run of
the driver (core-20261115-132525-e67ed74) reported a relative error 1 of the Moller
speed for that one case; the driver's metric was wrong, not the kernel.

### P6 statistic refined before the production run (13:40 UTC)

Driver check at small size (scouting runs core-20261115-132811-b33b7f3 for the rate
driver and core-20261115-133017-b33b7f3 for the relaxation driver, 20000 particles in
8^3 cells; both drivers ran through, relaxation to Maxwell-Juttner visible). The
multinomial standard error of the absolute entropy estimate (0.009 at 20000 particles)
is ten times the scatter between late snapshots, because the run has a fixed total
energy and the dominant term of that error is the energy fluctuation of a free sample.
The reference is now: bias b and scatter sd_b of the estimator at fixed energy, measured
on 16 exact Maxwell-Juttner samples of the same size, each compared with the exact
entropy at its own temperature. Criteria (stricter than before): end value within
4 sd_b of s_MJ(theta_eq) + b; no decrease beyond 4 sqrt(2) sd_b between snapshots at
least a quarter relaxation time apart.

## 2026-11-15 13:45 UTC  outcome of P1 (processor), P2, P3, P4; a bias found and removed

### P1, processor: run core-20261115-132618-1a050f3

Passed. Five existing set-ups, 36 output files, baseline (94dc093) twice and the new
executable once: no differing byte (c1 5 files, c2 3, c3 14, c4 4, c5 10). The source
has changed since (sub-step rule, below): the regression is repeated with the final
executable.

### P2, P3, P4: run core-20261115-132842-b33b7f3 (1e6 particles, 32^3 cells, 200 steps)

Figures looked at: `fig_rate_history.png`, `fig_rate_summary.png`,
`fig_rate_conservation.png` in the run directory.

- P2 passed: the final snapshots of the run without the option and of the run with
  `coll_sigma = 0` are byte-identical; the run without the option writes no `coll.hst`.
- P3a FAILED as written. sum_W of the code differs from sigma M dt/(2 V) sum N (N - 1)
  of the snapshot by 4.7e-14 to 4.6e-12 relative, above my 1e-12 in five of eight runs.
  My threshold ignored the rounding of the sum itself: the code adds 5e5 to 1.7e6 terms
  that take few distinct values to one accumulator, so the rounding errors do not
  average out; the bound of a sequential sum is n eps/2 = 5.8e-11 to 1.9e-10. All values
  are below it, and one miscounted pair would change the sum by 2e-6. The criterion is
  now the rounding bound (n_tested eps). Pair counting, volume and time factors are
  therefore right to rounding, also with sub-cycling and with the triples of odd cells.
- P3b: passed without sub-cycling: mean Moller speed of the tested pairs against random
  pairs of the actual particles z = +0.9, +1.6, +0.5, -0.6 (theta = 0.01, 0.1, 1, 10),
  against Maxwell-Juttner at the sample temperature -7.7e-5, +3.9e-5, -2.1e-5, -6.0e-5.
  FAILED with sub-cycling: z = -6.1, -7.1, -7.3, -4.7, i.e. low by 0.095, 0.112, 0.119,
  0.117 percent, the same sign at every temperature (red curves of
  `fig_rate_history.png` lie below one throughout).
  Cause as I understand it, to be tested by the fix: the number of sub-steps was taken
  from the largest probability of the first pairing, and that same pairing is then
  tested with weight 1/n_sub. A first pairing that happens to contain fast pairs gets
  more sub-steps and is diluted by more fresh pairings than one with slow pairs, so
  E[(v_0 - <v>)/n_sub] < 0. My design argument ("the expectation is right for any
  n_sub") holds only if n_sub does not depend on the pairing. This rule is the one of
  the track's SPEC.md 4.5.
  Fix: n_sub from the particles of the cell alone, P_bound = (N - 1) sigma_max M_cell
  min(v_1 + v_2, 2) alpha dt/V with the two largest speeds of the cell (v_Mol <=
  |v_a - v_b| <= v_a + v_b). Prediction for the rerun, written before it: the
  sub-cycled runs agree with the pair average within 4 standard errors and with
  Maxwell-Juttner within 3e-4, like the plain runs; n_sub is larger than before (the
  bound is not attained by the pairs); if the deficit of 0.1 percent stays, the cause
  named above is wrong.
- P3c passed: collisions against sum_P, z between -1.1 and +1.5 (1.5e6 and 1.5e7
  collisions per run).
- P3d passed: sum_W over the run against (1/2) N rho_0 sigma dt x 200 within 5e-5 in all
  runs (allowed 8e-3).
- P3e passed: KS p of |u| at the end against Maxwell-Juttner 0.23 to 0.996.
- P4 passed: the exactly rounded sums of M W over the 1e6 particles at t = 0 and at the
  end are equal to the last bit in all eight runs (up to 1.5e7 collisions); the
  momentum components change by at most 4.6e-19 of sum M |u|; largest mean pair defect
  per step 0.46 eps of the pair energy and 0.28 eps of the pair momentum scale. The
  history column sum_MW (a plain floating sum) scatters by 1.7e-13 relative.

## 2026-11-15 13:50 UTC  outcome of P7 (first run), prediction for a second box

Run core-20261115-133737-82e2040 (1e5 particles, 100 cycles, 4.97e5 collisions,
sub-cycling active). Figure `fig_repro.png` looked at.
- Analytic path: all five snapshots byte-identical for 1, 8 and 64 MeshBlocks; integer
  history columns identical; restart from the dump of cycle 37 gives the identical last
  snapshot and identical history records (1 and 64 MeshBlocks); seed 8 instead of 7
  changes all 1e5 particles from the first cycle on. Passed.
- Mesh path: restart identical (passed). The two layouts are ALSO byte-identical,
  against my prediction. Reason, by inspection of the numbers: the box [100, 101]^3 with
  32^3 cells has block edges and a cell size that are exact binary fractions, so
  (x - xmin)/dx of two MeshBlock divisions differ by an exact integer and the metric
  reconstruction rounds identically. The momenta of the mesh path differ from the
  analytic path by at most 3.6e-15 (99930 particles), with the same collisions.
  So this box cannot show the limitation of `rng.md` section 9, nor does it exercise the
  face table of the collision cells.
- Prediction for a second box, [100.3, 101.2]^3 with 30^3 cells in 1 or 27 MeshBlocks
  (faces are not binary fractions), written before the run: analytic path byte-identical
  (this is what the tabulated faces are for; with the block-relative cell index a
  particle within rounding of a face could change cell). Mesh path: NOT byte-identical;
  my first prediction ("amplified by the first acceptance that flips") was also wrong in
  its mechanism: a flip needs a uniform deviate within 1e-16 of a probability, which
  does not happen in 5e6 tests, so the difference stays at rounding level: most
  particles differ, by less than 1e-13 in u, and the integer history columns are
  identical.

## 2026-11-15 14:00 UTC  outcomes P3 (rerun), P5, P6, P7 (second box); P8a restated

### P3 after the change of the sub-step rule: run core-20261115-133533-0ca5e3b

Passed, all eight runs. Sub-cycled runs (mean n_sub 3.4 to 4.3, largest 10, max P 0.113):
mean Moller speed of the tested pairs against random pairs of the actual particles
z = -1.7, +0.5, +1.4, +0.7; against Maxwell-Juttner +2.6e-6, +4.9e-6, -3.2e-5, -4.5e-5
(theta = 0.01, 0.1, 1, 10). The deficit of 0.1 percent is gone, in a run that could have
kept it: the cause named above stands. Plain runs unchanged (same numbers as before, as
they must be: no sub-step is taken). P3a: 4.7e-14 to 5.4e-12, below the rounding bounds
1.2e-10 to 5.1e-10. P3c: |z| < 1.6. P3d: within 6.2e-5. P3e: p from 0.34 to 0.996.
P4: exact sums of M W equal to the last bit in all runs; momentum within 3.5e-19 of
sum M |u|. P2: null runs byte-identical. Figures `fig_rate_history.png` (red curves now
centred on one), `fig_rate_summary.png`, `fig_rate_conservation.png` looked at.

### P5, P6: run core-20261115-134036-5684674 (4e5 particles, 16^3 cells, 25 collision times)

Passed, all four starts (shell u0 = 0.3 and 2; two temperatures 0.03/0.01 and 3/1).
- End state: KS p of |u| against Maxwell-Juttner at theta_eq (from the conserved
  energy) 0.90, 0.74, 0.45, 0.26; <u^2/W>/3 = theta_eq within 0.06 sigma; both tag
  populations of the two-temperature starts at theta_eq within 0.52 sigma.
- Entropy estimate: rises from -3.612 to -0.9800 (shell 0.3; exact MJ value -0.9824,
  estimator bias +0.0023), 2.150 to 4.917, -1.5715 to -1.5238, 8.2616 to 8.3842; end
  values within 1.4 sd of s_MJ + bias (sd at fixed energy 1.0e-4 to 1.4e-4); largest
  decrease between snapshots a quarter relaxation time apart 2.4 sd/sqrt2 units, i.e.
  noise. The gap to equilibrium falls by four decades and then scatters around zero
  (`fig_relax_entropy.png`); `fig_relax_distributions.png` and
  `fig_relax_temperatures.png` looked at.
- Energy: exact sums equal at start and end (one run differs by one unit in the last
  place); 25 collisions per particle; no probability above one.
- The initial slope of theta_1 - theta_2 (second half of P5(b)) is not measured here
  (one snapshot per collision time); it is part of P8a.

### P7, second box: run core-20261115-133912-f104754

Passed as predicted. Box [100.3, 101.2]^3, 30^3 cells: analytic path byte-identical for
1 and 27 MeshBlocks (3.6e5 collisions); mesh path differs in 99979 of 1e5 particles by
at most 4.9e-15 with identical integer history columns (the pusher's metric
reconstruction, `rng.md` section 9), while the first box stays byte-identical on both
paths. No MeshBlock edge differs from the tabulated faces (no warning in any log).

### P8a restated before the run

The series nu_0 dt = 0.4, 0.2, 0.1, 0.05 without sub-cycling that I wrote first cannot
be run: the mean pair probability is 1.5 nu_0 dt and pairs in the tail exceed one. The
plain series is nu_0 dt = 0.1, 0.05, 0.025, 0.0125 (`coll_pmax = 1`, no probability above
one expected: checked by n_trunc), the sub-cycled run nu_0 dt = 0.4 with
`coll_pmax = 0.225` (about eight sub-steps). theta_1 = 3e-3, theta_2 = 1e-3 (the
closed form is non-relativistic), 1e6 particles, three seeds each; the temperatures come
from the new history columns 28, 29 (energy of species 0) at every step. Fit of
ln(theta_1 - theta_2) over [0, 2/nu_0]. Predictions: (i) nu_fit = nu_inf + s dt_c with
s = nu_inf^2/2 within 15 percent (first order with the forward-Euler coefficient);
(ii) the sub-cycled run lies on the same line at its mean sub-step dt/<n_sub>, far from
the value nu_inf + s 0.32 of a plain step; (iii) nu_inf/nu_0 between 0.95 and 1.02 (the
fit window is not the initial slope: the populations leave the Maxwellian form).

### Prediction for the replay test, before the run (14:10 UTC)

`run_replay.py`: the Python twin, written from the interface text, repeats the collision
step of cycle 5 from the dump of the code, in seven cases (flat box with sub-cycling;
`coll_cell_factor = 2`; `coll_subcycle = conservative`; cross-section model `cutoff`;
unequal masses with `nanbu`; homogeneous curved metric on the mesh with the symmetric
triad; the same with the Cholesky triad and the Boris pusher). Predicted for every case:
cell indices recomputed from the positions equal those of the dump; n_sub and the number
of momentum updates of every particle equal; n_tested, n_coll, n_updated equal to the
history record; sum_P within 1e-11; momenta after the step within 1e-13 max(1, |u|);
particles without an update bit-identical before and after. Any mismatch refutes either
the code or the interface text.

## 2026-11-15 14:20 UTC  outcomes: replay, P8a; P8b restated

### Replay: run core-20261115-134644-466dcfd

Passed in all seven cases. The twin reproduces the cell indices, n_sub and the number of
momentum updates of every one of the 20000 particles, n_tested, n_coll and n_updated of
the history record (for example 75739 pairs tested, 2412 collisions, 3718 updates with
`nanbu`), sum_P to 2e-14, and the momenta after the step to 8.9e-16 max(1, |u|) in the
flat cases and 9.8e-15 (symmetric triad), 2.8e-15 (Cholesky triad, Boris pusher) in the
homogeneous curved metric. Particles without an update are bit-identical before and
after. Figure `fig_replay.png`.

### P8a: run core-20261115-134511-0607ce8 (1e6 particles, three seeds per point)

Figure `fig_conv_dt.png` looked at (right panel: four points on a straight line, the
sub-cycled point on it at its own sub-step).
- (i) passed. Fitted decay rates 1.2293(36), 1.2004(34), 1.1875(23), 1.1786(23) for
  nu_0 dt = 0.1, 0.05, 0.025, 0.0125 (nu_0 = 1.25 in the units of the box). Straight line:
  nu_inf = 1.1722(21), slope 0.716(59) against the forward-Euler value nu_inf^2/2 = 0.687
  (chi^2 = 0.3 for 2 degrees of freedom). Successive differences 0.0289, 0.0129, 0.0089
  (ratios 2.2 and 1.4; halving expected, standard errors about 0.004 each). First order
  in the collision sub-step, with the predicted coefficient.
- (ii) passed. Sub-cycled run (step 0.32, nu_0 dt = 0.4, mean n_sub 7.7): 1.1939(60)
  against 1.2020 on the line at dt/<n_sub> = 0.0416 (z = -1.3); a plain step of that
  size would give 1.40.
- (iii) FAILED as written: nu_inf/nu_0 = 0.938, below my interval 0.95 to 1.02. The fit
  over [0, 2/nu_0] is not the initial slope; I underestimated how much the decay slows
  as the populations leave the Maxwellian form (left panel: the compensated curves bend
  in the first half of the window). The initial slope (quadratic fit of ln D over the
  first fifth of the window) is 1.2975(81), 1.273(11), 1.260(11), 1.2572(39) for the four
  steps; removing the first-order term with the fitted slope gives 1.250(4) at dt -> 0
  from the finest step, i.e. 1.000(4) of the non-relativistic closed form of the track
  (P5(b): within 3 percent, passed; the track's relativistic value at theta_2 = 1e-3 is
  0.995 of it, SPEC.md section 6).

### P8b restated before the run

`run_cells.py`: 4e5 particles, collision cells from 2^3 to 64^3 (50000 to 1.5 particles
per cell), two seeds. Predictions: pair counting exact to rounding at every size
(including cells of two and three particles, where the triple of odd cells carries most
pairs); collisions = sum_P within 4 sigma; summed weight = nominal within 4 x the
frozen-population scatter; (32,1) and (64,2), and (16,1) and (64,4), byte-identical.
Decay rate of theta_1 - theta_2: I predicted "the same within noise" for all sizes. On
reflection I expect that to FAIL for 1.5 particles per cell: a particle moves 0.07 cell
per step there, so the same two particles are paired and collide repeatedly, which
exchanges energy inside the pair instead of mixing the populations; the decay should be
slower (by an amount I cannot predict), while the number of collisions stays right.
For 6 particles per cell and more I expect no difference beyond 4 sigma.

## 2026-11-15 14:40 UTC  outcome P8b; prediction for unequal masses; card jobs

### P8b: run core-20261115-135219-42c8489 (4e5 particles, two seeds)

Figure `fig_cells.png` looked at.
- Pair counting against the cell populations of the last snapshot: 3.7e-13 to 4.9e-12
  at every size, 2^3 to 64^3 collision cells (50000 to 1.5 particles per cell, where
  118000 of 262144 cells hold a pair), below the rounding bound. Passed.
- Collisions against sum_P: |z| <= 1.6; summed weight against nominal: within 1e-3
  (allowed 1.3e-2). Passed: the number of collisions does not depend on the cell size.
- (32,1) = (64,2) and (16,1) = (64,4): final snapshots byte-identical. Passed: the
  blocks of f^3 mesh cells are the cells of the coarser mesh.
- Decay rate of theta_1 - theta_2 over nu_0: 0.957(12), 0.951(6), 0.948(6) for 50000,
  781, 98 particles per cell; 0.926(4) for 12.2 (-2.6 percent, z = -4.2); 0.879(5) for
  1.5 (-7.5 percent, z = -11). My first prediction ("the same within noise at every
  size") FAILED; the restated one holds at 1.5 per cell and FAILED marginally at 12 per
  cell, where I expected nothing beyond 4 sigma. Consistent with repeated partners:
  particles move 0.035 (0.07) cell per step and stay about one (half a) collision time
  in a cell of the 32^3 (64^3) mesh, so with few particles per cell the same pairs meet
  again and exchange energy among themselves. This is a statement about this box (slow
  particles, cells of the order of the mean free path); the mechanism was not isolated
  by a control (for example the same occupation with fast-moving particles), so it is
  [JUDGEMENT]. Consequence for users, [VERIFIED] here: the relaxation rate is within one
  percent for about 100 particles per collision cell and low by a few percent for about
  10; the collision count is unbiased throughout.

### Prediction for unequal masses, before the run

`run_unequal.py`: two classes of equal number, masses 1 : 4, theta 0.03 (light) and
0.01 (heavy), 2e5 particles, 25 collision times, four seeds with `nanbu`.
- `coll_weights = equal` on this file: the run stops at the first collision step with
  the error that names the two masses.
- Both classes end at the same temperature within 4 sigma and are Maxwell-Juttner (KS
  p > 1e-3 against the temperature of the final energy). A pairwise exactly conserving
  scheme would leave the heavy class colder per unit mass (equipartition per
  macroparticle: factor 4 in theta), far outside.
- Momentum updates per collision at late times: 20/13 = 1.538 (pair probabilities
  light-light : heavy-heavy : mixed = 1 : 4 : 8 for equal numbers and one temperature,
  updates 2, 2, 5/4), within 4 sigma.
- In one step the light and the heavy particles receive the same number of updates
  within 4 sigma of the Poisson error (every macroparticle changes momentum at the rate
  of its physical particles, whatever its mass).
- Energy and momentum are not conserved pair by pair: the cumulative defects of the
  history equal the change measured from the snapshots (to 1e-9 of the thermal energy),
  and their mean over the seeds is zero within 4 standard errors. Expected size of the
  energy random walk: about 1e-2 of the thermal energy [JUDGEMENT: sqrt(collisions) x
  theta/N].

### Card jobs

The node has four cores in all. My first submission (job 4419, part A, with `-c 4`,
queued 13:35 UTC) would have kept the second card idle while a one-core job ran on the
first; cancelled and resubmitted with two cores (4424 part A, 4425 part B, 14:36 UTC).
4424 started at 14:38 UTC.

## 2026-11-15 15:05 UTC  card results (parts A, B); unequal masses; P11 restated

### Card, part A (job 4424, 0.037 card-hours)

- P1 on the card: run core-20261115-135757-18d4555. c1 (analytic metric) and c2 (mesh
  metric, one particle with deposit): all files identical between the baseline and the
  new executable. c3, c4, c5: the baseline is not reproducible run to run on the card in
  2, 2 and 3 files (`tpc.nrpic.hst`, `tpc.trajmet.bin`; `flrw.cstat.hst`,
  `flrw.nrpic.hst`; the three `.rst` files), and exactly these files differ between
  baseline and new; the other 12, 2 and 7 files are identical. So: no file differs that
  the baseline reproduces, and no verdict on the files it does not. (The same limit is
  recorded for the card regression of the random-number package.)
- P9, rate: run core-20261115-135816-18d4555. All eight runs pass with the criteria of
  P3. The numbers of collisions are those of the processor run, digit for digit
  (1500395, 15000024, 1500294, 14998415, 1501865, 14998790, 1501368, 14998645), and so
  are the z values; 1e6 particles x 200 steps take 2 to 4 s.
- P9, relaxation: run core-20261115-135932-18d4555. All four starts pass; KS p,
  entropy values and population temperatures equal those of the processor run to the
  printed digits.

### Card, part B (job 4425, 0.013 card-hours)

- P9, reproducibility: run core-20261115-140011-18d4555. On the card: analytic path
  byte-identical for 1, 8, 64 MeshBlocks, for the second box with 1 and 27, and across
  the restart; mesh path byte-identical in the first box, 5.8e-15 apart in the second
  with identical collisions; restart identical. Passed.
  Processor against card (same input, runs core-20261115-133912-f104754 and
  core-20261115-140011-18d4555): the last snapshots are NOT byte-identical (98143 of 1e5
  particles differ, by at most 1.8e-15 in u and 6e-13 in x), with the same 496813
  collisions: as predicted in P9 (contraction of products and sums), and without a
  flipped acceptance in 5e6 tests.
- P8a on the card with 4e6 particles: run core-20261115-140021-18d4555. nu_inf =
  1.1792(16), slope 0.744(32) against nu_inf^2/2 = 0.695; decay rates 1.2388(17),
  1.2095(27), 1.1931(18), 1.1874(18); sub-cycled 1.2022(12) at dt_c = 0.0348 against
  1.2051 on the line (z = -1.5; mean n_sub 9.2). Initial slope 1.3123(25), 1.2689(7),
  1.2577(29), 1.2505(16); Richardson value of the two finest steps 1.2433(43), i.e.
  0.995(4) of the non-relativistic closed form: the track's exact relativistic value is
  0.995 (SPEC.md section 6, its run C-sidm-20261115-120703-9b3e868). Passed.

### Unequal masses: run core-20261115-140030-7a0efc0 (processor, 2e5 particles, 4 seeds)

Passed. Figure `fig_unequal.png` looked at.
- `coll_weights = equal`: the run stops with "<particles> coll_weights = equal, but the
  colliding particles have unequal rest masses (smallest and largest:
  1.9999999999999999e-06 and 7.9999999999999996e-06) ...".
- `nanbu`: light and heavy class end at the same temperature (difference 0.1 to 0.6
  sigma; 0.01407 against 0.01407 in seed 1) and are Maxwell-Juttner (KS p 0.36 to 0.96).
- Momentum updates per collision at late times 1.538, 1.539, 1.539, 1.539 against 20/13
  = 1.5385 (z = -1.7, +0.7, +1.8, +3.4; my standard error ignores the fluctuation of
  the pair mix).
- One step (cycle 300): updates of light and heavy particles 5033/4940, 4980/4921,
  4987/4994, 4988/5082 (|z| < 1).
- Energy defect over the thermal energy after 25 collision times (3.26e6 collisions):
  -8e-5, -6.3e-3, -4.3e-3, +2.9e-3; mean -0.0020(21), scatter 0.4 percent. Momentum
  defect: scatter 3.2e-3 of sum M |u|, mean 1.8 sigma. The defects summed from the
  history equal the changes measured from the snapshots to 7e-15.

### P11 restated before the run (the null part)

The card regression shows that runs with deposit are not reproducible run to run on
the card. The null prediction "operator on with sigma = 0 is byte-identical to operator
absent" can therefore hold only on the processor (checked there on a short run), and on
the card the null run is compared with a repeat of the baseline: its difference from
the baseline (central lapse over the run, positions at the end) must not exceed ten
times the difference between the two baseline runs.

### Prediction for the refined mesh, before the run (15:25 UTC)

`run_smr.py`: periodic box with the octant [100, 100.5]^3 refined by one level, 2e5
Maxwell-Juttner particles, 40 steps, MeshBlocks of 16^3 and 8^3 cells and
`coll_cell_factor` 1 and 2. Predicted: level and collision cell of every particle as
assigned from the geometry (octant: 64 cells per unit length, elsewhere 32); summed
weight = sigma M dt/2 x sum over the cells of both levels of N (N - 1)/V_cell to
rounding; collisions = sum_P within 4 sigma; total weight within 2 percent of the
nominal rate (it does not depend on the cell size); snapshots byte-identical for the two
MeshBlock divisions; no warning about MeshBlock edges.

## 2026-11-15 15:40 UTC  outcomes: refined mesh, P10 (curved box)

### Refined mesh: run core-20261115-140539-54f8bee (processor)

Passed. Level and collision cell of all 2e5 particles as assigned from the geometry
(24681 particles in the refined octant), for MeshBlocks of 16^3 and 8^3 cells and for
cell factor 2; summed weight against the cell populations of both levels 1.6e-13 to
5.0e-13; collisions 200632 (factor 1, both divisions) and 200058 (factor 2), z = 1.3 and
0.2 against sum_P; total weight within 2.3e-4 of nominal; snapshots of the two MeshBlock
divisions byte-identical; no warning about MeshBlock edges. Figure `fig_smr.png`
(occupation of the cells of both levels; the two divisions coincide).

### P10: runs core-20261115-140259-8742cdf (card), core-20261115-140147-15c576d (processor)

Passed on both; the numbers of collisions are the same on card and processor. Homogeneous
metric with lapse 0.7 and sqrt(det gamma) = 1.1044, 2e5 particles, 400 steps, about 20
collisions per particle. Figure `fig_curved_box.png` looked at (card run).
- Pair counting with the factor alpha/sqrt(gamma): 0 to 1.1e-16 (card), 1.4e-13
  (processor) against the snapshot populations.
- Collisions: 1993695 (symmetric triad, midpoint pusher), 1992802 (Cholesky triad, Boris
  pusher), 1993138 (flat box with the same triad momenta and the same rate per
  coordinate time): z = +0.28 and -0.17 against flat; z = 0.34 and -0.36 against sum_P.
- Mean Moller speed of the tested pairs in the last quarter against random pairs of the
  triad momenta of the last snapshot: z = -0.48, +0.49.
- Conservation from the snapshots (exact sums): sum of M W with gamma^ij changes by
  1.0e-14 and -8.8e-16 relative; the components of sum M u_i by at most 5.1e-17 of
  sum M |u_hat|. Mean pair defect 0.39 eps of the pair energy.
- Energy with the metric reconstructed at each particle (`coll_budget`): summed change
  over the 400 collision steps 1.2e-14, -2.0e-15 (card) and 3.7e-15, -3.2e-14
  (processor) relative. These are differences of two plain sums of 2e5 terms; their
  size is that of the rounding of the sums, so the statement is "no change above 3e-14".
- Relaxation: KS p of the triad |u| against Maxwell-Juttner 0.78 and 0.92; both
  populations within 0.73 sigma of theta_eq.
The first processor run of this driver (core-20261115-135349-1134b04) stopped in the
analysis because the flat reference run had failed: the box deck did not contain
`coll_budget`, which the driver sets on the command line (fixed in the deck).

## 2026-11-15 16:05 UTC  outcome P1 (final), P11; a systematic energy gain found

### P1 with the final source

Runs core-20261115-140120-7a0efc0 (source of the test runs) and
core-20261115-140938-0f9d0cf (final source, which differs from it by three wrapped
lines in `nrpic_collide.cpp`): all 36 files of the five set-ups byte-identical to the
baseline. With the final executable the reproducibility test was repeated (run
core-20261115-140950-0f9d0cf): passed, and every snapshot of its nine run variants is
byte-identical to that of the earlier build (run core-20261115-133912-f104754), so the
collisional results obtained with the earlier builds since the change of the sub-step
rule hold for the final source.

### P11: runs core-20261115-135728-18d4555 (processor, 2 steps), core-20261115-140316-8742cdf (card, 150 M)

Figure `fig_cluster.png` looked at.
- Null on the processor (two steps of the full problem: Z4c, six refinement levels,
  deposit): operator on with sigma = 0 gives byte-identical snapshots and particle
  history to operator absent. Passed.
- Null on the card: the baseline repeated differs from itself (central lapse by 9.8e-15
  over the run, positions at t = 150 M by 3.7e-13), as the card regression suggested; the
  run with sigma = 0 differs from the baseline by 8.3e-15 and 3.0e-13. Passed in the
  restated form.
- Kn = 30 (sigma = 6.753, collision cells of 4^3 mesh cells = 2 M, 19 particles per
  occupied cell, largest cell size over mean free path 0.012): 470 collisions in 1200
  steps (sum_P = 461.3, z = +0.4), 0.094 momentum updates per particle. Central lapse
  within 0.0024 of the collisionless run at all times (ranges 0.8080 to 0.8147 against
  0.8094 to 0.8159); radii of 10, 50, 90 percent of the rest mass within 2.3 percent at
  all snapshots; no particle lost, rest mass identical to the bit, deposit identity
  1.0e-15. Passed by the criteria written before the run (0.017 and 10 percent). Looking
  at the figure, the difference is not noise: from t = 25 M on the lapse of the
  collisional run lies below the collisionless one, the sign of the Kn = 3 run.
- Kn = 3 (sigma = 67.53): 5001 collisions (sum_P = 5037, z = -0.5), one update per
  particle. Central lapse falls to 0.7914 at t = 150 M; the 10 percent radius shrinks
  from 3.13 to 2.59, the 90 percent radius grows from 8.03 to 8.70. Observation only:
  collisions change the structure within five dynamical times at this Knudsen number;
  nothing here says whether the rate of that change is right.
- Energy. Pair energies in the cell frame: conserved to rounding (mean defect 1.2 eps of
  the pair energy, sum over the run 1.8e-19 of sum M W). Energy with the metric at each
  particle (the history's sum_mW; its record in `coll.hst` agrees with `nrpic.hst` to
  4e-16): the collision steps change it by +3.9e-6 of its value at Kn = 30 and +5.2e-5
  at Kn = 3 over the run, below my bound of 1e-4, but it is a steady gain, proportional
  to the number of collisions: 8.3e-9 and 1.05e-8 of sum M W per collision, about 5e-5
  of a pair's energy. My design note said "random sign". That was wrong.
  Explanation to be tested: the two particles of a pair sit at different depths of the
  potential inside one collision cell. The collision conserves the energy measured
  with the metric of the cell centre, and on average moves kinetic energy from the
  deeper (faster) particle to the shallower one without the potential difference being
  paid: Delta(sum M W) ~ +(grad psi . Delta x)^2 x (kinetic energy), second order in the
  cell size and always positive.
  Prediction, written before the run (card, part D): at Kn = 3 with collision cells of
  2^3 and 1^3 mesh cells the gain per collision is 1/4 and 1/16 of that with 4^3
  (2.6e-9 and 6.6e-10 of sum M W), within 40 percent; the number of collisions is
  unchanged within 4 sigma. If the gain does not fall with the cell size, the
  explanation is wrong.
