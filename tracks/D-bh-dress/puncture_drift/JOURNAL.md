# JOURNAL of the package puncture_drift (D-pre-4, tracks/D-bh-dress/puncture_drift)

Append-only, newest at the bottom. Predictions are written before a run, outcomes after,
also when a prediction fails.

## 2026-11-15T12:25Z  helper (D-pre-4)  before any run

did: read CLAUDE.md, coord/CHARTER.md to "Owners", decision 0010, the brief by the ranges
of the task (30-68, 232-238, 279-313, 394-405, 766-783, 834-860), the paper's
"Numerical methods" (paper/sections/method.tex:193-203) and its setup tables
(paper/sections/tables/tab_setups.tex, row "Vacuum black hole"), docs/TESTLOG.md:81-89,
191-223, 310-385, 457-470, the finder source (athenak/src/z4c/fastflow.cpp:57-140,
425-520, 740-830, 1354-1380; z4c_tasks.cpp:335-356) and the lead's SCOPE.md section 5
(D-pre-4 criterion: |M_AH(t)/M_AH(t_0) - 1| for t_0 = 50 M to t_0 + 450 M at M/8 and M/16).

What exists before this package [VERIFIED, docs/TESTLOG.md]:
- Corrected finder (`metric_drvts = interpolant`) on the dx = M/8 slice: 1.000044,
  1.000189, 1.000323 at t = 8, 10, 11.5 M (GPU, :459-460); 1.001338 at t = 50 M (CPU
  restart, :351, :372). On the M/16 slice at t = 50 M: 0.999738 (:376).
- Misner-Sharp mass of the slice at t = 50 M: 1.0015 to 1.0017 (M/8), 1.000014 (M/16),
  slice error 3.9e-2 at M/4 (:354-355, :375, :384-385). Finder minus slice at production
  settings about -3e-4 at both resolutions, of which 6e-5 stopping tolerance and 1.8e-4
  the 16-point angular grid (:381-383).
- No long run with the corrected finder exists; the only long run (runs/puncture/single_v3,
  250 M at M/8) used the defective finder (:197-205, withdrawn :363-365).
- The finder reports the Christodoulou mass sqrt(M_irr^2 + S^2/(4 M_irr^2)) with
  M_irr = sqrt(A/16 pi) (fastflow.cpp:761, :821) and a spin S from the flat-space
  coordinate rotation vectors about the search centre (fastflow.cpp:1356-1376). Exact
  Schwarzschild has S = 0, and the mesh and data are reflection-symmetric about the three
  coordinate planes (the six tracers carry no mass), so any S is numerical.

Plan (card budget 3 card-hours):
- G1: `inputs/drift_dx8.athinput`, release card executable
  `.work/build_gpu_c3/src/athena`, chained, to t = 500 M; one segment (MAX_SEGMENTS = 1).
  Expected cost from the measured 4.71-5.0 s per M (runs/puncture/hcal/dx8_*/athena.log):
  2400-2500 s, 0.7 card-hours.
- G2: `inputs/drift_dx16.athinput`, same, to t = 500 M; two segments (MAX_SEGMENTS = 2).
  Expected 11.46 s per M (runs/puncture/hcal/dx16/athena.log): 5730 s, 1.6 card-hours; if
  the rate is 5 percent worse the run ends near 490 M at the cap.
- Hard cap 3 segments x 59 min = 2.95 card-hours.
- P (processors): every restart dump (every 50 M) re-searched on the processor executable
  with other finder settings: tight stopping (1e-9, 4000 iterations), a start from outside
  (2 M), and a finer angular grid (32 points, l_max 16). Also now, on the dumps that exist
  (runs/puncture/hcal/{dx4,dx8_tight,dx16}/rst at t = 50, 60 M; made with the defective
  finder, but the finder does not act on the evolution, so the slices are valid).
- Misner-Sharp mass of every dump (analysis/diag/slicemass.py, --no-fig) as a
  finder-independent measure.

Predictions, written before any of these runs:

P1 (M/8 drift). Between t_0 = 50 M and 500 M the M/8 finder mass at production settings
changes by at most 3e-3 in total, and its mean rate over 250-500 M is below 2e-6 per M
(the slice excess of 1.5e-3 at 50 M comes from the gauge transient at the puncture,
TESTLOG:467-470, and I expect it to saturate rather than grow on). Refuted by a total
change above 3e-3 or a late rate above 2e-6 per M.

P2 (M/16 drift). |M(500) - M(50)| <= 1e-4 at M/16, mean |dM/dt| <= 2e-7 per M.
Refuted by more.

P3 (resolution). |Delta M| over 50-500 M falls from M/8 to M/16 by a factor >= 8 (order
>= 3; the slice error at t = 50 M fell by 100 between these resolutions). Refuted if the
factor is below 4: the drift would then not be set by the resolution at the hole (outer
boundary, finder, or round-off would be the floor).

P4 (outer boundary). The mesh boundary at 128 M uses outflow conditions on a 4 M root
grid. The outgoing gauge pulse (speed about sqrt(2) for 1+log far out) reflected there
returns to the hole near t = 2 x 128 / sqrt(2) = 180 M, light-speed modes near 256 M. If
a feature appears in M(t) between 170 and 270 M with the same size at both resolutions,
the floor of the null test in this configuration is the boundary, not the hole. I expect
such a feature below 1e-4 at M/16 [JUDGEMENT]; refuted if it is larger.

P5 (spin). |S|/M^2 < 1e-6 at all times after t = 5 M, at both resolutions, and smaller
at M/16. (The defective finder gave 1e-6 at M/8 and 8.8e-6 at M/16, single_v3 and
hcal/dx16 summaries; I attribute that to the defect.) Refuted if |S|/M^2 > 1e-5 after
the transient.

P6 (finder settings). On the same slice, tight stopping moves the mass by 3e-5 to 1e-4,
the 32-point grid by 1e-4 to 3e-4 (TESTLOG:372-374 for M/8 at 50 M), a start from 2 M
by less than 1e-4. These offsets change by less than 5e-5 between t = 50 M and 500 M, so
the drift (difference of two times) depends on the settings by less than 5e-5. Refuted if
the drift differs by more than 1e-4 between settings (the floor would then be the
finder's).

P7 (existing dumps, processors now). The release processor executable on the
hcal dumps reproduces the TESTLOG values at t = 50 M with production settings to 1e-5
(1.001338 at M/8 from hcal/dx8_tight, 0.999738 at M/16); refuted by more (a change of the
executable). At M/4 the corrected finder reads within 5e-3 of the slice mass (about
0.961). Between 50 and 60 M the M/8 mass rises by 1e-4 to 3e-4, the M/16 mass changes by
less than 3e-5.

Detectability (deliverable, defined now so that it is not tuned afterwards): for a run of
length T started at t_0 = 50 M, the smallest mass change a matter run of the same length
can detect is
  Delta M_min(T) = |D(T)| + 2 sigma(T),
with D(T) the vacuum drift M(t_0 + T) - M(t_0) at that resolution (largest over the
finder settings tested) and sigma the scatter of M about a smooth fit (rms of residuals of
a running 20 M average) times sqrt(2) for the two ends; quoted at M/8, M/16 and, with the
measured order, extrapolated to M/32 [JUDGEMENT] for T = 40, 120, 450 M (one doubling of
a at eps = 0.03 and 0.01, and the full span).

## 2026-11-15T12:45Z  outcome of run D-bh-dress-20261115-121427-284ec4f (existing dumps)

Finder re-searched on the processor executable (`.work/build_cpu_c1`) on the dumps at
t = 50 and 60 M of runs/puncture/hcal/{dx4, dx8_tight, dx16}, six settings each, and the
Misner-Sharp mass of the six slices. Tables: `results/hcal_drift.txt`; figure
`figs/hcal_finder.png` (looked at: left, the offsets of every setting from the production
one are flat lines from 50 to 60 M at M/8 and M/16 and lie on top of each other; only
M/4 moves; right, production finder, converged finder and slice at the three resolutions).

P7, against the prediction:
- Reproduction holds: production setting 1.001337 at M/8 (TESTLOG 1.001338) and
  0.999738 at M/16 (TESTLOG 0.999738), t = 50 M, to 1e-6. The release executables read
  these slices as the earlier build did.
- M/4: corrected finder 0.96518, slice M_H 0.96556 (t = 50 M): within 5e-3, holds
  (difference 3.8e-4).
- 50 -> 60 M, production finder: M/8 +6.19e-5, M/16 -3.5e-6, M/4 -3.76e-3. Predicted
  +1e-4 to +3e-4 at M/8: FAILED, the rise is 1.6 times smaller than the lower bound (I had
  extrapolated the 11.5-50 M mean slope, 2.6e-5 per M; the rate at 50-60 M is 6.2e-6 per M,
  so the transient is decaying). M/16 below 3e-5: holds. The slice gives the same changes:
  M_H +6.2e-5 (M/8), +1.6e-6 (M/16), -3.65e-3 (M/4).

P6 on these two times (the full test needs the long runs):
- Offsets from the production setting at M/8 and M/16, t = 50 / 60 M, in 1e-5:
  tolerance 1e-9: 6.09 / 6.01 and 6.11 / 6.50; start at 2 M: 12.5 / 12.0 and 12.4 / 13.2;
  32 points: 17.6 / 17.7 and 18.4 / 18.4; 32 points and 1e-9: 24.5 / 24.5 and 24.6 / 25.0;
  32 points from 2 M: 31.2 / 30.8 and 31.1 / 31.1. Predicted: tight 3e-5 to 1e-4 (holds),
  32 points 1e-4 to 3e-4 (holds), start from 2 M below 1e-4 (FAILED: 1.2e-4 to 1.3e-4; the
  tolerance stops the flow early on either side, so the two starts bracket the surface by
  twice the stopping offset).
- The offsets do not depend on the resolution (M/8 and M/16 agree to 8e-6) and change
  by at most 8e-6 in 10 M: so far the drift does not depend on the finder setting by
  more than 8e-6 (prediction: below 5e-5). At M/4 they change by up to 1e-4 in 10 M (the
  production search ends with rms expansion 6e-7 there instead of 7e-9; the tolerance
  1e-9 search did not converge in 4000 iterations at t = 50 M).
- The converged finder (32 points, 1e-9) is below the slice M_H by 2.7e-5 at both M/8
  and M/16 and both times; the production finder by 2.7e-4.
- Spin: |S| (= |S|/M^2 here) 2.6e-8 and 8.8e-9 at M/8, 1.6e-11 and 1.9e-9 at M/16
  (16 points); 1.6e-9 and 1.4e-10 to 3.8e-12 on 32 points; 4e-7 at M/4. It falls with the
  angular grid, so it is the quadrature of the search, not the slice.
- Slices: the asymptotic Misner-Sharp mass is 1 + 1.2e-5 to 1.5e-5 at every resolution
  (outer region, initial data); the excess at the hole at M/8 (1.6e-3) is local:
  m(R = 10 M) - 1 = 1.26e-3 at 50 M and 1.59e-3 at 60 M, so the excess is spreading
  outward, as TESTLOG:467-470 described.

Card runs: chains D-bh-dress-20261115-121313-284ec4f (M/8, job 4406) and
D-bh-dress-20261115-121314-284ec4f (M/16, job 4407) queued at 12:13Z, still pending at
12:44Z behind 7 jobs.

## 2026-11-15T14:17Z  M/8 card run complete; M/16 in its second segment

Run D-bh-dress-20261115-121313-284ec4f (M/8): Slurm job 4406, 12:53:07Z-13:32:22Z, one
segment, 16000 cycles to t = 500 M, 2355 s on one A100 = 0.654 card-hours (4.71 s per M,
as in the calibration runs). Run D-bh-dress-20261115-121314-284ec4f (M/16): segment 1
(job 4407) 12:57:24Z-13:47:26Z to t = 272.92 M (0.834 card-hours, 11.0 s per M); segment 2
(job 4420) started 13:56:14Z from that dump.

Found while waiting (not a test of mine; recorded because it changes what exists on
disk): the chain's wall-clock stop writes a restart through the ordinary restart writer,
which advances `last_time` by dt at every write (athenak/src/outputs/restart.cpp:193-201),
so after the restart the next periodic dump is one interval late. Here the dump at
t = 300 M of the M/16 run was never written (dump 00006 at 272.92 M stores last_time =
300, file_number = 7; segment 2 writes 350, 400, 450, 500). The probes of the M/16 run
therefore have no t = 300 M point.

Analysis run D-bh-dress-20261115-130954-49ed46f (`tools/finish.sh`, continued with
FINISH_RUN_ID; passes at 13:10Z, 13:35Z, 13:50Z, 14:07Z). At registration the package
directory held uncommitted tool changes; they are the ones committed in d07b8e8, f1d90b2.
Figures looked at: history (M/8 to 500 M, M/16 to 311 M), floor, finder.

M/8 outcome (complete):
- P1 holds. Finder mass minus one: 1.3348e-3 (50 M), 1.5032e-3 (100), 1.5087e-3 (150),
  1.4890e-3 (200), 1.4722e-3 (250), 1.5147e-3 (300), 1.5911e-3 (400), 1.6124e-3 (450)
  (punc.horizon_summary_0.txt of the run). Total change of the 20 M mean from 50 M:
  +2.95e-4 (limit 3e-3). Late rate: linear slope over 250-500 M +6.8e-7 per M (limit
  2e-6). The history has three parts: the end of the gauge transient, +1.6e-4 between 50
  and 100 M (3.4e-6 per M); a plateau 100-210 M (-2.6e-7 per M); after the window below,
  a steady rise, +6.2e-7 and +7.5e-7 per M over 300-400 and 400-500 M.
- The Misner-Sharp mass of the slice at the horizon moves the same way: M_H - 1 =
  1.609e-3, 1.782e-3, 1.765e-3 (200), 1.745e-3 (250), 1.789e-3 (300), 1.927e-3 (500)
  (slices.json of the analysis run). The finder follows the slice; the drift is the
  slice's, not the finder's.

Common to both resolutions (P4, the outer boundary): between 220 and 255 M the finder
mass makes the same excursion at M/8 and M/16, at the same times: relative to the
level before, -4.9e-5 and -4.1e-5 at 230 M, +5.2e-5 and +5.8e-5 at 240 M, back by 255 M
(5 M running mean about a line over 150-300 M: peak-to-peak 9.3e-5 at M/8 and 9.2e-5 at
M/16, minimum at 229 M and maximum at 239-239.5 M in both; outside 170-270 M the same
measure is 1.4e-5 and 6.6e-6). A feature of equal size and timing at two resolutions of
the hole is not made at the hole; the outer region is the same mesh in both runs. The
timing fits a pulse that leaves at the 1+log gauge speed sqrt(2), reaches the faces at
128 M near 89 M, and returns at light speed (126 M), arriving near 215 M [JUDGEMENT; a
run with the boundary at 256 M would move it to about 430 M; not run]. P4 said "below
1e-4 at M/16": 9.2e-5 peak-to-peak on the 5 M mean and 1.0e-4 on the raw finder values:
at the bound, not clearly below it. The asymptotic Misner-Sharp mass of the outer shells
also grows with time at both resolutions (m_inf - 1 = 1.3e-5 at 50 M, then 1.9e-3,
4.5e-3, 8.5e-3, 1.6e-2 at 100, 150, 250, 500 M at M/8; 6.9e-3 at 250 M at M/16): the
outer region is not clean after the first boundary crossing. In AthenaK's Z4c an
`outflow` mesh boundary applies the Sommerfeld condition to the right-hand side
(athenak/src/z4c/z4c_Sbc.cpp:145-185) [VERIFIED by reading the source]; that condition is
not constraint preserving, so a partial reflection is expected [BACKGROUND].

P5 holds: |S|/M^2 after 5 M at most 3.3e-7 at M/8 (falling to 5e-9 after 250 M) and
5.7e-9 at M/16; the 32-point grid lowers S by 10 to 100 on the same slice (probes).

P6 holds over the full span: the offsets of the five other settings from production are
flat from 50 to 500 M at M/8 and from 50 to 273 M at M/16 (figure drift_finder); the
largest change of a drift between settings, D_fs, is 7.8e-6 (M/8) and 8.0e-6 (M/16)
from t0 = 50 M, 1.0e-5 and 9.5e-6 from t0 = 100 M (limit 5e-5).
