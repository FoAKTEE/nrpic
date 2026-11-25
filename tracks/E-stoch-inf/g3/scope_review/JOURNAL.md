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

## entry-2 (2026-11-25 05:20 PST): outcomes of RB1 and BS1-BS5

RB (run E-20261125-130854-ef74ef8, `ref_bins.json`, `fig_ref_bins.png` looked at: the right panel shows the
measured and expected points; in the left panel the dotted "truncated" steps lie under the solid ones except
in the top bin, so only the two drops are visible):
- RB1 HOLDS. Expected var/var_lattice of the lattice variant: 0.97785 (|n| <= 32; measured 0.9796 +- 0.0032,
  pull +0.55) and 0.99058 (|n| <= 64; measured 0.9905 +- 0.0016, pull -0.05). The top bin carries 3.39 per cent
  (32) and 1.13 per cent (64) of the band variance and gets the factor 0.279 (32) and 0.166 (64) instead of
  0.934 and 0.992; with that bin truncated at ln NLAT the expected ratio is 1.00001 and 0.99991. The "six
  standard errors" tension of the lattice variant (langevin/JOURNAL.md, entry of 04:05 PST, and entry 10 for the
  256 band) is the bin normalisation of `lattice_factor_fn`, not physics. Not a blind test (entry 1).

BS (run E-20261125-131002-ceefa2f, `box_stats.json`, `fig_box_stats.png` looked at: rho(r), one-point density
against the Gaussian and the Edgeworth curve of the reference skewness, even part against odd part with the
reference parabolas, and the s.d. bars):
- BS1 HOLDS: sigma_lin 0.4939516 (read_seed 0.49395); sd(R+)/sigma_lin 1.001616; skewness 0.001384; F_+(3)/Q
  1.0481; F_-(3)/Q 1.0336; F_+(4)/Q 1.099, F_-(4)/Q 1.220: the numbers of g3/JOURNAL.md entry 3 to all quoted
  digits, from an independent parser and an independent R^NR.
- BS2 HOLDS, at the edge: the Owen's-T s.d. of F_+(3) per box with the record's rho is 5.42e-5 (4.01 per cent of
  Q(3)); the power run's 400 synthetic boxes gave 4.96e-5, 9.2 per cent lower (inside the 10 per cent band;
  2.6 times the 3.5 per cent sampling error of an s.d. from 400 boxes, so the power run probably understates the
  scatter slightly); n_eff(F3) = 4.6e5 against 5.5e5 (-16 per cent). Block jackknife on the real box: 5.40e-5.
  At nu = 4: 6.20e-6 (19.6 per cent of Q(4)), n_eff 8.2e5 (power run 5.98e-6). rho(r) = 0.68, 0.26, -0.005,
  -0.058 at 1-4 cells: the field decorrelates within two cells, as the scope says.
- BS3 REFUTED: the scatter of the box variance accounts for 23 per cent of Var F(3) (2.8 per cent at nu = 4),
  not more than half; the "effectively independent cells" reading of the scope is the better picture. The
  effective number of modes of the variance is 1.32e5 (below 1.4e5 as predicted): the per-mode power is nearly
  flat over the band, so every mode counts. The box variance scatters by 0.39 per cent (s.d. of s2_box/sigma^2).
- BS4 HOLDS: a_R = 2.81e-4 from the mirrored pair (|a_R| < 0.002); mean skewness of the pair 8.4e-4 (< 0.006);
  the even part is 2.0e-4 sigma_lin rms and 90 per cent of it is the local quadratic (residual 1e-5 of
  sigma_lin... rms 9.7e-6 against 9.8e-5). R^NR carries 3.0-3.6 per cent of the one-patch delta-N value
  a = 0.0078-0.0095. The scope's statement (4) holds, and more strongly than "to the precision of one box".
- BS5 HOLDS trivially, with a finding: the chi term of R^NR has rms 8.3e-7 sigma_lin (the aniso term 2.3e-7);
  R^NR at N_f is (H_b/Pi_b) dphi to one part in 1e6, and the logarithmic chi changes a_R by 1e-13. On the
  geodesic slice at N_f the local scale factor is uniform to about 4e-7 (eps1 ~ 1e-12 after USR, record header).
  Consequence for the review [JUDGEMENT]: the non-Gaussianity of zeta in the box will come almost entirely from
  the map Delta N_bg(phi, dphi/dN) that the zeta reader evaluates on homogeneous backgrounds, the same
  separate-universe map that makes the reference's skewness; the slicing leg (kdriver drives K, and K is uniform
  to that precision) has no lever arm.

## entry-3 (2026-11-25 05:22 PST): predictions for `sensitivity.py` (a calculation from the two runs above)

- SE1: at nu = 3 with S = 256 and 4e6 direct reference realisations, the reference dominates the combined
  error (reference relative s.e. 1.36 per cent, NR 0.25 per cent); three combined s.e. are 4.1-4.3 per cent of
  F(3), i.e. a sigma error of 0.4-0.45 per cent or a skewness difference near 0.01.
- SE2: the bin artefact of the lattice variant moves F_ref(3) by -9 to -12 per cent, i.e. 6-9 combined s.e.:
  the comparison of 4d.3 as written would report "NR differs from one-patch delta N" from a reference defect.
- SE3: a direct comparison of the skewness has a three-s.e. threshold near 0.003, three times smaller than
  the skewness difference F(3) can see.
- SE4: beyond about 20-40 seeds the NR error at nu = 3 is below a third of the reference's; at nu = 4 the
  reference by direct sampling (4e6) has about 9 per cent relative error, so the 1.2 per cent of 256 seeds
  is wasted unless the importance sampler reaches about 1 per cent.
Refuted item by item if outside these ranges.
