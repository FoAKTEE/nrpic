# JOURNAL of the waves package (B-emd-gw, wave 2b): G1 criterion 1

Linear gravitational waves with both diagnostics of gw_diag, against analytic solutions,
with measured convergence. Helper session of 2026-11-19. Times UTC.

Times are UTC, taken from the commit times (the first headings were written from memory and corrected at 14:58).

## 2026-11-19 14:10 Start; what exists

- Worktree clean after `git merge --no-edit main` (main at 71acd0c3, merge d058b72a); no
  partial work of this package from wave 2 (the directory did not exist; the wave-2 lead
  report, `scratch/orch/wave2_reports/B-emd-gw.md` lines 82-125, lists criterion 1 as "not
  run by the track").
- Executable: core/requests-b processor build
  `scratch/core/exe/core_requests-b/athena_cpu` (sha256 c32a1389..., COMMIT 9c92f68),
  corrected polarization tensor of `z4c_linear_wave`, `amp_cross`/`phase_cross`,
  double-precision `bin` output (READY items 1, 2). Serial Kokkos build, no MPI.
- Diagnostics: `tracks/B-emd-gw/gw_diag` (TT projection `tt.tt_from_conformal`; Weyl
  `weyl.electric_magnetic` + `weyl.psi4` with a fixed direction).

## 2026-11-19 14:15 Design of the two tests [JUDGEMENT]

**Test F (flat, oblique).** `z4c_linear_wave`, box [-1/2,1/2]^3, k = 2 pi (1,1,1),
amp = 1e-6, amp_cross = 5e-7, phase_cross = 1 rad (elliptic: both polarizations, their
ratio and relative phase are tested in one run), four periods (t = 4/sqrt 3), dumps every
period/8, N = 16, 32, 64, production numerics (input `inputs/flat_oblique.athinput`).
k along (1,1,1) has a vanishing discrete divergence (all theta_i equal), so the data are
TT for the code's stencils too (REQUESTS_B.md section 1 on core/requests-b).

**Test X (expanding box).** Which set-up, exactly: the cosmological gauge of
`cosmo/README.md` (conformal-time lapse d_t alpha = -(1/3) alpha^2 K, zero shift, H = 1 at
a = 1, a = (1 + t/2)^2), box of side 4, matter only, carried by a lattice of particles at
rest (one per cell, masses rho_0 h^3, the layout of `cosmo/ic/make_lattice.py --ppc 1`),
production configuration of `cosmo/README.md`; problem generator `nrpic_cosmo` with
`id = file`. The release generator cannot set a TT metric perturbation (NRCOSMO1 carries
psi, K, alpha and Ahat_ij only; REQUESTS_B.md item 6 deferred), but it can set a TT
extrinsic curvature: the initial slice is conformally flat (h = 0) with
Ahat_ij = -(1/2) h'_ij, h' = eps_+ e+ cos(k.x) + eps_x ex cos(k.x + phi_x),
eps_+ = 2e-6, eps_x = 1e-6, phi_x = 1, k = (2 pi/4)(1,1,0) (the (k,k,0) direction whose
strain the first GW source measures). Momentum constraint: exact (TT Ahat, uniform psi
and K). Hamiltonian constraint: violated only by the second-order term
Ahat_ij Ahat^ij <= ~1e-12 against 16 pi rho = 6. The solution is a standing wave
h = T(t) [eps_+ e+ cos(k.x) + eps_x ex cos(k.x + phi_x)] with
T'' + (4/s) T' + |k|^2 T = 0, s = t + 2, T(0) = 0, T'(0) = 1:
T = c1 j_1(|k|s)/(|k|s) + c2 y_1(|k|s)/(|k|s) (`wlib/refs.py`, checked against a direct
integration of the ODE to 1e-11 in `tests/test_refs.py`). The particles stay at rest to
second order (the lapse is homogeneous at first order, so d_t u_i = -alpha d_i alpha = 0).
t = 0 to 10 (a = 1 to 36; |k| s from 4.44 to 26.7, 3.5 oscillations), dumps every 0.25,
N = 16, 32, 64 (input `inputs/expanding.athinput`, data `scripts/make_expanding_ic.py`).

**Measures (both tests).** Amplitudes at +k of the two polarizations, in gw_diag's basis
`pol_basis(khat)`: P = (1/2) e+ : c_k[h], X = (1/2) ex : c_k[h], and their time
derivatives P', X' (t = coordinate time = conformal time; h' = <alpha> d_tau h).
Forward combination W = P + i P'/|k| (the whole wave for a mode exp(-i|k|t); for the
standing wave of test X, W = (eps/2)(T + i T'/|k|), which never vanishes): amplitude error
|W/W_ex| - 1 and phase error arg(W/W_ex) per polarization; backward error
|Wb - Wb_ex|/|W_ex| with Wb = P - i P'/|k|; polarization ratio W_x/W_+ against the exact
one (modulus and argument).
- TT diagnostic: h^TT, d_tau h^TT from (gt, At) of the dump (`tt.tt_from_conformal`).
- Weyl diagnostic: Psi_4 along +khat and -khat from gw_diag's E, B (finite differences of
  order 6, the code's stencil, and spectral) on (gamma, K) of the dump. The eight
  coefficients at +-k determine (P, X, P', X') through the closed form below at the
  measured background (a = <chi>^(-1/2), calH = -<alpha K>/3), so the Weyl diagnostic
  gives amplitude, phase and polarization in the same terms as the TT one.

## 2026-11-19 14:15 Derivation of the closed form (wlib/weylref.py)

Slice gamma = a^2 (delta + h), K_ij = -(1/2 alpha) d_t gamma_ij with alpha = a:
K_ij = -(calH/a) gamma_ij - (a/2) h'_ij, K = -3 calH/a (h traceless). To first order in h:
K K_ij = 3 calH^2 (delta + h) + (3/2) calH h', K_ik K^k_j = calH^2 (delta + h) + calH h',
R_ij = -(1/2) lap h_ij. So [R + K K - K K]_ij = -(1/2) lap h + 2 calH^2 (delta + h)
+ (1/2) calH h', whose trace-free part (with respect to gamma, the 2 calH^2 (delta + h)
piece is pure trace) is E_ij = (1/2)(-lap h_ij + calH h'_ij). eps_i^kl = a^-1 [ikl],
D_k K_lj = -(a/2) d_k h'_lj, so B_ij = -(1/2) sym([ikl] d_k h'_lj). No field equation is
used. In the flat case (a = 1, calH = 0) this is gw_diag's linear reference
(analytic.py). Check (tests/test_refs.py, 5 tests pass, 2 s): the closed form equals
gw_diag's full spectral evaluation of E, B, Psi_4 on exact (gamma, K) to < 1e-5 relative
(the O(h) nonlinear terms, h ~ 1e-6) for the flat elliptic wave and for the FLRW standing
mode at t = 3.1; the inversion recovers (P, X, P', X') to 1e-10 and its matrix has
condition number < 1e3.

## 2026-11-19 14:20 Predictions of tests F and X (before any run of either test)

Numbers from run **B-20261119-141844-2c5d622** (`scripts/predict.py`,
`results/predictions.json`, `figs/predictions.png`): the code's operators (sixth-order
second derivative, KO sigma = 0.5 at nghost 4 summed over the axes, RK4 at dt = 0.25 dx,
for X also dt <= 0.01/calH) applied to the single tensor mode; the predictor reproduces
core's card numbers for one period of the (1,1,1) wave at N = 64 (-7.9e-9 amplitude and
1.76e-7 rad per period, READY of core/requests-b, CARD TEST) times four. Sign convention
here: phase error = arg(W_num/W_ex) with W ~ exp(-i|k|t), so a lagging numerical wave has
a positive phase error.

Test F (flat, k = 2 pi (1,1,1), A = 1e-6, A_x = 5e-7, phase 1 rad, t_end = 4/sqrt 3):

| N | steps | amplitude error | phase error (rad) | 1 - w_h/k |
|---|---|---|---|---|
| 16 | 148 | -1.41e-4 | +2.53e-4 | 3.2e-6 |
| 32 | 296 | -1.72e-6 | +1.22e-5 | 5.1e-8 |
| 64 | 592 | -3.17e-8 | +7.03e-7 | 8.0e-10 |

orders 6.4, 5.8 (amplitude), 4.4, 4.1 (phase).

- **F1** (generator = gw_diag basis). At t = 0 the TT amplitudes equal amp/(2i),
  amp_x e^{i phase}/(2i) to <= 1e-12 relative, so the generator's e+, ex are
  pol_basis(khat) (core's statement, REQUESTS_B.md section 1). Refuted if > 1e-10.
- **F2** (evolution). TT amplitude and phase errors of W+ and Wx at t_end equal the table
  to 10 per cent at N = 32 and 64 and to 30 per cent at N = 16. Refuted otherwise.
- **F3** (polarization). W_x/W_+ equals (A_x/A) e^{i} to <= 1e-8 in modulus and argument
  at every N and time (both polarizations have the same discrete symbol). Refuted if > 1e-7.
- **F4** (direction). Backward part |Wb|/|Wf| = |1 - w_h/k|/2 (the semi-discrete
  eigenvector; RK4 does not change it): 1.6e-6, 2.5e-8, 4e-10; refuted if off by more
  than a factor 2 above 1e-11.
- **F5** (Weyl vs TT). With gw_diag's order-6 stencils the Weyl W differs from the TT W by
  the symbol error of those stencils (relative 6.4e-6, 1.0e-7, 1.6e-9 for the second and
  2.5e-5, 4.1e-7, 6.4e-9 for the first derivative at N = 16, 32, 64): between 1e-6 and
  5e-5 at N = 16, 1e-8 and 1e-6 at N = 32, 1e-10 and 2e-8 at N = 64, order about 6.
  With spectral derivatives: <= 1e-8 at every N (nonlinear terms reach the mode k only
  at O(A^2)). The Weyl amplitude, phase and polarization errors then equal the TT ones
  to within that difference. Refuted if outside these bands.
- **F6** (non-TT content). ||h - h^TT||/||h^TT|| <= 1e-4 (core: a second-order non-TT
  part 3.4e-6 A per period at k = 0 and 2k); TT content outside +-k <= 1e-5 of the wave.

Test X (expanding box, k = (pi/2)(1,1,0), eps+ = 2e-6, eps_x = 1e-6, phase 1, t_end = 10):

| N | steps | amplitude error | phase error (rad) |
|---|---|---|---|
| 16 | 360 | -6.97e-5 | +8.36e-5 |
| 32 | 413 | +1.65e-6 | +3.21e-6 |
| 64 | 658 | +1.94e-7 | +1.34e-7 |

(N = 16 runs at the expansion step 0.01/calH throughout, so its RK4 error does not scale
with dx; N = 64 is dominated by the RK4 error of the early steps.)

- **X1** (data path). At t = 0 the TT measurement gives P = X = 0 and
  P' = eps+/2, X' = eps_x e^{i}/2 to <= 1e-12 relative. Refuted if > 1e-10.
- **X2** (background). a = <chi>^(-1/2) equals (1 + t/2)^2, <alpha> equals a, and
  calH = -<alpha K>/3 equals 1/(1 + t/2), each to <= 1e-6 relative over t <= 10 (RK4 at
  dt <= 0.01/calH; the particle lattice deposits a uniform density). Refuted if > 1e-5.
- **X3** (evolution). TT amplitude and phase errors at t = 10 equal the table to 20 per
  cent at N = 16 and 32; at N = 64 within a factor 2 (a background error of order 1e-7
  would enter the amplitude directly). Refuted otherwise.
- **X4** (polarization). W_x/W_+ = (eps_x/eps_+) e^{i} to <= 1e-8. Refuted if > 1e-7.
- **X5** (Weyl vs TT). Order-6 Weyl vs TT: 1e-7 to 1e-4 (N = 16), 1e-9 to 2e-6 (32),
  1e-11 to 3e-8 (64), order about 6; spectral Weyl vs TT <= 1e-7 at every N. The matter
  term -4 pi S^TF is zero for dust at rest; refuted if outside these bands.
- **X6** (non-TT, shift). ||h - h^TT||/||h^TT|| <= 1e-4; max |beta| = 0.

Cost [JUDGEMENT]: the only serial Z4c rate on record is 1.5e4 zone-cycles per second
(periodic_z4c run B-emd-gw-20261115-113218-0ea0f74, with Weyl extraction); without it I
expect 3e4 to 1e5. N = 16, 32 on processors (minutes); N = 64 (1.6e8 zone-cycles per
test) goes to one card in a batch job (about 0.05 card-hours with the queue overhead)
unless the processor rate exceeds 1e5.

## 2026-11-19 14:21 Runs started; cost measured

- Processors, N = 16 and 32: test F run **B-20261119-142016-ee73a03**, test X run
  **B-20261119-142021-8f4c441** (two serial processes each, in the background).
- Measured serial rate in the first minute: 1.46e4 zone-cycles per second (F, N = 16:
  100 cycles in 28 s), 1.1e4 (X, N = 16 with particles). So N = 32 takes about 11 and
  20 minutes, and N = 64 would take 3 and 4.5 hours: the cost prediction of 3e4 to 1e5
  failed (the low rate is that of the Kokkos Serial build, not of the Weyl extraction).
  N = 64 of both tests goes to one card (batch `inputs/card64.list`, executable
  `scratch/core/exe/core_requests-b/athena_gpu`, initial data of X from run
  B-20261119-142108-1e5add9). Prediction for the card: both runs complete in under
  5 minutes of card time (about 1.7e8 zone-cycles each at >= 1e6 per second);
  card-hours charged <= 0.1 (wall limit 20 minutes requested).

## 2026-11-19 14:22 Insurance runs at N = 48 on processors

The card job (Slurm 4635) waits behind two running jobs of another user and five pending
ones (squeue 14:22). So that convergence does not hang on the queue, both tests also run
at N = 48 on processors (one serial process each, expected 56 and 90 minutes).
Predictions at N = 48 (same predictor, `wlib/predict.py`): F: 444 steps, amplitude
-1.58e-7, phase +2.27e-6; X: 524 steps, amplitude +5.52e-7, phase +5.05e-7; criteria as
F2 and X3 (10 and 20 per cent).

## 2026-11-19 14:56 Provisional outcome at N = 16 and 32 (run B-20261119-145125-51e9f8f)

Analysis of runs B-20261119-142016-ee73a03 (F) and B-20261119-142021-8f4c441 (X). The run
is recorded as failed (exit 1): `results.json` and the per-dump tables were written, then
the convergence figure raised a TypeError (`lw` given twice); fixed in `scripts/analyze.py`.
The figures come with the final analysis.

- F1: at t = 0 the TT amplitudes equal the generator's to 6.0e-12 (N = 16) and 2.7e-12
  (N = 32) in modulus, 2.4e-11 in the phase of the cross part. Not refuted (threshold
  1e-10), but the number I wrote (1e-12) was too optimistic: a diagonal component 1 + h
  with h ~ 1e-6 carries a rounding of 1e-10 of h per cell, averaged by the projection over
  N^3 cells. The generator's e+, ex are gw_diag's pol_basis(khat): confirmed.
- F2: confirmed to three to four digits. N = 16: amplitude -1.409e-4 (predicted -1.409e-4),
  phase +2.531e-4 (+2.531e-4); N = 32: -1.717e-6 (-1.718e-6), +1.218e-5 (+1.217e-5); the
  cross polarization identical; orders 6.36 and 4.38 (predicted 6.36, 4.38).
- F3: confirmed: polarization ratio errors <= 6.2e-10 (modulus) and 7.0e-10 (argument).
- F4: refuted as worded. The backward combination is not constant at |1 - w_h/k|/2; it
  oscillates with half the wave period between 0 (at every half period, so also at the last
  dump, 4.9e-10) and |1 - w_h/k| (3.19e-6 at N = 16, 5.08e-8 at N = 32; 1 - w_h/k = 3.2e-6
  and 5.1e-8). Cause: the generator sets At from the continuum frequency |k|, so the data
  excite the backward eigenmode of the semi-discrete system with relative amplitude
  (k/w_h - 1)/2, which beats against the forward error term; zeros, period and maximum
  follow from that and are what the dumps show (pattern dump by dump in
  `dumps_flat_N16.json`).
- F5: confirmed. Order-6 Weyl vs TT 3.07e-5 (N = 16), 4.91e-7 (N = 32), order 5.97;
  spectral Weyl vs TT 1.2e-11 at both N. With order-6 stencils the Weyl amplitude error is
  -1.716e-4 / -2.208e-6 (TT -1.409e-4 / -1.717e-6): the stencil error of the diagnostic adds
  to the evolution error; the Weyl phase error equals the TT one to 3 digits.
- F6: refuted for the full field: ||h - h^TT||/||h^TT|| reaches 1.44e-4 at the end (bound
  1e-4), the same at N = 16 and 32 to three digits and growing as t^2 (1.7e-5 at t = 0.79,
  1.44e-4 at t = 2.31, ratio 8.5 = (2.31/0.79)^2). The TT content outside +-k is 8e-10 and
  1.2e-9 (bound 1e-5): confirmed. [JUDGEMENT, tested below by the amplitude scan] the
  non-TT part is the second-order backreaction of periodic_z4c item 3 (A^2 t^2).
- X1: P = X = 0 and P' to 2.4e-11 (N = 16), 2.0e-11 (N = 32): not refuted (threshold
  1e-10), number too optimistic for the same rounding reason (K_xx = -1 + Ahat_xx).
- X2: confirmed: max relative errors over t <= 10: a 5.1e-8 / 4.3e-8, calH 3.6e-8 / 3.4e-8,
  alpha/a 7.0e-8 / 6.5e-8 (N = 16 / 32).
- X3: N = 16 confirmed (amplitude -7.05e-5 against -6.97e-5, phase 8.30e-5 against
  8.36e-5). N = 32: phase confirmed (3.09e-6 against 3.21e-6), amplitude +1.32e-6 against
  +1.65e-6, 20.0 per cent low: on the bound, counted as failed.
- X4: confirmed: polarization ratio errors <= 7.9e-9 (modulus), 2.4e-8 (argument).
- X5: confirmed. Order-6 Weyl vs TT 3.13e-5 / 5.01e-7 (order 5.97); spectral Weyl vs TT
  1.9e-8 / 2.2e-8 (bound 1e-7), not falling with N.
- X6: max |beta| = 0 confirmed; ||h - h^TT||/||h^TT|| = 5.6e-4 at both N: refuted (bound
  1e-4), resolution independent like F6.

Post hoc, not a prediction: after seeing the N = 32 amplitude I integrated the uniform
background (chi, Khat, Theta, alpha with the code's equations) together with the mode in
classical RK4 (`predict_flrw_coupled(..., scheme="classical")`): N = 32 amplitude 1.60e-6
instead of 1.65e-6, a error 6.7e-9 (the code: 4.3e-8). That does not explain the gap.

Trap met (recorded so nobody repeats it): at about 14:54 I edited `scripts/run_expanding.sh`
while run B-20261119-142234-85da208 (N = 48) was executing it; bash reads a script as it
goes, so the wrapper would have resumed at a shifted offset. I restored the committed bytes
(`git checkout`, `cmp` equal) a minute later, before its `wait` returned. The scan uses a new
script `scripts/run_ascan.sh` instead.

## 2026-11-19 14:57 Hypothesis H1 and the amplitude scan: predictions

**H1.** AthenaK's `rk4` is not classical RK4 but RK4()4[2S] of Ketcheson (2010)
(`athenak/src/driver/driver.cpp` lines 145-176). On a linear problem with constant
coefficients it has the same stability polynomial (checked: |R - (1 + z + ... + z^4/24)|
<= 2e-15 for four values of z), which is why F matches to four digits; on the nonlinear
background coupled to the mode its error constants differ. The predictor with the 2S
stages (`wlib/predict.py`, step_rk4_2s, fourth order checked on y' = y^2) should give the
measured X errors: amplitude -7.05e-5 and +1.32e-6 within 5 per cent at N = 16 and 32,
phase 8.30e-5 and 3.09e-6 within 5 per cent, and an a error within a factor 2 of the
measured 4.3e-8. Refuted if the N = 32 amplitude is off by more than 10 per cent.

**Amplitude scan** (`scripts/run_ascan.sh`, N = 16, amplitudes x10 and x1/10 for both
tests; analysis with `--scale-flat/--scale-exp`). Predictions:
- A1: TT amplitude and phase errors at the end do not change with the amplitude (linear
  regime): equal to the N = 16 values above within 1e-3 of themselves for x1/10 and within
  1 per cent for x10.
- A2: the non-TT fraction is second order: proportional to the amplitude, 1.44e-3 (F, x10),
  1.44e-5 (F, x1/10), 5.6e-3 and 5.6e-5 (X), each within 20 per cent.
- A3: the spectral-Weyl vs TT difference of X (1.9e-8) is second order too: 1.9e-7 for x10
  and 1.9e-9 for x1/10 within a factor 2; refuted if it stays or grows as 1/A (rounding).
- A4: F1/X1 at t = 0 scale as 1/A (rounding): about 6e-13 (x10) and 6e-11 (x1/10) for F.

## 2026-11-19 15:37 H1 confirmed (run B-20261119-153548-c7338f1)

`scripts/predict_2s.py` (`results/predict_2s.json`, `figs/predict_2s.png`): with the code's
RK4()4[2S] stages on the uniform background coupled to the mode, the predicted X errors
at t = 10 are, against the measured ones (TT):

| N | amplitude 2S / measured | phase 2S / measured | max a error 2S / measured |
|---|---|---|---|
| 16 | -7.048e-5 / -7.048e-5 (ratio 1.0001) | 8.304e-5 / 8.304e-5 (1.0000) | 5.1e-8 / 5.09e-8 |
| 32 | +1.317e-6 / +1.324e-6 (0.995) | 3.065e-6 / 3.089e-6 (0.992) | 4.3e-8 / 4.30e-8 |

H1 holds (bound 5 per cent): the 20 per cent gap of X3 at N = 32 was a defect of my
predictor (classical RK4, exact background), not of the code; the error of the background
itself is the 2S integrator's too. The classical-RK4 predictors give 1.65e-6 (exact
background) and 1.60e-6 (coupled). F is unaffected: on a linear problem with constant
coefficients the two schemes share the stability polynomial.

**Revised predictions for the runs still going** (X at N = 48, run
B-20261119-142234-85da208, at cycle 300 of about 524 now; X at N = 64 in the card job),
2S predictor: N = 48 amplitude +4.25e-7, phase +5.88e-7; N = 64 amplitude +1.40e-7, phase
+2.76e-7; within 5 per cent. Note: the X errors at N >= 32 are dominated by the time
integration of the early, expansion-limited steps (dt = 0.01/calH does not shrink with
dx), so the convergence of X in N is not a clean power law: amplitude 7.0e-5, 1.3e-6,
4.3e-7, 1.4e-7 predicted (orders 5.7, 2.7, 3.9), phase 8.3e-5, 3.1e-6, 5.9e-7, 2.8e-7.
The spatial part alone (exact-background, classical predictor minus its RK4 part) is not
separated here [JUDGEMENT: a run with dt_expansion = 0.001 would isolate it; not run].

## 2026-11-19 15:50 Amplitude scan: outcomes (runs B-20261119-153637-02c822f, analyses -154708-89d00ea, -154738-30faa29)

N = 16, amplitudes x10 and x1/10 of both tests (`results/ascan_s10_results.json`,
`ascan_s0p1_results.json`; x1 from B-20261119-145125-51e9f8f). Card batch
B-20261119-142124-feb2daf (N = 64 of both tests) ran meanwhile: Slurm 4635, 69 s,
0.0192 card-hours (prediction <= 0.1: confirmed); X at N = 64 took 658 steps as predicted.

| quantity at N = 16 | x10 | x1 | x1/10 | scaling |
|---|---|---|---|---|
| F TT amplitude error | -1.4094e-4 | -1.4092e-4 | -1.4092e-4 | none (A1 confirmed) |
| F TT phase error | 2.5320e-4 | 2.5310e-4 | 2.5309e-4 | none |
| X TT amplitude error | -7.0480e-5 | -7.0476e-5 | -7.0450e-5 | none (A1: within 4e-4 of itself) |
| X TT phase error | 8.3042e-5 | 8.3043e-5 | 8.3097e-5 | none (6e-4) |
| F non-TT fraction (max) | 1.44e-3 | 1.44e-4 | 1.44e-5 | proportional to A (A2 confirmed) |
| X non-TT fraction (max, instantaneous norm) | 5.57e-3 | 5.57e-4 | 8.45e-5 | A at large A; x1/10 is 50 per cent above A2's 5.6e-5 (refuted for that point) |
| X non-TT against the envelope (max) | 3.11e-4 | (final run) | 4.72e-6 | between A and A^1.1 |
| F spectral Weyl vs TT | 4.2e-10 | 1.2e-11 | 5.6e-14 | about A^2 (cubic terms at the mode k) |
| X spectral Weyl vs TT | 1.93e-8 | 1.91e-8 | 1.95e-8 | none (A3 refuted) |
| F TT at t = 0 | 9.9e-13 | 6.0e-12 | 5.9e-11 | 1/A, rounding (A4 confirmed) |
| X TT at t = 0 | 3.1e-12 | 2.4e-11 | 1.6e-10 | 1/A, rounding |
| X polarization ratio error (max) | 6.2e-10 | 4.6e-9 | 3.9e-8 (modulus) | 1/A, rounding |

Readings:
- The measured amplitude and phase errors are those of the linear discrete system at every
  amplitude: the comparison is in the linear regime and A = 1e-6 is not at a floor.
- The non-TT part of F is second order in A (exactly proportional to A relative to the
  wave), so F6's excess is the backreaction of periodic_z4c item 3, and the TT content at
  +-k is untouched by it. Named cause [VERIFIED by this scan].
- The polarization errors of both tests and the t = 0 errors are rounding of 1 + O(A).
- The spectral-Weyl vs TT difference of X, 1.9e-8, depends neither on A (this scan) nor
  on N (2.2e-8 at N = 32). [JUDGEMENT, not tested] it is the background error (a, calH
  and alpha/a are wrong by 4e-8 to 7e-8 for every N <= 32, H1): the inversion uses the
  measured a and calH = -<alpha K>/3 and the TT side uses h' = <alpha> d_tau h, which
  agree with each other only up to that error, through the calH h' term of E.

## 2026-11-19 16:00 Outcome at N = 64 (analysis B-20261119-155119-5459be6, runs on one card)

Test F at N = 64 (card run B-20261119-142124-feb2daf/flatN64): TT amplitude -3.10e-8
(predicted -3.17e-8, 2 per cent), phase 7.067e-7 (7.034e-7, 0.5 per cent): F2 confirmed at
all three N; orders 6.36, 5.79 (amplitude) and 4.38, 4.11 (phase), equal to the predicted
6.36, 5.76 and 4.38, 4.11. F3: polarization ratio errors 1.0e-9 / 1.1e-9 (bound 1e-8).
F4 (reworded form): backward maximum 9.7e-10 against |1 - w_h/k| = 8.0e-10. F5: order-6
Weyl vs TT 3.07e-5, 4.91e-7, 8.47e-9 (orders 5.97, 5.86; band at 64: 1e-10 to 2e-8);
spectral 1.1e-11 to 1.2e-11. The Weyl (order 6) amplitude error is -1.716e-4, -2.208e-6,
-3.867e-8 and its phase error equals the TT one to 4 digits at every N.

Test X at N = 64 (card run, expN64): the cross polarization equals the 2S prediction to
4 digits (amplitude 1.3989e-7 against 1.399e-7, phase 2.7624e-7 against 2.762e-7). The plus
polarization does not: amplitude 1.538e-7 (+10 per cent), phase 3.84e-7 (+39 per cent), so
the revised X prediction fails for the plus polarization at N = 64. The difference is the
polarization-ratio error, which grows steadily in time (arg R = -1.1e-7 at t = 10, -2.4e-8
at N = 32, -4.5e-9 at N = 16: about N^2.3) while the wave decays as 1/a (|W+| from 4.5e-7 to
1.3e-8). The plus polarization of k = (1,1,0) lives in the diagonal components
(e+ = zz - (xx + yy - xy - yx)/2), the cross one in xz and yz only. [JUDGEMENT] It is the
rounding of the diagonal 1 + h through the second differences (relative size about
1e-16 (N/L)^2/(|k|^2 |h|), growing as N^2 and as 1/|h|), the same mechanism as the 1/A
scaling of the polarization errors in the amplitude scan at N = 16.

X non-TT part against the envelope: 3.11e-5 at the end for N = 16, 32, 64 alike, and
3.11e-4 / 3.11e-5 / 4.7e-6 for amplitudes x10 / x1 / x1/10: second order in A, with a
rounding floor at x1/10 (the instantaneous-norm values of X6 were inflated at the nodes of
the standing wave).

**Prediction for a check of that judgement** (card run, X at N = 64 with eps x10): the plus
polarization then follows the 2S prediction like the cross one: amplitude and phase errors
within 5 per cent of 1.40e-7 and 2.76e-7, and |arg R| <= 1.5e-8 (a tenth of now). Refuted if
the plus phase error stays near 3.8e-7.

## 2026-11-19 16:40 Correction of the 14:57 trap note; N = 48 runs done

The restore of `scripts/run_expanding.sh` did not protect run B-20261119-142234-85da208:
my edit (python, `open(..., "w")`) rewrote the file in place, so the running bash, which
keeps reading the open file, saw the edited bytes; `git checkout` then wrote a new file
(new inode) that bash never read. After its last command the wrapper read the shifted tail
of the edited file and stopped with exit 127 ("line 37: ena.log | tr ...: command not
found"), so nrpic-run recorded the run as failed. AthenaK itself is unaffected: its log
ends with rc=0 at t = 10 after 524 cycles (predicted 524), and all 41 dumps exist. The
failed status stays on record; the analysis uses the outputs with this note. Lesson for
the HANDOFF trap list: a restore with git does not help a running bash script; only never
editing it does.

F at N = 48: run B-20261119-142233-70d5043 completed (444 cycles as predicted, 88 min).
X at N = 48: 524 cycles, 2 h 16 min at 7.1e3 zone-cycles per second.

## 2026-11-19 16:48 Final analysis at N = 16, 32, 48, 64 (run B-20261119-164402-7438a99)

`results/final_results.json`, `figs/final_{flat,exp}_errors.png`, `figs/final_convergence.png`
(looked at). Run B-20261119-163932-5ce4298 is the same analysis with local orders computed
as log2 of the ratio, wrong for 32-48-64; superseded, kept on record.

- F at N = 48: amplitude -1.574e-7 (predicted -1.576e-7), phase 2.273e-6 (2.270e-6): F2
  confirmed at all four N. Local orders (16-32, 32-48, 48-64): amplitude 6.36, 5.89,
  5.65; phase 4.38, 4.14, 4.06; Weyl-6 vs TT 5.97, 5.94, 5.74 (3.07e-5, 4.91e-7,
  4.42e-8, 8.47e-9); spectral Weyl vs TT 1.1e-11 to 1.2e-11; polarization ratio errors
  <= 1.1e-9; backward maxima 3.2e-6, 5.1e-8, 4.5e-9, 9.7e-10.
- X at N = 48: the cross polarization equals the 2S prediction (amplitude 4.250e-7 against
  4.250e-7, phase 5.880e-7 against 5.879e-7); the plus polarization is off by +2.6 per cent
  (amplitude 4.362e-7) and +10 per cent (phase 6.478e-7): the revised prediction (5 per
  cent) holds for the cross polarization at every N and fails for the plus phase at
  N = 48 and 64, as at 64 (arg R = 6.0e-8 at N = 48, between 2.4e-8 and 1.1e-7).
  Weyl-6 vs TT 3.13e-5, 5.01e-7, 4.50e-8, 1.66e-8 (orders 5.97, 5.95, then the 2e-8
  offset); spectral 1.9e-8 to 2.4e-8.
- The x10 card check (B-20261119-155758-458cf17, Slurm 4662) is still waiting in the queue
  (25 jobs, 16:47); its analysis command is in README.md, "Open".

## 2026-11-19 16:52 End of the session

Unit tests: 5 pass. Pending: the x10 card check, Slurm 4662 (run
B-20261119-155758-458cf17), about eighteen jobs ahead of it in the queue (16:50); its
analysis command is in README.md, "Open". Card-hours used by this package: 0.019
(B-20261119-142124-feb2daf) of the half card-hour allowed; 0.2 requested for 4662 (10-minute
limit, expected about 0.02). No processor run of this package is still going.

## 2026-11-20 22:15 Wave 3, round 1: start (helper session; times UTC)

State: worktree at c9aba208 (PLAN-wave3, round 1, package `waves`); no partial work of
this package since 2026-11-19 16:52. Card job 4662 = run B-20261119-155758-458cf17 (X at
N = 64, eps x10) ran on 2026-11-19 20:01-20:02 UTC, rc = 0, 658 cycles, 41 dumps; closed
now with `nrpic-run finish` (commit dc94328d; 26 s wall, 0.0072 card-hours). Tasks of the
round: (1) judge the x10 check; (2) flat wave along k = 2 pi (1,2,0) (nonzero discrete
divergence); (3) time/space split of the X error; (4) two-precision reader and G_tot into
gw_diag.

### Prediction of the x10 check (restated from 2026-11-19 16:00, before the analysis)

Numbers at x1 (N = 64, final analysis B-20261119-164402-7438a99, `results/final_results.json`)
and the 2S prediction (`results/predict_2s.json`, run B-20261119-153548-c7338f1,
"64"/"coupled_2s": amplitude 1.39885e-7, phase 2.76207e-7):

| quantity at t = 10 | x1 measured | 2S | excess at x1 | predicted at x10 |
|---|---|---|---|---|
| plus amplitude error | 1.5384e-7 | 1.3989e-7 | 1.40e-8 | 1.399e-7 + 1.4e-9 |
| plus phase error | 3.8415e-7 | 2.7621e-7 | 1.08e-7 | 2.762e-7 + 1.1e-8 |
| cross amplitude error | 1.3989e-7 | 1.3989e-7 | 1e-11 | unchanged |
| cross phase error | 2.7624e-7 | 2.7621e-7 | 3e-11 | unchanged |
| arg R error (end) | -1.079e-7 | 0 | | about -1.1e-8 |
| abs R error (end) | -1.39e-8 | 0 | | about -1.4e-9 |

Judgement [JUDGEMENT under test]: the plus excess is rounding of the diagonal 1 + h through
the second differences, which scales as 1/|h|. Prediction: at x10 the plus amplitude and
phase errors are within 5 per cent of the 2S values (as written at 16:00), the plus excess
falls by a factor 10 +- 3 (arg R at the end between -0.8e-8 and -1.5e-8), and the cross
polarization stays on the 2S prediction within 5e-9 absolute (the second-order shift of the
amplitude error seen at x10 at N = 16 was 4e-9, 15:50 table). Refuted if the plus phase error
stays near 3.8e-7, or if the excess falls by less than a factor 5.

## 2026-11-20 22:25 Outcome of the x10 check: rounding confirmed (analysis B-20261120-221708-d8eae03, figure B-20261120-222234-4e2435d)

`results/x10_64_results.json`, `results/x10_check.json`, `figs/x10_check.png` (looked at:
left, the plus phase error of the x10 run lies on the 2S curve like both cross curves, the
x1 plus curve departs from t = 4 on; right, the x10 polarization-ratio errors times 10 lie
on the x1 curve from t = 1 to 10). Numbers at t = 10, TT diagnostic [VERIFIED]:

| quantity | x1 | x10 | ratio x1/x10 |
|---|---|---|---|
| plus amplitude error (2S 1.3989e-7) | 1.5384e-7 | 1.4154e-7 (+1.2 per cent) | |
| plus phase error (2S 2.7621e-7) | 3.8415e-7 | 2.8952e-7 (+4.8 per cent) | |
| cross amplitude error | 1.39889e-7 | 1.40092e-7 | |
| cross phase error | 2.7624e-7 | 2.7858e-7 | |
| arg R error (end) | -1.0792e-7 | -1.0940e-8 | 9.86 |
| abs R error (end) | -1.3947e-8 | -1.4491e-9 | 9.62 |
| plus excess over 2S, amplitude | 1.395e-8 | 1.66e-9 | 8.4 |
| plus excess over 2S, phase | 1.079e-7 | 1.33e-8 | 8.1 |
| spectral Weyl vs TT (end) | 2.30e-8 | 2.32e-8 | 1.0 |

- Prediction confirmed: plus amplitude and phase within 5 per cent of 2S (1.2 and 4.8 per
  cent), plus excess down by 8.1 to 8.4 (band 7 to 13), arg R at the end -1.09e-8 (band
  -0.8e-8 to -1.5e-8), cross within 5e-9 of 2S (+2.0e-10 and +2.4e-9).
- The clean measure is the plus-minus-cross difference (the polarization ratio), which falls
  by 9.86 (argument) and 9.62 (modulus) for a tenfold amplitude: the plus-polarization excess
  of X at N >= 48 is rounding of the diagonal 1 + h (scales as 1/A) [VERIFIED by this run;
  the mechanism "through the second differences" stays JUDGEMENT].
- New, not predicted: the cross phase error at x10 sits 2.4e-9 above 2S (x1: 3e-11). The
  factor 75 for a tenfold amplitude is about A^2: a second-order frequency shift (relative
  size A^2), the same size core reported for the flat wave at A = 1e-5 (REQUESTS_B.md
  section 1, T8) [JUDGEMENT]. It is also inside the plus excess at x10, which is why that
  excess fell by 8.1 rather than 10.
- The spectral-Weyl vs TT offset (2.3e-8) does not depend on the amplitude at N = 64 either
  (as at N = 16): not rounding; tested next by the step test (task 3).
- Order-6 Weyl vs TT 1.68e-8 at x10 (x1: 1.66e-8). Card time of 4662: 0.0072 card-hours.

Verdict for criterion 1 [JUDGEMENT]: the one open sub-item is closed; both polarizations of
X follow the code's integrator prediction at N = 64 once the rounding floor of the diagonal
metric is lowered, and the floor itself behaves as rounding.

## 2026-11-20 22:30 Predictions of F2 and of the step test XS (run B-20261120-222735-4a8f0e1)

`scripts/predict_r1.py`, `results/predictions_r1.json`, `figs/predictions_r1.png` (looked
at). New model `wlib/z4c_symbol.py`: the whole linearized Z4c system of the code about flat
space (h_ab, A_ab, Gamma^a, Khat, Theta, chi, alpha; 25 amplitudes per mode), with the
code's stencils (first derivative s_a, second derivative q_a, mixed derivatives s_a s_b,
Kreiss-Oliger on every variable) and its rk4. Checks before use: with kappa1 = 0 or along
(1,1,1) it reproduces the two-variable predictor of predict.py to 1e-10 relative (TT
amplitude and phase), with a non-TT part <= 2e-14 (rounding) [VERIFIED, same run].

**Why (1,2,0) differs from (1,1,1) [derivation, JUDGEMENT until the run].** The generator
sets Gamma^i = 0 and continuum-TT data. The code's Ricci uses the evolved Gamma^i
(z4c_calcrhs.cpp line 436), so at t = 0 every component of h obeys the same scalar
equation and the TT part evolves exactly as along (1,1,1). The discrete divergence enters
only through the constraint damping term -2 kappa1 (Gamma - Gamma_d) of the Gamma equation
(line 657): Gamma_d = d_b h_ab is not zero for (1,2,0) (relative size of the discrete
divergence 4.1e-4, 7.1e-6, 6.3e-7, 1.1e-7 at N = 16, 32, 48, 64, order 5.9), so Gamma^i
grows at rate 2 kappa1 and feeds a non-TT part into A and h. The TT amplitude feels this
only at second order in the divergence.

### F2: k = 2 pi (1,2,0), amp 1e-6, amp_cross 5e-7, phase 1 rad, four periods (t = 4/sqrt 5)

| N | steps | amplitude error | phase error (rad) | 1 - w_h/k | non-TT at +k (max) | abs Gamma at +k (max) | Weyl-6 symbol e1 / e2 |
|---|---|---|---|---|---|---|---|
| 16 | 115 | -6.677e-3 | +4.321e-3 | 1.5e-4 | 2.1e-5 | 2.6e-11 | -1.2e-3 / -3.1e-4 |
| 32 | 229 | -6.308e-5 | +9.479e-5 | 2.6e-6 | 3.6e-7 | 4.5e-13 | -2.0e-5 / -5.1e-6 |
| 48 | 344 | -3.997e-6 | +1.173e-5 | 2.3e-7 | 3.2e-8 | 4.0e-14 | -1.8e-6 / -4.6e-7 |
| 64 | 458 | -5.764e-7 | +2.924e-6 | 4.1e-8 | 5.7e-9 | 7.1e-15 | -3.3e-7 / -8.2e-8 |

Local orders: amplitude 6.7, 6.8, 6.7 (Kreiss-Oliger), phase 5.5, 5.2, 4.8 (the space part,
order 6, gives way to the RK4 part, order 4), non-TT and Gamma 5.9, 6.0, 6.0. Theta and Khat
stay below 4e-14 (second order in the divergence). The two models agree on amplitude and
phase to 1.2e-8 absolute at N = 16 and to 4e-11 at N = 64.

- **F2-1** (basis). At t = 0 the TT amplitudes equal amp/(2i), amp_x e^{i}/(2i) to <= 1e-10
  relative: the generator's e+, ex are gw_diag's pol_basis for (1,2,0) too (theta = pi/2).
  Refuted if > 1e-9.
- **F2-2** (TT evolution). Amplitude and phase errors of both polarizations at the last dump
  equal the table to 10 per cent at N = 32, 48, 64 and to 30 per cent at N = 16.
- **F2-3** (polarization). W_x/W_+ = 0.5 e^{i} to <= 1e-8 at every N and time.
- **F2-4** (the new sector). The mode coefficients of Gamma^i at +k from the dumps follow
  the model (abs value within 20 per cent where it is above 1e-15, the same nodes in time),
  and the non-TT part of h at +k follows the model within 30 per cent; both fall as N^-6.
  Refuted if Gamma or the non-TT part at +k is absent, does not fall with N, or is off by
  more than a factor 2 at N <= 48.
- **F2-5** (Weyl vs TT). Order-6 Weyl vs TT between |e2| and 2 |e1| of the table (test F at
  (1,1,1) measured 1.2 |e1|); spectral Weyl vs TT <= 1e-9 at every N (test F: 1.2e-11).
  The non-TT part at +k does not enter Psi_4 along khat at first order (its mbar mbar
  projection vanishes). Refuted outside these bands.
- **F2-6** (backward part). Maximum of the backward combination over time within a factor 2
  of |1 - w_h/k| (F4 reworded): 1.5e-4, 2.6e-6, 2.3e-7, 4.1e-8.
- Whole-field non-TT fraction: the second-order part seen along (1,1,1) (1.44e-4 at four
  periods, A t^2) plus the first-order part at +k above; at N = 16 both are near 1e-4.

Cost: serial processor N = 16, 32, 48 about 1, 8 and 45 minutes at 1.4e4 zone-cycles per
second; N = 64 on the card.

### XS: the time and space parts of the X error

2S predictor on the coupled background (`wlib/predict.py`, predict_flrw_coupled) at t = 10:

| N | dt_exp = 0.01 (reference) amp / phase | dt_exp = 0.001 amp / phase | 1e-4 (space part) amp / phase | time part at 0.01 amp / phase |
|---|---|---|---|---|
| 16 | -7.048e-5 / 8.304e-5 | -7.841e-5 / 7.198e-5 | -7.841e-5 / 7.198e-5 | 7.9e-6 / 1.1e-5 |
| 32 | 1.317e-6 / 3.065e-6 | -5.929e-7 / 1.146e-6 | -5.937e-7 / 1.147e-6 | 1.91e-6 / 1.92e-6 |
| 48 | 4.250e-7 / 5.879e-7 | -3.155e-8 / 1.021e-7 | -3.233e-8 / 1.024e-7 | 4.57e-7 / 4.86e-7 |
| 64 | 1.399e-7 / 2.762e-7 | -3.11e-9 / 1.917e-8 | -3.89e-9 / 1.951e-8 | 1.44e-7 / 2.57e-7 |

Steps: 3585 at every N with 0.001 (every step limited by the expansion); the time part left
at 0.001 is 7.8e-10 in amplitude and -3.5e-10 in phase at every N. The space part converges
at order 7.0-7.2 (amplitude, Kreiss-Oliger) and 6.0 (phase, the sixth-order stencil).
Background: max |a/a_ex - 1| 1.8e-11 and |alpha/a - 1| 3.3e-11 at 0.001 (4.3e-8, 6.5e-8 at
0.01).

- **XS-1** (cross polarization). With dt_expansion = 0.001 the cross-polarization errors at
  t = 10 equal the 0.001 column within 5 per cent at N = 16, 32, 48 and within 20 per cent
  (or 1e-9 absolute) at N = 64. Then the reference X errors are the time part (column 5)
  plus the space part (column 4) [the split]. Refuted otherwise.
- **XS-2** (background). Max |a/a_ex - 1| and |alpha/a - 1| <= 1e-9 (the predictor gives
  2e-11 and 3e-11; the code may add rounding). Refuted if above 1e-8.
- **XS-3** (the 2e-8 spectral-Weyl vs TT offset). If it comes from the background error
  through the calH h' term (judgement of 2026-11-19 15:50), it falls by at least a factor
  100, to <= 2e-10. Refuted (and the judgement with it) if it stays above 2e-9.
- **XS-4** (rounding of the plus polarization). The polarization-ratio error is rounding
  that accumulates per step: with 8.7 (N = 32), 6.8 (48), 5.4 (64) times more steps, |arg R|
  at t = 10 grows by a factor between sqrt(steps ratio) and steps ratio over the reference
  run at the same N (reference 2.4e-8, 6.0e-8, 1.08e-7). Refuted if it does not grow or
  grows by more than 1.5 times the steps ratio.

Runs: N = 16 and 32 on processors with the executable of the reference runs
(core/requests-b athena_cpu, sha256 c32a1389..., `scripts/run_expanding.sh` with
EXTRA="particles/dt_expansion=0.001"; it rewrites the same data, compared by checksum with
the reference data), N = 16, 32, 48, 64 on the card with the reference card executable and
the reference data (`inputs/card_r1.list`, with F2 at N = 64): card prediction about 8
minutes, <= 0.2 card-hours.
