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
