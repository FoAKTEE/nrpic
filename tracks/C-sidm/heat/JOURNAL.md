# JOURNAL of the heat package (C-sidm, wave 3a): tests T6-T8 of collide/TESTS.md

Predictions are written here before the run they concern; outcomes after, failed ones
included. Times are UTC (the machine's clock shows PST; `date -u`).

## 2026-11-19 14:35 Set-up

Executable: core's branch core/collisions-2, `scratch/core/exe/core_collisions-2/athena_cpu`
(commit f46f159 in its COMMIT file; READY says: options absent = release core-v0.3 byte for
byte; `coll_energy = particle` conserves each pair's canonical energy with the metric at
the particle). Deck `inputs/heat.athinput` (flat Kerr-Schild functor, periodic box at
x0 = 10, `coll_energy = particle`). Particle files from `collide/analysis/make_box.py`
(the track's generator, wave 1). References: `collide/REFERENCES/` (wave 1) and
`scripts/isobaric.py` (this package, nonlinear isobaric conduction).

Cost basis from wave 2 (`../box_tests/README.md`, run C-20261115-165500-c67e036): one core,
5.7-6.7e-7 s per tested pair in one sub-step, 3.3-3.7e-7 s per tested pair sub-cycled,
3.0e-7 s per particle and step. Owner allotment at the start: 16 cores at a time, 8 busy
(`nrpic-run budget`, 14:30 UTC).

## 2026-11-19 14:40 Prediction S0 (smoke and cost)

Mode box theta = 0.003, k lambda = 0.2, 2e5 particles, 128 x 4 x 4 cells, dt = 0.1 t_coll,
60 steps, `coll_energy = particle` and `cell` side by side (`scripts/smoke.py`).
Predicted: both exit 0; n_trunc = 0, n_noroot = 0, n_balance = 0 (flat metric: the
canonical energy is W, the root exists, no detailed-balance rejection); about 0.5 tested
pairs per particle and sub-step and 2 to 4 sub-steps per step (P_bound/pmax with
v_bound/<v_Mol> ~ 2.5 and 0.1 t_coll per step gives P_bound ~ 0.25); cost
1.5-3e-6 s per particle and collision time (12-25 tested pairs per particle per t_coll at
3.5e-7 s each, plus the push); `particle` and `cell` give the same final momenta to
1e-12 (equal to rounding in a flat metric) and differ in cost by less than a factor 2.
Refuted by: a non-zero exit, truncated pairs, any root failure or balance rejection in a
flat box, a particle/cell difference above 1e-12, or a cost outside 0.5-10e-6 s.

## 2026-11-19 14:45 Outcome S0: function confirmed, cost prediction FAILED (7 times higher) (run C-20261119-143228-31ba665)

Both exit 0; n_trunc = n_noroot = n_balance = 0; 3.4 sub-steps per step on average (max 6),
1.73 tested pairs per particle and step; final momenta of `particle` and `cell` 1.7e-16
apart, positions 3.1e-13. Cost: 2.1e-6 s per particle and step (`particle`), 1.7e-6
(`cell`); 1.19e-6 s per tested pair, i.e. 2.1e-5 s per particle per collision time at
dt = 0.1 t_coll. The prediction of 1.5-3e-6 s per particle per t_coll FAILED by a factor
about 7: 17 tested pairs per particle per t_coll as predicted, but 1.2e-6 s per pair
instead of 3.5e-7 (machine load 100 on 144 cores at the time; about 100 particles per
cell instead of 30; `particle` 25 percent dearer than `cell`). Consequence: a 1 percent
measurement of kappa at eps = 0.05 needs ~2e7 particles per k lambda over ~500 t_coll,
i.e. ~60 core-hours: not on processors in this package. Design below.

## 2026-11-19 14:50 Design and predictions of T6-T8 (design run C-20261119-144117-37b2328)

Design run C-20261119-144117-37b2328 (`scripts/design.py`; copy
`results/design_C-20261119-144117-37b2328.json`; figure `figs/design_references.png`,
looked at: references of T6(a), T6(b) and the mode). Reference self-test (`isobaric.py`):
linear mode rate = kappa_1 k^2/(n c_p) to 1.2e-5, energy conserved to 1e-11 (mode) and
5e-8 (step), step grid change 3e-5 of the amplitude. One FAILED first try: BDF at rtol
1e-8 gave the linear rate 5e-4 high; at 1e-10 it is within the grid error.

Readings declared before the runs (TESTS.md is the lead's; no criterion is loosened, two
set-ups are changed for cost and the reason is given):
- D1 (T6b) transverse box lambda x lambda with 4 x 4 cells instead of L/8 x L/8: the step
  is one-dimensional, so transverse size and transverse cell size do not enter the
  conduction; L/8 at dx = lambda/4 would need 50 x 50 transverse cells and 2e7 particles.
  1.6e5 particles, 25 per cell, two seeds.
- D2 (T6b) the step has a temperature contrast of 2, so the gas is not in the linear
  regime: chi varies as T^{3/2} along the profile and the final temperature is 0.01333,
  not the mean 0.015. The nonlinear isobaric reference with kappa = kappa_1(T) scores
  0.967 on the literal statistic chi_fit/chi(kappa_1, theta = 0.015) (window
  [20 t_coll, 2/(chi k_1^2)] = [0.741, 50.88], t_coll = 0.0370), and 0.991 for
  kappa = 1.025 kappa_1. The literal interval [0.95, 1.10] therefore corresponds to
  kappa/kappa_1 in [0.982, 1.138]. I report both: the literal statistic, and f = the
  factor on kappa_1(T) of the nonlinear reference fitted to the code's slab rest mass over
  the same window, judged against [0.95, 1.10].
- D3 (T7) eps = 0.2 instead of 0.05 for the precise runs. Reason: the statistical error of
  the fitted rate is set by the equilibrium entropy-mode noise, var(A_S) = 5.0/N at
  theta = 0.003 (5.65/N at 0.1, 7.5/N at 1), against a signal eps c_p; a Monte Carlo of the
  least-squares fit with Ornstein-Uhlenbeck noise of rate Gamma (Onsager) at the snapshot
  times gives 4.9 percent per run of 1e6 particles at eps = 0.05 (k lambda = 0.1),
  8.6 percent at k lambda = 0.4. At eps = 0.2 the nonlinear reference shifts the fitted
  rate by -1.01 percent (theta = 0.003; -0.78, -0.79 percent at theta = 0.1, 1; -0.06
  percent at eps = 0.05), so kappa is divided by that factor (b = 0.9899 at 0.003). The
  fit uses the entropy combination A_S = (A_K - A_N)(<W> - 1)/theta - A_N (A_N number
  mode, A_K kinetic-energy-density mode; A_S(0) = eps c_p), which removes the sound modes
  of the number-density noise. A set at eps = 0.05 is run as the literal check.
- D4 (T8) eps = 0.2, theta = 0.003, k lambda = 0.2, one particle file for all seven
  variants, transverse box and cells fixed (16 x 16 cells of lambda/4), so only dt, pmax
  and the x cell size change; the eps bias is common to all variants and cancels in the
  differences.

Predictions (refuted as stated):
- P-T6a (lambda/L = 1000 and 100; N = 2e6; two seeds): at 1000, slab rest mass, energy and
  kinetic energy within the sampling noise of the exact collisionless curve: rms deviation
  below 1.5 noise units (noise from resampling, as `collide/analysis/an_step.py`); the
  fitted initial slopes of rest mass and energy within 5 percent of
  -2 (Phi(1) - Phi(2)) = +0.03153 (rest mass) and +0.03066 (energy) per unit time and
  area (kinetic: -0.00087, too small for a 5 percent test, reported). Slope estimator:
  quadratic fit over t <= 0.5 L/<|v|>_2, the same fit applied to the exact curve gives its
  bias, which is subtracted. At 100: deviation from the free streaming of the same sample
  grows with t; ratio of the deviations (100 against 1000) about 10, as t/t_coll; fraction
  of particles that have collided at t = 5 L/<|v|>_2 = 31.3: 0.9 percent (1000) and
  9 percent (100). Refuted by rms above 1.5 at 1000 in either seed, a slope off by more
  than 5 percent, or a 100/1000 deviation ratio outside 3-30.
- P-T6b (lambda/L = 0.01): f = 1.025 +- 0.03 (higher Sonine terms [BACKGROUND]; the
  relativistic correction at theta ~ 0.015 and the early Knudsen layer are not in the
  reference [JUDGEMENT]); literal statistic 0.967 f = 0.99 +- 0.03; statistical error of
  f about 1 percent per seed (4.7/sqrt(N)). Pass if f in [0.95, 1.10] for both seeds.
  The Balberg et al. constant would give f = 0.72: refuted far outside.
- P-T6c (10, 1, 0.1): the slab rest mass moves monotonically from the collisionless curve
  (10) to a diffusive one (0.1); reported.
- P-T7 (theta = 0.003, eps = 0.2, 4 seeds x 4e5, k lambda 0.4, 0.2, 0.1; window
  [10 t_coll, 2/Gamma_1]): expected seed-combined error of kappa(k lambda) 1.7, 1.1,
  1.0 percent; kappa(k lambda)/kappa_1 extrapolated linearly in (k lambda)^2 to zero:
  1.025 +- 0.02; pass if in [0.99, 1.06]; the Burnett-order change between k lambda = 0.1
  and 0.4 is reported (sign not predicted). Balberg et al. (0.72) refuted if > 0.80.
  theta = 0.1 and 1 (reported, no reference): kappa/kappa_1(theta) about 1.0 +- 0.1 at
  0.1 and 0.75 +- 0.25 at 1 [JUDGEMENT: mean-free-path estimate c_p <v> lambda with the
  relativistic c_p and the mean speed, which saturates at c].
  Collisionless check k lambda = 100: A_N(t)/A_N(0) follows `mode_collisionless(number)`
  within noise (|z| < 4 at every snapshot).
  eps = 0.05 literal set: consistent with the eps = 0.2 set within the combined error.
- P-T8: kappa changes by less than 2 percent between the two finest values of dt
  (0.1 -> 0.05 t_coll), pmax (0.1 -> 0.05) and dx (lambda/4 -> lambda/8) [BACKGROUND: DSMC
  transport errors are quadratic in dx/lambda and dt/t_coll with small coefficients;
  Alexander, Garcia & Alder 1998, Garcia & Wagner 2000 not in the corpus, not re-read];
  pmax has no effect beyond noise (pairs are redrawn each sub-step; the rate is exact).
  T2(b) at max P = 0.5 without sub-cycling (coll_nsub_max = 1): no deficit (sum_P per step
  equal to the analytic rate within 0.5 percent) as long as n_trunc = 0, because the
  acceptance of a pair is exact in expectation for P <= 1; refuted by a deficit above
  0.5 percent with n_trunc = 0.

## 2026-11-19 15:05 Runs started (processors) and card jobs queued

Processors (core_collisions-2 `athena_cpu`, `coll_energy = particle`):
- C-20261119-144535-2c7b6a4 T6(b), 2 seeds x 1.6e5, 16583 steps each (~85 min per seed).
- C-20261119-144545-c606492 T7 theta = 0.003, eps = 0.2, k lambda 0.4/0.2/0.1 x 4 seeds x 4e5.
- C-20261119-145733-558136e T6(a), lambda/L = 1000 and 100, 2 seeds x 2e6.
- C-20261119-150358-66295f7 T8 part 2 (T2(b) without sub-cycling), C-20261119-150358-3805fd5
  T7 collisionless check (k lambda = 100, theta 0.003, 0.1, 1).
Card (core_collisions-2 `athena_gpu`), particle files from prep run
C-20261119-145725-d91858e (`scripts/prep_card.sh`, lists `inputs/card_A.list`,
`inputs/card_B.list`): job A = run C-20261119-150335-73fd40f (Slurm 4652: T8 variants, T7 at
eps = 0.05), job B = run C-20261119-150347-e100007 (Slurm 4653: T7 at theta 0.1, 1 and a
4e6 seed at 0.003). 0.92 card-hours reserved each; about 19 jobs of the machine's users
were pending ahead of them at submission, so they may start hours later. Card cost assumed
1/100 of the processor cost (wave-2 ratio 96-173), i.e. ~19 min and ~26 min of card time.

## 2026-11-19 15:12 T8 part 2 (run C-20261119-150358-66295f7): first analysis wrong (my script)

The in-run analysis gave sum_P/expected = 0.99502 +- 0.00500 (nosub) and 0.99499 +- 0.00500
(sub), z_a = 1.12 and 0.38, n_trunc = 0 in both, max P 0.557 (nosub) and 0.107 (sub,
3.42 sub-steps). The identical -0.5 percent in both runs and a step-to-step scatter of 7
percent are not the operator: tlim = 200 dt (1 + 1e-9) makes the code take a 201st step of
6e-9, whose sum_P (0.013) entered the mean with the full-step expectation (1/200 of the
records = -0.5 percent). Corrected (`t2nosub.py analyse`: expectation with each record's
own step, records shorter than dt/2 excluded) and re-analysed in a separate registered run
from the same output; the simulations are not rerun. The same sliver step ends every run
of this package (harmless for the snapshots: it adds one record of ~1e-9 dt).

## 2026-11-19 15:16 Outcome T8 part 2: confirmed, no deficit without sub-cycling (analysis run C-20261119-151044-a584069)

Maxwell-Juttner box, theta_gas = 0.09985, 1e6 particles, sigma = 6.877 (max P = 0.557 with
one sub-step), 200 steps. sum_P per step / (1/2) N rho0 sigma <v_Mol>(theta_gas) dt:
without sub-cycling 1.000025 +- 0.000041 (z = +0.62), accepted collisions against sum_P
z = +1.18, n_trunc = 0; with sub-cycling (3.43 sub-steps, max P 0.107) 0.999992 +- 0.000026
(z = -0.32), z_a = +0.42. Both pass T2(a, b). The prediction (no deficit as long as no pair
exceeds P = 1) held: TESTS.md T8's "the deficit is reported" has nothing to report; what
sub-cycling buys is not the rate but the time resolution of successive collisions (T8
part 1). Figure `figs/T8_t2_nosub.png` (looked at: both ratios scatter by 3-5e-4 per step
around 1, no trend over 200 steps).

## 2026-11-19 15:29 Outcome T7 collisionless check: confirmed (runs C-20261119-150358-3805fd5, analysis C-20261119-152845-017d186)

k lambda = 100, 4e5 particles, eps = 0.05, theta 0.003, 0.1, 1 (to 6/(k sqrt(theta)) or 6/k).
Against `mode_collisionless` (ensemble): max |z| = 3.03, 3.08, 2.89 (< 4: pass as written),
rms z 1.80, 1.89, 2.01. The rms looked systematic in the first analysis (C-20261119-152743-
2367d74, superseded): the code lies below the ensemble curve by 1-2 noise units at all
three temperatures. Checked before naming a cause: the free streaming of the same sample
(deterministic) lies there too (rms z sample vs ensemble 1.80, 1.80, 2.05: make_box draws
the positions of all three from seed 1 with the same box, so the three runs share one
noise realization), and the code follows it to rms 0.27, 0.14, 0.05 noise units (max 0.90,
0.27, 0.09); the remainder grows with the fraction of particles that collided by the end
(12.5, 11.1, 5.7 percent), as collisions slow the phase mixing. Figure
`figs/T7_collisionless.png` (looked at; the legend covers the first points of the left
panel).

## 2026-11-19 15:31 Outcome T6(a): passed; the 100/1000 deviation ratio prediction FAILED in its mechanism (runs C-20261119-145733-558136e, analysis C-20261119-152744-2bba6de)

2e6 particles per run, box 1 x 1/8 x 1/8, 500 steps to 5 L/<|v|>_2 = 31.3.
- lambda/L = 1000: rms deviation from the exact collisionless curve (noise units of 64
  resamplings): seed 1 1.20, 1.20, 1.11 (rest mass, energy, kinetic), seed 2 0.86, 0.87,
  1.04; max 2.7. Pass (< 1.5) in both seeds. Initial slopes (quadratic fit over
  t <= 0.5 L/<|v|>_2, fit bias on the exact curve removed) over -2 (Phi(1) - Phi(2)):
  rest mass 1.0010 and 0.9783, energy 1.0011 and 0.9770 (estimator sd 1.2 and 1.3 percent:
  seed 2 is -1.8 sd); pass (within 5 percent). Kinetic slope 0.9994 and 1.0232 (sd 1.7
  percent; reported).
- lambda/L = 100: rms 1.18, 1.18, 1.07 and 0.91, 0.91, 1.07 against the collisionless curve.
- Fraction of particles that collided by t = 31.3: 0.80 and 0.79 percent (1000), 7.61 and
  7.62 percent (100) (predicted 0.9 and 9: my t/t_coll used <v_Mol> at the mean
  temperature instead of the slab rates; the ratio 9.5 is as predicted).
- Deviation from the free streaming of the same sample (the effect of the collisions):
  rms 2.7e-5 and 3.3e-5 (1000), 8.9e-5 and 1.0e-4 (100) in slab rest mass per area, i.e.
  0.08-0.09 and 0.25-0.28 noise units. Ratio 100/1000: 3.3 and 3.1, inside the stated
  band 3-30 but not the predicted 10 (t/t_coll). The ratio is sqrt(9.5) = 3.1: the
  deviation is the random scatter of the collided particles (each collision redirects a
  particle; their net effect on a slab sum adds like a random walk), not a systematic
  drift proportional to the number of collisions; a systematic part is below this scatter
  at both mean free paths and two seeds cannot show it. So "consistent with a deviation
  proportional to t/t_coll" (TESTS.md T6a) is not what the runs show; the reported finding
  is "consistent with stochastic scatter of the collided fraction".
Figure `figs/T6a_step_long.png` (looked at: code, sample free streaming and exact curve
overlap in all three sums at both mean free paths; the kinetic energy of the left slab
dips by 10 percent at t ~ 0.3 L/<|v|>_2 as fast hot particles leave first, then overshoots).

## 2026-11-19 15:41 Prediction T8 coarse (processors, while card job A waits in the queue)

The seven T8 variants of card job A at 5e5 particles instead of 4e6 (transverse 8 x 8
cells of lambda/4, same eps = 0.2, theta = 0.003, k lambda = 0.2, one particle file):
expected sd of f per variant ~1.9 percent (design Monte Carlo scaled to 5e5), of a
difference ~2.7 percent. So this set can only refute a dependence larger than about 5
percent between neighbouring values; P-T8 (changes below 2 percent between the two finest
values) is judged on card job A. Predicted here: no change above 5 percent between any two
neighbouring values of dt, pmax or dx; refuted otherwise.

## 2026-11-19 15:44 Outcome T6(c): transition reported; the "diffusive at 0.1" part of P-T6c FAILED (runs C-20261119-151104-b930d71, C-20261119-145733-558136e; analysis C-20261119-154057-471b5ec)

Left-slab rest mass per area (seed 1; 1e6 particles at lambda/L = 10, 1, 0.1 and 2e6 at
1000, 100) at t = 0.5 L/<|v|>_2: 0.4642, 0.4641, 0.4634, 0.4605, 0.4330 for lambda/L =
1000, 100, 10, 1, 0.1; at 1.3 L/<|v|>_2: 0.5005, 0.5005, 0.4999, 0.4996, 0.4852; at the end
(5 L/<|v|>_2) all within 8e-4 of 0.5. Fraction of particles collided by the end: 0.008,
0.076, 0.54, 0.999, 1.000. The ordering in lambda is monotone, as predicted, but down to
lambda/L = 1 the curve stays on the collisionless one (the step mixes in about one
crossing time, before most particles collide), and at lambda/L = 0.1 the mass rises more
slowly and then oscillates with a period of about 1.1 L/<|v|>_2, close to the sound
crossing L/c_s = 1.07 L/<|v|>_2 at theta = 0.0133 [JUDGEMENT: the kinetic transient at
the interfaces launches sound waves]. That is not the diffusive curve I predicted for 0.1:
there the diffusion time 1/(chi_1 k_1^2) = 0.42 L/<|v|>_2 is shorter than a crossing, so
neither limit applies. Figure `figs/T6c_transition.png` (looked at).
