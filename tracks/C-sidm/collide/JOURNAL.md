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

## 2026-11-15 Outcomes R1-R7 (commit 9747576 tests; run C-sidm-20261115-120703-9b3e868)

Test suite `REFERENCES/tests` (pytest): 61 passed after two corrections of my scripts
that were not physics: scipy's `quad` refuses epsrel = 1e-14 with epsabs = 0 and
`brentq` refuses rtol = 4e-16 (raised errors, no wrong numbers); and the entropy
estimator (below).

- R1 confirmed. Closed form vs Monte Carlo (1e6 pairs each, run above,
  `figs/ref_numbers.json`): deviations -1.3 to +1.0 standard errors at 11 temperatures
  from 1e-3 to 100; vs the one-dimensional integral 1e-10; non-relativistic and
  ultra-relativistic limits as predicted. Figure `figs/ref_rate.png` (looked at).
- R2 failed at first (above), R2b confirmed: after the change of gamma_rel - 1 the worst
  error over 2e4 pairs is 1.1e-15 (pytest bound 1e-14), 9.7e-16 over the 6000 pairs of
  the run; relative error of gamma_rel - 1 at most 4.3e-15 against up to 1.0e-8 for the
  rejected norm form; four-momentum residual at most 0.72 eps (momentum) and 2.6 eps
  (energy) relative to the pair energy. Figure `figs/ref_kinematics.png` (looked at).
- R3 confirmed: direction average of E_a' equals (E_a + E_b)/2 within 4 standard
  errors (4e5 directions); the CM energy of a equals sqrt(s)/2 to 1e-12 E.
- R4 confirmed: at theta ~ 1e-4 the exact quadrature is within 2e-3 of the
  non-relativistic closed form, the Monte Carlo collision integral within 4 standard
  errors of the quadrature at theta 1e-4, (1, 0.5), (3, 0.1); run above: MC/quadrature
  = 1.0048 +- 0.0029, 0.9990 +- 0.0025, 1.0014 +- 0.0022, 1.0029 +- 0.0022 at
  theta_2 = 1e-3, 0.1, 1, 10. New number: the exact initial rate of (theta_1 - theta_2)
  for theta_1 = 2 theta_2 is 0.995, 0.813, 0.162, 0.027 of the non-relativistic form at
  theta_2 = 1e-3, 0.053, 2.8, 100. Figure `figs/ref_relax.png` (looked at).
- R5 confirmed: one-sided fluxes vs quadrature 1e-9, limits, initial slope of the
  collisionless step 1e-4, late-time mixing 1e-3. Figure `figs/ref_conduction.png`
  (looked at): at theta_2 = 1 the slab energy oscillates with period ~ L/c, recurrences
  of nearly luminal particles in the periodic box, as free streaming requires.
- R6: closed form vs quadrature and Sackur-Tetrode confirmed. Estimator FAILED as first
  written: equal-probability bins put the tail into one bin and biased s by +0.0195
  (11 standard errors) at theta = 1. Bins uniform in s = sqrt(zeta (W - 1)) (400 bins):
  deviations -0.5 to +1.7 standard errors at theta = 1e-3 to 10 (run above, figure
  `figs/ref_entropy.png`, looked at). Entropy gap of the two-temperature start
  (theta_1 = 3 theta_2): 0.045 per particle at theta_2 = 1e-3, 0.123 at theta_2 = 1:
  the H-test needs a resolution well below that, i.e. N >~ 1e5 per snapshot.
- R7 confirmed (normalization, identities, Bessel forms vs quadrature, inversion,
  sampler KS, drifting-gas moments).

## 2026-11-15 Prediction T6-0: collisionless step with the existing executable

Run (to be registered): `analysis/run_step_collisionless.sh 100000` through
`register_run.py`, processor executable of main (`.work/build_cpu_c1/src/athena`, no
collision module), deck `inputs/box_step_collisionless.athinput`: flat metric
(kerr_schild, bh_mass = 0), periodic box 1 x 0.125 x 0.125 at x0 = 10, 32 x 4 x 4 cells,
1e5 equal-mass particles, left slab theta = 0.02, right slab theta = 0.01, equal pressure,
dt = 0.02, t = 0..30 (about 2.4 crossing times L/<|v|> of the cold slab), snapshots every
1.0. Purpose: check the box set-up, the periodic wrapping of particles in an analytic
metric, and the analysis pipeline of T6 before any collision code exists.

Prediction: every particle moves on x0 + (u/W) t (mod L) with a position error below
1e-9 L at all snapshots, u unchanged to rounding (Christoffel symbols vanish), so the
slab sums of the code equal the free-streaming sums of the sample to 1e-12 relative; the
slab sums lie within about 3 sampling-noise units of the exact ensemble curve
(`conduction.step_collisionless`) at all times. Refuted by a position error above 1e-9 L
(a wrapping or pusher defect), a change of u above 1e-12, or ensemble deviations
systematically above 4 noise units (an error in the reference or in the sampler).

## 2026-11-15 Outcome T6-0: confirmed (run C-sidm-20261115-121302-313d399)

53 s on 4 cores, 1501 cycles, 3.6e6 particle updates per cpu second. Largest position
error against x0 + (u/W) t (mod L): 1.8e-12 L; u unchanged bit for bit (0.0); slab sums of
the code equal the free-streaming sums of the sample exactly (relative difference 0.0);
deviation from the exact ensemble curve at most 1.85 sampling-noise units, rms 1.01, 1.01,
0.82 (rest mass, energy, kinetic energy; noise from 64 resamplings). Sample temperatures
0.02026 and 0.009997 (target 0.02, 0.01; 2 and 0.03 standard errors of a mean of 3.3e4
and 6.7e4 mirrored samples). Figure `figs/T6_0_step_collisionless.png` (looked at): the
transient is over within about one crossing time and is resolved by only six snapshots at
snap_dt = 1; the collisional T6 runs need snap_dt <= 0.1 L/<|v|>. The kinetic energy of
the hot slab first drops (fast particles leave first) and then overshoots, in the exact
curve as well as in the run. So the Minkowski box (analytic kerr_schild with bh_mass = 0,
periodic mesh, box away from r = 0) works with the existing code, and the T6 pipeline is
ready for the collisional runs.

## 2026-11-15 Discriminating power of T4 and T11 against a non-invariant relative speed

Before writing the criteria, computed (now a reference test,
`REFERENCES/tests/test_rate.py::test_noninvariant_relative_speed_is_refuted`, 2e6
Monte Carlo pairs, seed 31): a collision code that used |v_a - v_b| instead of v_Mol would
give an initial two-temperature rate 1.266 times the correct one at (theta_1, theta_2) =
(3, 1) and 1.0008 times at (3e-3, 1e-3); in a gas at theta = 1 drifting with beta = 0.6 its
lab-frame pair average is 0.931 against <v_Mol> = 0.628, which equals
<v_Mol>_rest/gamma_b^2 = 0.6277 as SPEC.md section 2 requires. So T4 at theta_2 = 1 and
T11(a) refute the wrong speed by 27 and 48 percent; T4 at theta_2 = 1e-3 cannot.
