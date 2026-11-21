# VERIFIER (verifier3): G1 criterion 1 of Track B (tests F and X) and the spatial-gauge piece

Independent verifier of B-emd-gw, wave 3 round 1 (2026-11-20; two sessions, cut at 14:35 and
resumed at 18:56 PST). I did not produce the runs I check. I derived the exact solutions,
wrote my own readers, TT projection and Weyl/Psi_4 code (`scripts/diag.py`, `exact.py`;
nothing imported from gw_diag, waves/wlib or first_source/fslib), measured the raw dumps,
committed my numbers (commits b2e3effe, 483924b9), and only then read `waves/README.md`
'Results' and 'Open' (JOURNAL entry 10). Labels: [VERIFIED] = measured or derived and
checked by me in the run named; [JUDGEMENT] = my inference; [BACKGROUND] = standard fact.

## 1. What was checked, and how

| Step | How | Run ids (all registered, package `stage/G1/verifier3`) |
|---|---|---|
| V1 exact solutions | (F) linear TT plane wave of `z4c_linear_wave` (core/requests-b) in ADM/Z4c variables; (X) tensor mode on Einstein-de Sitter in the code's gauge (a = (1 + t/2)^2, alpha = a, zero shift): T'' + (4/(t+2)) T' + k^2 T = 0, T = c1 j1(x)/x + c2 y1(x)/x, x = k (t+2), T(0) = 0, T'(0) = 1; Weyl parts E, B to first order. Sympy residuals, ODE integration (DOP853), the generator's polarization tensors against my basis | B-20261120-222342-8cda367 (failed attempt B-20261120-222232-3d7d57e) |
| V2 readers and diagnostics | bin reader (single and double, header checks, re-blocked and truncated files), TT projection, Weyl E/B and fixed-direction Psi_4 tested on analytic flat and FLRW fields and on the initial dumps | B-20261120-222822-e26afae |
| V3 measurement | all 337 dumps of F (N = 16, 32, 48, 64) and X (N = 16, 32, 48, 64, and 64 at x10): mode coefficients at +K of the TT route and of the Weyl route (spectral and sixth-order derivatives), background of X; errors against the exact solution, orders, plus/cross, x1/x10 | B-20261121-025826-80973e3 (measurement), B-20261121-030121-58fe5dc (summary), B-20261121-030542-b2e3eff (supplement), B-20261121-030848-59f89b5 (classification numbers, own F predictor); failed: B-20261121-025612-ed4a875 (my shell timeout), B-20261121-030110-52ae004 (key sort) |
| V4 gauge piece | own derivation (plain and conformal metric), exact pure-gauge test, term-by-term comparison with `first_source/fslib/gauge.py`, recomputation from the raw scan dumps, TT energies | B-20261121-031220-8b9c4d7 (test), B-20261121-031808-3ef8c39 (scan), B-20261121-031833-c0ec479 (energies) |

Error measure: complex amplitude of each polarization at +K. F: Z = 2i c(K) of h (h alone),
and the forward combination Z_F = (Z_h + i Z_h'/w)/2 (the README's W = P + i P'/|k|); X:
Z = H + i H'/k with H = 2 c(K). Amplitude error |Z|/|Z_ex| - 1, phase error arg(Z/Z_ex)
(positive = lag). Figures: `figs/v3_*.png` (all looked at).

## 2. My numbers

Test F (k = 2 pi (1,1,1), amplitudes 1e-6 and 5e-7, phase 1 rad, four periods), forward
combination at the last dump [VERIFIED, B-20261121-030848-59f89b5; the h-alone values at the
last dump are the same, B-20261121-030121-58fe5dc]:

| N | TT amplitude | TT phase | FD6-Weyl amplitude | my predictor (amp, phase) | TT vs FD6 Weyl | TT vs spectral Psi_4 (forward) | TT (h alone) vs spectral Psi_4, max over t |
|---|---|---|---|---|---|---|---|
| 16 | -1.409e-4 | 2.531e-4 | -1.791e-4 | -1.409e-4, 2.531e-4 | 3.81e-5 | 6.4e-11 | 3.19e-6 |
| 32 | -1.717e-6 | 1.218e-5 | -2.327e-6 | -1.718e-6, 1.217e-5 | 6.09e-7 | 6.4e-11 | 5.08e-8 |
| 48 | -1.574e-7 | 2.273e-6 | -2.112e-7 | -1.576e-7, 2.270e-6 | 5.38e-8 | 6.4e-11 | 4.44e-9 |
| 64 | -3.101e-8 | 7.067e-7 | -4.065e-8 | -3.167e-8, 7.034e-7 | 9.64e-9 | 6.4e-11 | 1.02e-9 |

- Orders (16-32, 32-48, 48-64): amplitude 6.36, 5.89, 5.65; phase 4.38, 4.14, 4.06; TT vs FD6
  Weyl 5.97, 5.99, 5.98.
- My predictor: sixth-order second-derivative symbol, Kreiss-Oliger rate 0.5 sum sin^8(theta/2)/h,
  RK4 amplification with the cycle counts of the dumps; measured/predicted 1.000, 1.000, 0.998,
  0.979 (amplitude) and 1.000, 1.000, 1.001, 1.005 (phase).
- TT (h alone) and Psi_4 differ by |delta sin(w t)|, delta = theta^6/1120 (theta = 2 pi/N),
  the backward discrete wave that the continuum initial data excite; measured maximum over
  delta: 0.999, 0.999, 0.992, 1.28 (N64: round-off floor 4.7e-10)
  [VERIFIED, B-20261121-030542-b2e3eff, `figs/v3_F_diag_diff.png`].
- Plus and cross: forward Z_x/Z_+ = 0.5 e^{i} to <= 1.03e-9 (modulus), 1.08e-9 (argument) over
  all dumps and N. At t = 0 the TT amplitudes equal the exact ones to 6.0e-12 (+) and 2.5e-11
  (x) at N16 (<= 1.1e-11 at N >= 32).
- Non-TT part of gt - delta: 1.44e-4 of the TT part at t = 2.31 at every N, growing as t^2 at
  late times (fitted exponent 2.000 over the second half); 99.9997 % of it at k = 0, a uniform
  traceless shear with equal off-diagonal entries 6.58e-11, i.e. proportional to TF(khat khat).
  TT content outside +-K <= 1.3e-9.

Test X (EdS, side 4, k = (pi/2)(1,1,0), eps_+ = 2e-6, eps_x = 1e-6, t = 0..10), last dump
[VERIFIED, B-20261121-030121-58fe5dc]:

| N | TT amp + | TT amp x | TT phase + | TT phase x | FD6-Weyl amp + / phase + | TT vs FD6 Weyl (max over t) | TT vs spectral Weyl (max) |
|---|---|---|---|---|---|---|---|
| 16 | -7.048e-5 | -7.048e-5 | 8.304e-5 | 8.304e-5 | -9.58e-5 / 8.21e-5 | 5.13e-5 | 1.91e-8 |
| 32 | 1.3166e-6 | 1.3169e-6 | 3.089e-6 | 3.065e-6 | 9.33e-7 / 3.07e-6 | 8.20e-7 | 2.23e-8 |
| 48 | 4.2346e-7 | 4.2498e-7 | 6.478e-7 | 5.880e-7 | 4.12e-7 / 6.46e-7 | 7.22e-8 | 2.41e-8 |
| 64 | 1.3775e-7 | 1.3989e-7 | 3.854e-7 | 2.762e-7 | 1.54e-7 / 3.84e-7 | 1.66e-8 | 2.30e-8 |
| 64, x10 | 1.3979e-7 | 1.4007e-7 | 2.895e-7 | 2.786e-7 | 1.57e-7 / 2.88e-7 | 1.68e-8 | 2.31e-8 |

- Background: max |a_num/a_ex - 1| = 5.09e-8, 4.30e-8, 3.72e-8, 3.22e-8 (x10: 3.24e-8); alpha
  <= 7e-8, trK <= 3.4e-8; chi uniform to 4e-15; Theta <= 3.6e-9.
- Steps (from the dump cycles): dt = 0.0106 near t = 0 at every N (expansion limit
  0.01 (1 + t/2)), then h/4 from t = 1.1 (N64), 2.1 (N48), 4.2 (N32), never at N16.
- The amplitude error changes sign (a gain) from N = 32 on and converges with orders 2.8 and
  3.9; the gain appears after the step has become h/4 (at t ~ 2.2 for N48 and N64, t ~ 4 for
  N32) and is the same for both polarizations and both amplitudes.
- Plus/cross: the argument of Z_x/Z_+ deviates by 4.0e-9, 2.44e-8, 5.98e-8, 1.09e-7 (N = 16..64)
  and by 1.09e-8 at x10: ten times smaller relative error at ten times the amplitude, i.e. a
  fixed absolute error ~2e-13 in the components that carry e+ (rounding). Moduli agree to
  <= 2.1e-9 (x1) and 2.8e-10 (x10).
- TT vs spectral Weyl: N- and amplitude-independent 2e-8, following the zeros of the mode and,
  at late times, 0.6-0.7 of |calH_num/calH - 1| (my Weyl inversion uses calH = -alpha K/3 of the numerical
  background) [VERIFIED, `figs/v3_X_diag_diff.png`].

## 3. Verdicts on the claims of waves/README.md (Results and Open) about F and X

| # | Claim (README) | Their number | Mine | Verdict |
|---|---|---|---|---|
| F1 | TT amplitude and phase, N = 16..64 | -1.409e-4/2.531e-4 ... -3.10e-8/7.067e-7 | identical to the printed digits | CONFIRMED |
| F2 | Weyl-6 amplitude, phase | -1.716e-4, -2.208e-6, -2.006e-7, -3.87e-8; phase = TT | -1.791e-4, -2.327e-6, -2.112e-7, -4.065e-8; phase = TT | CONFIRMED IN PART: phases equal; amplitudes 4-5 % apart, a property of the FD6 construction of the curvature (mine: first derivatives applied twice) [JUDGEMENT] |
| F3 | predicted amplitude, phase (symbol + integrator) | -1.409e-4, 2.531e-4; ...; -3.17e-8, 7.034e-7 | my own predictor gives the same digits | CONFIRMED |
| F4 | Weyl-6 vs TT, orders 5.97, 5.94, 5.74 | 3.07e-5, 4.91e-7, 4.42e-8, 8.47e-9 | 3.81e-5, 6.09e-7, 5.38e-8, 9.64e-9; orders 5.97, 5.99, 5.98 | CONFIRMED IN PART: sixth order yes; level depends on the stencil (+14..24 %) |
| F5 | spectral Weyl vs TT | 1.2e-11 at every N | 6.0-6.4e-11 (forward combination); with h alone up to 3.2e-6 (N16) | NOT CONFIRMED AS WORDED: holds for the forward combination only, and at 6e-11 in my evaluation; say "forward combination" |
| F6 | local orders amplitude 6.36, 5.89, 5.65; phase 4.38, 4.14, 4.06 | as left | 6.36, 5.89, 5.65; 4.38, 4.14, 4.06 | CONFIRMED |
| F7 | cross has the same errors; W_x/W_+ = 0.5 e^{i} to <= 1.1e-9 at every N and time | <= 1.1e-9 | <= 1.03e-9 (modulus), 1.08e-9 (argument) | CONFIRMED; "scales as 1/A" not checked |
| F8 | backward part oscillates between 0 and \|1 - w_h/k\|, maxima 3.2e-6, 5.1e-8, 4.5e-9, 9.7e-10; continuum data excite the backward semi-discrete mode | as left | 3.19e-6, 5.08e-8, 4.44e-9, 9.7e-10 (backward fraction); equals theta^6/1120 sin(w t) to 1 % at N <= 48 | CONFIRMED |
| F9 | at t = 0 the TT amplitudes equal the generator's to 6e-12; its e+, ex are gw_diag's basis | 6e-12 | 6.0e-12 (+), 2.5e-11 (x, N16), <= 1.1e-11 (N >= 32); generator = (theta-hat, phi-hat) basis to 2.2e-16 (V1) | CONFIRMED IN PART (the cross polarization at N16 is at 2.5e-11) |
| X1 | TT amplitude/phase table, both polarizations | + amp 1.324e-6, 4.362e-7, 1.538e-7 at N = 32, 48, 64; all else as mine | + amp 1.3166e-6, 4.2346e-7, 1.3775e-7; x and phases identical to the printed digits | CONFIRMED except the plus amplitude at N = 48 and 64: NOT CONFIRMED AS WORDED (3 % and 12 % above mine; my plus equals the cross to <= 2e-9 and the x10 value 1.40e-7; [JUDGEMENT] rounding in their processing of the diagonal components) |
| X2 | Weyl-6 amplitude, phase (+) | -9.58e-5 / 8.13e-5 ... 1.70e-7 / 3.83e-7 | -9.58e-5 / 8.21e-5 ... 1.54e-7 / 3.84e-7 | CONFIRMED IN PART (stencil-dependent levels; phases within 1 %) |
| X3 | Weyl-6 vs TT, sixth order (5.97, 5.95) | 3.13e-5, 5.01e-7, 4.50e-8, 1.66e-8 | 5.13e-5, 8.2e-7, 7.2e-8, 1.66e-8 (max over t; final 2.54e-5, 3.84e-7, 1.19e-8, 1.66e-8); orders 5.97, 6.0 | CONFIRMED IN PART (order yes, level stencil-dependent) |
| X4 | spectral Weyl vs TT | 1.9e-8, 2.2e-8, 2.4e-8, 2.3e-8 | 1.91e-8, 2.23e-8, 2.41e-8, 2.30e-8; x10 2.31e-8 | CONFIRMED |
| X5 | rk4 is RK4()4[2S] (Ketcheson 2010, driver.cpp 145-176); the 2S predictor reproduces the cross errors to <= 0.5 % and the background error 5.1e-8, 4.3e-8, 3.7e-8, 3.2e-8 to two digits | as left | driver.cpp lines 145-176 say so; my measured cross values equal their predicted column to every printed digit; background 5.09e-8, 4.30e-8, 3.72e-8, 3.22e-8 | CONFIRMED IN PART: integrator and measured side confirmed; the 2S predictor itself not rebuilt |
| X6 | early steps limited to 0.01/calH whatever N; from N = 32 on the errors are dominated by time integration and follow no single power of N | as left | step sequence confirmed from the dump cycles; amplitude orders 2.8 and 3.9; the gain starts where dt becomes h/4 | CONFIRMED IN PART (the attribution is consistent; no step-split run was checked) |
| X7 | plus/cross argument 4.5e-9, 2.4e-8, 6.0e-8, 1.1e-7, in the plus polarization, grows with N, ~1/A [JUDGEMENT: rounding]; x10 check pending | as left | 4.0e-9, 2.44e-8, 5.98e-8, 1.09e-7; x10 at N64: 1.09e-8 | CONFIRMED, and the rounding judgement is now supported by the x10 run (the relative error falls tenfold) |
| X8 | the 2e-8 spectral offset comes from the background error through calH h' [JUDGEMENT] | 3e-8 to 7e-8 background | offset tracks \|calH_num/calH - 1\| at 0.6-0.7 of it, at every N and A | CONFIRMED IN PART (consistent in size and time dependence; not proven) |
| N1 | F non-TT grows as t^2 to 1.44e-4 at every N, proportional to A; second-order backreaction | 1.44e-4 | 1.44e-4 at every N; exponent 2.000 late (1.87 overall); a k = 0 traceless shear proportional to TF(khat khat) | CONFIRMED IN PART (proportionality to A not checked; the k = 0 structure supports the reading) |
| N2 | TT content outside +-k <= 1.3e-9 | 1.3e-9 | 1.3e-9 | CONFIRMED |
| N3 | X non-TT 3.1e-5 of the mode envelope at t = 10, proportional to A | 3.1e-5 | different normalization (5.6e-4 of the TT rms at x1, 5.6e-3 at x10) | proportionality CONFIRMED; the level not checked |
| N4 | X shift stays zero; Hamiltonian-constraint norm 9.0e-14 | as left | not measured | NOT CHECKED |
| A1 | amplitude scan at N = 16 (x10, x1/10): errors independent of A to <= 6e-4 | as left | runs not in my artefacts; at N64 (X) x1/x10 amplitudes agree to 1.5 % (+) and 0.2 % (x) | NOT CHECKED at N16 |
| C | criterion paragraph: difference 1e-11 (F) and 2e-8 (X) with spectral derivatives; errors = prediction to <= 2 % (F) and <= 0.5 % (X, cross; plus at N <= 32); plus of X at N >= 48 off by up to 39 % of 4e-7 rad | as left | 6e-11 (F, forward), 2.3e-8 (X); F ratios 0.979-1.005; X plus phase at N64 39.5 % above the cross | CONFIRMED IN PART: "1e-11" should be "6e-11 or less, for the forward combination"; the 39 % is a phase statement (the plus amplitude agrees with the cross in my measurement) |

Open items of the README: the x10 card check (run B-20261119-155758-458cf17) is analysed here
(X7, x1 vs x10); the space/time split of X and the direction (1,2,0) were not in my artefacts.

## 4. G1 criterion 1: "the two diagnostics agree on analytic linear waves"

Holds for both set-ups [VERIFIED for the numbers; the level statements are mine]:
- F (flat, oblique, elliptic): the TT and Psi_4 diagnostics give the same amplitude and phase of
  both polarizations to <= 6.4e-11 relative when the TT route uses its forward combination,
  and to theta^6/1120 (3.2e-6 at N = 16, 8e-10 at N = 64) when it uses h alone, which then
  also carries the backward discrete wave. Against the exact wave both have the same errors,
  -1.4e-4 / 2.5e-4 rad at N = 16 down to -3.1e-8 / 7.1e-7 rad at N = 64, converging at the
  orders of the code's operators and equal to a symbol-plus-RK4 prediction to <= 2.1 %.
  Evaluated with sixth-order differences the Weyl route differs by its own truncation
  (3.8e-5 at N = 16, sixth order).
- X (expanding box, cosmological gauge): the two diagnostics agree to 2.4e-8 (spectral) at
  every N and amplitude, and to the sixth-order truncation of the Weyl evaluation otherwise;
  against the exact tensor mode both are within 1e-4 (N = 16) and 4e-7 (N = 64) in amplitude
  and phase, both polarizations, with a rounding share of 1.1e-7 rad in the plus phase at
  N = 64 that a tenfold amplitude removes.

## 5. V4: the spatial-gauge piece

**Derivation** (JOURNAL entry 12, before any reading of fslib). Both scan runs use the lapse
condition along the normal observers (the second-gauge run sets `lapse_advect = 1`), so they
share the foliation and differ on each slice by a spatial map X = x + zeta(x), zeta = int beta dt
at first order. For h = gamma/a^2 - delta, Lambda h_new = Lambda h_old + G + O(3) with
G = Lambda[L_zeta h_old + d zeta . d zeta^T] = Lambda[L_zeta hbar] (hbar the mean of the two
metrics); for the conformal metric gt = det(gamma)^(-1/3) gamma (a density of weight -2/3)
Gt = Lambda[L_zeta ht_old + d zeta . d zeta^T - (2/3) div zeta (ht_old + 2 d_(i zeta_j))]
= Lambda[L_zeta htbar - (2/3) div zeta htbar].

**Exact pure-gauge test** [VERIFIED, B-20261121-031220-8b9c4d7, `figs/v4_gauge_test.png`]: on
32^3, random first-order metric and displacement scaled by eps, exact transform: Lambda h
changes as eps^2 (slope 2.000) and Lambda h - G as eps^3 (3.000), plain and conformal, one-sided
and symmetric forms; on conformal data the plain formula (no density term) leaves 74 % of the
change (slope 2): the -(2/3) div zeta term is needed for gt. zeta from the metric difference is
exact to O(eps) and gives the same eps^3 residual.

**fslib/gauge.py** (read after the test): `gauge_piece_total` = G + G_x with
G = Lambda[M^T M - (2/3)(div xi)(M + M^T)], G_x = Lambda[M^T A + A M - (2/3)(tr M) A + (xi.grad) A],
A = Lambda h + h0, xi from the traceless non-TT part of h. Term by term this is my one-sided
conformal formula with the reference coordinates chosen spatially transverse (h_old = A,
zeta = xi), and its inversion formula equals mine [VERIFIED by derivation and the exact test].
It refers each gauge to its own transverse coordinates; its products are dealiased (mine on the
N grid and, as a check, on a 2N grid: no difference above 1e-12 at m = (1,1,0)).

**Recomputation from the raw scan dumps** (eps = 1, c_+ of Lambda(gt/det^(1/3) - delta) at
m = (1,1,0), divided by |c_+^zs|; interpolated to t(a) between bin dumps) [VERIFIED,
B-20261121-031808-3ef8c39, `figs/v4_scan.png`]:

| a | raw, 64^3 | after G, zeta = int beta (direct) | after G, zeta from the metric difference | after G_tot in each gauge (my implementation of the fslib method) | raw, 32^3 | after G direct, 32^3 | float32 floor |
|---|---|---|---|---|---|---|---|
| 5 | 1.26e-3 | 2.31e-5 | 2.33e-5 | 2.06e-5 | 1.21e-3 | 3.28e-5 | 4.7e-6 |
| 10 | 3.26e-3 | 4.15e-5 | 4.56e-5 | 6.92e-5 | 3.26e-3 | 5.10e-5 | 7.0e-6 |
| 20 | 1.39e-2 | 4.81e-5 | 8.82e-5 | 2.88e-4 | 1.39e-2 | 5.8e-6 | 4.1e-6 |
| 40 | 4.31e-2 | 6.57e-4 | 9.46e-4 | 2.62e-3 | 4.29e-2 | 7.81e-4 | 4.0e-6 |
| 60 | 8.74e-2 | 2.71e-3 | 3.62e-3 | 9.13e-3 | 8.46e-2 | 4.95e-3 | 2.6e-6 |

- The two displacement routes agree (zeta from the metric difference = int beta dt to 2e-4 ..
  5e-3, the size of the first-order non-TT metric), and the transverse displacements satisfy
  xi_gd - xi_zs = zeta to the same level: the two runs are related by a spatial map at first
  order, as the derivation assumes.
- The gauge piece removes the difference by 55x, 79x, 289x, 66x, 32x (direct route, 64^3);
  G_tot in each gauge by 61x, 47x, 48x, 16x, 9.6x. The residual depends weakly on resolution
  (64^3 over 32^3: 0.55 .. 0.8) and lies above the float32 rounding floor of the bin dumps.
- TT energies [VERIFIED, B-20261121-031833-c0ec479, `figs/v4_energy.png`]: rho_kin/rho_grad of the
  TT part (gw_diag definitions) over all dumps with a >= 12: largest 8.82e-3 (eps = 1, zero shift,
  a = 13.0), 8.59e-3 (eps = 0.1, a = 99), 8.0e-3 (eps = 0.3), 1.80e-2 (eps = 1, Gamma driver,
  a = 84); 32^3: 8.85e-3 and 1.35e-2. The TT part is nearly static (c_+ = 1.5e-5 .. 2.0e-5 from
  a = 5 to 60), so kinetic << gradient; a TT wave would give a ratio near one.

**Verdicts on the ledger rows** (note/tables/ledger.tex, block "Spatial gauge of the
projection", lines 114-125, and the energy row, line 101; the working copy and HEAD agree there):

| Row | Ledger | Mine | Verdict |
|---|---|---|---|
| 115 | exact pure-gauge data: slopes of Lambda h and Lambda h - G: 2, 3; with a slicing change Lambda h - G: 2 | 2.000, 3.000 (plain and conformal) | CONFIRMED for the spatial part; the slicing-change slope NOT CHECKED |
| 116 | largest \|G_tot/c_+\| for a <= 20, zero shift, eps = 0.1, 0.3, 1: 0.0055, 0.00596, 0.0112 | eps = 1: 1.0e-3, 2.4e-3, 0.0112 at a = 5, 10, 20 | CONFIRMED for eps = 1 (sampled at three a only); eps = 0.1, 0.3 NOT CHECKED |
| 117 | the same at a = 40: 0.0163, 0.0185, 0.0397 | eps = 1: 0.0397 | CONFIRMED for eps = 1 |
| 118 | gauge difference of c_+ over \|s\|, as projected, a = 5..60: 0.00121, 0.0036, 0.0147, 0.0487, 0.115 | over \|c_+^zs\|: 1.26e-3, 3.26e-3, 1.39e-2, 4.31e-2, 8.74e-2 | CONFIRMED IN PART: same size and growth; the normalization differs (\|s\| is not \|c_+^zs\|: my/theirs 1.04, 0.91, 0.95, 0.89, 0.76) |
| 119 | the same after G_tot in each gauge: 1.95e-5, 7.64e-5, 3.05e-4, 2.96e-3, 0.012 | 2.06e-5, 6.92e-5, 2.88e-4, 2.62e-3, 9.13e-3; after/before 0.0164, 0.0212, 0.0207, 0.0608, 0.1045 against the ledger's 0.0161, 0.0212, 0.0207, 0.0608, 0.1043 | CONFIRMED (reduction factors to 1 %; normalization as row 118). But the direct map leaves 1-6x less (4.8e-5 at a = 20, 2.7e-3 at a = 60): at a >= 10 much of the ledger's residual is the third-order remainder of the transverse-reference method, not a property of the code [JUDGEMENT] |
| 120 | median corrected/projected where projected > 1e-3 \|s\|: 0.084, 0.0928; share 0.89 | my five a: 0.016 .. 0.10 (median 0.021) | NOT CHECKED (all dumps not processed) |
| 121 | median with the quadratic piece alone: 5.24, 5.32 | not computed | NOT CHECKED |
| 122 | departure from s g at a = 10, 20 | not computed (s, g not defined in what I read) | NOT CHECKED |
| 123 | rms non-TT zero shift over driven shift, a >= 10: 16.2, 52.2 | not computed | NOT CHECKED |
| 124 | median relative gauge difference, a <= 64: magnetic Weyl 0.00121, flat TT 0.0139 | not computed | NOT CHECKED |
| 125 | first-order slicing of the three-wave runs | other runs | NOT CHECKED |
| 101 | largest kinetic over gradient energy of the TT part for a >= 12: eps = 0.1, 1: 0.00857, 0.00821 | over all bin dumps: 0.00859 (a = 99), 0.00882 (a = 13.0); the ledger's values are exactly mine at the dumps nearest t = 5, 6, ..., 21 (the restart cadence) | NOT CONFIRMED AS WORDED for eps = 1 (the maximum over a >= 12 is 0.0088, at a = 13, between the sampled times); eps = 0.1 CONFIRMED; the conclusion (kinetic << gradient) holds, also for the driven shift (0.018) |

## 6. The three weakest points of the evidence for criterion 1

1. The two diagnostics are not independent measurements: both are post-processing of the same
   dumped metric and curvature, and at linear order with spectral derivatives the Weyl route is
   an algebraic re-expression of the TT route (E_+ = k^2 h_+/2 + calH h'_+/2, B ~ k h'/2; JOURNAL
   entry 4). Their agreement checks the analysis chain (projection, basis, signs, inversion),
   not the evolution; what checks the evolution is the comparison with the exact solution and
   the predictor. AthenaK's own Psi_4 output (radial triad about the origin) was not used.
2. Narrow coverage of the waves: one direction per test ((1,1,1) and (1,1,0), both with a
   vanishing discrete divergence), one wavelength per box, amplitudes 1e-6 (linear regime),
   and in X a homogeneous lattice without scalar perturbations. The science runs have scalar
   tidal fields, for which Psi_4 is not a clean wave measure (gw_diag README), shift in the
   second gauge, and power up to the Nyquist scale; criterion 1 says nothing about that regime.
3. The X error budget is not closed: from N = 32 on the amplitude error is a gain that
   converges at orders 2.8-3.9 and starts when the step becomes h/4; the README attributes it
   to the 2S integrator, which I confirmed only on the measured side. At N >= 48 the plus
   polarization is at the rounding floor of the processing (my and the README's plus amplitudes
   differ by 1.4e-8 relative), so the N = 64 X numbers carry an analysis-dependent part.

## 7. What was not checked

- The README's 2S predictor for X (rebuilt neither the integrator nor the coupled background).
- The amplitude scan at N = 16 (runs B-20261119-153637-02c822f and analyses), the A-scaling of
  the F non-TT norm, the X shift and Hamiltonian-constraint norms, the X non-TT level in the
  README's normalization.
- Test F2 (direction (1,2,0)) and the X step-split run of round 1 (other helpers).
- AthenaK's built-in Weyl/Psi_4 output.
- V4: the slicing-change part of the pure-gauge test; ledger rows 120-125; eps = 0.1 and 0.3 in
  rows 116-117; the gauge comparison at every dump (I used a = 5, 10, 20, 40, 60 only); the
  restart (double-precision) dumps of the scan (I used the float32 bin dumps and estimated their
  rounding floor); running fslib's own code (compared by formula and by my implementation of
  its method, not executed).

## 8. Requests

To the lead of B-emd-gw (rewordings; nothing blocks G1 criterion 1):
1. waves/README F5 and the criterion paragraph: "spectral Weyl vs TT 1.2e-11" holds only for the
   forward combination W = P + i P'/|k| (my evaluation: 6.4e-11); with h alone the two differ by
   the backward discrete wave theta^6/1120 |sin w t| (3.2e-6 at N = 16). Say so.
2. waves/README X1: the plus amplitudes at N = 48, 64 (4.362e-7, 1.538e-7) are above the cross
   values by 1.1e-8 and 1.4e-8 relative; on the same dumps I get 4.2346e-7 and 1.3775e-7, equal
   to the cross to 2e-9, and the x10 run gives 1.40e-7 for both. Flag them as rounding-limited or
   replace them; "deviates by up to 39 %" is a phase statement.
3. waves/README F2, F4, X2, X3: the Weyl-6 numbers depend on how the sixth-order curvature is
   built (mine differs by 4-5 % in amplitude and 14-24 % in the TT difference); state the
   construction next to the numbers.
4. ledger row 101: give 0.0088 (eps = 1, a = 13.0, all dumps) or state that the maximum is over
   the restart cadence; consider adding the driven-shift value 0.018 (a = 84).
5. ledger rows 118-119: define s next to the rows; consider a row with the direct
   zero-shift-to-driven-shift map (residual 2.3e-5, 4.2e-5, 4.8e-5, 6.6e-4, 2.7e-3 at
   a = 5..60, 64^3), which shows that most of the G_tot residual at a >= 10 is the method.
6. Future scans: the bin output of the scan is float32; at a <= 10 it puts a floor of ~5e-6
   (relative to c_+) under gauge differences. Double-precision bin output (as in test X) removes it.

To core: none.
