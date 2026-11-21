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

See JOURNAL.md for the outcome of every prediction. Runs of this package:

| run id | what | state |
|---|---|---|
| A-20261120-222355-cc8e0af | geometry probe of BH-1R (design input) | completed |
| A-20261121-075131-2682bb0 | design table (design_calc.py) | completed |
| A-20261121-075356-1ad4c81 | data set 3 with the nested lattices | completed |
| A-20261121-075401-1412a08 | ball 1.25 times larger, lattices nestA, nestB | completed |
| A-20261121-075404-ac51b7e | ball 1.35 times larger, lattices nestA, nestB | completed |
| A-20261121-075916-0b98e86 | processor smoke test of every deck | see JOURNAL |
| A-20261121-075926-d10c2c1 | card job 1 (Slurm 4776): A, B, A-L32, A-R1.25, A-R1.35, A-N8 | see JOURNAL |

## Requests

None yet.
