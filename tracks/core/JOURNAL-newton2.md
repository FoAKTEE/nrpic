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
