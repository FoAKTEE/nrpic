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

## 2026-11-22 18:00 PST (lead of batch 10a): outcomes P4-P12 of series 1

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

## 2026-11-24 05:35 PST (lead of batch 11): why L2 gave no number; f = 1 run read as it is; predictions

Found by reading series 1's outputs (no new run): in L2 (beta = 0.5, HL = 4) the A rays (towards
+x) had not reached x = L by tlim = 6: at t = 6 they stood at x = 0.6 to 3.7 and |y| up to 7.9;
2 of 61 crossed (59 None in `crossing`), and `shoot` then built its window of four rays from two,
whose duplicated abscissae gave NaN in the Lagrange weights, hence NaN arrival times and the
error in `transport` (analyze_rays.py:182). The B rays all crossed at t = 3.07-3.10. Fix in
`analyze_rays.py` (batch 11): s, miss and the crossings are filtered together and fewer than four
crossings give "ok": false with the reason, instead of NaN; cases with every ray crossing give the
same numbers as before (same arrays). The cure for L2 is a later end: series 2
(`inputs/series2.txt`) runs L2 with tfac = 2.5 (tlim = 10). `run_cases.py` gains keys
"x:<block>/<name>" passed to AthenaK.

The f = 1 run S1_n64_lap1 (series 1): its guard stop came at t = 0.578, after the rays arrive in
that slicing (the f = 1/3 run has them at conformal t = 1.0, a = 2.25; with f = 1 the same events
lie near t = 0.47 if the background lapse grows as a^3 [arithmetic on the background equations,
not checked against the run]); its constraint norms stay at 1e-15 to t = 0.54 and grow by about
seven per step only in the last eight steps; the step followed the expansion limit
(dt = 0.01 a^(-3/2) from t = 0.42). So P10 can be judged on the trajectories it wrote before the
stop: the analysis is run on that directory as it is. The stop itself (RISKS R18) keeps no named
cause.

Predictions (before the runs and the analysis) [JUDGEMENT]:
- P10 (restated, unchanged): the f = 1 run gives cos(theta) equal to S1_n64 (f = 1/3) within
  1e-4 relative. Refuted above 1e-4; not judged if fewer than four rays of a fan crossed
  before t = 0.578.
- P9' (L2 with tlim = 10): every case reaches tlim; at least eight A rays and all B rays cross;
  Delta within max(3 x own error, 0.01) of CosmoGRaPH's -0.8183 (draft.tex:360) and away from
  -0.619 and -0.68 (gevolution, GRAMSES). Refuted if Delta at the finest mesh or extrapolated lies
  outside that band, or if the three meshes do not converge (differences not falling).
- P7' (S3 at N_y = 256): |Delta(256) - Delta(128)| below |Delta(128) - Delta(64)| = 3.25e-5 and
  |Delta(256)| below 3e-4. Refuted if the difference grows again (then S3 does not converge in
  N_y at this HL and the cause is to be looked for in the rays' step or the observer transport).
- Wall time: L2_n128 below 8 minutes, S3_n256 below 30 minutes (series 1: 149 s and 144 s at 128).

## 2026-11-24 05:45 PST (lead of batch 11): outcome of P10 (f = 1 against f = 1/3)

Run B-20261124-131336-bc61eee (`analyze_rays.py --plot` on a copy of series 1's S1_n64_lap1 in
its own directory; `rays.png` looked at: both fans bracket the root, gamma_xy at O on the linear
curve, constraint means at 1e-9 (H) and 1e-6 (M) until t = 0.54). [VERIFIED by this run]
- Rays arrive at t_A = 0.46913, t_B = 0.46912 in the f = 1 slicing (a = 2.2500 there; the f = 1/3
  run has them at t = 1.0000, a = 2.2500): the background estimate t = 0.469 of the entry above
  holds.
- P10 HOLDS: cos(theta) = 1.431017e-3 (f = 1) against 1.431142e-3 (f = 1/3), relative difference
  -8.7e-5, inside the 1e-4 of the prediction. Delta = -1.050e-4 (f = 1) and -1.77e-5 (f = 1/3) at
  N_y = 64; the difference is six times the f = 1/3 run's error at that mesh (1.4e-5 against its
  extrapolation), so the f = 1 run carries the larger error; it has no convergence series.
- Not predicted, on record: k_x, k_z of the rays drift by 3.6e-3 of |k| over the whole stored
  track (6e-15 with f = 1/3); the track runs into the last steps before the guard stop, where the
  fields blow up, and the drift was not restricted to t < 0.54 [TO VERIFY before quoting it].
- The guard stop at t = 0.578 keeps no cause (R18); it does not touch the observable.

## 2026-11-24 06:20 PST (lead of batch 11): L2 of series 2 read; series 3 predicted

Series 2 = run B-20261124-133702-4a06a52 (L2 cases ended; S3_n256 still running when this was
written). Read from `L2_n*/rays.json` (the summary script runs when S3 ends):
- Every L2 case reached tlim = 10 (wall 22, 67, 267 s); 13, 14, 14 of 61 A rays and all 61 B rays
  crossed (P9' part "at least eight A rays": HOLDS). Roots: s_A = -0.920, -0.919, -0.922 and
  s_B = 0.1997, 0.2011, 0.2015 at N_y = 32, 64, 128; arrival t_A = 6.55-6.56, t_B = 3.08-3.09
  (a about 9.9 at the end).
- Delta (cubic shooting) -0.179, -0.159, -0.322; Delta (quadratic) -0.717, -0.672, -0.732. The two
  interpolations of the same fan differ by 0.4-0.5: the A fan (spacing 0.078 in s) moves the miss
  by 1 to 2.3 per ray, and t and k interpolated across four or three rays at the root disagree
  (t_A 6.545 against 6.710 at N_y = 64). P9' NOT JUDGED: series 2 gives no reliable number.
  Design error, recorded: the fan was widened for the root (series 1) but not refined for the
  interpolation.
- Series 3 (`inputs/series3.txt`): the same cases with absolute fans about the roots, A -0.92 +-
  0.04 with 41 rays (spacing 0.002), B 0.200 +- 0.01 with 21 rays (spacing 0.001).

Predictions for series 3 [JUDGEMENT], before it runs:
- P9''a: at every N_y the A and B roots lie inside the fans, and the cubic and quadratic
  shootings give Delta within 1e-3 of each other. Refuted otherwise (then the miss function is
  not smooth at that scale, e.g. several images).
- P9''b: Delta converges in N_y (|Delta(64) - Delta(128)| < |Delta(32) - Delta(64)|).
- P9 (unchanged from 2026-11-20): Delta within max(3 x own error, 0.01) of CosmoGRaPH's -0.8183
  (draft.tex:360) and away from -0.619 and -0.68. Refuted if the extrapolated Delta lies outside.

## 2026-11-24 06:50 PST (lead of batch 11): outcomes of series 2 (S3 at 256) and series 3 (L2)

Runs: series 2 B-20261124-133702-4a06a52 (closed, completed), series 3 B-20261124-134209-4584052
(closed, completed; 22, 67-ish, 263 s), summary B-20261124-134720-c753aff (`series2_summary.py
--l2 <series 3>:L2f`; `results/series2_3.json`, `figs/fig_series2.png` looked at). [VERIFIED by
these runs]

L2 (beta = 0.5, HL = 4), narrow fans (series 3):
- P9''a HOLDS: every root inside its fan (s_A = -0.9255, -0.9230, -0.9235; s_B = 0.1997, 0.2011,
  0.2015), all 41 A and 21 B rays cross, and the cubic and quadratic shootings agree to 2.0e-4,
  2.6e-4, 7.5e-4 in Delta.
- Delta = -0.8281, -0.8302, -0.8348 at N_y = 32, 64, 128 (cos theta = 0.0866, 0.0855, 0.0832
  against the linear 0.5037).
- P9''b FAILS: the differences grow (2.1e-3, then 4.6e-3; observed order -1.2), so there is no
  extrapolation (the p = 2 value, -0.836, is only a placeholder of the script).
- P9 FAILS by its letter: distance to CosmoGRaPH's -0.8183 is 0.0098, 0.0119, 0.0165 (only the
  coarsest mesh inside 0.01) and grows with N_y. The value lies 0.2 below gevolution (-0.619) and
  0.15 below GRAMSES (-0.68): it sides with CosmoGRaPH, the fully relativistic code of the
  comparison, at the 1-2 per cent level.
- Not predicted, on record: the parallel transport of the B covector along the observer from
  t_B = 3.08 to t_A = 6.5 moves Delta by -0.0044, -0.0132, -0.0265 at N_y = 32, 64, 128 (Delta
  without it: -0.8237, -0.8169, -0.8083), i.e. the non-convergence sits in the observer's metric
  history between the two arrivals; whether stream crossing near O (P9 of 2026-11-20: crossing
  at a = 9 to 16) or the transport integration causes it is not tested [TO VERIFY]. Series 2's
  coarse fan (no reliable number) is superseded.
S3 (beta = 0.005, HL = 4) over N_y = 32-256:
- Delta = -5.65e-5, -3.32e-5, -6.8e-7, +2.01e-5; differences 2.33e-5, 3.25e-5, 2.08e-5.
  P7' HOLDS by its letter (|Delta(256) - Delta(128)| = 2.08e-5 below 3.25e-5; |Delta(256)| below
  3e-4) but S3 does not converge: the differences stay at 2-3e-5, a floor of that size, two
  orders below the paper's 3e-4 bound (draft.tex:348).
Figure defects: overlapping tick labels on the N_y axis of the S3 panel; the L2 panel's
extrapolated star rests on a forced order.

## 2026-11-24 07:00 PST (lead of batch 11): where L2 stops converging; prediction

Seen in series 3's rays.json while summarising: up to the A arrival the constraint means of L2 at
N_y = 64 reach Hr_mean 0.38 and Mr_mean 0.32 (`cstat_max_to_arrival`). `scripts/l2_observer.py`
tabulates, per N_y, the constraint means at t_B and t_A, the observer's metric at O at both
times, and their differences between meshes. Prediction [JUDGEMENT]: the constraint means at t_A
exceed 0.1 at every N_y and do not fall with N_y (the dust crosses streams before the A rays
arrive, P9 of 2026-11-20), and h_xy at O at t_A differs between meshes by more than at t_B, the
mesh difference growing 32-64 to 64-128 like Delta does. Refuted if the means at t_A fall by two
or more per doubling (then the non-convergence is not in the field at O).

Outcome (run B-20261124-135244-17ebf5c, `figs/fig_l2_observer.png` looked at) [VERIFIED by it]:
- HOLDS in its first part: at t_A the relative constraint means are Hr 0.40, 0.24, 0.25 and Mr 0.26,
  0.18, 0.15 at N_y = 32, 64, 128, above 0.1 everywhere and not falling by two per doubling (Hr
  rises from 64 to 128). They climb to 0.05-0.3 already by t = 1 (a = 2.25) at every mesh and stay
  there: L2's field carries a 10-40 per cent constraint violation over the whole interval between
  the arrivals.
- Second part mixed: h_xy at O at t_A differs by 0.042 (32-64) then 0.106 (64-128), growing as
  Delta does; at t_B the differences are 0.072 and 0.066, so the field at O is not better
  converged at t_B than at t_A for 32-64. h_xy at O shows kinks at t = 3.1, 5.4 and 8.2 (streams
  crossing at or near O [JUDGEMENT from the shape]).
- What this says about R19: the L2 values (-0.828 to -0.835) are taken in a field whose
  constraints are violated at 10-40 per cent and do not converge with N_y; the number is not a
  converged statement of this code. No cause of the violation is named; a run that could show it
  (a smaller step, more particles per cell along y, or a lower amplitude between M2 and L2) is the
  next step.

## 2026-11-24 07:10 PST (lead of batch 11): series 4, where L2's constraint violation comes from; prediction

Series 4 (`inputs/series4.txt`): L2 at N_y = 64 with series 3's fans, (a) half the step (cfl
0.125, dt_expansion 0.005), (b) four particles per cell along y. Prediction [JUDGEMENT]: neither
lowers the relative constraint means over 1 <= t <= t_A by more than 30 per cent against series
3's L2f_n64 (Hr_mean at t_A 0.237, Mr_mean 0.175), and Delta moves by less than the 32-64
difference of series 3 (2.1e-3): the violation comes from the dust itself (streams crossing at
the grid scale), not from the step or the particle sampling. Refuted if either halves the means
(then that is the cause to pursue).

Outcome of series 4 (run B-20261124-135516-34befaf; read from rays.json against series 3's
L2f_n64) [VERIFIED by it]:
- Half the step: Delta -0.83009 (series 3: -0.83017, change 8e-5); mean Hr and Mr over
  1 <= t <= t_A 0.142 and 0.149 (0.154, 0.146). The step is not the cause: HOLDS.
- Four particles per cell along y: Delta -0.82180 (change +8.4e-3, four times the 32-64 mesh
  difference); means 0.146 and 0.127 (down 5 and 13 per cent). The means part HOLDS (not halved);
  the Delta part is REFUTED: the particle sampling along y moves L2's number more than the mesh
  does, and toward CosmoGRaPH's -0.8183 (0.0035 from it).
- So the non-convergence of series 3 at one particle per cell is at least partly particle
  sampling [VERIFIED for N_y = 64 by this pair]; the constraint violation of 0.1-0.4 is not
  (it barely moves with either).

## 2026-11-24 07:20 PST (lead of batch 11): series 5, particle number at L2; prediction

Series 5 (`inputs/series5.txt`): L2 with series 3's fans at N_y = 64 with 2 and 8 particles per
cell along y, and at N_y = 128 with 4. Prediction [JUDGEMENT]: Delta converges in the particle
number at N_y = 64 (|Delta(8) - Delta(4)| < |Delta(4) - Delta(2)|, and below 3e-3), and at 4 per
cell N_y = 128 lies within 5e-3 of N_y = 64; the converged value lies within 0.01 of CosmoGRaPH's
-0.8183. Refuted if Delta(8) - Delta(4) is not smaller than Delta(4) - Delta(2).

Outcome of series 5 (run B-20261124-135951-237e27b; summary B-20261124-140808-e6ba5c3,
`figs/fig_ppc.png` looked at; the y label is cut at the left edge) [VERIFIED by these runs]:
- At N_y = 64, Delta = -0.83017, -0.82327, -0.82180, -0.82082 for 1, 2, 4, 8 particles per cell
  along y: differences 6.9e-3, 1.5e-3, 1.0e-3. Converges in particle number: HOLDS (8 - 4 below
  4 - 2, and below 3e-3). Linear in 1/n at the two largest n puts the limit near -0.820, 0.002
  from CosmoGRaPH's -0.8183 [arithmetic on these runs].
- At 4 per cell N_y = 128 gives -0.83123, 9.4e-3 below N_y = 64: the "within 5e-3" part FAILS. The
  mesh dependence remains at fixed particles per cell, away from CosmoGRaPH; the constraint means
  (Hr 0.135-0.15, Mr 0.12-0.15 over 1 <= t <= t_A) move little with either.
- The converged-value part of the prediction is therefore not judged: the particle limit at
  N_y = 64 sits beside CosmoGRaPH, the mesh limit is open.

## 2026-11-24 07:35 PST (lead of batch 11): series 6, the mesh leg at 4 particles per cell; prediction

`inputs/series6.txt`: L2 at N_y = 256 with 4 per cell along y. Prediction [JUDGEMENT]: the mesh
dependence at fixed particles per cell slows: |Delta(256) - Delta(128)| below the 64-128
difference 9.4e-3 (Delta(256) between -0.840 and -0.832). Refuted if the difference is as large
or larger (then L2 does not converge in the mesh at this amplitude, and the constraint violation
is the first suspect).

Outcome of series 6 (run B-20261124-140856-911ded9, 27 min on one core; summary
B-20261124-172643-d1e88c7, `figs/fig_ppc.png` panel (b) looked at) [VERIFIED by these runs]
(written 2026-11-24 09:30 PST, resumed session of batch 11b; the prediction was committed in
911ded99 before the run was registered at that commit):
- Delta(256, 4 per cell) = -0.83915 (quadratic shooting -0.83898). Mesh differences at 4 per cell:
  64-128 9.4e-3, 128-256 7.9e-3. The prediction HOLDS as written (7.9e-3 < 9.4e-3; -0.8392 inside
  -0.840 to -0.832), but only just: the ratio 0.84 is an order of about 0.25, and a geometric
  series with that ratio would put the mesh limit near -0.88 [arithmetic on these three numbers,
  not a claim]. Each refinement moves Delta away from CosmoGRaPH's -0.8183 (draft.tex:360).
- At one particle per cell the mesh differences grow (32-64 2.1e-3, 64-128 4.6e-3).
- Relative constraint means over 1 <= t <= t_A at 4 per cell: Hr 0.146, 0.135, 0.131 and Mr 0.127,
  0.123, 0.119 at N_y = 64, 128, 256: they barely move with the mesh.
- Reading [JUDGEMENT]: L2 of this code does not converge in the mesh at practical resolutions;
  the particle limit at N_y = 64 (about -0.820, next to CosmoGRaPH) is therefore not a converged
  statement, and the agreement with CosmoGRaPH there may be a coincidence of one mesh. No cause is
  named: the first suspect stays the stream crossing before the A rays arrive (constraint
  violation of 10-15 per cent that does not fall with the mesh); the run that could refute it is
  an amplitude between M2 and L2 at which no stream crosses before t_A, at N_y = 64, 128, 256 with
  4 per cell (prediction to be written before it is queued). The track reports L2 as
  "not converged in this code" and uses S1-S4, M1 and L1 (which converge or sit inside the
  paper's bounds) for the weak-field comparison.
