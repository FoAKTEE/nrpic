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

## 2026-11-15, entry 8: outcome A1 (run C-20261115-174557-8978b36)

`../equilibria/smoke_athenak.py` with the processor build of core-v0.3 on
`tmb01_Z0p5404_stratified_N100000_s1` (run C-20261115-170742-84990ed), 4 threads, two
cycles, 205 s; reference y_c = 0.819 (make_ic.py, N = 10^4), 224 s. Results
(`results/athenak_smoke_tmb01_Z0p5404_N100000.json`, `figs/fig_smoke.png`, looked at):
- both cases exit 0, two cycles each; np = 100000 in the first record: PASS.
- sum m in AthenaK against the file: -1.08e-12 relative. The prediction (1e-13) FAILS by a
  factor 11. Not investigated; the size is that of the rounding of a sum of 10^5 equal
  terms in another order (MeshBlock partial sums against numpy) [JUDGEMENT, untested].
- deposited int E against sum m W at t = 0: 8.9e-15 (reference 4.7e-15): PASS.
- alpha_probe(0) = 0.65411 against alpha_c = 0.64918 of the model, +0.76 percent (limit
  1 percent): PASS. (The King file of run C-sidm-20261115-125308-54870b9 read +0.5 percent;
  the probe value of the reference here is 0.80939 against 0.80908.)
- squared Hamiltonian-constraint norm at t = 0, new over reference: 0.655 (limit: within a
  factor 3): PASS. Momentum-constraint norm 6.3 times smaller than the reference's (10
  times more particles).
- sum m W and int E change by +6e-6 over the two cycles (reference -7e-6).
So AthenaK reads the b = 0.1 table and a 10^5-particle file; one prediction bound (sum m to
1e-13) was set too tight.

Figures: final figure run C-20261115-175406-e8ffa67 (adds fig_smoke; the other three are
redrawn by the same code as run C-20261115-173404-378c69e); figs/ holds its output.

## 2026-11-20, entry 9 (wave 3, package models): the fixed estimator, its definition and predictions

Task: G1 open item 3 (`stage/G1/OPEN.md`), plan `PLAN-wave3.md` round 1, package 2. State
verified from the files: G1 passed 18/18 (run C-20261115-170346-298a1ba), G2 and G4 failed
(same run), D1 traced G2 to the reference y(0) (run C-20261115-170713-cefe1c2, table in
entry 5). Nothing of this package was left uncommitted by wave 2b/3a (`git status` clean).

### Disclosure: what I looked at before writing these predictions

The committed figure `figs/fig_growth.png` (wave 2), the decks and table headers of the
runs (`runs/st/*/st_*.athinput`, `cluster.tab`), and the first three records of
`runs/st/dir_yc0500_comp/st.nrpic.hst`: alpha_probe(0) = 0.5520453 against the table's
alpha_c = 0.5504417. I read the probe code (`athenak/src/particles/nrpic_io.cpp:73-135`):
the probe at the origin, a MeshBlock corner, is the mean of the lapse at the eight
surrounding cell centres, i.e. at isotropic radius r_p = (sqrt 3/2) dx. I have not
evaluated the table at r_p, so R1 below is not blind as to the size of the offset
(0.0016) but is as to its agreement.

### Definition of the fixed estimator (growth.growth_fit_v2), fixed before any run

1. Departure d = y - y_ref (or y/y_ref - 1 with relative=True). y_ref is a number (the
   model's equilibrium value as the probe samples it: the table lapse at r_p,
   `growth.probe_reference`), an array on the record times (a control run of the same
   model and seed), or 'first' (the old reference y(0), kept for comparison).
2. Period P of the oscillation: supplied, or measured from d: least-squares periodogram
   with a cubic trend (columns 1, t, t^2, t^3, sin, cos) over the record from t0 to the
   first time |d| (3-record running mean) reaches hi, trial periods from 5 M to 2/3 of that
   segment; P minimises the residual. The spacing of zero crossings of d minus the cubic
   trend is reported as a cross-check.
3. Centred boxcar of width P (on the median record step, as before).
4. Initial amplitude A_init = rms of the raw d over [t0, t0 + P].
5. Window: lo = k_lo A_init (default k_lo = 3), hi stated per use; it ends at the first
   |d_s| >= hi and starts after the last earlier |d_s| <= lo (as before). No window if
   ln(hi/lo) < 1.
6. sigma = least-squares slope of ln|d_s| in the window. Standard error
   se = (se_noise^2 + se_fit^2)^(1/2): se_noise is the exact linear propagation of white
   record noise of level s_n = std(diff d)/sqrt 2 (window plus one boxcar width) through
   the boxcar and the slope; se_fit is the old residual error inflated by
   sqrt(n/n_eff), n_eff = window length / P (at least 2).
7. Settings for the first paper's runs: y_ref = probe reference of the run's table and
   finest spacing at the origin at t = 0; P measured from the alpha_c record; k_lo = 3;
   hi = 0.1 (unperturbed y_c = 0.5) and 0.2 (collapsing runs), as before. r10: relative
   departure from r10(0) of the particle file (no continuum value at hand), P supplied
   from the alpha_c fit of the same run, (a) own window with hi = 0.3, (b) the time window
   of the alpha_c fit of the same run.

### Predictions

U (unit tests, `test_growth_v2.py`, synthetic): U1 the periodogram finds P = 25 M of a
noise-free sinusoid (amplitude 2e-3) on an exponential trend (1e-3 e^{sigma t}, sigma =
0.02, 0.05) within 1 percent, and within 5 percent with white noise 1e-3 per 0.25 M record;
U2 a pure exponential with exact reference: sigma to 1e-6 relative (a boxcar keeps the
slope of an exponential); U3 exponential plus oscillation, exact reference and supplied
exact period, no noise: sigma within 2e-3 relative; U4 reference given as an array (an
arbitrary drifting, oscillating control plus A e^{sigma t}): sigma within 1e-4 relative;
U5 propagated se_noise against the scatter of sigma over 200 noise realisations (no
oscillation): ratio between 0.85 and 1.15. Refuted by any failed bound.

R1 (probe reference): |alpha_probe(0) - alpha_table(r_p)| < 1e-5 for the four static-mesh
runs dir_yc0500_* (dx = M/4, r_p = 0.2165 M). For the adaptive-mesh runs (yc0500_v5,
yc0605_v5) the same bound holds for one of dx = M/4, M/8, M/16 (it names the finest level
at the origin at t = 0). Consequence stated now [JUDGEMENT]: if R1 holds, the lapse record
of a run started from the tabulated lapse holds no initial mode amplitude in y(0); then
'first' and the probe reference coincide on these runs to 1e-5 (1e-3 of lo), D1's
mechanism does not act on them, and on runs the fix changes only the boxcar and the
window start.

G2' (same synthetic signals as G2: seed 7, 50 realisations, sigma = 0.02, 0.05, 0.1 per
M, oscillation 2e-3 with P = 25 M, noise 1e-3; v2 with y_ref = 0.6 exact, P measured,
k_lo = 3, hi = 0.1): mean relative bias within +-1 percent for each sigma; rms below 2
percent; 3-SE coverage >= 0.90 for each sigma; 1-SE coverage between 0.50 and 0.97 (above
0.97 would mean the error is inflated); median measured P within 5 percent of 25 M for
sigma = 0.02, 0.05 and within 15 percent for 0.1. With y_ref = 'first' (otherwise the
same): mean bias between +1 and +6 percent for every sigma (D1's mechanism). The old
estimator repeats entry 4 exactly (+3.34, +2.92, +1.84 percent; 3-SE coverage 0.58, 0.90,
0.86). Refuted by any failed clause.

G1' (collapse and crossing times; code untouched): 18 of 18 again.

G3' (v2 on the three compensated y_c = 0.5 samples): rates within 15 percent of their
mean; each within 15 percent of its old value (0.0655, 0.0606, 0.0602) and inside
0.050-0.075 per M; measured P between 15 and 40 M, the three within 20 percent of each
other. The plain-filter run is recorded, not judged.

G4' [JUDGEMENT, low confidence]: (a) with r10's own window, at least one of the three
differs from its alpha_c rate by more than 20 percent (the early r10 record is a step and
a breathing of 2-6 percent, `fig_growth.png`, that the window start cannot clear below
hi = 0.3); (b) over the alpha_c time window at least two of three agree within 20 percent.
If (b) fails, the deliverable is the statement that early r10 and alpha_c are not one
linear mode over that window, with its evidence.

G5' (as written in entry 1, with v2 and hi = 0.2): sigma(y_c = 0.605) < sigma(0.500) in
the kicked runs; kicked y_c = 0.5 rate within 30 percent of the unperturbed mean; lead
t_AH - t(alpha_c = 0.2) within 0-6 M (unchanged code: 3.3, 1.8, 1.1 M). My expectation
[JUDGEMENT]: lead PASS, order holds in central values only, the 30 percent clause FAILS
again (the kicked runs have no linear phase above the floor; the window catches the
plunge).

G6' (fit settings, three compensated samples): width 0.8, 1, 1.25 P x k_lo 2, 3, 5 x hi
0.07, 0.1, 0.14 (27 settings): every rate that exists within 20 percent of the default;
at least 24 of 27 settings find a window per sample. Refuted otherwise.

K (reading of the wave-2 King runs, scouting, no threshold claim): d = alpha_c(collisional)
- alpha_c(control of the same model, seed and particle file), P measured from the control,
k_lo = 3, hi = 0.1, records before alpha_min < 0.3 and before the state turns non-finite;
window-choice error = half the range over the 27-setting grid of G6'. Expected: d < 0 in
all four (contraction); a window in all four; sigma(Kn = 1) in 0.04-0.15 per M and
sigma(Kn = 10) in 0.01-0.06 per M for both models; sigma(Kn = 1)/sigma(Kn = 10) between
1.5 and 10; sigma(CC1) >= sigma(CC2) at each Kn in central values (collapse times 72.5 <
77.8 M and 184 < 207 M, `threshold_scan/README.md`); window-choice error below 25 percent
of sigma. Refuted per clause.

### Entry 9, amendment before any run (2026-11-20, while writing the code)

Two details of the definition changed before anything was run: (i) the periodogram's
trend is 1, x, x^2 plus either x^3 or e^{s t} with s on 40 values in [0.002, 0.5] per M,
whichever leaves the smaller residual (a cubic misfits an exponential that grows by e^4.6
over the segment by about the oscillation's amplitude); (ii) the boxcar of v2 has exactly
the width P (records as cells, fractional end weights, `growth.boxcar_exact`); the old
`boxcar` rounds the width to an odd number of records, which leaves 1/k of an
oscillation of period P. The noise propagation uses these weights. The predictions are
unchanged.

## 2026-11-20, entry 10: outcomes U1-U5 (run C-20261120-222339-663f963); diagnosis of U5

Run `python3 tracks/C-sidm/models/test_growth_v2.py` (commit 663f963, registered, exit 1
because U5 failed; output `scratch/C-sidm/C-20261120-222339-663f963/test_growth_v2.json`).
[VERIFIED]
- U1 PASS: noise-free period 24.951-25.071 M against 25 (largest error 0.28 percent; the
  exponential trend wins with s = 0.0193 and 0.0519 for sigma = 0.02, 0.05); with noise the
  median of 20 realisations is 24.996 and 24.989 M (range 24.79-25.25).
- U2 PASS, U3 PASS, U4 PASS: sigma to the printed six digits (relative error below 5e-7)
  in every case; U4 finds the sign -1 of a contraction against an array reference.
- U5 FAIL at sigma = 0.1: median se_noise / scatter of sigma = 1.035 (0.02), 1.104 (0.05),
  1.660 (0.1; bound 0.85-1.15). Bias of the 200-realisation mean below 4.2e-4 relative.

Diagnosis (cause not yet tested): the noise level std(diff d)/sqrt 2 is taken over the
window plus one boxcar width beyond its end, where at sigma = 0.1 the exponential itself
reaches about 0.35 and grows by up to sigma d dt = 9e-3 per record, more than the noise's
1.4e-3 in a first difference; the trend inflates the level. Prediction for the rerun: the
first-difference level at sigma = 0.1 is above 1.3e-3 (median of 200) while at 0.02 it is
within 5 percent of 1e-3; the second-difference level (std/sqrt 6) is within 5 percent of
1e-3 at every sigma; with it the U5 ratio lies in 0.85-1.15 at all three sigma. Refuted if
the first-difference level at 0.1 is within 10 percent of 1e-3 (then the cause is
elsewhere) or the ratio stays outside the bound. Change: `growth.noise_level`, order 2 by
default (order 1 selectable); U5 now reports both levels. U1-U4 do not depend on it.

## 2026-11-20, entry 11: outcomes U5 rerun, R1, G1'-G6' (runs C-20261120-222454-8721534, C-20261120-222716-9d86ebc); predictions D2, D3

U5 rerun (run C-20261120-222454-8721534, exit 0) [VERIFIED]: U1-U4 repeat; U5 PASS with
the second-difference level: ratio 1.026, 1.022, 1.039. Cause test: the first-difference
level is 1.007e-3 (sigma = 0.02), 1.068e-3 (0.05), 1.588e-3 (0.1; predicted above 1.3e-3)
against 1.000e-3, 0.987e-3, 0.996e-3 from second differences (predicted within 5 percent):
the cause named in entry 10 is confirmed.

Validation run C-20261120-222716-9d86ebc (`validate_growth_v2.py`, commit 9d86ebc, 2 cores,
`growth_validation_v2.json`) [VERIFIED for every number]:

- Old estimator: identical to run C-20261115-170346-298a1ba (largest difference 0 in the
  G2 biases and coverages and in all six alpha_c rates; the 18 printed G1 values equal).
- G1' PASS: 18 of 18.
- R1 PASS: alpha_probe(0) - alpha_table(r_p) = -5.8e-9 (all four dir_yc0500_* and
  yc0500_v5), -5.3e-9 (yc0605_v5), -2.0e-9 (reconf_yc0756_hc), all at level 6 (r_p = 0.2165
  M; the adaptive runs start with level 6 as the finest at the origin). The model's
  alpha_c lies 0.0016 (y_c = 0.5), 0.0008 (0.605), 0.0002 (0.756 compressed) below. So on
  these runs y(0) is the equilibrium as the probe reads it; 'first' and the probe
  reference agree to 6e-9 and D1's mechanism does not act on them (the v2 rates with
  'first' equal those with the probe reference to the printed digits).
- G2' (v2, exact reference 0.6): mean bias -0.00 +- 0.06, -0.06 +- 0.06, +0.07 +- 0.09
  percent (PASS); rms 0.40, 0.45, 0.66 percent (PASS); 3-SE coverage 1.00, 1.00, 0.96
  (PASS); 1-SE coverage 0.76, 0.80, 0.42: FAILS at sigma = 0.1 (bound 0.50-0.97; the median
  error is 0.56 of the rms there, 1.15 at the other two); median P 25.00, 24.93, 24.91 M
  (PASS), but at sigma = 0.1 the range is 17.9-31.0 M (0.02: 24.89-25.08; 0.05:
  24.65-25.48). All 150 fits found a window (1.8-2.7 e-folds, median). G2' therefore FAILS
  on one clause. With 'first': +5.06, +5.15, +2.18 percent (PASS of the prediction +1 to +6:
  D1's mechanism, 3-SE coverage 0.10-0.30).
- G3' FAIL (not evaluable): with A_init = rms of d over the first period (P = 35.2, 31.7,
  31.3 M measured; zero crossings 22.5, 31.0, 30.5 M), A_init = 0.0174, 0.0139, 0.0101 and
  lo = 3 A_init leaves less than one e-fold below hi = 0.1 for comp and comp_s2; comp_s3
  gives 0.0480 +- 0.0026 per M over 33.5-57.8 M (1.18 e-folds), 20 percent below its old
  0.0602. The period clause holds (31.3-35.2 M, within 12 percent).
- G4': only comp_s3 is evaluable: r10 0.0559 +- 0.0046 with its own window (32-54 M), +17
  percent; 0.0530 +- 0.0038 over the alpha_c window, +10 percent. Prediction (a) not
  evaluable (one of three), (b) FAILS as stated (one of three evaluable, two required).
- G5': sigma(0.605) = 0.0529 +- 0.0070 (window 124-175 M, P = 36.5 M) < sigma(0.500
  kicked) = 0.0830 +- 0.0065 (57-92 M, P = 33.7 M): the order holds beyond the errors (wave
  2: not significant). Kicked against unperturbed: the unperturbed mean does not exist
  (G3'); against comp_s3 the kicked rate is 1.73 times larger, against the old mean 0.0621
  1.34 times: the 30 percent clause FAILS again, but the v2 windows now lie before the
  plunge (wave 2: 79-93 and 162-176 M, rates 0.17 and 0.16). Lead times unchanged (3.3,
  1.8, 1.1 M): PASS. Compressed y_c = 0.756: 0.0314 +- 0.0025 (25-123 M; wave 2 0.0265).
- G6' FAIL: comp_s3 (the only sample with a default window) finds a window in 18 of 27
  settings (none with k_lo = 3, hi = 0.07 or k_lo = 5, hi <= 0.1); the rates span
  0.038-0.063 (-20 to +32 percent of the default). The pattern is systematic: an earlier
  start (k_lo = 2) raises the rate (0.052-0.063), a later end (hi = 0.14) lowers it
  (0.043-0.047).
- On runs se_noise is 0.0000 (the lapse record is smooth from record to record): the
  run errors are the residual part only; the honest error of a run rate is the seed and
  window scatter.

Reading [JUDGEMENT, to be tested by D2]: the unperturbed y_c = 0.5 runs grow with
sigma P = 0.05 x 32 = 1.6-2 per period and hold about two e-folds between the floor and
the bend toward migration (|d| ~ 0.1 of a final 0.36); a one-period boxcar plus a start
at three times the first-period rms leaves less than one e-fold, and ln|d_s| is concave
over the rest, so the rate depends on the window. On the synthetic signals the estimator
is unbiased and its errors hold for sigma P <= 1.25 (sigma = 0.02, 0.05); at sigma P =
2.5 the error is too small by about 1.8 (D3 tests why).

### Prediction D2 (diag_v2.py, the three compensated y_c = 0.5 samples)

(a) Curvature: a quadratic a + b t + c t^2 fitted to ln|d_s| (v2 smoothing, measured P)
from the first smoothed time to the first |d_s| >= 0.14 has c < 0 in all three, and the
local rate at the end over that at the start, (b + 2c t1)/(b + 2c t0), is below 0.7 in all
three. Refuted if c >= 0 or the ratio >= 0.7 in any sample (then the window dependence of
G6' is noise, not curvature).
(b) A common fixed interval, from the latest first smoothed time of the three to the
earliest time any of them reaches |d_s| = 0.1 (`growth.slope_over`): the three rates lie
within 15 percent of their mean (seed scatter as in wave 2, 5.5 percent). Refuted
otherwise.

### Prediction D3 (G2' at sigma = 0.1)

The 29 realisations outside one SE have a median |P/25 - 1| more than twice that of the
21 inside: the excess error comes from misestimated periods, which neither error term
contains. Refuted otherwise (then the cause is elsewhere: window selection at 1.8
e-folds).
