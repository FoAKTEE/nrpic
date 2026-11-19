# JOURNAL of core, work package newton2 (branch `core/newton-2`)

Append-only. Predictions are written before a test runs, outcomes after, also when the
prediction failed. Runs are registered under `tracks/core/runs/<run_id>/manifest.json`
(outputs under `scratch/core/<run_id>/`). Labels: [VERIFIED] read or measured in this
session (with locator), [BACKGROUND], [JUDGEMENT], [TO VERIFY].

## 2026-11-19 session newton2-1 (wave 3a)

Read: `CLAUDE.md`; charter to "Owners"; brief lines 493-553, 688-706, 834-860; decisions
0010, 0016, 0017; `harness/RULES.md`; `scripts/README.md`;
`tracks/core/interfaces/newtonian_mode.md`, `REQUESTS_ADF.md`;
`athenak/src/particles/nrpic_newton.cpp`, `nrpic_external.hpp`, `nrpic_mesh.hpp`,
`particles.hpp`, `gravity/mg_gravity.cpp` (lines 30-320), `gravity/gravity.{hpp,cpp}`;
`python/nrpic/newton.py`, `cosmo/newton/pm.py`, `problems/newton/*`; the four requests
(`git show track/B-emd-gw:tracks/B-emd-gw/outbox/20261115T191056Z__to-core__newtonian-
laplacian-order.md`, `...__newtonian-species-history.md`,
`track/A-emd-pbh:.../20261115T183721Z__to-core__newton-mode-followup.md`,
`track/D-bh-dress:.../20261115T195036Z__to-core__newton-selfforce-doc.md`); Track B's
`newton_tests/README.md`, `inputs/pancake.athinput`, `scripts/make_particles.py`,
`baseline/BASELINE.md` section 4, `baseline/scripts/ellipsoid.py`; Track A's
`newton/SCAN.md` sections 1-5, `newton/README.md`, `newton/make_deformed_ball.py`; Track
D's `secondary_infall/README.md`, `nm_ic.py`, `nm_infall.athinput`.
Triage: `tracks/core/interfaces/REQUESTS_NEWTON2.md`.

State of the worktree: `git merge main` (clean); `athenak/` equals the source of the
published executables of `core/requests-adf` (`git diff 3f75eb8 HEAD -- athenak` is
empty) [VERIFIED]. Baseline executables: release core-v0.3
(`/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena`) and the branch start
(`scratch/core/exe/core_requests-adf/athena_cpu`, sha256 17ee5e28...).

### Design decisions [JUDGEMENT]

1. Laplacian order (B). A Fourier solve on the periodic uniform mesh, not a Mehrstellen
   stencil inside the multigrid module: the code base has no Fourier library
   (`grep -ri fft athenak/src` finds none; the top-level CMake links FFTW only for
   Kadath), so the transform is written with Kokkos kernels in a new file
   (`particles/nrpic_newton_fft.cpp`: mixed radix 2, 3, 5, 7, one line per thread). It
   leaves the multigrid kernels untouched (another package changes neighbouring source),
   costs one hook line in `NrpicNewtonPotential`, and offers two symbols: `spectral`
   (K^2 = k^2) and `seven_point` (the symbol of the multigrid operator), the second as a
   cross-check of both solvers. Isolated and refined meshes keep the multigrid solver
   and its second order.
2. Species history (B, A). A new file per group, `<basename>.newton.g<g>.hst`
   (`particles/nrpic_newton_groups.cpp`): selection by species and tag range, nearest
   image about a reference point, moments about the centroid, comoving with
   conformal-time derivatives and physical with cosmic-time derivatives. The existing
   history is unchanged (bit-identical rule). The sums take one more gather per particle
   and are formed only for recorded states and the states one cycle before them.
3. Remainder step (B, low priority): the new group history skips the difference quotient
   after a step below 1e-6 of the one before; the existing d3I columns keep their
   behaviour (bit-identical rule) and the note says so.

### Predictions, written before any test of the new source ran

Executable: processor build of this branch (`.work/build_cpu`), one core per run.

**T1 Fourier solver against the multigrid solver and against numpy.**
Plane wave of `problems/newton` (N = 32, amplitude 0.25, shell crossing at a = 4, to
t = 3, `periodic.athinput`, cloud-in-cell, Catmull-Rom, dt = 0.005).
- T1a `newton_fft_symbol = seven_point` against the multigrid run of the same input
  (`threshold = 0`): the two potentials solve the same linear system, the multigrid to
  its rounding floor. Positions at every snapshot agree to 1e-10 of the box (I expect
  about 1e-12), K and W of the history to 1e-10 relative, Phi_min and Phi_max to 1e-10.
  Refuted (a wrong symbol, normalisation or index map) if any of these is above 1e-8.
- T1b `spectral` against the scheme of the code in numpy (`python/nrpic/newton.py`,
  `scheme_fields` with the symbol -k^2, to be added; stepping of `pm.py`): positions at
  all 12 snapshots within 1e-12 of the box (the seven-point twin agreed to 1.3e-15,
  `newtonian_mode.md` 5.6). Refuted above 1e-10.
- T1c mixed radix: a mesh of 48 x 80 x 112 cells (factors 3, 5, 7 times 16) with 2000
  massive particles at random positions, one step of 1e-6: the acceleration of every
  particle (momentum after the step over the step) against the numpy scheme on the same
  mesh, both symbols: relative difference below 1e-9 of the largest acceleration.
  Refuted above 1e-7.

**T2 Track B's pancake with the spectral symbol** (their P1: `pancake-east` particles,
delta = 0.05, L = 1, cubic cloud with compensation, cubic-spline force, step L/(4n);
their generator and input, `newton_poisson = fft`). Their measurement with the
seven-point solve, largest sheet error against Zel'dovich in units of the displacement
[VERIFIED, `newton_tests/README.md` P1, analysis B-20261115-173904-a7297e3]:
n = 16: 5.64e-3 (a = 2), 1.16e-2 (a = 5); n = 32: 1.39e-3, 2.99e-3; n = 64: 3.51e-4,
7.42e-4; `pm.py` (spectral): n = 32: 1.1e-4, 6.1e-4; n = 64: 4.8e-5, 3.3e-4.
Prediction: with the spectral symbol the mode differs from `pm.py` only in the gather
(gradient of the spline interpolant of the potential against the spline interpolant of
the spectral gradient), a fourth-order difference, (kh)^4/180 = 8e-6 at n = 32. So the
error at n = 32 is 1.1e-4 at a = 2 and 6.1e-4 at a = 5 within 30 per cent (at least
seven times below the seven-point value at a = 2), at n = 64 4.8e-5 and 3.3e-4 within 30
per cent, and the mode minus `pm.py` falls below 5e-5 at a <= 5 for n = 32. With
`seven_point` the numbers of the track's table are reproduced to three digits (same
operator as the multigrid). Refuted if the n = 32 error at a = 2 stays above 5e-4.

**T3 Group history on the exact pancake** (Track B's P2 particles `pancake-sin`, n = 32,
equal masses, never wrap before a = 20; run to a = 16).
- T3a group 1 = all particles, reference point = middle of the box: its comoving
  moments about the centroid equal those of the existing history after the
  parallel-axis shift (I - M X X and its derivatives) to 1e-12 of their size; refuted
  above 1e-10.
- T3b the columns J, dJ/dT, d2J/dT2 equal the conversion of the comoving columns done in
  Python to 1e-13 relative; d3J/dT3 equals the difference quotient of d2J/dT2 in cosmic
  time to 1e-10.
- T3c group 2 = the slab L/4 <= q_x < 3L/4 (a tag range): exact solution x = q + a psi,
  I_xx = c0 + c1 a + c2 a^2 about the centroid at L/2. The track measured for all
  particles, n = 32, seven-point: I_xx - c0 2.0e-3, dI 2.6e-3, d2I 1.6e-2, d3I 2.4 per
  cent rms (1.2 <= a <= 15) and attributed half to three quarters of the d3I error to
  the Laplacian. Prediction for the slab with the spectral symbol: I_xx - c0 and dI_xx
  below 5e-4 (at least four times better), d3I rms between 0.5 and 1.5 per cent (the
  part that is not the Laplacian remains). Refuted if I and dI improve by less than two.
- T3d restart: a run stopped at cycle 300 and continued gives group files identical byte
  for byte to the uninterrupted run. Refuted by any difference.

**T4 Ellipsoid of tracks A and B.**
- T4a generator: `problems/newton/make_ic.py ball --axes --vgrad [--rotate]` reproduces
  the particle file of Track A's `make_deformed_ball.py` for (delta_L, e, p) =
  (0.2, 0.2, 0) at hxi = 0.05, with and without rotation seed 3: positions, velocities
  and masses equal to 1e-13 relative, and the JSON carries the same volume radius.
  Refuted above 1e-10.
- T4b embedded ellipsoid (Track B's N2, model A of BASELINE.md 4.2): the 2605.04487
  benchmark patch at the turnaround of its first axis as species 0 inside background
  particles (species 1) at rest in comoving coordinates, periodic box of side 48 t_k
  with expansion (code time 0 = t_turn, a = 1 there), 64^3 cells (dx = 0.75), eight
  particles per cell in the patch, Fourier solver. Reference: the track's ODE
  (`baseline/scripts/ellipsoid.py`, model A): first crossing of the short axis at
  24.25 t_k, of the second at 31.40 t_k [VERIFIED, BASELINE.md 4.2]. Prediction from the
  track's N1 at the same cell size (N = 32 in a box of 24: crossing time +0.90 per
  cent): the semi-axis sqrt(5 J_xx/M) of group 1 from the physical columns reaches its
  first minimum at a cosmic time within 2 per cent of 24.25 t_k, and the three
  semi-axes follow the ODE to 3 per cent of R_L up to one t_k before the crossing. The
  periodic images and the excess mean density enter at (R/L)^3 = 2e-3. The same run
  with the multigrid solver differs in the crossing time by less than 0.3 per cent.
  Refuted if the crossing time is off by more than 5 per cent or the centroid of the
  patch moves by more than 0.05 dx.

**T5 Point-mass infall of Track D** (their N64c set-up: eps = 0.03, dust lattice for
3 M <= r < 18.35 M in the Hubble flow, isolated box of half-width 68 M, 64^3 cells,
dx = 2.125 M, multigrid with the multipole boundary), with the clump replaced by
`newton_pm_mass = 1` (softening 0). Reference: before a shell is crossed its enclosed
mass is constant and it moves on a radial Kepler orbit, so the mass inside the
turnaround radius at a given time is known in closed form (to be computed from the
particle file before the run; the track's clump runs gave 1.5064 and 2.5966 M at
a/a_i = 2 and 4, their shells with the mesh kernel 1.5058 and 2.5934).
Prediction: with the point mass at a mesh vertex and at a cell centre the turnaround
mass at a/a_i = 2 and 4 agrees with the closed form to 0.3 per cent and the two
placements agree to 1e-3 (the mass is not deposited, so it has no self-force and
cannot run off; the track's vertex clumps left at a/a_i = 1.75 to 3.4). Refuted if the
placements differ by more than 0.5 per cent or either is off the closed form by more
than 1 per cent.

**T6 Multigrid on a refined mesh** (core's deferred item). The moving, rotating ball of
`newtonian_mode.md` 5.5 (N = 64 root, uniform: centre of mass off uniform motion by
1.8e-5 R, momentum change 2.5e-5, angular momentum 4.3e-5, energy 1.4e-4), on a mesh
with one static level placed so that the ball crosses the level boundary during the run.
Prediction [weak: nothing of this kind has run]: the run completes, the solver converges
at every step, and the four conservation errors stay within ten times the uniform
values. Any failure (no convergence, a kick at the boundary above 1e-3) leaves refined
meshes "not verified" and is reported with its numbers.

**T7 Which energy the history reports (Track A).** By reading: column 6 is
W = sum m Phi(x_p)/(2a) with the potential gathered at the particle by the
interpolation of the force (Catmull-Rom or spline); column 7 is the mesh sum of the
deposited density. Neither is an invariant of the scheme: with deposit kernel S_d and
gather kernel S_g, dW/dx_p = (m_p/2) [grad(S_g * Phi) + grad(S_d * Phi~)](x_p), Phi~
the potential of the density deposited with S_g, which equals the applied force
m_p grad(S_g * Phi) only for S_d = S_g. The defect is of the size of the truncation
error where the density is smooth and of order one for a sheet thinner than a cell.
Prediction: for the plane wave of `problems/newton` (crossing at a = 4) the drift of the
Layzer-Irvine constant after the crossing (4.9e-3 at N = 32, 1.5e-3 at N = 64 of max
a|W|, `newtonian_mode.md` 5.6) changes by less than 20 per cent when the step is halved
(a property of the space discretisation), while before the crossing it follows the
resolution. Refuted if halving the step lowers the post-crossing drift by two or more
(then it is a time-integration error and the answer to Track A is different).

**T8 Self-force of a single particle (Track D's request for the note).** One particle
of mass 1 on an isolated 32^3 mesh (dx = 0.125), one step of 1e-6, placed on the line
from a mesh vertex to a cell centre along x and along the diagonal: g_max of the history
is its self-force. By symmetry it vanishes at the vertex and at the cell centre.
Prediction from the track's measurement (e-folding 0.8 (dx^3/GM)^(1/2) at a vertex for a
clump of radius 0.14 to 0.28 dx): near a vertex the force points away from it with a
slope between 1.2 and 2.5 G m/dx^3, near a cell centre it points towards the centre;
the largest value along x is between 0.2 and 0.6 G m/dx^2 (5.2 of the note: components
up to 0.36 to 0.58). With the cubic cloud and the cubic-spline gather the largest value
is at least three times smaller [weak]. Refuted if the vertex is stable or the cell
centre unstable.

**T9 Throughput on a card** (core's deferred item, Track D's question): 2e6 particles,
20 steps each: isolated 256^3 with the multigrid solver (`newton_mg_tol = 1e-6`),
periodic 256^3 with the multigrid and with the Fourier solver, periodic 384^3 with the
Fourier solver. Expectation from 0.65 s per step at 128^3 with 13 V cycles
(`newtonian_mode.md` 5.8): multigrid 256^3 between 1 and 5 s per step, the Fourier
solver below 0.5 s per solve at 256^3. No refutation attached: a measurement.

**T10 Regression.** With none of the new options in the input, the processor executable
of this branch gives output files identical byte for byte to the executable of the
branch start (`scratch/core/exe/core_requests-adf/athena_cpu`) for the Newtonian tests
(plane wave, collapse, point-mass tests of dfix) and the relativistic set of
`tracks/core/tools/regress_relativistic.py`, and to release core-v0.3 except where
`REQUESTS_ADF.md` section 4 (T6) lists a deliberate difference. Refuted by any
unlisted difference.

### T1 outcome (2026-11-19T14:52Z) [VERIFIED]

Runs: cases core-20261119-144414-c629377 (processors, 5 cases, 307 s on two cores),
analysis core-20261119-145129-e89a132 (`t1_fft.json`, figure `t1_fft.png`). Two earlier
analysis attempts are on record: core-20261119-144855-2a2ef23 failed because I started
it before the last case had ended; core-20261119-144933-515de0f completed but wrote its
files into a directory named by the unexpanded variable `$NRPIC_RUN_DIR` in the worktree
(nrpic-run starts the command without a shell); that directory was removed and the script
now takes the run directory from the environment.
- T1a seven_point against multigrid (13.1 V cycles per step on average, largest defect
  norm 1.7e-11): positions within 2.2e-15 of the box at all 13 snapshots, momenta within
  8.7e-15, K and W of the 601 records within 2.2e-13 relative, Phi_min and Phi_max within
  6.9e-15. Prediction (1e-10) held with five orders to spare.
- T1b spectral against the numpy scheme with the symbol -k^2: positions within 3.9e-16 of
  the box, momenta 1.4e-15. Held. (The seven-point Fourier run and the multigrid run
  agree with the numpy scheme of the seven-point operator to 2.2e-15 and 1.4e-15.)
- T1c mixed radix 48 x 80 x 112 (3, 5, 7 times 16): accelerations of 2000 particles
  against numpy within 1.8e-12 (spectral) and 3.6e-12 (seven_point) of the largest
  acceleration, rms 1.7e-13 and 3.1e-13. Held (bound 1e-9); the difference is the
  movement of the particles during the step of 1e-6.
- The spectral and the seven-point potential energies differ by 1.7 per cent of max |W|
  at N = 32 through shell crossing (a real difference of the two operators, not an
  error of either).
- Cost on one core at 32^3 with 32768 particles: 0.24 s per step with the Fourier
  solver against 0.34 s with the multigrid; the particle work dominates both.

### T5 closed form, computed before the run (amends the prediction of T5)

Set-up fixed for the processors the allotment leaves: 1e5 dust particles instead of
Track D's 5e5 (100 000 on the lattice of spacing 0.636 M, dust mass 2.7671 M, edge
18.35 M), softening `newton_pm_soft = 0.5` M (Plummer, as the track's wave-1 shell
reference: radial orbits pass through the seed, an unsoftened point mass would give
unbounded kicks), `newton_cfl = 0.15`, step at most 0.25 M. Closed form from the particle
file (`t5_infall.py --predict`, unregistered arithmetic on the generated file):
M_ta = 1.24616, 1.50428, 2.04929, 2.59430 M at a/a_i = 1.5, 2, 3, 4, the same for both
placements of the seed. The softening changes the force at the turnaround radii
(r > 8 M) by less than (s/r)^2 = 4e-3 and the turnaround mass by less than that.
Prediction as written: both placements within 0.3 per cent of these numbers at
a/a_i = 2 and 4, and within 1e-3 of each other.

### Amendments to the test plan, written before the runs concerned (2026-11-19T15:22Z)

Owner core runs eight packages at once and its allotment of 16 processor cores at a
time (decision 0006) is used up: `nrpic-run submit` accepted T1 and T2 with two cores
and refuses most other attempts ("16 busy in live local runs of core"). The tests are
therefore submitted one after another by a retrying queue
(`scratch/core/tmp/n2queue/queue.sh`), and trimmed:
- T2: n = 64 goes to the card job (two hours on one core); processors run n = 16, 32
  with the spectral symbol and n = 32 with the seven-point symbol.
- T3: the pancake runs end at t = 3.5 (a = 7.56) instead of a = 16; the error window of
  T3c is 1.2 <= a <= 7.56 for both symbols (the track's numbers for a <= 15 are then not
  directly comparable; the seven-point run is the like-for-like reference). The
  multigrid twin is dropped (T1a showed the seven-point Fourier run to be the multigrid
  run to 2e-15).
- T4b: step 0.04 instead of 0.02 (the track's step check at 0.01 against 0.02 changed its
  crossing time by 2e-7); the multigrid twin is its own case, T4c, last in the queue.
- T7: the two runs at half the step that answer Track A's configuration (cloud-in-cell,
  Catmull-Rom; multigrid and spectral); the cubic-cloud pair only if cores remain.
- T9 and the card twins of T1 and T3 wait in the card queue (job 4648, fifteen jobs
  ahead at submission).
Predictions are otherwise unchanged.

A debugging pass of the T8 cases and of its analysis script ran outside the registry
before the registered run (17 s on one core, `scratch/core/tmp/n2dbg/t8`): I have
therefore seen numbers of T8 (slope at the vertex 1.80 G m/dx^3 with cloud-in-cell and
Catmull-Rom) before the registered run; the prediction above was written before either.
The same holds for T1 (a debugging pass of the five cases before run
core-20261119-144414-c629377) and for a 16^3 smoke run of the group history with a
continuation (`n2dbg/t3smoke`, 6 s).

## 2026-11-19 session newton2-2 (resumed at 15:34Z)

The first session of this package stopped at 15:31Z with the queue of processor tests
(`scratch/core/tmp/n2queue/queue.sh`) still running; it was left running. To use the free
cores of the allotment, a second queue (`queue2.sh`, list `list2.txt`: T7, T6, T4c) runs
beside it; it claims its tests by a placeholder so that the first queue skips them. The
predictions above stand; nothing below changes them.

### T2 outcome (Track B's pancake with the spectral symbol) [VERIFIED]

Runs: cases core-20261119-150559-c1ff7ca (n = 16, 32 spectral, n = 32 seven-point; 686 s
on two cores), analysis core-20261119-153046-039c454 (Track B's own `analyze_pancake.py`
from the tip of `track/B-emd-gw`; `t2_pancake.json`, figure `t2_pancake.png`, looked at).
Largest displacement error against Zel'dovich in units of (a - 1) d/k (the track's
`ex_cont`):

| n, solver | a = 2 | a = 5 | a = 10 | a = 15 |
|---|---|---|---|---|
| 16, spectral | 3.28e-4 | 1.57e-3 | 4.21e-3 | 5.05e-3 |
| 32, spectral | 9.55e-5 | 5.56e-4 | 1.97e-3 | 1.79e-3 |
| 32, seven_point | 1.390e-3 | 2.993e-3 | 4.417e-3 | 5.763e-3 |
| 32, track's multigrid run | 1.39e-3 | 2.99e-3 | 4.42e-3 | 5.76e-3 |
| 32, track's `pm.py` | 1.1e-4 | 6.1e-4 | 2.1e-3 | 1.7e-3 |
| 32, spectral minus `pm.py` | 2.0e-5 | 6.6e-5 | 1.9e-4 | 3.5e-4 |

- n = 32 against `pm.py` within 30 per cent: 9.55e-5 against 1.1e-4 (-13 per cent) and
  5.56e-4 against 6.1e-4 (-9 per cent). Held. Below the seven-point value at a = 2 by a
  factor 14.6 (prediction: at least seven). Held.
- Mode minus `pm.py` below 5e-5 at a <= 5: 2.0e-5 at a = 2 held; 6.6e-5 at a = 5 FAILED
  (by 30 per cent). The difference grows with the nonlinearity faster than the
  fourth-order gather estimate (kh)^4/180 that I used; I have not separated the gather
  from the time integration (both codes use the same step), so no cause is named.
- seven_point reproduces the track's multigrid numbers: ratios 1.0000, 1.0011, 0.9993,
  1.0006 (prediction: three digits; held to 0.11 per cent, the a = 5 entry by a hair).
- Refutation (n = 32 at a = 2 above 5e-4): not refuted.
- n = 64 runs in the card job (pending).
- At n = 16 the spectral error is 17 times below the track's seven-point run at a = 2
  and 5 times at a = 15.

### T4a outcome (generator of the deformed ball) [VERIFIED]

Runs: core-20261119-152228-0ad3c0e (no simulation; 9 s), figure by
core-20261119-152928-6be4984 (`t4a_generator.png`, looked at: core's particles on Track A's,
aligned and rotated). (delta_L, e, p) = (0.2, 0.2, 0), hxi = 0.05, 33552 particles, with
and without rotation seed 3: positions, velocities and masses of `make_ic.py ball --axes
--vgrad [--rotate 3]` equal those of Track A's `make_deformed_ball.py` exactly (largest
difference 0, prediction 1e-13: held); r_vol = 1.0004144105705273 in both JSON files, the
same r_mom to the last digit (rotated: 2e-16). The two files differ in 16776 bytes, all of
them the sign bit of a zero velocity component (the track writes -0.0 where core writes
+0.0; byte 47 of the first record, and so on). Centre of mass 5e-17, net momentum 4e-18.
The JSON key `semi_axes` of core holds S times `--radius`; the track's
`semi_axes_start` holds S times r_vol (2.34375 against 2.34472).

### T8 outcome (self-force of one particle) [VERIFIED]

Runs: cases core-20261119-152207-d4e656c (75 one-step cases, 18 s), analysis
core-20261119-152742-a6810bd (`t8_selfforce.json`, figure `t8_selfforce.png`, looked at).
Force in G m/dx^2, slopes in G m/dx^3, counted away from the vertex:

| case | at vertex | at centre | slope at vertex (diag., edge) | slope at centre (diag., x) | largest radial on diagonal | largest on edge | largest component | e-folding at vertex (dx^3/Gm)^1/2 |
|---|---|---|---|---|---|---|---|---|
| isolated, CIC + Catmull-Rom | 1e-16 | 2e-7 | 1.80, 1.79 | -7.6, -8.0 | 0.97 | 0.34 | 0.83 | 0.75 |
| isolated, PCS + spline | 2e-16 | 2e-7 | 0.50, 0.50 | -0.81, -0.81 | 0.165 | 0.087 | 0.10 | 1.42 |
| periodic Fourier (spectral), CIC | 2e-16 | 0 | 1.19, 1.18 | -4.8, -5.0 | 0.62 | 0.22 | 0.52 | 0.92 |

- The force vanishes at the vertex and at the cell centre, points away from the vertex
  (unstable) and towards the cell centre (stable) in all three: not refuted.
- Slope at the vertex between 1.2 and 2.5 for the configuration the track used
  (isolated, CIC, Catmull-Rom): 1.80, held; its e-folding 0.75 against the track's 0.8.
  The periodic spectral case, which the prediction did not name, is at 1.19.
- Largest value along x between 0.2 and 0.6: on the edge (s, 0, 0) 0.34, held; the largest
  component anywhere, on the line from a face centre to the cell centre, is 0.83, above
  the 0.36 to 0.58 of the note's section 5.2 (those were components of the track's clumps,
  which are not single particles).
- The cubic cloud with the spline gather is smaller by 5.9 on the diagonal (prediction:
  at least three). Held.
- The isolated "at centre" value of 2e-7 is the asymmetry of the multipole boundary about
  a cell centre that is not the middle of the domain.

### Predictions for the card job, written before it ran (Slurm 4648, run core-20261119-145346-2f89b86; expected start 16:00Z)

Cases of `card.list` (decks of run core-20261119-145326-d509829). On a card the deposit
sums in an order that changes from run to run (`newtonian_mode.md` 5.8), so the card
reproduces the processor runs only to rounding, amplified after shell crossing; the
Fourier kernels themselves have no atomics.
- chk_mg, chk_fft7, chk_fftsp against the processor cases mg, fft7, fftsp of T1 (run
  core-20261119-144414-c629377; plane wave N = 32 to t = 3, shell crossing at t = 2):
  positions within 1e-9 of the box at every snapshot, K and W of every record within
  1e-8 relative. Refuted (a fault of the card path: an index map, a race in a line
  transform, a missing fence) if any is above 1e-6. On the card chk_fft7 equals chk_mg to
  the same 1e-9.
- east64 (Track B's pancake, n = 64, spectral): T2's prediction for n = 64 stands, the
  error against Zel'dovich at a = 2 and 5 is 4.8e-5 and 3.3e-4 within 30 per cent
  (`pm.py`); refuted if the a = 2 value is above 1.5e-4 (the seven-point run had 3.51e-4).
- chk_sin32 (group history, spectral, to t = 5) against the processor case sin32_sp of
  T3 where both exist (t <= 3.5): columns 5-30 and 38-55 of both group files within 1e-9
  relative to the largest value of each column, the difference quotients (31-36, 56-61)
  within 1e-6. Refuted above 1e-6 and 1e-3.
- Throughput (T9): a measurement. Seconds per step from the logs (mean of steps 2 to 20);
  expectation of T9 stands (multigrid 256^3 1 to 5 s per step, Fourier solve below 0.5 s
  at 256^3).

### T7 outcome (which energy; drift against the step) [VERIFIED]

Runs: cases core-20261119-153710-13876fa (plane wave N = 32 at dt = 0.0025, multigrid
and spectral; 677 s on one core), with the dt = 0.005 runs mg and fftsp of T1
(core-20261119-144414-c629377); analysis core-20261119-160023-99dc253 (`t7_energy.json`,
figure `t7_energy.png`, looked at: the dashed curves of half the step lie on the solid
ones). Largest |C - C_0| of the Layzer-Irvine combination (column 8) in units of max a|W|:

| solver | step | before the crossing (a < 4) | whole run (to a = 6.25) | same with W_mesh, whole run |
|---|---|---|---|---|
| multigrid | 0.005 | 6.248e-4 | 4.901e-3 | 1.256e-2 |
| multigrid | 0.0025 | 6.244e-4 | 4.914e-3 | 1.256e-2 |
| spectral | 0.005 | 5.515e-4 | 5.334e-3 | 1.161e-2 |
| spectral | 0.0025 | 5.514e-4 | 5.332e-3 | 1.161e-2 |

- Halving the step changes the drift after the crossing by 0.27 per cent (multigrid) and
  0.03 per cent (spectral); prediction: less than 20 per cent. Held. Refutation (a drop by
  two or more) did not occur: the drift is not an error of the time integration.
- Before the crossing the drift does not change with the step either (ratios 1.0006 and
  1.0002): it is a property of the space discretisation over the whole run, as written
  ("follows the resolution"; the resolution itself was not varied in this test, the
  first pass measured 4.9e-3 at N = 32 and 1.5e-3 at N = 64, `newtonian_mode.md` 5.6).
- The mesh form of W (column 7) drifts more than the particle form (column 6), by a
  factor 2.2 to 10.4; the spectral solver does not remove the drift (it lowers it by 12
  per cent before the crossing and raises it by 9 per cent over the run).
- Answer to Track A: column 6 (W gathered at the particles with the interpolation of the
  force) is the better diagnostic of the two; neither is an invariant of the scheme
  because the cloud (deposit) and the Catmull-Rom gather differ; the jump at the crossing
  of a sheet thinner than a cell is a space-discretisation effect and does not go away
  with a smaller step. The track's own numbers (1.1e-3 to 9.3e-3 of |W_0| at the first
  crossing) are of the size measured here (4.9e-3 at N = 32).
