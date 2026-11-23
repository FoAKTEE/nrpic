# Journal of repro/langevin (arXiv:2401.08530, section V)

Source: `kb-data/raw/arxiv/2401.08530/v2/src/Stochastic_Inflation.tex` (read-only; cited as
`SI.tex:<line>`). Paper figures looked at from the store (`plot2v2.png`, `plot2bv2.png`,
`plot4v2.png`, `plot3v2.png`); never copied. Values read off those figures appear only in
this text, marked "read off", never in a data file.

## Entry 0 (2026-11-22 18:05 PST): set-up, what the paper fixes and what it leaves open

Equations used, as printed:
- e-folds, SI.tex:806: dN/dN_b = sqrt(1 + (alpha^2 - 1)(1 - eps1/3)).
- lapse, SI.tex:825-826: dalpha/dN_b = 3 alpha (sqrt(...) - 1) + alpha^3 <S^2>
  + (-3 + eps1 + eps2/2) alpha (alpha^2 - 1) + alpha^3 S.
- amplitude, SI.tex:838 and 1071-1072: sqrt<S^2> = (3/(2 pi)) H / (sqrt(2 eps1) M_Pl),
  on the background.
- background, SI.tex:847 (caption): V = V0 for phi >= phi_c = 9.056, V0 [3x^2 - 2x^3],
  x = phi/phi_c below; phi* = 10, dphi/dN* = -2.0001; V0 from the Friedmann constraint
  with H* = 1e-5; M_Pl = 1. Slow-roll parameters with the paper's sign,
  eps_{i+1} = -d ln eps_i / dN (SI.tex:919): eps2 = +6 in USR, as SI.tex:842 says.
- noise on between N_b = 2 and 6 (SI.tex:847), steps of 0.01 e-fold, 50 000 paths
  (SI.tex:842), Stratonovich evolver of Mathematica (SI.tex:836).

My own derivation check of SI.tex:825 from SI.tex:812 (on paper, deterministic part):
alpha = phidot_b / Z, Z = phidot_b/alpha; with the background equation
phiddot_b/phidot_b = -3H - V'/phidot_b the drift is 3 alpha (dN/dt - H)
+ (V'/phidot_b) alpha (alpha^2 - 1), and V'/(H phidot_b) = -3 + eps1 + eps2/2 for either
sign of the velocity. [VERIFIED by hand] The noise term is -alpha^3 S (sign irrelevant).
The Ito term: Ito's lemma on f(Z) = phidot_b/Z with noise alpha S_Pi in the Z equation
gives (alpha^3/phidot_b^2) * alpha^2 <S_Pi^2>, i.e. alpha^5, not alpha^3; the paper prints
alpha^3 and says the multiplier of S_Pi is "left undecided" (SI.tex:814). I implement
the printed alpha^3 <S^2> and treat the whole printed equation as a Stratonovich SDE.
[JUDGEMENT] Its Ito-equivalent drift adds (1/2) g dg/dalpha = (3/2) alpha^5 <S^2>.

Choices the paper does not state (to be listed in the README):
1. Which integrator gave the background, and at which step (footnote SI.tex:842 says the
   tuning depends on the step of 0.01).
2. The scheme of the "Stratonovich evolver" (Mathematica method not named).
3. Whether "alpha^3 set to 1" (SI.tex:875) also sets the Ito term's alpha^3 to 1.
4. KDE kernel and bandwidth, number of bootstrap resamples (SI.tex:861).
5. Caption SI.tex:861 says "five background efold times" and lists four (3, 4, 5, 6).

Scouting observation before this entry (unregistered probe,
`scratch/E-stoch-inf/tmp/bgprobe.py`, to be re-established by a registered run): the exact
plateau solution of the background (RK4, any step <= 0.01) stops at phi = 9.06402, ABOVE
phi_c = 9.056, so the exact background never reaches the slope; forward Euler at step
0.01 crosses phi_c between N_b = 3.04 and 3.05; forward Euler at 0.005, Heun at 0.01 and a
semi-implicit Euler do not cross. Analytic check of the stop: on the plateau
dphi/dN = u, du/dN = -(3 - u^2/2) u, so Delta phi = (1/sqrt 6) ln((sqrt6 + v)/(sqrt6 - v))
with v = 2.0001, = 0.93598, phi_stop = 9.06402. [VERIFIED analytically and numerically]

## Entry 1 (2026-11-22 18:15 PST): predictions before the registered runs

P1 background (run `bg`). eps1(N=0) = 2.0002, eps2(0) = 2(3 - eps1) = 1.9996; on the
plateau w = u^2 obeys w/(6-w) = 2.0006 e^{-6N}: eps1(1) = 0.0148, eps1(2) = 3.69e-5,
eps2(2) = 6 - 7e-5; USR (eps1 < 1e-2, |eps2 - 6| < 0.03) from N = 1.1. The paper's "USR from
2 e-folds onwards" holds (it is conservative). Euler-0.01 background crosses phi_c at 3.04-3.05;
after the crossing the field follows delta'' + 3 delta' - (18/phi_c^2) delta = 0
(delta = phi_c - phi), rates 0.0715 and -3.0715: |u| keeps falling by a factor ~36 to a
minimum near N = 3.05 + 2.4 = 5.4, then rises at e^{0.07 N} ("increases extremely slowly",
SI.tex:842). eps2 falls from 6 to 0 near N ~ 5.4 and below. Refuted if the Euler background
does not cross between 3.0 and 3.1, or the minimum of |u| is not between 5 and 6.

P2 linear check at N_b = 3 (run `base`). Linearised lapse a = alpha - 1 obeys
da/dN = (-3 + eps1 + eps2) a + sigma xi = +3a + sigma xi in USR, with sigma ∝ e^{3N}:
std a(3) = sigma(2) e^3 = 6.4e-3 and std(N - N_b)(3) = 4.9 sigma(2) = 1.6e-3, with
sigma(2) = 3.2e-4. Refuted if the run differs by more than 10%. (Read off the paper's
Fig. 3 top row: Gaussian peaks 60 and 250, i.e. std 0.0066 and 0.0016.)

P3 base run against the paper (Euler-0.01 background, Heun, alpha^3 and Ito term on).
Widths at N_b = 4, 5, 6: std(alpha) ~ 0.12-0.13 at each, std(N - N_b) ~ 0.04, 0.15, 0.19
(read off Fig. 3 Gaussian peaks 3.4/9.4, 3.0/2.65, 3.3/2.1). Skewness of alpha ~ 1.1 from
N ~ 4.2 on, excess kurtosis of alpha ~ 3 with spikes; skewness and kurtosis of N - N_b peak
near 4.4 at ~0.6-0.8 and fall to ~0.3 and ~0.2 by 6 (read off Fig. 2). Prediction: our
widths within 25% of these, the same signs and time shapes of the moments; refuted if a
width is off by more than a factor 1.5 or a skewness has the other sign.

P4 Stratonovich vs Ito (runs `base`, `ito_em`, `ito_naive`, `heun_h001`). Heun on the
printed equation and Euler-Maruyama on its Ito-equivalent drift agree in std within 3% and
skewness within 0.15 at h = 0.01; at h = 0.001 both converge to each other within
sampling error. Euler-Maruyama on the printed equation without the conversion (Ito
reading) shifts the mean of alpha by ~ +0.02 to +0.05 at N = 5-6.

P5 Ito term off (run `no_ito`). Mean of alpha shifts by 0.01-0.03, std changes < 10%,
skewness changes < 0.2: "practically unaffected" (SI.tex:822) holds at that level.

P6 noise off at 6 (run `off6`, to N_b = 10). alpha returns to 1: median |alpha - 1| < 1e-3
at N = 8, < 1e-5 at N = 10, for all finite paths; N - N_b changes by less than 1e-3
(absolute, median) between N = 7 and 10. Refuted if alpha stays away from 1 or N - N_b
drifts.

P7 alpha^3 -> 1 (run `a3one`, both the noise factor and the Ito-term factor set to 1). The
skewness of alpha becomes negative at N = 5, 6 (left-skewed, SI.tex:875); some paths
cross alpha = 0 (attractor alpha = -1 exists for eps2 ~ 0). Refuted if skewness stays > 0.

P8 step and background (runs `h005`, `h02` with the same Euler-0.01 background
interpolated in ln eps1; `bg_euler005`, `bg_exact`, `bg_exact_tuned`). SDE step alone:
std change < 5%, skewness change < 0.15. Background from Euler at 0.005 or from the exact
solution: the field never reaches the slope, sigma grows like e^{3N} and nearly all paths
become non-finite before N = 5. Exact background with dphi/dN* tuned so that it crosses
phi_c at 3.045: statistics within 10% of `base` (the velocity history, not the integrator,
sets them). Refuted if the tuned exact background differs by more than 20% in std.

P9 seeds (runs `seed2..4`). Across 4 seeds: std(alpha) varies < 2%, skewness(alpha)
varies by 0.05-0.2, kurtosis(alpha) by more (heavy tail, the paper's kappa4(alpha) is
spiky).

P10 exponential tails (from `base`). At N = 3 the PDFs are Gaussian (|skew| < 0.1); at
N = 4, 5, 6 the right tails of alpha and of N - N_b are exponential: the exceedances above
the 90% quantile pass a KS test against an exponential (p > 0.01) and fail against the
Gaussian tail of the same mean and variance, and the log-survival function has no
significant curvature. Refuted if the right tail at N = 4 is Gaussian.

## Entry 2 (2026-11-22 18:12 PST): first outcomes (runs E-20261123-020327-e524721, analysis E-20261123-020825-1a01a96) and a new hypothesis

(Analysis run E-20261123-020746-78d0c54 failed on a plotting keyword; fixed in 1a01a96, rerun.)
Numbers from `results/langevin.json` of the analysis run; figures looked at: fig1_paths,
fig2_moments, fig3_pdfs, fig4_logpdfs.

- P1 HELD. Euler-0.01 background crosses phi_c at N_b = 3.0435; converged and Euler-0.005
  never cross (phi -> 9.06402 = analytic stop, 9.0600); USR (eps1 < 1e-2, |eps2-6| < 0.03)
  from N = 1.06; minimum of |u| at N = 5.41 after the crossing; eps2(4, 5, 6) = 4.07, 0.34, -0.12.
- P2 FAILED at the 10% level as worded (my hand estimate 6.4e-3 used the converged eps1(2)
  = 3.69e-5; the Euler background has 3.23e-5), but the linear-theory moment ODE on the same
  background agrees with the run to 0.2% (std alpha 7.065e-3 vs 7.050e-3) and 0.4% (std D) at
  N = 3, 0.7% at 3.5; nonlinearity shows at 4 (8%). The run at N = 3 is within 7% of the
  paper's read-off widths (0.0066, 0.0016).
- P3 PARTLY HELD. Shapes and signs right; kappa3(N), kappa4(N) peak 0.66, 0.9 near 4.35 and fall
  to 0.39, 0.29 at 6 (paper read off: 0.6, 0.8 -> 0.3, 0.2). Widths: std alpha 0.126, 0.169,
  0.144 and std D 0.046, 0.171, 0.217 at N = 4, 5, 6, i.e. 8-20% above the read-off values;
  kappa3(alpha) ~ 1.5 and kappa4(alpha) ~ 6 with spikes to 400 (paper 1.1 and 3); mean D at 6 =
  0.085 (paper's 100-path mean ~0.01-0.02 read off, standard error ~0.02).
- P4 FAILED in part. At h = 0.001 Heun and Euler-Maruyama on the Ito-equivalent agree (std
  within 0.6%), as predicted; at h = 0.01 Euler-Maruyama is 5-7% narrower at N = 4 (not < 3%).
  The Ito reading (EM on the printed equation, no conversion) shifts the mean of alpha at 5-6 by
  -0.05 (I predicted +0.02 to +0.05: right size, wrong sign) and mean D at 6 from 0.085 to 0.003.
- New observation: the Ito reading `ito_naive` gives std alpha 0.117, 0.137, 0.121 and std D
  0.0425, 0.150, 0.185 at N = 4, 5, 6, within 4% of every read-off width of the paper, and
  kappa3(alpha) at 6 = 0.99, mean D at 6 = 0.003.

Hypothesis H-Ito: the paper's figures are an Euler-Maruyama (Ito) solution of the printed
equations at step 0.01, the background included (that is also what puts the slope at 3.04).
Predictions for run 2 (seeds 2, 3 of the Ito reading; Ito reading at h = 0.001; without the
Ito term; on the tuned converged background):
  (a) seeds 2, 3: std alpha and std D at N = 4, 5, 6 within 5% of the read-off widths
      (0.117/0.042, 0.133/0.150, 0.121/0.190), mean D at 6 below 0.02, median over
      N in [4.5, 6] of kappa3(alpha) between 0.9 and 1.3 (base: ~1.5);
  (b) h = 0.001: within 7% of h = 0.01 in std (the reading, not the step, makes the match);
  (c) without the Ito term: mean alpha lower still by ~0.03 (base minus no_ito was 0.03);
  (d) tuned converged background: widths 10-15% below the Euler-0.01 background (as for Heun:
      bg_tuned std alpha 0.110 vs 0.126 at 4).
Refuted if (a) misses by more than 10% at two of the six widths.
