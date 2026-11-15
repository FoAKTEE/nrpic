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
