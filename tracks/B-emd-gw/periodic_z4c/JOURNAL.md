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
- [VERIFIED, athenak/src/pgen/tests/z4c_linear_wave.cpp lines 107-112, checked with
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

## Outcome P2 (oblique data), 2026-11-15 11:50 UTC

Runs B-emd-gw-20261115-113216-0ea0f74 (k = (1,1,1)), -113217- (k = (1,0,0)),
`analysis/ana_check3d.py`, `figs/lw3d_check.png`, `tables/lw3d_check.json`.
Prediction confirmed, also in value: k = (1,1,1) gives M-norm2 = 1.558e-9 (predicted
from the generator's e_ij: 1.559e-9) and H-norm2 = 1.385e-9 (predicted 1.385e-9; the
Hamiltonian constraint is violated as well, since k.e.k = -4/3 != 0), largest |H| =
5.24e-5 (predicted 5.26e-5); k = (1,0,0) gives 1.2e-22 and 3.9e-22. The oblique data of
`z4c_linear_wave` are not a gravitational wave.

## Outcome P1 (TT wave along x), first pass, 2026-11-15 12:00 UTC

Runs: lw_x_prod N = 16..128 B-emd-gw-20261115-113219/113220/113221/113222-0ea0f74,
lw_x_ref B-emd-gw-20261115-113223/113227/113231/113232-0ea0f74, lw_x_nodiss
B-emd-gw-20261115-113236/113254-0ea0f74; `analysis/ana_lw.py`, `tables/lw_x.md`,
`figs/lw_x_history.png`, `figs/lw_x_convergence.png`.
- Confirmed for N = 16, 32, 64 in all sets: amplitude and phase errors at t = 10 equal
  the Fourier-symbol prediction to better than 1 percent (prod 16: -1.718e-4 / -2.494e-4
  rad against -1.718e-4 / -2.493e-4; ref 32: -2.840e-4 / -5.233e-4 against the same
  digits), except prod N = 64 phase (-2.63e-7 against -2.40e-7, 10 percent).
- Measurement artefact found and removed: the table header prints the time with seven
  digits; when the outputs do not fall on steps (ref set) this puts a sawtooth of up to
  3e-6 rad on the phase after t = 1 (visible in the first version of the history
  figure). The analysis now takes the time as cycle * cfl / N.
- Refuted in part: at N = 128 the errors leave the prediction. prod: phase -8.6e-8
  against -1.27e-8, amplitude +3.7e-9 against -2.1e-10; ref: phase -1.18e-6 against
  -2.05e-6, linear in time (a frequency offset of +1.4e-8 relative), while ref N = 64 is
  within 0.6 percent. The departure grows about fourfold from N = 64 to 128.
- Refuted: the fields that vanish at first order reach 2e-10 (alpha - 1, prod) and
  1e-9 (alpha - 1, ref, 1+log) at t = 10, not < 1e-12. They are independent of N and grow
  as t^2: the box mean of Khat grows as pi^2 A^2 t (9.8e-12 at t = 1, 9.9e-11 at t = 10;
  pi^2 A^2 = 9.87e-12), the source alpha At_ij At^ij of d_t Khat averaged over the box
  (the energy of the wave acting on the homogeneous mode of a closed box; the data are
  constraint-satisfying only at first order), and alpha - 1 follows from the slicing:
  -(1/6) pi^2 A^2 t^2 = -1.6e-10 for the conformal-time lapse (measured -1.6e-10 to
  -1.8e-10), -pi^2 A^2 t^2 = -9.9e-10 for 1+log (measured -1.0e-9). My estimate "A^2"
  had left out pi^2 t^2.

### P1b. Prediction for the follow-up set lw_x_roundoff (written before the runs)

Hypothesis: the departure at N = 128 comes from the rounding of 1 + h in double
precision (absolute 1.1e-16, so relative 1e-10 in h at A = 1e-6, amplified by 1/dx^2 in
the second derivatives); it should scale as N^2/A. The second-order homogeneous drift
does not shift the phase under the conformal-time lapse (alpha chi^(1/2) is constant,
so the coordinate light speed is unchanged), so these runs use that lapse.
Prediction: (a) lw_x_refconf_A1e-6_N128 (ref numerics, conformal lapse) reproduces the
ref departure: phase -1.2e-6 +- 0.2e-6 (the gauge is not the cause); (b) at A = 1e-5 the
departure falls tenfold: refconf phase within 5 percent of -2.05e-6, prod phase between
-2e-8 and -0.6e-8 (prediction -1.27e-8). Refuted if the A = 1e-5 departures stay at the
A = 1e-6 level.

## Interim P4 (nonlinear), 2026-11-15 12:10 UTC, and prediction P4b

Seen in the running set gauge_nl (N = 128, kappa = 1.5): the conformal-time lapse
(B-emd-gw-20261115-114004-0ea0f74) and the volume lapse (-114122-) turn non-finite
between t = 2.69 and 2.75, and between 2.88 and 2.94; before that the largest lapse
gradient grows from 0.75 (t = 1) to 5.5 (t = 2) and Theta reaches 4 to 16 at the last
finite dump. The harmonic slicing (-113859-) is back to alpha = chi = 1 to four digits at
t = 10; 1+log (-113943-) and the K driver (-114143-) are alive with gradients near 2.
P4b, written before the runs gauge_nl_conformal_N64 and _N256 (to t = 4, outputs every
1/32): if this is a gauge shock of the conformal-time condition (Bona-Masso with constant
f = 1/3, which does not satisfy 1 - f - alpha f'/2 = 0), the curves of the largest lapse
gradient for N = 128 and 256 agree within 5 percent up to t = 2, and the failure time
moves by less than 0.3 between them (N = 64 may fail earlier: fewer cells across the
steepening front). Refuted if the N = 256 run does not fail before t = 4, or if the
gradient curves differ by more than 5 percent before t = 2 (then the growth is a
numerical instability, not a property of the continuum slicing).

## Outcome P1b (lw_x_roundoff), 2026-11-15 12:05 UTC, and prediction P1c

Runs B-emd-gw-20261115-114947/114948/114949-dbd105a; `tables/lw_x_roundoff.md`,
`figs/lw_x_roundoff.png`. Departure = measured minus predicted phase at t = 10, N = 128.
(a) Confirmed: ref numerics with the conformal-time lapse at A = 1e-6 depart by
+9.1e-7 rad, as with 1+log (+8.75e-7): the gauge is not the cause.
(b) Refuted: at A = 1e-5 the departure does not fall tenfold; it becomes -1.32e-6
(prod) and -1.29e-6 (ref numerics). At A = 1e-5 the second-order secular terms (the box
mean of gt_xx and chi drift as A^2 t^2; 6.6e-10 at A = 1e-6, t = 10, so 6.6e-8 at
A = 1e-5) change the coordinate light speed by a few 1e-8 and lag the phase by ~1e-6:
the A = 1e-5 runs measure the second-order backreaction, not the floor, so (b) did not
test the roundoff hypothesis. Fitting departure = c A^2 + d with d independent of A
gives d = -6.0e-8 (prod) and +9.3e-7 (ref numerics); the same data are equally fitted
with d proportional to 1/A.
P1c, written before the runs lw_x_prod_A1e-7_N128 and lw_x_refconf_A1e-7_N128: if the
floor is roundoff of 1 + h (d ~ 1/A), the departures at A = 1e-7 are -6e-7 (prod) and
+9e-6 (ref numerics), within a factor 2; if the floor is a property of the discrete
scheme that the symbol analysis misses, they stay at -6e-8 and +9e-7 within a factor 2.
Second-order terms at A = 1e-7 are 100 times below those at 1e-6.

## Outcome P1c (roundoff floor), 2026-11-15 12:20 UTC

Runs B-emd-gw-20261115-120348-3907d49 (prod, A = 1e-7), -120350-3907d49 (ref numerics,
conformal lapse, A = 1e-7); `tables/lw_x_roundoff.md`, `figs/lw_x_roundoff.png`.
Confirmed: the departures at A = 1e-7 are -6.14e-7 (prod; predicted -6e-7) and
+9.24e-6 (ref numerics; predicted +9e-6), ten times those at A = 1e-6 (-7.3e-8 with the
second-order part removed, +9.1e-7). The floor at 128 cells is the rounding of 1 + h in
the evolved conformal metric (it scales as 1/A); at A = 1e-5 the second-order
backreaction on the homogeneous mode dominates instead. Between the two, A ~ 1e-6 gives
the cleanest test at 128 cells; the convergence orders are taken from N = 16 to 64,
where every error lies above both.
The floor grows with the resolution as well (ref numerics, A = 1e-6: departure 1.9e-7
at N = 64, 9.1e-7 at N = 128), as expected for rounding errors amplified by the 1/dx^2
of the second derivatives.
[JUDGEMENT] For the gravitational-wave work of Track B: a metric evolved as 1 + h in
double precision has a phase floor that scales as N^2/A; with the production numerics
it is 6e-8 rad per ten crossings at A = 1e-6 and 128 cells per wavelength, 6e-7 at
A = 1e-7. Signals with h far below 1e-7 at this resolution would need the perturbation
evolved separately from the background (noted under Requests, not needed now).

## Outcome P4 (record of the lapse and shift options), 2026-11-15 12:20 UTC

Runs: gauge_lin B-emd-gw-20261115-113304, 113321, 113418, 113517, 113548, 113600,
113615/113700/113713 (onelog_gd N = 32/64/128), 113816, 113850 (all -0ea0f74);
gauge_nl -113859, 113943, 114004, 114122, 114143, 114151 (-0ea0f74); gauge_nl_res
-115139/115140-42096b9. `tables/gauge.md`, `figs/gauge_linear.png`,
`figs/gauge_nl_profiles.png`, `figs/gauge_nl_gradient.png`.
- Linear set confirmed: for all nine options the four mode amplitudes follow the
  linearized system within 1.6e-6 kappa over t = 10 (prediction: within 1e-3 kappa),
  so the reading of the gauge terms of z4c_calcrhs.cpp is right, including the gauge
  speeds 1, sqrt 2, 1/sqrt 3 (conformal and volume), sqrt(4/3) (K driver mu = 1 on top
  of conformal time), the Gamma-driver mode -eta/2 +- i sqrt(4 mu_S k^2/3 - eta^2/4),
  the secular drift of geodesic slicing, and the absence of shift excitation for the
  harmonic shift terms with harmonic slicing (d_t b = k (h/2 - a) = 0 when a = h/2).
  The Gamma-driver case converges from 32 to 64 cells (departure 2.1e-5 to 1.1e-6
  kappa, order 4.3), then flattens (6.2e-7 at 128), the level of the second-order terms.
- Nonlinear set, kappa = 1.5 (lapse excursions 0.25 to 0.35):
  harmonic slicing stays smooth, its slicing identity alpha chi^(3/2) = 1 holds to
  1.7e-8, and alpha returns to 1 within 4e-8 at every integer and half-integer time
  (the harmonic time function solves the flat wave equation, so the slicing is periodic
  with the light-crossing time): confirmed.
  1+log, 1+log with Gamma driver, and conformal time with the K driver (mu = 1) run to
  t = 10 with lapse gradients up to 3.7 and Theta up to 3e-3 (1+log identity residual
  3e-5): profiles flatten and develop kinks but do not fail within ten crossings.
  Conformal time and the volume lapse steepen into jumps (`figs/gauge_nl_profiles.png`,
  t = 2.5) and turn non-finite at t = 2.75 and 2.94 (N = 128): confirmed as predicted
  for slicings that violate the shock-avoidance condition.
- P4b, partly refuted: the gradient curves of the conformal-time lapse agree within 3.5
  percent up to t = 1.5 (2.09 and 2.17 at N = 128, 256) but not at t = 2 (5.45 and 8.29);
  at t = 2.25 they are 4.5, 8.0, 13.5 for N = 64, 128, 256, approaching the doubling per
  refinement of an unresolved jump: the gradient diverges in the continuum between
  t = 1.5 and 2 (a gradient catastrophe, [JUDGEMENT] a gauge shock). The failure time is
  not a property of the continuum: N = 64 and 128 fail at 2.78 and 2.75, N = 256 does not
  fail by t = 4 but carries Theta of order 1 to 3 and chi down to 0.3 from t = 2.25 on,
  i.e. the solution is no longer the flat spacetime it started as. So the statement to
  keep is "the conformal-time and volume lapses form a gauge shock at t ~ 2 for these
  data and the Z4c solution is invalid afterwards at every resolution", not a failure
  time.
- [JUDGEMENT] Consequence for the cosmology runs: the production lapse (conformal time,
  `lapse_harmonic = 1/3`) is not shock-avoiding. With these data the shock needs an
  inhomogeneous K of about 1.5 on a wavelength of one box (K/k ~ 0.24); in the
  cosmological runs the inhomogeneous part of K is set by the matter, and where it
  approaches this level in units of the local wavenumber, gauge shocks are possible.
  Not tested here: a criterion in terms of the matter perturbation.

## Outcome P3 (gauge wave), 2026-11-15 12:35 UTC

Runs (awa_gw): A = 0.01 N = 50/100/200 B-emd-gw-20261115-114426/114809/113212-0ea0f74,
A = 0.1 N = 50/100/200 -114940/115059/113214-0ea0f74, long runs N = 50 to t = 200
-113213- (A = 0.01) and -113215- (A = 0.1); `tables/awa.md`, `figs/awa_history.png`,
`figs/awa_long.png`.
- (a) Confirmed: at N = 200 the evaluated |H| starts at 6e-10 for both amplitudes
  (rounding level of the evaluation), constraints of the data are satisfied.
- (b) Confirmed for A = 0.1 (orders of the largest gamma_XX error 5.98 and 4.74, of |H|
  5.89 and 5.90) and for A = 0.01 from 50 to 100 cells (5.66, |H| 5.92); refuted for
  A = 0.01 from 100 to 200 cells: the error does not fall (1.14e-7 to 1.52e-7 of A),
  and |H| stays at the 6e-10 floor of the initial data for the whole run. [JUDGEMENT]
  rounding floor, as in P1c (absolute error 1.5e-9 at 200 cells); not separately tested.
- Measurement artefact found and removed before these numbers: the table header prints
  t with seven digits (5e-5 at t = 100), which entered the comparison with the exact
  solution as a phase error of up to 3e-4 in the first version of the analysis; the
  time is now cycle * cfl * dx.
- (c) Partly refuted: A = 0.01 at 50 cells stays bounded to t = 200, but its error grows
  faster than linearly (5.8e-6 at t = 20, 3.5e-5 at 50, 1.6e-4 at 100, 8.8e-4 at 200 of
  A: about t^2.3 between 50 and 200), and A = 0.1 grows to 9.4e-2 of A at t = 200 (about
  t^2.6), |H| 4.1e-3. Whether this is the known continuum gauge mode of the harmonic gauge
  wave or numerical growth is not decided here (it would need the growth at two
  resolutions over the same time, and the source in the knowledge base).
