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

## 2026-11-15  helper criteria2 (wave 2)  session 1

Task: amplitude conversion in `predict.py` with a test; the spherical LTB profile of
arXiv:2609.14218 in expball-compatible form with its threshold statement; the four failures
of wave 1 examined; prediction tables for the periodic scouting runs S1/S2 and for SR-1.

### Sources read for this session

2609.14218 v1 MDPBH.tex 480-550 (initial data, H_i = 5k at 549), 552-830 (LTB metric 564,
equation 573, S(x) 593-619, t_b = 0 at 625, m(r) 680, ktilde(r) 695, profile 704, r_m 709,
entry 714, t_H 718, singularity time 743, nakedness procedure 748-753, threshold 766-768),
833-983 (aspherical profile 839, D 892, eigenvalues 907-908, hoop line 913-918);
2507.18312 v3 Main.tex 150-220 (compaction function and delta_m, 194-205; Gaussian K, 188);
1707.03595 v4 Spin_PBH.tex 1285-1365 (semi-analytic formulas and the agreement statements),
1403-1425 (caption of the production-rate figure: I = 1, q = sqrt 2), 1811-1925 (appendix:
derivation of the semi-analytic formula, A ~ 9t^2/(10 s3^2) for t >~ 1);
1609.01588 v2 apj_nonsphericalpbh.tex 1300-1345 (derivation of 0.05556, E-bar).
The figure of 1707.03595 (`WsWide20170622v2.eps`, a GIMP raster) was decoded as data by a
script of mine in `scratch/A-emd-pbh/tmp/criteria2/eps_raster.py` (ASCII85 + run-length, no
PostScript interpreted) and viewed: log10 beta0 from -30 to 0, sigma_H from 1e-5 to 1; the
2nd-order curves are drawn from sigma_H ~ 2.5e-4, the 1st-order curves from ~0.017 (where
they leave the frame at -30). Not committed (third-party figure).

### Exploratory numbers (interactive, not registered; repeated in the registered runs below)

mpmath (30 digits): E-bar = 1.1816596669; c = 0.0555549716; the code's `Ebar()` gives the
same 1.1816596669 to 1e-15. **The wave-1 entry above that says "my E-bar = 1.18174" and
"c = 0.05556 needs E-bar = 1.18168" is wrong in both numbers** (1.1817 was the four-decimal
print); the true distance of c from the printed 0.05556 is 5e-7 relative, below the
rounding boundary 0.055555 by 2.8e-8.

### Predictions (written before any run of this session)

A. Amplitude conversion (`predict.py: amplitude_measures`, test `test_criteria2.py`):
- A1 For ln Psi = (mu/2) exp(-k^2 r^2/6) the central linear contrast at entry is
  delta_c = 12 mu/5 and the mean inside r_m is deltabar = 12 mu/(5 e); quadrature of
  -(2/5) r_m^2 lap(zeta) reproduces both to 1e-10 (ratio = Euler's e).
- A2 On a Cartesian grid with e = 0.2, p = 0 and with e = 0.25, p = -0.1: the ball average of
  the same field inside r_m equals 12 mu/(5e) within 2e-3 (voxel error), the Hessian at the
  centre gives the eigenvalues (4 mu/5)(1+3e+p, 1-2p, 1-3e+p) of MDPBH.tex:908 at
  k^2/(aH)^2 = 6 within 1e-4: the anisotropic part does not change either measure.
  Refuted if the ball average moves with e or p by more than the voxel error.
- A3 2507.18312:188 consistency: zeta(0) = (5e/12) delta_m with delta_m = deltabar(mu)
  returns mu to 1e-12 (the Gaussian K of 2507.18312 is the same Gaussian zeta).
- A4 Nonlinear compaction C_max = (3/5)[1 - (1 + r zeta')^2] at r_m (MDPBH.tex:695, 709 with
  2507.18312:198-205) = deltabar (1 - mu/e): 0.2560 at mu = 0.33; the maximum over r on a
  fine grid is at k r = sqrt 6 and equals the closed form to 1e-9.
- A5 The hoop line: 12/5 hhat(0.2, 0) from MDPBH.tex:918 (own implementation) equals
  `hoop_threshold_delta(0.2, 0)` = 1.084 to 1e-12, i.e. R1's delta is the central contrast.

L. LTB profile of 2609.14218 in expball form (`ltb2609.py`, same test file):
- L1 Linear limit (mu = 1e-4, slice with H R_m = 0.3): Delta(R) = C(r)/(H rhat)^2 (rhat = r
  Psi^2) to relative 1e-3.
- L2 Crunch times of `expball.exact.Shells` on a Ball made with the profile equal
  t_s(r) = (pi/3) m ktilde^(-3/2) of MDPBH.tex:743 (own implementation, 2609 conventions) to
  1e-8 relative for shells inside the cutoff, mu in {0.01, 0.03}.
- L3 Areal radius of the shells from `expball.exact` equals R = r m^(1/3) t^(2/3) S(x) of
  MDPBH.tex:593-619 (own implementation of S) to 1e-8 at three times.
- L4 The expball ball (H R_b < 1, every shell expanding on the slice: Delta < 9pi^2/16 - 1)
  holds mu only up to mu_max ~ 0.443 (H R_b)^2/q^2: 0.040 +- 0.004 for q = R_b/r_m = 3 and
  0.090 +- 0.009 for q = 2 at H R_b = 0.9; the binding condition is the turnaround of the
  central shell before the slice. So the LTB threshold mu_c in (0.32, 0.33] of
  MDPBH.tex:766-768 cannot be tested in the ball; it belongs to the periodic box. Refuted
  if mu_max is outside these bands (then my reading of the binding constraint is wrong).
- L5 No shell crossing before the central crunch for mu <= 0.5 (t_s(r) increasing).

F. The four failures of wave 1:
- F1 T1.2b: c = 0.0555549716 rounds to 0.05555; the paper's 0.05556 is what a two-step
  rounding (to 0.0555550, then to four digits) gives; any E-bar in [1.1816170, 1.1816595]
  gives it; the exact E-bar lies 1.7e-7 above that interval. Explained, not a code error.
- F2 T2.2d: the ratio of the two printed prefactors of 1707.03595 (1.921e-7/3.244e-14),
  which does not depend on E-bar, differs from the exact ratio 0.4^6/(12/125)^9 by 1.2e-3,
  three times the largest rounding effect (4.1e-4): no single E-bar gives both. 1.921e-7
  needs E-bar in [1.18163, 1.18176] (contains the exact value), 3.244e-14 needs
  [1.18195, 1.18202] (contains 1.182). Explained: the paper used two values of E-bar.
- F3 T2.4a, corrected to what the paper states (agreement on its figure, 30 decades): over
  the window it plots (beta0(2) >= 1e-30, sigma_H <= 0.005) max |log10(num/semi)| <= 0.5;
  I expect 0.36 near sigma_H = 0.0034-0.005, and the ratio falling monotonically to 1 as
  sigma_H -> 0 (T2.5a). Refuted if the band is exceeded.
- F4 T2.4c, corrected likewise: window beta0(1) >= 1e-30 (sigma_H >~ 0.017) to 0.04;
  max |log10 ratio| <= 0.5 (expected <= 0.2).
- F5 T2.6, the cause of the 1st-order drift (wave 1, [JUDGEMENT]): with I2 the [t2, inf)
  part of the appendix integral (1707.03595, eq. t-integral) evaluated with the exact A and
  with A ~ 9t^2/(10 s3^2): (a) numerical beta0(1) / I2(exact A) = 1 within 2 % at
  sigma_H = 0.006, 0.0077, 0.01, 0.017; (b) I2(exact A)/I2(approx A) < 1, falling towards
  small sigma_H, and equal to numerical/semi-analytic within 10 %; (c) I2(approx A)/semi-
  analytic is constant within 10 % over the same sigma_H. Refuted if (a) or (b) fails.

P. Prediction tables (`scouting_table.py`):
- P1 SR-1 (data set 2t): the homogeneous core (Delta = 1 inside R_i = 2.4, H = 1/16) has the
  linear contrast 0.5642 on the slice and delta_H = 0.02015 at the horizon entry of its
  edge; criteria R5 (exact top hat of 2507.18312) then puts R = 2M of the core edge at
  tau = 44.381, equal to expball's exact value to 1e-6 relative (both are the same closed
  FLRW region). Refuted beyond 1e-6: then the mapping (Delta, H R) -> delta_H is wrong.
  R1 for a sphere (Zel'dovich point collapse at a/a_H = 3/delta) comes at a/a_H ~ 149,
  after the run's end (crunch at a/a_H ~ 84): the Zel'dovich time is 1.8 times the exact one.
- P2 S1 (mu = 0.5, e = 0.2, eps_i = 1, 64^3 lattice): R1 yes (mu > 0.452, margin 10 %); top-hat
  time of the compaction shell ~ 7.5 t_H (periodic helper's P0); spherical LTB (e = 0) of the
  same mu: first trapped sphere earlier than the top-hat time of r_m (inner shells are denser).
  S2 (mu = 0.03): R1 no; top-hat time ~ 508 t_H > 250 t_H; R4 at t_end = 250 t_H is "yes" in
  the central measure (0.072 > 0.0252) and marginal in the mean (0.0265 > 0.0252);
  2609.14218's particle bracket (0.045, 0.05] says no.

### Outcome A and L (run A-emd-pbh-20261115-161543-36e461d; repeated with layout-only figure changes as A-emd-pbh-20261115-162306-80396e4, results_criteria2.json byte-identical; pytest of the same functions A-emd-pbh-20261115-162524-d32d331, 10 passed)

Code faults found before the registered run (development runs in `scratch/A-emd-pbh/tmp/criteria2/dev`, not registered): my A1 test input had lap(zeta)(0) = -mu k^2/2 instead of -mu k^2 (a slip of mine in the test, not in predict.py); the y-solver of ltb2609 rejected a converged Newton step as "outside the bracket" (wn == lo) and fell into bisection onto a wrong root (y = -1.9 at kappa = 0.0048), which made R(r) non-monotonic; fixed (strict bracket test, Newton in w = sqrt(1 - y)).

- A1 confirmed: quadrature gives r_m, delta_c, deltabar to 9e-12, 2e-11, 4e-16; ratio = e.
- A2 confirmed, better than predicted: ball average 0.088291039 for all four (e, p), relative 3.0e-7
  from 12 mu/(5e) (the second-difference Laplacian), the same to 6e-11 relative between the four cases;
  eigenvalues at the centre equal (4mu/5)(1+3e+p, 1-2p, 1-3e+p) within 4.6e-6 of 0.8 mu.
- A3 confirmed: zeta(0) = (5e/12) deltabar returns mu to 2e-16; round trips 2e-16.
- A4 confirmed: maximum of (3/5)(1 - (1 + r zeta')^2) at k r = sqrt 6 (grid spacing), C_max =
  deltabar (1 - mu/e) to 7e-14: 0.02619 (mu 0.03), 0.2493 (0.32), 0.2560 (0.33), 0.3603 (0.5).
- A5 confirmed: 12/5 hhat(0.2, 0) = 1.0841937 = R1's delta_th to 2e-16 (also e = 0.1, 0.25 with
  p = -0.1, 0.2 with p = 0.1): R1's amplitude is the central contrast. The hoop line in mu is
  0.4517 at e = 0.2, in deltabar 0.399.
- L1 prediction (1e-3 at mu = 1e-4) **refuted**: relative deviation from linear theory 2.2e-3 at
  mu = 1e-4 and 2.2e-4 at mu = 1e-5, i.e. proportional to Delta (2.7e-3, 2.7e-4 at the centre),
  and (deviation)/Delta = 0.809524 = 17/21 to 3e-7: the second-order coefficient of the mean
  contrast in spherical collapse. My tolerance ignored that a slice at a/a_H = 11 carries an
  order-Delta nonlinear correction; the test now checks the 17/21.
- L2/L3 confirmed, far below the tolerance: expball shells built from the profile have the
  slice age t_i to 4e-16, crunch times equal (pi/3) m ktilde^(-3/2) (MDPBH.tex:743) to 9e-16,
  R = 2M times to 7e-16, areal radii equal the S(x) form (593-619) to 3e-15 at 0.1, 0.5, 0.9 of
  the central crunch; mu = 0.005, 0.01, 0.015 in a ball with H R_b = 0.9, r_m = R_b/4.5.
- L4 partly refuted: mu_max = 0.0435 for q = 3 (inside my band 0.040 +- 0.004) but 0.112 for
  q = 2 (outside 0.090 +- 0.009). The binding condition is the one I named (central shell at
  turnaround on the slice), but kappa(0) = 4 mu e^(-2 mu)/(H r_m)^2 carries Psi(0)^-4 = e^(-2mu),
  which my leading-order band left out; mu_max = 0.0184 for q = 4.5. Construction succeeds at
  0.999 mu_max and is refused at 1.001 mu_max for all three q. So the expanding ball holds the
  2609.14218 profile only for mu <~ 0.04 (q = 3) to 0.11 (q = 2), far below the LTB threshold
  mu_c in (0.32, 0.33]: that threshold can only be tested in the periodic box [VERIFIED as
  arithmetic], as decision 0013 already places the threshold line.
- L5 confirmed: t_s(r) increasing and R(t, r) increasing in r up to 0.99 t_s(0) for mu = 0.01,
  0.1, 0.32, 0.33, 0.5 (no shell crossing before the central crunch). New: the earliest
  marginally trapped sphere is the centre itself at the central crunch (t_ah(r) increases
  outward from t_s(0)) for all five mu, so with t_b = 0 the apparent horizon emerges from the
  central singularity, as the paper says of its slices (778-779). Central crunch t_s(0)/t_H =
  607, 25.1, 8.50, 8.36, 7.47 for mu = 0.01, 0.1, 0.32, 0.33, 0.5; in closed form
  t_s(0)/t_H = (108 pi/576) e^(3mu) mu^(-3/2), i.e. the linear top-hat crunch time of the
  central contrast 12 mu/5 times e^(3 mu) (the Psi(0)^6 of m(r), 680).
- Figures viewed: fig_amplitude (profiles of the two measures; thresholds of the literature in
  mu, delta_c, deltabar), fig_ltb2609 (Delta(R) and the local contrast on the slice with the
  taper; residuals expball vs closed forms at 1e-16 to 1e-14; t_s and t_ah against r; the
  compaction function peaking at r_m). First versions had overlapping labels, fixed.

### Outcome P (run A-emd-pbh-20261115-162303-80396e4: `scouting_predictions.md`, `.json`, figure)

The table uses the initial data only. The first SR-1 card segment had already run when I
computed it (runs_ball commit 208f933, whose subject I read afterwards: "fields non-finite from
t = 33"); nothing from that run enters the table.

- P1 confirmed: core Delta = 1, y = 0.74638, linear contrast on the slice 0.56423, horizon entry
  of the core edge at a_H/a_i = 0.035717, delta_H = 0.020152. R5 (exact top hat of
  2507.18312) against expball's exact shells: turnaround 16.893769 (difference 0), R = 2M of
  the core edge 44.381466 (2.2e-16), crunch 44.454205 (0). Zel'dovich point collapse of the
  sphere (R1, R2 with e = p = 0) at a/a_H = 148.9, tau = 120.1, after the planned end 44.37
  (a/a_H = 83.6), as predicted. Two facts the table adds: (i) with the planned end 44.37 the
  core edge (44.381) is not yet trapped, only the first trapped sphere of the data set
  (44.349, R_i = 2.731, in the smoothing region) is; (ii) R10 (lattice noise, [JUDGEMENT]
  extension) says "no" for SR-1 (b_min = 0.12 > b_BH = 0.034 with 463 core particles), but in
  geodesic slicing (alpha = 1, beta = 0) u_i = 0 solves the geodesic equation, so particles at
  rest stay at rest and the lattice cannot generate a dispersion: R10 does not apply to SR-1
  [JUDGEMENT]; it would apply to SR-2. The compaction function of data set 2t peaks outside
  the homogeneous core (R = 3.63 M, C_max = 0.0377), so the threshold measure deltabar of
  SCOPE.md section 3 for this data set is 0.0377, not the core's 0.0202.
- P2, S1 (mu = 0.5): delta_c = 1.2, deltabar = 0.4415, C_max = 0.3603. R1 "yes" (first axis at
  1.95 t_H) in the central measure, "no" in the mean (0.44 < 1.084): by A5 the hoop row is
  defined with the central measure, so "yes" is its verdict. R5 in the central measure is
  outside the top-hat formula (delta >= 0.6, b_BH >= 1); **the wave-1 code printed "no" there,
  a defect of mine now corrected to n/a**; in the mean it gives R = 2M of r_m at 6.07 t_H.
  My prediction "spherical LTB of the same mu: first trapped sphere earlier than the top-hat
  time of r_m" is **refuted**: the exact LTB (e = 0) first traps the centre at its crunch,
  7.47 t_H, later than the linear top-hat time 6.07 t_H; the r_m shell is trapped at 15.4 t_H.
  At mu = 0.5 the linear measures are poor: the exact central crunch is the linear one times
  e^(3 mu) = 4.5 (L5). S1's planned end, 30 t_H, is after all of these.
- P2, S2 (mu = 0.03): delta_c = 0.072, deltabar = 0.02649. R1 no (first axis at 133 t_H); top
  hat of r_m (mean): R = 2M at 507 t_H, crunch 508 t_H (> 250, as predicted); R4 at 250 t_H yes
  in both measures (0.072 and 0.0265 > 0.0252; marginal in the mean, as predicted); 2609.14218
  particles: no; LTB e = 0 verdict: globally naked, no PBH. But in the central measure R5 puts
  R = 2M of the central region at 112 t_H, and the exact spherical LTB of mu = 0.03 crunches
  its centre at 124 t_H, both inside the planned 250 t_H; R10 (lattice noise, ~2017 particles
  in r_m) says the collapse halts. So the statement of the periodic helper's S2 plan that
  "every criterion predicts no horizon by 250 t_H" holds for the hoop line, the top hat of the
  compaction shell and the particle runs of 2609.14218, not for the central-region rows:
  something happens at the centre (a pancake at 133 t_H for e = 0.2, a central crunch near
  110-125 t_H for e = 0) inside the run [JUDGEMENT on which applies; the numbers are
  arithmetic].
- Figure viewed (fig_scouting_predictions): formation epochs per criterion against the end of
  each run; first version had the legend outside the canvas and overlapping labels, fixed.

### Outcome F (run A-emd-pbh-20261115-161813-6c820fb, full check_criteria.py at commit 6c820fb: 40 checks, 3 failed (T2.6a-c, nan), 4 diagnostics)

The first attempt, run A-emd-pbh-20261115-161542-36e461d, failed at T1.2b on my own code
(decimal conversion of a numpy float, `repr` of numpy 2 floats); fixed in 6c820fb; the failed
manifest is kept.

- F1 (T1.2b) confirmed: c = 0.0555549716 (E-bar = 1.1816597, equal to mpmath); one-step rounding
  0.05555, two-step 0.05556. The corrected check (within one unit of the last printed digit)
  passes; the wave-1 digit check stays as diagnostic T1.2b-d. The wave-1 journal's
  explanation (E-bar 1.18174 vs 1.18168) is withdrawn above.
- F2 (T2.2d) confirmed: printed ratio deviates from the exact one by 1.22e-3, rounding allows
  4.14e-4 (T2.2f); 1.921e-7 needs E-bar in [1.181633, 1.181756], 3.244e-14 needs
  [1.181945, 1.182018]; exact 1.1816597; with E-bar = 1.182 the 1st-order prefactor is
  3.244e-14 (T2.2e). The two printed prefactors of 1707.03595 cannot come from one E-bar; the
  code is right.
- F3 (T2.4a) confirmed, closer to the band than I expected: on the plotted window (2.5e-4 to
  0.005) the ratio rises monotonically from 1.139 to 3.038, max |log10| = 0.483 at
  sigma_H = 0.005 (I expected 0.36 there; the wave-1 grid did not include 0.005). Within the
  0.5 band, 1.6 % of the figure's 30 decades.
- F4 (T2.4c) confirmed: plotted window 0.0192 to 0.04 (beta0(1) >= 1e-30 from 0.0192), ratio
  1.448 to 2.319, max |log10| = 0.365 (I expected <= 0.2: refuted in size, inside the band).
- F5 (T2.6) **failed as coded**: I added sigma_H = 0.004 to the list in the code without
  checking; there beta0 underflows (exponent -0.0184/sigma^2 ~ -1150) and the nan made all
  three checks fail. At the four sigma_H of the prediction: (a) numerical/I2 = 1.0028,
  1.0060, 1.0120 at 0.006, 0.0077, 0.01 (within 2 %, confirmed) but 1.0416 at 0.017 (my "within
  2 % at 0.017" refuted: the [t1, t2] and t < 0 parts grow with sigma_H); (b) I2(exact
  A)/I2(approx A) = 0.258, 0.423, 0.591, 0.828, below 1 and falling towards small sigma_H
  (confirmed), but **not** equal to numerical/semi-analytic within 10 % (0.398, 0.656, -, 1.363):
  refuted, because (c) I2(approx A)/semi-analytic = 1.538, 1.542, 1.549, 1.581 is a constant
  factor of ~1.55 (constant within 3 %, confirmed). So the drift of the 1st-order formula
  with sigma_H is entirely the dropped (2u^2 + 3/2)/s3^2 in A (now demonstrated), and on top
  of it the closed form is low by a sigma-independent 1.55, which partly compensates the drift
  near sigma_H ~ 0.012, the reason the two curves look alike on the paper's figure.
  The root formula t_{1,2}(u) printed at Spin_PBH.tex:1880-1886 has 3 delta_th in the
  denominator; solving z* = z_th gives 3 pi delta_th, which also gives the paper's own limit
  t2 ~ 12 E/(pi delta_th) (1921) [VERIFIED by derivation]; a typo of the paper; the code uses
  the corrected root (with the printed one I2 was 140 times too small, development run).

### Prediction for T2.6d and the repeat of T2 (written before the repeat)

- T2.6 repeated at sigma_H = 0.006, 0.0077, 0.01, 0.017 only (no underflow there).
- T2.6d: the constant factor of (c) is the approximation t2 ~ 12 E~/(pi delta_th) of 1921:
  I2(approx A)/semi-analytic = [int (1-4u^2) t2(u)^-5 du / int (1-4u^2) (12 E~(u)/(pi
  delta_th))^-5 du] x (2 + 2X + X^2)/X^2 at X = delta_th^2/(2 sigma_H^2), within 1 %, at all
  four sigma_H. Refuted beyond 1 % (then another approximation of the appendix contributes).

### Outcome of the T2 repeat (run A-emd-pbh-20261115-163358-9b2d048, `check_criteria.py --only 2` at 9b2d048: 17 checks, 0 failed, 3 diagnostics)

- T2.6a-c at sigma_H = 0.006, 0.0077, 0.01, 0.017: the numbers of the full run (above), now
  without the nan; T2.6a passes on sigma_H <= 0.01 as written in its check (1.0028-1.0120), the
  1.0416 at 0.017 stays a refuted part of my F5 prediction.
- T2.6d confirmed, exactly: I2(approx A)/semi-analytic = 1.5378, 1.5417, 1.5485, 1.5806 equals
  the t2 factor 1.5318 times (2 + 2X + X^2)/X^2 to the four printed digits at all four
  sigma_H. So the semi-analytic 1st-order formula of 1707.03595 (1345) differs from the
  integral it approximates by three identified pieces: the dropped (2u^2 + 3/2)/s3^2 in A
  (the sigma-dependent drift, 0.26-0.83), the approximate root t2 (a constant 1.53 at
  delta_th(1) = 0.192, q = sqrt 2) and the terms 2 + 2X of F (< 1 %); the remainder
  (numerical/I2, 0.3-4 %) is the [t1, t2] and t < 0 parts the appendix neglects.
- T2.4a, T2.4c, T2.5a, T2.5b and the rest of T2 identical to the full run.
- Figure `check_T2_ratios_1707.03595` viewed: left, the ratios on the paper's plotted windows
  (shaded) with the 0.5-dex band; right, the decomposition of T2.6.
- State of the four wave-1 failures: T1.2b and T2.2d explained (rounding in the paper; two
  values of E-bar); T2.4a and T2.4c corrected to the paper's actual statement and passing; the
  cause of the 1st-order drift demonstrated (T2.6).
