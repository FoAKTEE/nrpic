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
