# JOURNAL of the shear package (B-emd-gw, wave 3 round 1): G2 multi-code row

The shearing-dust test of arXiv:2003.08014 v2 with AthenaK particles (decision 0013).
Helper session of 2026-11-20. Times UTC (from `date -u`). Specification: `SPEC.md`.

## 2026-11-20 22:15 Start; what exists

- `tracks/B-emd-gw/shear/` did not exist (no partial work of an earlier session).
  Worktree at c9aba208 (PLAN-wave3 round 1). No merge run (task rule for helpers).
- Read: CLAUDE.md, harness/RULES.md (nrpic-run), decisions 0010 and 0013,
  `verify_cosmo/VERIFY.md` section 3, draft.tex lines 100-557, cosmo/README.md,
  `nrpic_cosmo.cpp`, `cosmo/ic/nrp_io.py`, `ray_ic.py`, `cosmo/analysis/ray_obs.py`,
  `ray_test_flrw.py`, `constraint_field.py`, the lapse code of `z4c_calcrhs.cpp`
  (694-708), the null-particle launch (`nrpic.cpp` 450-480), the trajectory output
  (`nrpic_io.cpp` 800-935), READY of core_requests-b (item 4) and core_build-openmp.
- Executables: release core-v0.3 processor build `.work/build_cpu_v03/src/athena`
  (production kind); threaded `scratch/core/exe/core_build-openmp/athena_cpu` if needed.

## 2026-11-20 22:30 Design [JUDGEMENT] and predictions (before any run)

Design (details in SPEC.md sections 2-6): sheared-Euclidean slice rewritten with
x' = x + (b/(2 pi H)) sin(2 pi y/L): psi = 1, K = -3H, alpha = 1,
Ahat_xy = (3b/(4L)) cos(2 pi y/L); particles on a lattice with masses D(y) Delta V and
u_x = u*^x(y); a tracer observer at O; two fans of null rays from O (towards +x: ray A;
towards +y: ray B); cos(theta) at O after shooting by interpolation over each fan.
Thin box 4 x N_y x 4. Cases S1-S4 (beta = 0.005, HL = 1, 1/16, 4, 1/128), M1-M2
(beta = 0.05, HL = 1, 4), L1-L2 (beta = 0.5, HL = 1, 4); N_y = 32, 64, 128.

Predictions, each with what refutes it:

- P1 (reference). My own linear ray tracing through the linear solution of SPEC section 3
  (shooting, observer at rest at O) reproduces cos(theta_lin) of draft.tex:262 to 1e-6
  relative at HL = 2^n, n = -7 ... 2, and the formula has the limits 3b/4 and 2b/(HL)^2
  (draft.tex:265). Refuted if any HL differs by more than 1e-4 relative (my reading of
  the events, the observer or the sign would then differ from the paper's).
- P2 (symbolic). The slice of draft.tex:149-158 has zero Riemann tensor; the transformed
  data of SPEC section 2 satisfy both constraints identically with rho0*, u*^x of
  draft.tex:177-182; the paper's linear solution (draft.tex:237-241) matches the initial
  slice at first order in b and has alpha = gamma^(1/6) at first order. Refuted by any
  nonzero symbolic residual.
- P3 (written data). Constraint residuals of the written fields with spectral derivatives
  and the analytic matter: at rounding (relative 1e-14). With an own PCS deposit of the
  written particles (compensation 1/6, 7/15) the momentum residual relative to 8 pi S_x
  falls by >= 16 per doubling of N_y (fourth order or faster).
- P4 (code at t = 0). The code's cstat at t = 0: Mr_mean and Hr_mean fall by >= 16 per
  doubling of N_y (fourth order or faster), and Mr_mean <= 1e-4 at N_y = 32 for S1.
- P5 (exact conservation). u_x of every tracer and k_x, k_z of every ray stay at their
  launch values to 1e-10 relative for the whole run (x, z Killing). Refuted by a drift
  above 1e-10.
- P6 (metric). For S1 the tracer at O records gamma_xy(t) = a^2 (b/L)[(2/tau)^3 - 1]
  (SPEC section 3, tau = t_c + 2) to 1e-3 relative at N_y = 128 until the rays arrive, and
  alpha = a to 1e-6 (the linear lapse has no first-order perturbation).
- P7 (small amplitude). For beta = 0.005 (S1-S4) the Richardson-extrapolated
  Delta = cos(theta)/cos(theta_lin) - 1 lies within +-3e-4 (draft.tex:348); the numerical
  error at N_y = 128 (finest minus extrapolated) is below 3e-4; the observed order from
  32-64-128 lies between 1.5 and 4.5 (I expect about 2, from the midpoint pusher of the
  rays: relative error of the deflection about (k dt)^2 with dt = L/(4 N_y)). S4
  (HL = 1/128, cos(theta) of order 2e-7) may be limited by rounding: refuted for S4 only if
  |Delta| > 3e-4 at every N_y.
- P8 (moderate). M1: |Delta| <= 1e-3 (draft.tex:383). M2: Delta negative, |Delta| < 1e-2
  (draft.tex:354, sign: the HL = 4 departures of the paper are negative at beta = 0.5,
  draft.tex:360; for beta = 0.05 the sign is my guess).
- P9 (large). L1: |Delta| <= 1e-2 (draft.tex:383). L2: Delta within max(3 x own error,
  0.01) of CosmoGRaPH's -0.8183 +- 0.0004 (draft.tex:360), and clearly away from -0.619
  and -0.68 (gevolution, GRAMSES). The least certain prediction (relativistic dust with
  W of order 2, stream crossing, a = 9 to 16 before the rays arrive).
- P10 (gauge). S1-type case at N_y = 64 with lapse_harmonic = 1 (f = 1): cos(theta)
  equal to the f = 1/3 run within the numerical error of the series (<= 1e-4 relative).
- P11 (particles per cell). S1 at N_y = 64 with 1, 2, 4 particles per cell along y: cos(theta)
  equal to 1e-5 relative (a lattice in smooth fields; particle number is not the
  limiting error).
- P12 (constraints in time). For beta = 0.005 the cstat Hr_mean and Mr_mean stay below 1e-4
  up to the arrival of the rays and fall by >= 4 per doubling of N_y.
