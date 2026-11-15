# JOURNAL of tracks/C-sidm/models (wave 2 helper package "models")

Predictions are written before the registered run of each test; outcomes are appended
below them, also when a prediction fails. Labels: [VERIFIED] computed in a registered run
or read at a source with a locator; [BACKGROUND] standard, not re-derived; [JUDGEMENT];
[TO VERIFY]. Units G = c = 1; models in units of their ADM mass M unless stated.

## 2026-11-15, entry 1: predictions

### Disclosure: smoke check before these predictions

Before writing the predictions below I ran one unregistered smoke check of the
generalised solver `evstatic_b.py` (interactive, not kept): King b = 1 at y0 = 0.314,
0.334032, 0.354 gave E_b, R and Z_c bit-identical to `equilibria/evstatic.py`; the F21
family b = 0.1 at four w0 (2.973, 3.165, 3.587, 4.051) gave Z(0), eps, R/M and M0/M equal
to `gravothermal/tmb.py` to the ten printed digits; the first E_b maximum lay at
y0 = 0.380564 (eps = 0.0351789). Predictions M1 and M2 below are therefore not blind for
these points; the registered run repeats them on the full model set.

### M1. King regression (the generator chain is unchanged)

Prediction: the five King models (y0 = 0.314, 0.324, y_max = 0.334032, 0.344, 0.354)
built by `make_models.py` (equilibria's `make_equilibria.build` with `evstatic_b`,
b = 1.0) at N = 10^4, seed 1, stratified, give `.nrp` and `.tab` files byte-identical to
those of run C-sidm-20261115-120610-b4592be. Refuted by any differing byte.

### M2. F21 family b = 0.1 against the independent solver of the gravothermal package

Prediction: for every b = 0.1 model, Z(0), eps = E_b, R/M and M0/M of `evstatic_b`
(variable y = -ln(1 - b w), Gauss-Jacobi moments) agree with `tmb.solve` (variable w,
Gauss-Legendre) at w0 = (1 - e^{-y0})/b to 1e-8 relative; the first E_b maximum along y0
gives Z(0) = 0.5404 within 1e-6 of criteria.json (0.5404128568, run
C-sidm-20261115-120722-38ab057). Refuted by a larger difference.

### M3. Offline checks of the particle files at N = 10^4 and 10^5

Prediction: every enforced check of `equilibria/check_equilibria.check_model` passes for
the 5 King and 8 b = 0.1 models at both N: matching to Schwarzschild below 1e-12, TOV
residual below 1e-6, Hamiltonian-constraint residual of the table below 1e-6 away from
the edge, rest mass by the isotropic integral to 1e-8, file round trip, table monopole
M = 1 to 1e-12, stratified radial and polar ECDF within 1/N, equal-mass shell counts
exact, max E/E0 <= 1, shell moments within 4.5 standard errors (N = 2e4 resamples), KS
p-values > 1e-3, |sum m W/psi - M| < 1e-3. I expect |sum m W/psi - M| about 2e-4 at
10^4 (the King files of run -120610 have 2.2e-4) and smaller at 10^5 (not enforced).
Risk [JUDGEMENT]: the b = 0.1 models are core-halo (r_core about 2 M, R about 20 M), so
the table resolution (rbar_s/4000, about 5e-3 M) is fine, but the Hamiltonian-constraint
check near the steep core is the most likely failure.

### F1. Fluid onset with the Juttner adiabatic index (b = 0.1)

Prediction:
(a) Pipeline check: variant F21 (gamma = 1 + p/u) reproduces the gravothermal onset
    Z(0) = 0.6348 (w0 = 3.58710) to 1e-4 in Z(0) at N = 600 FEM nodes.
(b) Gamma_1 = 1 + 1/c_v of a Juttner gas falls twice as fast with temperature as the
    perfect-gas 1 + p/u (series: 5/3 - (5/3) theta against 5/3 - (5/6) theta
    [BACKGROUND]); at the centre theta_T = b/(1 - b w0) is about 0.15, so Gamma_1 is about
    1.45-1.50 against F21's gamma(0) = 1.607 at the eps maximum (criteria.json). At the
    eps maximum F21's gamma_cr = 1.568 (criteria.json), above this Gamma_1, so by the
    trial-function criterion the Juttner fluid is already unstable there. I therefore
    predict the J_T onset at Z(0) between 0.30 and 0.5404, i.e. BELOW the collisionless
    E_b maximum (the opposite order from the F21-gamma onset, 0.6348). Refuted if
    Z(0)_J_T >= 0.5404 or < 0.30.
(c) Ordering: Z(0)(J_T) <= Z(0)(J_E), Z(0)(J_p) < Z(0)(J_pu) < Z(0)(F21): the truncated
    distribution is colder than its temperature parameter (theta_E, theta_p < theta_T), so
    Gamma_1 is higher with theta_E or theta_p. Refuted by another order.
(d) Resolution: N = 600 and 1200 roots agree to 1e-3 in Z(0).

### G1-G6. Growth-rate and collapse-time pipeline on the first paper's runs

Runs: `/data/haiyangw/nrpic/runs/st/` (main checkout, read-only). Published numbers:
`paper/sections/tables/tab_outcomes.tex`, tables `tab:outcomes_clusters` and
`tab:outcomes_migration`.

G1. Recovery of the published numbers to their printed digits: first apparent horizon
    t/M 191.0 (y_c = 0.605, `yc0605_v5`), 104.3 (0.500, `yc0500_v5`), 147.2 (0.756
    compressed, `reconf_yc0756_hc`); M_AH/M at the end 1.0000, 1.0001, 0.9970;
    macroparticles left 6, 3, 0; alpha_c at the end 0.051, 0.016; alpha_c(0) = 0.749
    (compressed); first upward crossing of alpha_c = 0.8 at 59 (plain filter) and 88, 86,
    91 (compensated samples 1-3, `dir_yc0500_*`); half-swing growth of the stable
    y_c = 0.819 model 1.3e-5 per M (`ctl/s1_nf4c`, sample 1) and 1.7e-5 (`osc/dx2b`, half
    the cell spacing; the row lists sample 1 first, `make_tables.py` loops over
    s1_nf4c then dx2b). Refuted by any value that differs at the printed precision.
G2. Synthetic signals d(t) = A e^{sigma t} + oscillation + white noise, sigma = 0.02,
    0.05, 0.1 per M, window spanning 2.3 e-folds: the smoothed log-linear fit recovers
    sigma within 3 percent on average over 50 noise realisations, and |fit - truth| < 3 SE
    in at least 90 percent of them. Refuted otherwise.
G3. The three compensated unperturbed y_c = 0.5 samples (same model, other noise) give
    growth rates of alpha_c within 15 percent of their mean. The plain-filter run crosses
    0.8 earlier (59 against 86-91) mainly because it starts with a larger amplitude (its
    deposit is 3e-3 low in E, tab:outcomes_clusters), not because it grows faster:
    sigma_plain within 25 percent of the compensated mean and the extrapolated amplitude
    at t = 0 larger by more than a factor 2. Refuted otherwise.
G4. In the same runs the growth rate of the radius enclosing 10 percent of the rest mass
    agrees with that of alpha_c within 20 percent (one linear mode).
G5. Kicked collapsing runs: sigma(y_c = 0.605) < sigma(y_c = 0.500) (0.605 is closer to
    the threshold y_c = 0.67961, run C-sidm-20261115-115344-eb8b752); the kicked y_c = 0.5
    rate within 30 percent of the unperturbed y_c = 0.5 rate (same mode, opposite sign;
    adaptive against static mesh) [JUDGEMENT]; the lapse collapse time t(alpha_c = 0.2)
    precedes the first apparent horizon by 0 to 6 M in all three collapsing runs.
G6. Fit settings (smoothing 5-20 M, amplitude window (0.003, 0.03) to (0.01, 0.1)) change
    the growth rates of G3 by less than 20 percent.

## 2026-11-15, entry 2: outcomes F1 (run C-20261115-165315-7b473b8)

Run: `python3 tracks/C-sidm/models/fluid_onset.py` (commit 7b473b8, 4 cores, registered by
nrpic-run), output `scratch/C-sidm/C-20261115-165315-7b473b8/fluid_onset.json`.
Tabulated Juttner functions against `collide/REFERENCES/mj.py` at 40 random theta in
[1e-4, 10]: c_v to 2.0e-11, <W> - 1 to 1.0e-11, inverse to 7.1e-12; Gamma_1 = 5/3 and 4/3
in the limits. [VERIFIED]

| b = 0.1, variant | w0 (N = 1200) | Z(0) (N = 1200) | Z(0) N = 600 minus N = 1200 |
|---|---|---|---|
| F21 (gamma = 1 + p/u) | 3.587099 | 0.634816 | 1.3e-7 |
| J_T (Gamma_1 at the Tolman theta) | 2.532868 | 0.412527 | 1.3e-8 |
| J_E (Gamma_1 at the energy-matched theta) | 3.130772 | 0.533056 | 5.4e-8 |
| J_p (Gamma_1 at theta = p/n) | 3.124408 | 0.531703 | 5.0e-8 |
| J_pu (1 + p/u of an untruncated Juttner gas) | 3.165085 | 0.540379 | 2.8e-8 |
| reference: E_b maximum (criteria.json) | 3.165241 | 0.540413 | |

(a) PASS: F21 variant 0.6348166 against 0.6348166 of the gravothermal run (difference
1e-9). (b) PASS: J_T onset at Z(0) = 0.4125, inside the predicted 0.30-0.5404 and below the
collisionless E_b maximum. (c) PASS: order J_T < J_p < J_E < J_pu < F21 (the prediction
left J_E and J_p unordered). (d) PASS: resolutions agree to 1.3e-7 in Z(0).
Central values at the onsets (fluid_onset.json, "central"): at the J_E onset theta_T =
0.1456, theta_E = 0.0959, theta_p = 0.0970; Gamma_1(theta_E) = 1.552 against F21's gamma
1.608. [VERIFIED]

Other b (N = 600 only): Z(0) of the J_E onset 0.5039 (b = 0.2), 0.4978 (0.3), 0.4937 (0.5),
each below that b's E_b maximum (0.5225, 0.5176, 0.5142); F21-gamma onsets 0.5923, 0.5843,
0.5790 (the gravothermal values 0.5790 for b = 0.5 agree). J_T: 0.2747 (0.2), 0.2036 (0.3);
for b = 0.5 omega^2 < 0 already at the lowest model of the scan (w0 = 0.20), so the J_T
onset lies below it (not located). [VERIFIED]

Observation, no cause tested: the J_pu onset (0.540379) lies 3.4e-5 below the E_b maximum
(0.540413), a coincidence or a near-identity that I did not investigate.

Reading [JUDGEMENT]: with any Juttner adiabatic index the fluid onset of the b = 0.1 family
moves from 0.6348 to at or below the collisionless E_b maximum; with the temperature that
collisions conserve (J_E) it lies 0.0074 in Z(0) below it. The Kn -> 0 anchor of decision 3
(stage/G0/REPORT.md section 2) therefore sits just on the stable side of the collisionless
threshold, if that threshold is the E_b maximum; the window in which collisions could
stabilise a collisionlessly unstable core (the reading behind 0.6348) does not exist with
this index. J_T, which assigns the truncated distribution's temperature parameter to a
Juttner gas, is the least physical variant (theta_T is 1.5 times the kinetic temperature
theta_E at the centre) and gives the largest shift.

## 2026-11-15, entry 3: outcomes G1-G6, first attempt (run C-20261115-170231-4e68455, FAILED)

The run stopped with KeyError 'sigma' in the verdict bookkeeping after all fits had been
printed (run.log of the run): the plain-filter run has no fit window (see G3 below), and
the verdicts did not allow for that. No JSON was written. Numbers from run.log:

- G1 PASS: all 18 published numbers recovered at their printed precision (191.0, 104.3;
  1.0000, 1.0001; 6, 3; 0.051, 0.016; 0.749, 147.2, 0.9970, 0; 59; 88, 86, 91; 1.3e-05,
  1.7e-05).
- G2 FAIL: mean relative bias +3.3, +2.9, +1.8 percent for sigma = 0.02, 0.05, 0.1 (limit 3
  percent: the first fails); 3-SE coverage 0.58, 0.90, 0.86 (limit 0.9: two fail). The
  log-linear fit with the threshold-defined window overestimates sigma by 2-3 percent and
  its error is underestimated. Not yet explained; candidates [TO VERIFY]: selection of the
  window by noisy threshold crossings (the window starts where the noise is low and ends
  where it is high), the oscillation residual left by a 10 M boxcar on a 25 M period.
- G3 seeds PASS: 0.0655, 0.0606, 0.0602 per M (mean 0.0621, largest deviation 5.5 percent,
  limit 15). G3 plain NOT EVALUABLE with the fixed settings: |d_s| exceeds lo = 0.01 at the
  first smoothed point (the plain-filter run departs by 0.015 within the first 5 M).
- G4 FAIL: sigma(r10) = 0.0748, 0.0405, 0.0437 against sigma(alpha_c) = 0.0655, 0.0606,
  0.0602 (+14, -33, -27 percent; limit 20). The r10 fits carry standard errors 0.011-0.025,
  so the differences are within 1-1.5 SE; no cause tested.
- G5: sigma = 0.1716 +- 0.0207 (y_c = 0.500 kicked, window 79-93 M) and 0.1645 +- 0.0171
  (0.605, 162-176 M): the predicted order holds in the central values but not beyond the
  errors; the kicked y_c = 0.5 rate is 2.8 times the unperturbed one (FAIL of the 30
  percent prediction): the kicked window (alpha_c departure 0.02-0.2, after the oscillation)
  measures the nonlinear plunge, not the linear mode. Lead times not printed (rerun).
- Compressed y_c = 0.756: 0.0265 +- 0.0009 (alpha_c, 45-124 M), 0.0405 +- 0.0046 (r10).

Change for the rerun: the verdicts handle a missing fit (`evaluable: false`); the fits are
unchanged, so G1-G5 numbers must repeat exactly.

## 2026-11-15, entry 4: outcomes G1-G6 (run C-20261115-170346-298a1ba) and predictions D1

Rerun with the fits unchanged: every number of entry 3 repeats (G1 18/18; G2 biases +3.3,
+2.9, +1.8 percent, 3-SE coverage 0.58, 0.90, 0.86; G3 seeds 0.0655, 0.0606, 0.0602;
G4 +14, -33, -27 percent; G5 rates 0.1716, 0.1645). New in the JSON:

- G2 curve_fit estimator (A e^{sigma t} + C on the unsmoothed records): mean bias +1.0,
  +0.7, -2.0 percent.
- G3 plain: not evaluable with the fixed window (above lo at the first smoothed point).
- G5 lead PASS: t_AH - t(alpha_c = 0.2) = 3.3 M (y_c = 0.500), 1.8 M (0.605), 1.1 M
  (0.756 compressed), all within 0-6 M. Order sigma(0.605) < sigma(0.500) holds in the
  central values (0.1645 < 0.1716) but not beyond one SE (0.017-0.021): not significant.
  Kicked against unperturbed y_c = 0.5: 2.76 times (FAIL).
- G6: over 9 settings (smoothing 5, 10, 20 M x windows (0.003, 0.03), (0.005, 0.05),
  (0.01, 0.1)) the rates that exist stay within 7, 8, 18 percent of the default for the
  three compensated samples (limit 20), but 3, 3 and 2 settings find no window (the
  smallest lo lies below the departure of the first smoothed point). As written ("change
  by less than 20 percent"), PASS for the rates; the missing windows are recorded.

Figures `figs/fig_growth.png` (looked at): the three compensated samples grow in parallel
over 12-60 M between departures 0.01 and 0.1 of alpha_c; the plain-filter run starts at
0.015 and stays above the others by a factor 2-3 (consistent with a larger initial
amplitude, not tested by a fit); the r10 departures are dominated by a step and a plateau
over 10-30 M before they grow, which is why their rates scatter (G4); in the kicked runs
the fitted segment is the start of the plunge after the last oscillation.

### Prediction D1 (diag_g2.py): why the log-linear fit is biased in G2

The departure is measured from the first record, d = y - y(0). For a pure mode
y(0) already holds the initial amplitude A, so d = A (e^{sigma t} - 1) and ln|d| lies
below sigma t + ln A by -ln(1 - A/d): 0.105 at the window start (d = lo = 10 A) and 0.010
at its end (d = hi). The slope is then too steep by about (0.105 - 0.010)/ln(hi/lo) =
4.1 percent of sigma [derivation, JUDGEMENT on its size]. Prediction for diag_g2.py (50
realisations per sigma = 0.02, 0.05, 0.1):
 G (as G2) reproduces biases of +2 to +4 percent;
 A, B, C, D, E (exact reference 0): |mean bias| < 1 percent for every sigma;
 H (curve_fit, exact reference): |mean bias| < 1 percent; F (curve_fit as G2): within 2.5.
Refuted if A stays above 1.5 percent for any sigma (then oscillation or window selection
is the cause, decided by B-E).

## 2026-11-15, entry 5: outcomes M1-M3 at N = 10^4 and D1; prediction T1

Build run C-20261115-170126-b4f74af (N = 10^4, 13 models, 2.5-2.8 s each); check run
C-20261115-170221-b1a491c (exit 1 because of three failed checks, below).

- M1 PASS: the five King models' `.nrp` and `.tab` files are byte-identical to those of
  run C-sidm-20261115-120610-b4592be (10 of 10 sha256 equal).
- M2 PASS: Z(0), eps, R/M, M0/M of evstatic_b against tmb.solve agree to 5.2e-11 or
  better for all eight b = 0.1 models; the E_b maximum at y0 = 0.3805639 (w0 = 3.1652414)
  has Z(0) = 0.54041288, 2.4e-8 from criteria.json.
- M3: 250 checks pass, 3 FAIL: the anisotropic TOV residual (limit 1e-6) is 1.1e-6,
  1.2e-6, 1.4e-6 for Z(0) = 0.58, 0.60, 0.6348; it rises smoothly with Z(0) from 7.3e-7
  (0.50) and is 2.2-2.4e-7 for the King models. Every other check passes for every model:
  Hamiltonian-constraint residual of the table 1.8-3.6e-8, file round trip, ECDFs within
  1/N, shell counts exact, max E/E0 < 1, shell-moment z at most 1.22, KS p-values of E/E0
  0.24-0.59; sum m W/psi - M = +2.2e-4 to +3.0e-4 (predicted about 2e-4).
- Observation on the check itself (equilibria/check_equilibria.py): the KS p-value of the
  radii of the plain Monte Carlo sample is 0.277 for every model, here and in run
  C-sidm-20261115-121626-e99907d. The sampler draws radii by inverting the same rest-mass
  CDF that the test uses, with the same seed (11) for every model, so the statistic only
  tests the inversion and the uniforms of seed 11, not the radial distribution. The E/E0
  test (continuum CDF by a separate double integral) and the shell moments are the
  independent checks. [VERIFIED for the values; the reading is JUDGEMENT]

D1 (run C-20261115-170713-cefe1c2, diag_g2.py): the reference offset is the main cause.
Mean relative bias (50 realisations; G = as G2, A = exact reference):

| sigma | G | A | B no osc. | C no noise | D oracle window | E boxcar = period | F curve_fit (G) | H curve_fit (A) |
|---|---|---|---|---|---|---|---|---|
| 0.02 | +3.34% | -0.84% | -0.04% | -0.84% | +0.08% | -0.02% | +1.01% | +1.28% |
| 0.05 | +3.51% | -1.01% | -0.01% | -1.02% | +0.17% | -0.03% | +0.93% | +1.82% |
| 0.1 | +3.77% | -0.49% | +0.04% | -0.53% | +0.25% | +0.00% | +0.89% | +0.04% |

G reproduces +3.3 to +3.8 percent (predicted 2-4: PASS). With the exact reference the
bias falls to -0.5 to -1.0 percent (A); the prediction |bias| < 1 percent fails narrowly
for A and C at sigma = 0.05 (-1.01, -1.02 percent) and holds for B, D, E. The residual
-1 percent needs the oscillation (present in A and C, absent in B) and vanishes with a
boxcar of one oscillation period (E: below 0.03 percent, rms 0.4 percent, 3-SE coverage
0.82-1.00). The curve_fit estimator is not better (H up to +1.8 percent; at sigma = 0.1
its rms is 15-16 percent and its 3-SE coverage 0.12-0.16). Cause of G2 [VERIFIED by A
against G]: d = y - y(0) subtracts the initial mode amplitude, d = A(e^{sigma t} - 1),
which steepens ln|d| at the start of the window. Consequences for the threshold runs
[JUDGEMENT]: smooth over one core oscillation period, start the window well above the
initial amplitude, and measure the departure from the equilibrium value of the model
(alpha_c of the initial-data table) rather than from a perturbed first record. A
multiplicative bias of a few percent in sigma does not move the zero of sigma^2 along a
sequence, so the threshold location is insensitive to it; error bars should come from
independent samples (G3: 5.5 percent spread between three seeds).

### Prediction T1 (tov_check.py)

The three TOV failures are the truncation error of the central difference in the check
(step h = 1e-4 (R - r_in), about 2e-3 M), not a defect of the solved models (the
structure equations are integrated to rtol 1e-12, and the Hamiltonian-constraint residual
of the same models is 3e-8): halving h twice reduces the residual by about 4 each time
(ratios 3.5-4.5) for every b = 0.1 model, and all fall below 1e-6 at h/4. Refuted if a
ratio is below 2 or a residual stays above 1e-6 at h/4.

## 2026-11-15, entry 6: outcome T1; prediction A1

T1 PASS (run C-20261115-171723-17d46f0): halving the step of the TOV check reduces the
residual by 4.00 and then 3.99 for all 13 models; at h/4 the residuals are 1.4e-8 to
8.9e-8. The three M3 failures are the h^2 truncation error of the check's central
difference, which grows with the steepness of the core; the solved models satisfy TOV to
better than 1e-7. [VERIFIED]

### Prediction A1: AthenaK reads a b = 0.1 model at N = 10^5

`../equilibria/smoke_athenak.py` (two cycles, processor build of core-v0.3,
`.work/build_cpu_v03/src/athena`, 4 threads) on `tmb01_Z0p5404_stratified_N100000_s1` of
run C-20261115-170742-84990ed, with the paper's y_c = 0.819 model as reference. Expected:
both cases exit 0; np = 100000 in the first history record; sum m equal to the file's to
1e-13 relative; deposited int E equal to sum m W to 1e-12 (the King file of run
C-sidm-20261115-125308-54870b9 gave 1e-15); alpha_probe at t = 0 within 1 percent of the
model's alpha_c = 0.64918 (the King run read 0.6647 against 0.66141, 0.5 percent); the
initial Hamiltonian-constraint norm within a factor 3 of the reference's [JUDGEMENT; the
model is wider than the refined region of the deck, |x| < 15.9 M against rbar_s = 19.4 M].
Refuted by a failed run or any number outside these bounds.

## 2026-11-15, entry 7: outcomes M3 at N = 10^5; figures

Build run C-20261115-170742-84990ed (N = 10^5, 13 models, 16-17 s each, 80 MB); check run
C-20261115-171137-9e3c807 (exit 1 for the same three TOV checks as at 10^4).
- M3 at 10^5: 240 checks pass, the same 3 fail (TOV residual 1.1e-6, 1.2e-6, 1.4e-6 at
  Z(0) = 0.58, 0.60, 0.6348; explained by T1 as the check's own truncation error). Equal-mass
  shell counts 12500 x 8 exact, stratified ECDFs within 1/N, max E/E0 = 0.99992 (b = 0.1
  E_b maximum), KS statistic of E/E0 of the file 0.0020 (0.0014 King threshold), shell
  moments within 2.15 standard errors. sum m W/psi - M = -2.2e-5 to -4.0e-5 (10^4:
  +2.2e-4 to +3.0e-4); the prediction "smaller at 10^5" holds for every model. [VERIFIED]
- Centre resolution at 10^5 (index_N100000.json): 30 macroparticles per M/4 cell at the
  centre of the b = 0.1 E_b-maximum model (19 for the King threshold model, as
  stage/G1/STATUS.md section 4 estimated), proper spacing 0.118 M.

Figures (run C-20261115-173404-378c69e, copies in figs/; each looked at):
- `fig_fluid_onset`: Juttner Gamma_1 and 1 + p/u against theta; omega_0^2 R^3/M along the
  b = 0.1 sequence for the five indices with the roots; gamma(r) at the E_b maximum; onset
  Z(0) against b. The J_E curve lies below the E_b maximum at every b, the F21 curve above.
- `fig_models`: E_b(Z(0)) with the eight b = 0.1 models; n/n_c of the b = 0.1 and King
  threshold models with the density of the 10^5 files (counts over the continuum
  expectation), on the curve over five decades; E/E0 of the 10^5 file against the
  continuum; |sum m W/psi - M| of every file at both N.
- `fig_growth`: synthetic example and the 150 synthetic fits; departures and fits of the
  unperturbed y_c = 0.5 runs (alpha_c and r10); alpha_c of the three collapsing runs with
  the first apparent horizons and t(alpha_c = 0.2); the fitted plunge segments.
