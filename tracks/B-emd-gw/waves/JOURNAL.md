# JOURNAL of the waves package (B-emd-gw, wave 2b): G1 criterion 1

Linear gravitational waves with both diagnostics of gw_diag, against analytic solutions,
with measured convergence. Helper session of 2026-11-19. Times UTC.

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

## 2026-11-19 14:30 Design of the two tests [JUDGEMENT]

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

## 2026-11-19 14:40 Derivation of the closed form (wlib/weylref.py)

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

## 2026-11-19 14:25 Predictions of tests F and X (before any run of either test)

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
