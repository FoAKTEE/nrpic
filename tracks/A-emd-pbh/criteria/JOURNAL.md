# JOURNAL of package A-pre-2 (criteria), track A-emd-pbh

Append-only. Predictions are written before a test runs, outcomes after it.

## 2026-11-15  helper criteria  session 1

### Sources read (kb-data/raw/arxiv/<id>/<version>/src, fetched with nrpic-fetch-arxiv)

1609.01588 v2 apj_nonsphericalpbh.tex (all); 1707.03595 v4 Spin_PBH.tex 63-1440, 1762-1811;
2211.13950 v3 MD_threshold10.tex 80-788; 2507.18312 v3 Main.tex 60-648; 2508.10070 v1
main.tex 38-1000. Also 2609.14218 v1 MDPBH.tex 830-1000 (read only for its mapping
(e, p, mu) -> deformation eigenvalues at line 908 and its particle threshold at 1145), which
the brief names as the comparison for the threshold line.

### Predictions for the checks of `check_criteria.py` (written before the first run)

T1 (1609.01588, hoop)
- T1.1 Doroshkevich density (641-645) integrates to 1 (689-692) to better than 1e-5.
  Refuted if |integral - 1| > 1e-4.
- T1.2 E-bar from 1338 is 1.182 (1341) to 3 decimals; c = 0.05556 (764); bounds 0.01338 and
  0.1280 (771). Refuted if any differs in the printed digits.
- T1.3 Khlopov-Polnarev coefficient (926-931): my hand evaluation gives 27/(8 sqrt5 pi) x
  (1/30) x (10/9)^3 = 0.0220; the paper prints "0.02". Refuted if outside 0.015-0.025.
- T1.4 The exact double integral beta0(sigma)/sigma^5 tends to 0.0556 for sigma <= 1e-3
  (within 1 percent) and exceeds it for sigma >~ 0.01 (730, 874-882): ratio at sigma = 0.1
  above 1.1. Refuted if the small-sigma ratio is off by more than 1 percent or the ratio at
  0.1 is below 1.02.
- T1.5 Monte Carlo over Gaussian tensors (Doroshkevich law) agrees with the double integral
  at sigma = 0.3, 0.5, 1.0 within 3 standard errors. Refuted otherwise.
- T1.6 The curve looks like Fig. 1 of the paper (WsWide20160814.pdf, viewed, not copied):
  same shape, and values read off at sigma = 0.1 and 1 agree within the reading precision
  (a factor of about 1.5 on the log axis).

T2 (1707.03595, spin)
- T2.1 q_c coefficient sqrt(2/3)(5/2)^(7/6) = 2.38, printed as 2.4 (72).
- T2.2 Exponent coefficients 0.1474 and 0.004608 (1339, 1346) and prefactors 1.921e-7 and
  3.244e-14 (1338, 1345) follow from 1325-1329 with delta_th(2), delta_th(1) (958-960) to the
  printed digits. Refuted if any printed digit differs.
- T2.3 Mode of f_BH(2) with I = 1: 0.63 at sigma_H = 0.1 (1147); reaches 1 at sigma_H about
  0.04 (1150; my estimate 0.0405). Refuted if the mode at 0.1 is outside 0.60-0.66 or the
  crossing outside 0.035-0.045.
- T2.4 Numerical beta0(2) (1304-1308, I = 1) agrees with the semi-analytic 1338 within 20
  percent for sigma_H <= 0.005 and is within a factor 2 of P_ai for 0.02 <= sigma_H <= 0.2
  (1351-1358); numerical beta0(1) (q = sqrt2) agrees with 1345 within 20 percent for
  sigma_H <= 0.02 (1359-1362). Refuted if outside these bands.

T3 (2211.13950, velocity dispersion)
- T3.1 sigma_cr(mu=1, ln(kmin/k)=1) = e^-3, so ln sigma0 = -5 lies below and -2.5 above,
  as the caption of Fig. 2 states (517). Refuted otherwise.
- T3.2 The two Case boundaries (423-426) and the line sigma = (k/ktilde)^-4 meet at
  (delta^-1/2, delta^2) (468). Refuted if the numerical intersection differs.
- T3.3 delta_th(sigma0) jumps at sigma_cr exactly when mu ln(kmin/k) < 2 (569-571), for the
  five (mu, L) pairs of Fig. 3. Refuted if any pair behaves otherwise.
- T3.4 My delta_th(sigma0) curves look like Fig. 3 (thresholds.pdf, viewed).

T4 (2507.18312, profile statistics)
- T4.1 The exact top-hat LTB solution (211-214) gives R_max delta_m / r_m = 3/5 (304),
  a(t_max) delta_m = 3(6 pi)^(2/3)/20 = 1.0631 (276, 308) and R = 2M at b = 5 delta_m/3
  (316); its early-time density contrast is delta_m a (normalisation of delta_m). Refuted
  if any relation fails by more than 1e-6 relative (1e-2 for the linear limit at a delta =
  1e-3).
- T4.2 zeta(0)/delta_m = 5e/12 = 1.1326 for the Gaussian K (188, printed 1.13) by quadrature
  of 161.
- T4.3 a_rms = zeta^(7/4) = 0.018 at zeta_rms = 0.1, printed "~0.01" (637): agreement in
  order of magnitude only.

T5 (2508.10070, peak statistics)
- T5.1 The general pancake criterion (309-331) with a spherical region reproduces the
  1609.01588 h exactly (relative difference < 1e-10 on random samples).
- T5.2 My small-sigma closed form for the monochromatic spectrum gives beta = 1.08
  sigma-bar^5 (657) within 1 percent, i.e. 19 times 0.05556 (659).
- T5.3 The numerical monochromatic integral reproduces Table V (beta/sigma-bar^5 = 1.08,
  1.12, 1.51, 2.77, 0.67 at sigma* = 1e-5, 1e-3, 1e-2, 5e-2, 0.1) and Table IV (Mbar/M* =
  14.7, 14.7, 14.7, 15.5, 18.1) within 5 percent. Refuted if any differs by more.

### Outcome of the first two check runs (code at 5581665)

- Run A-emd-pbh-20261115-113223-5581665 (T3, T4): 7 of 7 passed. T4.1a: a(t_max) delta =
  1.0625 from both the formula 3(6 pi)^(2/3)/20 and the maximum of the exact LTB solution
  (relative difference 1e-14); my predicted "1.0631" was an arithmetic slip of mine, the
  paper prints "about 1.06". T3.4 (visual, thresholds.pdf of 2211.13950 viewed): all five
  lower branches and the upper branches of (1,1), (1/2,1), (2,1) coincide with the paper's
  curves at the values read off (e.g. 0.025, 0.011, 0.0023 at sigma0 = 1e-4; 2.4e-3 and
  3.3e-4 for (1,1) at 0.05 and 1). One difference: eq. 551-563 gives for (mu, L) = (1, 2) an
  upper branch from (0.0183, 0.0183) falling onto the (1,1) branch at 0.0498, which the
  paper's figure does not draw (it shows a dashed continuation of the lower branch instead).
  My reading of the geometry (non-formation triangle bounded by sigma = (k/k)^-4 and
  sigma = delta^(5/2) k/k, apex at the merge point) agrees with the equation, not the figure
  [JUDGEMENT].
- Run A-emd-pbh-20261115-113244-8e0363b (T1, T2, T5 quick): 13 of 22 passed. The double
  integral of 1609.01588 came out low by a factor sigma3^6: a bug of mine (the integrand was
  multiplied by s3^6 where the absorbed prefactor needs s3^-6). Direct evaluation at sigma =
  1 gives 0.13964, Monte Carlo 0.13966 +- 0.00017. Fixed in emd_criteria._beta0_tu; all
  failures of T1.4, T1.5, T2.4a, T2.4c came from it. Remaining genuine last-digit misses:
  T1.2b 0.05555 vs printed 0.05556 (my E-bar = 1.18174, paper "1.182"; c = 0.05556 needs
  E-bar = 1.18168, a 5e-5 relative difference) and T2.2d 3.248e-14 vs 3.244e-14. A diagnostic
  check T2.2e (prefactors with E-bar rounded to 1.182) is added to test whether the paper
  used the rounded value.
- With the fix: beta0(sigma)/(c sigma^5) - 1 = 6.75 sigma for sigma <= 1e-3 (1.0000068 at
  1e-6), so the exact integral tends to the semi-analytic coefficient of 1609.01588 App. B;
  ratio 2.02 at sigma = 0.1. Monochromatic peak integral at sigma* = 1e-3: beta/sigma-bar^5 =
  1.122, Mbar/M* = 14.697 (3 s of CPU).

### Predictions for `scan_disagreement.py` (written before its first run)

- S.1 Hoop threshold for a Lagrangian ball at p = 0: delta_th = 0.82 at e = 0.1 and 1.08 at
  e = 0.2, i.e. 2.4 hat-h(e, 0) of 2609.14218; the particle threshold of 2609.14218 at
  e = 0.2 maps to delta = 0.108, a factor 10 below. Refuted if the factor is outside 5-20.
- S.2 Hoop for the peak ellipsoid of a monochromatic spectrum (2508.10070) is stricter than
  for the ball: ratio of thresholds between 1.0 (e -> 0) and 1.5 (e = 0.25). Refuted if the
  ratio falls below 1 anywhere.
- S.3 At sigma_H = 0.01 the dispersion threshold of 2211.13950 (mu = 1, ln(kmin/k) = 1) is
  0.071 and the top-hat threshold of 2507.18312 with zeta = 0.025 is 0.23: R8 and R9 disagree
  on about a quarter of the log-delta range [0.01, 1] (0.25 +- 0.03). R1 disagrees with R3
  over most of the map (> 0.5) because R1 needs delta >~ 8e while R3 needs only 0.025.
- S.4 Formation time times delta: 3/(1+3e) (Zel'dovich pancake), 1 (1707 turnaround
  estimate), 1.69 (exact top hat, R = 2M, delta -> 0): the duration criteria differ by up to
  a factor 3 in a_end.
- S.5 Spin at delta = 0.1, sigma_H = 0.01: 1707 a*(2) = 0.13, 2507 zeta^2/delta^(5/2) =
  0.20, 2508 typical 0.043 (sigma_H/6)^(1/2) = 0.0018 and zero for an aligned ellipsoid.

### Outcome of the full check run A-emd-pbh-20261115-113446-024989f (35 checks, 4 failed)

Passed: T1.1 (normalisation 1.00000000), T1.2a (E-bar 1.1817), T1.2c (0.01338, 0.1280), T1.3
(KP 0.0220 vs "0.02"), T1.4a (1.0068 at 1e-3), T1.4b (2.018 at 0.1), T1.5 (Monte Carlo
0.00092 +- 0.00002 / 0.01451 +- 0.00006 / 0.13966 +- 0.00017 vs 0.00091 / 0.01451 /
0.13964), T2.1 (2.378), T2.2a-c, T2.3a (0.636), T2.3b (0.0405), T2.4b (0.986-1.000), T3.1-3,
T4.1-3, T5.1 (2e-15), T5.2 (1.0840, 19.5 times 0.05556), T5.3 at all five sigma*
(beta/sigma-bar^5 = 1.084, 1.122, 1.508, 2.769, 0.672; Mbar/M* = 14.70, 14.70, 14.71, 15.45,
18.08 against 1.08, 1.12, 1.51, 2.77, 0.67 and 14.7, 14.7, 14.7, 15.5, 18.1). T1.6 (visual):
my Fig. reproduces Fig. 1 of 1609.01588 (power law to sigma ~ 0.01, log beta0 = -0.85 at
sigma = 1, crossing of the radiation curve near sigma ~ 0.08).

Failed:
- T1.2b 0.05555 vs 0.05556 and T2.2d 3.248e-14 vs 3.244e-14: last printed digit. T2.2e
  (prefactors recomputed with E-bar = 1.182 exactly) gives 3.244e-14 but then 1.919e-7 instead
  of 1.921e-7: the two coefficients of 1707.03595 were evaluated with different roundings of
  E-bar. Immaterial (relative 2e-4 and 1e-3).
- T2.4a beta0(2) numerical/semi-analytic = 1.41-2.30 for sigma = 1e-3-3.4e-3, not within 20
  percent. Follow-up (interactive, then T2.5a in the next registered run): 1.408 at 1e-3,
  1.072 at 1e-4, 1.015 at 1e-5, so the semi-analytic formula is the sigma -> 0 asymptote but
  reached slowly (delta_th/sigma = 5.4, 11.7, 25). The paper's "agrees for sigma <~ 0.005"
  refers to a log plot over 30 decades; my 20 percent band was the wrong reading of it.
- T2.4c beta0(1) (q = sqrt2) numerical/semi-analytic = 0.65-1.38 for sigma = 0.0077-0.017.
  Splitting the t integral at the kinks of max(z*, delta/(3t)) and tightening epsrel to
  1e-10 changes nothing (3.01294e-138 both ways at sigma = 0.0077); the u integrand is smooth
  (trapezoid on 41 points agrees with quad to 5e-4). At fixed delta_th/sigma = 25 the ratio is
  1.02, 1.04, 1.07 for delta_th = 0.003, 0.0125, 0.05 but 0.65 for 0.192. Candidate cause
  [JUDGEMENT]: the semi-analytic derivation keeps A ~ (9/10)(t/s3)^2 and drops
  (3/2 + 2u^2)/s3^2, whose contribution to the exponent grows like delta_th^4/sigma^2 when
  delta_th is held fixed. Prediction for T2.5b: the ratio keeps falling, below 0.65 at sigma =
  0.006; refuted if it rises back towards 1.

### Outcome of the scan (runs A-emd-pbh-20261115-114638-35ca5e4, -115122-2eb3117, -115232-bee5b2e, -120425-80492f8; the last three differ only in figure labels and added example tables, scan_summary.json identical)

- S.1 confirmed: hoop threshold 0.821 (e = 0.1), 1.084 (e = 0.2); 2609.14218 particles 0.108;
  factor 10.0.
- S.2 not refuted (ratio >= 1 everywhere): peak/ball threshold ratio 1.0022-1.543; the upper
  end slightly exceeds the 1.5 I wrote.
- S.3 confirmed: R8-R9 disagree on 0.259, 0.247, 0.259 of the grid at sigma_H = 0.003, 0.01,
  0.03; R1-R3 on 0.87, 0.70, 0.56.
- S.4 confirmed: 3/(1+3e), 1, 1.686 (delta = 0.01), 1.583 (delta = 0.3); top-hat turnaround
  1.0624.
- S.5 confirmed: 0.126, 0.198, 0.0018.
- Figures viewed: scan_criteria_overview (four panels) and scan_verdict_map (three panels);
  first versions had overlapping labels and a colour bar outside the figure, fixed.

### Outcome of T2.5 (run A-emd-pbh-20261115-115120-2eb3117)

- T2.5a: 1.0719 (1e-4), 1.0149 (1e-5): the second-order semi-analytic formula of 1707.03595 is
  the asymptote of the integral 1304-1308, approached like (sigma/delta_th)^2.
- T2.5b: 0.656 (0.0077), 0.398 (0.006): the prediction (keeps falling below 0.65) held. The
  candidate cause stays [JUDGEMENT] until the dropped term is put back into the asymptotic
  evaluation.
