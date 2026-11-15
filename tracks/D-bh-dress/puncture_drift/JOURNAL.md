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
