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
