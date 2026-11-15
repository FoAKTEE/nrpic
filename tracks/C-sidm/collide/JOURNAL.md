# JOURNAL of the work package `collide` (C-pre-1, C-pre-2 under decision 0010)

Helper of owner C-sidm. Predictions are written before the test runs; the outcome is
appended under the same heading afterwards, also when the prediction failed.
Units G = c = k_B = 1; theta = T/m.

## 2026-11-15 Session start: state of the dependencies

- `core/collisions` (worktree `wt/core-coll`) has no commit beyond main's a9fec22 and no
  uncommitted change: no collision code and no `tracks/core/interfaces/collisions.md`.
- `core/rng` has an uncommitted draft (`wt/core-rng`: `athenak/src/utils/rng.hpp`,
  `python/nrpic/rng.py`): Philox-4x64-10, key (seed, stream), counter (entity,
  entity_hi, step, draw), stream `kStreamCollisions = 2`, `Direction` (Marsaglia).
  RNG_REQUIREMENTS.md is written against this draft.
- So nothing of the code can be checked in this session; the package delivers the
  specification, the references with their own tests, the test plan with pass criteria,
  and the analysis scripts, tested on synthetic data.

## 2026-11-15 Reference sources read

- arXiv:2602.17487 (the brief's cross-check for collisions, lines 520 and 852) is a
  collisionless discontinuous-Galerkin Vlasov-Maxwell solver: `results.tex` line 18
  ("in the absence of collisions or sources"), `intro.tex` line 9 (C[f] named only).
  It contains no collision operator and cannot cross-check relaxation or conduction.
  [VERIFIED]
- Koda & Shapiro, arXiv:1101.3097 (`sidm1.tex`): pairwise probability
  P_0j = m W sigma |v_0 - v_j| dt (lines 568-574), pairs scattered together for
  conservation (586-596), unequal masses "not trivial" (604-608), P_bar < 0.1 (672),
  neighbour distance below the mean free path (680-685); conduction constants
  a = sqrt(16/pi), b = 25 sqrt(pi)/32 = 1.38 (lines 409-417). [VERIFIED]
- Balberg, Shapiro & Inagaki, astro-ph/0110561 (`SIDMGT_Xiv2.tex`): t_r = 1/(a rho v
  sigma), a = sqrt(16/pi) for hard spheres (lines 309-323); b ~ 25 pi/(32 sqrt 6) = 1.002
  (line 394) in the same flux law (lines 382-390). [VERIFIED]
- arXiv:2601.17117 (`SIDM_MS.tex` line 233) uses b = 25 sqrt(pi)/32 with Chapman-Cowling;
  Eckart heat flux (line 271). arXiv:2010.15132 (`smbh.tex` line 116):
  kappa_smfp ~ 2.1 v k_B / sigma, i.e. (3/2) b = 75 sqrt(pi)/64 = 2.08. [VERIFIED]
- So two values of b are in the literature, differing by sqrt(6/pi) = 1.38; the
  short-mean-free-path test T7 of TESTS.md separates them. [VERIFIED that both are
  printed; which one is right is decided by T7, prediction: 25 sqrt(pi)/32, JUDGEMENT]

## 2026-11-15 Predictions for the reference scripts (before running their tests)

R1 `rate.py`. The closed form <v_Mol> = 4 K3(2 zeta) / (zeta K2(zeta)^2) (zeta = 1/theta),
derived in SPEC.md section 2 from the one-dimensional thermal-average integral, agrees
with a direct Monte Carlo average of v_Mol over independently sampled Maxwell-Juttner
pairs within 4 standard errors at theta = 1e-3, 0.1, 1, 10. Non-relativistic limit:
ratio to (4/sqrt(pi)) sqrt(theta) (1 - 25 theta/16) equal to 1 within 1e-6 at
theta = 1e-4. Ultra-relativistic limit: |<v_Mol> - 1| < 1e-3 at theta = 100.
Refuted by any of these failing.

R2 `kinematics.py`. The double-precision pair scattering agrees with a 50-digit mpmath
evaluation of the same formulas, with the same direction, to a relative error below 1e-13
(relative to the larger of |p| and m) for 2e4 random pairs spanning theta from 1e-8 to
1e6 and bulk Lorentz factors up to 1e4; the pair's four-momentum is conserved to a few
units of 1e-16 relative to the pair energy. Refuted by any case above 1e-12.

R3 `kinematics.py`. For equal masses the direction average of the post-collision
energy of each particle is (E_a + E_b)/2 exactly (SPEC.md section 3); a Monte Carlo
over directions agrees within 4 standard errors.

R4 `relax.py`. Initial rate of the temperature difference of two Maxwellian populations
of equal particle mass (non-relativistic, derived in SPEC.md section 5):
d(T1 - T2)/dt = -(4/3) sqrt(2/pi) (n1 + n2) sigma sqrt((T1 + T2)/m) (T1 - T2).
A Monte Carlo collision integral (independent pairs, oracle kinematics, no time
evolution) agrees within 4 standard errors at theta ~ 1e-4; the relativistic quadrature
agrees with the Monte Carlo integral at theta = 1 within 4 standard errors.

R5 `conduction.py`. One-sided Maxwell-Juttner fluxes (closed forms in SPEC.md section 6)
agree with direct quadrature to 1e-9; limits sqrt(T/(2 pi m)) n and n/4 for the number
flux, 3 n T / 4 for the energy flux. The collisionless step solution has the initial slope
-2 (Phi_E1 - Phi_E2) and tends to E_tot / 2 at late time (to 1e-3).

R6 `entropy.py`. The Maxwell-Juttner entropy per particle in closed form agrees with the
quadrature of -int f ln f to 1e-9 and reduces to Sackur-Tetrode; the histogram estimator
with the Miller-Madow correction on 1e6 samples is within 4 bootstrap standard errors of
the exact value.

R7 `mj.py`. The identity <u^2/W> = 3 theta and the closed forms of <W> hold to 1e-12
against quadrature; the inverse-CDF sampler passes a Kolmogorov-Smirnov test against the
exact CDF (p > 1e-3) at theta = 1e-3, 1, 100.

## 2026-11-15 Outcome R2 (first run): FAILED as stated

`pytest tests/test_kinematics.py::test_against_mpmath`: worst error 3.41e-13 relative to
max(1, |u|) over 2e4 pairs (median 2e-16, 99th percentile 6.6e-14, 99.9th 1.6e-13); the
eight worst cases all have |u| = 4.5e3 to 8.8e3 (bulk Lorentz factor of the pair of that
order) and gamma_rel - 1 between 1e-7 and 7e-2. Cause found by reading the algebra, to be
confirmed by the rerun: gamma_rel - 1 = 2 sinh^2(d_eta/2) + ab(1 - cos psi) uses
a - b = |u_a| - |u_b| of two rounded norms of size 6e3 whose difference is 0.05, i.e. a
relative error eps a/(a - b) ~ 1e5 eps in gamma_rel - 1, then boosted by the pair's
Lorentz factor.

Fix (as first written; the selector was then corrected, see next entry): for co-moving
pairs (u_a . u_b > 0) gamma_rel - 1 from D = u_a - u_b and
S = u_a + u_b only: with e = S/|S|, D_par = (D.e)^2, D_perp = |D x e|^2,
A = (W_a + W_b)^2, gamma_rel - 1 = (D_perp + 4 D_par/A) / (2 (1 - D_par/A)), where
D_par/A < 1/2 for co-moving pairs (no cancellation; derivation in SPEC.md section 3).
The previous form is kept for u_a . u_b <= 0, where ab(1 - cos psi) >= ab dominates.

Prediction R2b (before the rerun): with the fix, the worst error over the same 2e4 pairs
is below 1e-14 relative to max(1, |u|); the other kinematics tests pass unchanged.
Refuted if the worst error stays above 1e-14.

Correction before the rerun: the claim "D_par/A < 1/2 for co-moving pairs" is false (a
nearly resting partner of an ultra-relativistic particle gives D_par/A -> 1, and then
1 - D_par/A cancels). The branch is selected by r = D_par/A <= 1/2 instead of the sign of
u_a . u_b; for r > 1/2 the norm form has no cancellation (docstring of gamma_rel_m1).
Prediction R2b unchanged.
