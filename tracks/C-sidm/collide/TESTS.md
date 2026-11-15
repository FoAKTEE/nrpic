# TESTS: Minkowski-box tests of the collision operator, with pass criteria

Written 2026-11-15, before any run of a collision code (none exists yet:
`core/collisions` holds no commit beyond main). The criteria below are fixed now; a
change after a run is recorded in `JOURNAL.md` with its reason. References:
`REFERENCES/` (SPEC.md sections named). Analysis: `analysis/`. Inputs: `inputs/` and
`analysis/make_box.py`. Executable: the one built from `core/collisions` once core has run
its own tests; processor build first, card only where stated.

## 1. Common set-up

- Flat metric: `<particles> metric = kerr_schild`, `bh_mass = 0`, box at x0 = 10 (the
  functor divides by r); periodic mesh in all directions; `deposit = false`;
  `pgen_name = nrpic_geodesic` (no `<z4c>`). Verified for the collisionless case: run
  C-sidm-20261115-121302-313d399 (T6-0 in `JOURNAL.md`, positions exact to 1.8e-12 L).
- Particles: `make_box.py KIND` (Poisson positions, mirrored momenta per population,
  equal rest masses unless `unequal`); m = 1, theta = T/m; mean rest-mass density
  rho_0 = 1; the cross-section per unit mass sigma sets lambda = 1/sigma.
- Collision options needed (SPEC.md 4.8; names to be replaced by core's
  `tracks/core/interfaces/collisions.md`): `collisions = true`, `coll_sigma`,
  `coll_pmax`, `coll_subcycle`, `coll_nsub_max`, `coll_cell_factor`, `coll_weights`,
  `coll_dump_cycle`, `<job> rng_seed`; history `<base>.coll.hst` with the columns of
  SPEC.md 4.7; snapshots `snap_dt`.
- Statistics: "within k sigma" means with the standard error estimated in the analysis
  (Poisson for counts, sample variance for means, resampling where stated). Every test
  runs with two seeds; both must pass.
- t_coll = 1/Gamma (SPEC.md eq. R); tau_rel of SPEC.md section 6.

## 2. Tests

T0 Kernel unit test (core runs it). Input `REFERENCES/test_vectors.json` (209 cases,
inputs exact as hexadecimal doubles, outputs from the 60-digit evaluation;
`kinematics.make_test_vectors`). Pass: for every case the kernel's u_a', u_b' are within
1e-13 of max(1, |u_a|, |u_b|) of the expected values, and the pair's four-momentum is
conserved to 4 eps of the pair energy. The oracle itself reaches 1.1e-15
(`JOURNAL.md`, R2b).

T0b Replay of one collision step. `coll_dump_cycle = 20` on the T2 box at theta = 0.1
with 1e4 particles in 4^3 cells. `analysis/replay.py` (to be written against core's dump
format) recomputes from the "before" dump: cell membership, pairing keys (K1), order,
probabilities (SPEC.md eq. P), acceptances (K2), directions (K3) and the scattering
(oracle), with the Python twin `python/nrpic/rng.py`. Pass: identical set of tested pairs
and of accepted pairs; every post-collision u within 1e-13 of max(1, |u|) of the "after"
dump; untouched particles bit-identical.

T1 Conservation (equal masses). Any collisional run below. Pass: per step the relative
change of sum M W and of each sum M u_i across the collision step (coll.hst) below
1e-14 sqrt(n_collisions + 1); over a run of 1e4 steps the relative drift of sum M W in
`<base>.nrpic.hst` below 1e-11; `n_truncated = 0`.

T2 Collision rate. `make_box.py mj`, theta in {1e-3, 0.1, 1, 10}, N = 1e6, 32^3 cells
(~30 per cell), sigma chosen so that max P ~ 0.02 without sub-cycling (one run per
theta) and one run per theta with sub-cycling active (max P before sub-cycling ~ 0.5),
200 steps. Pass: (a) the accepted collisions over the run agree with sum_P (the
conditional expectation the code reports) within 4 sqrt(sum_P); (b) sum_P per step agrees
with the analytic expectation (1/2) N rho_0 sigma <v_Mol>(theta) dt within 4 standard
errors of its step-to-step scatter and within 0.5 percent; (c) the gas stays
Maxwell-Juttner: theta from <W - 1> constant within 4 sigma.

T3 Relaxation to Maxwell-Juttner. `make_box.py twotemp` (theta_1 = 3 theta_2,
n1 = n2), theta_2 in {1e-3, 1}, N = 1e6, run to 15 tau_rel. Pass at the end:
Kolmogorov-Smirnov test of |u| against MJ(theta_eq) with p > 1e-3 (theta_eq exact from
energy conservation, SPEC.md 6), the identity <u^2/W> = 3 theta_eq within 4 sigma, and
both populations (tags) at theta_eq within 4 sigma.

T4 Two-temperature initial rate. Same runs, snapshots every 0.01 tau_rel up to
0.15 tau_rel. Population temperatures theta_i(t) from their mean kinetic energies
(`mj.theta_from_kinetic`); linear fit of theta_1 - theta_2 over [0, 0.1 tau_rel]. Pass:
slope within 4 standard errors of the fit and within 5 percent of
`relax.dtheta_dt` (exact initial rate, quadrature; at theta_2 = 1e-3 the
non-relativistic closed form agrees with it to 0.5 percent). Refutes the use of
|v_a - v_b| instead of v_Mol at theta_2 = 1: that rate is 1.27 times the correct one
(`REFERENCES/tests/test_rate.py::test_noninvariant_relative_speed_is_refuted`, Monte
Carlo over 2e6 pairs; 1.0008 at theta_2 = 1e-3, where the test cannot tell them apart).

T5 Entropy. Snapshots of T3/T4 (N = 1e6; the entropy gap is 0.045 per particle at
theta_2 = 1e-3 and 0.123 at theta_2 = 1, the estimator's standard error ~1.5e-3).
`entropy.s_estimate` (bins in s at theta_ref = theta_eq). Pass: s(0) equals
`entropy.s_mixture` within 4 standard errors; s(t_{k+1}) - s(t_k) > -4 sqrt(2) standard
errors for all snapshot pairs at least 0.25 tau_rel apart; s(end) equals
s_MJ(theta_eq) within 4 standard errors.

T6 Heat conduction between two reservoirs (step). `make_box.py step`, theta_1 = 0.02,
theta_2 = 0.01 (equal pressure), box L x L/8 x L/8, snapshots every 0.1 L/<|v|>.
(a) Long mean free path, lambda/L = 1000: slab sums (rest mass, energy, kinetic energy)
within the sampling noise of the collisionless exact curve (rms deviation below 1.5
noise units over t <= 5 L/<|v|>) and the initial slope within 5 percent of
-2 (Phi(1) - Phi(2)) (SPEC.md 7.1); at lambda/L = 100 the deviation from the
collisionless curve is larger than at 1000 and both are consistent with a deviation
proportional to t/t_coll [reported]. (b) Short mean free path, lambda/L = 0.01, cells
dx <= lambda/4: fit of `conduction.step_diffusive` with chi free to the slab rest mass
over t in [20 t_coll, 2/(chi k_1^2)]; pass: chi_fit/chi(kappa_1) in [0.95, 1.10].
(c) lambda/L in {10, 1, 0.1}: the transition, reported (no criterion). The collisionless
run of (a) with sigma = 0 is done: run C-sidm-20261115-121302-313d399.

T7 Conductivity from the isobaric mode. `make_box.py mode`, eps = 0.05, k lambda in
{0.4, 0.2, 0.1}, dx <= lambda/4, >= 20 particles per cell, theta in {0.003, 0.1, 1}.
Mode amplitude A(t) = sum M cos(k x) / sum M (number-density mode) and the same weighted
with W - 1; fit A = A0 exp(-Gamma_k t) over t in [10 t_coll, 2/Gamma_k]; kappa =
Gamma_k n c_p(theta)/k^2 (SPEC.md 7.3), extrapolated linearly in (k lambda)^2 to zero.
Pass at theta = 0.003: kappa/kappa_1 in [0.99, 1.06] (kappa_1 = 2.077 sqrt(theta)/sigma;
expected about 1.025 from higher Sonine terms [BACKGROUND]); a ratio below 0.80 would
support the Balberg et al. constant (ratio 0.72) and fail the test. theta = 0.1 and 1:
kappa measured with its uncertainty and reported as a result (no reference in the sources
read). Collisionless check at k lambda = 100: A(t) follows `mode_collisionless` within
noise.

T8 Convergence. T7 at theta = 0.003, k lambda = 0.2: dt in {0.2, 0.1, 0.05} t_coll,
`coll_pmax` in {0.2, 0.1, 0.05}, dx in {lambda/2, lambda/4, lambda/8}. Pass: kappa
changes by less than 2 percent between the two finest values of each parameter; trends
reported. T2(b) at max P = 0.5 with and without sub-cycling: with sub-cycling the rate
criterion holds; without, the deficit is reported.

T9 Unequal masses. `make_box.py unequal` (classes M and 4M, equal total mass,
theta_A = 3 theta_B), theta_B = 0.01, N = 1e6, `coll_weights = nanbu`, 8 seeds, run to
15 tau_rel. Pass: both classes at the same theta within 4 sigma at the end and both
Maxwell-Juttner (KS p > 1e-3); total energy and momentum drifts have zero mean over the
seeds within 4 standard errors; with `coll_weights = equal` the run stops at start-up
with an error naming the unequal masses.

T10 Reproducibility (RNG_REQUIREMENTS.md R4). `twotemp` box, 1e5 particles, 100 cycles,
seed 7: MeshBlocks 1, 8, 64; MPI ranks 1 and 4 (if the build has MPI); restart written
at cycle 37 and resumed. Pass: final snapshots (x, u, M, tag) bit-identical in all
variants (`analysis/an_box.py repro`). A different seed gives a different state.
T10b Processor and card: T2 and T4 statistics agree within 4 sigma (not bitwise).

T11 Lorentz covariance. `make_box.py boosted`, theta = 1, beta = 0.6 along x.
(a) collisions per lab step = (1/2) N Gamma(theta)/gamma_b dt within 4 sigma
(SPEC.md 2); (b) the drifting Maxwell-Juttner state is stationary: lab-frame
<W>, <u_x>, <u_x^2/W> unchanged within 4 sigma over 10 t_coll; (c) a drifting
two-temperature start (both populations with the same drift) relaxes to the drifting
Maxwell-Juttner gas at theta_eq of the rest frame. A code using |v_a - v_b| fails (a)
by a factor 1.48 (lab-frame pair average of |v_a - v_b| 0.931 against <v_Mol> 0.628 =
<v_Mol>_rest/gamma_b^2; same test file).

T12 Curved spacetime (G2, after T0-T11 pass). Needs a static, homogeneous non-flat
metric (constant lapse alpha0 and conformal factor psi0, beta = 0) as a problem-generator
option (request to core). Pass: collisions per coordinate step and coordinate volume
equal alpha0 psi0^6 times the flat value for the same proper density and temperature
(SPEC.md 5), within 4 sigma; conservation as in T1 for the covariant sum M u_i.

## 3. Order and cost

T0, T0b, T1, T2 first (processors, minutes). Then T3-T5 and T11 (1e6 particles, about
1e3 steps: processors with 16 cores or one card, below 0.5 card-hour in total), T6-T8
(the short-mean-free-path runs are the expensive ones: 1e6-1e7 particles for 1e3-1e4
collision times; card), T9, T10. This package was given no card time; the card runs
are pending, listed in README.md.
