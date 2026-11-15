# langevin: stochastic delta-N reference statistics (work package E-pre-3)

Reference statistics outside numerical relativity for Track E: a Langevin first-passage
solver for stochastic delta-N, its validation against analytic results printed in
1308.4754 and 2206.11234, reference distributions of delta N for the two test cases of the
reproduction specification (`../spec/SPEC.md`), and an assessment of the stochastic-lattice
comparison of 2405.10692. Everything here is a semi-analytic reference or an analysis tool
in the sense of decision 0010: zero-dimensional stochastic and ordinary differential
equations, no spatial simulation. Journal with predictions and outcomes: `JOURNAL.md`.

## Contents

| Path | What |
|---|---|
| `sdn/models.py` | potentials: quadratic with potential-position fixing, Higgs-like inflection with H0 fixing (locators in the file) |
| `sdn/langevin.py` | vectorised first-passage solvers: overdamped (Euler-Maruyama, Brownian-bridge crossing test, reflecting wall with exact image likelihood, importance sampling) and phase-space (RK4 drift + Ito noise with a 2x2 covariance, several end surfaces, Hermite crossing, importance sampling along the dominant noise direction) |
| `sdn/exact.py` | semi-analytic references: inverse Gaussian (drift-diffusion), moment recursion of the adjoint Fokker-Planck equation, BDF2 survival solver (density and Laplace transform), Sturm-Liouville eigenvalues, the closed-form characteristic function of quadratic inflation (2206.11234 appendix) |
| `sdn/linear.py` | classical background, flat-gauge linear modes with Bunch-Davies start, noise covariance tables at k_sigma = sigma a H, P_R(k), lattice shell counts |
| `scripts/run.py` | registers a run: `tracks/E-stoch-inf/runs/<run_id>/manifest.json`, output in `scratch/E-stoch-inf/<run_id>/` |
| `scripts/v1_drift_diffusion.py` | V1: exact drift-diffusion first passage (1308.4754) |
| `scripts/v2_quadratic.py` | V2: quadratic inflation, m = M_Pl (2206.11234, Fig. 2 set-up) |
| `scripts/ref_spec.py`, `scripts/ref_plot.py` | reference delta-N statistics for the two specification cases, and their figures |
| `scripts/ref_endinf.py` | end-of-inflation delta N of the inflection potential after USR |
| `results/*.json` | numbers of each registered run (the `run_id` field names the run) |
| `fig/*.png`, `fig/*.pdf` | figures (style `python/nrpic/figstyle.py`) |

## How to rerun

From the worktree root, with committed code (the wrapper refuses otherwise):

```text
P=tracks/E-stoch-inf/langevin/scripts
python3 $P/run.py --purpose "V1" --cores 8 -- python3 $P/v1_drift_diffusion.py      # ~2 min
python3 $P/run.py --purpose "V2" --cores 8 -- python3 $P/v2_quadratic.py            # ~2 min
python3 $P/run.py --purpose "ref" --kind production --cores 8 -- python3 $P/ref_spec.py inflection 1000000   # ~30 min
python3 $P/run.py --purpose "ref" --kind production --cores 8 -- python3 $P/ref_spec.py quadratic 1000000    # ~30 min
python3 $P/run.py --purpose "plots" --cores 4 -- python3 $P/ref_plot.py inflection /data/haiyangw/nrpic/scratch/E-stoch-inf/<run_id of ref_spec>
python3 $P/run.py --purpose "endinf" --cores 8 -- python3 $P/ref_endinf.py
```

Python 3.10 with numpy 2.2, scipy 1.15, mpmath 1.3, matplotlib 3.10 (system packages; no
virtual environment was needed). Seeds are fixed in the scripts (numpy SeedSequence).

## Validation (analytic answers printed in the papers)

V1, drift-diffusion X = mu N + W to m [runs E-stoch-inf-20261115-125312-dafadc4,
E-stoch-inf-20261115-125656-e3eaef3; `results/v1_drift_diffusion.json`, `fig/v1_drift_*.png`].
Reference: 1308.4754 v2 lines 341-364 (<N> = m/mu, var = m/mu^3, mu3 = 3 m/mu^5) and the
inverse Gaussian density.
- With the Brownian-bridge crossing test, the mean, variance and third moment at dN <= 0.003
  are within 2.1 standard errors of the exact values for (mu, m) = (1, 5) and (0.5, 2), with
  2e5 runs each. Without it the mean is biased high as c dN^p, p = 0.42 and 0.55.
- The binned density agrees with the inverse Gaussian bin by bin (mean z^2 0.83 to 1.27,
  max |z| <= 3.25). With importance sampling (constant bias) it continues down to
  P = 3.4e-14 at N = 60.6.
- The importance weights satisfy E_S[w] = 1 within 1.7 SE. With the sign printed in
  2206.11234 method.tex lines 78 and 151, E_S[w] is between 4.7e4 and 1.6e80: the printed
  sign is a typo (JOURNAL entries 2 and 6).

V2, quadratic inflation m = M_Pl, phi_in = phi_UV = sqrt42, phi_end = sqrt2 (2206.11234 Fig.
2 set-up) [run E-stoch-inf-20261115-125658-e3eaef3; `results/v2_quadratic.json`,
`fig/v2_quadratic_m1*.png`].
- Three independent semi-analytic references agree:
  - the closed-form characteristic function of appendix.tex lines 60-102;
  - the BDF2 survival solver;
  - the moment recursion.

  Laplace transforms agree to 5e-4 for J <= 1, means to 5e-5 and variances to 1e-6:
  <N> = 9.38603, var = 4.52154, skewness 1.0197, excess kurtosis 1.8997.
- Monte Carlo (1e6 runs, dN = 0.002): mean +2.9 SE, which is a first-order step bias of
  about 1.2 dN; variance -1.3 SE; density chi^2 per bin 0.93.
- Importance sampling (A = 0.8, naive estimator) reaches P = 6.7e-13 at N = 50. The tail
  slope there is -0.661, against the lowest Sturm-Liouville eigenvalue 0.652823.
- The closed form has its first poles at J = -0.6528232 and -1.0978390, matching the
  eigenvalues to 3e-7, and it is smooth through J = -v0/4. The statement of 2206.11234
  (appendix.tex 168-173) that Lambda_0 = v0/4 is the leading pole "in general" does not
  hold for finite phi_UV.

## Reference distributions for the reproduction specification

Set-up: background, fixing methods and N* of `../spec/SPEC.md` section 6, which are the
same as what this package derived independently from the paper sources:
- quadratic: phi0 = -14.0950, m = 1.734945e-6, N* - N0 = 5;
- inflection: phi0 = -1.2, dphi/dN = 0.102682, N* - N0 = 3.

The noise covers the lattice band of the NR runs, k from dk = a* H* to 64 dk
(L k_sigma* = 2 pi, N = 256, k_max = N dk / 4; 2512.14649 lines 509-512). Each mode enters
the separate-universe phase-space Langevin system when sigma a H = k. The noise covariance
in (phi, varpi) comes from the linear flat-gauge mode functions, with Bunch-Davies data at
N0.

delta N is measured from N* to the uniform-field surface phi_bg(N_e), with N_e = N* + 15
in both cases. For sigma = 0.01 the slice N_f = 13 of the NR runs is too early for the
inflection case: the variance there is 3.8 percent low, because the realisations are not
yet back on the attractor 1.2 e-folds after the last noise. For sigma = 1 and 0.1 the two
surfaces agree to 0.4 percent or better.

Results below are at N_e, with 1e6 realisations unless noted. Numbers come from
`results/ref_quadratic.json` (run E-stoch-inf-20261115-130139-176cdd6) and
`results/ref_inflection.json` (run E-stoch-inf-20261115-130137-176cdd6). Figures:
`fig/ref_<case>_setup.png` and `fig/ref_<case>_pdf.png`.

| | quadratic (SR) | inflection (USR) |
|---|---|---|
| linear band variance, continuum int P_R dln k | 3.9248e-10 | 0.79884 |
| linear band variance on the 256^3 lattice (sum over \|n\| <= 64) | 4.2407e-10 (x 1.0805) | 0.79863 (x 0.9997) |
| P_R across the band at N_e | 1.037e-10 to 8.53e-11 | 1.02e-5 to 1.017 |
| sigma = 0.01: var / var_lin | 0.9981 +- 0.0012 | 1.0001 +- 0.0016 |
| sigma = 0.01: skewness, excess kurtosis | 0.003 +- 0.003, 0.000 +- 0.005 | 0.038 +- 0.002, -0.001 +- 0.006 |
| sigma = 0.01: <N> - N_cl | -1e-9 | +0.0063 |
| sigma = 0.01: P(dN > 3 sigma_lin), P(dN < -3 sigma_lin) | 1.32e-3, 1.30e-3 | 1.57e-3, 1.14e-3 (Gaussian 1.35e-3) |
| sigma = 0.01: P(dN > 4 sigma_lin), P(dN < -4 sigma_lin) | 3.6e-5, 2.5e-5 | 3.6e-5, 2.5e-5 (Gaussian 3.2e-5) |
| sigma = 0.01, quantiles of dN at 1e-5 and 1 - 1e-5 | -8.31e-5, +8.58e-5 | -3.656, +3.819 |
| sigma = 0.01 with the lattice density of states: var / var_lattice | 1.0056 +- 0.0015 | 0.9905 +- 0.0016 |
| sigma = 0.1: var / var_lin | 1.0050 +- 0.0014 | 1.0055 +- 0.0016 |
| sigma = 1 (literal NR timing): var / var_lin | 1.4492 +- 0.0022 | 1.4233 +- 0.0023 |
| de Sitter noise (H/2pi)^2 in phi only, sigma = 0.01: var / var_lin | 0.789 +- 0.002 (2.5e5) | 5.65 +- 0.02 (2.5e5) |
| linear limit (amplitude x 1e-3), sigma = 0.01: var / var_lin | 1.0019 +- 0.0027 (2.5e5) | 0.9990 +- 0.0027 (2.5e5) |

What follows from the table:
- [VERIFIED by runs] For sigma <= 0.1, with momentum noise taken from the mode functions,
  the separate-universe Langevin system reproduces linear theory to 0.5 percent in both
  cases. It does so at full amplitude, not only in the linear limit.
- [VERIFIED by runs] With sigma = 1, the timing of the NR runs, the separate-universe
  variance is 1.42 to 1.45 times the linear one. Cause: a massless mode kicked into the
  separate universe at k = aH and evolved without gradients ends at
  |(1 - i) - 1/3|^2 = 13/9 = 1.444 times the frozen power (JOURNAL entry 8). So sigma = 1 is
  not a valid stochastic delta-N reference. The NR runs keep the gradients, so they must
  be compared with the sigma <= 0.01 numbers or with linear theory.
- [VERIFIED by runs] Noise as (H/2pi)^2 in phi only is wrong at sigma = 0.01:
  - in slow roll by -21 percent (delta phi grows like sqrt(eps1) after crossing);
  - in the USR case by a factor 5.6.

  During USR, the mode-function noise of the band modes at 0.1 a H and 0.01 a H is 1e-3
  to 1e-7 below (H/2pi)^2, in phi and in the momentum alike
  (`fig/ref_inflection_setup.png`, middle panel). The de Sitter kicks are therefore far
  too large, and the large N_phi of the USR phase turns them into a variance 5.6 times
  too large. 2405.10692 (footnote at line 351) uses phi-only noise and warns that USR
  models need more care. Only the mode-function covariance, momentum included, passes the
  linear-limit test here.
- [VERIFIED by runs] The lattice-band statistics are close to Gaussian in both cases: the
  inflection case has skewness 0.04 and a 16 percent enhanced 3 sigma tail at
  sigma_lin = 0.89 e-folds. 2512.14649 (line 534) reports "R ~ 10 for the furthest
  outliers" in real space. Under this one-point reference |zeta| = 10 would be an
  11 sigma_lin event, while the 1 - 1e-5 quantile is 3.8 e-folds. Comparing |zeta| with
  |R| assumes both are frozen super-Hubble values. [JUDGEMENT: either the NR extraction of
  R^NR (a linear combination, 2512.14649 lines 522-527) differs from delta N for large
  amplitudes, or their outliers come from something the separate-universe band does not
  carry; TO VERIFY with the NR reproduction.]
- On the 256^3 lattice the one-point variance of the quadratic case is 8 percent above the
  continuum value, because the low shells are over-populated relative to 4 pi n^2 dn. The
  NR acceptance should therefore compare with the lattice sum, not with int P_R dln k.

End of inflation for the inflection potential [run E-stoch-inf-20261115-130747-1b9bee4,
`results/ref_inflection_endinf.json`, `fig/ref_inflection_endinf.png`].
- After USR the classical field is delta_s = 2.03e-4 to the right of the exact inflection
  point, with eps1 = 9.8e-13 at N_s = 12. It takes 115.7 classical e-folds to reach
  delta = 1e-3 and 30.1 more to the end of inflation (eps1 = 1 at N = 157.8).
- Overdamped stochastic delta N from N_s gives <N> = 114.89 (0.78 e-folds shorter than
  classical) and var = 29.89, i.e. sigma_N = 5.47 e-folds; skewness 0.32, excess kurtosis
  0.22. This is from the moment recursion; the wall position and grid change these by
  less than 2e-4.
- The linear slow-roll integral over the same path is 29.73.
- So the end-of-inflation curvature perturbation of this potential is dominated by the
  post-USR creep, not by the USR peak. Its total variance is linear to 0.5 percent despite
  P_zeta ~ 1 per e-fold, because it accumulates over about 100 e-folds. For Track A this
  potential is not a source of large-but-rare perturbations at the end of inflation; only
  the band-limited (NR-box) statistics above are meaningful as initial-condition
  statistics [JUDGEMENT].
ENDINF_MC_PLACEHOLDER

## Stochastic-lattice comparison (2405.10692, STOLAS): what it would need, and when

What STOLAS does [VERIFIED: 2405.10692 v2 draft_JCAP.tex]:
- It evolves, on a 64^3 lattice, the separate-universe phase-space Langevin equations at
  every grid point (lines 320-332), with spatially correlated noise. At step N the noise is
  built in Fourier space from the shell |n| = n_sigma(N) +- 1/2, which gives the
  correlation sin(k_sigma r)/(k_sigma r) (lines 445-479).
- Its noise amplitude is the slow-roll NLO P_phi (lines 619-627), or the analytic USR
  formula of the linear-potential model (lines 697-718). The momentum noise is neglected
  (lines 351-356).
- Integration is Euler-Maruyama with an RK4 drift (lines 372-388).
- When all cells are super-Hubble, each cell is evolved with the classical delta N to a
  uniform-field end surface: zeta(x) = N_cl(phi(x), varpi(x)) - mean (lines 535-549).
- Production settings: sigma = 0.1, 1000 realisations (lines 639-640), and importance
  sampling with a sinc-profile bias for PBH statistics (lines 870-933).
- Its power spectrum agrees with linear theory for n >~ 4 (lines 642, 757).

What a comparison with our reproduction runs would need:
1. The same box, band and random numbers as the NR run. That means the same alpha_k from
   the counter-based generator (`core/rng`), so the comparison is cell by cell (zeta_SL(x)
   against R^NR(x) of one realisation) and not only statistical. Only a cell-wise
   comparison isolates what S11 asks about: gradients, shear and constraints.
2. Noise in phi and in the momentum from the mode functions. For the inflection case the
   phi-only noise is wrong by a factor 5.6 in the variance (table above). STOLAS as
   published would have to be extended.
3. sigma <= 0.01, or a correction for sigma: at sigma = 1 (the NR timing) the separate
   universe overestimates the variance by 42 to 45 percent.
4. An end surface at least about 3 e-folds after the last noise (finding above).
5. Under decision 0010 this is a simulation capability, so it belongs in AthenaK. The
   cheapest form is a separate-universe mode of core's scalar-field module, with gradient
   terms dropped and the metric frozen to the local FLRW, plus a per-cell output of the
   e-folds to a uniform-field slice. It would run with the same seed, box and noise
   kernels as the NR run, and the difference between the two runs is then exactly the
   effect of gradients and metric perturbations. The cost is negligible next to the NR run
   (independent ODEs per cell).

What it would add beyond this package [JUDGEMENT]:
- In the separate-universe approximation every cell is a draw of the same one-point
  process, so for one-point statistics (mean, variance, tails of zeta at the lattice
  resolution) a stochastic lattice adds nothing to the reference above. The lattice-DOS
  variant already accounts for the discrete box.
- It adds the two-point function and the spatial profiles: peaks, the compaction function
  (S11 deliverable 2, Track A), and the cell-wise comparison with the NR realisation.

Whether to do it before the feasibility gate [JUDGEMENT]: no.
- G0 needs the specification, the code-base assessment and the compute estimate.
- G1's acceptance of the reproduction (spectrum, freezing, constraints) is covered by
  linear theory and by the one-point references here.
- The comparison depends on two things that come after G0: core's scalar field with
  stochastic sources and the RNG interface (E-pre-4).
- Recommended placement: G2, as the "sensitivity to gradients and metric" item, run as an
  AthenaK separate-universe configuration with the seed of the NR run.
- Before G0, the only stochastic-lattice-type number worth having is the
  lattice-discreteness correction of the one-point variance, which is computed here.

## Requests

- To the E-stoch-inf lead (spec owner): confirm N* - N0 = 5 and 3 and N_f = 13 as used
  here; adopt N_e >= last noise + 3 e-folds for any delta-N comparison. Note in SPEC.md that
  the acceptance of the one-point variance must use the lattice sum (8 percent above the
  continuum in the quadratic case) and that sigma = 1 separate-universe numbers are not a
  reference. 2512.14649 line 534 ("a very shallow maximum is passed") does not match the
  printed potential, which has an exact inflection point at -sqrt2 v and no maximum on the
  path; line 108 lacks 3 M_Pl^2 in the Friedmann denominator.
- To core (through the lead): when the scalar field with stochastic sources lands in
  `athenak/src/`, a switch for a separate-universe mode (no gradient terms, metric frozen
  to the local FLRW) and a per-cell output of the e-folds to a uniform-field slice. That
  is enough for the stochastic-lattice comparison inside AthenaK with the seed of the NR
  run. Noise in both phi and Pi from the mode functions, as SPEC.md already specifies.
- To A-emd-pbh: the band-limited statistics of the inflection case (table above,
  `results/ref_inflection.json`, samples in `scratch/E-stoch-inf/E-stoch-inf-20261115-130137-176cdd6/`)
  are close to Gaussian (skewness 0.04). At the end of inflation this potential gives
  sigma_N = 5.5 e-folds from the post-USR creep. Neither is a PBH-relevant tail;
  initial-condition statistics for Track A need a different potential.
- To kb: the two errata of 2206.11234 (importance-weight sign, method.tex 78 and 151;
  leading pole v0/4, appendix.tex 168-173), with the runs above as evidence.

## Not done or open

- Importance sampling in the phase-space solver is implemented, but it was not validated
  and not used for the specification cases. Their tails are from direct sampling (1e6),
  so they reach probabilities of about 1e-5 only.
- The lattice density-of-states variant uses 0.05-wide bins in ln n. It agrees with the
  lattice sum to 0.6 and 1.0 percent, but the 1.0 percent is 6 standard errors, so the
  binning is an approximation at that level.
- The full stochastic delta N from N* to the end of inflation in one solver is not done.
  The end-of-inflation number starts from the classical state at N = 12, so it is
  conditional and omits the noise before N = 12.
- The sigma = 1 variance changes by 0.8 percent when the step is doubled (dN = 0.002 to
  0.004) in the inflection case. The smaller-sigma variants were not step-tested.
- The reweighted Laplace transform for the strongest V1 bias is off by 1.4 percent without
  an error estimate.
