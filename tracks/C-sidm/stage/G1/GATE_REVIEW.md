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

Outcome of R1 (run C-20261121-165320-a2e557b): all four held; numbers in the final version.

## Reviewer's own check R2 (T6(a), long mean free path): prediction written before the run

T6(a) and the T7 collisionless check are the long-mean-free-path end of "heat conduction at
both ends" (brief C-pre-1) and have no second check (OPEN.md item 2; REVIEW-wave3.md section
1 checks T6(b) and T7 only). Own reduction and own reference on the four cases of run
C-20261119-145733-558136e (lambda/L = 1000 and 100, two seeds, 2e6 particles, box [10, 11)
in x): (1) slab sums of the hot half from the first and last snapshots against the
package's `reduced.npz`; (2) the same-sample free-streaming curve (t = 0 snapshot drifted
with v = u/W); (3) the ensemble collisionless curve by 2D quadrature over Maxwell-Juttner
momenta, with the variance of independent particles; (4) the initial slope over the first
snapshot interval. Script `scratch/C-sidm/tmp/gate_review_G1/t6a_check.py` (checksummed).

- R2.1 My slab sums of the first and last snapshots equal the package's reduced rows to
  1e-12 relative. Refuted by a difference above 1e-10.
- R2.2 At lambda/L = 1000 the data deviate from the same-sample free-streaming curve by less
  than 0.3 ensemble noise units at every snapshot (about 8e3 collisions among 2e6
  particles); at lambda/L = 100 by less than 1.0. Refuted by a larger deviation.
- R2.3 Against the ensemble collisionless curve the rms deviation of the rest mass, M W and
  M (W - 1) of the hot half over the run is below 1.5 noise units for both seeds at
  lambda/L = 1000 (the TESTS.md criterion), near the package's 0.86-1.20. Refuted by an
  rms above 1.5.
- R2.4 The initial slope at lambda/L = 1000 is within 5 percent of the ensemble slope over
  the same interval (TESTS.md), near the package's 1.001 and 0.978. Refuted otherwise.
