# Journal of the package E-pre-1 (reproduction specification)

Owner: E-stoch-inf (helper for E-pre-1). Entries are appended; nothing is rewritten.
Labels as in the brief: [VERIFIED], [BACKGROUND], [JUDGEMENT], [TO VERIFY].

## 2026-11-15 12:20 UTC: sources read

Fetched with `harness/bin/nrpic-fetch-arxiv` (sources under `kb-data/raw/arxiv/<id>/<v>/src`):
2401.08530 v2, 2512.14649 v2, 2610.32592 v1 (thesis), 2502.06783 v3, 2606.14853 v2.
Read closely: 2512.14649 (whole), 2502.06783 (whole), 2606.14853 (whole), thesis chapters
`chap_SINR.tex` (whole), `chap_SIGR.tex` 249-538, `chap_QCl.tex` 317-468, `appendix.tex`
394-642. 2401.08530 read by grep for the source terms and gauge families (section 3 of
SPEC.md says what was taken from it).

## 2026-11-15 12:25 UTC: predictions before the reference computations (run ids below)

Test T1, background of the two test cases from the stated parameters only.
- T1a quadratic (potential-position fixing, eps1 = 0.01, eps2 = -0.02, H0 = 1e-5 Mpl at N0,
  field rolling towards positive phi). Prediction: eps2 (Launay sign, eps2 = -dln eps1/dN)
  equals -0.02 at N0 to 1e-6; eps1 rises monotonically, to between 0.012 and 0.015 at
  N0 + 13 (= N_f, Table I of 2512.14649: N* - N0 ~ 5, N_f - N* ~ 8); H falls by a factor
  between 0.80 and 0.92 over the 13 e-folds; inflation does not end. Refuted if eps2(N0)
  differs from -0.02 by more than 1e-4, or inflation ends before N0 + 13.
- T1b inflection (Lambda = 1.86e-6, v = 0.198 Mpl, phi0 = -1.2 Mpl, H0 fixing with the
  slow-roll velocity read as dphi/dN = -Mpl^2 V'/V). Predictions taken from the text of
  2512.14649 lines 532-534, with simulation time cN = N - N* and N* = N0 + 3: the field
  reaches the nearly flat part at cN ~ 3; USR (eps2 > 3, peak near 6) from cN ~ 3.5 to
  cN ~ 8; afterwards slow roll with (eps1, eps2) ~ (0, -2.8e-2). H0 near 1e-5 Mpl (hand
  estimate 9.6e-6). The near inflection point lies at |phi| ~ 0.28 Mpl (2502.06783 line
  579). Refuted if no USR phase appears, if its onset is more than one e-fold from
  cN = 3.5, or if the late eps2 is not within a factor two of -2.8e-2. If refuted, the
  other reading of the initial velocity (dphi/dt instead of dphi/dN) is tried and both
  outcomes stay on record.

Test T2, freezing of super-horizon modes (linear reference for the criterion of
2606.14853), for the lattice modes of the N = 256, sigma = 1 set-up (k from k*_sigma to
64 k*_sigma).
- T2a quadratic, full Mukhanov-Sasaki equation: once a mode is three e-folds outside the
  horizon, |d ln Delta_R / dN| < 1e-3 per e-fold. Deformed equation (no metric
  perturbations, eq. 7 of 2606.14853): d ln Delta_R / dN = -4 eps1 within 25 percent,
  i.e. between -0.03 and -0.07 per e-fold. Final full spectrum: Delta_R within 20 percent
  of H_k^2 / (8 pi^2 eps1_k Mpl^2) evaluated at crossing, about 1.2e-10. Refuted if any
  of the three fails.
- T2b inflection: the full spectrum at N_f peaks between 1e-2 and 1 on the lattice modes
  (2512.14649 line 536 reports Delta[R] up to 0.1-1). The deformed spectrum differs from
  the full one by more than 10 percent for modes that left the horizon before the USR
  onset. Refuted if the peak lies outside [1e-2, 1] or the deformed spectrum agrees with
  the full one to 10 percent everywhere.
- T2c cross-check of the reference itself: the deformed equation solved in two forms
  (R with the extra mass term, and delta-phi on an unperturbed background) agrees to
  1e-6 relative. Refuted otherwise (then the reference has an error).

Test T3, normalisation of the random draw (appendix "Randomness with a power spectrum" of
2502.06783 and of the thesis). Prediction from my derivation: with the unnormalised
inverse transform IRFFTN and s_k = N^(-3/2) RFFTN(white noise), the field
f(x) = L^(-3/2) IRFFTN{f_k s_k} has a shell-averaged Delta = k^3 |f_k|^2 / (2 pi^2) equal
to the input within 3 / sqrt(M) per shell of M modes; the two prefactors printed in the
papers, dk^(3/2) and (dk / sqrt(2 pi))^(3/2), give powers off by (2 pi)^3 and (2 pi)^(3/2).
Refuted if the measured ratio for L^(-3/2) is not 1 within the stated scatter.

## 2026-11-15 12:50 UTC: change of plan for T1b, and a further prediction (T2d)

- The fallback reading of the initial velocity in T1b (dphi/dt = -Mpl^2 V'/V) is dropped
  before running: -Mpl^2 V'/V has the dimension of a mass, dphi/dt of a mass squared, so
  only dphi/dN = -Mpl^2 V'/V is consistent [JUDGEMENT]. Only that reading is run.
- A development run (scratch/E-stoch-inf/tmp/dev1, not a result) showed full-MS drifts of
  1e-3 to 2e-3 per e-fold for the higher sampled modes over [N_k + 3, N_f], i.e. above the
  1e-3 of prediction T2a. The outcome is recorded from the registered run below. Proposed
  cause: gradient corrections of order (k/aH)^2, which decay as exp(-2 dN) after crossing.
  T2d, prediction: for the eight lowest sampled modes of the quadratic case the full-MS
  drift fitted over [N_k + 5, N_k + 6] is smaller than the one over [N_k + 3, N_k + 4] by
  a factor below 0.1 (expected near exp(-4) = 0.02). Refuted if any ratio exceeds 0.1;
  then the drift has another origin (numerical, or the initial data) and the cause stays
  open.

## 2026-11-15 12:58 UTC: prediction for T4 (initial data against the linear constraints)

While writing SPEC.md section 6, re-deriving delta-Pi at t* in the geodesic gauge from
2502.06783 eqs. (14)-(16) gave an extra term -sqrt(2 eps1) Mpl H Psi_B compared with the
printed eq. (17) (it comes from dot(Phi^NR) = dot(Phi_B) - H dot(chi), dot(chi) = Psi_G -
Psi_B). Prediction (T4, symbolic, script ref/ic_constraint_check.py): with the re-derived
delta-Pi the linear Hamiltonian constraint of 2502.06783 eq. (9) vanishes identically, with
the printed one it leaves a first-order residual; the momentum constraint vanishes for both,
and delta-K = 3 (dot Phi_B + H Psi_B) equals 3 eps1 H (R - Phi_B). Refuted if the printed
form is the one that satisfies the Hamiltonian constraint (then my derivation is wrong), or
if neither does (then a convention is misread, e.g. the Laplacian or delta-rho).

## 2026-11-15 13:35 UTC: outcomes (runs registered under tracks/E-stoch-inf/runs/)

Runs: E-stoch-inf-20261115-122806-ef0d039 (T1, T2, T2c; identical to the development
run), -122934-9ac98d8 (T3), -123146-82d2fd4 (T4), -123236-2e87364 (figures and T2d; the
earlier figure run -123201-82d2fd4 differs only in a margin). Figures in `fig/`, looked at.

- T1a quadratic: PASSED. eps2(N0) = -0.0200000 (1e-11), eps1(N_f) = 0.01350, H(N_f)/H0 =
  0.860, inflation does not end; phi0 = -14.0950 Mpl, lambda = 1.50502e-12 (m = 1.73494e-6
  Mpl), H* = 9.48692e-6 Mpl. Against Fig. 1 of 2512.14649 (values read off the axes, about
  2 percent): eps1(N*) 1.111e-2 (read 1.11e-2), eps2(N*) -2.213e-2 (read -2.23e-2),
  V(N*) = 2.690e-2 in Mpl = 100 units (read 2.68e-2). fig/fig_background.png.
- T1b inflection: PASSED against the figure, the text's phase boundaries are loose.
  H0 = 9.5902e-6 Mpl (hand estimate 9.6e-6), H* = 9.3623e-6. USR (eps2 > 3) from
  cN = 2.53 to 6.55, eps2 max 6.000, eps1 min 9.72e-13 at cN = 8.33, late eps2 = -2.762e-2
  (text: -2.8e-2), the field ends at phi = -0.2798 Mpl where |V'| is smallest (text:
  inflection at |phi| ~ 0.28). The text's "USR from cN ~ 3.5 to ~ 8" is off by about one
  e-fold, but Fig. 1 of the paper shows eps2 crossing 3.2 at cN ~ 2.5 and ~ 6.45, eps1 peak
  2.4e-2 at ~ 1.6 (ours 2.408e-2 at 1.62), eps1 min ~ 0.98e-12 at ~ 8.4: the reconstruction
  matches the figure. V' does not change sign between phi0 and 0 (the "very shallow
  maximum" of the text, line 534, is not a maximum of V for these parameters; [TO VERIFY]
  what the authors meant).
- T2a quadratic: PARTLY FAILED as predicted. Final full spectrum / (H^2/(8 pi^2 eps1) at
  crossing) = 1.010 to 1.012 for all 25 sampled modes (passes). Deformed drift
  d ln Delta/dN = -0.0509 to -0.0552 per e-fold, -4 eps1 = -0.046 to -0.054 (passes).
  Full-MS drift over [N_k + 3, N_f]: -2.5e-4 to -1.9e-3 per e-fold; the prediction (below
  1e-3) FAILED for the 6 highest of the 23 fitted modes (19 dk <= k <= 45 dk), whose fit
  windows are short and start only three e-folds after crossing.
- T2d (cause of the T2a failure): PASSED. Ratio of the drift over [N_k+5, N_k+6] to the one
  over [N_k+3, N_k+4] = 0.0192 for all eight tested modes (exp(-4) = 0.0183): the residual
  drift is the (k/aH)^2 gradient correction, not a numerical error. fig/fig_drift.png.
  Consequence for the criterion: freezing is to be tested from N_k + 4 or later, or against
  the full MS solution instead of a constant.
- T2b inflection: MARGINAL FAIL / PARTLY FAILED. Full spectrum at N_f rises monotonically
  over the lattice range, reaching 1.017 at k = 64 dk (prediction: peak within [1e-2, 1];
  exceeded by 1.7 percent, and the maximum sits at the UV cutoff, not inside the range).
  Deformed/full at N_f: 8.40 at k = dk, 1.18 at 4 dk, 1.07 at 5.7 dk, 1.003 at 11.3 dk,
  1.0000 at 64 dk. Modes leaving the horizon less than about one e-fold before the USR
  onset differ by less than 10 percent, so the prediction "more than 10 percent for all
  modes that left before the onset" FAILED for 5.7 dk <= k <= 11.3 dk.
- T2c: PASSED. Deformed equation in R form vs delta-phi form: max relative difference
  1.5e-11 (quadratic), 5.2e-9 (inflection).
- T3: PASSED. L^(-3/2) IRFFTN{f_k s_k}: shell ratios 0.83 to 1.014 (lowest shell, 13
  modes, 8 draws: 0.83 +- 0.07; all shells within 3/sqrt(8 M)); overall 0.975. The two
  printed prefactors give 241.8 (expected (2 pi)^3 = 248.1) and 15.35 (expected
  (2 pi)^(3/2) = 15.75). fig/fig_norm.png.
- T4: PASSED. Hamiltonian residual with the printed delta-Pi of 2502.06783 eq. (17):
  4 eps1^2 H^3 a^2 k^-2 Rdot (first order in the perturbation); with the re-derived
  delta-Pi: 0. Momentum residual 0; 3 (dot Phi_B + H Psi_B) = 3 eps1 H (R - Phi_B)
  identically. The printed eq. (17) is therefore incomplete; their code must use the
  complete form since they report second-order Hamiltonian violations [JUDGEMENT].

## 2026-11-15 13:55 UTC: deliverables written; corrections to this journal

- SPEC.md, scope/SCOPE.md and README.md written from the sources and the runs above.
- Correction to the first entry: what was taken from 2401.08530 (source terms with "+ c.c.",
  constraints without sources, gauge families, BSSN form; lines 585-704 and 972-1031) is cited
  in SPEC sections 2.1, 2.2 and 9 under the key P0, not in a "section 3".
- Correction to the T1a outcome: at cN = 7.6, where the published figure ends, the reference has
  eps2 = -2.659e-2 and V = 2.234e-2 (Mpl = 100 units) against my readings -2.62e-2 and 2.22e-2;
  the tick labels of that figure are rounded to two digits, so "about 2 percent of the axis" was
  optimistic for these two points. SPEC section 6 states the differences.
- Not run: the unit conversion of SPEC 2.5, the window derivatives of SPEC 3 and the
  extraction factors of SPEC 9 E6 are hand derivations; the sixth-order dispersion numbers of
  A2 are arithmetic on the stencil coefficients. All are labelled [JUDGEMENT] in SPEC.md.
