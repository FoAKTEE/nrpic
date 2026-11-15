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
