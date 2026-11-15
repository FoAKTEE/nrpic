# Journal of the work package scalar (core, branch core/scalar-field)

Entries are appended. Labels: [VERIFIED] read at the locator or measured by a registered
run, [BACKGROUND] standard, not re-checked, [JUDGEMENT] design inference, [TO VERIFY] open.
Run ids: `tracks/core/runs/<run_id>/manifest.json`, outputs `scratch/core/<run_id>/`.

## 2026-11-15, entry 1: state found, design, predictions (written before any run)

### State found

- `core/scalar-field` merged `main` (a1c2237) and `core/rng` (a6e5c46); start commit b28ecca.
- `tracks/E-stoch-inf/spec/SPEC.md` exists on `track/E-stoch-inf` (176cdd6), with a design
  review `tracks/E-stoch-inf/codebase/DESIGN_REVIEW.md` (requests R1 to R8 to core) and a
  noise reference `tracks/E-stoch-inf/noise/ref/` (keys of the mode amplitudes). So the
  hook implements the source terms of the SPEC (sections 2.1, 2.2, 3, with the mapping of
  2.5 and the design review sections 5 and 6), and a generic model (power-law amplitude,
  window, frozen or white in time) for the unit test of the generator. The file
  `NOISE_SPEC.md` that `noise_ref.py` cites is not on the branch; the keys are taken from
  `philox_ref.py` (docstring): stream = Stream(3, 2^16 + dof), entity = (nx + 2^20) |
  (ny + 2^20) << 21 | (nz + 2^20) << 42, step = epoch, draw 0, alpha = (z1 + i z2)/sqrt 2.
- Baseline executable for the regression: source snapshot of b28ecca
  (`scratch/core/base_src_b28ecca`), `.work/build_cpu_base/src/athena`.

### Where the module goes, and why [JUDGEMENT]

A new physics module `athenak/src/scalar_field/` (namespace `scalarfield`, class
`ScalarField`, pack pointer `pscalar`), built like `dyn_grmhd` and not like the particles:
its sources change with the field at every stage of the integrator, so its tasks go into
the numerical-relativity task queue (`tasklist/numerical_relativity.*`) next to those of
Z4c, with named dependencies. The alternative, two more entries in the Z4c state vector,
would give communication, restart and dissipation for free but changes `nz4c`, the restart
file layout and every existing run; the separate module leaves them bit-identical.

- State `u0(m, {phi, Pi}, k, j, i)` at cell centres, registers `u1`, `u_rhs`, coarse array,
  own `MeshBoundaryValuesCC` (Z4c flavour: the same restriction, prolongation and
  same-level exchange as the spacetime variables), so static refinement comes with the
  existing machinery. Adaptive refinement needs entries in `mesh_refinement.cpp` and is
  not done: fatal error with `<mesh_refinement> refinement = adaptive`.
- Metric at a stage from the Z4c state of that stage (chi, conformal metric, Khat, Theta,
  lapse, shift), never from `padm`, which is refreshed only at the last stage.
- Sources: `Tmunu` gets a third container `tmunu_tot` (all matter modules together). The
  scalar field assembles it before every right-hand side and before every evaluation of
  the constraints: own sources plus `u_tmunu` of the other modules (or their step densities
  times 1/sqrt(gamma) of the stage, plus the vacuum energy). The solver and the
  constraints read `tmunu_tot` when `use_total` is set, in three-line hooks.
- Restart: side file `<restart file>.sf` (as the particles' `.prt`), so the mesh restart
  file keeps its layout.
- Stochastic sources: Fourier coefficients per wave vector of a ball |n|^2 <= nmax2 (one
  hemisphere), amplitudes from `utils/rng.hpp`; fields synthesized MeshBlock by MeshBlock
  with three one-dimensional sums over tables of cos and sin built from global cell
  indices (no Fourier library in `athenak/src`; the turbulence driver sums modes directly
  too). Time-dependent mode data are integrated on the host with the same low-storage
  update as the fields ("in lockstep"), so each stage has its own values and no stage time
  is needed.

### Sign conventions and equations [BACKGROUND; signs checked against z4c_calcrhs.cpp]

Metric ds^2 = -alpha^2 dt^2 + gamma_ij (dx^i + beta^i dt)(dx^j + beta^j dt); n^mu =
(1, -beta^i)/alpha; K_ij = -(1/2 alpha)(d_t - L_beta) gamma_ij, K = -3H in an expanding
universe (`z4c_calcrhs.cpp:628-629, 665`). G = c = 1, G_munu = 8 pi T_munu.
T_munu = d_mu phi d_nu phi - g_munu [ (1/2) g^rs d_r phi d_s phi + V(phi) ].

    Pi   = n^mu d_mu phi = (d_t phi - beta^i d_i phi)/alpha
    d_t phi = beta^i d_i phi + alpha Pi
    d_t Pi  = beta^i d_i Pi + alpha (D^i D_i phi + K Pi - V') + gamma^ij d_i alpha d_j phi
    D^i D_i phi = psi^-4 [ gt^ij d_i d_j phi - Gt^k d_k phi + 2 gt^ij d_i ln psi d_j phi ]
    E    = Pi^2/2 + (1/2) gamma^ij d_i phi d_j phi + V
    S_i  = -Pi d_i phi
    S_ij = d_i phi d_j phi + gamma_ij (Pi^2/2 - (1/2) gamma^kl d_k phi d_l phi - V)

with gamma_ij = psi^4 gt_ij, psi^-4 = chi^(-4/chi_psi_power), d_i ln psi = d_i chi /
(chi_psi_power chi), K = Khat + 2 Theta, Gt^k = gt^ij Gamma^k_ij computed from the
conformal metric (not the evolved Gamma). Check: alpha = 1, homogeneous: ddot phi + 3 H
dot phi + V' = 0. A wave moving towards +x has S_x > 0.

### Initial data for the inhomogeneous test, built without an elliptic solve [JUDGEMENT]

Plane perturbation phi = phi0 + A sin(k.x), conformally flat with psi = 1, At_ij = 0,
K = K(phi(x)), Pi = K'(phi)/(12 pi). The momentum constraint -(2/3) d_i K = 8 pi S_i =
-8 pi Pi d_i phi holds identically. Because |grad phi|^2 = |k|^2 (A^2 - (phi - phi0)^2)
= G(phi) is a function of phi for a single plane wave, the Hamiltonian constraint
(2/3) K^2 = 16 pi (Pi^2/2 + G/2 + V) becomes the ordinary differential equation

    K'(phi)^2 = 12 pi K^2 - 144 pi^2 G(phi) - 288 pi^2 V(phi)

(the Hamilton-Jacobi equation of a homogeneous field plus the gradient term), integrated
from phi0 - A, where K = -sqrt(24 pi (Pi0^2/2 + V)), with the sign of K' that of Pi0.
Both constraints then hold exactly at every point for any amplitude for which the
right-hand side stays positive (gradient energy below kinetic energy).

### Predictions

P-reg (regression). The five cases of `tracks/core/analysis/rng/run_regression.py`
(analytic metric; mesh metric with deposit; refined mesh with deposit and excision; Z4c
with particle sources; restart files with removal): every output file byte-identical
between `.work/build_cpu_base` and the new executable. Refuted by any differing file in a
case whose baseline reproduces itself.

P1 (Klein-Gordon plane wave, flat spacetime, coupling off, periodic box of side 1,
quadratic potential m = 5, wave numbers n = (1, 1, 0), no dissipation).
(a) The semi-discrete solution is the plane wave with omega_h^2 = m^2 + sum_i kap2(k_i h)
/h^2, kap2 the symbol of the centred second difference (orders 2, 4, 6 for nghost 2, 3, 4);
omega_h^2 - omega^2 = -sum_i k_i^2 [(k_i h)^2/12, (k_i h)^4/90, (k_i h)^6/560] to leading
order. Measured: the frequency fitted to the mode amplitude over t = 2 differs from
omega_h by less than 3 omega (omega dt)^4/120 (classical RK4 phase error; the 2S scheme
has about twice the error norm) and from omega by the spatial term; fitted spatial orders
2, 4, 6 within 0.2 at small fixed dt (N = 8 to 32).
(b) At fixed N = 16, nghost = 4, the error against the semi-discrete solution falls as
dt^4 (order within 0.2) for Courant factors 0.4, 0.2, 0.1, 0.05.
Refuted by an order outside the band in the asymptotic range, or by a frequency that
matches neither omega_h nor omega.
(c) Kreiss-Oliger dissipation 0.5 with nghost = 4 (operator h^7 D^8/256 per direction):
amplitude decay rate sigma = 0.5/(256 h) sum_i (2 sin(k_i h/2))^8, i.e. for N = 16 a loss
of 2 sigma t; prediction within 5 percent of the measured decay of the amplitude.
(d) Potentials (quadratic, quartic, plateau, Higgs inflection, table): homogeneous field
on flat spacetime against the ordinary differential equation ddot phi = -V'(phi) (SciPy,
rtol 1e-12): differences below 1e-7 relative at Courant factor 0.25 over ten time units;
table (2001 points, cubic Hermite) within 1e-9 of the analytic form it tabulates.

P2 (homogeneous slow roll with the evolved metric). Quadratic potential m = 0.1, phi0 = 3,
Pi0 on the slow-roll attractor (-m^2 phi/(3H)), K0 from the Hamiltonian constraint, box 1,
16^3 cells, RK4, Courant 0.25, nghost 4, no damping. Two gauges: conformal time
(`lapse_harmonic = 1/3`, `lapse_oplog = 0`, the cosmological lapse of cosmo/README.md) to
t = 1.2 (a about 3.8), and geodesic slicing to t = 8 (about 5 e-folds).
Expected: a = chi^(-1/2), phi, Pi, K, alpha follow the Friedmann and Klein-Gordon ordinary
differential equations in the same gauge (SciPy DOP853, rtol 1e-13) with relative
differences below 1e-5 at Courant 0.25 and falling as dt^4 (factor 16 +- 4 per halving,
until rounding); eps1 = 4 pi Pi^2/H^2 stays within 20 percent of 1/(4 pi phi^2).
Constraints: momentum constraint and all gradients at rounding (below 1e-12); Hamiltonian
constraint relative to 16 pi E starts at rounding, grows by time truncation, stays below
1e-5 at Courant 0.25 and falls as dt^4.
Refuted by a difference that does not converge, or by a slow-roll parameter off by more
than the band.

P3 (plane perturbation, constraint-satisfying data as above). phi0 = 3, A = 0.003,
n = (1, 1, 0), box 1, m = 0.1, Pi0 = -0.05, conformal-time lapse, zero shift, nghost 4,
RK4, Courant 0.25, meshes N x N x 8 with N = 16, 32, 64, to t = 0.5.
(a) At t = 0 the norms of H and M are truncation errors of sixth-order differences of
smooth data: they fall by 64 (order 6 +- 0.3) per doubling until the rounding floor
(relative 1e-13). (b) During the evolution the norms at fixed time fall with resolution
at an order between 4 (time integrator, Courant fixed) and 6; the Hamiltonian constraint,
dominated by the time truncation of the homogeneous part, at order 4 +- 0.5.
(c) Without the K' term in Pi (control: Pi = Pi0 everywhere) the momentum constraint is of
first order in A and does not converge.
Refuted by constraint norms that do not fall with resolution, or by a control that
converges.

P4 (noise hook).
(a) Mode amplitudes: the alpha_n used by the code equal those of the Python twin
(`python/nrpic/rng.py` with the keys above) bit for bit; the synthesized field, analysed
with numpy's FFT, has the coefficients c_n alpha_n prescribed, within 1e-12 of the rms
(rounding of the three sums and of the tables), and nothing above 1e-12 outside the ball.
(b) Spectrum: shell means of |xi_n|^2 / prescription are 1 within 4/sqrt(M_shell) (the
|alpha|^2 are exponential deviates), for the generic model (frozen and white in time) and
for the Mukhanov-Sasaki model.
(c) Layout: the dumped noise fields are bit-identical for 1, 8 and 64 MeshBlocks of a
32^3 mesh, and for a run restarted halfway against the uninterrupted run (fields, noise
and the lockstep mode data).
(d) White in time: increments of two different steps have a correlation coefficient
within 4/sqrt(M) of zero; with the frozen scheme it is 1 (same alpha).
(e) Lockstep integration: the mode data R_q, dot R_q and the background of the level-0
model agree with a SciPy integration of the same equations to O(dt^4) (factor 16 +- 4
per halving of the step).
(f) Kicks (SPEC 2.2, design review 5): with the stencil projector the first-order
momentum constraint of a single kick is at rounding relative to its terms, with the
continuum projector it is of the order (k h)^6; flipping the sign of the Pi kick gives a
first-order Hamiltonian violation. (Track E's test L5; run here only as a smoke test.)
Refuted by any bit difference in (a) alphas or (c), by a shell outside its band, or by a
first-order momentum violation with the stencil projector.

## 2026-11-15, entry 2: build, regression, outcomes of tests 1 and 2

### Build and regression [VERIFIED]

- The module builds on processors (`.work/build_cpu_sf`, 74 s). Commits ba37619 (module),
  5384d02 (block name `scalar_field` allowed in `parameter_input.cpp`), 836ac86 (inputs).
- P-reg holds: run core-20261115-132758-ba37619, five cases, 36 files, baseline twice and
  baseline against the new executable all byte-identical. (Repeated with the final
  executable at the end of the package.)
- Found on the way: Z4c with the driver's `rk4` does not keep a constant state constant to
  the last bit. The coefficients of the low-storage scheme are given to 15 digits, so a
  constant drifts by about 1.4e-15 per step (lapse 1 - 1.7e-15 after 16 steps of flat
  space, 1 - 7.4e-13 after 512 steps). This is the existing integrator, not the scalar
  field; it sets the rounding floor of the geodesic-slicing test below.

### Test 2, outcome (run core-20261115-133955-836ac86) [VERIFIED]

A first run (core-20261115-133847-836ac86) is void: the driver passed `pi0` as the text
`np.float64(...)`, which the code read as 0; the errors of 3e-3 that did not converge
showed it. Repeat with a plain number:

| Gauge | Courant | steps | a at the end | rel. diff. of a | of phi | of K | of alpha | max rms H / [H] |
|---|---|---|---|---|---|---|---|---|
| conformal | 0.5 | 39 | 3.7662 | 4.5e-6 | 3.4e-9 | 3.4e-9 | 8.1e-7 | 5.0e-12 |
| conformal | 0.25 | 77 | 3.7662 | 2.9e-7 | 2.2e-10 | 2.2e-10 | 5.4e-8 | 2.9e-13 |
| conformal | 0.125 | 154 | 3.7662 | 1.8e-8 | 1.4e-11 | 1.4e-11 | 3.5e-9 | 1.5e-13 |
| geodesic | 0.5 | 256 | 123.08 | 8.2e-8 | 3.8e-13 | 3.5e-13 | 3.6e-13 | 1.3e-13 |
| geodesic | 0.25 | 512 | 123.08 | 5.0e-9 | 7.5e-13 | 7.4e-13 | 7.4e-13 | 1.2e-13 |
| geodesic | 0.125 | 1024 | 123.08 | 3.2e-10 | 1.5e-12 | 1.5e-12 | 1.5e-12 | 1.2e-13 |

P2 holds: below 1e-5 at Courant 0.25 (2.9e-7), ratios per halving of the step 15.5 and
15.7 (a), 15.3 and 15.8 (phi, K) in conformal time, 16.2 and 15.8 (a) in geodesic slicing;
there the field, K and the lapse sit on the rounding floor of the integrator (the
difference doubles with the number of steps). eps1 = 4 pi Pi^2/H^2 is 0.994 to 0.997 of
1/(4 pi phi^2). Momentum constraint below 6.3e-15, rms of phi about its mean 4e-14, the
Hamiltonian constraint starts at 2.2e-16 of [H] and stays below 5e-12. Figures
`fig_flrw_conformal.png`, `fig_flrw_geodesic.png` (looked at).

### Test 1, outcome (run core-20261115-133809-836ac86) [VERIFIED]

The first run (core-20261115-133146-5384d02) stopped in part d: the input file lacked the
parameters the driver overrides (`lambda`, ...). Input completed; all parts repeated.

- (b) holds: errors against the semi-discrete solution 2.535e-4, 1.585e-5, 9.907e-7,
  6.192e-8 for Courant 0.4 to 0.05; orders 3.9993, 3.9998, 3.9999. The errors equal the
  estimate of classical RK4, omega t (omega dt)^4/120/sqrt 2, to four digits: for a
  linear problem the low-storage scheme has the amplification factor of classical RK4.
- (a) spatial orders hold: 1.99, 3.96, 5.92 for nghost 2, 3, 4. The frequency part FAILED
  as analysed: the straight-line fit of the phase differs from omega_h by 0.5 to 1 percent
  of omega_h - omega in all twelve cases (2.5e-7 absolute at N = 16, nghost 4, against the
  bound 4.0e-8). Suspected cause: the initial momentum uses the continuum omega, so on
  the mesh the data are a travelling plus a small standing wave, amplitude cos(Omega t) +
  i (omega/Omega) sin(Omega t), and a straight line through that phase is biased.
  New prediction, before the re-analysis: fitting Omega and the ratio r gives
  |Omega - omega_h| below the bound 4.0e-8 in all twelve cases and r = omega/omega_h. If
  not, the cause is something else.
- (c) FAILED as predicted: measured decay rate 4.1e-5 against 3.4e-5 from the stencil
  (ratio 1.21, band 5 percent). (The journal's "2 sigma t" was loose: sigma is the decay
  rate of the amplitude, 2 sigma that of the energy.) Suspected cause: the amplitude loss
  of RK4 itself, (omega dt)^6/144 per step = 7.1e-6 per unit time at Courant 0.25, which
  I left out. New prediction, before the re-analysis: measured / (stencil + integrator)
  within 2 percent of 1, and the amplitude loss of the runs of part b (no dissipation)
  equals (omega_h dt)^6/144 per step within 5 percent for Courant 0.4 and 0.2.
- (d) the number FAILED, the physics holds: differences to the ordinary differential
  equation at Courant 0.25 are 2.2e-6 (quadratic), 1.5e-5 (quartic), 7.2e-7 (plateau),
  3.8e-7 (inflection), not below 1e-7; the bound ignored that the phase error grows as
  omega t (omega dt)^4/120 with dt = 1/32. They fall by 16.0, 16.6, 15.7, 16.0 per
  halving of the step (orders 4.00, 4.06, 3.98, 4.00). The table agrees with the quartic
  potential it tabulates to 9.1e-10 (prediction 1e-9: holds).

### Test 1, follow-up (run core-20261115-134423-836ac86, analysis only) [VERIFIED]

Both new predictions hold. Fitting Omega and r: Omega - omega_h = -1.21e-8 to -1.34e-8 in
all twelve cases (bound 4.0e-8); the value is -omega (omega dt)^4/120 = -1.336e-8, the
phase error of classical RK4; r - omega/omega_h = -1.2e-10. Amplitude loss without
dissipation: 0.992, 0.998, 0.9995, 1.0000 of (omega_h dt)^6/144 per step for Courant 0.4
to 0.05. With dissipation 0.5: measured rate 4.0816e-5, stencil 3.3574e-5, integrator
7.266e-6, measured/(sum) = 0.9994. So the dispersion relation of the code is that of the
stencils, and the dissipation term is the one of the spacetime variables. Figures
`fig_wave_convergence.png`, `fig_wave_diss_potentials.png` (looked at; margins corrected
afterwards).

## 2026-11-15, entry 3: test 3, and the first look at test 4

### Test 3, outcome (run core-20261115-134118-836ac86) [VERIFIED]

| N | rms H, t = 0 | rms M, t = 0 | rms H, t = 0.25 | rms M, t = 0.25 | rms H, t = 0.5 | rms M, t = 0.5 |
|---|---|---|---|---|---|---|
| 16 | 5.56e-7 | 1.31e-5 | 3.66e-5 | 2.01e-5 | 1.64e-5 | 3.28e-6 |
| 32 | 8.88e-9 | 2.59e-7 | 7.47e-7 | 5.26e-7 | 4.63e-7 | 7.48e-8 |
| 64 | 1.40e-10 | 4.31e-9 | 1.17e-8 | 9.08e-9 | 8.65e-9 | 2.00e-9 |
| control 16 | 9.12e-3 | 1.50e-3 | 3.07e-3 | 1.49e-3 | 6.57e-4 | 6.45e-4 |
| control 32 | 9.12e-3 | 1.51e-3 | 3.06e-3 | 1.48e-3 | 6.70e-4 | 6.42e-4 |

([H] = 4.67.) (a) holds for H (orders 5.97, 5.99 at t = 0) and for M between 32 and 64
(5.91); M between 16 and 32 is 5.66, 0.04 outside the band (N = 16 is not yet
asymptotic). (c) holds: the control does not converge (orders 0.00 +- 0.03) and its
momentum constraint is 1.5e-3, 6e3 times that of the data at N = 32.
(b) the general statement holds (orders between 4 and 6: H 5.15 to 5.61 between 16 and
32, 5.72 to 6.00 between 32 and 64; M 5.26 to 5.62 and 5.22 to 5.99), but my specific
claim for H FAILED: I expected order 4 from the time truncation of the homogeneous part.
That part is only 3e-13 of [H] at these steps (test 2); the constraint error is the
spatial truncation of the perturbation and converges at nearly sixth order with a fixed
Courant factor. Figures `fig_plane_constraints.png`, `fig_plane_convergence.png` (looked
at).

### Test 4, before the registered run

- A debugging run of part A in a scratch directory (not registered, 32 cycles) showed the
  coefficients of the synthesized field within 8e-16 of the rms of the twin's
  prescription; a debugging run of part B showed orders 4.1 of the lockstep data,
  bit-identical fields for 1 and 8 MeshBlocks and through a restart. Numbers are quoted
  from the registered run only.
- The constraint histories of that debugging run show what P4 (f) cannot show in an
  evolved run on this coarse test mesh (k h up to 2.4, k dt up to 0.6): after the first
  step the momentum constraint is 2.7e-12 with either projector and doubles with the
  amplitude, i.e. a first-order residual, 5e-4 of that with the flipped sign.
  [JUDGEMENT, not tested: the discretisation of the evolution inside the step, not the
  kick.] So (f) is checked on the kick itself. Prediction, written before the registered
  run was read: the discrete momentum constraint of the dumped kick fields,
  D_i I_R - sum_j D_j T_ij with the sixth-order difference, relative to D_i I_R, is below
  1e-12 with the stencil projector and between 1e-3 and 0.3 with the continuum projector
  at the dump near t = 2 (modes with k h near 1.2 are in the window, where the stencil
  wave number is 1.3 percent below k). Flipped sign of the Pi kick: Hamiltonian violation
  after the first step more than 100 times that of the correct sign, and twice as large
  with twice the amplitude (first order).

## 2026-11-15, entry 4: test 4, outcome (run core-20261115-134715-1b6bc30) [VERIFIED]

Generic model (32^3, 2084 modes, 85 shells):
- (a) holds for the frozen scheme and the step window: coefficients of the synthesized
  fields minus the twin's prescription at most 2.9e-15 of the rms (frozen), 2.2e-16 (step
  window); nothing outside the ball (below 9e-17). It FAILED for the white-in-time scheme
  at cycle 64: 1.2e-11 (1.3e-14 at cycle 32). Suspected cause: the increment of the window
  was formed as W(t1) - W(t0); for modes far inside the window both are 1 to 1e-16, the
  difference is rounding, and its square root (the white-in-time amplitude) carries it at
  1e-8 of the shell amplitude, differently in the code (libm) and in the twin (NumPy).
  Change made: dW = sinh(s h dt)/(2 cosh x1 cosh x0), an identity without cancellation,
  in the code and in the twin. Prediction before the repeat: all cases below 1e-13.
- (b) holds: shell means of |xi_n|^2 over the prescription within 2.91 sigma (85 shells),
  mean over the 2084 modes 1.031 (1.4 standard errors).
- (c) holds: every field of the dumps (stochastic fields, phi, Pi, chi, K, lapse,
  constraints) bit-identical for 1, 8 and 64 MeshBlocks (frozen) and 8 and 64 (white in
  time), at cycles 32 and 64; a run restarted at cycle 32 gives a byte-identical dump at
  cycle 64 for both schemes.
- (d) white in time holds (0.007, band 0.088). For the frozen scheme my estimator gave
  0.13, not 1: it weighted the modes with the shell factors of the two steps, which peak
  at different wave numbers. The statement to test is that the amplitudes are the same:
  estimator replaced by the mean of the phase factors u1 conj(u2) per mode. Prediction
  before the repeat: 1 (to rounding) for frozen, within 4/sqrt(2M) of 0 for white in time.
- One step with the sources: phi and Pi equal the response of the Runge-Kutta polynomial
  per mode to 4.6e-16 and 2.9e-15, so the sources enter with the coefficients stated
  (the naive phi = c_phi xi is off by 3.8e-3, the (kappa dt)^2/6 term).

Mukhanov-Sasaki model (16^3, box 10, 435 modes in 31 shells, slow-roll background):
- (e) holds: mode functions against SciPy 6.37e-3, 3.65e-4, 2.17e-5 for Courant 0.25,
  0.125, 0.0625 (orders 4.12, 4.07; the test mesh has H dt = 0.096 and k dt up to 0.59
  at Courant 0.25); the source factors S_R the same (4.83e-3, 2.78e-4, 1.66e-5). The
  background of level 0 agrees to 1e-12 (it is smooth in slow roll). The mesh mean of
  ln a differs from the lockstep background by 3.0e-5, 1.8e-6, 1.1e-7 (order 4): the
  truncation of the mesh evolution, as in test 2.
- (a) holds: the six fields (I_R and five T_ij) minus (shell factor of the record) x
  (twin alpha) x (stencil projector) at most 7.1e-17 of the rms, at t = 2.03 and t = 4.
- (c) holds: 1 and 8 MeshBlocks bit-identical in every field; restart byte-identical.
- (f) holds on the kick fields: discrete momentum constraint of the kick 4.9e-16 of its
  terms with the stencil projector, 1.37e-2 with the continuum projector. Flipped sign of
  the Pi kick: rms H after the first step 1.90e-7 against 2.66e-11 (7e3 times), 3.81e-7
  with twice the amplitude (first order).
- Seen and not explained by a test: in the evolved run the momentum constraint after the
  first step is 2.65e-12 with either projector and doubles with the amplitude (first
  order, 5e-4 of the flipped case); later the continuum projector gives 1.2e-9 against
  6.7e-11 with the stencil projector. Level 1 (box means) gives the same constraint
  levels as level 0. Track E's test L5 on a resolved mesh has to settle whether the
  residual first-order part is the discretisation of the evolution.
Figures `fig_noise_power.png`, `fig_noise_ms.png` (looked at; legends moved afterwards).

## 2026-11-15, entry 5: repeat of test 4, final regression, cost, refined mesh, card

- Test 4 repeated with the window increment without cancellation and the phase estimator
  (run core-20261115-135414-5a6953e): both predictions of entry 4 hold. All twin cases
  at most 2.2e-16 of the rms (white in time 3e-17 to 6e-17); phase correlation 1.0
  (frozen), -4.7e-5 with band 0.062 (white in time). Everything else unchanged (lockstep
  orders 4.12, 4.07; fields 7.1e-17; layouts and restarts identical; kick identity
  4.9e-16 and 1.37e-2).
- Final regression (run core-20261115-135417-5a6953e): c1 to c4 identical, c5 reported
  "differs": the three mesh restart files, 35 bytes each. P-reg as written is REFUTED for
  these three files; the cause was then tested, not assumed. Hypothesis: the bytes are
  never-set members of a struct written raw into the restart header, so their content is
  heap history, which my one-line change of `parameter_input.cpp` (a longer list of
  block names) shifts. It could have failed: the differing bytes could have lain
  anywhere. They lie at 8252 to 8287 in all three files, exactly the nine coarse-mesh
  indices of `Mesh::mesh_indcs` after the ten set ones (offset of "<par_end>" + 10 + 8 +
  72 + 40) (run core-20261115-140328-5a6953e). The particle restart files, histories and
  all other outputs are identical. The first regression (ba37619) had happened to see
  the same heap content in both executables.
- Cost on one core at 64^3 (run core-20261115-135423-5a6953e): Z4c 1.494e4, with the
  field 1.337e4, with the Mukhanov-Sasaki sources (8538 modes, six fields per stage)
  1.239e4 zone-cycles per second.
- Refined mesh, smoke run (core-20261115-135434-5a6953e): the wave of test 1 crosses one
  refinement level for 64 steps without growth; rms difference to the exact wave 2.5e-6
  on the coarse and 6.4e-6 on the fine level, maximum 1.8e-5; a uniform 32^3 mesh would
  give 7e-8. No prediction had been written for the size of this error (smoke run).
- Standard outputs: `variable = sf` (bin) and `sf_phi` (vtk) written and read back with
  `bin_convert.py` (unregistered smoke run).
- Card: the module builds with CUDA 12.6 (`.work/build_gpu_sf`, 742 s with four jobs).
  Slurm job 4427 (`gpu_job.sh`: cost at 128^3, tests 2, 4, 3, 1) was submitted at 14:04
  UTC and was pending behind other owners' jobs. Prediction for the card, before it
  runs: the same verdicts as on processors; dumps bit-identical between layouts on the
  card; coefficients against the twin below 1e-12 of the rms (the card may contract
  products and sums differently, so not necessarily 1e-16); lockstep data identical to
  the processor run to rounding (they are integrated on the host); cost of the field
  below 25 percent and of the sources below 25 percent of a Z4c step at 128^3.

## 2026-11-15, entry 6: test 5 (particles and field together), prediction before the run

The additive sources (interface section 5) had not run with particles. Test: the dust
universe of `problems/cosmo/flrw.athinput` (32^3 particles, density-form sources with
extrapolation, conformal-time lapse) with a vacuum energy Lambda = 0.6, once from the
particle module (`particles/lambda`), once from a scalar field at rest with the constant
potential `v_offset = Lambda/(8 pi)` (phi = Pi = 0, so E = V and S_ij = -V gamma_ij: the
same sources through `tmunu_tot`). The initial data do not satisfy the Hamiltonian
constraint with Lambda (H0 = 1 is set for dust alone); both runs start from the same
data, which is all the comparison needs. Also the pair without vacuum energy (field
present with V = 0 against no field).
Prediction: lapse at the probe, proper time of the probe, proper volume and the deposited
energy agree between the members of each pair to better than 1e-10 relative over the run
to t = 0.5 (64 steps; the arithmetic differs: the field path multiplies the step
densities by 1/sqrt(gamma) and adds the vacuum energy before the solver, the particle
path inside it); the vacuum energy changes the final proper volume by more than 1 percent
(so the test is not vacuous). Refuted by a difference above 1e-8, which would mean a
source is counted twice, dropped, or taken at the wrong time level.
