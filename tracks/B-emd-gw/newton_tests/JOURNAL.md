# JOURNAL of newton_tests (helper package of B-emd-gw, wave 2)

Predictions are written before the runs they concern; outcomes are appended below each
block afterwards, including the failed ones. Labels: [VERIFIED], [BACKGROUND],
[JUDGEMENT], [TO VERIFY]. Units G = c = 1.

## 2026-11-15 16:30 UTC: what is being tested, with what

Code: release core-v0.3, processor executable `/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena`
(serial Kokkos, `Kokkos_ENABLE_SERIAL=ON`, `CMakeCache.txt`), card executable
`.work/build_gpu_v03/src/athena`; Newtonian mode `<particles> pusher = newton`
(`coord/INTERFACES/newtonian_mode.md`). References: the exact plane-symmetric solution
`tracks/B-emd-gw/verify_cosmo/scripts/zeldovich.py` (continuum and discrete sheets), the
Newtonian particle-mesh code `cosmo/newton/pm.py` results of run
B-emd-gw-20261115-115239-69ab1db (same particles), and the homogeneous-ellipsoid ODE of
`tracks/B-emd-gw/baseline/scripts/ellipsoid.py` (model C; acceptance numbers of
`baseline/BASELINE.md` section 4.2 from run B-emd-gw-20261115-115752-840e994: first x
crossing 23.852 t_k, E(t_turn -> t_x) = 4.91e-4 M c^2, self-similar constant
F_C = 0.0946).

Names used here. The task statement calls the tests "N1 to N3 of BASELINE.md" and
describes them as the pancake, the ellipsoid with quadrupole diagnostics, and the
scaling. BASELINE.md 4.2 numbers its tests N1 (static isolated ellipsoid, model C), N2
(embedded ellipsoid, model A, periodic box) and N3 (self-similarity). This package
runs: P1 and P2 (pancake), N1, N3; N2 needs a history of one species that the mode
lacks (see the end of this entry).

Smoke tests before writing this entry (not registered, no number cited from them):
6 to 40 cycles of the two inputs in `scratch/B-emd-gw/tmp/mp/` to check that the inputs
parse and to time a cycle on one core of the loaded machine: pancake 32^3 0.45-0.53 s
per cycle, 64^3 4.5 s; ellipsoid 32^3 0.12 s, 64^3 0.79 s; set-up 1-9 s. Consequence
[JUDGEMENT]: the 64^3 pancakes (2048-2806 cycles, 2.5-3.5 h on a processor) go to a
card; everything else runs on processors (ellipsoid 128^3 about 1.4 h).

### P1 Plane-wave pancake against Zel'dovich and pm.py (east data, n = 32 processor, n = 64 card)

Data and numerics as `verify_cosmo/scripts/newton_pancake.py` (delta = 0.05, L = 1,
one particle per cell, cubic cloud, compensation c = 1/6, c2 = 7/15, cubic-spline force,
step L/(4n), to a = 42; first crossing of the continuum at a = 21). Trajectories of the
n sheets of one x line every two steps (pm.py records every two steps too).

Predictions:
- P1a. The largest sheet error against the continuum, in units of the displacement
  (a - 1) d/k (the metric of verify_cosmo), is within a factor two of pm.py's at a = 5,
  10, 15: pm.py n32 6.1e-4, 2.1e-3, 1.7e-3; n64 3.3e-4, 1.0e-3, 8.3e-4
  (`verify_cosmo/results/pancake.json`, `N_n32`, `N_n64`), because the lattice
  sampling error dominates both (core's note 5.6 and verify_cosmo P1, P8).
- P1b. AthenaK against pm.py, the same metric: smaller than either against the
  continuum, at most 1e-3 at n = 32 for a <= 15, and smaller by at least a factor two at
  n = 64 (both are second-order schemes; they differ in the Laplacian and the gradient).
- P1c. First crossing of neighbouring sheets: within 1 % of pm.py's a = 21.55 (n32) and
  within 0.5 % of 21.22 (n64).
- P1d. Plane symmetry: the spread of x over a lattice plane stays at rounding level,
  below 1e-12 L, before the crossing.
Refuted if: AthenaK's error against the continuum exceeds twice pm.py's at any of the
three times, or the AthenaK - pm.py difference does not fall from n = 32 to 64.

### P2 Pancake with the second-moment columns (sin data, n = 32 processor, n = 64 card)

Equal-mass Zel'dovich lattice q = (i + 1/2) h, psi = (d/k) sin(k q_x), d = 0.05, so the
sheets move towards L/2 and never wrap before crossing (a = 20); the second moment about
the origin is then defined. Exact (discrete sheets, before crossing; derivation: the force
on a sheet is (3/2)(x - Q) with Q its mass coordinate, here Q = q_i, so x = q + a psi with
a = (1 + t/2)^2): I_xx = c0 + c1 a + c2 a^2 with lattice sums c0 = sum m q^2,
c1 = 2 sum m q psi, c2 = sum m psi^2; dI_xx = (c1 + 2 c2 a) a', d2I_xx = c1/2 + 3 c2 a
(a' = sqrt(a), a'' = 1/2), d3I_xx = 3 c2 sqrt(a); the other components constant, their
derivatives zero.

Predictions:
- P2a. I_xx - c0, dI_xx, d2I_xx within 2e-3 (relative to the exact value) for
  1.2 <= a <= 15 at n = 32.
- P2b. d3I_xx (the one-step difference quotient of the history, at its mid-step time):
  rms relative error at most 3 % over 1.2 <= a <= 15 at n = 32, smaller at n = 64. The
  jerk is the time derivative of the mesh force; it fluctuates as the lattice sheets move
  across cells (core's note 5.4: 8.6 % rms in the cold collapse with CIC and one particle
  per cell); the cubic cloud and spline should do better.
- P2c. d2I_yy, d2I_zz, dI_xy: zero to rounding (below 1e-12 of d2I_xx).
- P2d. Layzer-Irvine constant C: changes by at most 1e-3 of max a|W| before crossing.
Refuted if: any of P2a-P2c fails at n = 32, or the d3I error does not fall at n = 64.

### N1 Static isolated ellipsoid against the ODE (model C), N = 32, 64, 128

Zel'dovich ellipsoid of the 2605.04487 benchmark (lambda = 0.11122237, 0.06683367,
0.02194397) at t_turn = 9.5316: semi-axes 3.372, 4.717, 6.078, velocities 0, 0.188, 0.379
(ellipsoid.initial_state); M = 0.75, equal-mass particles on a cubic lattice of spacing
dx/2 inside the ellipsoid, linear velocity field; box [-12, 12]^3 (largest semi-axis
before the x crossing 8.71 from the ODE), multipole boundary of order 4, cloud-in-cell,
Catmull-Rom; step 0.02, to t_turn + 15.5. Lattice sampling: the second moments of the
lattice differ from the continuum M R_i^2/5 by up to 0.75 %, 0.23 %, 0.04 % at N = 32,
64, 128 (generator output, smoke test). The analysis therefore also integrates the ODE
from the equivalent ellipsoid of the lattice (same mass and second moments; velocities
scaled with the axes), which separates the dynamics error from the sampling error.
Crossing time t_x: zero of dI_xx (the minimum of I_xx).

Predictions:
- N1a. t_x later than the ODE (the mesh softens the force where the x axis is thin and
  the cloud smears the edge): by at most 2 % at N = 32, 1 % at 64, 0.5 % at 128,
  approaching 23.852 monotonically.
- N1b. Trace-free Q_ii(t) within 1 % of max|Q| of the equivalent-ellipsoid ODE for
  t <= t_x - 1 at N = 64; Q''_ii within 2 % of max|Q''|.
- N1c. Q'''_ii: the raw difference quotient carries mesh noise; averaged over 0.5 t_k it
  is within 5 % of max|Q'''| of the ODE (averaged the same way) for t <= t_x - 1 at
  N = 64.
- N1d. E(t_turn -> t_x) = int (1/5) Q''':Q''' dt from the averaged Q''': converges to
  the ODE value 4.91e-4 M c^2 with the error falling by at least 1.5 per doubling; at
  N = 128 within 10 %. Most of the ODE energy comes from the last time unit before the
  crossing (66 % from t > t_x - 1, where R_x < 0.48; smoke-test call of
  `ellipsoid.sample`), where R_x is a few cells: the particle value is expected below
  the ODE value. With the raw Q''' the energy is larger (noise power added).
- N1e. K + W constant to 1e-3 of |W| before the crossing; total momentum below 1e-4
  M sqrt(GM/R).
- N1f. Step check, N = 64 with step 0.01: t_x and E within 0.1 % of the step-0.02 run.
Refuted if: the t_x error grows with N or exceeds the bounds of N1a; E at N = 128 is off
by more than 20 % or does not approach the ODE value.

### N3 Self-similarity (alpha = 0.05, 0.1, 0.2 and the benchmark), N = 32 and 64

Each run is an exact rescaling of the benchmark run at the same N: lengths (box,
lattice, axes) times alpha_b/alpha, times (step, end, snapshot interval) times
(alpha_b/alpha)^(3/2), mass fixed; then G M T^2/L^3 is the same and the discrete
problems are the same up to rounding, provided nothing in the mode or the solver has a
scale of its own (the stopping rule of the multigrid solve with threshold = 0 is
relative; the multipole boundary is scale-free).

Predictions:
- N3a. E(t_turn -> t_x)/(M c^2 (2 alpha)^(7/2)) and t_x/t_turn agree across the four
  runs of one N to 1e-8 relative.
- N3b. The value at each N equals that of N1 at that N, so its distance from
  F_C = 0.0946 is the discretisation error measured by N1, and the (2 alpha)^(7/2) law
  of 2403.15126 (Omega ~ sigma^(7/2), its line 1031) holds in the code for the single
  patch exactly (BASELINE.md section 2).
Refuted if: the spread exceeds 1e-6 (a hidden scale in the mode or in the solver).

### N2 (embedded ellipsoid, model A): not run, and why

The history of the mode sums over all particles about the coordinate origin, with
positions wrapped on a periodic mesh (`newtonian_mode.md` section 3, "Diagnostics", and
section 6, "Second moment"). A patch inside background particles in a periodic box
therefore cannot be separated from its background in the history: what N2 needs is the
species selection and the second moments about the centroid of that species in physical
coordinates (request 2 of `outbox/20261115T1340Z__to-core__newtonian-mode-for-track-b.md`).
Without it only the particle snapshots are available (positions and momenta, no
acceleration), which give Q and Q' of the patch but Q'' and Q''' only by differencing
snapshots. Not attempted in this package.
