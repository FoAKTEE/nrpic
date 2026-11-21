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

## Entry 7 (2026-11-20 23:58 PST) Restart after the usage-limit cut; V2 run started; V3 predictions

Restart (new session of this package): the worktree held my V2 script with an uncommitted
change (the Moller quadrature split at the |eta_1 - eta_2| kink); it agrees with the closed
form to 4e-14 at theta 1e-3 ... 10 (smoke check, not of record; the run of record repeats it).
Committed (5d9ae56) and started as run C-20261121-074926-5d9ae56 with the predictions of
entry 6 unchanged. Blind status: in reading the section list of the collisions-2 interface
text I saw the table row of section 11.6 for T12 (core's own claim about its run
core-20261115-182101-3a6e046: same collisions with and without the flat twin, z = -0.03).
That is core's statement on its own run, not the track's reading of its runs; I note it here
so that the reader can weigh my V3 accordingly.

V3 (run C-20261119-143049-0cf699a; decks `box_tests/inputs/box_static.athinput` and
`box_c2.athinput`, arguments in each `athena.log`). Set-up read from the files: coordinate
box [10, 11)^3, 32^3 cells, gamma_ij = psi0^4 delta_ij, psi0 = 1.1, alpha0 = 0.8, zero
shift, `metric = mesh` with `<adm> dynamic = false`; sum M = 1 per coordinate volume
(nrpic.hst column 4), proper volume 1.771561 = psi0^6 (column 28). Flat twins: box side
1.21 = psi0^2, dt_flat = alpha0 dt (0.0254785 = 0.8 x 0.0318482), same sigma and seed.
Own derivation [JUDGEMENT, standard kinetic theory]: the number of collisions per proper
four-volume is (1/2) n^2 sigma_tot <v_Mol> with n the particle density in the frame of the
normal observer and <v_Mol> the Moller mean of that frame (an invariant combination, since
n_a n_b v_Mol is invariant: collisions.md section 1 says the same [BACKGROUND]). A coordinate
cell of volume dV_c has proper volume psi0^6 dV_c, a coordinate step dt is a proper time
alpha0 dt, so collisions per coordinate time and coordinate volume are
alpha0 psi0^6 x (1/2) n_p^2 sigma <v_Mol>, n_p the proper density: alpha0 psi0^6 =
1.417249 times the flat rate per unit time and volume at the same proper density and
temperature. Per step of the run, with rest-mass density rho_p = sum M/(psi0^6 V_c):
expected collisions (1/2) N rho_p sigma_m <v_Mol>(theta_s) alpha0 dt, theta_s from <W> of
the initial snapshot with W = sqrt(1 + delta^ij u_i u_j/psi0^4) (the snapshot holds
covariant u_i). Numbers at theta = 0.1: rho_p = 0.564474, sigma = 0.202463,
<v_Mol>(0.1) = 0.618059, alpha0 dt = 0.0254785: about 900 collisions per step, 1.8e5 in the
run (Poisson 0.24 percent), against 1993 per step in the flat T2 box at the same dt (ratio
alpha0/psi0^6 = 0.4516).
Predictions:
- Sum of n_coll over the 200 steps within 4 Poisson standard errors of 200 x the expected
  per-step value, and mean sum_P within 0.5 percent of it, in all four curved cases (theta
  0.1, 1; seeds 1, 2) and the `cell` case.
- Pair counting: sum_W of cycle 1 equals my own sum over the coordinate cells of
  N_c (N_c - 1) sigma M alpha0 dt / (2 psi0^6 dV_c), positions advanced by one straight
  push x + alpha0 u_i dt/(psi0^4 W) from the initial snapshot, to 1e-12 relative.
- Twins: n_tested and n_coll identical in every step between curved and flat twin;
  end-snapshot momenta u_i/psi0^2 (curved) equal to the flat u_i within 1e-12 absolute and
  positions psi0^2 (x - 10) equal to x_flat - 10 within 1e-11; hence the ratio of the
  collision counts per coordinate time and volume is alpha0 psi0^6 to the definition of the
  twin.
- Conservation: per step |dE|, max|dP_i| below 1e-14 sqrt(n_coll + 1) of sum_MW; snapshot
  sums of M u_i (covariant) constant to 1e-13 of sum M W; n_noroot = n_balance = 0 and
  max_dlam below 1e-13 (homogeneous metric: the particle metric is the cell metric).
- `cell` against `particle` (theta 0.1, seed 1): identical n_tested and n_coll in every step.
Refuted if any fails; a failure of the 4-sigma clause alone in one of five cases at about
the 4-sigma level would be reported, not explained away.

## Entry 8 (2026-11-20 23:54 PST) V2 and V3 outcomes

(Entry 7 was written at 23:50, not 23:58.)

V2, run C-20261121-074926-5d9ae56 (`figs/v2_box.png`, `figs/v2_series.png`,
`results/v2_box.json`), 16 collisional cases per executable and 2 collisionless controls:
- Reference: my rapidity quadrature equals 4 K3(2 zeta)/(zeta K2^2) to 3e-14 to 5e-14
  at theta 1e-3, 0.01, 0.1, 1, 10 (finer grid the same to 6e-14). Prediction holds.
- T2(a): |z| <= 2.10 in all 32 cases (z of sum n_coll against sum sum_P). Holds.
- T2(b), 0.5 percent clause: |sum_P per step / ((1/2) N rho_0 sigma <v_Mol>(theta_s) dt) - 1|
  <= 9.6e-5 in all cases. Holds. 4-standard-error clause: with the standard error of the
  step-to-step scatter (std/sqrt(200), the literal definition) |z| <= 2.92 in all cases:
  holds. With my stricter batch-mean error (10 batches of 20 steps) two of the 16
  configurations reach z = +4.21 (theta 1e-3 plain seed 2) and -4.55 (theta 1 sub seed 2),
  identical in both executables (same pairs). The decomposition locates them in the sample:
  the tested pairs agree with the sample's own all-pairs Moller mean (2e7 random pairs) within
  |z| <= 2.26 in all 32 cases, and sum_W (positions) and the tested <v_Mol> (velocities)
  deviate by a few 1e-5 each, the size the 2a clarification of TESTS.md names. Prediction
  "the 4-se clause may fail at the 1e-4 level through the finite sample" came true in this
  stricter form only.
- T2(c): sum M W of the end snapshot equals that of the start exactly (math.fsum difference
  0.0 in every case); KS p of |u| at the end against MJ(theta_s) 0.095 ... 0.985. Holds.
- T1: largest per-step |dE| / sum_MW is 1.1e-7 of the bound 1e-14 sqrt(n_coll + 1), largest
  |dP_i| 3.6e-8 of it; snapshot sums of M u_i change by <= 5e-19 of sum M W over the run;
  step-to-step change of the history sums of M u_i <= 5.9e-17; n_trunc = 0; collisions-2 in
  flat space: n_noroot = n_balance = 0, max_dlam = 0. Holds. The 1e4-step drift clause
  cannot be tested on these 200-step runs (energy exactly conserved over 200 steps).
- Both executables tested and collided the same pairs: n_tested and n_coll identical in all
  200 steps of all 16 cases, sum_P to 8.9e-16. Holds.
- Controls: momenta of the end snapshot bit-identical to the start, energy change 0. Holds.

V3, run C-20261121-075256-2084cb5 (`figs/v3_static.png`, `results/v3_static.json`):
- Rate: sum n_coll over 200 steps against my expectation (1/2) N rho_p sigma <v_Mol>
  alpha0 dt (rho_p = 0.564474 = 1/psi0^6): z = -1.02, +0.27 (theta 0.1, seeds 1, 2),
  -0.67, -0.61 (theta 1), -1.02 (`cell`); mean sum_P within 9e-5 of the expectation.
  Collisions per coordinate time and coordinate volume: 28203.7 (theta 0.1 seed 1) against
  19900.3 of the flat twin per its time and volume: ratio 1.417249 = alpha0 psi0^6. Holds.
- Pair counting: sum_W of cycle 1 equals my count from the straight-pushed snapshot to
  2.5e-13 ... 4.1e-13 relative in all nine cases (curved and flat). Holds (prediction 1e-12):
  the proper volume psi0^6 dV_c and the proper time alpha0 dt enter as derived.
- Twins: n_tested and n_coll identical in all 200 steps of all four pairs; end momenta
  u_i/psi0^2 equal the flat ones within 1.4e-14 (theta 0.1) and 2.5e-13 (theta 1), positions
  within 4.0e-13. Holds.
- Conservation: per-step |dE| <= 3.6e-7 and |dP| <= 3.2e-8 of the T1 bound; snapshot sums of
  the covariant M u_i constant to 6.2e-17 of sum M W, sum M W exactly; n_noroot = n_balance =
  0, max_dlam 5e-14 (theta 1), 0 (theta 0.1). Holds.
- `cell` against `particle`: identical counts in every step, end momenta within 1.3e-14.
- Remark: the end snapshot of every case carries cycle 199 in its header while the history
  has 200 records; the time of the snapshot is the end time, so I take it as the header
  convention of the snapshot writer, not a missing step [TO VERIFY with core; no influence on
  any number above, which use the history for counts and the snapshot only for sums that do
  not change without collisions].

Correction to entry 8: the snapshot remark is settled: the end snapshot of T12_th0.1_curved_s1
carries time 6.369635175264278, equal to the time of history record 200 (cycle 200), header
cycle 199; so the header counts the cycle before the last increment [VERIFIED, own read].

## Entry 9 (2026-11-21 00:02 PST) V4 set-up and predictions, before any computation

Sources read (kb-data/raw, untrusted data, read only):
- arXiv:2009.08163 v1 `paper.tex`: Schwarzschild-coordinate field equations lines 305-314,
  sources rho, p, j lines 343-355; King ansatz f0 = (e^{1 - E/E0} - 1)_+ line 635, E = eps e^mu
  line 615; y = ln E0 - mu and the reduced equation lines 661-673, z_c = e^{y0} - 1 line 685;
  binding energy E_b = (N - M)/N lines 920-924; Table "First binding energy maximizer and
  zero": King y_max = 0.334, y_zero = 0.784 (line 953) [VERIFIED read].
- arXiv:2108.11967 v2 `main.tex` (F21): truncated distribution line 113, w, alpha, b and
  T(r) = T(R)/(1 - b w) line 118, moments (I integrals) lines 124-138, gamma = 1 + p/u
  line 174, TOV line 144, pulsation equation lines 202-204, trial function xi = r e^Phi and
  <gamma>, gamma_cr lines 208-218 and appendix lines 406-461, E_rest line 244, Z(r) line 256;
  b = 0.1 results: adiabatic criterion at v(0) = 0.566, Z(0) = 0.750 (line 274), w(0) = 4.05
  (line 276); eps_max = 0.0352 at v(0) = 0.506, Z(0) = 0.548 (line 280); B_max = 8.49e-4 at
  Z(0) = 0.297 (line 286), E_max = 3.47e-2 at Z(0) = 0.087 (line 286); Table 1 b = 0.1
  (lines 490-503, a grid in w(0) of step 0.2-0.5; the marginal rows are underlined:
  w(0) = 0.6 (E), 1.9 (B), 3.2 (eps), 4.05150 (<gamma> = gamma_cr = 1.62117, Z(0) = 0.750107,
  M = 1.42556e-2, R = 0.368001, rho(0) = 81.7923, p(0) = 8.74006)); their R carries a grid
  step of 1e-3 (values 0.368001, 0.378001, ...).

Own formulation [JUDGEMENT, own algebra; checked against both papers' definitions]. Static
spherically symmetric Einstein-Vlasov, Schwarzschild coordinates, G = c = m = 1,
f = (exp((E0 - E)/T_inf) - 1)_+ with E = eps e^mu the conserved energy and T_inf = b E0. With
y = ln E0 - mu: local cutoff energy eps_c = e^y (y = 0 at the surface R), local temperature
T = b e^y (Tolman), and F21's w = (1 - e^{-y})/b (so T = T(R)/(1 - b w) and 1 + eps_c/m =
e^{y}; for b = 1 this is the King ansatz of 2009.08163 exactly, T_inf = E0). Moments at y:
n = 4 pi int_1^{eps_c} f eps sqrt(eps^2 - 1) d eps, rho = 4 pi int f eps^2 sqrt(eps^2 - 1),
p = (4 pi/3) int f (eps^2 - 1)^{3/2}, f = exp((eps_c - eps)/T) - 1. With coefficient 1 these
equal F21's hat quantities exactly (rho = 4 sqrt2 pi I_rho, p = (8/3) sqrt2 pi I_p with x =
(eps - 1)/T), so lengths come out in F21's unit zeta and Table 1 can be compared number by
number. Equations: m' = 4 pi r^2 rho, y' = -(m + 4 pi r^3 p)/(r (r - 2 m)), N' = 4 pi r^2 n
(1 - 2m/r)^{-1/2}; M = m(R), E_b = (N - M)/N, B = N - M, Z(0) = e^{y0}(1 - 2M/R)^{-1/2} - 1,
v(0) = sqrt(3 p/rho) at the centre, Phi = (1/2) ln(1 - 2M/R) - y.
Radial pulsation [Chandrasekhar's equation as printed in F21 lines 202-204, put in
variational form by me]: omega^2 int e^{3 Lam - Phi} (rho + p) r^2 xi^2 = int e^{3 Phi + Lam}
(gamma p/r^2) [(r^2 e^{-Phi} xi)']^2 + int e^{Phi + Lam} r^2 [4 p'/r + 8 pi e^{2 Lam} p (rho + p)
- p'^2/(rho + p)] xi^2 (boundary terms vanish: xi(0) = 0, p(R) = 0); the same as F21
eq. (integral) after their first integration by parts. Rayleigh-Ritz with xi_k = r e^Phi
(r/R)^{2k}, k < K: K = 1 is F21's trial function; the lowest eigenvalue of the K x K
generalised problem is an upper bound of omega_0^2 that decreases with K (converged by K = 6
expected). Two adiabatic indices: F21's gamma = 1 + p/u (u = rho - n), and the Juttner
Gamma_1(T) = 1 + 1/c_v(T) of the local temperature T = b e^y (ideal classical gas: p = n T,
adiabatic n c_v dT = T dn, so (d ln p/d ln n)_s = 1 + 1/c_v; c_v = d<E>/dT of
Maxwell-Juttner, <E> = K3/K2 - T; limits 5/3 and 4/3).

Predictions:
- Check of the formulation: at F21's tabulated w(0) (b = 0.1) my M, E_rest, eps, rho(0),
  p(0), v(0), <gamma>, gamma_cr agree with Table 1 to 4 significant digits, and R and Z(0)
  to their R grid (about 3e-3 relative). F21's closed-form gamma_cr equals my K = 1 Rayleigh
  quotient form to 1e-8. Refuted otherwise (then my formulation or their table is wrong and I
  must find which before using either).
- V4(a): King (b = 1): first maximum of E_b at y0 = 0.334 +- 0.0010 (published 0.334), and
  the first zero of E_b at 0.784 +- 0.001.
- V4(b): King with Juttner Gamma_1: the gas is hot (T >= T(R) = m), Gamma_1 ~ 1.36-1.38, so
  the fluid onset comes far before the E_b maximum: y0_onset in [0.02, 0.15] (estimate from
  the homogeneous-sphere gamma_cr = 4/3 + (19/42)(2M/R) [BACKGROUND, from memory]). With
  F21's gamma = 1 + p/u the onset lies later than with Gamma_1. The exact (K = 6) onset lies
  at y0 <= the K = 1 onset (upper-bound property).
- V4(c): F21 b = 0.1 with their gamma: onset w(0) = 4.05 +- 0.03, Z(0) = 0.750 +- 0.005;
  eps_max 0.0352 +- 0.0002 at Z(0) in [0.50, 0.59]; B max at Z(0) in [0.25, 0.35]; E max at
  Z(0) in [0.05, 0.15]. With the Juttner Gamma_1 of the local temperature: onset at a smaller
  Z(0), in [0.35, 0.70] (Gamma_1 falls with T twice as fast as 1 + p/u of a full MJ gas, and
  the truncation raises 1 + p/u further); exact onset Z(0) <= K = 1 onset, within 3 percent.
- Afterwards I compare with the model files of runs C-sidm-20261115-120610-b4592be and
  C-20261115-170742-84990ed. Their file names, seen when listing the directories, carry
  King y0 = 0.31400 ... 0.35400 including 0.33403, and F21 Z(0) = 0.5000 ... 0.6348
  including 0.5331, 0.5404, 0.6348; the manifest purpose says "near the E_b maximum and at
  both fluid onsets". I have not opened the files. My predictions above were formed from the
  papers; the names are noted here so that the reader can judge.

## Entry 10 (2026-11-21 00:12 PST) V4 debug evaluations (not of record) and sharpened predictions

(Entry 9 was written at 23:57 on 2026-11-20, not 00:02.)
Debug evaluations of v4_ev.py before the run of record (interactive, not registered; numbers
here only motivate the method, the run of record repeats them):
- At F21's marginal row (b = 0.1, w(0) = 4.05150) my equilibrium gives M = 0.0142545 (F21
  0.0142556), E_rest 0.0147413 (0.0147424), eps 0.0330228 (0.0330243), R 0.368803 (0.368001,
  their grid), Z(0) 0.750099 (0.750107), rho(0) 81.79233 (81.7923), p(0) 8.740059 (8.74006),
  v(0) 0.566189 (0.566189), <gamma> 1.621166 (1.62117), gamma_cr 1.621186 (1.62117). F21's
  closed-form gamma_cr equals my K = 1 Rayleigh quotient to 4e-13. The formulation reproduces
  F21 (prediction of entry 9 holds at this row; the run of record checks five rows).
- The polynomial Rayleigh-Ritz basis (r/R)^{2k} did not converge with K (lowest omega^2 at
  that row -0.0006, -0.88, -1.61, -2.15, -2.54, -2.80 for K = 1..6), although each single
  basis function has a positive quotient there: the mode is concentrated in the core
  (rho_c/rho_mean = 1206), which powers of r/R represent badly. Replaced by piecewise-linear
  finite elements for eta = xi/(r e^Phi) on J elements uniform in u = sqrt(r/R) (the F21 trial
  function is eta = const, inside the space, so FEM <= K = 1 by construction); diagonal
  scaling of the mass matrix before the generalised eigenproblem. Converged: J = 100, 200, 400
  agree to 1e-4 relative at all points tried. The FEM eigenvector at that row is concentrated
  in the core (eta falls from 1 at r/R = 0.02 to 0.24 at 0.4 and changes sign near the surface).
- Consequence seen in the debug evaluation (b = 0.1, F21's gamma = 1 + p/u): exact omega^2
  = +0.89 at Z(0) = 0.548, -0.050 at 0.638, -3.32 at 0.750, while the F21 trial function is
  +1.06, +0.71, -0.0006 there. So the exact fluid onset with F21's own gamma lies near
  Z(0) = 0.63, well before F21's 0.750; the "insensitivity to xi" of F21 line 220 does not hold
  for these centrally condensed models [JUDGEMENT until the run of record].
- Juttner Gamma_1: b = 0.1 exact -1.67 at Z(0) = 0.548 and +0.027 at 0.087; King: exact
  +1e-5 at y0 = 0.02, -8e-5 at 0.05 (F21's gamma: stable up to y0 = 0.334 at least).
Sharpened predictions for the run of record (v4_ev.py at the commit after this entry):
- King Juttner exact onset y0 in (0.02, 0.05); King with F21's gamma: no onset below the E_b
  maximum.
- F21 b = 0.1: F21-gamma K = 1 onset at Z(0) = 0.750 +- 0.002 (reproduction), exact onset
  in (0.548, 0.638); Juttner: K = 1 and exact onsets both in (0.087, 0.548), exact below K = 1.
- J = 400 onset equal to J = 200 to 1e-4 in y0.

## Entry 11 (2026-11-21 00:04 PST) V4 first run failed at the figure; numbers seen; variant added

(Entry 10 was written at 00:01, not 00:12.)
Run C-20261121-080152-b8d0acd computed everything and wrote v4_ev.json, then failed on the
figure (`nrpic` not on the path: the script did not add the worktree's python/ directory).
It stays on record as failed. Numbers it printed (the rerun of record must reproduce them):
F21 Table 1 rows reproduced (M, E_rest, eps, Z(0), rho(0) to <= 1.3e-4; R to <= 0.25 percent,
their grid); King E_b maximum y0 = 0.334032, zero 0.784518; F21 turning points Z(0) = 0.0891
(E), 0.2997 (B), 0.5404 (eps); onsets: King 1+p/u K1 y0 0.3961, FEM 0.3721; King Juttner K1
0.03935, FEM 0.03919; F21 1+p/u K1 Z(0) 0.75001, FEM 0.6348; F21 Juttner K1 0.4357, FEM 0.4125.
Two of these coincide with names of the track's model files (entry 9): Z(0) = 0.5404 (my eps
maximum) and 0.6348 (my exact onset with F21's gamma). The third name, 0.5331, matches none of
my numbers. A plausible other reading of "Juttner adiabatic index" is 1 + p/u of a full
Maxwell-Juttner gas at the local temperature (p = nT, u = n(<E> - 1)), which is not
(d ln p/d ln n)_s; I add it as a labelled sensitivity variant (`mjpu`) so that a difference of
definition can be told from an error. Prediction for the variant (before running): its onset
lies between my Juttner Gamma_1 onset and the F21-gamma onset (1 + p/u of MJ falls with T half
as fast as Gamma_1), i.e. Z(0) in (0.41, 0.63) exact. My verdict uses Gamma_1 = (d ln p/d ln
n)_s = 1 + 1/c_v, the adiabatic index of the pulsation equation (F21 appendix line 386 defines
gamma the same way).

## Entry 12 (2026-11-21 00:16 PST) V4 run of record, then the model files; predictions for the comparison

V4 run of record C-20261121-080313-84094f1 (`figs/v4_ev.png`, `results/v4_ev.json`) reproduced
the numbers of entry 11 exactly. Outcomes against entries 9-10:
- F21 Table 1, five rows: M, E_rest, eps, Z(0), rho(0), p(0), v(0), <gamma>, gamma_cr within
  1.3e-4 (M at w(0) = 4.5: -1.1e-4; most within 1e-5); R within 0.25 percent (their 1e-3 grid);
  closed-form gamma_cr = K = 1 quotient to 4e-13. Prediction holds.
- (a) King E_b maximum y0 = 0.334032 (E_b = 0.0355886), zero 0.784518: paper 0.334 and 0.784
  (2009.08163 line 953). Holds.
- (b) King, Juttner Gamma_1(T_Tolman): exact onset y0 = 0.039192 (J = 400: 0.039191),
  Z(0) = 0.0558, K = 1 onset 0.039350: far below the E_b maximum. Holds (predicted
  [0.02, 0.15], sharpened (0.02, 0.05)). With F21's 1 + p/u: exact onset y0 = 0.37206 (Z(0) =
  0.5757), K = 1 0.39612 - after the E_b maximum, not before it. Full-MJ 1 + p/u variant:
  exact 0.11137.
- (c) F21 b = 0.1: turning points Z(0) = 0.08913 (E max), 0.29966 (B max), 0.54041 (eps max,
  eps = 0.035179). F21: 0.087, 0.297, 0.548 on their w(0) grid, eps_max 0.0352: holds within
  their grid. Onsets: F21 gamma K = 1 Z(0) = 0.75001 (w(0) = 4.0511; F21 0.750, 4.05: holds);
  exact 0.63482 (w(0) = 3.5871; predicted (0.548, 0.638): holds). Juttner Gamma_1(T_Tolman):
  K = 1 Z(0) = 0.43567, exact 0.41253 (w(0) = 2.5329, v(0) = 0.4533) (predicted (0.087, 0.548),
  exact below K = 1: holds). Full-MJ 1 + p/u: K = 1 0.59440, exact 0.54038 (between my two,
  as predicted; it falls on the eps maximum 0.54041 to 3e-5 in Z(0) [observation, not
  understood]). J = 400 onsets equal J = 200 to <= 6e-7 in y0. All holds.
- Not predicted: F21's trial-function quotient turns positive again above Z(0) ~ 1.3 while
  the exact eigenvalue stays negative (figure, lower left): the K = 1 criterion is not
  reliable along this family.

Model files. Listing their JSON fields (family, b, y0, role, and the scalar fields) showed me
the track's labels: King 0.33403216 "threshold (computed y_max)"; b = 0.1 Z(0) = 0.5404 "E_b
maximum (computed), F21 turning point", 0.6348 "fluid onset, F21 gamma = 1 + p/u", 0.5331
"fluid onset, Juttner Gamma_1 at the energy-matched temperature". So the difference to my
Juttner onset (0.4125) is one of definition: their temperature is the MJ temperature with the
same mean energy per particle (<E>_MJ(T) = rho/n), mine the Tolman temperature b e^y of the
truncated distribution. Predictions for v4_models.py (run after this entry):
- At each model's y0 my E_b, C, Z(0), M (F21/King paper units), R/M, M0/M, n_c, rho_c, p_c
  agree with the file to 1e-6 (both solve the same ODE; the King and b = 0.1 values listed
  agree with mine to ~1e-8 where I can see them).
- k = 0.5 polytrope (2009.08163 line 954): E_b maximum at 0.298 +- 0.001, zero 0.693 +- 0.001.
- Energy-matched temperature: T_em < T_Tolman (truncation removes the tail), so Gamma_1 is
  larger and the onset later than 0.4125; exact onset Z(0) = 0.533 +- 0.002 if the track used
  the exact fundamental mode, about 0.56-0.60 if it used the trial function.
- Particles of the threshold models: KS distance of the isotropic-radius distribution from my
  enclosed rest mass below 1.36/sqrt(1e5) = 4.3e-3 (stratified samples: expect much less).

## Entry 13 (2026-11-21 00:12 PST) V4 model files: outcome

(Entry 12 was written at 00:06.) Run C-20261121-080633-8ee41f7 completed, but its particle-sample
check had a sign error in my isotropic-radius integral (KS distance 1.0 in all three samples:
my bug, the radius grid ran the wrong way); fixed (commit after it) and rerun as
C-20261121-080720-dbcd7ff, which is the run of record (`figs/v4_models.png`, redrawn
`figs/v4_ev.png` with the right axis inside the frame, `results/v4_models.json`). Outcomes:
- 18 King and b = 0.1 model files (both runs): my equilibrium at the file's y0 reproduces E_b,
  C, Z(0), M (paper units), R/M, M0/M, n_c, rho_c, p_c to <= 6e-10 relative. Prediction (1e-6)
  holds. The five k = 0.5 polytrope files agree to 2e-5 (E_b) and 5e-6 (others): my 48-point
  Gauss rule meets the square-root edge (1 - E/E0)^{1/2} of that ansatz and is the less accurate
  side [JUDGEMENT]; the gr-qc/0601112 shell files were not checked (other ansatz, L0 > 0).
- k = 0.5 polytrope: E_b maximum y0 = 0.297661 (file 0.297664), zero 0.693022; paper 0.298,
  0.693 (2009.08163 line 954). Holds.
- Energy-matched temperature (<E>_MJ(T) = rho/n): T_em(0) = 0.0959 against T_Tolman(0) =
  0.1456 at the b = 0.1 onset; exact onset Z(0) = 0.533057 (y0 = 0.3755336, J = 400 the same),
  the file 0.5330561 (y0 0.37553330): agreement 1e-6; the trial function gives 0.5947. So the
  track's onset is the exact fundamental mode with Gamma_1(T_em). Prediction holds (0.533 for
  the exact mode). For King the two temperatures differ grossly (T_em(0) = 0.10 against
  T_Tolman(0) = 1.38; w(0) = 0.27: the distribution is far from thermal); energy-matched
  exact onset y0 = 0.32143 (Z(0) = 0.4910), K = 1 0.34033.
  [JUDGEMENT] For a collision-dominated gas the relevant equation of state is that of the
  Maxwell-Juttner gas the collisions produce at fixed number and energy density, so the
  energy-matched temperature is the physically appropriate reading of "Gamma_1 of the local
  temperature"; my Tolman-temperature reading (0.4125; King 0.0392) uses a parameter of the
  truncated distribution that is not the thermodynamic temperature of its particles.
- Particle samples of three threshold models (1e5 each): the isotropic-radius distribution
  equals my enclosed rest-mass fraction to D = 1.0e-5 = 1/N (stratified sampler: exact
  quantiles); rbar_s mine = file to 1e-12; sum of the particle masses = my M0/M to 6e-13.

## Entry 14 (2026-11-21 00:10 PST, from `date`) V5 set-up and predictions, before any computation

(Entry 13 was written at 00:08.) Runs (layouts read from the run directories and decks):
T10 C-20261119-143041-f94e350 (collisions-2 CPU, coll_energy = particle, 1e5 particles, 16^3
cells, seed 7, 100 cycles; MeshBlocks 1, 8, 64; restarts written every 37 cycles of mb8 and
resumed: rst0 (cycle 0), rst1 (37), rst2 (74), rst3 (100, no step); seed 8). T1 long
C-20261115-170741-248af65 (release CPU, twotemp 0.3/0.1, 1e5 particles, 1e4 steps, seeds 1, 2).
T3/T4 C-20261115-170539-28432c3 (release CPU, twotemp theta1 = 3 theta2, theta2 = 1e-3 and 1,
N = 1e6, seeds 1, 2; A: snapshots every 0.01 tau_rel to 0.25, B: the same start run to 15 tau_rel
with snapshots every 0.25). T9 C-20261115-170814-8a54b43 (release CPU, classes M and 4M with
equal total mass, thetaA = 0.03, thetaB = 0.01, nanbu weights, 8 seeds; refusal case).
Own exact initial relaxation rate [JUDGEMENT, own derivation]: an inter-population collision
moves particle a of population 1 to energy (W_a + W_b)/2 on direction average (isotropic in
the centre-of-momentum frame: <E_a'> = gamma_cm E* = E/2); collisions inside a population do
not change its energy; so d e_1/dt = n_2 sigma <v_Mol (W_b - W_a)/2>_{MJ1 x MJ2} and with
theta_i from the mean energy, d(theta_1 - theta_2)/dt = sigma X (n_2/c_v(theta_1) +
n_1/c_v(theta_2)), X = <v_Mol (W_b - W_a)/2>; n_1 = n_2 = 1/2 (rho_0 = 1, m = 1). X by my
two-dimensional quadrature (angular average of v_Mol in closed form, as in V2), checked by a
Monte Carlo of 4e6 random pairs within 4 standard errors.
Predictions:
- T10: final snapshots of mb1, mb8, mb64, rst0, rst1, rst2 bit-identical after sorting by tag
  (x, u, m, tag); the coll.hst records of rst1 and rst2 equal those of mb8 for the same cycles;
  seed 8 differs. Extra: in T345 the B run's snapshot at 0.25 tau_rel equals the A run's last
  snapshot bit for bit (same start, seed, step).
- T1 long: relative drift of the exactly rounded sum M W over 1e4 steps below 1e-11 (I expect
  < 1e-13); per-step defects below the T1 bound; n_trunc = 0.
- T3 (end of B): KS p > 1e-3 of |u| against MJ(theta_eq) (theta_eq from the conserved mean
  energy of the sample); <u^2/W> = 3 theta_eq within 4 sigma; both populations at theta_eq
  within 4 sigma; all four cases.
- T4: quadratic fit of theta_1 - theta_2 over the first 0.15 tau_rel (16 snapshots of A) gives
  a slope within 4 se + 1 percent and within 5 percent of my exact rate, all four cases. My
  own tau_rel = (theta_1 - theta_2)/|rate| should match the snapshot spacing x 100 to a few
  percent if the generator used the same rate.
- T9: at the end both classes at the same theta within 4 sigma and KS p > 1e-3 against
  MJ(theta_eq); mean over the 8 seeds of the drifts of sum M W and sum M u_i zero within
  4 standard errors; the equal-weights case stops with an error that names the unequal masses
  (I saw that message already when listing the directory).
- T5 (entropy) is not attempted: it needs an entropy estimator with its own bias study.

## Entry 15 (2026-11-21 00:15 PST) V5 outcome (run C-20261121-081036-0d6117b) and one more prediction

(Entry 14 was written at 00:09.) `figs/v5_box.png`, `results/v5_box.json`.
- Quadrature of X = <v_Mol (W_b - W_a)/2> against 4e6-pair Monte Carlo: z = 0.99, 0.32, -1.27
  (theta pairs 3e-3/1e-3, 3/1, 0.3/0.1); non-relativistic limit -2.018e-4 at 3e-3/1e-3 against
  my quadrature -2.016e-4 [own algebra, entry 14]. Holds.
- T10: final snapshots of mb1, mb64, rst0, rst1, rst2 bit-identical to mb8 (also the whole
  files byte for byte); seed 8 differs in every momentum. History of the restarts identical to
  mb8 record by record (100, 63, 26 records); the MeshBlock variants have identical counts but
  differ in the last bits of the sums (sum_P, sum_MW, sum_W to <= 1.8e-13 relative; sum_Mu_i,
  which are ~1e-18 absolute, differ in their rounding): summation order over blocks, which only
  enters the history (as collisions.md 3.9 says). In T345 the B run's snapshot at cycle 49
  equals the A run's last snapshot bit for bit in all four cases. Prediction holds. Not tested:
  MPI ranks (no MPI in that executable).
- T1 long: the exactly rounded sum M W of the snapshots does not change at all over 1e4 steps
  (drift 0.0 in both seeds; momentum sums 2.4e-18); per-step defects <= 8.8e-7 of the bound;
  n_trunc = 0; 1.56e7 collisions per seed. Holds (criterion 1e-11).
- T4: fitted initial slope / my exact rate - 1 = -0.37, -1.74, +0.03, +0.88 percent (theta2 =
  1e-3 s1, s2; 1 s1, s2), fit errors 0.5, 0.6, 0.4, 0.3 percent: all pass both clauses
  (4 se + 1 percent; 5 percent). My tau_rel = (theta1 - theta2)/|rate| equals 100 snapshot
  spacings to 0.1 percent, so the generator used the same initial rate. |v_a - v_b| instead of
  v_Mol: 1.265 times the rate at theta2 = 1, 1.0007 at 1e-3 (TESTS T4 says 1.27, 1.0008).
  Holds.
- T3 (end of B, 15.0 tau_rel): KS p = 0.084, 0.77, 0.99, 0.92; <u^2/W> - 3 theta_eq: |z| <= 0.007;
  populations at theta_eq: |z| <= 0.78. Holds.
- T9: classes at the same theta: |z| <= 1.16 in all 8 seeds (holds); refusal with
  coll_weights = equal names the unequal masses (holds); mean energy drift over the seeds
  +5.3e-5 +- 2.2e-5 of the total energy (z = 2.42), momentum z = 0.40, 2.19, 1.08: zero within
  4 se (holds, but the energy drift is positive in 7 of 8 seeds). KS against MJ at the theta of
  the INITIAL energy: light class p = 1.7e-4 in seed 3 (fails p > 1e-3), all others >= 0.049.
  Seed 3 has the largest energy drift (+1.48e-4); a drift dE raises theta by about dE (1 + <K>)/c_v
  = 1.0e-4, which is what the light class shows (0.020202 against 0.020108).
Prediction for v5_t9ks.py (run after this entry): with theta from the FINAL energy, or the
class's own theta, every class passes KS p > 1e-3 in all 8 seeds, and the classes agree with
the final-energy theta within 4 sigma: then the seed-3 failure is the temperature offset of the
nanbu energy drift, not a departure from the Maxwell-Juttner shape.

## Entry 16 (2026-11-21 00:16 PST) V5b outcome (run C-20261121-081415-b8c9d29); blind verdicts

`figs/v5_t9ks.png`, `results/v5_t9ks.json`. With theta from the final energy every class passes
KS (p >= 0.084) in all 8 seeds, and with its own theta (p >= 0.089); each class agrees with
the final-energy theta within |z| <= 1.30. Prediction holds: the seed-3 KS failure at the
initial-energy theta is the offset caused by the nanbu energy drift (+1.48e-4 in that seed),
not a departure from the Maxwell-Juttner shape. T9 as written ("both Maxwell-Juttner (KS p >
1e-3)") does not name the theta; against the theta of the initial energy it fails in 1 of 16
class-seeds, against the final-energy theta it passes everywhere [JUDGEMENT: the definition
should name the reference temperature; with nanbu the energy is conserved only in
expectation].
Next: VERDICTS_BLIND.md completed with V5 and committed and pushed before any claim is read.

## Entry 17 (2026-11-21 00:22 PST) Claims read (after the blind verdicts were committed and pushed, 00adbb95); predictions for the claim checks

Read now: stage/G1/CHECKLIST.md, stage/G1/EVIDENCE.md, heat/README.md (results, verdict),
box_tests/README.md (results), models/README.md (models, results), stage/REVIEW-wave2.md
sections 1-3 and 6. Most numbers agree with my blind values (VERIFIER.md). Four claims need a
computation I had not done; predictions before the run (v6_claims.py):
- T10: 385554 collisions in mb8 of both T10 runs, the same in mb1 and mb64 (counts identical);
  release snapshots of 8/64 MeshBlocks and restarts byte-identical to 1 MeshBlock.
- REVIEW-wave2 section 3: "first mass maximum of the King sequence (y0 = 0.0982)". With the
  King ansatz at fixed amplitude (f = e^{1 - E/E0} - 1) the maximum of M(y0) lies near 0.098
  if the claim used the same normalisation [no prior of mine; a pure check].
- T6(b) "literal 0.994, 1.027" with chi(kappa_1, theta = 0.015): my linear values 1.051, 1.086
  were taken with chi_1 at the final temperature 0.013359 (particle-weighted); converted to
  0.015 they become 0.994, 1.027 if the difference is only the reference temperature.
- heat/README quotes my V1a as 1.0988 +- 0.0015 (theta 0.1) and 0.9933 +- 0.0010 (theta 1):
  my ce_kappa.json order 4 divided by 75 sqrt(pi)/64 should give these.

## Entry 18 (2026-11-21 00:21 PST) Claim checks outcome (run C-20261121-081715-2ad1421); VERIFIER.md

All four predictions of entry 17 held: 385554 collisions in mb1/mb8/mb64 of both T10 runs (seed 8:
385838); release T10 snapshots byte-identical to 1 MeshBlock; King mass maximum at y0 = 0.098197
(claim 0.0982; the rest mass peaks at 0.1050, `figs/v6_king_mass.png`); T6(b) literal at
theta = 0.015: 0.9940, 1.0271 (claim 0.994, 1.027: the only difference is the reference
temperature); CE ratios 1.0988(15), 0.9933(10) as quoted. VERIFIER.md written
(`../stage/G1/VERIFIER.md`): claims found wrong or unsupported: the seed-8 collision count wording
(REVIEW-wave2.md:49), the T9 KS clause without a named reference temperature, the fit-specific
size of the number-mode bias, and (baseline paper) F21's trial-function onset cited as the onset.
The blind verdicts were not changed.
