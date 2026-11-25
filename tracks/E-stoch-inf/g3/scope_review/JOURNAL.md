# JOURNAL of package g3/scope_review (Track E): independent review of the G3 scope before its runs

Reviewer: a helper of E that did not write SCOPE 4d (commit cbe20398), batch 18, 2026-11-25. Task: decide
whether SCOPE 4d can be failed by the runs it plans and whether passing it means what it says (decision
0039 item 1). No card time. Every calculation below is a registered processor run.

## entry-1 (2026-11-25 05:08 PST): predictions before the runs

### RB: the lattice-density variant of the one-patch reference (`ref_bins.py`)

Honesty note: this prediction is written AFTER a 25-point development run of `ref_bins.py` (output in
`scratch/E-stoch-inf/tmp/scope_review_smoke`, not registered) had printed its result. What I had worked
out by hand before that run (from the text of `langevin/scripts/ref_spec.py` lines 64-77): the last bin
of `lattice_factor_fn` is [3.45, 3.50) in ln n for |n| <= 32, its shell volume is counted to e^3.5 = 33.1
while shells exist only to 32, so its factor is about (32^3 - 31.5^3)/(33.1^3 - 31.5^3) = 0.30 instead of
about 1; the bin holds about 3.4 per cent of the band variance (P_R ~ 0.53 at the top over 0.016 in ln n),
so the variant loses about 0.7 x 3.4 = 2.4 per cent of its variance: the measured 0.9796 +- 0.0032. The
registered run (241 points of P_R instead of 25) is therefore a check of the number, not a blind test.
- RB1: expected V_variant/var_lattice for |n| <= 32 in [0.973, 0.986] and for |n| <= 64 in [0.986, 0.995];
  with the top bin truncated at ln NLAT both within 0.002 of 1. Refuted if the |n| <= 32 value is above
  0.990 (the artefact would then explain less than half of the deficit).

### BS: an own reader on the 128^3 mirrored pair b_p / b_m of the window scan (`box_stats.py`)

Inputs: dump 20 (t = 10.0016) of b_p (noise_mode_scale = +1) and b_m (-1) of run E-20261120-222424-0eb754b
(scouting build core_scalar-2, 128^3, nmax2 = 1024, s = 5, sigma = 1; the set-up of G3 except for the
executable and tlim). Not a G3 result: a test of the statistic and its estimator on real output.
- BS1 (reader consistency; the same dump and the same definition as `g3/read_seed.py`, run
  E-20261125-120930-980b18e): sigma_lin 0.49395 within 1e-4 relative; sd(R+)/sigma_lin = 1.0016 +- 0.0005;
  skewness of R+ 0.0014 +- 0.0005; F_+(3)/Q(3) = 1.048 +- 0.002. Refuted outside: one reader is wrong.
- BS2 (effective cells): the Gaussian two-point (Owen's T) estimate of the box-to-box s.d. of F_+(3), with
  rho(r) from the record's spectrum, lies within 10 per cent of the power run's 4.96e-5 (400 synthetic
  boxes, E-20261125-115822-29795d6), i.e. n_eff(F3) within 20 per cent of 5.5e5; the block-jackknife s.d.
  from the one real box within a factor 1.5 of it. Refuted outside: one of the two estimates is wrong.
- BS3 (what sets the scatter): the scatter of the box variance (the finite number of modes, not of cells)
  accounts for more than half of the box-to-box variance of F(3) at a fixed threshold (share > 0.5), and
  the effective number of modes of the variance, 1/sum p_n^2, is below 1.4e5 (the band |n|^2 <= 1024 holds
  about 1.37e5 lattice vectors and the spectrum is steep). Refuted if the share is below 0.3: then
  "independent cells" is the right picture and the scope's reading of the power run stands.
- BS4 (second order of R^NR from the pair): the quadratic coefficient a_R in R^NR = O + a_R (O^2 - <O^2>)
  satisfies |a_R| < 0.002 and the mean skewness of the pair |.| < 0.006 [JUDGEMENT: R^NR is a linear
  extraction]. Refuted if |a_R| > 0.004: then R^NR carries half or more of the one-patch delta-N value
  a = skew/(6 sigma) = 0.008-0.0095 (128 band, run E-20261125-115707-b845282), and the scope's statement that
  the comparison rests on zeta alone (g3/JOURNAL.md entry 3) needs revision.
- BS5 (reader sensitivity, reported): replacing the chi term dchi/(2<chi>) by (1/2)(ln chi - <ln chi>)
  changes a_R by less than 0.002 if the chi term carries less than 0.1 sigma_lin of the rms [low
  confidence: I do not know how the curvature divides between the chi and the phi terms on the geodesic
  slice at N_f]. Refuted if |Delta a| > 0.002 while the chi term's rms is below 0.1 sigma_lin.
