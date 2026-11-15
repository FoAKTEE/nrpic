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
