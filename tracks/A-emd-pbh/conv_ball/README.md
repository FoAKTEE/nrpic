# conv_ball: G2 convergence series of horizon formation in the expanding ball (Track A)

Helper package of A-emd-pbh, wave 3 (round 1; continued in batch 2b on 2026-11-20/21).
Criterion (coord/CHARTER.md 9.4, G2): the errors of the turnaround time and of the
horizon-formation time against the exact solution converge in particle number, mesh spacing
and ball radius; the horizon-mass error is of the order of the source paper's
Oppenheimer-Snyder test; plus the boundary leg of the common three-way convergence (9.2).

State (2026-11-21 04:10 PST): every planned member has run and been analysed (14 card runs in
4 card jobs, 3.50 card-hours of the cap of 6); outcomes in JOURNAL.md entries 4-12; no card run
is pending. Final numbers: analysis A-20261121-120257-a2eb839 (convergence.md,
convergence.json, fig_convergence.png under scratch/A-emd-pbh/<run id>/).

## What is here

| path | content |
|---|---|
| `DESIGN.md` | nested static geometry (level boundaries fixed at 1, 2, 4, 8 M; finest box [-1, 1]^3), memory and cost model, lattices, the legs, run table ordered by value, what is measured |
| `JOURNAL.md` | what was read, design inputs, predictions (entry 3: S smoke tests, G the series) written before the runs, outcomes |
| `scripts/common.py`, `compare.py`, `fields.py`, `summary3.py`, `prep_bh.py`, `bh.athinput`, `bh_smr.athinput` | copies of `runs_ball/` at commit 9cddbfc6 (header line says so); changes marked `conv_ball:` (paths; `prep_bh.py --M --edge-w --nested`; `compare.py --nest` with line points through nested levels and particle clocks interpolated to the finder's time) |
| `scripts/geometry_probe.py` | coordinate radii of the shell groups, finder radius, cost and memory of a finished run (run A-20261120-222355-cc8e0af on BH-1R) |
| `scripts/nested.py` | nested geometry, nested particle lattice on expball's model, cost and memory model calibrated on BH-1R |
| `scripts/design_calc.py` | design table of all members, figure (run A-20261121-075131-2682bb0) |
| `scripts/make_decks.py`, `decks/` | AthenaK decks `nest<1/h_f>_L<outer>.athinput` |
| `scripts/make_lists.py`, `lists/` | card lists `job1.list`, `job3.list`, chain arguments `C.args`, `members.json` (member -> deck, data, lattice) |
| `scripts/smoke.py` | processor smoke test of every deck (core_gauge/athena_cpu) |
| `scripts/analyse.py`, `scripts/converge.py` | compare.py on every finished member, then the convergence table and figure of all legs |

## How to rerun

All runs are registered (`harness/bin/nrpic-run submit --kind scouting --gate G2 --package
tracks/A-emd-pbh/conv_ball ...`; commands in each manifest under `tracks/A-emd-pbh/runs/`).
1. Data: `python scripts/prep_bh.py --out DIR --nlat --nested nestA:16:16:1 nestA8:16:16:2
   nestA64:16:16:4 nestB:32:16:1 nestB8:32:16:2 nestC:64:16:1`; larger balls with `--HRb 0.875
   --M 1.953125 --R1 0.52 --R2 0.76` or `--HRb 0.945 --M 2.460375 --R1 0.48148148148148145 --R2
   0.7037037037037037`, both `--edge-w 0.16836734693877542 --nlat --nested nestA:16:16:1
   nestB:32:16:1`.
2. Decks and lists: `python scripts/make_decks.py`; `python scripts/make_lists.py` (reads the
   prep run directories named in it).
3. Cards: `--launcher batch --exe /data/haiyangw/nrpic/scratch/core/exe/core_gauge/athena_gpu
   --list tracks/A-emd-pbh/conv_ball/lists/job1.list --wall 00:58:00`; C as a chain:
   `--launcher chain --exe <same> --gpu-hours 3 -- $(cat lists/C.args)`.
4. Analysis: `python scripts/analyse.py --card <card run dir> [--card <chain dir>:C]
   [--prior NAME=<numbers.json>] [--prior-turnaround <turnaround.json>] --out DIR` (the
   command of each analysis is in its manifest).

## Runs and results

| run id | what | state |
|---|---|---|
| A-20261120-222355-cc8e0af | geometry probe of BH-1R (design input) | completed |
| A-20261121-075131-2682bb0 | design table (design_calc.py) | completed |
| A-20261121-075356-1ad4c81 | data set 3 with the nested lattices | completed |
| A-20261121-075401-1412a08 | ball 1.25 times larger, lattices nestA, nestB | completed |
| A-20261121-075404-ac51b7e | ball 1.35 times larger, lattices nestA, nestB | completed |
| A-20261121-075916-0b98e86 | processor smoke test of every deck (all pass) | completed |
| A-20261121-080727-e2f9074 | smoke figure: initial psi^4 on the nested line within 5e-13 of exact | completed |
| A-20261121-075926-d10c2c1 | card job 1 (Slurm 4776): A, B, A-L32, A-R1.25, A-R1.35, A-N8; 0.29 card-h | completed |
| A-20261121-085252-f4ed504 | analysis of job 1 | completed |
| A-20261121-083336-6a82131 | chain of C (Slurm 4781, 4786, 4789), t = 0 -> 16; 1.86 card-h | completed |
| A-20261121-100945-3985b90 | interim analysis of C after segment 1 (turnaround leg) | completed |
| A-20261121-091934-ac62f5f | card job 3a (Slurm 4784): B-N8, A-N64; 0.84 card-h | completed |
| A-20261121-104359-4ce67d9 | analysis of B-N8 | completed |
| A-20261121-110025-e6aec8c | analysis of A-N64 | completed |
| A-20261121-110017-471b0ae | card job 3b (Slurm 4787): B-R1.25, B-R1.35, B-L32; 0.51 card-h | completed |
| A-20261121-115055-4554451 | analysis of job 3b | completed |
| A-20261121-120257-a2eb839 | final analysis: C and the convergence of all legs | completed |

Errors against the exact solution of each member's own data (DESIGN.md section 4: ddet =
particles' proper time at the finder's radius minus the exact trapping time of that shell, at
the first detection; dtrap = trapping time per particle, band R_i = 2.603 M; turnaround by the
cycloid fit; eta = largest core |R/R_exact - 1| at the turnaround; mass = finder
sqrt(A/16 pi) against the exact horizon mass of the same slice, median over the detections):

| member | first detection t | ddet (M) | dtrap (M) | turnaround C (M) | eta | mass median |
|---|---|---|---|---|---|---|
| A (M/16, 1 per cell) | 10.875 | +0.193 | -0.093 | -0.0148 | 8.1e-3 | +7.4e-3 |
| B (M/32, 1 per cell) | 10.781 | +0.068 | -0.022 | -0.0127 | 3.1e-3 | -2.1e-3 |
| C (M/64, 1 per cell) | 10.750 | +0.017 | -0.0077 | -0.0030 | 1.1e-3 | -2.1e-4 |
| A-N8 | 10.813 | +0.109 | -0.047 | -0.0172 | 4.2e-3 | -1.3e-3 |
| A-N64 (4969736 particles) | 10.812 | +0.146 | -0.048 | -0.0153 | 6.2e-3 | +5.0e-4 |
| B-N8 (4969736 particles) | 10.750 | +0.071 | -0.028 | -0.0083 | 3.5e-3 | -3.0e-4 |
| A-R1.25 | 10.906 | +0.100 | -0.049 | +0.0210 | 8.0e-3 | +6.7e-3 |
| A-R1.35 | 10.938 | +0.164 | -0.029 | +0.0173 | 8.3e-3 | +1.0e-2 |
| B-R1.25 | 10.750 | +0.065 | -0.015 | -0.0041 | 3.7e-3 | -1.9e-3 |
| B-R1.35 | 10.750 | +0.107 | -0.008 | -0.0048 | 5.8e-3 | -1.25e-3 |
| A-L32 | identical to A to 1e-7 | | | | | |
| B-L32 | identical to B to 1e-11 | | | | | |

Findings (JOURNAL.md entry 12):
- mesh (A, B, C): the first-detection error falls 0.193 -> 0.068 -> 0.017 M (orders 1.5, 2.0),
  the trapping error 0.093 -> 0.022 -> 0.0077 M (2.1, 1.5), the finder's lag behind the first
  trapped slice 0.43 -> 0.20 -> 0.09 (1.1, 1.1); the horizon mass error 7.4e-3 -> 2.1e-3 -> 2.1e-4
  (C below the source's fiducial Oppenheimer-Snyder level of 1e-3, main.tex:945, and its best AMR
  particle RMS 7.3e-4, main.tex:1484); the shell error at the turnaround converges at order 1.4;
  the turnaround time converges only from B to C (order 2.1; a flat maximum).
- particles: at mesh B the time errors no longer depend on the particle number; the horizon
  mass does (B: -2.1e-3 with 1 per cell, -3.0e-4 with 8); at fixed N = 4969736 the mass error is
  2-5e-4 on all three meshes.
- ball radius: the time errors vary with the ball radius by 0.09 M at A and 0.04 M at B (the
  dependence shrinks with the mesh); the mass by under 1e-3.
- outer boundary 16 M against 32 M: identical results at A and B.

Not done: the ball-radius leg on C; a finer constant-occupancy member for the turnaround time.

## Pending card runs

None. A suggested next member, if the lead wants the ball-radius leg at the finest mesh: C-R1.25
(deck nest64_L16; needs the nestC lattice of the 1.25 ball, `prep_bh.py` with the 1.25 arguments
of "How to rerun" and `--nlat --nested nestC:64:16:1`, a MEMBERS line in `make_lists.py`, and a
chain of about 2 card-hours).

## Requests

None to other owners.
