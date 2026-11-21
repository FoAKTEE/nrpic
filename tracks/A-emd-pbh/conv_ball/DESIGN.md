# DESIGN of the G2 convergence series of horizon formation in the expanding ball (conv_ball)

Package conv_ball of A-emd-pbh, wave 3 (brief: `tracks/A-emd-pbh/PLAN-wave3.md`, round 1,
package 3). Criterion (coord/CHARTER.md 9.4, G2): in the spherical case the errors of the
turnaround time and of the horizon-formation time against the exact solution converge in
particle number, mesh spacing and ball radius; the horizon-mass error is of the same order as
in the source paper's Oppenheimer-Snyder test; plus the boundary leg of the common three-way
convergence (9.2). Every member uses the executable of BH-1R,
`scratch/core/exe/core_gauge/athena_gpu` (source b4430da, relaxed 1+log lapse `lapse_leak`),
so that the series is consistent. Numbers below come from the runs named; model numbers are
marked [JUDGEMENT].

## 1. Physics, data, gauge (unchanged from BH-1R)

Data set 3 (run A-20261119-143524-334e553; rebuilt byte-identically with the nested
lattices in run A-20261121-075356-1ad4c81): compensated top-hat, H R_b = 0.7, delta_c = 1.5
inside R1 = 0.65 R_b = 2.653 M, underdense shell to R2 = 0.95 R_b = 3.878 M, Einstein-de
Sitter envelope to R_b = 4.082 M, taper to the matter edge at rbar = 4.25 M. Exact: core
turnaround tau = 3.3716 M; first trapped sphere = core edge at tau_AH = 9.5511 M, m = 0.686563,
R_AH = 1.373 M; horizon mass 0.69610, 0.70437 at tau_AH + 2, 4 (runs_ball/JOURNAL.md entry 7;
prep run.log of A-20261121-075401-1412a08 repeats them). Gauge and physics of the deck
`scripts/bh_smr.athinput` (BH-1R, run A-20261119-164634-f1fe887): relaxed 1+log
(`lapse_leak = 8`), Gamma-driver, PCS clouds with the fourth-order compensation, excision
below alpha = 0.1, finder from t = 9 every 0.125 M (start radius 1 M, 400 iterations, mass
tolerance 1e-5), t = 0 -> 16. Only the mesh, the lattice and (legs R, L) the data change.

## 2. Mesh: nested static levels that scale by two (scripts/nested.py, make_decks.py)

(a) Geometry nest(h_f, outer): root over [-outer, outer]^3 and L = log2(outer) refined
levels; level l covers |x|_inf < b_l = outer/2^l with cells h_l = h_f 2^(L-l). Every level box
holds 2/h_f cells per direction, MeshBlocks are a quarter of that wide, so each level box is
4 x 4 x 4 blocks and the next box is exactly its central 2 x 2 x 2 (one block of 2:1
margin). The level boundaries sit at |x|_inf = 1, 2, 4, 8 M for every h_f: halving h_f halves
every cell and keeps every boundary. Leaf blocks 56 L + 64 (288 for outer 16 M, 344 for 32 M).
The `refined_region` boxes are given at 0.975 b_l so that they end inside the boundary
blocks.

| member | finest cell (r < 1 M) | 1-2 M | 2-4 M | 4-8 M | 8-16 M | root cells | block |
|---|---|---|---|---|---|---|---|
| A | M/16 | M/8 | M/4 | M/2 | M | 32^3 | 8^3 |
| B | M/32 | M/16 | M/8 | M/4 | M/2 | 64^3 | 16^3 |
| C | M/64 | M/32 | M/16 | M/8 | M/4 | 128^3 | 32^3 |
| BH-1R (reference) | M/16 inside 3.9 M | M/16 | M/16 | M/8 | M/8 | 256^3 | 32^3 |

Why the finest box is [-1, 1]^3: the finder's horizon of BH-1R lies at mean coordinate
radius 0.418-0.443 M from its first detection (t = 10.875) to t = 15.875 (run
A-20261120-222355-cc8e0af, `geometry_probe.py`, fig_geometry.png), 7 cells of M/16; the
core shells (R_i <= 2.6 M) start at coordinate radius <= 2.43 M and are inside 0.4 M when the
horizon is first found, so the core edge starts on the 2-4 M level, crosses 2 M near t = 5
and 1 M near t = 8.5 (fig_design.png of run A-20261121-075131-2682bb0, right panel). A finest box
of [-2, 2]^3 would cost 6.5 times the cells per member and does not fit C (memory). The
coarsest member A keeps BH-1R's M/16 where the horizon forms (the known working value: BH-1
at uniform M/8 found no horizon, run A-20261119-144419-13d5601) but is coarser than BH-1R
outside 1 M; C is finer than BH-1R everywhere inside 8 M. [JUDGEMENT] The turnaround (core
at 1.5-2.8 M) is resolved by the 1-4 M levels, so its error measures the mesh at 4 h_f to
2 h_f; the trapping and the horizon by the finest level.

(b) Memory, model of nested.py calibrated on the measured peaks: BH-1R 80633 MiB for 568
blocks of 32^3 (142 MiB per block with its ghosts; the uniform BH-1 used 644 MiB per 64^3
block, 1.7e-3 against 2.2e-3 MiB per ghosted cell: refinement costs about 30 per cent more
per cell), scaled by the ghosted block volume, plus 2.1e-4 MiB per particle (bh_n256
against sr1l_n256, same mesh). The model gives BH-1R 79.5 GiB (measured 78.7). Members:
A 3.1, B 9.2, C 41.4 GiB [JUDGEMENT, model]; all below 70 GB.

(c) Wall time: one global step dt = 0.25 h_f (no sub-cycling), 1024, 2048, 4096 steps to
t = 16 for A, B, C. Cost per step = BH-1R's 1.7187 s per cycle (zone-cycles 1.08e7 per
second) per ghosted cell, plus 6.2e-8 s per particle and step (bh_n256 against sr1l_n256),
floor 0.03 s [JUDGEMENT]. A 0.058 s/step, 0.016 card-hours; B 0.22 s/step, 0.12 card-hours;
C 1.14 s/step, 1.29 card-hours, so C is a chain of two or three segments
(`--launcher chain`, athena -t 00:50:00, restart files every 4 M and at the wall limit).
The finder costs nothing visible: BH-1R's cycles 400-500 and 600-700 (with 12 searches)
took 171.5 and 171.9 s.

(d) Particles: one particle per cell of the local level (nested lattice of nested.py on
expball's model: sites at the cell centres of each level inside the matter, mass
rho_* psi^6 h_l^3, the sites within one local spacing of the matter edge scaled together so
that the total is the rest mass, as expball/particles.lattice). A uniform lattice at M/64
over the ball would be (8.5 x 64)^3 x 0.52 = 8e7 particles; the nested one has 77704 (A),
621464 (B), 4969736 (C) (run A-20261121-075356-1ad4c81, lattices.json; every lattice sums to
the rest mass 1.14593857). Because the level boxes do not move, the lattice with 8 per cell
on mesh h_f IS the lattice of mesh h_f/2 (nestA8 = nestB, nestA64 = nestB8 = nestC: same N,
same sites), so the series holds three sequences like the source's convergence suites:
constant occupancy A, B, C (one per cell); fixed particles A-N64, B-N8, C (4969736 each,
mesh only); fixed mesh A, A-N8, A-N64 (particles only). The lattice of each level is aligned with its cells; the core
compresses by about 6 in coordinate radius before the horizon forms, so every finest cell
there holds one particle or more. Tracked particles: 60 per target shell (12 shells from
0.3 R1 to R2 + 0.1) and 600 random (about 1315).

(e) Particle-number leg: B with 1 and 8 particles per local cell (B, B-N8; the brief's
leg), and the cheap A with 1, 8, 64 (A, A-N8, A-N64; a three-point leg at fixed mesh).

(f) Ball-radius leg: the same core and H inside a ball lam times larger, lam = 1.25, 1.35
(prep_bh.py --HRb 0.7 lam --M lam^3 --R1 0.65/lam --R2 0.95/lam --edge-w 0.168367):
R1 = 2.653 M, R2 = 3.878 M, H = 0.1715/M and the taper unchanged, envelope to R_b = 5.102 and
5.510 M, matter edge at 5.270 and 5.679 M, mass 1.954 and 2.461 in the units of data set 3
(runs A-20261121-075401-1412a08, A-20261121-075404-ac51b7e). Largest 2m/R on the slice
0.757 and 0.884 (at the envelope edge, where 2m/R = (H R_b)^2), below 1; lam > 1.43 would
make the edge of the envelope trapped, which bounds the leg. The exact core events are
identical (turnaround 3.3716, tau_AH 9.5511, m_AH(tau) the same; both run.log files).
Members A-R1.25, A-R1.35 and B-R1.25 (lattices nestA, nestB of the larger balls).

(g) Boundary leg: outer boundary at 16 M and at 32 M with one coarser level more (root
cells 2 M for A, M for B; decks nest16_L32, nest32_L32), the same lattice (no matter beyond
8 M at t = 0). The matter edge reaches about 7 M by t = 16 in BH-1R (probe), so only the
boundary (outflow at 16 M against 32 M) changes. Members A-L32, B-L32.

## 3. Runs, ordered by value (h) (model of run A-20261121-075131-2682bb0, design_table.md)

| order | member | deck | data | particles | memory GiB | card-h (model) | job |
|---|---|---|---|---|---|---|---|
| 1 | A | nest16_L16 | nestA | 77704 | 3.1 | 0.016 | 1 |
| 2 | B | nest32_L16 | nestB | 621464 | 9.2 | 0.124 | 1 |
| 3 | C | nest64_L16 | nestC | 4969736 | 41.4 | 1.293 | 2 (chain) |
| 4 | B-N8 | nest32_L16 | nestB8 | 4969736 | 10.1 | 0.276 | 3 |
| 5 | A-N8 | nest16_L16 | nestA8 | 621464 | 3.2 | 0.026 | 1 |
| 6 | A-N64 | nest16_L16 | nestA64 | 4969736 | 4.0 | 0.102 | 3 |
| 7 | A-R1.25 | nest16_L16 | lam 1.25 nestA | 88280 | 3.1 | 0.017 | 1 |
| 8 | A-R1.35 | nest16_L16 | lam 1.35 nestA | 91216 | 3.1 | 0.017 | 1 |
| 9 | B-R1.25 | nest32_L16 | lam 1.25 nestB | 706768 | 9.3 | 0.127 | 3 |
| 10 | A-L32 | nest16_L32 | nestA | 77704 | 3.6 | 0.019 | 1 |
| 11 | B-L32 | nest32_L32 | nestB | 621464 | 10.9 | 0.144 | 3 |

Sum 2.16 card-hours by the model; with a factor two of model error 4.3, inside the cap of 6
card-hours this round. Jobs, one in the queue at a time for this package: job 1 (batch,
wall 58 min) A, B, A-L32, A-R1.25, A-R1.35, A-N8 (model 0.22 h): it shows first whether the
coarsest member forms the horizon and whether the nested geometry runs at all; job 2 the chain
of C; job 3 (batch) B-N8, A-N64, B-R1.25, B-L32 (model 0.65 h). Particle counts are those of
the prep runs (lattices.json of A-20261121-075356-1ad4c81, -075401-1412a08, -075404-ac51b7e).
Finder cadence 0.03125 M (every 2, 4, 8 cycles), four times BH-1R's, trajectories every
0.125 M as in BH-1R; compare.py interpolates the particles' proper times linearly to the
finder's time (section 4).

## 4. What is measured (compare.py of runs_ball at 9cddbfc6 with the nested line points; converge.py)

Per member, against the exact solution of its own data (compare.py `--gauge leak --leak 8
--nest <outer>:<1/h_f>`):
- ddet: at the finder's first detection, the proper time of the tracked particles at its
  mean coordinate radius minus the exact tau_AH of the shell there (the horizon-formation
  time error in the particles' own clock);
- dtrap: per tracked particle of the band just inside the core edge (R_i = 2.603 M, 60
  particles), the proper time at which its areal radius falls through 2m minus the exact
  tau_AH of its shell, mean;
- dta, dRmax: core turnaround proper time and R_max per particle against the exact cycloid
  (parabola vertex of compare.py; the window-independent estimators of
  runs_ball/turnaround.py are left to that package), mean over the core particles;
- eta: largest core |R/R_exact - 1| at the exact turnaround time;
- dm1, dmmed: finder irreducible mass sqrt(A/16 pi) against the exact horizon mass of the same
  slice (outermost shell whose particles have passed their tau_AH), at first detection and
  median over the detections.
Orders between neighbours p = log2(|e(h)| / |e(h/2)|) and the self-convergence order of the
three meshes; legs N, R, L: the spread of the errors across the leg against the mesh error of
the member. The comparison level is the source's Oppenheimer-Snyder test: Delta M/M_ADM <~
1e-3 for the fiducial run (refs/arxiv_2611.12831/src/main.tex:945), RMS 2.061e-3, 9.362e-4,
7.347e-4 over its AMR particle sequence A1-A3 and no monotonic trend for its fixed-N SMR
sequence (main.tex:1484-1485) [VERIFIED]. Its error is that of the final mass after all the
dust has fallen in, against M_ADM; ours is the mass of a horizon that is still growing,
against the exact slice, which is the harder measure [JUDGEMENT].

### 3a. Change after job 1 (2026-11-21 01:10 PST; JOURNAL.md entries 5 and 6)

Measured on job 1 (run A-20261121-075926-d10c2c1): particles cost about 2e-7 card-seconds per
particle and step (A-N8 185 s against A 76 s for 543760 more particles over 1024 steps), three
times the model's 6.2e-8; the mesh part matches the model within 1.2 (B 537 s against 446 s).
New estimates: B-N8 about 39 min, A-N64 about 18 min, B-R1.25 and B-R1.35 about 9.5 min each,
B-L32 about 11 min; C about 2 s per step, 2.3 card-hours, so its chain (cap three segments of
50 min) is just long enough. Job 3 is split: job 3a = B-N8, A-N64 (lists/job3a.list); job 3b =
B-R1.25, B-R1.35 (added: the ball-radius leg at A varied by more than the mesh step, entry 5),
B-L32 last (A-L32 equalled A to 1e-7). Card total about 0.29 + 2.3 + 1.0 + 0.5 = 4.1 card-hours,
inside the cap of 6.
