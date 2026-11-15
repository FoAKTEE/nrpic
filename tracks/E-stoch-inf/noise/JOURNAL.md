# Journal of the package noise (E-pre-4 under decision 0010)

Owner: E-stoch-inf (helper for E-pre-4: coloured noise, random-number requirements).
Entries are appended; nothing is rewritten. Labels as in the brief: [VERIFIED],
[BACKGROUND], [JUDGEMENT], [TO VERIFY]. Run ids: `tracks/E-stoch-inf/runs/<run_id>/`.

## 2026-11-15 12:45 UTC: state found, sources read

- `core/scalar-field` has no commit beyond `main` (tip a9fec22, the merge base); the
  generator does not exist yet, so the validation cannot run on code output in this
  session. `core/rng` (tip 8e0eeb1) has the counter-based interface: proposal
  `tracks/core/interfaces/rng.md`, header `athenak/src/utils/rng.hpp`, twin
  `python/nrpic/rng.py`.
- Noise of the target scheme, read in `kb-data/raw/arxiv/2512.14649/v2/src/PRD_v2.tex`:
  sources `F^{-1}{S_k(t) alpha_k}` with `S_R = R_k Wddot + [2 Rdot_k + (3 - eps2) H R_k]
  Wdot` (lines 302-310); the alphas are drawn once and the real-space field R(t,x) is
  evolved (line 312); per RK4 step: Fourier transform, integral of S over the step,
  inverse transform, added to every right-hand side (lines 489-495); window
  `W = (1 + tanh[s ln(k_sigma/k)])/2`, s = 5 (lines 503-506), "non-Markovian noise when
  such a non-sharp window function is used" (line 507); N = 256, sigma = 1 (line 519),
  L k_sigma* = 2 pi, k_max = N k_sigma*/4 (lines 510-512); step count formula (line 721);
  convergence runs N = 32 to 256 with k_max/dk = 8 (line 756); all BSSN sources
  proportional to the same S_R (lines 668-677).
- Alphas: one complex Gaussian per mode of a hemisphere, alpha_{-k} = alpha_k^*
  (2512.14649 lines 121-128; 2502.06783 lines 852-856; thesis 2610.32592 appendix.tex
  lines 463-467). Printed prefactor `(dk/sqrt(2 pi))^{3/2} IRFFTN{f_k s_k}`
  (2502.06783 line 881). Courant factor 0.025 (2502.06783 line 492; thesis
  chap_ICsim.tex line 141); not stated in 2512.14649 [TO VERIFY].
- AthenaK facts relevant to the generator: no FFT in `athenak/src` (grep for "fft"
  empty); the turbulence driver sums modes directly with separable cos/sin factors
  (`athenak/src/srcterms/turb_driver.cpp` lines 236-270); the `bin` output writes
  variables as `float` (`athenak/src/outputs/binary.cpp` line 96), while the reader
  `athenak/vis/python/bin_convert.py` accepts 4- or 8-byte variables (lines 149-152).
- Repository Fourier convention: `cosmo/ic/random_field.py` lines 7-16
  (`delta_k = (1/N) sum_x delta(x) exp(-i k.x)`, x the cell centres,
  `<|delta_k|^2> = P/L^3`). The noise specification adopts it.

## 2026-11-15 12:50 UTC: predictions before the tests of this package

T-N0, independent re-implementation of the normal draw from the written interface
(`rng.md` sections 2-3) with `numpy.random.Philox` and the library logarithm, compared
with core's twin `python/nrpic/rng.py` (from `git show core/rng:...`) on all modes of the
N = 64, n_max = 16 test lattice and 2000 random keys. Prediction: raw words identical;
normal deviates equal to within 1e-13 absolute (the twin's logarithm error is below
1e-13, rng.md section 3). Refuted if any word differs or a deviate differs by more than
1e-12; then either the document or the twin is incomplete, and RNG_REQUIREMENTS records it.

T-N1, mode and draw counts at the resolutions of the specification (count_draws.py).
Prediction: hemisphere modes with 0 < |n| <= 64 about (2/3) pi 64^3 = 5.49e5 (within
1 percent); with |n| <= 8 about (2/3) pi 512 = 1072 (within 10 percent); steps for the
quadratic case at N = 256, sigma = 1, theta = 0.025 and 8 e-folds about
256/(2 pi 0.025) 8 = 1.3e4. Refuted if the counts differ by more than the stated
margins (then the formula or my reading of the lattice is wrong).

T-N2, the reference against itself (Monte Carlo of noise_ref over 200 seeds, N = 32):
the analytic expectations and variances of the estimators (shell power ratio, correlation
function, cross-correlation between steps and components) agree with the ensemble: means
within 4 standard errors, standard deviations within 20 percent. Refuted otherwise (then
an analytic variance formula in the reference is wrong and the pass criteria built on it
are miscalibrated).

T-N3, positive controls: fields made by the reference (frozen and Markovian schemes,
hemisphere amplitudes, tanh and Heaviside windows, 20 seeds) pass every acceptance test.
With about 30 statistical decisions per validation at a per-decision false-alarm level of
1e-4, expected false alarms in 20 validations: 0.06. Refuted if more than one validation
fails.

T-N4, negative controls (mutants): each mutant fails the test written for it:
(a) normalisation of the papers' printed prefactor, power x (2 pi)^{3/2}: A2 (and A1);
(b) white amplitudes (no colouring): A2; (c) positions at j h instead of (j + 1/2) h:
A1 only (all statistical tests pass); (d) fresh alphas each step in the frozen scheme:
A8, A9; (e) frozen alphas in the Markovian scheme: A8; (f) components of one degree of
freedom keyed independently: A6; (g) x and z axes swapped: A1 and A2-mu of the
direction-dependent component; (h) keys built from the MeshBlock-local index: A11;
(i) amplitudes of fixed modulus (phases random): A3 while A2 passes; (j) modes beyond the
cut included: A10; (k) the "pair" amplitude scheme where "hemisphere" is declared: A6
(phase of the cross-correlation); (l) a counter kept in memory across a restart: A12.
Refuted if any mutant passes all tests.

T-N5, the reader on real AthenaK output: z4c_linear_wave on the processor executable,
32^3 mesh on the unit cube, wave vector (1, 2, 3), amplitude 0.1, written at cycle 0 with
the `bin` output for 1, 8 and 64 MeshBlocks. Prediction: the assembled `z4c_gzz` arrays
are bit-identical for the three divisions and equal to `1 + azz amp sin(2 pi k.x)` at the
cell centres within float rounding (4e-7 absolute); with the axes transposed the error
is of order amp. Refuted if the divisions differ or the error exceeds 1e-6.

## 2026-11-15 12:58 UTC: amendment to T-N0 before it ran

The prediction "deviates within 1e-13" is wrong for a re-implementation with the library
logarithm: rng.md section 3 states that the documented logarithm (AGM) has absolute error
up to 3e-14 in L = -ln(s 2^-52), and the deviate z ~ sqrt(2L) then moves by about
dL / sqrt(2L), i.e. 1e-12 at L = 1e-3 (probability 1e-3 per draw) and more below.
Amended prediction, written before the run: (i) re-implementation of the documented AGM
logarithm (ten steps, pi/2 over the mean minus 32 ln 2, clamped at zero): deviates
bit-identical to the twin; (ii) library logarithm: max deviation below 1e-9 over the test
keys, median below 1e-15. The reference uses (i) for the exact-reconstruction test A1.
Refuted if (i) is not bit-identical.

## 2026-11-15 12:53 UTC: outcome T-N0 (run E-stoch-inf-20261115-125255-fcdcbdc)

Twin taken from `core/rng` at 8e05112 (the branch moved from 8e0eeb1 since the start of
this session; sha256 of the extracted file in the manifest).
- Raw words: 0 of 153684 lattice keys x 2 blocks and 0 of 2000 random keys differ.
  [VERIFIED] rng.md sections 2-3 define the words completely; numpy.random.Philox
  reproduces them.
- Normal pairs with the documented AGM logarithm: bit-identical for all 307368 lattice
  deviates and all 4000 random-key deviates. Prediction (i) holds: the document is
  complete enough to re-implement the normal draw bit for bit.
- Library logarithm: max |dz| = 1.16e-12, median 1.11e-15, 96 percent differ in some
  bit. Prediction (ii) holds for the maximum (below 1e-9) and fails narrowly for the
  median (1.11e-15 against "below 1e-15"): a few ulp of O(1) numbers, as one should
  have expected for a different logarithm. The deviations lie under 3e-14/sqrt(2L)
  (figure fig_check_twin.png of the run), as derived in the amendment.
- Consequence: the reference uses the AGM path; A1 can then demand agreement to
  rounding of the synthesis, not to the logarithm.

## 2026-11-15 12:57 UTC: outcome T-N1 (runs E-stoch-inf-20261115-125434-742a681, E-stoch-inf-20261115-125603-39cb4dd)

The first run used a z-major half space and a full-cube cost estimate, and its figure had
a legend over the data; the second run uses the half space of E-pre-2
(`codebase/ref/synth.py:half_space`, n_x first) and its refined cost formula. Mode counts
do not depend on the choice of half space (both runs: same numbers).
- N = 256, n_max = 64: 548958 half-space modes (estimate (2/3) pi 64^3 = 549033, 0.014
  percent). N = 32 to 256 with n_max = 8: 1054 modes (estimate 1072, 1.7 percent).
  Prediction holds.
- Steps at theta = 0.025, sigma = 1: 13038 (8 e-folds), 16298 (10 e-folds); predicted
  1.3e4. Holds. [TO VERIFY: theta of 2512.14649 is not stated there.]
- Normal pairs per step: Heaviside window with fresh draws at most 1485 (last e-fold
  of crossing), mean 81 while modes cross; tanh window (s = 5): every mode has
  Delta W >= 1e-16 in some step and up to all 548958 in one step, so a stateless frozen
  generator recomputes all alphas every step: 7.3e-5 s on one card, 3.7e-2 s on one core
  per set (rng.md costs). Draw cost is negligible against the synthesis.
- Synthesis cost per field and evaluation (half space, formula of E-pre-2 recomputed):
  2.50e9 complex multiply-adds with 128^3 MeshBlocks, 5.02e9 with 64^3, 1.35e10 with
  32^3; an FFT of 256^3 about 2.5e8. Agrees with E-pre-2 (codebase/README.md D2: 2.5e9
  and 5.0e9).

## 2026-11-15 13:20 UTC: additions to T-N2 to T-N4 before they ran

Written after NOISE_SPEC.md section 10 (criteria) and before the first run of
validate/selftest.py. Since the morning entry the unit-test transfer changed to the form
of SPEC 2.4 and DR section 5: in the frozen scheme the code writes the source rate at the
output time and integrates it (stoch_acc0) with its Runge-Kutta driver; the self-test
emulates the driver by classical RK4 at the stage times.
- (c) refined: positions at j h fail A1 and also A9 (A9 is an exact real-space comparison
  too); every statistical test passes.
- (m) frozen acc0 integrated with the rate at the step start (no stage times): fails A9
  only (error O(s hubble dt) = 5e-2 against the 1e-6 criterion).
- (n) a code that ignores the seed (U8 generated with the seed of U2): fails A15.
- (o) phases taken at the cell indices instead of the centres, at N = 32 and 64: fails A13.
- A9 positive control: classical RK4 reproduces the telescoped window to below 1e-6 of
  the rms (estimate 2e-8). Refuted if A9 fails on correct output.
- T-N2 also checks the A4 statistic at five lags and the A15 statistic between seeds.

## 2026-11-15 13:30 UTC: development run of the self-test; criterion amended before the registered run

A quick, unregistered run of selftest.py (40 seeds for T-N2, few seeds for T-N3; output in
scratch/E-stoch-inf/tmp/smoke) found one failure on correct output: Markov/Heaviside,
cycle 101, A4 with min p x lags = 4.8e-5. In that step only the 12 half-space modes with
n.n = 6 cross the window, and the lag statistic, a sum of 12 weighted exponentials, is far
from normal, so its normal-approximation p-value is too small. This is a miscalibration of
the criterion, not of the code. Amendment (NOISE_SPEC.md section 10, before the registered
run): the normal-approximation tests (A4, A6 pair, A7, A8 Markov, A15) apply only with at
least 100 effective modes, the fourth-moment z of A3 only with at least 1000 modes. The
same run showed all 15 mutants caught; some fail more tests than predicted (for example
the normalisation mutant also fails A3, A4, A7 and A9, whose statistics are normalised by
the reference G). A1 divided by zero for an all-zero reference field (Heaviside step
without crossing); fixed.

## 2026-11-15 13:12 UTC: outcome T-N5 (run E-stoch-inf-20261115-131126-8eb199a)

Processor release build of main (`.work/build_cpu_c1/src/athena`, sha256 in the manifest),
z4c_linear_wave at cycle 0 with 1, 8 and 64 MeshBlocks. The assembled z4c_gzz and z4c_gxy
are bit-identical for the three divisions; max |gzz - formula| = 5.4e-8 and
|gxy - formula| = 1.8e-9 (float rounding; predicted below 4e-7); with x and z exchanged
the error is 7.0e-2. The file header says "size of variable=4": AthenaK `bin` output is
single precision [VERIFIED], so request C1 (double precision) stands. Prediction holds.
Figure fig_reader_test.png of the run: the difference is the float quantisation pattern.

## 2026-11-15 13:35 UTC: outcomes T-N2, T-N3, T-N4 (run E-stoch-inf-20261115-131031-ec74943)

- T-N2 holds. 200 seeds, N = 32, nmax2 = 64: the ten statistics (A2 pooled z, A3 z4, A7
  Re and Im, A15 Re, A4 at five lags) have means between -0.131 and 0.087 (all within
  1.9 standard errors) and standard deviations between 0.937 and 1.068 (within 7 percent
  of 1). The 1600 exact Gamma p-values of the shells are uniform (KS p = 0.88; 0.69
  percent below 0.01). The analytic variances of the reference are right.
- T-N3 refuted. 38 validations of correct output (20 frozen/tanh, 5 Markov/tanh, 5
  Markov/Heaviside, 5 pair, 3 single precision) and the five comparisons: two failures,
  both A3 (Kolmogorov-Smirnov of |w|^2 against Exp(1)) in the frozen/tanh series: seed
  20379900 with p = 7.4e-6 (c0, c1, c3 at cycles 100 and 101, which share the same
  257 amplitudes) and seed 20387819 with p = 6.9e-5 (c3 at cycle 300). Predicted: at most
  one failing validation. Every other test passed in all 38.
- T-N4 holds. All 15 mutants fail the tests written for them; most fail more (the
  normalisation and white mutants also A3, A4, A7, A9; the axis exchange also A10 and A6,
  because G of c3 vanishes exactly at n_z^2 = n^2/3 and the exchanged field does not; the
  MeshBlock-keyed mutant fails nine tests). The statistical-only mutants are caught by
  their statistical tests: fixed modulus by A3, ignored seed by A15.
- A diagnostic (unregistered, 2000 seeds) showed the single KS p-values calibrated
  (fractions below 1e-2 and 1e-3: 0.007-0.013 and 0-0.0015 for six selections; 1.7e6
  pooled |alpha|^2: KS p = 0.88, tail beyond 10 at 4.51e-5 against e^-10 = 4.54e-5). No
  cause is named yet; T-N6 measures the family-wise rate of A3.

Prediction T-N6 (validate/calib_a3.py, 2000 seeds, the A3 decisions of the base case):
single decisions calibrated (fraction below 1e-3 within three binomial standard
deviations of 1e-3); the family-wise rate of A3 per validation at the per-decision level
1e-4 between 1e-3 and 1e-2 (40 correlated decisions). If so, two failures in 20 base
validations had a probability of the order of 1e-3 to 1e-2, i.e. bad luck but not
impossible; the remedy is to control the family-wise rate per validation (Bonferroni
over the counted decisions). Refuted if single decisions are miscalibrated (then the
draws or the selection are at fault) or the family rate exceeds 2e-2.

## 2026-11-15 13:45 UTC: outcome T-N6 (runs E-stoch-inf-20261115-131526-629fed8 failed, E-stoch-inf-20261115-131551-629fed8)

The first run stopped on a syntax error in the script (keyword names with "1e-4"); the
second ran. 2000 seeds (700000 + 7919 s), 40 A3 decisions per validation.
- Family-wise rate of A3 at the per-decision level 1e-4: 0.0025 +- 0.0011 (5 of 2000).
  Prediction [1e-3, 1e-2] holds. At the level 1e-3/40: 0.0005.
- Single decisions: fractions below 1e-2, 1e-3, 1e-4 = 0.01065, 0.00141, 0.000113.
  The prediction "within three binomial standard deviations" fails at 1e-3: 3.7 naive
  standard deviations (113 against 80 +- 9 of 80000). The naive count ignores that c1
  repeats c0 exactly and that cycles 100 and 101 select nearly the same 257 modes, which
  inflates the variance of the count; the fractions at 1e-2 (1.9 sd) and 1e-4 (9 against
  8) agree. Not settled by this run; T-N7 counts distinct decisions only.
- With a rate of 0.0025 per validation, two A3 failures in the 20 base validations of
  T-N3 have a probability of about 1e-3, and they came from consecutive seeds of the
  self-test's sequence (i = 15, 16 of 20261115 + 7919 i). A structure in the generator
  across seeds would matter for core, so T-N7 tests that sequence.

Prediction T-N7 (calib_a3.py --seed0 20261115 --stride 7919, 2000 seeds: the self-test's
sequence): seeds i = 15 and 16 reproduce p = 7.4e-6 and 6.9e-5; the family-wise rate is
consistent with T-N6 (below 0.0025 + 3 x 0.0011 = 0.006); for the distinct decisions the
fraction below 1e-3 lies within three binomial standard deviations of 1e-3. Refuted if
the rate exceeds 0.006 (then the generator has structure across seeds of this sequence)
or the distinct decisions are miscalibrated.

Amendment of the decision rule (before the rerun of the self-test): each validation
counts its D statistical decisions in a first pass and decides each at the level 1e-3/D
(Bonferroni; family-wise false alarm at most 1e-3 per validation). Also fixed: rec()
returned numpy booleans for A5, which the pass/fail bookkeeping read as "not applicable";
the A5 verdicts of run E-stoch-inf-20261115-131031-ec74943 were therefore not counted
(its values, |mean|/rms of order 1e-17, would have passed).

## 2026-11-15 13:50 UTC: prediction for the rerun of the self-test with the amended rule

D counted in a development pass (unregistered): 93 (frozen/tanh), 110 (Markov/tanh), 28
(Markov/Heaviside), 97 (pair); level 1e-3/D = 1.08e-5 for the base case. Same seeds as
before. Prediction T-N3b: exactly one failing validation, the base case with seed
20379900 (A3, p = 7.4e-6 < 1.08e-5, already known); seed 20387819 now passes (6.9e-5);
all other validations and comparisons pass; every result of T-N2 unchanged. Prediction
T-N4b: all 15 mutants still fail the tests written for them (their statistical failures
have p many orders below 1e-5). The A5 verdicts are now counted (all pass). Refuted if a
second validation fails or a mutant escapes.

## 2026-11-15 13:55 UTC: outcome T-N7 (run E-stoch-inf-20261115-131820-629fed8)

Self-test sequence 20261115 + 7919 i, 2000 seeds. Seeds i = 15 and 16 reproduce
p = 7.4e-6 and 6.9e-5 from the amplitudes alone. Family-wise rate at 1e-4: 0.002 +- 0.001
(hits at i = 15, 16, 323, 1781), consistent with T-N6 (0.0025); at 1e-3/40: 0.0005.
Distinct decisions (c1 left out, 60000): fractions below 1e-2, 1e-3, 1e-4 = 0.0096,
0.00085 (1.2 sd below 1e-3), 0.00012. Prediction holds: no structure of the generator
across this seed sequence, single decisions calibrated. Conclusion, now with a run in
which it could have failed: the two failures of T-N3 are chance (two of the four
2000-seed hits fell among the first 20 seeds) on top of a decision rule whose
family-wise rate per validation was about 2.5e-3 for A3 alone and larger in total,
not 3e-3 for the whole validation as section 10 had estimated. The amended rule (level
1e-3/D) addresses the second part.

## 2026-11-15 14:05 UTC: outcomes T-N3b, T-N4b (run E-stoch-inf-20261115-132950-16a0168)

Same seeds, family-wise level 1e-3/D, A5 counted.
- T-N3b holds as predicted: one failing validation of 38, the base case with seed
  20379900 (A3, KS p = 7.4e-6 against the level 1.08e-5, D = 93); seed 20387819 passes;
  all other validations and the comparisons A11-A15 pass; A5 passes everywhere. Under the
  reading rule of NOISE_SPEC section 10 this validation would be repeated on the second
  seed. T-N2 numbers identical to the first run (the calibration does not use the rule).
- T-N4b holds: all 15 mutants fail the tests written for them; the MeshBlock-keyed mutant
  now also fails A5 (seams give a nonzero mean), which the first run did not count.
- Figures looked at: fig_selftest_matrix, fig_selftest_calibration, fig_val_pos_frozen_*,
  fig_val_pos_markov_tanh_*, fig_val_neg_norm_2pi (the mutant's shell ratios sit at
  15.7 = (2 pi)^{3/2}), fig_calib_a3 (single decisions on the uniform line; the
  family-wise curve below D p). The Markov/Heaviside validation figure shows only the
  crossing shell of each step and two empty panels (A3, A4 not applicable below 100
  effective modes); the plotting now labels such panels, and the figure is not used.
  The A2 panels of this run draw the 1/sqrt(M) band only up to the shells of the first
  output; fixed in the code for later runs.

State at the end of the package: the generator does not exist on core/scalar-field (no
commit beyond main), so nothing written by the code has been validated. Every test above
is of the specification, the reference and the validation themselves.

## 2026-11-15 14:15 UTC: core's generator found; adapter to its output; prediction T-N8

`core/scalar-field` now has the generator (ba37619, 5384d02; "builds on processors;
untested"): `athenak/src/scalar_field/scalar_field_noise.cpp` uses the keys of
ref/philox_ref.py (stream 2^16 + dof, CellEntity(n + 2^20), half space n_x first, epoch 0
frozen, ncycle + 1 Markov), L^-3/2 and separable synthesis per MeshBlock. Its model
`<scalar_field> noise = power` writes per step the increment amp q^((tilt-3)/2) L^-3/2
g(dW) alpha (g = dW frozen, sqrt(dW) Markov) as two fields xi_0 (dof 0) and xi_1 (dof
noise_pi_dof), into the double-precision dump `<basename>.sf.NNNNN.dump` (NRSFDMP1, layout
in `scalar_field_io.cpp` lines 12-17). Core's journal (tracks/core/JOURNAL-scalar.md, P4)
lists its own noise tests as predictions; no noise run exists. So no code output is
validated in this package; the run is named for the lead in README.md.
Differences from NOISE_SPEC section 9 that the validation must absorb: the frozen field
is the increment of the step, not the rate; dt comes from the CFL condition; the dump
holds no input parameters; there is no integrated field (A9) and no complex-phase or
direction-dependent component (A6 reduces to xi_1 = xi_0 for noise_pi_dof = 0; A1 still
catches an exchange of axes because a random field is not symmetric under it).
Adapter: athenak_io reads NRSFDMP1 dumps with the parameters from the run's input file;
noise_ref gains the frozen increment form, noise_t0 and noise_tilt.

Prediction T-N8 (validate/dump_selftest.py): reference fields of core's power model
(frozen and Markov, tanh, N = 64, nmax2 = 256, noise_pi_dof = 1 and 0), written as NRSFDMP1
dumps with 8 MeshBlocks in the documented layout, read back through the adapter, pass
every applicable test (A9 not applicable); 1 against 8 MeshBlocks bit-identical (A11);
a dump whose MeshBlocks are written with the wrong logical locations fails A1 and A11.
Refuted otherwise (then the reader or the parameter mapping is wrong).

## 2026-11-15 14:40 UTC: outcome T-N8 (run E-stoch-inf-20261115-133731-2031735)

Prediction holds. Reference fields of core's power model written as NRSFDMP1 dumps (the
documented layout) with an input file, read back through athenak_io.read_run(dir, input):
the parameters map back exactly (seed, scheme, nmax2, N = 64, L = 2.5, x0 = -1.25,
dt = 0.01 from time/cycle, noise_t0 = 0.2 and noise_tilt = -0.04 in the Markov case,
noise_pi_dof 1 and 0); frozen (8 and 1 MeshBlocks), Markov and shared-dof cases pass every
applicable test (A9 not applicable: no integrated field); 1 against 8 MeshBlocks
bit-identical; the mutant with exchanged MeshBlock locations fails A1 (6.1 rms) and A11,
and also A2, A3, A8, A10. Figure fig_dump_selftest.png: read minus reference is exactly
zero; the mutant differs in the two exchanged MeshBlocks only. This checks the adapter
against the documented layout, not against a file written by the code.

## 2026-11-15 14:45 UTC: end of the package

Deliverables exist and are tested: NOISE_SPEC.md, RNG_REQUIREMENTS.md, the reference,
the validation (bin and NRSFDMP1 readers) and its self-tests T-N0 to T-N8. Not done:
validation of code output (no noise run exists on core/scalar-field; named in README.md
for the lead). Refuted predictions on record: T-N0 (ii) median, T-N3, T-N6 single-decision
calibration as worded.
