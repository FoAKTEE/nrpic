# decisive: runs D1 and D3 of stage/REVIEW-wave2.md section 7 (wave 3, round 1)

Helper package of C-sidm. Question: does the energy defect of the release collision operator
(`coll_energy` absent = `cell`) change the collapse of the wave-2 collisional King clusters
(D1), what is the seed scatter of a collapse time (D1), and does a King model clearly on the
stable side of the fluid onset contract relative to its control as the gravothermal
hypothesis says (D3)? `JOURNAL.md` holds the go/no-go reading of the card executable (entry
1: GO), the predictions (entries 2 and 4, written before the runs) and the outcomes.

State (2026-11-20 22:34 UTC): paused by `locks/PAUSE` with D1 job 1 queued; decks, predictions,
D3 initial data and the tested analysis exist; no card outcome yet.

## Contents

| Path | What |
|---|---|
| `JOURNAL.md` | go/no-go, predictions D1 and D3, outcomes |
| `scripts/decks.py` | `d1`: the D1 decks from `threshold_scan/inputs/cc{1,2}_kn10.athinput` (only `rng_seed`, `coll_energy` changed); `d3 --ic-dir DIR --tag TAG`: the D3 decks from the CC2 decks with the D3 model's files and sigma~; writes the card batch lists |
| `scripts/make_d3_ic.py` | D3 initial data (King b = 1, y0 = 0.26, N = 1e5) with the track's generator, its offline checks, K and sigma~; `--from DIR`: figure and geometry only |
| `scripts/analyze_decisive.py` | analysis of the histories: central lapse relative to the control, t_c(alpha_min < 0.3), D50/D100, collisions per particle, budget columns 31-36, seed scatter and mode comparison; reads the wave-2 runs under D1 names |
| `inputs/*.athinput` | decks: `cc{1,2}_kn10_part_s{1,2}`, `cc2_kn10_cell_s2`, `d3_kninf`, `d3_kn{10,1}_part_s1` |
| `inputs/d1_job{1,2}.list`, `inputs/d3_job{3,4}.list` | card batch lists, each starting with a smoke run to t = 0.5 M |

Executable of every card run: `/data/haiyangw/nrpic/scratch/core/exe/core_collisions-2/athena_gpu`
(core/collisions-2 at f46f159, sha256 82a05ada...). Mesh, particle numbers, options and
300 M as the wave-2 runs (`threshold_scan/JOURNAL.md` entry 1).

## How to rerun

From the worktree root `/data/haiyangw/nrpic/wt/C-sidm` (venv: `harness/bin/nrpic-env create --no-kokkos`):

```bash
python3 tracks/C-sidm/decisive/scripts/decks.py d1
harness/bin/nrpic-run submit --launcher local --cores 2 --kind scouting --gate G2 \
  --package tracks/C-sidm/decisive --purpose "D3 initial data" -- \
  python3 tracks/C-sidm/decisive/scripts/make_d3_ic.py --out '$NRPIC_RUN_DIR'
python3 tracks/C-sidm/decisive/scripts/decks.py d3 --ic-dir /data/haiyangw/nrpic/scratch/C-sidm/<IC run> --tag king_y0p26000
# card jobs: one per list, at most one of this package in the queue (see Pending)
harness/bin/nrpic-run submit --launcher local --cores 1 --kind scouting --gate G2 \
  --package tracks/C-sidm/decisive --purpose "D1/D3 analysis" -- \
  python3 tracks/C-sidm/decisive/scripts/analyze_decisive.py --out '$NRPIC_RUN_DIR' --batch <card run ids>
```

## Runs so far

| Run | What | Outcome |
|---|---|---|
| C-20261120-221846-797bdbe | card, D1 job 1: cc2_kn10_part_s1, cc2_kn10_part_s2 (Slurm 4737) | submitted 22:18 UTC |
| C-20261120-222427-6b27eea | D3 initial data, checks, K | completed: alpha_c 0.71884, +0.0482 from the Juttner onset (1.44 x the largest control drift); 18/18 checks pass; K = 251.509 |
| C-20261120-222941-595c263 | analysis test on the wave-2 runs | PASS: reproduces t_c, onsets, collision counts, defect sums |
| C-20261120-222949-2712568 | D3 figure and geometry | 97.4 percent of D3 particles in the M/4 region (CC2 98.9) |

## Results

None yet: no card run of this package has run (paused, see Pending).

## Pending

Paused at 22:34 UTC on 2026-11-20 (`locks/PAUSE`); see `JOURNAL.md` entry 5.

| Job | List | Runs | State |
|---|---|---|---|
| D1 job 1 | `inputs/d1_job1.list` | cc2_kn10_part_s1, cc2_kn10_part_s2 | run C-20261120-221846-797bdbe, Slurm 4737, queued |
| D1 job 2 | `inputs/d1_job2.list` | cc1_kn10_part_s1, cc1_kn10_part_s2 | not submitted |
| D3 job 3 | `inputs/d3_job3.list` | d3_kninf, d3_kn1_part_s1 | not submitted |
| D3 job 4 | `inputs/d3_job4.list` | d3_kn10_part_s1, cc2_kn10_cell_s2 | not submitted |

Each job: smoke run (t = 0.5 M) plus two runs of 300 M at about 3.45 s per M, about 0.6
card-hours; package total about 2.5 of the 3.0 allowed. Submit one at a time, only when
`squeue -u haiyangw -o '%i %j %T'` shows fewer than two C-* jobs and the pause flag is
absent, from `/data/haiyangw/nrpic/wt/C-sidm` with a clean `tracks/C-sidm/decisive`:

```bash
harness/bin/nrpic-run submit --launcher batch --list tracks/C-sidm/decisive/inputs/d1_job2.list \
  --wall 00:55:00 --gpu-hours 0.65 --exe /data/haiyangw/nrpic/scratch/core/exe/core_collisions-2/athena_gpu \
  --kind scouting --gate G2 --package tracks/C-sidm/decisive --particles 100000 \
  --purpose "decisive D1 job 2 of 2: CC1 (King b=1 y0=0.334032) at Kn=10 with coll_energy=particle, seeds 1 and 2, 300 M; predictions decisive/JOURNAL.md entry 2"
harness/bin/nrpic-run submit --launcher batch --list tracks/C-sidm/decisive/inputs/d3_job3.list \
  --wall 00:55:00 --gpu-hours 0.65 --exe /data/haiyangw/nrpic/scratch/core/exe/core_collisions-2/athena_gpu \
  --kind scouting --gate G2 --package tracks/C-sidm/decisive --particles 100000 \
  --purpose "decisive D3 job 3: King b=1 y0=0.26 control (Kn=inf) and Kn=1 with coll_energy=particle, 300 M; predictions decisive/JOURNAL.md entry 4"
harness/bin/nrpic-run submit --launcher batch --list tracks/C-sidm/decisive/inputs/d3_job4.list \
  --wall 00:55:00 --gpu-hours 0.65 --exe /data/haiyangw/nrpic/scratch/core/exe/core_collisions-2/athena_gpu \
  --kind scouting --gate G2 --package tracks/C-sidm/decisive --particles 100000 \
  --purpose "decisive D3/D1 job 4: King y0=0.26 at Kn=10 (particle) and CC2 Kn=10 cell mode seed 2; predictions decisive/JOURNAL.md entries 2 and 4"
# after each job: harness/bin/nrpic-run finish <run id>; then the analysis over all finished jobs:
harness/bin/nrpic-run submit --launcher local --cores 1 --kind scouting --gate G2 \
  --package tracks/C-sidm/decisive --purpose "decisive: D1/D3 analysis against predictions" -- \
  python3 tracks/C-sidm/decisive/scripts/analyze_decisive.py --out '$NRPIC_RUN_DIR' \
  --batch C-20261120-221846-797bdbe <later run ids>
```

D2 (cc2_kninf and cc2_kn10 in particle mode, one more refinement level, `coll_cell_factor =
2`; 2-5 card-hours by the review's estimate) does not fit the cap of this package after D1
and D3; no decks are written for it.

## Requests

To the lead of C-sidm:
1. Resume this package after the pause (JOURNAL entry 5 says what to do first); D1 job 1 may
   already have run.
2. Until D1 has run, read the wave-2 collapse times with the reference numbers of the
   analysis test (run C-20261120-222941-595c263): the relative lapse drop of the cell-mode
   seed-1 runs is D50 = 0.012-0.013 and D100 = 0.043-0.051 at Kn = 10, and part of every
   "relative" number is the controls' own rise (alpha_c +0.011 and +0.016 at 100 M).
3. D2 needs its own card allotment (2-5 card-hours); it is not in this package's cap.
