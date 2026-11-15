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

## 2026-11-15 16:48 UTC: first outcomes at n = 32 (debug pass of the analysis scripts)

Runs: B-20261115-163556-ad5637f (P1, east32), B-20261115-163558-20244f2 (P2, sin32),
B-20261115-163613-790095f (N1, N = 32), B-20261115-163620-5b286c1 (N3, N = 32). The
numbers below come from the analysis scripts run on these outputs in
`scratch/B-emd-gw/tmp/` while the scripts were being debugged; the cited numbers will be
those of the registered analysis run (same scripts), entered further down.

P1 at n = 32: **P1a failed, P1b failed.** AthenaK's largest sheet error against the
continuum, in units of the displacement: 1.39e-3, 2.99e-3, 4.42e-3, 5.76e-3 at a = 2, 5,
10, 15, against pm.py's 1.1e-4, 6.1e-4, 2.1e-3, 1.7e-3 (5 to 13 times larger, not within
two); AthenaK - pm.py 1.4e-3 to 5.7e-3 (bound 1e-3). P1c passed: first crossing at
a = 21.34 against pm.py's 21.55 (1.0 %; the discrete Zel'dovich sheets cross at 21.11).
P1d passed: plane spread at most 1.3e-15 L before the crossing.

Hypothesis H1 (formed after seeing P1; not yet tested): the excess is the seven-point
Laplacian of the multigrid solver, which pm.py (spectral) does not have. For the
fundamental mode along x its eigenvalue is -k^2 [sin(kh/2)/(kh/2)]^2, so the potential
and, with a gradient accurate to O(h^4) (cubic spline through the nodes; compensated cubic
cloud), the force are too strong by the factor F = [(kh/2)/sin(kh/2)]^2 = 1 + 3.219e-3 at
n = 32 (8.04e-4 at n = 64). Linear theory with that force: s = A a^n1 + B a^n2,
n1,2 = [-1/2 +- sqrt(1/4 + 6F)]/2, A, B from s = s0, ds/da = s0 at a = 1 (the growing
mode of F = 1). Predicted error of the sheet with the largest displacement, in the units
of P1: n = 32: 1.41e-3, 2.94e-3, 4.09e-3, 4.79e-3, 5.29e-3 at a = 2, 5, 10, 15, 20;
n = 64: 3.51e-4, 7.33e-4, 1.02e-3, 1.19e-3, 1.32e-3. The measured n = 32 values above
agree to 1 % at a = 2 and 5 and fall short by 8 % and 17 % at 10 and 15, where nonlinear
terms and the lattice error enter; this agreement was noticed after the run, so it is
not yet a test.

Tests of H1 that can fail:
- H1a (n = 32 data, computed after this entry): the error is proportional to the
  displacement sheet by sheet: (x_AK - x_exact)/(x_exact - x0) has the same value
  (A a^n1 + B a^n2 - a)/(a - 1) for every sheet with |cos k q| > 0.3, within 10 % at
  a = 2 and 5. A lattice-sampling error would vary from sheet to sheet.
- H1b (card run B-20261115-163653-f6324ea, still queued when this is written): at n = 64
  the error against the continuum is 3.5e-4 and 7.3e-4 at a = 2 and 5 within 15 %
  (falls by 4.0, second order), while pm.py's fell by 2.3 and 1.9.
- H1c (P2, sin data): the same linear theory with F, carried through
  I_xx = c0 + c1 D + c2 D^2, D = A a^n1 + B a^n2, reproduces the measured d3I_xx error
  (1.5-5 % high at n = 32 for 2 <= a <= 15) to within a third of its size at a <= 10,
  and at n = 64 the d3I error falls by about four.

P2 at n = 32: P2a partly failed: I_xx - c0 within 2.05e-3 of its largest value
(bound 2e-3: marginal fail), dI_xx 2.6e-3 (fail), d2I_xx 1.6e-2 (fail; d2I_xx contains
the acceleration and changes sign at a = 13.3, so the errors were normalised by the
largest exact value for a <= 15 instead of pointwise, a change of the metric made after
seeing the data). P2b passed at n = 32: d3I_xx rms relative error 2.4 % for
1.2 <= a <= 15, systematically high (1.6 % at 5-10, 3.2 % at 10-15, 4.7 % at 15-19).
P2c passed: dI and d2I of yy, zz, xy, xz, yz below 4.1e-13 of max d2I_xx. P2d passed:
Layzer-Irvine constant to 7.9e-7 of max a|W|.

N1 at N = 32: t_x = 24.066, 0.90 % after the nominal ODE (0.63 % after the
equivalent-ellipsoid ODE): within N1a. E_avg = 3.21e-4 M c^2 (E/M), 34 % below the ODE
(raw 33 %); up to one t_k before the crossing 8-10 % below. Q within 0.35 % of max|Q|,
Q'' within 3.4 %, Q''' averaged within 38 % in the window t <= t_x - 1 (the particle
Q''' turns over at t ~ 22.3, where R_x ~ 1 cell; figure in the debug directory).

N3 at N = 32: E/(M c^2 (2 alpha)^3.5) = 0.061787 for alpha = 0.05, 0.1, 0.11122237, 0.2
with a spread of 5.8e-15, t_x/t_turn 2.524849 with a spread of 2.6e-15: N3a passed.

## 2026-11-15 16:53 UTC: H1a checked (failed as stated); new test H1d at n = 16 before its run

H1a outcome (n = 32 data, computed after the entry above): **failed as stated.** The
per-sheet ratio of the measured error to the H1 error, over the sheets with
|cos k x0| > 0.3, spans 0.91-1.13 at a = 2 and 0.76-1.38 at a = 5 (bound: within 10 %).
The sheet with the largest displacement agrees to 1 %; the spread comes from sheets
with smaller displacement, where the lattice error that pm.py also has (1.1e-4 of the
largest displacement at a = 2, `verify_cosmo/results/pancake.json` N_n32) is not small
against the H1 error of that sheet [JUDGEMENT: an explanation, not tested]. A post-hoc
version that removes the shared lattice error, (x_AthenaK - x_pm)/(H1 error) sheet by
sheet, spans 0.94-1.07 at a = 2 and 0.86-1.20 at a = 5; it was formulated after seeing
the data and is not counted as a test.

H1c outcome (n = 32): **partly failed.** Mean signed relative error of d3I_xx, measured
against H1: 1.25 % against 0.69 % (2 <= a <= 5), 1.57 % against 1.11 % (5-10), 3.03 %
against 1.45 % (10-15). H1 accounts for a half to two thirds of the jerk error, not for
all of it within a third at a <= 10 (fails at 2-5, passes at 5-10).

H1d (new; written before the runs): at n = 16 the H1 force error is four times that of
n = 32 (F - 1 = 1.295e-2), so the error grows by four while the lattice error (first
order, verify_cosmo P8) only doubles. Runs east16 and sin16 (same data, same numerics,
step L/(4n), one core each, a few minutes). Predictions from the formula of H1:
- H1d-1. East data: largest sheet error against the continuum 5.66e-3, 1.19e-2,
  1.65e-2 at a = 2, 5, 10, within 10 % at a = 2 and 5 and within 25 % at a = 10.
- H1d-2. ex(n = 16)/ex(n = 32) at a = 2 is 4.0 within 10 % (n = 32: 1.39e-3).
- H1d-3. Sin data: mean signed relative error of d3I_xx 2.8 % (2-5) and 4.6 % (5-10)
  from H1, measured within a factor 1.5 (the n = 32 run had a remainder of about 0.5
  percentage points not explained by H1; at n = 16 it should be at most twice that).
Refuted if the ratio of H1d-2 is below 3 (then the error is not second order in kh,
and the seven-point Laplacian is not its main source).

## 2026-11-15 17:00 UTC: H1d outcome (runs B-20261115-165349-81a17bc, -165351-b38db6f)

- H1d-1 **passed**: n = 16 largest sheet error against the continuum 5.64e-3, 1.163e-2,
  1.84e-2 at a = 2, 5, 10 against the H1 values at the same records 5.74e-3, 1.184e-2,
  1.65e-2 (-1.6 %, -1.8 %, +12 %).
- H1d-2 **passed**: ex(16)/ex(32) at a = 2 is 5.643e-3/1.390e-3 = 4.06.
- H1d-3 **partly failed**: d3I_xx mean signed relative error 5.24 % against 2.75 % from
  H1 at 2 <= a <= 5 (factor 1.9, bound 1.5), 6.14 % against 4.51 % at 5-10 (passes).
  The measured jerk error itself scales by 4.2, 3.9, 4.1 from n = 16 to 32 in the three
  bands (5.24/1.25, 6.14/1.57, 12.3/3.03 %): second order in the cell size; H1 carries
  half to three quarters of it; the remainder is also of second order and not explained
  here.

Conclusion on H1 (a cause named after runs that could have refuted it): the position
error of the Newtonian mode in the pancake before shell crossing is set by the
seven-point Laplacian of the multigrid solve, (kh)^2/12 in the force of the
fundamental mode, which pm.py's spectral solve does not have; it is of second order in
the cell size and at n = 32 it exceeds the lattice-sampling error that dominates pm.py
[VERIFIED: runs above and B-20261115-163556-ad5637f]. The failed predictions P1a and P1b
were therefore wrong because they assumed the lattice error dominates both codes;
core's interface note 5.6 found the two codes comparable with the cloud-in-cell options,
where the cloud error is larger. The n = 64 card run (H1b) remains the test of the
second-order fall at the resolution of the verify_cosmo comparison.

## 2026-11-15 17:05 UTC: registered pancake analysis B-20261115-170156-2d69627

(The first attempt, B-20261115-170149-75036cf, failed: relative paths to `scratch/` do
not resolve from the worktree root; kept on record.) All P1, P2 and H1 numbers of the
entries above are reproduced by this run (`results/pancake.json`, figures
`figs/pancake_east.png`, `figs/pancake_sin_moments.png`, both looked at). Additional
numbers from it:
- P1 at n = 16: crossing of neighbouring sheets at a = 21.87 (n = 32: 21.34; pm.py
  n = 32: 21.55; discrete Zel'dovich sheets 21.44 and 21.11): the crossing approaches
  the exact one from late, as a force that is too strong would not do on its own
  [JUDGEMENT: near the caustic the force is smoothed over the cloud, which delays it].
- Plane symmetry at n = 16 and 32: largest spread of x within a lattice plane 8.9e-16
  and 1.3e-15 L before the crossing (P1d).
- The record times of AthenaK and pm.py agree exactly except the last record (end time
  not on the step grid).
- P2 at n = 16: I_xx - c0 within 8.1e-3, dI_xx 1.05e-2, d2I_xx 6.4e-2 of their largest
  values; d3I_xx rms 9.3 % (n = 32: 2.0e-3, 2.6e-3, 1.6e-2, 2.4 %): all four fall by
  about four from n = 16 to 32, second order. The early transient of the d3I error
  (a < 2, up to 50 % at n = 16) is reproduced by the H1 linear solution (the decaying
  mode that the stronger force excites from growing-mode data; dashed curves of the
  bottom panel).

## 2026-11-15 17:40 UTC: card run B-20261115-163653-f6324ea (P1, P2 at n = 64): H1b

The card job (Slurm 4459) started at 17:22 and ran both pancakes in 321 s (0.089
card-hours of the 0.4 reserved). Numbers from the debug pass of the analysis on these
outputs (the registered analysis below repeats them):
- H1b **passed**: largest sheet error against the continuum 3.507e-4 and 7.42e-4 at
  a = 2 and 5 against the predicted 3.508e-4 and 7.33e-4 (0.0 % and +1.2 %); the fall
  from n = 32 is 3.96 at a = 2.
- P1 at n = 64: 3.5e-4, 7.4e-4, 1.20e-3, 1.41e-3 at a = 2, 5, 10, 15 against pm.py's
  4.8e-5, 3.3e-4, 1.02e-3, 8.3e-4. P1a (within two of pm.py) fails at a = 2 and 5
  (7.3, 2.3) and passes at 10 and 15 (1.2, 1.7). P1b passes at n = 64: AthenaK - pm.py
  falls from n = 32 by 4.0, 4.0, 4.0, 4.1 at a = 2, 5, 10, 15 (bound: at least two),
  but its size (3.5e-4 to 1.4e-3) is above the 1e-3 stated for n = 32 only at a = 15.
  P1c passes: crossing at a = 21.16 against pm.py's 21.22 (-0.3 %). P1d: plane spread
  6.7e-16 L.
- P2 at n = 64: I_xx - c0, dI_xx, d2I_xx within 5.1e-4, 6.6e-4, 3.9e-3 of their largest
  values (each a fall of 4.0 from n = 32); d3I_xx rms 0.61 % for 1.2 <= a <= 15 (n = 32:
  2.35 %), P2b passes; off-diagonal and transverse derivatives below 6.0e-14 of
  max d2I_xx; Layzer-Irvine 2.1e-7.
- H1c at n = 64: mean signed d3I error 0.31 %, 0.40 %, 0.71 % (bands 2-5, 5-10, 10-15)
  against 0.17 %, 0.28 %, 0.36 % from H1; both fall by four from n = 32. H1 carries half
  to three quarters of the jerk error at every resolution; the rest is also second order.

## 2026-11-15 17:50 UTC: registered analyses B-20261115-173904-a7297e3 (pancakes) and B-20261115-174251-3698196 (ellipsoid)

B-20261115-173904-a7297e3 supersedes B-20261115-170156-2d69627 (adds n = 64, moves a
legend); every pancake number above is reproduced by it. The ellipsoid analysis drops one
record per run: the driver ends on tlim with a remainder step of 2.4e-13, and the d3I
difference quotient of that record is rounding over the step (d3I_xy = -1.2e-4 at
N = 128 while d2I_xy is 1e-15); seen in the debug pass, fixed before the registered run.

N1 outcomes (model C ODE: x crossing 23.8524 t_k, E(t_turn -> t_x) = 4.9135e-4 M c^2):

| N | t_x / t_k | t_x error | E raw / M c^2 | raw vs ODE | averaged vs ODE | averaged vs averaged ODE |
|---|---|---|---|---|---|---|
| 32 | 24.0659 | +0.90 % | 3.222e-4 | -34.4 % | -34.7 % | -29.8 % |
| 64 | 23.8955 | +0.18 % | 4.008e-4 | -18.4 % | -19.3 % | -13.2 % |
| 128 | 23.8604 | +0.034 % | 4.437e-4 | -9.7 % | -11.7 % | -5.0 % |
| Richardson | 23.8513 (order 2.3) | -0.005 % | 4.950e-4 (order 0.88) | +0.7 % | | |

- N1a **passed**: t_x later than the ODE by 0.90, 0.18, 0.034 % (bounds 2, 1, 0.5 %),
  monotone, observed order 2.3.
- N1b **passed**: at N = 64, Q_ii within 8.3e-4 of max|Q| and Q''_ii within 6.9e-3 of
  max|Q''| of the equivalent-ellipsoid ODE for t <= t_x - 1 (N = 128: 1.8e-4, 1.6e-3).
- N1c **passed**: Q''' averaged over 0.05 t_turn within 3.1 % of max|Q'''| of the ODE
  averaged the same way (N = 64; N = 128: 2.3 %); raw difference quotient rms 1.1 %
  (N = 64) and 0.9 % (N = 128).
- N1d **failed as stated** (the bound at N = 128): the averaged energy against the exact
  ODE is 11.7 % low at N = 128 (bound 10 %); its fall per doubling is 1.80 and 1.65
  (bound 1.5: passes). Measured afterwards: the averaging window alone lowers the ODE
  energy by 7.0 % (4.569e-4 against 4.914e-4 M c^2), because Q''' changes fastest at the
  crossing; the fair comparisons are raw against the exact ODE (-9.7 % at N = 128) and
  averaged against the averaged ODE (-5.0 %). The raw energy is above the averaged one
  at every N, as predicted. First-order convergence (observed 0.88 to 1.0): the energy
  missing near the crossing comes from the time during which R_x is a few cells
  [JUDGEMENT]; the Richardson value of the raw energy is 4.95e-4 M c^2, +0.7 % from the
  ODE. Up to one t_k before the ODE crossing (where R_x > 0.48), the averaged energy is
  within 10.2, 1.5, 0.27 % of the averaged ODE (second order and better).
- N1e **failed as stated**: K + W changes by 5.3e-3, 3.3e-3, 1.9e-3 of |W| up to t_x
  (bound 1e-3); up to t_x - 1 by 8.7e-4, 2.3e-4, 5.3e-5. Momentum and centre of mass
  stay at 1e-15 (the configuration is reflection-symmetric); the off-diagonal Q, Q', Q''
  stay below 2e-15 of the diagonal and Q''' below 5e-13.
- N1f **passed**: step 0.01 against 0.02 at N = 64: t_x within 2.1e-7, raw E within
  8.3e-5, averaged E within 6.8e-4.
- The particle runs reproduce what BASELINE.md T4 found semi-analytically: the energy to
  the first crossing is 6 to 9 times the Zel'dovich estimate on [t_turn, t_col]
  (5.15e-5 M c^2), approaching the ODE's factor 9.5 with resolution.

N3 outcomes: E/(M c^2 (2 alpha)^3.5) for alpha = 0.05, 0.1, 0.11122237, 0.2:
N = 32: 0.0617869 (averaged), 0.0620591 (raw), spread 5.8e-15 and 7.3e-15;
N = 64: 0.0763748, 0.0772053, spread 1.9e-14 and 3.1e-14; t_x/t_turn 2.524849 and
2.506970, spread 2.7e-15. N3a **passed** (bound 1e-8). N3b **passed**: the values equal
those of N1 at the same N; with N = 128 (raw 0.0855) and the Richardson value (0.0954)
they approach F_C = 0.09465. The (2 alpha)^(7/2) law of 2403.15126 holds in the code for
the single patch to rounding, as an exact symmetry of the discrete problem.

Not done: N2 (embedded ellipsoid; needs the species history, entry of 16:30); the
ellipsoid with the background term (models A, B) in any form; any run on a refined mesh.

## 2026-11-15 17:55 UTC: close of the package

B-20261115-174405-af11300 repeats the ellipsoid analysis with one legend moved; its JSON
equals that of B-20261115-174251-3698196 in every number (checked by comparing the two
files without the path fields). README.md cites it and B-20261115-173904-a7297e3.
Failed predictions on record: P1a, P1b (n = 32; P1a also at n = 64 for a <= 5), P2a
(dI and d2I at n = 32; I marginal), H1a as stated, H1c and H1d-3 in part, N1d (the bound
at N = 128 for the averaged energy), N1e (up to t_x). Passed: P1c, P1d, P2b-P2d, H1b,
H1d-1, H1d-2, N1a-c, N1f, N3a, N3b. Not run: N2.
