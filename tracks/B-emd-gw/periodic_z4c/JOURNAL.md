# Journal of the periodic_z4c work package (B-pre-1)

Helper of owner B-emd-gw. Predictions are written before the runs; outcomes are appended
below them, also when a prediction failed. Run ids: `tracks/B-emd-gw/runs/<run_id>/`.

## 2026-11-15 03:20 UTC: what exists, read from the code (commit b7b431d)

- [VERIFIED, athenak/src/pgen/pgen.cpp lines 963-964] `z4c_linear_wave` is a built-in
  problem generator of the release executables. The gauge-wave and robust-stability
  generators (`athenak/src/pgen/z4c/z4c_gauge_wave.cpp`, `z4c_stability.cpp`) define
  `ProblemGenerator::UserProblem` and are not in `athenak/src/CMakeLists.txt`: the
  release executables cannot run `athenak/inputs/z4c/awa/z4c_gauge_wave.athinput`.
  The gauge wave is therefore set up through `nrpic_cosmo` with `id = file`
  (conformally flat slices only) in the proper-length coordinate X of the initial
  slice, where the gauge-wave slice is flat (derivation in `analysis/refsol.py`, item 2).
- [VERIFIED, athenak/src/pgen/tests/z4c_linear_wave.cpp lines 95-101, checked with
  `refsol.tt_check`] The polarization tensor of `z4c_linear_wave` is traceless for every
  wave vector but transverse only when k lies along a coordinate axis: |e.k|/|k| = 1.0
  for k = (1,1,0) and 0.943 for k = (1,1,1) (the default of the upstream input
  `athenak/inputs/tests/linear_wave_z4c.athinput`). Against the TT tensor
  theta-hat theta-hat - phi-hat phi-hat, the components a_xy and a_yz have the wrong
  sign; flipping both makes e transverse for every k. Consequence: oblique waves start
  from data that violate the momentum constraint and the Gamma constraint (Gamma^i is
  set to 0 while -d_j gt^ij is not), so the oblique 3D test cannot be run correctly
  with the release executables. Request to core in README.md.
- [VERIFIED, athenak/src/outputs/binary.cpp, vtk_mesh.cpp] Mesh outputs bin and vtk
  are float32: a diagonal metric component 1 + h with h ~ 1e-6 is not representable.
  The tab output is double but one-dimensional; the restart file is the only
  double-precision full-mesh dump. The reader `analysis/athena_dumps.py` reads all
  three.
- [VERIFIED, athenak/src/z4c/z4c_calcrhs.cpp lines 682-728] Lapse:
  d_t alpha = lapse_advect beta.d alpha - f alpha Khat - lapse_kdriver alpha_ref alpha
  (Khat - <Khat>) + slow-start term, f = lapse_oplog lapse_harmonicf + lapse_harmonic
  alpha + lapse_volume chi^(-1/2). Shift: d_t beta^i = shift_Gamma Gt^i + shift_advect
  beta.d beta^i - shift_eta beta^i + shift_alpha2Gamma alpha^2 Gt^i + shift_H alpha chi
  (alpha d_j chi / 2 - d_j alpha) gt^ij. Defaults (z4c.cpp lines 139-157): 1+log
  (lapse_oplog = 2), shift_Gamma = 1, shift_eta = 2, advection on.
- [VERIFIED, athenak/src/utils/finite_diff.hpp] nghost 2, 3, 4 give centred differences
  of order 2, 4, 6 and Kreiss-Oliger dissipation of order 2 nghost with the factor
  sigma 2^(-2 nghost)/dx (z4c.cpp line 168, z4c_calcrhs.cpp lines 761-772).
- Speed of the processor executable (smoke runs below): 1.4e4 zone-cycles per second on
  one core for Z4c, in a 32^3 box as in a thin box. A 64^3 box over ten periods would
  take about 7 hours, so convergence is measured in thin boxes (N x 4 x 4 cubic cells,
  waves along x) and the 3D box is used only for the dumps and the oblique check.

## Smoke runs (setup checks, no prediction)

B-emd-gw-20261115-112946-b7b431d (pure-gauge file, Gamma driver), -112947- (3D box with
restart, bin and Weyl outputs), -112948- (gauge-wave file): all three run; the
nrpic_cosmo generator reads the file without a `<particles>` block; the restart reader
reproduces the exact initial data to 0 (gt) and 4e-22 (At); float32 bin differs from the
restart by 5.8e-8 on gt_yy (the float32 resolution of 1), 1e-13 on At_yy; the Weyl
scalar is zero in the first dump (computed only at waveform_dt after the first step)
and of order 1e-5 afterwards.

## Predictions, written 2026-11-15 03:35 UTC, before the runs of the sets below

### P1. TT wave along x, 10 crossings (sets lw_x_prod, lw_x_ref, lw_x_nodiss)

Amplitude 1e-6 (the upstream 1e-8 puts roundoff, about 1e-16/dx^2 per unit time in
Khat, chi and alpha, within 1e-4 of the signal: seen in a trial at 32 cells, 3e-13 in
Khat after one crossing). Amplitude and phase are measured by projecting
h_+ = (gt_zz - gt_yy)/2 on sin and cos of 2 pi x at every output; the reference is the
exact linear solution h_+ = A sin(2 pi (x - t)).
Prediction: the semi-discrete Fourier symbol of the code's operators
(`analysis/predict_lw.py`) gives, at t = 10:

| set | N | amplitude error | phase error (rad) |
|---|---|---|---|
| prod (ng 4, cfl 0.25, KO 0.5) | 16 | -1.72e-4 | -2.49e-4 |
| | 32 | -1.49e-6 | -6.23e-6 |
| | 64 | -1.46e-8 | -2.40e-7 |
| | 128 | -2.06e-10 | -1.27e-8 |
| ref (ng 3, cfl 0.3, KO 1) | 16 | -8.79e-3 | -8.29e-3 |
| | 32 | -2.84e-4 | -5.23e-4 |
| | 64 | -8.94e-6 | -3.28e-5 |
| | 128 | -2.80e-7 | -2.05e-6 |
| nodiss (ng 4, no KO) | 32 | -1.24e-7 | -6.23e-6 |
| | 64 | -3.89e-9 | -2.40e-7 |

Orders: prod amplitude 6.9, 6.7, 6.2 (KO of order 8 times 1/dx, then RK4 at order 5),
phase 5.3, 4.7, 4.3 (sixth-order space, RK4 phase at order 4 takes over); ref amplitude
5.0, phase 4.0. The measured numbers should match these within 10 percent wherever
they lie above 1e-9 (relative), and the gauge (conformal-time lapse in prod, 1+log
with Gamma driver in ref) makes no difference at first order. Refuted if: an error
differs by more than a factor 2 from the table, or the order is lower than 4 for the
phase, or the lapse or shift move above 1e-12 (second order: A^2 = 1e-12).
Roundoff floor expected near 1e-9 relative at 128 cells (1e-16/dx^2 integrated, then
projected); the N = 128 amplitude point of prod may sit on it.

### P2. Oblique data of z4c_linear_wave (set lw3d_check)

16^3, k = (1,1,1) and k = (1,0,0), A = 1e-6, constraints after the first steps.
Prediction: for k = (1,1,1) the momentum constraint |M_i| ~ 2 pi^2 sqrt(3) A |e.k|
~ 5e-5 (squared volume norm M-norm2 ~ 1e-9), for k = (1,0,0) below 1e-20 (second order
plus roundoff, ~1e-21 seen in the smoke run). Refuted if the two cases differ by less
than a factor 1e6 in M-norm2.

### P3. Apples-with-Apples gauge wave (set awa_gw)

H = A sin(2 pi (x - t)), A = 0.01 and 0.1, harmonic slicing, zero shift, production
numerics, N = 50, 100, 200 to t = 20, N = 50 to t = 200; exact solution of
`refsol.gw_exact_X`.
Prediction: (a) the initial data satisfy both constraints to roundoff (flat slice,
only K_XX); (b) at t = 20 the error of gamma_XX and alpha, relative to A, converges at
order between 4 and 6 (sixth-order space, fourth-order time; the wave travels at speed
1 with wavenumber close to 2 pi, so the TT table of P1 scaled to t = 20 is a guide:
about 3e-6 at 50 cells for the phase part), and the constraint norms converge at order
>= 4; (c) the A = 0.01 run at 50 cells stays bounded to t = 200 with an error that grows
at most linearly (phase drift); at A = 0.1 faster growth is possible [BACKGROUND: the
harmonic gauge wave has a continuum family of exponentially growing gauge modes, which
make many formulations fail this test at A = 0.1 within the 1000 crossings of the
standard; to be checked against the source in the knowledge base]. Refuted if the
A = 0.01 runs fail or lose convergence before t = 20.

### P4. Record of the lapse and shift options (sets gauge_lin, gauge_nl)

Flat slice, K_xx = kappa sin(2 pi x), alpha = 1, beta = 0 (exact vacuum data; flat
spacetime in other coordinates). Linearized prediction (`refsol.gauge_matrix`):
lapse sector oscillates at the gauge speed v_L = sqrt(F), F = lapse_oplog +
lapse_harmonic + lapse_volume + lapse_kdriver; the shift sector (Gamma driver)
oscillates at sqrt(4 mu_S/3) with damping eta/2.

| case | v_L | shift eigenvalues / k | at t = 10: a_s, K_s, h_s, b_c (kappa = 1e-6) |
|---|---|---|---|
| harmonic | 1 | - | ~0, 1.000e-6, ~0, 0 |
| onelog (1+log) | 1.414 | - | -1.753e-7, 6.270e-7, -1.753e-7, 0 |
| conformal (1/3) | 0.577 | - | 9.089e-8, 1.471e-7, 5.453e-7, 0 |
| volume (1/3) | 0.577 | - | same as conformal at first order |
| kdriver (1/3 + mu 1) | 1.155 | - | 5.349e-8, -9.567e-7, 8.024e-8, 0 |
| geodesic | 0 | - | 0, 1e-6, -2.000e-5 (secular drift), 0 |
| onelog_gd (Gamma driver 1, eta 2) | 1.414 | -0.159 +- 1.144 i | -1.753e-7, 6.270e-7, -5.471e-7, 2.210e-8 |
| conf_gd (0.75, eta 1) | 0.577 | -0.080 +- 0.997 i | 9.089e-8, 1.471e-7, -2.725e-7, -1.034e-9 |
| harm_hs (harmonic shift terms) | 1 | +-1 i (double) | ~0, 1e-6, ~0, ~0 |

At N = 64 the measured mode amplitudes follow the linear solution to within 1e-3 of
kappa over t = 10 (discretization errors of the frequency ~1e-7 at 64 cells, second-order
terms ~kappa^2 = 1e-12). onelog_gd at N = 32, 64, 128 converges to the linear solution.
Refuted if any case departs by more than 1 percent of kappa: that would mean the
reading of the gauge terms above is wrong.
Nonlinear set (kappa = 1.5, lapse excursions 0.1 to 0.3, N = 128, t = 10), qualitative:
harmonic slicing stays smooth (f = 1 satisfies the shock-avoidance condition
1 - f - alpha f'/2 = 0 of the Bona-Masso family [BACKGROUND, Alcubierre 1997]);
1+log (f = 2/alpha) satisfies it only at alpha = 1, the conformal-time and volume
lapses (f = alpha/3, chi^(-1/2)/3) not at all, so these may steepen and form gauge
shocks (a jump in the lapse, a crash or grid-scale noise). The time of failure, if
any, is recorded.
