# JOURNAL of package g3 (Track E, gate G3): tail statistics of the curvature perturbation in the inflection scenario

Scope: `../spec/scope/SCOPE.md` section 4d (written in batch 17 before any G3 run; decision 0038 item 2).

## entry-1 (2026-11-25 03:59 PST, lead of E, batch 17): the power estimate, predictions before its run

`power.py` draws Gaussian random fields with the linear spectrum of the 128^3 USR box at N_f (the
lockstep record `usr.sf.00020.modes` of the 128^3 window-scan run b_p, E-20261120-222424-0eb754b,
nmax2 = 1024, t = tlim) and measures the box-to-box scatter of the exceedance fractions F_pm(nu),
the skewness and the kurtosis; 400 boxes, 2 cores. The difference Delta used in (a) is the 256-band
value of `../langevin/results/ref_inflection.json` (P(dN > 3 sigma_lin) = 1.57e-3 against the Gaussian
1.35e-3, Delta = 2.2e-4) until the 128-band reference (run E-20261125-115707-b845282) has run.
Predictions:
- W1: the field variance equals the linear lattice variance (var_ratio mean 1 within 0.01) and the
  mean F_+(3) is the Gaussian 1.35e-3 within three standard errors of the mean (a test of the
  synthesis and the normalisation; refuted otherwise: the script is wrong and no seed count is
  taken from it).
- W2: the effective number of independent cells for F(3) lies between 1e3 and 1e5 (the band ends at
  |n| = 32, so a box holds of order 32^3 = 3e4 independent regions; clustering of exceedances lowers it).
- W3: seeds for (a) between 5 and 300; for (b) on F(4) at least 10 times more than for F(3).

Outcome (run E-20261125-115822-29795d6, 400 boxes, 2 cores; `power.json`, `fig_power.png` looked at):
- W1 HOLDS: var_ratio 1.0001 +- 0.0002; mean F_+(3) 1.3501e-3 +- 2.5e-6 against Q(3) = 1.3499e-3;
  F_+(4) 3.167e-5 +- 3e-7 against 3.167e-5. sigma_lin = 0.4940 (record t = 10.0016 of the window
  deck, nmax2 = 1024).
- W2 REFUTED: 5.5e5 effectively independent cells for F(3), five times above the band's top. The
  spectrum rises so steeply toward k_max (P_R from 1e-5 to 0.53 across the band, ref run
  E-20261125-115707-b845282) that the field decorrelates within a few cells; my count of 32^3
  regions treated the band as flat.
- W3 REFUTED for (a): 0.46 seeds (not 5-300) detect the 256-band delta-N excess at nu = 3 at three
  standard errors; for (b) F(4) needs 26 times the seeds of F(3) (3.6 against 0.13): holds.
Consequence for the scope: statistics at nu = 3 are not seed-limited; the seed count is set by the
reach into the tail (nu = 4 to 5). SCOPE 4d.2 fixes S = 256 from these numbers.

## entry-2 (2026-11-25 04:06 PST, lead of E, batch 17): predictions for G3 (SCOPE 4d), written before any G3 run

Pilot (queue label G3P, one batch job on .work/build_gpu_v07, list `inputs/pilot.list`): ten baseline
seeds i = 0..9 (rng_seed 20262000-20262009, s = +1, geodesic, level 0), seeds i = 0, 1 under
lapse_kdriver = 2, seeds i = 0, 1 at level 2; 128^3, nmax2 = 1024, dumps at t = 0 and tlim.
- G3P-1 (cost): 0.02-0.06 card-hours per baseline seed, wall including the two dumps; level 2 at most
  1.7 times a baseline seed; kdriver within 1.2 times. Refuted outside: the budget of 4d.8 is redone.
- G3P-2 (health): every run reaches tlim with finite fields; records <abs H'/[H]> and <abs M/[M]>
  below 1e-9 and 1e-1 as in 4c U-A4'(c) (the M bar at 128^3: the G2 group-1 value 2.47e-2).
- G3P-3 (estimator on real output): per seed, sigma of R^NR at N_f within 3 per cent of sigma_lin of
  its record; the seed-to-seed standard deviation of F_+(3) of R^NR within a factor 1.4 of the
  Gaussian 4.96e-5 (power run); mean F_+(3)/Q(3) of R^NR over ten seeds in [0.9, 1.3].
G3 proper (each judged when its runs exist; refutations stay on record):
- G3-T: skewness of R^NR over 256 seeds in [-0.01, 0.05]; F_+(4)/Q(4) in [0.9, 1.4] and F_-(4)/Q(4)
  in [0.6, 1.1] for both variables. For zeta against the one-patch reference: |r(3)| and |r(4)| below
  three combined standard errors [JUDGEMENT: at N_f the band is far outside the Hubble radius and
  the separate-universe picture holds]. Refuted if |r| exceeds three combined errors at nu = 3 or 4:
  then NR differs from one-patch delta N, the result S11 asks for, and it is reported only together
  with 4d.6 and 4d.7.
- G3-C: the model test holds at every dump with cN in [2.0, 6.6] and every judged factor lies within
  4 +- 0.05 at 128^3 (G2 at 256^3: within 4 +- 0.005 with the three-amplitude level).
- G3-R: the Richardson factor of D^L from 128 to 160 in [2.0, 4.5]; T changes by less than 10 per cent.
- G3-G: zeta tail statistics agree between geodesic and kdriver slicing within three paired standard
  errors; R^NR one-point sigma differs by less than 1 per cent.
- G3-L2: level 2 moves F_pm(3) of zeta by less than 10 per cent and the skewness by less than 0.02.
