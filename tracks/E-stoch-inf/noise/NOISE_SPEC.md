# Coloured Gaussian noise of the stochastic sources: specification for core

Status: PROPOSAL of E-stoch-inf (package noise, E-pre-4 under decision 0010), 2026-11-15.
The generator is code in `athenak/src/`, written by core with the scalar field (branch
`core/scalar-field`) on the random-number interface of `core/rng`
(`tracks/core/interfaces/rng.md` there, cited below as rng.md). This document, the reference
`ref/` and the validation `validate/` are the track's part. Labels as in the brief; run ids
refer to `tracks/E-stoch-inf/runs/<run_id>/manifest.json`.

Related documents of this track: the reproduction specification `spec/SPEC.md` (E-pre-1:
equations, mode functions, window, update rule; cited as SPEC) and the code-base review
`codebase/DESIGN_REVIEW.md` (E-pre-2: where the noise enters the code, the synthesis
without a Fourier library; cited as DR). Paper locators: P1 = arXiv:2512.14649 v2
`PRD_v2.tex`, P2 = arXiv:2502.06783 v3 `main_V2PRD.tex`, TH = arXiv:2610.32592 v1, all
under `kb-data/raw/arxiv/<id>/<v>/src/`.

## 1. What the generator does, and what it does not

It produces real Gaussian random fields on the periodic mesh whose Fourier coefficients
are `G^c_n(t) alpha_n`: a transfer function `G` supplied by the stochastic source times a
complex unit Gaussian amplitude `alpha_n` that is a pure function of a counter-based key
(seed, degree of freedom, wave vector, epoch). Because the amplitude belongs to the wave
vector and not to a cell, a MeshBlock, a rank or a step counter in memory, the field does
not depend on the division into MeshBlocks, on the order of evaluation or on where a run
was restarted, and the same seed gives the same realisation at every resolution.

Not part of the generator: the transfer functions themselves (mode functions R_k(t),
window W_k(t), BSSN prefactors: SPEC sections 2-3), the place where the noise enters the
right-hand sides (SPEC 2.4, DR section 5), the synthesis algorithm (DR 6.2: separable
partial sums per MeshBlock; any algorithm meeting section 10 is acceptable).

## 2. Fourier convention and normalisation

    box [x0, x0 + L)^3, N^3 cells, h = L/N, cell centres x_j = x0 + (j + 1/2) h, j = 0..N-1
    k_n = (2 pi / L) n,  n integer,  k_f = 2 pi / L
    mesh field     xi(x) = sum_n xi_n exp(i k_n . (x - x0))
    coefficients   xi_n  = N^-3 sum_j xi(x_j) exp(-i k_n . (x_j - x0))      (exact for |n_i| < N/2)
    continuum      xi(x) = int d^3k/(2 pi)^3 xit(k) exp(i k.x),
                   <xit(k) xit*(k')> = (2 pi)^3 delta_D(k - k') P(k)
    correspondence xi_n = xit(k_n) / L^3,   <|xi_n|^2> = P(|k_n|) / L^3
    variance       <xi^2> = sum_{n != 0} P(k_n) / L^3  ->  int d^3k/(2 pi)^3 P = int Delta(k) dk/k,
                   Delta(k) = k^3 P(k) / (2 pi^2)
    QFT amplitude  f(x) = int d^3k/(2 pi)^3 [f_k a_k e^{ik.x} + h.c.], [a_k, a_k'^+] = (2 pi)^3 delta_D
                   =>  P(k) = |f_k|^2,  and on the mesh  xi_n = L^{-3/2} f_k alpha_n

This is the convention of `cosmo/ic/random_field.py` (lines 7-16) and the QFT ("backward")
normalisation of SPEC section 1 (P2:835-849). The factor `L^{-3/2}` is the one E-pre-1
verified numerically (SPEC 5.4, run E-stoch-inf-20261115-122934-9ac98d8); the prefactors
printed in P2:879-882 and TH appendix give powers too large by (2 pi)^{3/2} or (2 pi)^3
(same run). The transfer `G^c_n = L^{-3/2} T^c(k_n, t)` therefore carries the factor
`L^{-3/2}`, and `T` is the continuum source amplitude of the papers (for example
`T^Pi = Mpl sqrt(2 eps1) S_R(k, t)`, P1:298-304). The generator adds no other factor.

Two choices that matter for reproducibility [JUDGEMENT]: phases are taken relative to the
lower corner x0, so that a shift of the coordinates does not change the realisation; and
relative to the cell centres, not the indices, so that the same mode has the same
coefficient on meshes of different N (with indices the coefficient would change by
exp(i pi n.(1,1,1)/N) between resolutions).

## 3. Mode set

    M = { n in H : 1 <= n.n <= nmax2 },   H = { n_x > 0 } u { n_x = 0, n_y > 0 } u { n_x = n_y = 0, n_z > 0 }

`nmax2` is an integer (the cut is on |n|, isotropic; SPEC U5 left this open, DR 6.2 chose
|n|). Every nonzero n lies in exactly one of H and -H. The half space H is that of DR
(`codebase/ref/synth.py:half_space`); the papers use the k_z > 0 half of RFFTN (TH
appendix:467). The choice changes the realisation, not its statistics. Required: 2 n_max < N,
so no mode lies on a Nyquist plane; the zero mode carries no noise (it is the background).
The cut of P1 is k_max = N k_min / 4 (P1:510-512), i.e. nmax2 = (N/4)^2.

## 4. Amplitudes and keys

    alpha_n = (z1 + i z2) / sqrt(2),   (z1, z2) = rng::Normal2(key, draw = 0),   n in M
    xi_{-n} = conj(xi_n)   (Hermitian completion)

| Word | Value | Note |
|---|---|---|
| key 0, seed | `<job> rng_seed` | rng.md rule 5: ensemble members differ only here |
| key 1, stream | `rng::Stream(kStreamStochastic, 0x10000 \| d)` | identifier 3 (rng.md section 6); bit 16 of the sub-stream marks mode entities; d = degree of freedom (below) |
| counter 0, entity | `(n_x + 2^20) \| (n_y + 2^20) << 21 \| (n_z + 2^20) << 42` | = `rng::CellEntity(n_x + 2^20, n_y + 2^20, n_z + 2^20)`; signed wave numbers, \|n_i\| < 2^20; independent of N |
| counter 1, entity_hi | 0 | |
| counter 2, step | epoch: 0 in the frozen scheme and for the initial slice; `ncycle + 1` of the step being taken in the Markov scheme | rng.md takes step = ncycle with 0 for initial data, so the first step and the initial data would collide; hence + 1 |
| counter 3, draw | 0 (one normal pair per mode) | draw 1 reserved for a second Gaussian per mode and step (higher-order stochastic schemes, P1:711) |

Degrees of freedom d (lower 16 bits of the sub-stream): 0 = the scalar curvature
perturbation R (inflaton): every scalar source (S_Pi, S_K, S_A_ij, all proportional to S_R,
P1:668-677) and the coarse-grained initial slice (P1:488, DR 6.3) use d = 0; 1 and 2 =
tensor polarisations (tensor sources of arXiv:2401.08530, not implemented in P1:678); 3 and
above = further fields. The unit test (section 9) uses d = 0 and d = 1.

The evolved variable is deliberately not part of the key. All sources of one degree of
freedom must use the same alpha_n: they are one Gaussian variable seen through different
transfer functions, and the constraints hold to first order only with that sharing (P1:541:
flipping the sign of one noise term gives H/[H] ~ 1e-5 and M/[M] ~ 1, first-order
violation). A key per evolved variable would make the sources independent and violate the
constraints at first order.

## 5. The field, its components and its time dependence

For component c of degree of freedom d(c), evaluated at time t (a Runge-Kutta stage time):

    xi^c(x, t) = sum_{n in M} 2 Re[ G^c_n(t) alpha^{d(c)}_n exp(i k_n . (x - x0)) ]          (5.1)

i.e. `xi^c_n = G^c_n alpha_n` on M, the conjugate on -M, zero elsewhere. G must be even in n
(a function of |k| and of k_i k_j), which every source of P1 is.

**Frozen scheme (default; the reproduction).** One set of amplitudes per run (epoch 0),
drawn "once at some fixed early time" (P1:312, SPEC 2.3); G^c_n(t) is the source rate at the
stage time (SPEC 2.4, DR section 5). The noise is then a smooth function of time for each
realisation, correlated between times through alpha ("non-Markovian", P1:507). For every
mode and every time, `xi^c_n(t) / G^c_n(t) = alpha_n`. A stateless generator recomputes
alpha at every evaluation; the cost is negligible (section 6).

**Markov scheme (option, for comparison with Langevin solvers, E-pre-3).** One increment per
step from cycle m to m + 1: `xi^c_n = G^c_n alpha^{(m+1)}_n` with epoch m + 1, where |G|^2 is
the variance added in the step (for example `L^-3 P(k) [W(t_{m+1}) - W(t_m)]`); applied once
per step, not per stage. Increments of different steps are independent. With a Heaviside
window both schemes give each mode one kick of the same law; with a smooth window they
differ (the Markov increment must scale as sqrt(dW) to have a limit dt -> 0).

**Amplitude variant "pair" (option).** Two independent amplitudes beta_n, beta_{-n} per pair
(n, -n), `xi_n = [G_n beta_n + conj(G_n) conj(beta_{-n})] / sqrt(2)`, as in
`cosmo/ic/random_field.py` (docstring line 72, code line 108). Each real field has the same law as in the
default ("hemisphere") variant. They differ only for two fields of one degree of freedom
whose transfers have a complex ratio: the hemisphere variant gives
`<xi^a_n conj(xi^b_n)> = G^a conj(G^b)` with the sign of the imaginary part flipped on -H
(an odd, sin(k.r), part of the real-space cross-correlation), the pair variant only
`Re[G^a conj(G^b)]`. The sources of P1 have real ratios (all proportional to S_R), so the
variant matters only between the initial slice's delta-phi and delta-Pi (R_k against
Rdot_k at k = sigma a H, sigma = 1). [JUDGEMENT; size TO VERIFY with the mode functions of
SPEC 5.3.] The reproduction uses the hemisphere variant (P1:121-128, P2:852-856).

## 6. Numbers at the resolutions of the specification

Run E-stoch-inf-20261115-125603-39cb4dd (`ref/count_draws.py`, `fig/fig_count_draws.png`);
draw cost from rng.md section 8 (0.133 ns per normal pair on one A100, 66.8 ns on one core).

| Configuration | N | nmax2 | modes in M | normal pairs per set | one set: card / core |
|---|---|---|---|---|---|
| P1 production (P1:510-512, 519) | 256 | 4096 | 548958 | 548958 | 7.3e-5 s / 3.7e-2 s |
| P1 convergence series (P1:756) | 32, 64, 128, 256 | 64 | 1054 | 1054 | negligible |
| unit test, base (section 9) | 64 | 256 | 8538 | 8538 | negligible |

- Steps for N = 256, sigma = 1, Courant factor theta = 0.025 (P2:492; P1 does not state it,
  SPEC U1 [TO VERIFY]), from N_T = N sigma (N_tot)/(2 pi theta) (P1:721): 13038 for 8
  e-folds (quadratic, P1:420), 16298 for 10 (inflection).
- Normal pairs per step. Frozen with stored amplitudes: 548958 once. Frozen and stateless
  (recomputed per evaluation): up to 548958 per stage, because with the tanh window every
  mode has dW >= 1e-16 for most of the run. Markov, Heaviside window: at most 1485 per
  step (last e-fold of crossing), 81 on average while modes cross. Markov, tanh window:
  up to 548958 per step, 5.75e9 over 8 e-folds, within the 1e11 keys of the statistical
  tests of rng.md section 7.
- Synthesis per real field and evaluation (formula of DR 6.2, recomputed in the run):
  2.50e9 complex multiply-adds with 128^3 MeshBlocks, 5.02e9 with 64^3, 1.35e10 with 32^3;
  an FFT of 256^3 about 2.5e8 (DR D2: 2.5e9 and 5.0e9). The draws are four orders of
  magnitude cheaper than the synthesis.

## 7. What must be reproducible

| Id | Requirement | How it is tested (section 10) |
|---|---|---|
| R1 | alpha_n is a pure function of (seed, d, n, epoch): the same bits on processors, on a card, in the twin `python/nrpic/rng.py` and in the independent `ref/philox_ref.py` | T-N0 (run E-stoch-inf-20261115-125255-fcdcbdc): philox_ref equals the twin bit for bit; A1 on code output |
| R2 | The field at a cell does not depend on the division into MeshBlocks or the number of ranks: bit-identical if every cell sums the same terms in the same order (DR D2 found this for the separable synthesis) | A11 |
| R3 | No generator state: the field at (x, t) depends only on the key and G(t), not on the order of evaluation | A1, A11 |
| R4 | A restarted run reproduces the noise bit for bit (same executable and division); the Markov epoch comes from the restored cycle number, never from a counter in memory | A12 |
| R5 | The amplitude of a mode does not depend on N or on the MeshBlock size: runs at N and 2N with the same seed, L and nmax2 share the realisation (so the convergence series of P1:756 compares like with like) | A13 |
| R6 | Ensemble members differ only in the seed, and different seeds give independent amplitudes | A15 |
| R7 | The initial slice and the noise share the amplitudes ("the same random lattice draw", P1:375): same stream, d = 0, epoch 0 | by construction of the keys; a test belongs to the scalar-field package |
| R8 | Processor and card agree to rounding (library sin and cos differ in the last bits), not bit for bit | A14 |

Not required: bit identity between two synthesis algorithms (partial sums, FFT); identity
with the realisations of the papers (their generator differs, SPEC 5.4).

## 8. Refinement, restart, initial slice

- Refinement: each level evaluates (5.1) at its own cell centres. The field is band-limited
  (|n| <= n_max), so all levels sample one continuous function; no prolongation, no
  cell-keyed noise (which rng.md rule 8 would make level-dependent) [JUDGEMENT, as DR 6.2
  item 3]. P1 runs without refinement (P1:483); G1 and G2 need a uniform mesh only.
- Restart: nothing to store beyond the seed (rng.md: stored with the parameters) and the
  cycle number.
- Initial slice: built by the same synthesis with the same alpha_n (DR 6.3), which is what
  R7 asks.

## 9. Unit test the code provides

A problem generator (name proposed: `stoch_noise_test`) that evolves no physics, takes a
fixed time step dt and writes the fields below. Transfer functions (reference:
`ref/noise_ref.py`, functions `transfer`, `acc_transfer`):

    q = |n|,  base_n = amp q^{-3/2} L^{-3/2}              (flat Delta: P proportional to k^-3)
    W_n(t) = (1/2){1 + tanh[s ln(ksigma0 e^{hubble t} / q)]}    or Heaviside(ksigma0 e^{hubble t} - q)
    frozen:  G^0_n(t_m) = base_n dW_n/dt (t_m)                  (rate at the output time t_m = t0 + m dt)
    markov:  G^0_n(t_m) = base_n sqrt(W_n(t_m) - W_n(t_m - dt)) (increment of the step ending at t_m; epoch m)
    G^1 = G^0 exp(i phase1)  (d = 0)     G^2 = G^0  (d = 1)     G^3 = G^0 (n_z^2/n^2 - 1/3)  (d = 0)
    stoch_acc0: a field a with da/dt = xi^0 integrated by the code's Runge-Kutta driver at the
      stage times (frozen), a(0) = 0; expected coefficients base_n [W_n(t) - W_n(t0)] alpha_n.
      Markov: a = sum of the increments of xi^0 of all steps so far.

Parameters (base case): `<job> rng_seed = 20261115`; mesh N = 64 on [-1.25, 1.25)^3
(L = 2.5, so L^{-3/2} = 0.253 is tested); nmax2 = 256; window tanh, s = 5; ksigma0 = 0.9;
hubble = 1; amp = 1; phase1 = pi/3; dt = 0.01, t0 = 0, 300 steps; output of `stoch_c0` to
`stoch_c3` and `stoch_acc0` at cycles 100, 101, 200 and 300, in double precision (section
11, request C1). k_sigma passes from 0.9 k_f to 18 k_f, so the outputs show modes before,
during and after crossing (W ranges from 0 to 1 at t = 1 and 2; from 0.77 to 1 at t = 3).

| Run | Variation from the base case | Feeds |
|---|---|---|
| U1 | base, 1 MeshBlock | A0-A10 |
| U2 | 8 MeshBlocks | A11 |
| U3 | 64 MeshBlocks | A11 |
| U4 | U2 restarted from its restart file at cycle 150 | A12 |
| U5a, U5b | nmax2 = 64, N = 32 and N = 64 (box and seed unchanged) | A13 |
| U6 | Markov scheme, tanh | A0-A10 |
| U7 | Markov scheme, Heaviside | A0-A10 |
| U8 | U2 with rng_seed = 20261116 | A15 |
| U9 | U2 on a card | A14 |

Each run takes seconds on one core. The track runs the validation; core runs U1-U9 or
hands the inputs to the lead.

## 10. Acceptance tests and pass criteria

Written before any code exists (this section is the contract; `validate/validate_noise.py`
implements it). Tolerances: real space `eps_x` and mode space `eps_m` relative to the rms of
the reference field or of its coefficients: eps_x = 1e-11 and eps_m = 1e-10 for double
precision output, eps_x = eps_m = 1e-5 for single precision. Statistical decisions are
two-sided. The validator counts the D statistical decisions of a validation (93 for the
base case U1, 110 for U6, 28 for U7) and decides each at the level p_D = 1e-3/D, with
|z| bound z_D (4.4 for D = 93): Bonferroni over the validation, family-wise false alarm at
most 1e-3; within one decision, Bonferroni over its shells or lags. (Amended after the
self-test, noise/JOURNAL.md 13:35-13:50: a fixed level 1e-4 per decision gave a
family-wise rate of 2.5e-3 for A3 alone, run E-stoch-inf-20261115-131551-629fed8.)
Reading a failure [JUDGEMENT]: if only statistical tests fail and every deterministic one
passes, the validation is repeated on the second seed (U8), and the code passes if the
repeat passes; a correct code fails twice with probability below 1e-6, while every error
the self-test planted fails deterministically or with p many orders below p_D. "Active"
modes are those with |G_n| > 1e-6 max |G|. The tests that use a normal approximation of a
sum over modes (A4, A6 for the pair variant, A7, A8 Markov, A15) apply only when the
effective number of modes (sum w)^2 / sum w^2 of their weights w (|G|^2 or |G_a||G_b|) is
at least 100, and the fourth-moment test of A3 only from 1000 modes; below that the exact
Gamma test of A2 carries the decision. (Amended before the registered self-test: in a
development run a Heaviside step with 12 crossing modes failed A4 on correct output,
noise/JOURNAL.md 13:30.)

| Id | Test | Criterion | Catches |
|---|---|---|---|
| A0 | Format | variables `stoch_c0..3`, `stoch_acc0` present; N, L, x0 from the file agree with the input; time of each output = t0 + cycle dt to 1e-12 | wrong output set-up |
| A1 | Exact reconstruction from the keys | max_x \|xi_code - xi_ref\| <= eps_x rms(xi_ref), every variable and output (acc0 of the frozen scheme: A9) | keys, normalisation, cell-centre phase, axis order, half space, scheme |
| A2 | Spectrum | per shell s (integer \|n\|): u = mean of \|xi_n\|^2/\|G_n\|^2 over the M_s active modes, M_s u ~ Gamma(M_s, 1); min_s p_s >= p_D / S; pooled \|z\| <= z_D. For stoch_c3 also five bins of (n_z/n)^2 | normalisation (resolved to about 4/sqrt(M), 4 percent at 8538 modes), colouring, axis exchange |
| A3 | Gaussian amplitudes | w_n = xi_n/G_n on modes with \|G_n\| > 1e-3 max: Kolmogorov-Smirnov of \|w\|^2 against Exp(1) and of arg w against uniform, p >= p_D; z of mean \|w\|^4 against 2 (variance 20/M), \|z\| <= z_D | non-Gaussian amplitudes with the right spectrum |
| A4 | Correlation function | C^(r) = N^-3 sum_x xi(x) xi(x + r) for r = 0..N/2 cells along x, y, z and (1,1,1); expected sum_H 2\|G\|^2 cos(k.r), variance sum_H 4\|G\|^4 cos^2(k.r); min p >= p_D / (number of lags) | real-space assembly (seams between MeshBlocks), anisotropy |
| A5 | One-point | mean <= eps_x rms; skewness and excess kurtosis reported only (cells are correlated, no calibrated p-value) | zero mode |
| A6 | Shared degree of freedom | c1, c3 against c0. Hemisphere: max_n \|xi^c_n - (G^c_n/G^0_n) xi^0_n\| <= eps_m rms. Pair: c3 as hemisphere; c1: rho = sum xi^1 conj(xi^0) / sqrt(sum\|xi^1\|^2 sum\|xi^0\|^2) against cos(phase1) and Im rho against 0, \|z\| <= z_D | separate keys per component; wrong amplitude variant |
| A7 | Independent degrees of freedom | S = sum_n xi^2_n conj(xi^0_n): Re S and Im S against 0 with variance sum \|G^0\|^2 \|G^2\|^2 / 2, \|z\| <= z_D | one stream for all degrees of freedom |
| A8 | Between outputs | frozen: for output pairs (100,101), (100,200), (200,300), max_n \|xi_n(b) - [G_n(b)/G_n(a)] xi_n(a)\| <= eps_m rms over modes active in both; Markov: S = sum xi_n(b) conj(xi_n(a)) / phase against 0, \|z\| <= z_D, "not applicable" below 100 effective modes (rule above) | fresh draws in the frozen scheme; reused draws in the Markov scheme |
| A9 | Integrated field | frozen: max \|a_code - a_ref\| <= max(1e-6, eps_x) rms(a_ref) in real space (Runge-Kutta truncation, estimated 2e-8 for dt = 0.01, s = 5 [JUDGEMENT: Simpson error bound]; a source taken at the step start instead of the stage time errs by O(s hubble dt) = 5e-2); Markov: A1 (exact) and A2 with \|G\|^2 = base^2 [W(t) - W(t0)] | stage-time bookkeeping, missed or doubled steps |
| A10 | Band limit | max \|xi_n\| over modes outside M (n = 0 and the Nyquist planes included) and over modes of M with G_n = 0: <= eps_m rms | aliasing, cut, leakage across MeshBlock seams |
| A11 | MeshBlocks | U1, U2, U3: bit-identical; a difference up to 1e-13 rms passes only with a stated reason (distributed FFT) | keys or positions taken from the MeshBlock |
| A12 | Restart | U4 against U2 at cycles 200 and 300: bit-identical | counters in memory |
| A13 | Resolution | U5a against U5b: coefficients on M agree to eps_m rms | keys or phases depending on N |
| A14 | Card | U9 against U2: <= 1e-12 rms; A1 holds for both | precision loss on the card |
| A15 | Seeds | U8 against U2: amplitudes uncorrelated (A7 statistic), \|z\| <= z_D | seed ignored |

With single-precision output A11 and A12 compare float bits, which hides differences below
6e-8 relative; double precision is therefore requested.

## 11. Requests and open points

Requests (repeated in README.md):
- C1 (core) A double-precision option of the `bin` output (the writer uses `float`,
  `athenak/src/outputs/binary.cpp` line 96; the reader `athenak/vis/python/bin_convert.py`
  already accepts 8-byte variables, lines 149-152), or a double-precision dump of the unit
  test in the same layout.
- C2 (core) The keys of section 4: a helper `rng::ModeEntity(nx, ny, nz)` (signed) in
  `utils/rng_mesh.hpp` and the twin, and the meaning of stream 3 (bit 16 = modes, lower 16
  bits = degree of freedom) in the registry of rng.md section 6.
- C3 (core) The unit test of section 9 and runs U1-U9 (seconds each); this track validates.
- C4 (core) Markov epoch = ncycle + 1; for streams shared by initial data and evolution,
  rng.md rule 2 should say so.
- L1 (lead, with E-pre-1) SPEC 5.4, third bullet, keys real-space white noise by cell
  (step 0) and transforms it; this specification and DR 6.2 key the amplitudes by wave
  vector. Wave-vector keys give R5 (one realisation at every N) and need no transform;
  cell keys give a different realisation at each N. Proposed: wave-vector keys.

Open: [TO VERIFY] the Courant factor of P1 (SPEC U1); the size of the hemisphere/pair
difference for the initial slice (section 5); independence of the rank count is untested
until the scalar field runs on several ranks (rng.md section 9 states the same for
particles).
