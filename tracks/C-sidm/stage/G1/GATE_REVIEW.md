# Gate review: C-sidm G1 (independent reviewer, decision 0019 item 3)

Draft written at the start of the review (2026-11-21 16:53 UTC), before the reviewer's own
check runs; the verdicts follow in the final version of this file.

## Reviewer's own check R1 (T5, entropy): prediction written before the run

T5 is the one test the brief names in C-pre-1 ("monotonic entropy increase") that no second
agent has checked (VERIFIER.md section 3; OPEN.md item 2). Own estimator, not the track's
`entropy.s_estimate`: for the isotropic homogeneous boxes of run C-20261115-170539-28432c3
(number and energy conserved) s_MJ(theta_eq) - s(t) = D(t) = KL(f(t) || MJ(theta_eq)), and for
an isotropic f the 3D divergence equals that of the |u| marginal. D from 100 bins of equal
probability under MJ(theta_eq), Miller-Madow corrected; theta_eq from the mean W of the t = 0
snapshot; reference D_ref(0) by quadrature of the two-temperature mixture at the sample
temperatures of the two populations (tags), on the same bins. Script
`scratch/C-sidm/tmp/gate_review_G1/t5_kl_check.py` (checksummed input of the run).

Predictions (numbers from `collide/TESTS.md` T5 and the design JSON of run
C-20261115-165028-a559ab8: gaps 0.04476 at theta_2 = 1e-3 and 0.12202 at theta_2 = 1):

- R1.1 D(0) of each of the four runs equals the binned reference within 4 of its standard
  errors; the binned reference lies a little below the continuous one, which is within 2
  percent of the design gap. Refuted by |z0| > 4 in any run.
- R1.2 D never increases: for every pair of snapshots at least 0.25 tau_rel apart the increase
  is below 4 combined standard errors. Refuted by one pair above 4.
- R1.3 At 15 tau_rel the |u| histogram is that of MJ(theta_eq): chi-square p > 1e-3 in all four
  runs. Refuted by p < 1e-3 in any run.
- R1.4 The mean W is constant to better than 1e-12 relative over each run (equal masses,
  pairwise exact conservation). Refuted by a drift above 1e-10.
