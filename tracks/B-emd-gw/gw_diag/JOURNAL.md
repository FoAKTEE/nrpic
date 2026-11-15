# JOURNAL of gw_diag (B-pre-3, helper of B-emd-gw)

Predictions are written before the test runs; outcomes are appended below each, also when
the prediction fails.

## 2026-11-15 Definitions taken from the source

- [VERIFIED] York's covariant TT decomposition `Q^ab = Q_TT^ab + (LV)^ab + gamma^ab Q/3`,
  `(LV)^ab = D^a V^b + D^b V^a - (2/3) gamma^ab D_c V^c`, `D_a (LV)^ab = D_a (Q^ab - gamma^ab Q/3)`:
  arXiv:2111.09163 v2, `kb-data/raw/arxiv/2111.09163/v2/src/prd_v1.tex` lines 163-175.
- [VERIFIED] `rho_K = (M_pl^2/2) K^TT_ab K_TT^ab` (Eq. rhoK, line 260), with `K_ab = (1/2) L_n gamma_ab`
  (line 225; opposite sign to AthenaK, irrelevant for a quadratic quantity); "rho_K = rho_Isaacson/2"
  for linear tensor modes (footnote, line 272); in Newtonian gauge `K_TT^ij = hdot^tt_ij/(2 a^2)` and
  `rho_K = (M_pl^2/8) hdot^tt_ij hdot^tt_ij` (Eqs. Aijnewton, rhoknew, lines 496 and 501).
- [VERIFIED] AthenaK conventions read from the source: Z4c variable order
  (`athenak/src/z4c/z4c.hpp` lines 48-56); `psi^4 = chi^(4/chi_psi_power)`, default
  `chi_psi_power = -4` (`z4c.cpp` line 125, `z4c_adm.cpp` lines 220-233);
  `K_ab = psi^4 A_ab + (Khat + 2 Theta) gamma_ab / 3`; Weyl scalar
  (`z4c_calculate_weyl_scalars.cpp`): radial triad about the origin, Gram-Schmidt in the order
  phi, r, theta, output multiplied by r; finite differences of order 2, 4, 6 for nghost 2, 3, 4
  (`utils/finite_diff.hpp`).

## 2026-11-15 Derivations used by the module [JUDGEMENT until the tests below pass]

D1. Trace removal before the projection. With `gamma = a^2 (delta + h)` and zero shift,
`K_ij = -(1/2 alpha) (2 a adot (delta + h) + a^2 hdot)`. `Lambda K` contains `-(a adot/alpha) h^TT`, a term
that is not a time derivative of the wave; the trace-free part with respect to the full metric,
`A_ij = K_ij - gamma_ij K/3 = -(a^2/2 alpha) hdot_ij`, does not. Hence the module projects
`tilde A_ij = chi A_ij = -(1/2) d_tau h_ij` (Z4c's variable) and never `K_ij` itself:
`d_tau h^TT = -2 Lambda(tilde A)`, `rho_kin = Lambda(tilde A)_ij Lambda(tilde A)_ij / (16 pi G)` = rho_K
of 2111.09163 to the order of the projection.

D2. Psi_4 sign. Linear wave along +z in TT gauge, `K = -hdot/2`: `R_ij = -(1/2) hddot_ij`, so
`E = -(1/2) hddot`; `B_ij = sym(eps_i^kl d_k K_lj)` gives `B_xx = -hddot_x/2`, `B_xy = hddot_+/2`,
`B_yy = hddot_x/2`. With `mbar = (x - i y)/sqrt 2`: `(E - iB) mbar mbar = -hddot_+ + i hddot_x` and
`(E + iB) mbar mbar = 0`. So `Psi_4 := -(E - iB) mbar mbar = hddot_+ - i hddot_x`, and the reversed
direction gives zero. AthenaK's expression (`rpsi4 + i ipsi4 = 2 Y_ab mbar^a mbar^b` with
`Y = -Rnn/4 + R_acb u^c/2 - R_dacb u^d u^c/4`, `mbar = (v - i w)/sqrt 2`) evaluates for the same wave
to `hddot_+ - i hddot_x` before the factor r, i.e. the same convention.

D3. Helicity. A Fourier mode `exp(i(k.x - omega t))` with polarization `e^(+2) = (e_+ + i e_x)/sqrt 2`
turns counterclockwise about its direction of motion (helicity +2). A mode at k moving along -k
with the same label turns clockwise about k, i.e. counterclockwise about its motion: also +2.
(A first version of `helicity_spectrum` flipped the label of backward parts; corrected before any
test ran.)

D4. Scalar perturbations and Psi_4. For `gamma = (1 + 2 zeta) delta + 2 dd E` the linear
`E_ij = -(d_i d_j - delta lap/3) zeta` is not zero (the tidal field of the matter); B = 0 and
`Lambda E = 0`. So Psi_4 along a direction n is `-(k.mbar)^2 zeta` for a plane scalar mode, zero
only for n parallel to k. A scalar perturbation is invisible to the TT diagnostics but not to
Psi_4 off its wavevector: in a box with matter, Psi_4 measures tidal fields as well as waves.

## Predictions (written 2026-11-15 before the tests ran)

P1 (unit tests, `tests/`). (a) Lambda is idempotent, symmetric, traceless and transverse to
round-off (< 1e-12 relative). (b) A plane wave along each axis and along lattice diagonals,
on a non-cubic grid (nx != ny != nz, Lx != Ly != Lz), is returned by tt_project to round-off
(it is band-limited and exactly TT), and its h_+, h_x, rho_kin and rho_grad equal the input to
round-off when the arrays are given as h directly. (c) Built from gamma = delta + h, K = -hdot/2
through the conformal decomposition, the relative error in h^TT and in rho is O(A) (the O(A^2)
terms of det(gamma)^(-1/3)): at A = 1e-6 below 1e-5, and falling by 10 per decade of A.
(d) Hand-written circular waves: h_xx = A cos(kz - wt), h_xy = A sin(kz - wt) along +z has
helicity -2 (pattern clockwise about +z); h_xx = A cos(kz + wt), h_xy = A sin(kz + wt) moving along
-z has helicity -2. All energy must land in the predicted helicity (other < 1e-12 of the total).
Refuted if any of these fails.

P2 (Weyl on waves). E and B from gamma, K agree with the linear references E = -hddot/2,
B = -(1/2) sym(eps d hdot); the error falls as dx^p for orders p = 2, 4, 6 (fitted slopes within
0.3 of p) until it reaches the O(A^2) floor; spectral derivatives sit on the floor at every
resolution. Psi_4 along k equals hddot_+ - i hddot_x; Psi_4 along -k is below 1e-6 of it at
A = 1e-6 with spectral derivatives (only O(A) relative). Refuted if a slope or the sign of Psi_4
differs.

P3 (pure gauge, exact Minkowski in random coordinates, with slicing). h^TT, d_tau h^TT and rho
scale as eps^2 (slope 2 +- 0.1 in eps over 1e-6 ... 1e-2), i.e. zero at linear order. E, B and
Psi_4 vanish analytically at every order; numerically they converge to zero as dx^p at fixed eps,
and at fixed resolution scale as eps (slope 1). Refuted if the TT parts scale as eps or the Weyl
parts do not converge.

P4 (scalar mode). h^TT, d_tau h^TT, rho, B and Lambda E scale as eps^2; E agrees with the linear
E = -(dd - delta lap/3) zeta to O(eps^2) + truncation; Psi_4 off-wavevector is nonzero and equals
-E_lin mbar mbar (D4). Refuted if B or Lambda E scale as eps.

P5 (random superposition, 48 modes, |m| in 1..6, A = 1e-6 per mode). Shell spectra of rho_kin and
rho_grad equal the per-mode expectation of `analytic.waves_expected` to relative 1e-5 (O(A)), at
every time; total rho_kin + rho_grad constant in time to 1e-5 while rho_kin and rho_grad separately
oscillate (finite number of modes; their time average is equal); helicity energies match the
input fractions to 1e-5. d_tau h^TT from centred time differences of h^TT at spacing dt converges to
the 3+1 value as dt^2.

P6 (AthenaK output, run B-emd-gw-20261115-113218-0ea0f74 of periodic_z4c: z4c_linear_wave, k along x,
A = 1e-6, 32^3, restart files every 1/16 period). The reader assembles the mesh; h^TT is the pgen
wave h_ij = A e_ij sin(2 pi (x - t)) with e = diag(0, -1, 1) (pgen source,
`athenak/src/pgen/tests/z4c_linear_wave.cpp`), i.e. h_+ = A sin(2 pi (x - t)) in the basis of
pol_basis(+x) (theta-hat = -z, phi-hat = +y), h_x = 0; rho_kin + rho_grad = (2 pi)^2 A^2 / (32 pi)
constant in time to the evolution error (sub-percent at 32^3 over two periods [JUDGEMENT]);
d_tau h^TT from K agrees with time differences between dumps. Psi_4 from E, B with AthenaK's
radial triad agrees with AthenaK's weyl output divided by r to the float32 and stencil
differences (relative 1e-3 [JUDGEMENT]), where the output was computed at the same time.
Refuted if the amplitude, polarization or sign differ.

## Outcomes of the unit tests (2026-11-15, `python3 -m pytest tests/`)

First run: 10 passed, 2 failed.
- P1(a), (b), (d) passed as predicted: Lambda idempotent, traceless, transverse to round-off;
  plane waves along axes and lattice diagonals on a non-cubic grid returned to < 1e-12 with
  h_+, h_x, rho_kin, rho_grad exact; the hand-written circular waves along +z and -z put all
  their energy in helicity -2 (helicity +2 below 1e-12 of the total).
- P1(c) FAILED as stated: the relative error of h^TT, d_tau h^TT from (gamma, K) is O(A^2), not
  O(A): 3.7e-8 at A = 1e-4, 3.7e-4 at A = 1e-2 (slope 1.77 including a round-off point at 1e-6).
  Cause, checked afterwards in a run where it could have failed (inline script, 24x20x18 grid,
  six random waves): tilde gamma - delta - h is O(A) relative (1.6e-4 at A = 1e-4) but its
  trace-free part is O(A^2) (4.1e-8 at A = 1e-4, 4.1e-4 at A = 1e-2) — the O(h^2) term of
  det(gamma)^(-1/3) is a pure trace, which Lambda removes. The test now expects slope 2.
- Gauge-mode test FAILED and exposed a bug: with K = 0 (flat metric in curvilinear coordinates)
  the Ricci tensor with spectral derivatives was 1.5e-3 at eps = 1e-3, scaling as eps^2. Cause: in
  `weyl.ricci` the quadratic Christoffel terms were contracted with einsum labels "i, j" inside a
  loop over (i, j), so einsum summed over i and j. Checked against the direct formula
  R_ij = d_k G^k_ij - d_j G^k_ki + G^k_kl G^l_ij - G^k_jl G^l_ki (difference 0.16 before, round-off
  after the fix). After the fix: R = 1e-12 (spectral) for the flat metric; with slicing, E and B
  are 1e-12 (spectral) while R itself is 8e-4 (balanced by the K terms); FD4 E falls by 15 from
  16^3 to 32^3 (order 3.9). The plane-wave tests could not see the bug (it is O(A^2), A = 1e-8).
After the two corrections: 12 passed, 2 skipped (the real-file reader tests need GWDIAG_RST /
GWDIAG_NRFIELD).

## Amendments to P5 (written before validate_tt.py ran)

- After the P1(c) outcome the expected error of quantities built from (gamma, K) is O(A^2)
  relative plus round-off ~1e-16/A: at A = 1e-6 per mode, below 1e-9 (not 1e-5).
- With no pair k_m = -k_n among the modes, the spatial average of each mode is time
  independent, so rho_kin and rho_grad are separately constant, not oscillating (the original
  P5 sentence is wrong on its face). They oscillate in antiphase only for standing waves; a
  standing-wave case (modes at m and -m with equal amplitudes) is added: prediction
  rho_kin + rho_grad constant to < 1e-9 while rho_kin/rho_ref swings between 0 and 2 for a
  single standing mode.

## Outcome of P1, P3 (TT part), P5 — runs B-emd-gw-20261115-115001-e9262bd, -115125-42096b9, -115206-2e6c497

(Same computations three times; the reruns only changed the figure layout; numbers identical.)
`results_tt.json`, figures `figs/tt_amplitude_spectrum.png`, `figs/tt_time.png`, `figs/tt_gauge_scalar.png`.
- From (gamma, K) for 12 random waves on a 32x28x24 non-cubic box: relative error of h^TT,
  d_tau h^TT and rho_GW proportional to A^2 (fitted slopes 2.00, 1.99, 2.00 for A >= 1e-4;
  9.5e-8 at A = 1e-4), with a round-off floor of 1e-11 at A = 1e-6. As amended.
- 48 waves, |m| = 1..6, 64^3, A = 1e-6 per mode, 70 % of the energy in helicity +2: total
  rho_GW relative error 2.4e-12, worst shell 2.6e-12, helicity +2 fraction 0.7000000000000428,
  empty shells 1e-21 of the total. PASSED (P5).
- Time series over one box crossing (41 times, 32^3): total, 2 rho_kin and rho_(+2) constant to
  2.7e-12; the standing wave (m = +-(0,0,2)): rho_kin/rho_ref between 6e-78 and 1.0 (i.e. 2 rho_kin
  swings 0..2) while the total stays at 1 to 1.7e-11. PASSED as amended (the original P5 claim of
  oscillation for distinct travelling waves was wrong; caught before the run).
- d_tau h^TT from centred differences of h^TT at spacing dt against the 3+1 value: 1.44e-2 at
  dt = 0.01 L, 3.6e-3 at 0.005 L (order 2.0 at the small end; slope 1.89 over the whole range
  because omega dt ~ 3 at the largest dt). PASSED.
- Pure gauge (exact Minkowski in random coordinates incl. slicing) and scalar data, 32^3,
  eps = 1e-6..1e-2: max |h^TT| and max |d_tau h^TT| scale as eps^2 (slopes 2.002 / 2.002 gauge,
  2.007 / 2.002 scalar), rho_GW as eps^4 (4.000, 4.002), while the input metric perturbation
  scales as eps (1.001, 1.000); h^TT / input = 7e-7 at eps = 1e-6. PASSED (P3, P4 TT part).

## Prediction for validate_weyl.py (written before it ran)

Convergence on 12..64 cells per side: for waves (8 modes, |m| <= 2, A = 1e-8) the errors of E
and B against the linear references, for the pure-gauge data (eps = 1e-3) max|E|, max|B|
divided by max|R| (R itself is O(eps) and balanced by the K terms), for scalar data
(eps = 1e-6) max|B| and max|Lambda E| divided by max|E_lin|: fitted orders 2, 4, 6 within 0.3
for the finite-difference stencils above the floors (waves 1e-8, scalar 1e-6 relative, gauge
round-off), spectral at the floor at every N. Psi_4 for the plane wave m = (1,1,0), spectral,
32^3: relative error and |Psi_4(-k)|/|Psi_4(k)| proportional to A (slope 1 +- 0.1) down to
round-off. Scalar mode zeta = eps sin(4 pi x + 0.3): Psi_4 along x zero to O(eps) relative to
max|E_lin| (the TT-part statement), Psi_4 along y and along (1,1,0) nonzero and equal to
-E_lin mbar mbar to relative O(eps) (D4).

## Outcome of the first Weyl validation, run B-emd-gw-20261115-115358-637c30b

- Waves: orders 2 and 4 converge as predicted (fitted 2.00/1.98 and 3.98/3.96 for E/B, N >= 24).
  Order 6: B 5.89, but E levels off at 1e-6 for N >= 48. The spectral E error is NOT constant: it
  grows from 1.2e-7 (N = 12) to 4.0e-6 (N = 64), ~N^2. Cause [checked by the scaling, not by a
  separate run]: the metric is stored as 1 + h with h ~ 1e-8, so each cell carries an absolute
  representation error ~1e-16 whose second derivative is ~1e-16 (pi N/L)^2 = 4e-12 at N = 64,
  against E ~ 1e-6: relative 4e-6. A floor of the data, not of the stencils; for AthenaK data with
  A = 1e-6, N = 32, k = 2 pi it is ~3e-8 relative. Spectral derivatives now subtract the mean before
  the FFT (removes the FFT's own round-off spread from the 1; the representation error stays).
- Pure gauge: order 2 showed no convergence (E/|R| = 0.48 at every N) and orders 4, 6 gave 2.9 and
  5.8. Cause: a bad normalization in the script, not the stencils. R of a pure gauge is O(eps^2)
  (spectral max|R| 8.4e-4 at eps = 1e-3, 8.4e-6 at 1e-4, earlier inline check), while the truncation
  error of every FD term is O(eps dx^p); for order 2 the truncation error dominates the FD |R|
  itself, so the ratio is constant. Changed to the O(eps) scale max|d_k d_l gamma_ij| (spectral).
- Scalar: orders 2 and 4 converge (B 1.97, 3.44 with the last point on the floor); order 6 B and
  Lambda E reach the floor 1.5e-5 = second order in eps (the unit test shows eps^2 scaling) by
  N = 32. Fits now use only points above 20x the spectral value at the same N.
- Psi_4 of the plane wave: relative error and reverse/forward ratio proportional to A (slope
  1.001), as predicted. Scalar mode: Psi_4 along k exactly 0; along y and (1,1,0) it equals
  -E_lin mbar mbar to 3.0e-6 relative (= O(eps), eps = 1e-6), max|Psi_4| = 7.9e-5 = 0.75 max|E_lin|.
  PASSED: a scalar perturbation produces Psi_4 off its wavevector (D4).

## Outcome of the Weyl validation rerun, run B-emd-gw-20261115-115540-2cb33df

Fitted orders (points with N >= 16 and above 20x the spectral value at the same N):
waves E/B 1.99/1.98, 3.95/3.95, 5.84/5.89; pure gauge (|E|, |B| / max|dd gamma|) 1.94/1.98,
3.93/3.95, 5.83/5.88; scalar E/B/Lambda E 1.93/1.97/1.91, 3.92/3.86/3.93, 5.82/-/5.81 (order-6 B
reaches the second-order floor 1.5e-5 by N = 32). Spectral: pure gauge E and B at 1e-12..1e-15
for N >= 24 (B at N = 12: 9e-7, the non-band-limited part of the nonlinear data); waves B at the
O(A) floor 1.7e-8; waves E rising 7e-8 -> 1.2e-6 with N (representation floor of 1 + h, ~N^2;
the mean removal lowered it from 4.0e-6 at N = 64). PASSED (P2, P3 Weyl part, P4).
Psi_4 of the plane wave m = (1,1,0): error proportional to A (slope 1.001) and equal to
hddot_+ - i hddot_x (sign convention D2 confirmed). FAILED in a benign way: |Psi_4(-k)|/|Psi_4(k)|
was predicted O(A) but is 5e-7 at A = 1e-8 falling to 6e-13 at A = 1e-2, i.e. a constant round-off
absolute value: for a single plane wave the reversed scalar vanishes at every order.
[BACKGROUND] a metric depending on x only through t - n.x is a plane-fronted wave whose Weyl
tensor is of Petrov type N with respect to n, so only the outgoing scalar is nonzero; the O(A^2)
part of the data is null dust (R_uu ~ hdot^2), which enters E and B only through traces and n n
terms that mbar mbar does not see. For a superposition with several directions the reverse
scalar is O(A^2) from the cross terms (not measured here).

## P6 refined (written before validate_athenak.py ran)

Input: run B-emd-gw-20261115-113218-0ea0f74 (periodic_z4c helper; finished, 33 restart files
t = 0 .. 2 every 1/16, binary weyl output at the same times; AthenaK computes the Weyl scalar at
the end of the step at which an output time is reached, `z4c_tasks.cpp` CalcWeylScalar, and
dt = 1/128 divides 1/16, so both refer to the same time). Predictions:
- my reader and the periodic_z4c reader (`../periodic_z4c/analysis/athena_dumps.py`, written
  independently) give bit-identical Z4c arrays;
- h_+ from Lambda(tilde gamma - delta) along +x: amplitude 1e-6 and phase -2 pi t to the evolution
  error (sub-percent at 32^3, 8 cells... [JUDGEMENT]: 32 cells per wavelength with 6th-order
  stencils and RK4, two periods: amplitude and phase errors < 1e-3); h_x < 1e-3 of h_+; the non-TT
  part |h - h^TT| at the level of the O(A^2) and constraint terms (< 1e-3 of A);
- rho_kin + rho_grad = pi A^2/8 = 3.93e-13 (G = 1) to < 1e-3, constant in time;
- d_tau h^TT = -2 Lambda(tilde A) against time differences of h^TT between dumps (dt = 1/16):
  second-order centred difference off by (omega dt)^2/6 = 2.6 %, fourth-order by
  (omega dt)^4/30 = 7.8e-4 (plus the evolution error);
- Psi_4 along +x from E, B (6th-order stencils, as AthenaK with nghost = 4): equals
  hddot_+ = -(2 pi)^2 A sin(2 pi (x - t)) to the evolution error, imaginary part ~0;
- Psi_4 in AthenaK's radial triad times r against AthenaK's weyl_rpsi4 + i weyl_ipsi4: same
  convention (D2), agreement to ~1e-5 relative to the maximum (float32 output, identical stencils
  for a wave that depends on x only). A sign flip or a factor would refute D2.

## Outcome of P6, run B-emd-gw-20261115-115846-214d142 (input run B-emd-gw-20261115-113218-0ea0f74)

- Readers: my read_rst and the periodic_z4c reader give bit-identical arrays (lw3.00005.rst). PASSED.
- TT on AthenaK output (33 dumps, t = 0..2): |h_+|/A within [0.9999997, 1.00000002], phase error
  <= 1.25e-6 rad, rho_GW/rho_ref within [0.9999994, 1.0000000], max|h_x|/A = 8e-25, non-TT part
  max|h - h^TT|/A = 2.7e-5. PASSED, far inside the predicted 1e-3.
- d_tau h^TT = -2 Lambda(tilde A) against time differences of the dumps: median relative difference
  2.550e-2 (second order; predicted 2.570e-2) and 7.78e-4 (fourth order; predicted 7.93e-4). PASSED:
  the residual is the truncation of the time difference itself, so -2 Lambda(tilde A) is the time
  derivative of h^TT to better than 1e-5.
- Psi_4 along +x from E, B (6th order): matches hddot_+ = -(2 pi)^2 A sin(2 pi (x - t)) to
  2.6e-7 .. 1.4e-6 relative. PASSED.
- Psi_4 in AthenaK's radial triad times r against AthenaK's weyl output written at the same t_n:
  FAILED as predicted: max relative difference 0.21 .. 0.58 (sign right: the negated comparison
  gives ~2). Diagnosis (inline scan, then built into the script): the weyl file written at t_n
  matches my Psi_4 of the dump at t_(n-1) to 3e-2 .. 7e-2 and the analytic wave through gwdiag at
  t_n - 7.00 dt (dt = 1/128 = the step; output interval 8 steps) to ~1e-4 at every file tested
  (n = 4, 5, 9, 16, 31). So AthenaK's weyl output at an output time holds the Weyl scalar of one
  step after the previous waveform time, i.e. it lags by waveform_dt - dt. Plausible mechanism
  [TO VERIFY by core]: InitRecvWeyl sets last_output_time when time >= last + waveform_dt and
  CalcWeylScalar runs only when time == last_output_time at the last stage, so the scalar is
  computed at the first step past a waveform time, then written by the mesh output of the NEXT
  output time. The convention D2 (sign and normalization) is confirmed at that time.
Prediction for the rerun with the timing fit built in: integer offset -7 steps at every file
tested (n = 2, 5, 9, 16, 23, 31), residual at the best fractional offset < 2e-4 and within 1e-3 of
-7.00 steps.

## Outcome of the rerun with the timing fit, run B-emd-gw-20261115-120128-7dfaa38

At every tested file (n = 2, 5, 9, 16, 23, 31) the best offset is -7.00 steps exactly (fractional
scan over +-0.5 step at 1/40 resolution), with residual 3.0e-7 .. 1.8e-6 relative to the maximum
(growing with t like the evolution error of the dumps), against 0.25 .. 0.58 at offset 0. PASSED:
AthenaK's weyl output and gwdiag's Psi_4 (independent formula: E, B instead of Riemann
contractions) agree to ~1e-6 in the same triad once the output lag of waveform_dt - dt is taken
into account; convention D2 holds on AthenaK output. Figures `figs/athenak_tt.png`,
`figs/athenak_psi4.png`.

## Prediction for the readers on real cosmology dumps (written before the run)

`tests/test_readers.py` with GWDIAG_RST = runs/cosmo/restart_test/a/rst/east.00002.rst (nrpic_cosmo,
8 MeshBlocks, particles in a separate file) and GWDIAG_NRFIELD =
runs/cosmo/dav_c704_n32_tsc4t/east.field.00001.bin: both read without error, the restart's
size check (header + nmb data_size == file size) passes, chi > 0 and finite; the NRFIELD dump has
no trailing bytes. (An inline read of the restart already gave t = 0.5, 32^3, L = 4, chi in
[0.4095, 0.4097].)

## Outcome: readers on real dumps (pytest, 2026-11-15)

`tests/test_readers.py` with the two real files: 4 passed. The restart (nrpic_cosmo, 8 MeshBlocks
of 16^3, t = 0.5) passes the size check; the NRFIELD dump is NRFIELD1, t = 4.29, 32^3, no
trailing bytes. PASSED.

## Mechanism of the 7-step lag (source reading after the run)

`athenak/src/z4c/z4c_tasks.cpp`: `InitRecvWeyl` is queued at Task_Start and, at the last RK
stage, sets `last_output_time = time` when `time >= last_output_time + waveform_dt`;
`CalcWeylScalar` runs at Task_End of the same step when `time == last_output_time`.
`athenak/src/driver/driver.cpp` line 600 increments `pmesh->time` only after all stage task lists,
so the Weyl scalar is computed from the state at t + dt while labelled t. The mesh output written
at the next output time t_n = t + waveform_dt stores this array: lag waveform_dt - dt = 7 steps,
as measured (a pure "previous waveform time" lag would have been 8 steps; the run distinguishes
the two). Whether the extracted waveforms (CalcWaveForm, same Task_End) carry the one-step offset
was not tested [TO VERIFY by core].

## Scouting prediction: diagnostics on two full-GR cosmology runs (written before cosmo_demo.py ran)

Input: `runs/cosmo/dav_c256_n128_t` (quadratic cloud) and `runs/cosmo/dav_c256_n128_pcs4bt`
(cubic cloud, fourth-order compensation), 128^3, one particle per cell, 14 restart dumps each
from a = 1 to ~1000 (cosmo/TESTLOG.md, C5). All [JUDGEMENT]:
(1) the reader assembles the dumps; a from <chi>^(-1/2) runs from 1 to about 1000;
(2) the TT part of the metric is far below the non-TT part: rms h^TT / rms(non-TT) <= 1e-2 at
    all times (induced tensor modes are second order in the potential, ~7e-5 at the start);
(3) rho_GW / rho_bar is tiny (< 1e-6) and grows as structure forms;
(4) if the TT power at the highest k is particle noise, the two deposit schemes differ there by
    more than a factor 2, while at low k they agree within 20 percent; if they agree at all k,
    the TT content is not deposit noise;
(5) at the last dump B and Lambda E are small against E (rms ratio < 0.1): the Weyl field of a
    matter-dominated box is mostly the Coulomb-type tidal part.

Run B-emd-gw-20261115-120531-40a3597 FAILED at the first dump (ZeroDivisionError): the initial
data of the cosmology runs are conformally flat, tilde gamma = delta exactly, so h and its non-TT
part are zero at a = 1. Guarded (ratio recorded as null) and rerun.
