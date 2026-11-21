# conv_ball: G2 convergence series of horizon formation in the expanding ball (Track A)

Helper package of A-emd-pbh, wave 3 (round 1; continued in batch 2b on 2026-11-20/21).
Criterion (coord/CHARTER.md 9.4, G2): the errors of the turnaround time and of the
horizon-formation time against the exact solution converge in particle number, mesh spacing
and ball radius; the horizon-mass error is of the order of the source paper's
Oppenheimer-Snyder test; plus the boundary leg of the common three-way convergence (9.2).

State: see "Runs and results" below and the last entries of JOURNAL.md.

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
   [--prior NAME=<numbers.json>] --out DIR`.

## Runs and results

Outcomes of every prediction: JOURNAL.md (entries 4, 5, 8, 9, 10 so far). Runs of this package:

| run id | what | state |
|---|---|---|
| A-20261120-222355-cc8e0af | geometry probe of BH-1R (design input) | completed |
| A-20261121-075131-2682bb0 | design table (design_calc.py) | completed |
| A-20261121-075356-1ad4c81 | data set 3 with the nested lattices | completed |
| A-20261121-075401-1412a08 | ball 1.25 times larger, lattices nestA, nestB | completed |
| A-20261121-075404-ac51b7e | ball 1.35 times larger, lattices nestA, nestB | completed |
| A-20261121-075916-0b98e86 | processor smoke test of every deck (all pass) | completed |
| A-20261121-080727-e2f9074 | smoke figure: initial psi^4 on the nested line within 5e-13 of exact | completed |
| A-20261121-075926-d10c2c1 | card job 1 (Slurm 4776): A, B, A-L32, A-R1.25, A-R1.35, A-N8; 0.29 card-hours | completed |
| A-20261121-085252-f4ed504 | analysis of job 1 (convergence.md, fig_convergence.png) | completed |
| A-20261121-083336-6a82131 | chain of C (Slurm 4781, then 4786, ...) | running |
| A-20261121-091934-ac62f5f | card job 3a (Slurm 4784): B-N8, A-N64; 0.84 card-hours | completed |
| A-20261121-104359-4ce67d9 | analysis of B-N8 | completed |
| A-20261121-110025-e6aec8c | analysis of A-N64 (with all earlier numbers) | completed |
| A-20261121-110017-471b0ae | card job 3b (Slurm 4787): B-R1.25, B-R1.35, B-L32 | submitted |
| A-20261121-100945-3985b90 | interim analysis of C after its first segment (t <= 6.32): turnaround leg | completed |

Results of jobs 1 and 3a (analyses A-20261121-085252-f4ed504, -104359-4ce67d9, -110025-e6aec8c; errors against the exact solution of
each member's own data; DESIGN.md section 4):

| member | first detection t | first-detection error (M) | trapping, band 2.603 (M) | turnaround V3 / C (M) | core eps at turnaround | horizon mass, median |
|---|---|---|---|---|---|---|
| A (M/16) | 10.875 | +0.193 | -0.093 | -0.037 / -0.015 | 8.1e-3 | +7.4e-3 |
| B (M/32) | 10.781 | +0.068 | -0.022 | -0.033 / -0.013 | 3.1e-3 | -2.1e-3 |
| A-L32 | 10.875 | +0.193 | -0.093 | -0.037 / -0.015 | 8.1e-3 | +7.4e-3 |
| A-R1.25 | 10.906 | +0.100 | -0.049 | -0.020 / +0.021 | 8.0e-3 | +6.7e-3 |
| A-R1.35 | 10.938 | +0.164 | -0.029 | -0.025 / +0.017 | 8.3e-3 | +1.0e-2 |
| A-N8 | 10.813 | +0.109 | -0.047 | -0.048 / -0.017 | 4.2e-3 | -1.3e-3 |
| A-N64 (4969736 particles) | 10.812 | +0.146 | -0.048 | -0.040 / -0.015 | 6.2e-3 | +5.0e-4 |
| B-N8 (4969736 particles) | 10.750 | +0.071 | -0.028 | -0.015 / -0.008 | 3.5e-3 | -3.0e-4 |

So far: the horizon is found in every member and in every search after the first; the
first-detection and trapping errors fall from A to B at orders 1.5 and 2.1; the horizon-mass
error (median) falls from 7.4e-3 to 2.1e-3 in magnitude (B: twice the source's fiducial OS
level of 1e-3, main.tex:945); the turnaround time does not converge between A and B (a flat
maximum set by slopes of the shell error; R_max converges); the outer boundary at 16 M and
32 M gives identical results to 1e-7; at A's mesh the time errors vary with the ball radius by
more than the mesh step (open: B-R1.25, B-R1.35). The mesh triple needs C.

C after its first segment (t <= 6.32, analysis A-20261121-100945-3985b90): core shell error
at the turnaround 8.1e-3, 3.1e-3, 1.1e-3 (A, B, C; order about 1.4); turnaround time (cycloid
fit) -0.0148, -0.0127, -0.0035 M: converges only from B to C (order 1.9).

Particles (job 3a): at mesh B the time errors no longer depend on the particle number (B-N8
against B: 0.003 M in the first-detection error); the horizon mass does: its median error is
-2.1e-3 with one particle per cell and -3.0e-4 with eight (B-N8_horizon.png: 1e-4 to 7e-4 from
t = 11.5 to 16), below the source's fiducial OS level of 1e-3; A-N64 gives +5.0e-4.

## Pending card runs

| run | members | expected cost | state |
|---|---|---|---|
| A-20261121-083336-6a82131 (chain) | C (M/64, 4969736 particles) | about 2.1 card-hours, 3 segments | segment 1 done (t = 6.32), segment 2 Slurm 4786 running from 02:59 |
| A-20261121-110017-471b0ae (batch) | B-R1.25, B-R1.35, B-L32 | about 0.5 card-hours | Slurm 4787 |

Submit: `harness/bin/nrpic-run submit --kind scouting --gate G2 --package
tracks/A-emd-pbh/conv_ball --purpose '...' --launcher batch --exe
/data/haiyangw/nrpic/scratch/core/exe/core_gauge/athena_gpu --list
tracks/A-emd-pbh/conv_ball/lists/job3a.list --wall 00:58:00`; analyse with
`python tracks/A-emd-pbh/conv_ball/scripts/analyse.py --card <run dir> [--card <chain dir>:C]
--prior NAME=<numbers.json> ... --prior-turnaround <turnaround.json> --out '$NRPIC_RUN_DIR'`
(numbers of job 1: scratch/A-emd-pbh/A-20261121-085252-f4ed504/<member>_numbers.json).

## Requests

None yet.
