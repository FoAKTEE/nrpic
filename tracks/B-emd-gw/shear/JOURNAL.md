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

## 2026-11-20 22:34 Outcomes P1-P3 (run B-20261120-223409-29c92ec)

- P1 MET [VERIFIED]: rays shot through the linear solution reproduce draft.tex:262 to
  at most 5.3e-13 relative at HL = 2^-7 ... 4, in the code's and in the paper's
  coordinates; my first-order integrals (cos = s_A + s_B - h(tau_* + L, 0)) to 3e-14
  (`results/ref_table.json`, `figs/ref_table.png`, looked at). The closed form is thus the
  first-order observable for the observer at rest at O with the events of draft.tex:224,
  propagation directions +x (A) and +y (B). Linear launch slopes of the cases:
  `results/ref_table.json` "cases" (e.g. S1: s_A = -2.222e-3, s_B = +1.349e-4).
- P2 MET [VERIFIED]: 24 tests pass (`pytest.log` of the run): flat Ricci tensor of the
  slice, gamma' = delta and K' of SPEC section 2, both constraints identically with
  rho0*, u*^x, W^2 = 1 + u_x^2, rho_ADM of draft.tex:515; the paper's linear solution
  matches the slice at first order and has alpha = gamma^(1/6) at first order (f = 1/3),
  its transform is SPEC's gamma'_xy, and it satisfies draft.tex:254 with B_x of 246.
- P3 MET [VERIFIED]: written fields equal the analytic ones exactly; spectral constraint
  residuals 1.5e-16 (H) and 1e-15 to 2.5e-14 (M, growing with N_y as rounding of the
  derivative); own pcs deposit of the particles: momentum residual 6.4e-3 at N_y = 32 raw
  (second order), 4.1e-5, 2.6e-6, 1.6e-7, 1.0e-8 at N_y = 32, 64, 128, 256 with one
  compensation pass 1/6 (ratio 15.9-16.0: fourth order); identical relative residual
  for S1 and L2 because 8 pi S_x = -(3 pi b/(2L^2)) sin(2 pi y/L) is a pure sine for every
  b (`results/check_ic.json`, `figs/check_ic.png`, looked at).

## 2026-11-20 22:35 Smoke run failed; PAUSED

- Smoke run B-20261120-223445-3686145 (S1, N_y = 32, release processor executable):
  AthenaK stopped at start, "Parameter name 'probe1_x1' not found in block 'particles'"
  (`S1_n32/athena.log`): the deck has nprobe = 1 without the probe1_* lines. Fix for the
  restart: set `nprobe = 0` in `inputs/shear.athinput` (the probe is not needed; the
  observer tracer records alpha and gamma_ij at O), then resubmit the smoke run.
  The submit went out in the same shell command as the pause check, which had already
  found the flag (my error: `;` instead of `&&`); the run died in 2 s.
- The pause flag /data/haiyangw/nrpic/locks/PAUSE exists (written 22:33 UTC, five-hour
  window at 97 per cent). Stopped here: nothing new started after this entry.
- Where to continue: (1) fix nprobe, smoke run, look at `S1_n32/rays.png`;
  (2) the series lists (S1-S4, M1-M2, L1-L2 at N_y = 32, 64, 128; legs ppc_y = 2, 4 and
  lapse_harmonic = 1 at S1 N_y = 64); (3) for M2, L1, L2 a wide fan first (linear slopes
  are far off at beta = 0.5); (4) summary script with Richardson extrapolation and
  figures; (5) outcomes P4-P12, README. No card job submitted (the owner had two queued).

## 2026-11-21 12:32 PST (lead of batch 5): deck fix; smoke run again; predictions

- Deck fix as the entry above asks: `nprobe = 0` in `inputs/shear.athinput` (nothing else
  changed). Executable from now on: the release core-v0.6 processor build
  `/data/haiyangw/nrpic/.work/build_cpu_v06/src/athena` (new series; given with --exe).
- Prediction of the smoke run S1_n32 (before it runs): AthenaK reaches tlim = 1.5 (exit 0,
  no guard stop); `rays.json` is written; cos(theta) within 10 per cent of the linear
  value 1.4312e-3 of `results/ref_table.json` (a 32-cell mesh, one resolution: P4-P7 are
  judged on the series, not here). Refuted if the run stops, or the observable differs from
  the linear value by more than a factor 2 (then the fan or the reader is wrong, not the
  mesh).

## 2026-11-21 12:40 PST (lead of batch 5): smoke run outcome; series 1 submitted

- Smoke run B-20261121-202359-d12511c (S1, N_y = 32, release v0.6 processor build): exit 0,
  10 s; cos(theta) = 1.43108e-3 against the linear 1.43117e-3, Delta = -6.32e-5; ray k_x,
  k_z drift 2.8e-15, tracer u_x, u_z drift 7.3e-13; alpha/a_O 2.7e-10 (`S1_n32/rays.json`).
  Prediction (within 10 per cent of linear) MET. One resolution only: no claim on P7.
- Series 1 = `inputs/series1.txt` (27 cases: S1-S4, M1-M2, L1-L2 at N_y = 32, 64, 128;
  legs S1_n64_lap1, _ppc2, _ppc4), one local run, 4 at a time. Predictions: P4-P12 above,
  unchanged; for L1 and L2 the fans are wide (relative half width 1.5, 61 rays) because the
  linear slopes are not expected to bracket the root at beta = 0.5. Additional prediction:
  every case reaches tlim (no guard stop) and the wall time is below 15 minutes per case
  (smoke: 10 s at N_y = 32; cost proportional to N_y^2 at fixed HL).
- Then: a summary script (Richardson extrapolation per case, figures) and outcomes P4-P12.

## 2026-11-21 12:47 PST: series 1 failed at the initial data; fixed, resubmitted

- Run B-20261121-202503-abdf6f0 FAILED before any AthenaK process started: make_shear_ic.py
  refused `--fanA -0.1555...,0.5,21` (argparse reads a value that begins with "-" as an
  option; `M2_n32/ic.log`). My error in run_cases.py, not in the list. Fix: the fan is passed
  as `--fanA=<value>`. Predictions of the entry above unchanged; series 1 resubmitted as is.

## 2026-11-21 12:58 PST (lead of batch 5): series 1 ended (raw outcome, not analysed)

Run B-20261121-202830-417af0c, closed by the sequencer as failed (exit 1 because one case
failed). 26 of 27 AthenaK runs reached tlim (wall 10-150 s each). Failed: S1_n64_lap1
(lapse_harmonic = 1) stopped by the guard at t = 0.578, cycle 175 (non-finite Khat in 22
cells; nine cells with a non-positive metric determinant at t = 0.576 before it): prediction
P10 cannot be judged; cause not established (RISKS R18). Ray analysis failed (analyze_rc = 1)
for L2_n32, L2_n64, L2_n128: NaN in the transport step of analyze_rays.py (line 182), i.e. no
arrival time for the wide fan at beta = 0.5, HL = 4; not yet looked into. P4-P9, P11, P12
wait for the summary script (Richardson per case, figures).

## 2026-11-22 18:06 PST (lead of batch 10a): outcomes P4-P12 of series 1

Summary run B-20261123-015919-dec4392 (`scripts/summarize_series.py` on series 1 =
B-20261121-202830-417af0c; `results/series1_summary.{json,txt}`, `figs/fig_series.png`
looked at: |Delta| against N_y with the extrapolated values dashed, the t = 0 momentum
constraint with an N^-4 guide, the constraint means up to the arrival of the rays).
Richardson: observed order p from the two differences of cos(theta) over N_y = 32, 64, 128;
extrapolation with p when 1 <= p <= 6, else with p = 2. [VERIFIED by these runs]

| family | HL | beta | Delta 32 / 64 / 128 | p_obs | Delta extrapolated | error at 128 |
|---|---|---|---|---|---|---|
| S1 | 1 | 0.005 | -6.32e-5 / -1.77e-5 / -6.99e-6 | 2.08 | -3.68e-6 | -3.3e-6 |
| S2 | 1/16 | 0.005 | -5.97e-6 / -9.46e-7 / -2.35e-7 | 2.82 | -1.18e-7 | -1.2e-7 |
| S3 | 4 | 0.005 | -5.65e-5 / -3.32e-5 / -6.83e-7 | -0.48 (p = 2 used) | +1.02e-5 | -1.1e-5 |
| S4 | 1/128 | 0.005 | -3.19e-6 / -2.28e-7 / -1.14e-8 | 3.77 | +5.8e-9 | -1.7e-8 |
| M1 | 1 | 0.05 | -4.07e-4 / -3.58e-4 / -3.47e-4 | 2.12 | -3.43e-4 | -3.4e-6 |
| M2 | 4 | 0.05 | +3.34e-3 / +3.40e-3 / +3.43e-3 | 1.22 | +3.45e-3 | -2.0e-5 |
| L1 | 1 | 0.5 | -1.22e-2 / -6.06e-3 / -5.17e-3 | 2.78 | -5.02e-3 | -1.5e-4 |
| L2 | 4 | 0.5 | no result (ray analysis NaN at every N_y) | | | |

- P4 MET for the momentum constraint, FAILED for the Hamiltonian constraint: Mr_mean at t = 0
  1.54e-6, 9.25e-8, 5.72e-9 (ratios 16.7, 16.2, the same in every family) and 1.5e-6 <= 1e-4
  at N_y = 32; Hr_mean at t = 0 falls by 8.5 and 14.3 per doubling (S1 1.60e-11, 1.88e-12,
  1.31e-13; L1 the same ratios), below the predicted 16; S4 sits at rounding (2e-16).
- P5 MET: ray k_x, k_z drift at most 8.8e-15 of |k|; tracer u_x, u_z at most 6.6e-12 relative.
- P6 MET: S1 at N_y = 128, gamma_xy at O within 1.25e-5 of the linear solution (relative to
  its largest value) until the rays arrive; alpha/a_O - 1 at most 2.9e-11.
- P7 MET for S1, S2, S4; FAILED in part for S3: every extrapolated Delta lies within +-3e-4
  (largest 1.0e-5, S3) and every error at 128 below 3e-4 (largest 1.1e-5, S3); the observed
  order is 2.08, 2.82, 3.77 for S1, S2, S4 (within 1.5-4.5) but not defined for S3 (HL = 4):
  the differences grow, 2.33e-5 then 3.25e-5, so S3 does not converge monotonically over
  32-128 and its extrapolation (p = 2 assumed) is not reliable.
- P8: M1 MET (Delta -3.43e-4, |Delta| <= 1e-3). M2 FAILED in sign: Delta = +3.45e-3, positive
  (predicted negative, "my guess"); the size < 1e-2 holds; slow convergence (p = 1.22).
- P9: L1 MET (Delta -5.02e-3, |Delta| <= 1e-2, p = 2.78, error at 128 1.5e-4). L2 NOT JUDGED:
  the analysis fails at every mesh (NaN arrival time in the transport step,
  analyze_rays.py:182); cause not looked into.
- P10 NOT JUDGED: S1_n64_lap1 (f = 1) stopped by the guard at t = 0.578 (entry of 2026-11-21
  12:58); no cause named.
- P11 MET: 2 and 4 particles per cell along y give cos(theta) within 1.5e-7 and 1.4e-7 of one
  per cell (predicted 1e-5).
- P12 MET in size, FAILED in convergence for S2, S3, S4: up to the arrival of the rays every
  beta = 0.005 case keeps Hr_mean and Mr_mean below 1e-4 (largest Mr_mean 5.7e-5, S3 at 32);
  they fall by >= 4 per doubling only for S1 (Mr 7.3, 4.1; Hr 4.0, 4.0). S3 falls more slowly
  (Mr 5.5, 3.1; Hr 1.9, 4.2); in S2 (HL = 1/16) and S4 (HL = 1/128) both means RISE with N_y
  (S4: Mr 3.2e-6, 1.1e-5, 5.5e-5; Hr 9.6e-9, 3.3e-8, 1.4e-7), at levels where round-off in
  second differences could matter [TO VERIFY; no run has tested it].

What the comparison with the paper's codes stands on now: the small-amplitude cases agree with
linear theory to 1e-5 or better after extrapolation, M1 and L1 lie inside the paper's bounds
(draft.tex:383); the decisive case L2 (CosmoGRaPH -0.8183, draft.tex:360) has no number yet.
Next: L2 (why the fan gives no arrival: look at `L2_n64/rays.json` miss values and the
trajectories), the f = 1 guard stop (processor diagnosis at N_y = 32), S3 at N_y = 256 to
settle its order. Figure defects: the y label of panel (a) is cut at the top; the legend of
panel (a) covers part of the S curves.
