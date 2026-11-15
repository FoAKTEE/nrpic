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
