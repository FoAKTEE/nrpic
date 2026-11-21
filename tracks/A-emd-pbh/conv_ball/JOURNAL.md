# JOURNAL of the package conv_ball (helper of A-emd-pbh, wave 3, round 1)

G2 convergence series of horizon formation in the expanding ball (data set 3): mesh
spacing, particle number, ball radius, outer boundary. Brief of the package: PLAN-wave3.md
round 1, package 3 (card cap 6 card-hours, executable core_gauge for every member).

## 2026-11-20, entry 1: what was read, design inputs found (no simulation run yet)

Read: CLAUDE.md, coord/CHARTER.md to "Owners" and 9.4, decisions 0010, 0013, 0014, 0016,
0017-0019, harness/RULES.md, PLAN-wave3.md, runs_ball/README.md and JOURNAL.md entries 7-10,
the runs_ball scripts at 9cddbfc6, expball/README.md, core_gauge/READY, core/gauge
cosmo_gauge.md section 7 and problems/ball/ball_collapse.athinput, the source paper
main.tex lines 930-952 and 1476-1492.

Facts checked in the files (planner's FACTS):
- BH-1R (run A-20261119-164634-f1fe887, bh_smr/athena.log): 568 MeshBlocks of 32^3,
  1317216 particles, 1024 cycles, 1769 s, gpu_mem_peak_MiB = 80633 [VERIFIED].
- BH-1 at uniform M/8 (bh_n256 of run A-20261119-144419-13d5601): its athena.log says 64
  MeshBlocks (root grid 4 x 4 x 4, blocks of 64^3), not 512 as the planner wrote; peak
  41223 MiB, 545 s for 512 cycles [VERIFIED]. sr1l_n256 of the same job (same mesh, 28768
  particles) peaked at 41195 MiB and took 1.056 s per cycle against 1.0645 s: particles cost
  about 2e-4 MiB and 6e-8 s per particle and step (nested.py, cost model).
- Source paper: fiducial OS horizon-mass error Delta M/M_ADM <~ 1e-3 (main.tex:945); AMR
  particle sequence RMS 2.061e-3, 9.362e-4, 7.347e-4 for A1-A3, no monotonic trend for the
  fixed-N SMR sequence (main.tex:1484-1485) [VERIFIED].

Design input, run A-20261120-222355-cc8e0af (`scripts/geometry_probe.py` on BH-1R; figure
fig_geometry.png looked at): the finder's horizon sits at mean coordinate radius
0.418-0.443 M (first found t = 10.875, 41 searches to 15.875); the core shells (R_i <= 2.6)
start at coordinate radius <= 2.43 M and are at r < 0.4 M when the horizon is first found;
the core-edge group reaches its exact trapping proper time at t ~ 10.9, when the finder first
reports a horizon; outer shells move out to r ~ 7 M by t = 16; particles are first removed at
t = 12.70; 1.72 s per cycle.

Design chosen (to be written into DESIGN.md; code committed in a9c36d98): nested static
geometry, finest box [-1, 1]^3, level boxes at 1, 2, 4, 8 M, outer boundary 16 M (32 M for
the boundary leg), each level box 4 MeshBlocks wide; members A, B, C with finest cells M/16,
M/32, M/64 (root 32^3, 64^3, 128^3 in blocks of 8^3, 16^3, 32^3; 288 leaf blocks each);
nested lattice with one particle per local cell (77704 particles for A: tested in
scratch/A-emd-pbh/tmp/conv_ball/preptest, not a result; its table is byte-identical to that
of data set 3, run A-20261119-143524-334e553). Model numbers (design_calc.py, code test in
tmp, NOT yet a registered run): C about 41 GiB and 1.3 card-hours (a chain of two segments),
B 0.12, A 0.02 card-hours; the series with the N, R_b and boundary legs about 2.1
card-hours.

## 2026-11-20 14:34 PST, entry 2: PAUSED (locks/PAUSE present: five-hour window at 97 per cent)

Stopped here, nothing running, no card job submitted. Committed: scripts (copies of runs_ball
at 9cddbfc6 with adjusted paths, geometry_probe.py, nested.py, design_calc.py, prep_bh.py with
--M, --edge-w and --nested, make_decks.py) and decks/nest{16,32,64}_L{16,32}.athinput.
Next steps on restart, in order:
1. registered run of design_calc.py (--exact .../A-20261119-143524-334e553/exact.json
   --probe .../A-20261120-222355-cc8e0af), look at fig_design.png, write DESIGN.md;
2. predictions for every member in this journal, commit;
3. registered prep runs: data set 3 with --nlat --nested nestA:16:16:1 nestA2:16:16:2
   nestA4:16:16:4 nestB:32:16:1 nestB2:32:16:2 nestC:64:16:1; the larger balls
   (--HRb 0.875 --M 1.953125 --R1 0.52 --R2 0.76 --edge-w 0.16836734693877542; and
   lam = 1.35: --HRb 0.945 --M 2.460375 --R1 0.48148148148148145 --R2 0.7037037037037037)
   with nestA and nestB;
4. processor smoke tests of the decks with core_gauge/athena_cpu (nlim 2; nest32/nest64 with
   a reduced mesh override);
5. card job 1 (batch, 58 min): A, B, A-N8, A-N64, A-R1.25, A-L32, B-N8; then the chain of C.

## 2026-11-20 23:58 PST, entry 3 (batch 2b): restart, design run, data, predictions (written before any simulation of the series)

Restart: the flag is gone; nothing of this package ran since entry 2 (no card job, git log,
squeue). Done since, in order:
- design table, registered: run A-20261121-075131-2682bb0 (`design_calc.py`; fig_design.png
  looked at: level structure of A, B, C against BH-1R; BH-1R's core-edge shells cross 2 M near
  t = 5 and 1 M near t = 8.5, the horizon (finder radius 0.42-0.44 M) lies inside the finest
  box). Model check: BH-1R 79.5 GiB and 1.7187 s/cycle against measured 78.7 GiB, 1.7187.
- data, registered: data set 3 with the nested lattices nestA, nestA8, nestA64, nestB, nestB8,
  nestC (run A-20261121-075356-1ad4c81: 77704, 621464, 4969736, 621464, 4969736, 4969736
  particles; each sums to the rest mass 1.14593857; exact events as data set 3: turnaround
  3.371611, tau_AH 9.551092, m 0.686563); the larger balls lam = 1.25 (A-20261121-075401-1412a08:
  nestA 88280, nestB 706768; largest 2m/R 0.757) and lam = 1.35 (A-20261121-075404-ac51b7e:
  91216, 729656; 0.884), with identical exact core events and m_AH(tau). The nested lattice
  with 8 per cell on mesh h equals the lattice of mesh h/2 (same N and sites), so the series
  also holds a fixed-N mesh sequence A-N64, B-N8, C (DESIGN.md 2d).
- DESIGN.md written. Two changes against entry 2: the finder now runs every 0.03125 M (2, 4, 8
  cycles), four times BH-1R's cadence, so that its detection lag (at most 0.03 M x lapse in
  proper time) stays below the errors to be measured; compare.py interpolates the tracked
  particles' proper times and radii linearly to the finder's time (was: nearest record), and
  takes the line points of the nested levels (`--nest OUTER:HF`); `converge.py` tabulates the
  legs.

BH-1R raw finder summary (run A-20261119-164634-f1fe887, bh_smr/ball.horizon_summary_0.txt,
read directly, not a registered analysis): first horizon at t = 10.875 with mass 0.70106 and
mean radius 0.4425 M; mass 0.68571 at t = 11.375 (lowest), then rising to 0.70761 at t = 15.875;
the exact first-trapped mass is 0.686563 and the exact m_AH grows to 0.69610 at tau_AH + 2.
So at BH-1R's mesh the first detections sit about 2 per cent high and the later ones within
about 1 per cent; this sets the scale of the predictions below [JUDGEMENT].

### Prediction S (processor smoke tests, core_gauge/athena_cpu, before the card job)
nest16_L16 (with nestA, and with the lam = 1.35 nestA data), nest16_L32 and nest32_L16 run 2
cycles, nest32_L32, nest64_L16 and nest64_L32 initialize (nlim = 0) on their full meshes: all
exit 0 with 288 (outer 16 M) or 344 (outer 32 M) MeshBlocks, finite history lines, and the
particle count of their lattice. Refuted by a refusal of the 8^3 blocks with four ghost cells
under static refinement (then nest16 needs blocks of 16^3: root 32^3 in 2 x 2 x 2 blocks, which
breaks the one-block margin and needs a new geometry).

### Prediction G (the series; all [JUDGEMENT])
G1 runs: every member reaches t = 16 with finite fields outside the excised region
(probability 0.8 each); cost within a factor 2 of the model (A 0.016, B 0.12, C 1.3
card-hours).
G2 finder: a horizon is found in every member of the mesh, N, R and L legs, first between
t = 10.4 and 11.6 (BH-1R 10.875), and in every later search (probability 0.7 for the A-type
members, which are coarser than BH-1R outside 1 M; 0.85 for B and C).
G3 first-detection error ddet (DESIGN.md 4): in [-0.1, +0.4] M for A, |ddet| falling A -> B -> C
with |ddet(C)| <= 0.08 M; apparent order between B and C at least 0.8.
G4 trapping per particle of the band just inside the core edge (dtrap, R_i = 2.603): |dtrap| <=
0.15 M (A), 0.07 M (B), 0.04 M (C), falling monotonically, order >= 1 between B and C (BH-1 at
uniform M/2: -0.40 M, entry 9 of runs_ball).
G5 turnaround: core |eps| at the exact turnaround (eta) below 6e-3 (A), 2e-3 (B), 7e-4 (C),
order >= 1.5 per halving; mean core turnaround error |dta| below 0.03 M (A) and falling to C
until it reaches the estimator's floor of about 3e-3 M (the parabola vertex of three records;
runs_ball entry 13).
G6 horizon mass: |dm1| (first detection) below 3e-2 at A and falling; the median |dmmed| about
1e-2 (A), 5e-3 (B), 2.5e-3 (C), order about 1 (the top-hat jump of the density limits the
order). Against the source's OS level (Delta M/M_ADM <~ 1e-3, main.tex:945; RMS 7.3e-4 to
2.1e-3, main.tex:1484): C 1.5 to 5 times that level, i.e. "of the same order" only in the
loose sense; a C error below 2e-3 would meet it plainly.
G7 legs: the spread of ddet, dtrap and dmmed across the N leg at fixed mesh (A, A-N8, A-N64;
B, B-N8) is smaller than the mesh difference |e(A) - e(B)| (resp. |e(B) - e(C)|) (the lattice
is free of sampling noise, so the particle number acts only through the deposit); the fixed-N
sequence A-N64, B-N8, C converges like A, B, C. R leg (A, A-R1.25, A-R1.35): the core errors
change by less than half of |e(A) - e(B)| (the exact core is the same; only the envelope and
the region near the boundary differ). L leg (A vs A-L32, B vs B-L32): ddet and dtrap differ by
less than 0.01 M and dm1 by less than 1e-3 (a signal from the boundary at 16 M needs about
15 M to reach the horizon, after the first detection).
Refuted, for the G2 criterion, by: no horizon in B or C; |ddet|, |dtrap| or |dmmed| not
falling from B to C (non-monotonic); a C mass error above 1e-2; a leg spread larger than
the mesh difference of its member. A non-monotonic sequence is recorded as such (the source
reports one for its fixed-N SMR sequence, main.tex:1485).

## 2026-11-21 00:08 PST, entry 4: outcome of prediction S (smoke tests); card job 1 submitted

Card job 1 (run A-20261121-075926-d10c2c1, Slurm 4776; A, B, A-L32, A-R1.25, A-R1.35, A-N8)
was submitted at 23:59 while the smoke tests ran, third in a queue of three pending jobs, so
that it holds its place; it would have been cancelled had a smoke test failed.

Outcome of S, run A-20261121-075916-0b98e86 (smoke.json) and its figure run
A-20261121-080727-e2f9074 (fig_smoke.png looked at): HOLDS. All seven cases exit 0:
nest16_L16 with data set 3 and with the 1.35 ball, nest16_L32 and nest32_L16 run 2 cycles with
finite history lines (77704, 91216, 77704, 621464 particles); nest32_L32, nest64_L16 and
nest64_L32 initialize (621464, 4969736, 4969736 particles). Mesh: 288 MeshBlocks (outer 16 M)
and 344 (outer 32 M), 56 per level and 64 on the finest, as designed; 8^3 blocks with four
ghost cells are accepted under static refinement. The initial psi^4 on the line through the
nested levels equals expball's exact slice to 4.8e-13 (largest, inside the matter) for all
three meshes, which also confirms the line-point reader of compare.py --nest (cells of
M, 1/2, ..., 1/16 for nest16, levels changing at |x| = 1, 2, 4, 8 M). Not tested by the smoke:
memory and speed on the card (the processor build reached 7.3e3 zone-cycles per second).

## 2026-11-21 01:05 PST, entry 5: card job 1 ran; outcomes of prediction G for A, B, A-L32, A-R1.25, A-R1.35, A-N8

Card run A-20261121-075926-d10c2c1 (Slurm 4776, 00:33-00:51 PST, 0.29 card-hours, closed):
all six members exit 0. Analysis run A-20261121-085252-f4ed504 (analyse.py: compare.py per
member, turnaround.py, converge.py; convergence.md, fig_convergence.png, figs/<member>_*.png
and fig_turnaround_*.png; looked at: fig_convergence, B_events, B_horizon, A_horizon,
fig_turnaround_eps). The C chain (A-20261121-083336-6a82131, Slurm 4781) was submitted when job 1
started and is pending (first in line at 01:01).

| member | first detection t | ddet (M) | dtrap (M) | dta V3 / C (M) | eta | dm1 | dm median | card s | peak GB |
|---|---|---|---|---|---|---|---|---|---|
| A (M/16) | 10.875 | +0.193 | -0.093 | -0.037 / -0.015 | 8.1e-3 | +9.3e-3 | +7.4e-3 | 76 | 4.5 |
| B (M/32) | 10.781 | +0.068 | -0.022 | -0.033 / -0.013 | 3.1e-3 | +4.5e-2 | -2.1e-3 | 537 | 11.4 |
| A-L32 | 10.875 | +0.193 | -0.093 | -0.037 / -0.015 | 8.1e-3 | +9.3e-3 | +7.4e-3 | 87 | |
| A-R1.25 | 10.906 | +0.100 | -0.049 | -0.020 / +0.021 | 8.0e-3 | +1.9e-2 | +6.7e-3 | 79 | 4.5 |
| A-R1.35 | 10.938 | +0.164 | -0.029 | -0.025 / +0.017 | 8.3e-3 | +1.6e-2 | +1.0e-2 | 80 | 4.5 |
| A-N8 | 10.813 | +0.109 | -0.047 | -0.048 / -0.017 | 4.2e-3 | +8.3e-3 | -1.3e-3 | 185 | 4.6 |

(ddet: particles' proper time at the finder's radius minus the exact tau_AH of that shell, at
first detection; dtrap: band R_i = 2.603, 60 particles; dm: finder sqrt(A/16 pi) against the
exact horizon mass of the same slice; DESIGN.md section 4.) The first slice on which a tracked
particle has reached its own tau_AH is t = 10.447 (A) and 10.584 (B); the finder follows 0.43
and 0.20 M later.

Outcomes:
- G1 HOLDS: all reach t = 16 with finite histories; card time within a factor 2 of the model
  (A 76 s against 58 s, B 537 s against 446 s, A-N8 185 s against 94 s); the memory model is
  low by 25-45 per cent for these small blocks (A 4.5 GB against 3.1 GiB, B 11.4 against 9.2),
  so C may need 50-60 GB [JUDGEMENT], still inside a card.
- G2 HOLDS: a horizon in all six, first at t = 10.78-10.94 (window 10.4-11.6), and in every
  later search (no miss after the first detection in any member).
- G3 so far HOLDS: ddet = +0.193 M at A (inside [-0.1, +0.4]), +0.068 M at B, order 1.51; C
  decides the rest.
- G4 so far HOLDS: |dtrap| 0.093 (A, bound 0.15) and 0.022 M (B, bound 0.07), order 2.05.
- G5 REFUTED at A and B: eta = 8.1e-3 (A, bound 6e-3) and 3.1e-3 (B, bound 2e-3), order 1.38
  (predicted >= 1.5); the mean core turnaround time does not converge from A to B (V3 -0.037 ->
  -0.033 M, order 0.16; cycloid C -0.0148 -> -0.0127 M, order 0.22), while R_max converges fast
  (mean relative error 1.8e-3 -> 2e-5 with V3, 1.2e-3 -> -1.5e-4 with C). Reading of the figures
  (B_events, fig_turnaround_eps) [JUDGEMENT]: the per-particle turnaround times scatter by
  +-0.05 M with a pattern in R_i; the local shift of the maximum, 8 B^2 eps', is +-0.05 M within
  2 M of the turnaround; the cycloid fit depends on its window by up to 0.03 M (A-R1.25: C2
  +0.004, C12 +0.029; turnaround.log). The turnaround of this core (tau_ta = 3.37 M, a flat
  maximum) is set at A and B by slopes of the shell error of a few 1e-3 per M, not by a
  secular time shift, so "turnaround time" is defined only to about 0.03 M here; R_max and the
  shell error at the turnaround converge.
- G6 mixed: dm median +7.4e-3 (A) and -2.1e-3 (B): magnitude falls by 3.6 (order 1.84) with a
  change of sign; B's plateau after t = 11.5 is -2e-3 (B_horizon.png), twice the source's
  fiducial OS level (1e-3, main.tex:945) and of the order of its A1 RMS (2.1e-3, main.tex:1484).
  dm1 (first detection) does NOT fall (+9.3e-3 -> +4.5e-2): at B's first detection only the
  tracked particles near R_i = 2.62 have passed their tau_AH, so the exact-slice estimate is
  0.660 and jumps to 0.688 one search later (B_horizon.png, left panel): the first-detection
  mass error measures the estimator at the instant of formation, not the code. Mass errors are
  judged on the median (and the plateau) from here on.
- G7 L leg HOLDS: A-L32 equals A to 1e-7 M in ddet and dtrap and 4e-6 in dm median (the
  boundary at 16 M does not reach the horizon before t = 16). N leg at A HOLDS against the
  mesh difference (spreads: ddet 0.084 < 0.125, dtrap 0.045 < 0.070, dm median 0.0087 <
  0.0094), but the particle number is not negligible: A-N8 (the lattice of B on A's mesh)
  removes about two thirds of the A-B difference in ddet and dtrap. R leg REFUTED at A for the
  time errors: ddet 0.193, 0.100, 0.164 and dtrap -0.093, -0.049, -0.029 for lam = 1, 1.25, 1.35
  vary by more than half the A-B mesh difference (0.063, 0.035), not monotonically in lam;
  dm median (7.4e-3, 6.7e-3, 1.0e-2) and eta (8.1e-3, 8.0e-3, 8.3e-3) stay within it. Whether
  the ball-radius dependence shrinks with the mesh is the question for B-R1.25 (job 3).
Open: C (mesh triple, fixed-N sequence), job 3 (B-N8, A-N64, B-R1.25, B-L32).

## 2026-11-21 01:10 PST, entry 6: plan change for job 3 and predictions for its members (before job 3 is submitted)

Particles cost 2e-7 card-seconds per particle and step (A-N8 against A), three times the
model; job 3 is split into 3a (B-N8, A-N64) and 3b (B-R1.25, B-R1.35 new, B-L32 last); C is
re-estimated at about 2.3 card-hours (DESIGN.md section 3a).
Predictions [JUDGEMENT], written before 3a and 3b run:
- R leg at B: across lam = 1, 1.25, 1.35 the spread of ddet and dtrap at B is at most half the
  spread at A (A: 0.093 and 0.064 M), i.e. the ball-radius dependence shrinks with the mesh.
  Refuted by a spread at B of more than 0.047 M (ddet) or 0.032 M (dtrap).
- N leg at B: B and B-N8 differ in ddet and dtrap by less than |e(A) - e(B)| (0.125, 0.070 M) and
  by less than A and A-N8 do (0.084, 0.045 M).
- fixed-N mesh sequence (A-N64, B-N8, C; 4969736 particles each): |ddet| and |dtrap| fall
  monotonically, order >= 1 between A-N64 and B-N8.
- B-L32 equals B to 1e-5 M in ddet and dtrap (as A-L32 did).

## 2026-11-21 01:26 PST, entry 7: C running, job 3a submitted

The chain of C (run A-20261121-083336-6a82131) started at 01:19 as Slurm 4781: 1.88 s per cycle
over its first 160 cycles (4096 cycles to t = 16: about 2.1 card-hours in three segments of
50 min; the model said 1.14 s, the difference being the particles at 2e-7 s each, entry 6),
41557 MiB on the card (model 41.4 GiB). Job 3a (run A-20261121-091934-ac62f5f, Slurm 4784:
B-N8, A-N64) was submitted when C started; job 3b waits until 3a runs (one pending job per
package).

## 2026-11-21 02:15 PST, entry 8: C after its first segment (t = 6.32): the turnaround leg of the mesh triple

C's first segment stopped at the wall limit at t = 6.324 (cycle 1619, 02:09); the chain resubmitted
itself (Slurm 4786, pending). Job 3a (Slurm 4784) started at 02:09: B-N8 runs at 1.17 s per cycle
(2048 cycles, about 40 min), so A-N64 (about 19 min) will probably be cut by the 58-min wall near
t = 14-15; its first detection and the window t <= 12.5 would still be inside the record.

Interim analysis A-20261121-100945-3985b90 (analyse.py on C's directory with the job-1 numbers;
C_events.png and convergence.md looked at; C has no finder search yet, the finder starts at t = 9):

| mesh | eta (core eps at tau_ta) | turnaround V3 (M) | turnaround C (M) | R_max V3 | R_max C |
|---|---|---|---|---|---|
| A (M/16) | 8.1e-3 | -0.0370 | -0.0148 | +1.8e-3 | +1.2e-3 |
| B (M/32) | 3.1e-3 | -0.0331 | -0.0127 | +2.0e-5 | -1.5e-4 |
| C (M/64) | 1.1e-3 | -0.0082 | -0.0035 | +1.4e-4 | +1.1e-4 |

- eta: orders 1.38 and 1.49, self-convergence order 1.31: converges at order about 1.4. G5's
  bound for C (7e-4) is REFUTED (1.1e-3), as it was for A and B: the shell error at the
  turnaround is about 1.4 times larger than predicted at every mesh, and converges at the
  predicted order within 0.1.
- turnaround time: does not converge from A to B (orders 0.16 V3, 0.22 C) but does from B to C
  (orders 2.02 V3, 1.87 C), so the self-convergence order is negative (-2.7, -2.2): the sequence
  is not in its asymptotic range at A and B. C's per-particle scatter is +-0.02 M (B: +-0.05 M,
  C_events.png against B_events.png). With the cycloid fit C reaches -0.0035 M, at the floor of
  about 3e-3 M named in G5 [JUDGEMENT: the turnaround time of a shell, a flat maximum, is
  resolved only once the slope of its shell error near tau_ta is below about 1e-3 per M].
- R_max: below 2e-3 at every mesh, non-monotonic (B's 2e-5 is a crossing of zero); the
  relative R_max error is no longer a usable convergence measure below about 2e-4.

## 2026-11-21 02:50 PST, entry 9: B-N8 (job 3a, first member): outcome of the N-leg prediction at B

B-N8 (mesh B, 8 particles per cell, 4969736 particles) finished at 02:43:45 (exit 0; 2048 cycles
at about 1.2 s). Analysis A-20261121-104359-4ce67d9 (B-N8_horizon.png, B-N8_events looked at):
first detection t = 10.750; ddet +0.0705 M (B: +0.0675); dtrap -0.0284 M (B: -0.0224); finder lag
0.165 (B: 0.197); eta 3.5e-3 (B: 3.1e-3); turnaround V3 -0.0150, cycloid C -0.0083 M (B: -0.0331,
-0.0127); horizon mass median -3.0e-4 (B: -2.1e-3), window t <= 12.5 -2.1e-4 (B: -2.0e-3).
- Prediction (entry 6) "B and B-N8 differ in ddet and dtrap by less than |e(A) - e(B)| (0.125,
  0.070 M) and by less than A and A-N8 do (0.084, 0.045 M)": HOLDS by a wide margin (0.003 and
  0.006 M): at mesh B the first-detection and trapping times no longer depend on the particle
  number, so their A -> B change (entry 5) is a mesh effect.
- The horizon mass does depend on it: with 8 per cell the finder's mass follows the exact slice
  mass within 1e-4 to 7e-4 from t = 11.5 to 16 (B-N8_horizon.png), below the source's fiducial
  OS level (Delta M/M_ADM <~ 1e-3, main.tex:945) and below its best AMR particle RMS (7.3e-4,
  main.tex:1484); with one per cell (B) it sits at -2e-3. [JUDGEMENT] The plateau error of B is
  the discreteness of the accreted underdense shell (one lattice site per cell of 1/16-1/8 M
  outside the core), as the steps of A's mass curve suggest (A_horizon.png).

## 2026-11-21 03:05 PST, entry 10: A-N64 (job 3a, second member); job 3a closed, job 3b submitted

Job 3a (run A-20261121-091934-ac62f5f, Slurm 4784, 02:09-02:59, 0.84 card-hours) closed: B-N8 and
A-N64 exit 0 (A-N64 1024 cycles at 1.09 s, peak 5.4 GB). C's second segment started at 02:59
(Slurm 4786); job 3b (run A-20261121-110017-471b0ae, Slurm 4787: B-R1.25, B-R1.35, B-L32) was
submitted at 03:00.

Analysis A-20261121-110025-e6aec8c (A-N64 with all earlier numbers; A-N64_horizon.png and
convergence.md looked at): first detection t = 10.812; ddet +0.146 M; dtrap -0.048 M; lag 0.350;
eta 6.2e-3; turnaround V3 -0.040, C -0.015 M; horizon mass median +5.0e-4 (window +5.2e-4).
- N leg at A (1, 8, 64 per cell): ddet 0.193, 0.109, 0.146 and lag 0.43, 0.31, 0.35 are not
  monotonic in N; dtrap -0.093, -0.047, -0.048 settles from 8 per cell on; the mass median
  +7.4e-3, -1.3e-3, +5.0e-4 falls by 15 from 1 to 64 per cell. At mesh A the time errors
  are set by the mesh once N >= 8 per cell (their N spread is below the A-B difference); the
  mass error is set by the particles.
- fixed-N mesh sequence (4969736 particles: A-N64, B-N8; C pending): ddet 0.146 -> 0.071 (order
  1.05), lag 0.35 -> 0.165 (1.09), dtrap -0.048 -> -0.028 (0.75); mass median +5.0e-4 -> -3.0e-4
  (sign change, magnitude order 0.75): at fixed particle number the horizon mass is already at
  the 3-5e-4 level on both meshes, i.e. below the source's fiducial OS level of 1e-3
  (main.tex:945) [VERIFIED for these two runs; C decides the third point]. Prediction of entry
  6 ("|ddet|, |dtrap| fall monotonically, order >= 1 between A-N64 and B-N8"): HOLDS for ddet
  (1.05), fails narrowly for dtrap (0.75).

## 2026-11-21 03:56 PST, entry 11: job 3b (B-R1.25, B-R1.35, B-L32): outcomes of the ball-radius and boundary predictions at B

Job 3b (run A-20261121-110017-471b0ae, Slurm 4787, 03:09-03:40, 0.52 card-hours, closed): all
three exit 0. Analysis A-20261121-115055-4554451 (convergence.md; B-R1.35_horizon.png looked at).
C's second segment stopped at the wall at 03:49 and its third (Slurm 4789) started at once.

| member | first detection t | ddet (M) | lag | dtrap (M) | turnaround C (M) | eta | mass median |
|---|---|---|---|---|---|---|---|
| B | 10.781 | +0.068 | 0.197 | -0.022 | -0.0127 | 3.1e-3 | -2.1e-3 |
| B-R1.25 | 10.750 | +0.065 | 0.173 | -0.015 | -0.0041 | 3.7e-3 | -1.9e-3 |
| B-R1.35 | 10.750 | +0.107 | 0.363 | -0.008 | -0.0048 | 5.8e-3 | -1.25e-3 |
| B-L32 | 10.781 | +0.068 | 0.197 | -0.022 | -0.0127 | 3.1e-3 | -2.1e-3 |

- R leg at B (entry 6: spread of ddet and dtrap at most half that at A, i.e. 0.047 and 0.032 M):
  HOLDS, narrowly for ddet (0.042; A: 0.093) and clearly for dtrap (0.015; A: 0.064): the
  ball-radius dependence of the time errors shrinks by 2.2 and 4.3 from A to B. B-R1.35's larger
  ddet comes with a later finder detection (lag 0.36 against 0.17-0.20): the trapping per
  particle (dtrap) is closer to exact in the larger balls, not further. The horizon mass is
  nearly independent of the ball radius (spread 8e-4 against its mesh change of 9.4e-3 from A
  to B); eta grows with lam (3.1e-3, 3.7e-3, 5.8e-3) [JUDGEMENT: the larger envelope, on the
  coarser 4-8 M level, perturbs the core before its turnaround].
- L leg at B (entry 6: B-L32 equals B to 1e-5 M): HOLDS, identical to 1e-11 in every quantity:
  the outer boundary at 16 M does not reach any measured quantity before t = 16 at either mesh.

## 2026-11-21 04:10 PST, entry 12: C finished; the mesh triple; outcome of G3-G6 and of the series

C (chain A-20261121-083336-6a82131: Slurm 4781, 4786, 4789; 01:19-04:01 with two waits; 1.86
card-hours; peak 41.4 GB) reached t = 16 (STATUS DONE, tlim), closed. Final analysis
A-20261121-120257-a2eb839 (all members; convergence.md, convergence.json, fig_convergence.png,
figs/C_horizon.png, figs/C_events.png; fig_convergence and C_horizon looked at). Card time of the
package this round: 0.294 + 1.856 + 0.840 + 0.513 = 3.50 card-hours (cap 6), from the manifests.

Mesh triple (one particle per local cell; finest cell M/16, M/32, M/64; level boundaries fixed):

| quantity | A | B | C | orders A-B, B-C | self-order |
|---|---|---|---|---|---|
| first detection t | 10.875 | 10.781 | 10.750 | | |
| ddet, first-detection error (M) | +0.193 | +0.068 | +0.0166 | 1.51, 2.02 | 1.30 |
| finder lag after the first trapped slice (code time) | 0.428 | 0.197 | 0.094 | 1.12, 1.06 | 1.17 |
| dtrap, trapping per particle, band 2.603 (M) | -0.093 | -0.022 | -0.0077 | 2.05, 1.53 | 2.26 |
| turnaround, cycloid C (M) | -0.0148 | -0.0127 | -0.0030 | 0.22, 2.09 | (-2.2) |
| eta, core eps at turnaround | 8.1e-3 | 3.1e-3 | 1.1e-3 | 1.38, 1.49 | 1.31 |
| horizon mass, median over detections | +7.4e-3 | -2.1e-3 | -2.1e-4 | 1.84, 3.31 (magnitude) | |
| horizon mass, median t <= 12.5 | +5.5e-3 | -2.0e-3 | -2.0e-4 | 1.42, 3.36 (magnitude) | |

Fixed particle number (4969736: A-N64, B-N8, C): ddet 0.146, 0.071, 0.0166 (orders 1.05, 2.09);
dtrap -0.048, -0.028, -0.0077 (0.75, 1.87); mass median +5.0e-4, -3.0e-4, -2.1e-4.
C's horizon mass follows the exact slice mass within 1e-5 to 6e-4 from t = 11.7 to 16 and within
3e-3 in the first 0.3 M after formation (C_horizon.png).

Outcomes:
- G1 HOLDS for C: t = 16 with finite fields; 1.88 s per cycle against the model's 1.14 (the
  particles, entry 6), within the factor 2; memory 41.4 GB against the model's 41.4 GiB.
- G2 HOLDS: a horizon in every member of every leg (14 runs), first at t = 10.75-10.94, and in
  every later search.
- G3 HOLDS: |ddet| falls A -> B -> C (0.193, 0.068, 0.017 M), |ddet(C)| = 0.017 <= 0.08, order
  2.02 between B and C (predicted >= 0.8).
- G4 HOLDS: |dtrap| 0.093, 0.022, 0.0077 M within the bounds 0.15, 0.07, 0.04, monotonic, order
  1.53 between B and C (predicted >= 1).
- G5 REFUTED in its bounds (eta 1.4 times above them at every mesh; the turnaround time does not
  converge from A to B), but the shell error at the turnaround converges at order 1.4 and the
  turnaround time from B to C at order 2.1, reaching -0.003 M at C (the floor named in G5).
- G6 HOLDS and is exceeded at C: the mass median falls from 7.4e-3 to 2.1e-4 in magnitude (orders
  1.84, 3.31; the sign changes from A to B); C's 2.1e-4 is below the source's fiducial OS level
  (Delta M/M_ADM <~ 1e-3, main.tex:945) and below its best AMR particle RMS (7.3e-4,
  main.tex:1484), where G6 had predicted C at 1.5 to 5 times that level. The mass error at the
  first detection is not a usable measure (entry 5): it is the estimator at the instant of
  formation (C: -1.5e-3).
- G7: L leg HOLDS at A and B (identical to 1e-7 and 1e-11); N leg HOLDS against the mesh
  difference at A and B, and at B the time errors are independent of N (entry 9); R leg REFUTED
  at A (entry 5) and HOLDS at B (entry 11): the ball-radius dependence shrinks with the mesh;
  fixed-N sequence: ddet order 1.05 then 2.09, dtrap 0.75 then 1.87 (entries 6, 10).

Reading for the G2 criterion of the sheet (coord/CHARTER.md 9.4) [JUDGEMENT; a second agent
should check it from convergence.json and the figures]: in the spherical case the errors of the
horizon-formation time (ddet, dtrap, finder lag) converge in mesh spacing at orders 1-2 with
monotonic sequences over three meshes, and in particle number they are settled at mesh B; their
ball-radius dependence shrinks with the mesh (A: spread 0.09 M, B: 0.04 M), but the R leg has
been run on A and B only; the turnaround time converges only between B and C (a flat maximum),
while the shell error at the turnaround converges at order 1.4 over all three meshes; the
horizon-mass error reaches 2e-4 at C, of the order of (below) the source's OS test; the
boundary leg is null (16 M against 32 M identical). Not done: the R leg on C, a second seed or
lattice offset (the lattice is noise-free, so there is no sampling seed), the turnaround time
from a constant-occupancy mesh finer than C.
