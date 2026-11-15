# Journal of the package E-pre-3 / langevin (reference statistics outside NR)

Owner: E-stoch-inf (helper for E-pre-3). Entries are appended; nothing is rewritten.
Labels: [VERIFIED] read in a paper source with locator or measured in a registered run,
[BACKGROUND] standard result not checked against a source here, [JUDGEMENT], [TO VERIFY].
Paper sources: `kb-data/raw/arxiv/<id>/<v>/src` (fetched 2026-11-15 with nrpic-fetch-arxiv):
1308.4754 v2, 2206.11234 v2, 2405.10692 v2; read from earlier fetches: 2512.14649 v2,
2610.32592 v1.

## 2026-11-15 ~04:30 UTC, entry 1: sources read, potentials, set-up decisions

Read: 1308.4754 lines 158-720 (stochastic delta-N, first passage, drift-diffusion
analytic moments, numerical algorithm); 2206.11234 method.tex, demonstration.tex,
appendix.tex, intro.tex 10-40 (importance sampling, quadratic benchmarks and closed form);
2405.10692 lines 204-783, 870-960, 1123-1160 (STOLAS); 2512.14649 lines 94-133, 398-427,
476-547 (Langevin system, Table I, pipeline, lattice design); 2610.32592 chap_ICsim.tex
55-79 and 348-362 (fixing methods, inflection potential).

Potentials of the reproduction specification, read at the source (the spec helper had not
written them into a file when this package started):
- Quadratic, potential-position fixing [VERIFIED: 2610.32592 chap_ICsim.tex 63-71, 195;
  2512.14649 PRD_v2.tex 405-417]: eps1 = 0.01, eps2 = -0.02, H0 = 1e-5 M_Pl. From the
  formula: phi0 = -14.09500 M_Pl, m = 1.734945e-6 M_Pl, dphi/dN = +0.141421 (smoke test,
  not a registered number; the registered values are in results/ref_backgrounds.json).
- Higgs-like inflection [VERIFIED: 2610.32592 chap_ICsim.tex 350-359]: Lambda = 1.86e-6,
  v = 0.198 M_Pl, phi0 = -1.2 M_Pl, H0 fixing. The thesis writes the slow-roll velocity as
  "phi-dot_0 = -(V'/V) M_Pl^2" (line 74); dimensionally this is dphi/dN, and the dphi/dt
  reading would give dphi/dN ~ 1/H0 [JUDGEMENT: dphi/dN is meant; the spec helper raised the
  same ambiguity in spec/JOURNAL.md].
- dV/dphi = 2 Lambda v^5 phi (2 v^2 - phi^2)(sqrt2 phi + 2 v)/(3 phi^2 + 2 v^2)^3 (sympy):
  exact inflection point (double root of V') at phi = -sqrt(2) v = -0.280014 M_Pl, V' <= 0
  for all phi < 0, so the field cannot be trapped in a false minimum. 2512.14649 line 534
  speaks of "a very shallow maximum" being passed; the potential as printed has none on the
  path [JUDGEMENT; for the spec owner].
- 2512.14649 line 108 prints H^2 = V / (1 - pi^2 / (6 M_Pl^2)); the Friedmann constraint
  gives H^2 = V / (3 M_Pl^2 (1 - pi^2/(6 M_Pl^2))) [BACKGROUND]; I use the latter.

Smoke tests (unregistered, code checks only; numbers here are not results):
- Quadratic background: eps2(N0) = -0.0200000, N_end (eps1 = 1) about 50.2 e-folds after N0;
  linear P_R of the first lattice mode 1.037e-10 and frozen to 1e-4 between N = 12 and 20.
- Inflection background: USR from about N = 5.5 to 10 (eps2 up to 6.00), then eps1 ~ 1e-12,
  eps2 ~ -0.028 (agrees with 2512.14649 line 534), and the field creeps past the
  inflection point for about 150 e-folds: eps1 = 1 only at N about 158. In that phase the
  classical drift per e-fold (1.4e-6) equals the noise H/2pi (1.4e-6): quantum diffusion
  dominates. Consequence for the design: the reference for the NR comparison must stop at
  the slice of the NR runs (N_f), with the noise limited to the lattice band; the
  end-of-inflation statistics of this potential are a separate, diffusion-dominated object.
- Overdamped solver, constant drift: mean first-passage bias visibly smaller with the
  Brownian-bridge test; importance weights with the sign derived below give <w> = 0.996
  (2e4 runs), with the sign printed in 2206.11234 method.tex line 78 <w> ~ 1e10.
- Spectral solver: correct eigenvalues (constant drift: lowest 0.503 against mu^2/2 = 0.5),
  but for the quadratic m = 1 case the weight 2 psi / S^2 spans e^226 and the symmetrised
  eigenvectors lose all relative accuracy: replaced by the BDF2 survival solver
  (SurvivalPDE), which reproduces the inverse Gaussian density to 2e-4 at N = 40.
- Quadratic m = 1, phi_in = phi_UV = sqrt42, phi_end = sqrt2: lowest Sturm-Liouville
  eigenvalue 0.652823 (M = 2000, 4000, 8000 agree to 1e-6); the printed closed form
  (2206.11234 appendix.tex 60-102) is finite through J = -v0/4 and changes sign between
  J = -0.6528 and -0.6529 and between -1.09 and -1.10. So its first pole is at 0.6528, not at
  v0/4 = 5.28e-4 as appendix.tex lines 168-173 state ("This thus gives us the leading pole,
  Lambda_0 = v0/4 ... valid in general") [JUDGEMENT until the registered run V2 repeats it].

## 2026-11-15, entry 2: derivation of the importance-sampling weight sign

Sampled step dx = (D + B) dN + S sqrt(dN) xi with xi ~ N(0,1). Target density of the same
step: exp[-(B dN + S sqrt(dN) xi)^2 / (2 S^2 dN)]; sample density exp(-xi^2 / 2). Ratio:
ln w = -(B/S^2)(B dN / 2 + S sqrt(dN) xi) per step, so E_S[w] = 1. 2206.11234 method.tex
line 78 and line 151 print the exponent with a plus sign (ln w = +A^2 N/2 + A sqrt(N) xi for
B = A S), which gives E_S[w] = exp(A^2 <N>) != 1; 2405.10692 line ~912 (eq. lnwN) has the
minus sign. [JUDGEMENT: typo in 2206.11234; tested in V1.] With a reflecting wall the code
uses the exact two-image likelihood ratio of the reflected step.

## 2026-11-15, entry 3: predictions for V1 (drift-diffusion, 1308.4754) before the run

Set-up: X = mu N + W from 0 to m, (mu, m) = (1, 5) and (0.5, 2); 2e5 realisations per
step size dN = 0.1, 0.03, 0.01, 0.003, 0.001, with and without the bridge test; importance
sampling with constant bias B = -0.5 mu and -0.8 mu at dN = 0.003 (bridge on).
Exact [VERIFIED: 1308.4754 lines 353-364]: <N> = m/mu, var = m/mu^3, mu3 = 3 m/mu^5.
- P1a without bridge test the mean is biased high, bias ~ c dN^p with p = 0.5 +- 0.1
  (overshoot of discretely monitored Brownian motion [BACKGROUND]); refuted if p outside
  [0.4, 0.6] or the bias is not positive.
- P1b with the bridge test the bias at dN <= 0.003 is within 3 standard errors of zero for
  the mean and the variance; refuted otherwise.
- P1c the density at dN = 0.001 follows the inverse Gaussian within the bin errors down to
  P ~ 1e-4 (direct) and, reweighted, down to P ~ 1e-12 (B = -0.8 mu), no systematic
  deviation larger than 10 percent where a bin has more than 100 samples; refuted otherwise.
- P1d E_S[w] = 1 within 3 standard errors for the derived sign; the printed sign gives a
  mean weight > 10; the reweighted Laplace transform <exp(-N/2)> agrees with
  exp(m mu - m sqrt(1 + mu^2)) within 1 percent.

## 2026-11-15, entry 4: predictions for V2 (quadratic, 2206.11234) before the run

Set-up as 2206.11234 Fig. 2 [VERIFIED: demonstration.tex 25, 45, 53]: V = m^2 phi^2 / 2,
m = 1, phi_in = phi_UV = sqrt42, phi_end = sqrt2; direct sampling with 1e6 runs and
importance sampling with B = A H/(2 pi), A = 0.4 and 0.8 (2e5 runs each, naive estimator),
dN = 0.01 and 0.002 (the paper used 0.02, from the figure file name), bridge test on,
reflecting wall with the image likelihood ratio. Semi-analytic references: closed form
(appendix.tex 60-102), BDF2 survival solver, moment recursion.
- P2a the three semi-analytic references agree: Laplace transform at J = 0.01, 0.1, 0.3 to
  1e-3 relative; mean and variance (recursion vs BDF2) to 1e-3.
- P2b the Monte Carlo mean and variance agree with the recursion within 3 standard errors
  at dN = 0.002 (a dN = 0.01 bias of a few 1e-3 in the mean is allowed and reported).
- P2c the Monte Carlo density agrees with the BDF2 density within errors from the peak to
  P ~ 1e-5 (direct) and to P ~ 1e-10 (A = 0.8); the far tail decays at the lowest eigenvalue
  (smoke test 0.6528), not at v0/4 = 5.3e-4 (refuted if the measured slope between N = 20
  and the end of the A = 0.8 data is within 50 percent of v0/4 or differs from the
  eigenvalue by more than 10 percent).
- P2d the paper's statements: a direct sample of 2e5 reaches P ~ 1e-3 with more than 400
  per bin (demonstration.tex 53); I predict the same order (1e-3 to 1e-4 for bins of 0.25).

## 2026-11-15 ~13:00 UTC, entry 5: correction of entry 1's clock

Entry 1 is stamped "~04:30 UTC"; that was the machine's local clock (uptime). The run ids
(UTC) show the session time was about 12:30 UTC. Later entries use UTC from the run ids.

## 2026-11-15 ~13:00 UTC, entry 6: outcome of V1 (runs E-stoch-inf-20261115-125014-097160b,
E-stoch-inf-20261115-125312-dafadc4, E-stoch-inf-20261115-125656-e3eaef3; same seeds, the
later runs add per-bin metrics and fix the plot; numbers from results/v1_drift_diffusion.json)

- P1a PASSED: mean bias without the bridge test positive, fitted exponent 0.42 (mu = 1, m = 5)
  and 0.55 (mu = 0.5, m = 2), coefficients 0.43 and 0.69 (times mu).
- P1b PASSED: with the bridge test, at dN = 0.003 and 0.001 the mean is within 2.1 standard
  errors and the variance within 2.0 standard errors of m/mu and m/mu^3 (20 batch means), and
  the third moment within 1.8.
- P1c PASSED in the z sense: per-bin mean z^2 = 0.83 to 1.27, max |z| <= 3.25 over up to 117
  bins with >= 100 samples, no trend in the residual panels (fig/v1_drift_*.png). Individual
  bins with ~100 samples deviate up to 25 percent, which is their statistical error; the
  wording "no deviation larger than 10 percent" in the prediction was too strict for bins of
  100. Reweighted densities reach P = 3.4e-14 at N = 60.6 (mu = 1, m = 5, B = -0.8).
- P1d PARTLY FAILED: E_S[w] = 1.0045 +- 0.0027, 0.9965 +- 0.0056, 0.9988 +- 0.0010,
  0.9996 +- 0.0016 (all within 1.7 SE); the printed sign of 2206.11234 gives E_S[w] = 2.0e6,
  1.6e80, 4.7e4, 2.3e24 [VERIFIED by run: the printed sign is wrong]. Reweighted
  <exp(-N/2)>: +0.63, -1.36, -0.47, -0.14 percent from exact; the strongest bias (B = -0.8,
  mu = 1) is outside the predicted 1 percent. No standard error was computed for this
  estimator, so I do not claim whether this is statistical; the strongly biased sample has
  few short paths, which dominate exp(-N/2) [JUDGEMENT].

## 2026-11-15 ~13:00 UTC, entry 7: outcome of V2 (run E-stoch-inf-20261115-125658-e3eaef3;
the first run E-stoch-inf-20261115-125316-dafadc4 computed the same numbers and failed at the
JSON dump; results/v2_quadratic.json, fig/v2_quadratic_m1*.png)

- P2a PASSED: BDF2 (M = 8000) vs closed form, <exp(-J N)> at J = 0.01, 0.03, 0.1, 0.3, 1:
  relative differences 4.7e-6, 1.4e-5, 4.7e-5, 1.4e-4, -5.0e-4. <N> = 9.38603 (recursion
  M = 40000), 9.38553 (BDF2 M = 8000); var = 4.521540 and 4.521537. Skewness 1.0197, excess
  kurtosis 1.8997 (recursion).
- P2b PASSED, with a visible step bias in the mean: Monte Carlo (1e6, bridge test) mean
  9.39014 +- 0.00144 at dN = 0.002 (+2.9 SE) and 9.39801 +- 0.00215 at dN = 0.01 (+5.6 SE),
  i.e. a first-order step bias of about +1.2 dN; variance 4.5110 +- 0.0080 (-1.3 SE). The
  Laplace transforms of the Monte Carlo are low by J x 0.004, the same bias.
- P2c PARTLY FAILED: direct sampling agrees with the BDF2 density (chi^2 per bin 0.93, max
  |z| 2.6, 62 bins) but only reaches P = 4.2e-4 with >= 100 per bin of 0.25: my "1e-5" was an
  arithmetic error (1e6 x 0.25 x 1e-5 = 2.5 counts). Importance sampling A = 0.4 reaches
  6.6e-6 (chi^2 per bin 1.09, max |z| 4.0), A = 0.8 reaches 6.7e-13 at N = 50 but with chi^2
  per bin 1.66 and single bins off by up to 177 percent: the naive estimator underestimates
  its errors when the weights are broad, as 2206.11234 method.tex 131-136 says. Tail slope
  of the A = 0.8 data over N = 20-50: -0.6606, against -lambda_0 = -0.652823 (1.2 percent)
  and far from -v0/4 = -5.3e-4. PASSED for the slope.
- Pole structure [VERIFIED by run]: lowest eigenvalues 0.652823, 1.097839, 1.557003 (M = 4000
  and 8000 agree to 1e-6); the closed form has sign-changing poles at J = -0.6528232 and
  -1.0978390 and is smooth through J = -v0/4 (1.004961 at -0.999 v0/4, 1.004971 at
  -1.001 v0/4). So appendix.tex lines 168-173 of 2206.11234 ("Lambda_0 = v0/4 ... the
  leading pole ... valid in general") is wrong for finite phi_UV: at alpha = 0 the two
  branches f and g coincide and the singularity is removable; the leading pole is the lowest
  Sturm-Liouville eigenvalue. For phi_UV -> infinity the spectrum becomes continuous above
  v0/4 (their lines 189-211), which is where v0/4 does play a role [JUDGEMENT].
- P2d: a direct sample of 2e5 with > 400 per 0.25-wide bin reaches P = 9.2e-3; the paper's
  "~1e-3" depends on its bin width, which the text does not give. Not a test.

## 2026-11-15 ~13:05 UTC, entry 8: predictions for the reference runs (ref_spec.py) before
any reference number was seen (the smoke test at n = 3200 was started but not read)

Common: band k in [dk, 64 dk], noise entering at sigma a H = k; surfaces phi_bg(N_f) and
phi_bg(N_e) (N_f = 13 both, N_e = 20 quadratic, 18 inflection); var_lin = continuum
int P_R(k, N_e) dln k over the band.
Quadratic (slow roll):
- R1a classical variant: crossing times equal the solve_ivp background to 1e-9.
- R1b linear limit (sigma = 0.01, amplitude 1e-3): var / 1e-6 = var_lin within 1 percent.
- R1c sigma = 0.01: var = var_lin within 1 percent; skewness and excess kurtosis consistent
  with 0 (|z| < 3); the delta N formula estimate is skewness ~ 1e-5 [JUDGEMENT].
- R1d sigma = 0.1: var/var_lin = 1.003 +- 0.004; sigma = 1: var/var_lin in [1.3, 1.6]
  (massless de Sitter mode kicked into the separate universe at k = aH and evolved without
  gradients ends at |(1 - i) - 1/3|^2 = 13/9 of the frozen power [derivation in this entry]).
- R1e de Sitter noise (H/2pi)^2 at sigma = 0.01: var/var_lin in [0.75, 0.9] (delta phi of a
  slow-roll mode grows like sqrt(eps1) after crossing and H falls; estimate 0.82).
- R1f lattice density of states: var / var_lin_lattice within 1 percent; var_lin_lattice /
  var_lin differs from 1 by less than 10 percent.
- R1g the two surfaces give the same variance within 0.5 percent where both lie after the
  noise window (sigma = 1, 0.1).
Inflection (USR):
- R2a classical variant equal to the background to 1e-6 e-folds.
- R2b linear limit at sigma = 0.01 reproduces var_lin within 2 percent (the separate-universe
  Langevin system with momentum noise from mode functions is linear theory at sigma << 1).
- R2c sigma = 0.01 full amplitude: positive skewness, |skewness| < 0.5; var/var_lin within
  10 percent; mean shift <N> - N_cl positive and below 0.1 e-fold. Refuted if the skewness is
  negative or larger than 0.5, or the variance ratio is outside [0.9, 1.1].
- R2d sigma = 1 differs from linear by more than 10 percent in the variance; sigma = 0.1
  within 10 percent.
- R2e de Sitter noise at sigma = 0.01 differs from var_lin by more than 20 percent.
- R2f the two surfaces (N_f = 13, N_e = 18) agree in variance within 1 percent (R frozen
  after USR).

## 2026-11-15 ~13:10 UTC, entry 9: predictions for the end-of-inflation run (ref_endinf.py)

Inflection potential, overdamped Langevin from the classical state at N_s = 12 (post-USR,
delta_s = phi + sqrt2 v ~ 2.0e-4) to phi_a = -sqrt2 v + 1e-3, reflecting wall at
delta_L = -4.9e-4 (variant -1e-3). Hand estimate: drift D ~ kappa delta^2 with
kappa ~ 35 (from dphi/dN = 1.4e-6 at delta = 2e-4), S = H/2pi ~ 1.42e-6; linear variance
int S^2/D^2 dN = S^2 / (5 kappa^3 delta_s^5) ~ 29; classical duration 1/(kappa delta_s)
~ 143 e-folds (114 to phi_a); diffusion width of the inflection region
(S^2/kappa)^(1/3) ~ 4e-5.
- E1 the linear slow-roll integral int H^2/(8 pi^2 eps1) dN from N_s to the end lies in
  [15, 60].
- E2 recursion, BDF2 and Monte Carlo agree: mean and variance within 3 standard errors of
  the Monte Carlo; recursion M = 250k vs 500k within 1e-3.
- E3 the stochastic variance differs from the linear estimate by more than 20 percent,
  the skewness exceeds 1 and the tail is exponential with the lowest eigenvalue as rate.
- E4 moving the reflecting wall from -4.9e-4 to -1e-3 changes mean and variance by less
  than 1e-3 relative.
Refuted item by item if outside these ranges.

## 2026-11-15 ~13:15 UTC, entry 10: outcome of the reference runs
(quadratic E-stoch-inf-20261115-130139-176cdd6, inflection E-stoch-inf-20261115-130137-176cdd6;
figures by E-stoch-inf-20261115-131133-02047c4 and -131232-02047c4; results/ref_*.json)

Predictions written in entry 8 and committed in 176cdd6 before the reference numbers were
read. The n = 3200 smoke test of the inflection case was read only after that commit.
Quadratic:
- R1a PASSED: classical variant within 4.4e-13 e-folds of the background.
- R1b PASSED: linear limit 1.0019 +- 0.0027.
- R1c PASSED: var/var_lin = 0.9981 +- 0.0012; skewness 0.0031 +- 0.0025, excess
  kurtosis 0.0002 +- 0.0054.
- R1d PASSED: sigma = 0.1 gives 1.0050 +- 0.0014 (estimate 1.0034); sigma = 1 gives
  1.4492 +- 0.0022 (range [1.3, 1.6]; massless estimate 13/9 = 1.4444, 2.2 SE away, the
  rest being slow-roll corrections) [JUDGEMENT on the residual].
- R1e PASSED: de Sitter noise 0.789 +- 0.002 (estimate 0.82).
- R1f PASSED: var / var_lattice = 1.0056 +- 0.0015; var_lattice / var_lin = 1.0805.
- R1g PASSED: N_f and N_e variances agree to 5e-6 (sigma = 1, 0.1).
Inflection:
- R2a PASSED: classical within 2.3e-9 e-folds.
- R2b PASSED: linear limit 0.9990 +- 0.0027.
- R2c PASSED: var/var_lin = 1.0001 +- 0.0016; skewness +0.0381 +- 0.0021 (positive,
  < 0.5); <N> - N_cl = +0.0063 (positive, < 0.1).
- R2d PASSED: sigma = 1 gives 1.4233 +- 0.0023 (> 10 percent off); sigma = 0.1 gives
  1.0055 +- 0.0016 (within 10 percent).
- R2e PASSED: de Sitter noise 5.65 +- 0.02.
- R2f PARTLY FAILED: N_f vs N_e agree to 0.4 percent (sigma = 1) and 0.15 percent
  (sigma = 0.1), but for sigma = 0.01 the variance at N_f = 13 is 3.8 percent low and the
  skewness is 0.20 instead of 0.04. N_f is only 1.2 e-folds after the last noise
  (N = 11.81); the attractor relaxes as e^(-3 dN), and e^(-3.6) = 0.03 has the size of
  the discrepancy [JUDGEMENT on the cause; a run with a surface at N = 15 would test it,
  not done].
Further, not predicted:
- The sigma = 1 inflection variance changes by 0.8 percent (2.4 SE) when dN is doubled to
  0.004: a small step error.
- For the inflection case the lattice variant is 0.9905 +- 0.0016 of the lattice sum
  (within 1 percent but 6 SE). The 0.05 bins in ln n of the density of states are an
  approximation at this level.

## 2026-11-15 ~13:35 UTC, entry 11: outcome of the end-of-inflation run
(E-stoch-inf-20261115-130747-1b9bee4; figure and tail slopes E-stoch-inf-20261115-132724-cab7451;
results/ref_inflection_endinf*.json)

- E1 PASSED: linear slow-roll integral from N_s = 12 to the end is 29.74 (in [15, 60]);
  P_zeta per e-fold at N_s is 1.024.
- E2 PASSED at dN = 0.005: recursion (M = 500k) <N> = 114.894, var = 29.891; BDF2 114.869,
  29.891; Monte Carlo 1e5 114.888 +- 0.016 (-0.4 SE), 29.98 +- 0.12 (+0.7 SE). At
  dN = 0.02 the mean is +3.8 SE (step bias). Recursion M = 250k vs 500k: 2e-4 in the mean,
  2e-7 in the variance (the 1e-3 criterion holds).
- E3 REFUTED as stated: the variance is 0.5 percent above the linear 29.73 (I predicted a
  difference of more than 20 percent) and the skewness is 0.32 (I predicted more than 1).
  Its tail part holds in substance: the right tail is exponential with local slope -0.49 to
  -0.51 per e-fold between 6 and 12 sd. But that rate is not the lowest eigenvalue of the
  symmetrised operator (3.7e-4), which does not show at all; unresolved (README, "Not done").
- E4 PASSED: reflecting wall at -4.9e-4 vs -1e-3 changes the mean by 6e-5 relative and
  the variance by 1e-8.
- Classical vs stochastic mean: <N> is 0.78 e-folds shorter than the classical 115.68
  [VERIFIED by run]. A convex drift (D ~ kappa delta^2) speeds up the average passage
  [JUDGEMENT on the cause].
