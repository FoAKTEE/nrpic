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
