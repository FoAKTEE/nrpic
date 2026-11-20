# JOURNAL of verify_g1 (fresh-context verifier of C-sidm G1)

Labels: [VERIFIED] read at a source with locator or measured in a registered run of this
package; [BACKGROUND] standard result not re-derived; [JUDGEMENT] own reasoning;
[TO VERIFY] open.

## Entry 0 (2026-11-20 14:13 PST) Set-up and blind rules

Read: CLAUDE.md, coord/CHARTER.md (to Owners, 9.6, 10), decisions 0010, 0016, 0019,
harness/RULES.md (nrpic-run), collide/TESTS.md, collide/SPEC.md (definitions), the
interface text of `core/collisions-2` (sections 1-5, 11; not section 8, which is core's
own verification), docs/FORMATS.md, python/nrpic/collide.py (readers only). Not read
(blind phase): stage/**, PLAN-wave3.md, STATUS/HANDOFF/RISKS/JOURNAL of the track, any
package JOURNAL, Results sections of READMEs, the note, results/*.json, summary.json of
the run directories (written by the drivers; they may hold fitted values).

Inputs found for V1: the run directories hold for every case `case.json`, the deck
arguments in `athena.log`, the first and the last snapshot (`heat.part.00000.bin`,
`heat.part.000NN.bin`) and `reduced.npz` (Fourier sums of every snapshot, written by the
driver; the intermediate snapshots were deleted). I use `reduced.npz` for the time series
and check it against the two snapshots that remain (my own sums from the particles).
Deviation of the runs from TESTS.md T7 seen in `case.json`: eps = 0.2 (T7 says 0.05).

## Entry 1 (14:40) V1 predictions, before any computation

V1a Chapman-Enskog conductivity [own Monte Carlo of the collision brackets, ce_kappa.py].
Method: variational form of the first Chapman-Enskog equation, kappa = k_B <X, L^-1 X>/T
... (non-relativistic: X = (x - 5/2) c_z, x = m c^2/(2 k T); trial functions
Phi = sum_j a_j S_j(x) c_z with Sonine polynomials S_j = L_j^(3/2)); brackets
<Phi_i, L Phi_j> = (1/4) n^2 sigma_tot E[g Delta Phi_i Delta Phi_j] over Maxwellian pairs
with isotropic centre-of-momentum scattering (= hard spheres = the code's operator).
Prediction: the first approximation gives kappa_1 sigma_tot/(k_B sqrt(k_B T/m)) =
75 sqrt(pi)/64 = 2.0771 within 4 Monte Carlo standard errors (formula of Koda & Shapiro
arXiv:1101.3097 `sidm1.tex` lines 401-415: q = -(3/2) b (v/sigma) d v^2/dr with
b = 25 sqrt(pi)/32 [VERIFIED read], which is kappa = (3/2) b sqrt(T/m)/sigma_tot); orders
2-4 raise it by 2-3 percent (Chapman-Cowling value about 1.025 [BACKGROUND]). Refuted if the
first approximation differs from 2.0771 by more than 4 standard errors or the sequence does
not increase monotonically (the variational sequence must). Relativistic first
approximation (Eckart frame, X = v_z (E - h), h = m K3/K2, Moller flux) at theta = 0.003:
within 1.5 percent of the non-relativistic value; at theta -> 0 it must reproduce 2.0771.

V1b Isobaric mode (runs C-20261119-144545-c606492, C-20261119-155434-8563453).
Separation of sound and entropy mode: from the n-mode A_n = c1_M/sM and the pressure mode
A_p = c1_MK/sMK (p = (2/3) e_kin, non-relativistic; at theta = 0.003 the difference from
(1/3) sum M u^2/W is O(theta) of a quantity that is itself small), the entropy amplitude
A_s = A_n - (c_v/c_p) A_p is free of adiabatic sound (delta s = c_v dp/p - c_p dn/n = 0)
and equals A_n for the isobaric mode. Prediction: A_n shows an oscillation at
omega = c_s k (period 2 pi/(c_s k) = 444 at k lambda = 0.2) that A_s does not; A_s decays
exponentially. Expected kappa/kappa_1 at (k lambda)^2 -> 0: 1.02-1.05 (Sonine 1.025 times a
cell-size gain of order +1 percent at dx = lambda/4 [BACKGROUND, TO VERIFY]); at finite
k lambda the apparent kappa falls below (Burnett order (k lambda)^2). Nonlinearity at
eps = 0.2: quantified with my isobaric Lagrangian reference (heat_ref.py); I expect a
correction to the fitted rate of order eps^2, i.e. 1-4 percent. Refuted: kappa/kappa_1 outside
[0.99, 1.06] after the corrections I can compute; per-seed scatter larger than the
fit errors by more than a factor 2 (would mean an unmodelled noise source).
V1c Temperature step (run C-20261119-144535-2c7b6a4, lambda/L = 0.01, theta 0.02/0.01,
equal pressure). Prediction: with the nonlinear isobaric reference (kappa = f kappa_1(T),
c_p(theta)), the fitted f is 1.02-1.05 and agrees with V1b within the errors; the linear
form `step_diffusive` of the test definition, with chi at the final state, gives a value
biased by the factor-2 contrast (sign not predicted).

## Entry 2 (15:05) V1a outcome (run C-20261120-222423-519f12b, 4e7 non-relativistic and 1e7-2e7 relativistic pairs)

- First approximation, non-relativistic: kappa_1 sigma_tot/(k_B sqrt(k_B T/m)) = 2.0810 +- 0.0014
  (40 batches) against 75 sqrt(pi)/64 = 2.0771: +2.8 standard errors, inside the 4-sigma
  criterion: prediction holds [VERIFIED in this run]. The analytic b_1 = -5/2 is reproduced
  (MC -2.5012).
- Sonine sequence, ratio to the first approximation from the same samples: 1.02235(30),
  1.02460(23), 1.02491(23) for orders 2, 3, 4; monotonic. Order 2 agrees with the
  Chapman-Cowling value 1 + 1/44 = 1.02273 [BACKGROUND, not re-read] at 1.3 sigma, the limit
  "about 1.025" of TESTS.md T7 is confirmed by an independent computation.
- Relativistic (Eckart, Moller flux, isotropic CM): theta = 1e-4 first order 2.0720(39)
  (reproduces the non-relativistic value; the identity <X, p_z> = 0 holds to 1e-10 in the
  quadrature, i.e. h = K3/K2 is the right enthalpy). theta = 0.003: 2.0930(26) first order,
  2.1386(20) at order 4, i.e. kappa/kappa_1(nonrel) = 1.0077(13) and 1.0296(10) [VERIFIED
  in this run]. Prediction "within 1.5 percent" holds (0.8 percent). Further: theta = 0.1:
  2.2813 (orders 1-4 equal within 0.04 percent), theta = 1: 1.954 -> 2.063; the vanishing
  order-2 gain near theta = 0.1 was checked at theta 0.01, 0.03, 0.1, 0.3 (debug evaluation,
  2e6 pairs: gains 1.6, 0.8, 0.0, 1.5 percent): it is a smooth zero crossing of the
  projection, not a defect [JUDGEMENT].
- So the continuum target of T7 at theta = 0.003 is kappa/kappa_1 = 1.030 (relativistic,
  converged in the trial space), before any DSMC cell-size or time-step bias.

## Entry 3 (15:10) V1b first outcome (run C-20261120-222754-14bd23d, 20 cases)

- reduced.npz equals my own sums of the first and last snapshot to the last bit in all 20
  cases (max relative difference 0.0); the initial profiles have amplitudes 0.199-0.202 in n
  and T: eps = 0.2, n ~ 1 - eps cos kx, T ~ 1 + eps cos kx [VERIFIED].
- Sound: A_p oscillates with periods about 450 (k lambda 0.2) and 220 (0.4), as predicted
  from 2 pi/(c_s k) = 444 and 222; A_s decays smoothly, A_n carries the sound: its T7
  estimator gives 1.04, 1.13, 1.79 at k lambda 0.1, 0.2, 0.4, so the separation is
  essential. Prediction holds.
- T7 estimator on A_s (definition of the test, c_p of MJ): 1.0128(38) [4 seeds], 1.0067(48)
  [8], 1.030(12) [8] at k lambda 0.1, 0.2, 0.4; linear extrapolation in (k lambda)^2:
  1.0090 +- 0.0038 (chi2 = 2.4, 1 dof; slope +0.09 +- 0.08, not significant). Inside
  [0.99, 1.06].
- Nonlinearity at eps = 0.2: the exponential fit to my isobaric reference gives 0.9897 of
  the linear rate in the same windows (the box keeps the pressure <n T> = n0 T0 (1 -
  eps^2/2), the final temperature is 2 percent below 0.003). Fit with the nonlinear
  reference: f = 1.0233(39), 1.0172(49), 1.041(12); extrapolated 1.0194 +- 0.0038. The
  adiabatic pre-adjustment of the reference start changes f by -0.0007.
- Against the prediction 1.02-1.05: the nonlinear-corrected value 1.019(4) is at the low
  edge; it lies 1.1 percent (2.7 sigma) below the converged relativistic Chapman-Enskog
  value 1.030, and a DSMC cell-size gain (dx = lambda/4) would raise, not lower, it
  [BACKGROUND, TO VERIFY]. Not a failure of the test interval; noted as an open small
  discrepancy. The seed scatter exceeds the naive fit errors by 1.8-2.3 x (my refutation
  clause): the residuals are correlated in time (the same particles), so the curve_fit errors
  are too small; the seed scatter is the error used [JUDGEMENT].
- Figure 2 of that run mixed the A_n points into the same axes and hid the relevant range;
  rerun with a two-panel figure (same numbers).

## Entry 4 (15:15) V1c prediction refinement (debug look at the step, before the run of record)

A first evaluation of v1_step.py (smoke, not of record; the snapshot positions turned out
not to be wrapped: fixed with mod L, after which my slab sums equal reduced.npz exactly)
shows a standing sound wave in the slab mass, period about 6.7 = L/c_s(theta_f), amplitude
3-4 percent of the contrast, the same phase in both seeds. Prediction for the run of record:
removing the adiabatic part with the bin profiles (M_ent = M_s - sum_slab (c_v/c_p) n
(p - <p>)/p dV, local MJ temperature from e_K/n) removes most of the oscillation from the
residual and changes f by less than the seed difference (3.4 percent in the smoke
evaluation). Expected f near 1.04 (relativistic CE at theta ~ 0.013 interpolated between
1.037 at 0.01 and 1.056 at 0.03, entry 2).

## Entry 5 (15:20) V1 runs of record and V1c outcome

- V1b of record: run C-20261120-223130-6742500 (same numbers as entry 3; figure with the
  relevant range: `figs/v1b_kappa_ratio.png`, `figs/v1b_mode_amplitudes.png`).
- V1c (run C-20261120-223133-2f98a0e): my slab sums equal reduced.npz exactly (after wrapping
  the positions); initial state theta 0.0201/0.0100 (seed 1), 53333/106667 particles.
  Linear square-wave form of the definition, chi_1 at the final state (theta_f = 0.013359
  from exact MJ energy conservation, c_p = 2.549): chi/chi_1 = 1.051 (seed 1), 1.086 (seed 2),
  mean 1.068 +- 0.018 (half difference). Nonlinear isobaric reference: f = 1.027, 1.062,
  mean 1.044 +- 0.017; c_p taken at the hot or the cold side instead: 1.054 / 1.039.
  Sound removed with the bin profiles: the oscillation of period L/c_s = 6.7 leaves the
  residual (rms 1.3-1.7 -> 0.4 percent of the contrast; prediction holds), f = 1.031, 1.066,
  mean 1.049 +- 0.017; the seed difference (3.5 percent) is not the sound: with two seeds the
  error is crude. All per-seed values lie in [0.95, 1.10] (T6(b) passes by its definition
  in both seeds); the expected value (relativistic CE at theta ~ 0.013) is about 1.04: the
  nonlinear values agree, the linear form is 2.4 percent higher than the nonlinear fit, the
  bias of the linear form at a factor-2 contrast [VERIFIED in this run].

## Entry 6 (15:25) V2 predictions, before the analysis run

Runs C-20261115-165500-c67e036 (release CPU executable, coll_energy absent) and
C-20261119-141806-af19c1c (collisions-2 CPU executable, coll_energy = particle), 16
collisional cases each (theta 1e-3, 0.1, 1, 10; plain and sub-cycled; seeds 1, 2; N = 1e6,
32^3 cells, 200 steps) and two collisionless controls.
Own reference: <v_Mol>(theta) by a two-dimensional quadrature over |u_1|, |u_2| of two MJ
distributions with the angular average in closed form in rapidities,
(1/2) int sqrt(g^2 - 1) dmu = [F(eta_1 + eta_2) - F(|eta_1 - eta_2|)]/(2 u_1 u_2),
F(eta) = (sinh eta cosh eta - eta)/2 (own derivation: g = cosh of the rapidity difference
for collinear velocities, dg = -u_1 u_2 dmu, int sinh^2 = F). Predictions:
- the quadrature equals the closed form 4 K3(2 zeta)/(zeta K2^2) (Gondolo-Gelmini
  reduction [BACKGROUND]) to 1e-9 relative at theta 1e-3 ... 10;
- T2(a): (sum n_coll - sum sum_P)/sqrt(sum sum_P) within +-4 in all 32 cases;
- T2(b): mean sum_P per step within 0.5 percent of (1/2) N rho_0 sigma <v_Mol>(theta_s) dt,
  theta_s from <W> of the initial snapshot (exact MJ inversion), in all cases; the
  4-standard-error clause may fail at the 1e-4 level through the finite sample (TESTS 2a);
  the decomposition sum_W against (1/2) N rho_0 sigma dt (positions) and sum_P/sum_W
  against <v_Mol> (velocities) locates any deviation; the tested-pair mean agrees with the
  sample's own pair mean (2e7 random pairs) within 4 standard errors;
- T2(c): <W> at the end equals <W> at the start to rounding (energy conserved); KS of |u|
  at the end against MJ(theta_s): p > 1e-3;
- T1: per step |dE|/sum_MW and max|dP_i|/sum_MW below 1e-14 sqrt(n_coll + 1); the
  snapshot sums (math.fsum) of M W and M u_i change by less than 1e-13 of sum M W over the
  200 steps; n_trunc = 0 everywhere; coll_energy = particle in flat space: n_noroot =
  n_balance = 0;
- the two executables test and collide the same pairs: identical n_tested and n_coll in
  every step of every case;
- collisionless controls: n_coll = 0 and the momenta of the end snapshot bit-identical to
  the start.
Refuted if any of these fails; a failure of the 4-se clause alone, explained by the
sample-to-ensemble difference, would be reported as such.
