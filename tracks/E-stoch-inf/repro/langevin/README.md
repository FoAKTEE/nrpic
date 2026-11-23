# repro/langevin: arXiv:2401.08530, section V (Langevin equations in the uniform-field gauge)

Reproduction of the numerical part of "Stochastic Inflation in General Relativity"
(arXiv:2401.08530 v2; source `kb-data/raw/arxiv/2401.08530/v2/src/Stochastic_Inflation.tex`,
cited `SI.tex:<line>`): two coupled Langevin equations for the lapse alpha and the e-folds N of
one patch, time = background e-folds N_b, fifty thousand paths, four figures and the
statements of SI.tex:842-875. Decision 0028 item 1. This is a zero-dimensional stochastic ODE,
a semi-analytic reference outside `athenak/src/` in the sense of decision 0010; the paper
itself says no numerical-relativity code exists in this gauge (SI.tex:879). Journal with
every prediction and outcome: `JOURNAL.md`. No card time used.

## Contents

| Path | What |
|---|---|
| `lsde.py` | background (forward Euler or RK4), noise amplitude of SI.tex:838, the printed equations SI.tex:806 and 825-826, integrators: Stratonovich Heun, Euler-Maruyama on the Ito-equivalent drift, Euler-Maruyama on the printed drift (Ito reading); linear-theory covariance ODE |
| `simulate.py` | the four backgrounds and the 21 variants (50 000 paths each); writes `var_<name>.npz`, `bg_<name>.npz`, `summary.json` |
| `analyse.py` | figures, KDE with bootstrap bands (Silverman bandwidth, 200 resamples), tail tests, bootstrap moments, window medians; writes `langevin.json` |
| `figstyle.py` | copy of `python/nrpic/figstyle.py` |
| `results/langevin.json` | every number below (backgrounds, per-variant moments at N_b = 3 ... 6, window medians over [4.5, 6], tail tests, linear check) |
| `results/simulate_summary.json` | per-variant moments at the record times, dead paths, wall times |
| `fig/*.png` | our figures (none of the paper's) |

Registered runs (manifests in `tracks/E-stoch-inf/runs/<id>/`, output in
`scratch/E-stoch-inf/<id>/`, one core each, scouting):

| Run | What |
|---|---|
| `E-20261123-020327-e524721` | run 1: backgrounds and 16 variants |
| `E-20261123-020746-78d0c54` | analysis of run 1, FAILED (plotting keyword), kept on record |
| `E-20261123-020825-1a01a96` | analysis of run 1 |
| `E-20261123-021043-d00a314` | run 2: all 21 variants (run 1 repeated bit for bit, plus the Ito-reading set) |
| `E-20261123-021647-46097e6` | analysis of run 2 |
| `E-20261123-021843-813759b` | analysis of run 2, final (title margin only); `results/` and `fig/` come from it |

## How to rerun

From the worktree root, with committed code (about 6 min and 2 min on one core):

```text
harness/bin/nrpic-run submit --kind scouting --gate G2 --purpose "..." --package tracks/E-stoch-inf/repro/langevin --cores 1 -- python3 tracks/E-stoch-inf/repro/langevin/simulate.py '$NRPIC_RUN_DIR'
harness/bin/nrpic-run submit --kind scouting --gate G2 --purpose "..." --package tracks/E-stoch-inf/repro/langevin --parent <sim run> --cores 1 -- python3 tracks/E-stoch-inf/repro/langevin/analyse.py /data/haiyangw/nrpic/scratch/E-stoch-inf/<sim run> '$NRPIC_RUN_DIR' --install tracks/E-stoch-inf/repro/langevin
```

Seeds are fixed (numpy PCG64 with SeedSequence(seed), seed 1 unless the variant says
otherwise); run 2 repeated run 1 exactly.

## Set-up and the choices the paper leaves open

As printed: V = V0 to phi_c = 9.056, V0 [3x^2 - 2x^3] below; phi* = 10, dphi/dN* = -2.0001,
V0 from the Friedmann constraint with H* = 1e-5 (V0 = 9.998e-11), M_Pl = 1 (SI.tex:847);
noise on for 2 <= N_b < 6, step 0.01, 50 000 paths, start alpha = 1, N = N_b (SI.tex:842);
amplitude (3/2pi) H / sqrt(2 eps1) on the background (SI.tex:838, 1072); eps2 = -d ln eps1/dN
(SI.tex:919, so eps2 = +6 in USR). Choices [JUDGEMENT]:

1. Background integrator. The converged background never reaches the slope: on the plateau
   the field stops at phi = 10 - (1/sqrt6) ln((sqrt6 + 2.0001)/(sqrt6 - 2.0001)) = 9.06402,
   above phi_c [VERIFIED analytically and by RK4]. Forward Euler at step 0.01 crosses phi_c at
   N_b = 3.0435, the paper's "about 3.04" (SI.tex:842); Euler at 0.005 stops at 9.0600, Heun at
   0.01 at 9.06393. We take the Euler-0.01 background as the paper's; this explains its
   footnote that the tuning depends on the step of 0.01.
2. Interpretation. The paper says it used Mathematica's Stratonovich evolver (SI.tex:836) and
   derives the alpha^3 <S^2> term with Ito's lemma (SI.tex:814-822). Our baseline `base` is the
   printed equation read as Stratonovich (Heun). We also solve the Ito reading (Euler-Maruyama
   on the printed drift, `ito_naive`) and the Ito-equivalent of the Stratonovich reading
   (`ito_em`).
3. Ito's lemma on f(Z) = phidot_b/Z with noise alpha S_Pi gives alpha^5 <S_Pi^2>/phidot_b^2,
   not the printed alpha^3 (SI.tex:817); the paper leaves the multiplier "undecided"
   (SI.tex:814). We use the printed alpha^3.
4. "alpha^3 set to 1" (SI.tex:875): set to 1 both in front of the noise and in the Ito term.
5. KDE: Gaussian kernel, Silverman bandwidth, 95% pointwise bootstrap band (200 resamples).
   Caption SI.tex:861 says "five" times and lists four (3, 4, 5, 6); we use the four.
6. A path with |alpha| > 50 or not finite is stopped and left out of the moments (counted).

Values of the paper read off its figures (`plot2v2.png`, `plot2bv2.png`, `plot4v2.png`;
widths from the peak of the dashed Gaussian, sigma = 1/(peak sqrt(2 pi))) appear only in this
text: std(alpha - 1) = 0.0066, 0.117, 0.133, 0.121 and std(N - N_b) = 0.0016, 0.042, 0.150,
0.190 at N_b = 3, 4, 5, 6; kappa3(alpha) ~ 1.1 and kappa4(alpha) ~ 3 (spiky) from 4.2 on;
kappa3(N), kappa4(N) peak ~0.6, ~0.8 near 4.4 and reach ~0.3, ~0.2 at 6. Reading accuracy
about 3-5%.

## Results and verdicts

Numbers from `results/langevin.json` (analysis `E-20261123-021843-813759b` of run
`E-20261123-021043-d00a314`). Main finding [JUDGEMENT, from statistics, not from the
authors]: the paper's four figures are matched to within the reading accuracy by the Ito
reading of the printed equations at step 0.01 on the Euler-0.01 background, and NOT by the
Stratonovich reading it states. The convergent Stratonovich solution (Heun and Ito-equivalent
agree at h = 0.001 within 0.6%) is 8-20% wider at N_b = 4-6, has kappa3(alpha) ~ 1.6 instead
of ~1.1, and a mean N - N_b = 0.085 at N_b = 6 (the paper's 100-path mean ~0.01-0.02).

| Width | paper (read off) | Ito reading, seeds 1/2/3, h = 0.01 | Ito reading h = 0.001 | Stratonovich (Heun), h = 0.01 |
|---|---|---|---|---|
| std alpha, N_b = 4 | 0.117 | 0.1168 / 0.1173 / 0.1167 | 0.1225 | 0.1263 |
| std alpha, 5 | 0.133 | 0.1365 / 0.1339 / 0.1331 | 0.1311 | 0.1688 |
| std alpha, 6 | 0.121 | 0.1207 / 0.1207 / 0.1207 | 0.1198 | 0.1443 |
| std N, 4 | 0.042 | 0.0425 / 0.0427 / 0.0426 | 0.0454 | 0.0461 |
| std N, 5 | 0.150 | 0.1498 / 0.1506 / 0.1497 | 0.1549 | 0.1707 |
| std N, 6 | 0.190 | 0.1853 / 0.1864 / 0.1856 | 0.1900 | 0.2171 |
| median kappa3(alpha) on [4.5, 6] | ~1.1 | 1.04 / 1.13 / 1.14 | 1.08 | 1.59 (seeds 2-4: 1.53-1.64) |
| median kappa4(alpha) on [4.5, 6] | ~3 | 4.41 / 3.02 / 3.18 | 2.83 | 7.23 |
| median kappa3(N), kappa4(N) on [4.5, 6] | ~0.3-0.5, ~0.2-0.5 | 0.34-0.36, 0.17-0.25 | 0.35, 0.22 | 0.46, 0.41 |
| mean N - N_b at 6 | ~0.01-0.02 (100 paths) | 0.0034 / 0.0033 / 0.0024 | 0.0046 | 0.085 |

Per figure:
- Fig. 1 (paths, `fig/fig1_paths.png`, `fig/fig1_paths_ito_naive.png`): REPRODUCED. Noise
  visible from ~3.2, alpha spread -0.3 to +0.6 with spikes to ~1 after 4, N - N_b fans out to
  +-0.4 and freezes; widths as in the table (Ito reading within 4%; Stratonovich 8-20% wider,
  with a drifting mean of N - N_b).
- Fig. 2 (skewness, kurtosis, `fig/fig2_moments_ito_naive.png`, `fig/fig2_moments.png`):
  REPRODUCED with the Ito reading (kappa3(N) and kappa4(N) peak at ~0.58 and ~0.68 near 4.35,
  read off our figure, then fall to 0.27 and 0.11 at 6; kappa3(alpha) plateau ~1.05; kappa4(alpha) 2.5-4.5 with spikes).
  REPRODUCED IN PART with the Stratonovich reading (same shapes for N; kappa3(alpha) ~1.6,
  kappa4(alpha) ~7 with spikes to 400). Single-time kurtosis of alpha is dominated by a few
  paths near blow-up (14 of 50 000 stopped in `base`, 0-2 in the Ito reading), so it is not a
  stable statistic (seed 3: 3143 at N_b = 5).
- Fig. 3 (PDFs with Gaussians and bootstrap bands, `fig/fig3_pdfs_ito_naive.png`,
  `fig/fig3_pdfs.png`): REPRODUCED. Gaussian at N_b = 3; at 4-6 alpha peaked left of its mean
  with a long right tail, N - N_b mildly right-skewed; the Ito-reading KDE peaks (read off our
  figure: 59/245, 3.75/9.7, 3.45/2.75, 3.8/2.15 for alpha/N at 3/4/5/6) match the paper's to a
  few per cent.
- Fig. 4 (log PDFs, `fig/fig4_logpdfs.png`, `fig/fig4_logpdfs_ito_naive.png`): REPRODUCED,
  including straight right tails from N_b = 4 and the sharp left cut-off of alpha.

Per statement:
- USR from ~2 e-folds, eps1 << 1, eps2 ~ 6 (SI.tex:842): REPRODUCED; eps1 < 1e-2 and
  |eps2 - 6| < 0.03 from N_b = 1.06; eps1(2) = 3.2e-5 (`fig/fig_background.png`).
- Slope reached at ~3.04, velocity then rises extremely slowly in USR (SI.tex:842):
  REPRODUCED only with the Euler-0.01 background (3.0435; |phi'| falls to its minimum
  9.2e-6 at N_b = 5.41, eps2 = 4.07, 0.34, -0.12 at 4, 5, 6). With the converged background
  the slope is never reached, sigma grows like e^{3N} and half the paths blow up by
  N_b = 4.75-4.8 (86-88% by 6; `bg_exact`, `bg_e005`; `fig/fig_step_seed.png`).
- Exponential tails between 3 and 4 e-folds (SI.tex:871): lapse REPRODUCED (exceedances above
  the 90% quantile, N_b = 4 to 6, Stratonovich and Ito reading: coefficient of variation
  0.97-1.12 against 1 for an exponential and 0.87 for the Gaussian tail, 1.6 once where one
  extreme path dominates; KS against the exponential p >= 0.013 in 7 of 8 cases, 1.3e-4 in that
  one; against the Gaussian tail p < 1e-88); e-folds REPRODUCED IN PART (much heavier than the
  Gaussian tail, KS p < 1e-22, but between Gaussian and exponential: CV 0.88-0.96, KS against
  the exponential p from 4e-5 to 0.034). At N_b = 3 both are Gaussian (KS against the Gaussian tail p = 0.10 to 0.39).
- Noise off at 6: lapse back to 1, e-folds conserved (SI.tex:873): REPRODUCED (`off6`,
  `fig/fig_off6.png`): median |alpha - 1| = 1.5e-4 at N_b = 8 and 2.8e-7 at 10 (max 2.0e-6);
  N - N_b changes between 7 and 10 by a median 1.1e-3, 0.5% of its spread 0.23.
- alpha^3 -> 1 gives left-skewed PDFs (SI.tex:875): REPRODUCED (`a3one`,
  `fig/fig_a3one.png`, `fig/fig_a3one_moments.png`): skewness of alpha -0.78, -0.96 and of N
  -0.26, -0.80 at N_b = 5, 6; paths cross alpha = 0 (minimum alpha -1.0 at 6), whereas with
  alpha^3 the smallest alpha at the record times of the Heun runs is 0.64 (the barrier of
  SI.tex:875; Euler-Maruyama on the Ito-equivalent: 0.12 at N_b = 6). In the Ito reading a few paths do cross 0 (seed 1: minimum -5.7 at 5).
- The Ito term changes little (SI.tex:822): REPRODUCED IN PART. Switching it off changes the
  widths at N_b = 4 and 6 by 1-8% (11% at 5 in the Stratonovich run, where one near-blow-up
  path inflates the width) and the skewness of N by < 0.02, but shifts the mean of alpha by -0.03 and the
  mean of N - N_b at 6 from 0.085 to 0.033 (Stratonovich) and from 0.003 to -0.040 (Ito
  reading): about a fifth of a standard deviation. The interpretation (Ito vs Stratonovich) of
  the alpha^3 noise matters more than the Ito term.
- Step dependence (SI.tex:842 footnote): the SDE step alone does not matter (h = 0.005, 0.01,
  0.02 within 1.5% in the widths at N_b = 4 and 6; Heun h = 0.01 vs 0.001 within 1%); the background step decides
  everything (item 1). The Ito reading at h = 0.001 moves the N_b = 4 widths up by 5-7%: the
  agreement with the paper is best at exactly 0.01, consistent with a first-order (Euler)
  integration at that step. With the background tuned instead (converged, dphi/dN* = -2.00818
  so that it crosses at 3.045) the widths are 9-17% smaller (`bg_tuned`, `naive_tuned`).
- Seed dependence: across seeds 1-4 the widths agree within 0.5% at N_b = 4 and 6 (at 5 single
  near-blow-up paths move std alpha by up to 15%), the medians of kappa3(alpha) within 0.11;
  single-time kappa4(alpha) varies by orders of magnitude.
- Linear regime check: the run follows the linear-theory covariance on the same background to
  0.2% (alpha) and 0.4% (N) at N_b = 3 and 0.7% at 3.5; nonlinear from 4 (`fig/fig_linear.png`).

What stays ambiguous: which integrator and which interpretation Mathematica actually applied
(the data point to Euler-type Ito integration of the printed drift, against the text's
"Stratonovich"); the alpha^3 vs alpha^5 Ito term; whether "alpha^3 set to 1" includes the Ito
term; KDE bandwidth; the fourth/fifth time in the caption of Fig. 3. [TO VERIFY] only the
authors could settle the first; nobody outside is contacted (rule 9).

## Requests

- To the lead of E-stoch-inf (for `repro/note` and `repro/verify`): the claim that the paper's
  figures are an Ito/Euler solution at step 0.01 deserves a check by a second agent from
  these artefacts (decision 0009), and the derivation of the alpha^5 Ito term should go to
  `repro/equations` for a computer-algebra check.
- None to core: nothing here needs `athenak/src/`.
